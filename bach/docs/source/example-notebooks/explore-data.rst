.. _explore_data:

.. frontmatterposition:: 4

.. currentmodule:: bach_open_taxonomy

=================
Explore your data
=================

This example notebook shows how you can easily explore your data collected with Objectiv. It's also available 
as a `full Jupyter notebook 
<https://github.com/objectiv/objectiv-analytics/blob/main/notebooks/explore-your-data.ipynb>`_
to run on your own data (see how to :doc:`get started in your notebook <../get-started-in-your-notebook>`), 
or you can instead `run the Demo </docs/home/quickstart-guide/>`_ to quickly try it out. The dataset used 
here is the same as in the Demo.

Get started
-----------
We first have to instantiate the model hub and an Objectiv DataFrame object.

.. doctest:: explore-data
	:skipif: engine is None

	>>> # instantiate the model hub, and set the default time aggregation to daily
	>>> from modelhub import ModelHub
	>>> modelhub = ModelHub(time_aggregation='%Y-%m-%d')
	>>> # get an Objectiv DataFrame within a defined timeframe
	>>> df = modelhub.get_objectiv_dataframe(db_url=DB_URL, start_date='2022-06-01', end_date='2022-06-30')

.. admonition:: Reference
	:class: api-reference

	* :doc:`modelhub.ModelHub.get_objectiv_dataframe <../open-model-hub/api-reference/ModelHub/modelhub.ModelHub.get_objectiv_dataframe>`


A first look at the data
------------------------

