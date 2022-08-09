.. _funnel_discovery:

.. frontmatterposition:: 6

.. currentmodule:: bach

.. testsetup:: funnel-discovery
	:skipif: engine is None

	df = modelhub.get_objectiv_dataframe(
			db_url=DB_URL,
			start_date='2022-02-01',
			end_date='2022-06-30',
			table_name='data')
	pd.set_option('display.max_colwidth', 93)

================
Funnel Discovery
================

This example notebook shows how to use the 'Funnel Discovery' model on your data collected with Objectiv. 
It's also available as a `full Jupyter notebook 
<https://github.com/objectiv/objectiv-analytics/blob/main/notebooks/funnel-discovery.ipynb>`_
to run on your own data (see how to :doc:`get started in your notebook <../get-started-in-your-notebook>`), 
or you can instead `run the Demo </docs/home/quickstart-guide/>`_ to quickly try it out. The dataset used 
here is the same as in the Demo.

Get started
-----------
We first have to instantiate the model hub and an Objectiv DataFrame object.

.. doctest:: funnel-discovery
	:skipif: engine is None

	>>> # instantiate the model hub, and set the default time aggregation to daily
	>>> from modelhub import ModelHub
	>>> modelhub = ModelHub(time_aggregation='%Y-%m-%d')
	>>> # get an Objectiv DataFrame within a defined timeframe
	>>> df = modelhub.get_objectiv_dataframe(db_url=DB_URL, start_date='2022-02-01', end_date='2022-06-30')

.. doctest:: funnel-discovery
	:skipif: engine is None

	>>> # add specific contexts to the data as columns
	>>> df['application'] = df.global_contexts.gc.application
	>>> df['feature_nice_name'] = df.location_stack.ls.nice_name

.. doctest:: funnel-discovery
	:skipif: engine is None

	>>> # select which event type to use for further analysis - PressEvents to focus on what users directly interact with
	>>> df = df[df['event_type'] == 'PressEvent']

.. admonition:: Reference
	:class: api-reference

	* :doc:`modelhub.ModelHub.get_objectiv_dataframe <../open-model-hub/api-reference/ModelHub/modelhub.ModelHub.get_objectiv_dataframe>`
	* :doc:`modelhub.SeriesGlobalContexts.gc <../open-model-hub/api-reference/SeriesGlobalContexts/modelhub.SeriesGlobalContexts.gc>`
	* :doc:`modelhub.SeriesLocationStack.ls <../open-model-hub/api-reference/SeriesLocationStack/modelhub.SeriesLocationStack.ls>`


First: define what is conversion
--------------------------------
As a prerequisite for Funnel Discovery, define the events you see as conversion.

In this example we will view someone as converted when they go on to read the documentation from our website, 
but you can 
:doc:`use any event <../open-model-hub/api-reference/ModelHub/modelhub.ModelHub.add_conversion_event>`

.. doctest:: funnel-discovery
	:skipif: engine is None

	>>> # define which data to use as conversion events; in this example, anyone who goes on to read the documentation
	>>> df['is_conversion_event'] = False
	>>> df.loc[df['application'] == 'objectiv-docs', 'is_conversion_event'] = True

Out of curiosity, let's see which features are used by users that converted, sorted by their conversion impact.

.. doctest:: funnel-discovery
	:skipif: engine is None

	>>> # calculate the percentage of converted users per feature: (converted users per feature) / (total users converted)
	>>> total_converted_users = df[df['is_conversion_event']]['user_id'].unique().count().value
	>>> top_conversion_locations = modelhub.agg.unique_users(df[df['is_conversion_event']], groupby='feature_nice_name')
	>>> top_conversion_locations = (top_conversion_locations / total_converted_users) * 100
	>>> 
	>>> # show the results, with .to_frame() for nicer formatting
	>>> top_conversion_locations = top_conversion_locations.to_frame().rename(columns={'unique_users': 'converted_users_percentage'})
	>>> top_conversion_locations.sort_values(by='converted_users_percentage', ascending=False).head()
																																										converted_users_percentage
	feature_nice_name	
	Link: Quickstart Guide located at Root Location: home => Navigation: docs-sidebar	                 15.946844
	Link: logo located at Root Location: home => Navigation: navbar-top                                10.797342
	Link: Tracking located at Root Location: home => Navigation: navbar-top                            10.631229
	Link: Taxonomy located at Root Location: modeling => Navigation: navbar-top                        10.299003
	Link: Modeling located at Root Location: tracking => Navigation: navbar-top                        9.966777
