"""
Copyright 2022 Objectiv B.V.
"""

import bach
from bach.series import Series
from sql_models.constants import NotSet, not_set
from typing import cast, List, Union, TYPE_CHECKING

from sql_models.util import is_bigquery, is_postgres

from modelhub.util import check_groupby

if TYPE_CHECKING:
    from modelhub.series import SeriesLocationStack


GroupByType = Union[List[Union[str, Series]], str, Series, NotSet]


class FunnelDiscovery:
    """
    Class to discovery user journeys for funnel analysis.

    The main method of this class is the `get_navigation_paths`, to get the navigation 
    paths of the users. This method can also get 'filtered' navigation paths to the 
    conversion locations.

    For the visualization of the user flow, use the `plot_sankey_diagram` method.
    """

    CONVERSTION_STEP_COLUMN = '_first_conversion_step_number'
    STEP_TAG_COLUMN = '_step_tag'

    @staticmethod
    def _tag_step(step_series: bach.Series) -> bach.Series:
        """
        Tag the step number, is it 1st step, 2nd step, ...

        :param step_series: series of ith step:
                index
                index1  val1_step_ith
                index2  val2_step_ith
                index3  val3_step_ith
                ...

        :returns: series with step number in the index:

                index    STEP_TAG_COLUMN
                index1   ith      val1_step_ith
                index2   ith      val2_step_ith
                index3   ith      val3_step_ith

            where ith is a step number.
        """

        step_df = step_series.to_frame()
        # add the step name as index
        step_df[FunnelDiscovery.STEP_TAG_COLUMN] = int(step_series.name.split('_')[-1])
        step_df = step_df.set_index(keys=FunnelDiscovery.STEP_TAG_COLUMN, append=True)
        step_df = step_df.materialize(node_name='tagged_step')
        return step_df[step_series.name]

    def _melt_steps(self, steps_df: bach.DataFrame) -> bach.Series:
        """
        Transform steps dataframe into a single series.

        :param steps_df: steps dataframe, which one can get from
            `FunnelDiscovery.get_navigation_paths` method:

                    step_1  step_2  step_3
            index1  v11     v12     v13
            index2  v21     v22     v23

        :returns: transformed steps_df to the following series:

            index   STEP_TAG_COLUMN
            index1  1               v11
                    2               v12
                    3               v13
            index2  1               v21
                    2               v22
                    3               v23

        """
        # tags the steps numbers
        tagged_steps = [self._tag_step(step_series)
                        for step_series in steps_df.data.values()]

        # melt all steps into a single series
        all_steps_series = tagged_steps[0].append(other=tagged_steps[1:],
                                                  ignore_index=False)
        return all_steps_series.copy_override(name='step_value')

    def _add_first_conversion_step_number_column(
            self,
            steps_df: bach.DataFrame,
            conversion_events_df: bach.DataFrame,
            conversion_location_column: str = 'feature_nice_name',
    ) -> bach.DataFrame:
        """
        Identify the first conversion step number per each navigation path and
        add it as a column to the copy of steps_df dataframe.

        :param steps_df: dataframe which one gets from `FunnelDiscovery.get_navigation_paths` method.
        :param conversion_events_df: dataframe where for each `conversion_location_column`
            value we have info if there was a conversion event.
        :param conversion_location_column: column name for merging steps_df and conversion_events_df
            dataframes in order to get converted steps df.

        :returns: copy of steps_df bach DataFrame, with the addition
            `CONVERSTION_STEP_COLUMN` column.
        """

        if 'is_conversion_event' not in conversion_events_df.data_columns:
            raise ValueError('The is_conversion_event column is missing in the dataframe.')
        conversion_events_df_columns = [conversion_location_column, 'is_conversion_event']

        _steps_df = steps_df.copy()

        # set a new index for _steps_df
        first_column = _steps_df.data_columns[0]
        _steps_df['_index'] = steps_df.groupby().window()[first_column].window_row_number()
        # need add also steps_df 'old' index
        initial_index = steps_df.index_columns
        index_columns = ['_index'] + initial_index
        _steps_df = _steps_df.reset_index().set_index(index_columns)

        # melting steps df in order later to merge with df where we have the conversion info
        all_steps_series = self._melt_steps(_steps_df)
        melted_steps_df = all_steps_series.reset_index(drop=False)
        melted_steps_df = cast(bach.DataFrame, melted_steps_df)  # help mypy

        # identify if step is a conversion
        _conversion_events_df = conversion_events_df[conversion_events_df_columns]
        _conversion_events_df = _conversion_events_df[_conversion_events_df.is_conversion_event].reset_index(
            drop=True).materialize(distinct=True)
        # merging in order to have is_conversion_event column
        converted_steps_df = melted_steps_df.merge(_conversion_events_df,
                                                   left_on='step_value',
                                                   right_on=conversion_location_column,
                                                   how='left')
        converted_steps_df = converted_steps_df[converted_steps_df.is_conversion_event]
        converted_steps_df = converted_steps_df.drop(columns=[conversion_location_column,
                                                              'is_conversion_event']).reset_index(drop=True)
        # consider only first conversion step
        first_converted_step_df = converted_steps_df.drop_duplicates(subset=index_columns,
                                                                     keep='first',
                                                                     sort_by=[self.STEP_TAG_COLUMN])
        first_converted_step_df = first_converted_step_df[index_columns + [self.STEP_TAG_COLUMN]]
        first_converted_step_df = first_converted_step_df.rename(
            columns={self.STEP_TAG_COLUMN: self.CONVERSTION_STEP_COLUMN})

        # final steps df with CONVERSTION_STEP_COLUMN column
        result_df = _steps_df.materialize().merge(first_converted_step_df.materialize(),
                                                  how='left', on=index_columns)

        result_df = result_df.reset_index(level='_index',  drop=True)

        return result_df

    def _filter_navigation_paths_to_conversion(
            self,
            steps_df: bach.DataFrame,
    ) -> bach.DataFrame:
        """
        Filter each navigation path to first conversion location.

        For each row of steps_df dataframe set to None the step values
         after encountering the first conversion location step.

        Corner case: in case the first location stack is conversion one we ignore it
        and proceed to the next step.

        :param steps_df: dataframe which one gets from `FunnelDiscovery.get_navigation_paths`
            method, the dataframe that we're going to filter.

        :returns: bach DataFrame, filtered each row of steps_df to the conversion location.
        """

        conv_step_num_column = self.CONVERSTION_STEP_COLUMN
        if conv_step_num_column not in steps_df.data_columns:
            raise ValueError(f'{conv_step_num_column} column is missing in the dataframe.')

        result_df = steps_df[steps_df[conv_step_num_column] != 1]

        _columns = [i for i in steps_df.data_columns if i != conv_step_num_column]
        for step_name in _columns:
            tag = int(step_name.split('_')[-1])
            mask = (tag > result_df[conv_step_num_column]) | (result_df[conv_step_num_column].isnull())
            # don't consider any step happened after the fist conversion step
            result_df.loc[mask, step_name] = None

        result_df = result_df.dropna(subset=[conv_step_num_column])
        return result_df

    def get_navigation_paths(
        self,
        data: bach.DataFrame,
        steps: int,
        by: GroupByType = not_set,
        location_stack: 'SeriesLocationStack' = None,
        add_conversion_step_column: bool = False,
        only_converted_paths: bool = False,
        start_from_end: bool = False,
        n_examples: int = None
    ) -> bach.DataFrame:
        """
        Get the navigation paths for each event's location stack. Each navigation path 
        is represented as a row, where each step is defined by the nice name of the 
        considered location.

        For each location stack:
        
        - The number of navigation paths to be generated is less than or equal to
            `steps`.
        - The locations to be considered as starting steps are those that have
            an offset between 0 and `steps - 1` in the location stack.
        - For each path, the rest of steps are defined by the `steps - 1` locations
            that follow the start location in the location stack.

        For example, having `location_stack = ['a', 'b', 'c' , 'd']` and `steps` = 3
        will generate the following paths:

        - `'a', 'b', 'c'`
        - `'b', 'c', 'd'`
        - `'c', 'd', None`

        :param data: :py:class:`bach.DataFrame` to apply the method on.
        :param steps: Number of steps/locations to consider in navigation path.
        :param by: sets the column(s) to group by. If by is None or not set,
            then steps are based on the order of events based on the entire dataset.
        :param location_stack: the location stack

            - can be any slice of a :py:class:`modelhub.SeriesLocationStack` type column
            - if None - the whole location stack is taken.

        :param add_conversion_step_column: if True gets the first conversion step number
            per each navigation path and adds it as a column to the returned dataframe.
        :param only_converted_paths: if True filters each navigation path to first
            conversion location.
        :param start_from_end: if True starts the construction of navigation paths from the last
                context from the stack, otherwise it starts from the first.
                If there are too many steps, and we limit the amount with `n_examples` parameter
                we can lose the last steps of the user, hence in order to 'prioritize' the last
                steps one can use this parameter.

                Having `location_stack = ['a', 'b', 'c' , 'd']` and `steps` = 3
                will generate the following paths:

                    - `'b', 'c', 'd'`
                    - `'a', 'b', 'c'`
                    - `None, 'a', 'b'`

        :param n_examples: limit the amount of navigation paths.
                           If `None`, all the navigation paths are taken.

        :returns: Bach DataFrame containing a new Series for each step containing the nice name
            of the location.
        """

        from modelhub.util import check_objectiv_dataframe
        check_objectiv_dataframe(df=data,
                                 columns_to_check=['location_stack', 'moment'])

        data = data.copy()

        from modelhub.series.series_objectiv import SeriesLocationStack
        _location_stack = location_stack or data['location_stack']
        _location_stack = _location_stack.copy_override_type(SeriesLocationStack)
        partition = None
        sort_nice_names_by = []

        if by is not None and by is not not_set:
            partition = check_groupby(
                data=data, groupby=by, not_allowed_in_groupby='location_stack',
            )
            sort_nice_names_by = [data[idx] for idx in partition.index_columns]

        # always sort by moment, since we need to respect the order of the nice names in the data
        # for getting the correct navigation paths based on event time
        sort_nice_names_by += [data['moment']]

        ascending = True
        if start_from_end:
            ascending = False
        nice_name = _location_stack.ls.nice_name.sort_by_series(by=sort_nice_names_by,
                                                                ascending=ascending)

        agg_steps = nice_name.to_json_array(partition=partition)
        flattened_lc, offset_lc = agg_steps.json.flatten_array()

        # flattening will assume items are still json type, we need to extract the items
        # as scalar types (string items)
        if is_bigquery(data.engine):
            flattened_lc = flattened_lc.copy_override(
                expression=bach.expression.Expression.construct('JSON_EXTRACT_SCALAR({})',
                                                                flattened_lc)
            )
        elif is_postgres(data.engine):
            flattened_lc = flattened_lc.copy_override(
                expression=bach.expression.Expression.construct(
                    '{} #>> {}',
                    flattened_lc,
                    bach.expression.Expression.raw("'{}'")
                )
            )

        flattened_lc = flattened_lc.astype('string')

        offset_lc = offset_lc.copy_override(name='__root_step_offset')

        nav_df = flattened_lc.to_frame()
        nav_df[offset_lc.name] = offset_lc

        nav_df = nav_df.sort_values(
            by=nav_df.index_columns + [offset_lc.name],
            ascending=[True if start_from_end else False] * len(nav_df.index_columns) + [False]
        )

        window = nav_df.groupby(by=nav_df.index_columns).window()
        root_step_series = window[flattened_lc.name]

        all_step_series = {}
        for step in range(1, steps + 1):
            step_series_name = f'{flattened_lc.name}_step_{step}'
            if step == 1:
                next_step = root_step_series.copy_override(group_by=None)
            else:
                next_step = root_step_series.window_lag(offset=step - 1)

            all_step_series[step_series_name] = (
                next_step.copy_override(name=step_series_name)
            )

        result = nav_df.copy_override(
            base_node=window.base_node,
            series={
                **all_step_series,
                offset_lc.name: offset_lc.copy_override(base_node=window.base_node),
            }
        )
        result = result.materialize(node_name='step_extraction')

        # limit rows
        if n_examples is not None:
            result = result[result[offset_lc.name] < n_examples]

        # removing the last step with nulls
        if steps > 2:
            mask = (result['__root_step_offset'] != 0) & (result[f'{flattened_lc.name}_step_2'].isnull())
            result.loc[mask, f'{flattened_lc.name}_step_1'] = None
            result = result.dropna(subset=[f'{flattened_lc.name}_step_1'])

        # re-order rows
        result = result.sort_values(by=result.index_columns + [offset_lc.name])

        # drop offset column
        result = result.drop(columns=[offset_lc.name])

        if start_from_end:
            # need to reverse column order
            # if path is `a, b, c, d` and steps=3, the current format is:

            # step_1 step_2 step_3
            #   d     c      b
            #   c     b      a
            #   b     a      None

            # but we expect this:

            # step_1 step_2  step_3
            #  b      c       d
            #  a      b       c
            #  None   b       a

            column_old_order = result.data_columns
            column_new_order = column_old_order[::-1]

            new_columns_name = {}
            for old, new in zip(column_old_order, column_new_order):
                new_columns_name[old] = new
            result = result.rename(columns=new_columns_name)[column_old_order]

        # conversion part
        if not (add_conversion_step_column or only_converted_paths):
            return result

        if 'feature_nice_name' not in data.data_columns:
            data['feature_nice_name'] = data.location_stack.ls.nice_name
        result = self._add_first_conversion_step_number_column(result, data)

        if not only_converted_paths:
            return result

        result = self._filter_navigation_paths_to_conversion(result)

        if add_conversion_step_column is False:
            result = result.drop(columns=[self.CONVERSTION_STEP_COLUMN])

        return result

    def plot_sankey_diagram(
            self,
            steps_df: bach.DataFrame,
            n_top_examples: int = 15,
            max_n_top_examples: int = 50) -> None:
        """
        Plot a Sankey Diagram of the Funnel with Plotly.

        Tihs method requires the dataframe from `FunnelDiscovery.get_navigation_paths`.
        In this function we convert this Bach dataframe to a Pandas dataframe, and
        in order to plot the sankey diagram, we construct a new `df_links` pandas dataframe
        out of it, with `df_links`:

        - `'source', 'target', 'value'`
        - `'step1', 'step2', 'val1'`
        - `'step2', 'step3', 'val2'`
        - `'...', '...', '...'`

        The navigation steps are our nodes (source and target), the value shows
        how many source -> target links we have.

        :param steps_df: the dataframe which we get from `FunnelDiscovery.get_navigation_paths` method.
        :param n_top_examples: number of top examples to plot.
        :param max_n_top_examples: if we have too many examples to plot it can slow down
            the browser, so you can limit to plot only the `max_n_top_examples` examples.
        """

        # count navigation paths
        columns = [i for i in steps_df.data_columns
                   if i != self.CONVERSTION_STEP_COLUMN]
        steps_counter_df = steps_df[columns].value_counts().to_frame()

        _steps_counter_df = steps_counter_df.reset_index().to_pandas()
        if n_top_examples is None:
            n_top_examples = len(_steps_counter_df)
        n_top_examples = min(n_top_examples, max_n_top_examples)
        print(f'Showing {n_top_examples} examples out of {len(_steps_counter_df)}')

        _counter = _steps_counter_df.head(n_top_examples).values.tolist()

        def func_ngram(data, n): return [data[i: i + n] for i in range(len(data) - n + 1)]

        source, target, value = [], [], []
        for elem in _counter:
            # node
            _steps = elem[:-1]

            # we remove 'single' steps
            _steps = [i for i in _steps if i is not None]
            if len(_steps) < 2:
                continue

            # link
            source_target_list = func_ngram(_steps, 2)
            source.extend([i[0] for i in source_target_list])
            target.extend([i[1] for i in source_target_list])
            # weight
            weight = elem[-1]
            value.extend([weight for i in range(len(source_target_list))])

        import pandas as pd
        df_links = pd.DataFrame({'source': source, 'target': target, 'value': value})

        unique_source_target = list(pd.unique(df_links[['source', 'target']].values.ravel()))
        mapping_dict = {k: v for v, k in enumerate(unique_source_target)}
        df_links['source'] = df_links['source'].map(mapping_dict)
        df_links['target'] = df_links['target'].map(mapping_dict)

        # summing up loops - we want one link for a loop
        df_links["value"] = df_links.groupby(['source', 'target'])['value'].transform('sum')
        # after summing, we neet to drop the rest
        df_links = df_links.drop_duplicates(subset=['source', 'target'])

        if not df_links.empty:
            links_dict = df_links.to_dict(orient='list')

            import plotly.graph_objects as go
            fig = go.Figure(data=[go.Sankey(
                # textfont=dict(color="rgba(0,0,0,0)", size=1), # make node text invisible
                orientation='h',  # use 'v' for vertical orientation,
                node=dict(
                    pad=25,
                    thickness=15,
                    line=dict(color="black", width=0.5),
                    label=[f'{i[:20]}...' for i in unique_source_target],
                    customdata=unique_source_target,
                    hovertemplate='NODE: %{customdata}',
                ),
                link=dict(
                    source=links_dict["source"],
                    target=links_dict["target"],
                    value=links_dict["value"],
                    customdata=unique_source_target,
                    hovertemplate='SOURCE: %{source.customdata}<br />' +
                                  'TARGET: %{target.customdata}<br />'
                ),
            )])

            fig.update_layout(
                hoverlabel=dict(
                    bgcolor="white",
                    font_size=11,
                ),
                font_color='black',
                title_font_color='black',
                title_text="Location Stack Flow", font_size=14)
            fig.show()
        else:
            print("There is no data to plot.")