.. doctest:: explore-data
	:skipif: engine is None
	
	>>> # have a look at the event data, sorted by the user's session ID & hit
	>>> df.sort_values(['session_id', 'session_hit_number'], ascending=False).head()
	                                             day                  moment                               user_id                                    global_contexts                                     location_stack              event_type                                  stack_event_types session_id session_hit_number
	event_id
	96b5e709-bb8a-46de-ac82-245be25dac29  2022-06-30 2022-06-30 21:40:32.401  2d718142-9be7-4975-a669-ba022fd8fd48  [{'id': 'http_context', '_type': 'HttpContext'...  [{'id': 'home', '_type': 'RootLocationContext'...            VisibleEvent  [AbstractEvent, NonInteractiveEvent, VisibleEv...        872                  3
	252d7d87-5600-4d90-b24f-2a6fb8986c5e  2022-06-30 2022-06-30 21:40:30.117  2d718142-9be7-4975-a669-ba022fd8fd48  [{'id': 'http_context', '_type': 'HttpContext'...  [{'id': 'home', '_type': 'RootLocationContext'...              PressEvent      [AbstractEvent, InteractiveEvent, PressEvent]        872                  2
	157a3000-bbfc-42e0-b857-901bd578ea7c  2022-06-30 2022-06-30 21:40:16.908  2d718142-9be7-4975-a669-ba022fd8fd48  [{'id': 'http_context', '_type': 'HttpContext'...  [{'id': 'home', '_type': 'RootLocationContext'...              PressEvent      [AbstractEvent, InteractiveEvent, PressEvent]        872                  1
	8543f519-d3a4-4af6-89f5-cb04393944b8  2022-06-30 2022-06-30 20:43:50.962  bb127c9e-3067-4375-9c73-cb86be332660  [{'id': 'http_context', '_type': 'HttpContext'...  [{'id': 'home', '_type': 'RootLocationContext'...          MediaLoadEvent  [AbstractEvent, MediaEvent, MediaLoadEvent, No...        871                  2
	a0ad4364-57e0-4da9-a266-057744550cc2  2022-06-30 2022-06-30 20:43:49.820  bb127c9e-3067-4375-9c73-cb86be332660  [{'id': 'http_context', '_type': 'HttpContext'...  [{'id': 'home', '_type': 'RootLocationContext'...  ApplicationLoadedEvent  [AbstractEvent, ApplicationLoadedEvent, NonInt...        871                  1
	<BLANKLINE>

.. admonition:: Reference
	:class: api-reference

	* :doc:`bach.DataFrame.sort_values <../bach/api-reference/DataFrame/bach.DataFrame.sort_values>`
	* :doc:`bach.DataFrame.head <../bach/api-reference/DataFrame/bach.DataFrame.head>`


Understanding the columns
-------------------------

.. doctest:: explore-data
	:skipif: engine is None

	>>> # see the data type for each column
	>>> df.dtypes
	{'day': 'date',
	'moment': 'timestamp',
	'user_id': 'uuid',
	'global_contexts': 'objectiv_global_context',
	'location_stack': 'objectiv_location_stack',
	'event_type': 'string',
	'stack_event_types': 'json',
	'session_id': 'int64',
	'session_hit_number': 'int64'}

.. admonition:: Reference
	:class: api-reference

	* :doc:`bach.DataFrame.dtypes <../bach/api-reference/DataFrame/bach.DataFrame.dtypes>`

What's in these columns:

* `day`: the day of the session as a date.
* `moment`: the exact moment of the event as a timestamp.
* `user_id`: the unique identifier of the user, based on the cookie.
* `global_contexts`: a JSON-like column that stores additional global information on the event that is logged, 
  such as device, application, cookie, etcetera. :doc:`See the open taxonomy notebook <./open-taxonomy>` for 
  more details.
* `location_stack`: a JSON-like column that stores information on the UI location that the event was 
  triggered. :doc:`See the open taxonomy notebook <./open-taxonomy>` for more details.
* `event_type`: the type of event that is logged, e.g. a `PressEvent`.
* `stack_event_types`: the parents of the `event_type` as a hierarchical JSON structure.
* `session_id`: a unique incremented integer ID for each session. Starts at 1 for the selected data in the 
  DataFrame.
* `session_hit_number`: an incremented integer ID for each hit in the session, ordered by moment.

.. admonition:: Reference
	:class: api-reference

	For a more detailed understanding of Objectiv events in general, and especially the `global_contexts` and 
	`location_stack` data columns, see the open analytics taxonomy documentation:

	* `Events </docs/taxonomy/events>`_.
	* `Global contexts </docs/taxonomy/global-contexts>`_.
	* `Location contexts </docs/taxonomy/location-contexts>`_.

Your first Objectiv event data
------------------------------
Before we dig any deeper, let's take a more global look at the data Objectiv is now tracking in your product. 
An easy way to do this, is by looking at it from the `'root locations' 
</docs/taxonomy/reference/location-contexts/RootLocationContext>`_; the main sections in your product's UI.

First, we want to extract data from the `global_contexts` and `location_stack` columns that contain all 
relevant context about the event. :doc:`See the open taxonomy notebook <./open-taxonomy>` for more details.

.. doctest:: explore-data
	:skipif: engine is None

	>>> # add specific contexts to the data as columns
	>>> df['application'] = df.global_contexts.gc.application
	>>> df['root_location'] = df.location_stack.ls.get_from_context_with_type_series(type='RootLocationContext', key='id')
	>>> df['path'] = df.global_contexts.gc.get_from_context_with_type_series(type='PathContext', key='id')

.. doctest:: explore-data
	:skipif: engine is None

	>>> # now easily slice the data using the added context columns
	>>> event_data = modelhub.agg.unique_users(df, groupby=['application', 'root_location', 'path', 'event_type'])
	>>> event_data.sort_values(ascending=False).to_frame().head(20)
	                                                                                                                    unique_users
	application         root_location   path                                            event_type 
	objectiv-website    home            https://objectiv.io/                            MediaLoadEvent                  202
	                                                                                    ApplicationLoadedEvent          194
	                                                                                    PressEvent                      161
	                                                                                    VisibleEvent                    158
	                                                                                    HiddenEvent                     82
	objectiv-docs       home            NaN                                             VisibleEvent                    79
	                                                                                    ApplicationLoadedEvent          67
	                    modeling        NaN                                             VisibleEvent                    56
	                    home            NaN                                             PressEvent                      47
	                                    https://objectiv.io/docs/                       VisibleEvent                    45
	                    modeling        NaN                                             PressEvent                      41
	                    taxonomy        NaN                                             VisibleEvent                    39
	                                    https://objectiv.io/docs/taxonomy/reference     VisibleEvent                    36
	                                    NaN                                             PressEvent                      34
	objectiv-website    about           https://objectiv.io/about                       PressEvent                      30
	objectiv-docs       taxonomy        NaN                                             ApplicationLoadedEvent          29
	                                    https://objectiv.io/docs/taxonomy/              ApplicationLoadedEvent          27
	                    home            https://objectiv.io/docs/home/quickstart-guide/ VisibleEvent                    26
	                    tracking        NaN                                             VisibleEvent                    25
	                    modeling        NaN                                             ApplicationLoadedEvent          24

.. admonition:: Reference
	:class: api-reference

	* :doc:`modelhub.SeriesGlobalContexts.gc <../open-model-hub/api-reference/SeriesGlobalContexts/modelhub.SeriesGlobalContexts.gc>`
	* :doc:`modelhub.SeriesLocationStack.ls <../open-model-hub/api-reference/SeriesLocationStack/modelhub.SeriesLocationStack.ls>`
	* :doc:`modelhub.Aggregate.unique_users <../open-model-hub/models/aggregation/modelhub.Aggregate.unique_users>`
	* :doc:`bach.DataFrame.sort_values <../bach/api-reference/DataFrame/bach.DataFrame.sort_values>`
	* :doc:`bach.Series.to_frame <../bach/api-reference/Series/bach.Series.to_frame>`


Understanding product features
------------------------------
For every event, Objectiv captures where it occurred in your product's UI, using a hierarchical stack of 
`LocationContexts </docs/taxonomy/location-contexts>`_. This means you can easily slice the data on any part 
of the UI that you're interested in. :doc:`See the open taxonomy notebook <./open-taxonomy>` for more details. 
It also means you can make product features very readable and easy to understand; see below how.

.. 
	The testsetup below sets the max_colwidth for this example, so it fits the code block.
	However, it has to re-instantiate `df` to be able to work, resetting the outputs before.
	Works in this case, but not a good solution in other cases. Didn't find something better yet.

.. testsetup:: explore-data-features
	:skipif: engine is None

	df = modelhub.get_objectiv_dataframe(
			db_url=DB_URL,
			start_date='2022-06-01',
			end_date='2022-06-30',
			table_name='data')
	pd.set_option('display.max_colwidth', 93)

.. doctest:: explore-data-features
	:skipif: engine is None

	>>> # add a readable product feature name to the dataframe as a column
	>>> df['feature_nice_name'] = df.location_stack.ls.nice_name

.. doctest:: explore-data-features
	:skipif: engine is None

	>>> # now easily look at the data by product feature
	>>> product_feature_data = modelhub.agg.unique_users(df, groupby=['feature_nice_name', 'event_type'])
	>>> product_feature_data.sort_values(ascending=False).to_frame().head(20)
	                                                                                                                       unique_users
	feature_nice_name                                                                              event_type 
	Root Location: home                                                                            ApplicationLoadedEvent           250
	Media Player: 2-minute-video located at Root Location: home => Content: modeling               MediaLoadEvent                   220
	Overlay: star-us-notification-overlay located at Root Location: home => Pressable: star-us...  VisibleEvent                     181
	                                                                                               HiddenEvent                       94
	Expandable: The Project located at Root Location: home => Navigation: docs-sidebar             VisibleEvent                      75
	Pressable: after located at Root Location: home => Content: capture-data => Content: data-...  PressEvent                        74
	Root Location: taxonomy                                                                        ApplicationLoadedEvent            58
	Expandable: the-project located at Root Location: home => Navigation: docs-sidebar             VisibleEvent                      55
	Pressable: after located at Root Location: home => Content: modeling => Content: modeling-...  PressEvent                        48
	Root Location: blog                                                                            ApplicationLoadedEvent            46
	Root Location: modeling                                                                        ApplicationLoadedEvent            45
	Link: about-us located at Root Location: home => Navigation: navbar-top                        PressEvent                        36
	Pressable: before located at Root Location: home => Content: capture-data => Content: data...  PressEvent                        35
	Expandable: reference located at Root Location: taxonomy => Navigation: docs-sidebar           VisibleEvent                      31
	Overlay: hamburger-menu located at Root Location: home => Navigation: navbar-top               VisibleEvent                      29
	Link: logo located at Root Location: home => Navigation: navbar-top                            PressEvent                        28
	Expandable: Reference located at Root Location: taxonomy => Navigation: docs-sidebar           VisibleEvent                      26
	Overlay: hamburger-menu located at Root Location: modeling => Navigation: navbar-top           VisibleEvent                      23
	Link: docs located at Root Location: home => Navigation: navbar-top                            PressEvent                        23
	Pressable: hamburger located at Root Location: home => Navigation: navbar-top                  PressEvent                        21

.. admonition:: Reference
	:class: api-reference

	* :doc:`modelhub.SeriesLocationStack.ls <../open-model-hub/api-reference/SeriesLocationStack/modelhub.SeriesLocationStack.ls>`
	* :doc:`modelhub.Aggregate.unique_users <../open-model-hub/models/aggregation/modelhub.Aggregate.unique_users>`
	* :doc:`bach.DataFrame.sort_values <../bach/api-reference/DataFrame/bach.DataFrame.sort_values>`
	* :doc:`bach.Series.to_frame <../bach/api-reference/Series/bach.Series.to_frame>`
	* :doc:`bach.DataFrame.head <../bach/api-reference/DataFrame/bach.DataFrame.head>`

Get the SQL for any analysis
----------------------------

Any dataframe or model built with Bach can be converted to an SQL statement with a single command to use 
directly in production.

.. doctest:: explore-data-features
	:skipif: engine is None

	>>> # show the underlying SQL for this dataframe - works for any dataframe/model in Objectiv
	>>> display_sql_as_markdown(product_feature_data)
	sql
	with "from_table___7a4057e80babeec1c65913e0a773d65d" as (SELECT "value","event_id","day","moment","cookie_id" FROM "data"),
	"getitem_where_boolean___fed67ee9d11d7631154f62679fc36a5b" as (select "value" as "value", "event_id" as "event_id", "day" as "day", "moment" as "moment", "cookie_id" as "user_id", "value"->>'_type' as "event_type", cast("value"->>'_types' as jsonb) as "stack_event_types", cast("value"->>'global_contexts' as jsonb) as "global_contexts", cast("value"->>'location_stack' as jsonb) as "location_stack", cast("value"->>'time' as bigint) as "time"
	from "from_table___7a4057e80babeec1c65913e0a773d65d"
	where ((("day" >= '2022-06-01')) AND (("day" <= '2022-06-30')))
	<BLANKLINE>
	<BLANKLINE>
	<BLANKLINE>
	<BLANKLINE>
	),
	"context_data___8b8b8232f369c68f2d1d5f3a9af30be5" as (select "event_id" as "event_id", "day" as "day", "moment" as "moment", "user_id" as "user_id", "global_contexts" as "global_contexts", "location_stack" as "location_stack", "event_type" as "event_type", "stack_event_types" as "stack_event_types"
	from "getitem_where_boolean___fed67ee9d11d7631154f62679fc36a5b"
	<BLANKLINE>
	<BLANKLINE>
	<BLANKLINE>
	<BLANKLINE>
	<BLANKLINE>
	),
	"session_starts___7f4511d848754e3b2c429cd717af7fd8" as (select "event_id" as "event_id", "day" as "day", "moment" as "moment", "user_id" as "user_id", "global_contexts" as "global_contexts", "location_stack" as "location_stack", "event_type" as "event_type", "stack_event_types" as "stack_event_types", CASE WHEN (extract(epoch from (("moment") - (lag("moment", 1, cast(NULL as timestamp without time zone)) over (partition by "user_id" order by "moment" asc, "event_id" asc RANGE BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW)))) <= cast(1800 as bigint)) THEN cast(NULL as boolean) ELSE cast(True as boolean) END as "is_start_of_session"
	from "context_data___8b8b8232f369c68f2d1d5f3a9af30be5"
	<BLANKLINE>
	<BLANKLINE>
	<BLANKLINE>
	<BLANKLINE>
	<BLANKLINE>
	),
	"session_id_and_count___1af1add976fc49285147ee0f7d855082" as (select "event_id" as "event_id", "day" as "day", "moment" as "moment", "user_id" as "user_id", "global_contexts" as "global_contexts", "location_stack" as "location_stack", "event_type" as "event_type", "stack_event_types" as "stack_event_types", "is_start_of_session" as "is_start_of_session", CASE WHEN "is_start_of_session" THEN row_number() over (partition by "is_start_of_session" order by "moment" asc, "event_id" asc RANGE BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) ELSE cast(NULL as bigint) END as "session_start_id", count("is_start_of_session") over ( order by "user_id" asc, "moment" asc, "event_id" asc RANGE BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) as "is_one_session"
	from "session_starts___7f4511d848754e3b2c429cd717af7fd8"
	<BLANKLINE>
	<BLANKLINE>
	<BLANKLINE>
	<BLANKLINE>
	<BLANKLINE>
	),
	"objectiv_sessionized_data___8ca784e7c855c8358b3d7d48507f91b3" as (select "event_id" as "event_id", "day" as "day", "moment" as "moment", "user_id" as "user_id", "global_contexts" as "global_contexts", "location_stack" as "location_stack", "event_type" as "event_type", "stack_event_types" as "stack_event_types", "is_start_of_session" as "is_start_of_session", "session_start_id" as "session_start_id", "is_one_session" as "is_one_session", first_value("session_start_id") over (partition by "is_one_session" order by "moment" asc, "event_id" asc RANGE BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) as "session_id", row_number() over (partition by "is_one_session" order by "moment" asc, "event_id" asc RANGE BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) as "session_hit_number"
	from "session_id_and_count___1af1add976fc49285147ee0f7d855082"
	<BLANKLINE>
	<BLANKLINE>
	<BLANKLINE>
	<BLANKLINE>
	<BLANKLINE>
	)
	select (
											select string_agg(
															replace(
																	regexp_replace(value ->> '_type', '([a-z])([A-Z])', '\1 \2', 'g'),
																	' Context',
																	''
															) || ': ' || (value ->> 'id'),
															' => ')
											from jsonb_array_elements("location_stack") with ordinality
											where ordinality = jsonb_array_length("location_stack")
									) || (
											case when jsonb_array_length("location_stack") > 1
														then ' located at ' || (select string_agg(
																	replace(
																			regexp_replace(value ->> '_type', '([a-z])([A-Z])', '\1 \2', 'g'),
																			' Context',
																			''
																	) || ': ' || (value ->> 'id'),
																	' => ')
															from jsonb_array_elements("location_stack") with ordinality
															where ordinality < jsonb_array_length("location_stack")
													)
													else '' end
									) as "feature_nice_name", "event_type" as "event_type", count(distinct "user_id") as "unique_users"
	from "objectiv_sessionized_data___8ca784e7c855c8358b3d7d48507f91b3"
	<BLANKLINE>
	group by (
											select string_agg(
															replace(
																	regexp_replace(value ->> '_type', '([a-z])([A-Z])', '\1 \2', 'g'),
																	' Context',
																	''
															) || ': ' || (value ->> 'id'),
															' => ')
											from jsonb_array_elements("location_stack") with ordinality
											where ordinality = jsonb_array_length("location_stack")
									) || (
											case when jsonb_array_length("location_stack") > 1
														then ' located at ' || (select string_agg(
																	replace(
																			regexp_replace(value ->> '_type', '([a-z])([A-Z])', '\1 \2', 'g'),
																			' Context',
																			''
																	) || ': ' || (value ->> 'id'),
																	' => ')
															from jsonb_array_elements("location_stack") with ordinality
															where ordinality < jsonb_array_length("location_stack")
													)
													else '' end
									), "event_type"
	<BLANKLINE>
	<BLANKLINE>
	<BLANKLINE>
	<BLANKLINE>
	<BLANKLINE>

Where to go next
----------------

Now that you've had a first look at your new data collected with Objectiv, the best next step is to 
:doc:`see the basic product analytics example notebook <./product-analytics>`. It shows you to how to easily 
get product analytics metrics straight from your raw Objectiv data.