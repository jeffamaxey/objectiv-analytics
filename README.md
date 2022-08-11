<img src="https://user-images.githubusercontent.com/82152911/159266790-19e0e3d4-0d10-4c58-9da7-16edde9ec05a.svg#gh-light-mode-only" alt="objectiv_logo_light" title="Objectiv Logo">
<img src="https://user-images.githubusercontent.com/82152911/159266895-39f52604-83c1-438d-96bd-9a6d66e74b08.svg#gh-dark-mode-only" alt="objectiv_logo_dark" title="Objectiv Logo">


[Objectiv](https://objectiv.io/) is open-source infrastructure for product analytics modeling. Collect data with an event structure designed for modeling and quickly build & run custom product analytics models that run on the full dataset and are reusable between platforms & projects.

### Go to

* [Demo notebooks](https://objectiv.io/docs/modeling/example-notebooks) - See Objectiv in action
* [Objectiv Docs](https://www.objectiv.io/docs) - Technical documentation.
* [Objectiv on Slack](https://objectiv.io/join-slack) - Learn & share about Objectiv and product analytics modeling.

---

## What's in the box?

Objectiv includes everything you need to build & run state-of-the-art product analytics models in minutes. Data collection & modeling were developed in close conjunction to ensure datasets carry the structure and information required for effective modeling. As a result, you can quickly build & run models straight on the full, raw dataset without any prepwork.

![objectiv_stack](https://user-images.githubusercontent.com/920184/180789710-94e7bf9c-f081-4a0f-9637-3edf6fe5f501.svg#gh-light-mode-only "Objectiv Stack")
![objectiv_stack_dark](https://user-images.githubusercontent.com/920184/180790336-4143f099-dee3-4e83-8fb2-5a71d35169bb.svg#gh-dark-mode-only "Objectiv Stack")

### The open analytics taxonomy

Objectiv is built around an [open analytics taxonomy](https://www.objectiv.io/docs/taxonomy): a universal structure for analytics data, so models built on one dataset can be deployed and run on another.

[![taxonomy](https://user-images.githubusercontent.com/82152911/162000133-1eea0192-c882-4121-a866-8c1a3f8ffee3.svg)](https://www.objectiv.io/docs/taxonomy)

It's designed and tested with UIs and analytics use cases of over 50 companies. Areas like payments & CRM are on the roadmap, and it's extensible to cover custom use cases.

### Tracking SDKs

Supports front-end engineers to [implement tracking instrumentation](https://www.objectiv.io/docs/tracking) that embraces the open analytics taxonomy.

* Provides validation and end-to-end testing tooling to set up error-free instrumentation.
* Support for React, React Native, Angular & JS, and expanding.
 
### Open model hub

A [growing collection of pre-built models and functions](https://objectiv.io/docs/modeling/open-model-hub/), so you can take and run what someone else made, or quickly build your own with pre-built models and functions.

* Covers a wide range of use cases: from basic product analytics to predictive analysis with ML.
* Works with any dataset that embraces the open analytics taxonomy.
* New models & functions are added continuously.

### Bach modeling library

Python-based [modeling library](https://www.objectiv.io/docs/modeling/bach/) that enables using pandas-like operations on the full SQL dataset.

* Includes specific operations to easily work with datasets that embrace the open analytics taxonomy.
* Pandas-compatible: use popular pandas ML libraries in your models.
* Output models to production SQL directly, to simplify data debugging & delivery to BI tools, dbt, etc. 

---

## Compatible data stores

Objectiv currently supports PostgreSQL and Google BigQuery (through Snowplow), with Amazon Athena next, and more data stores coming.

## Get started

1. Install the open model hub from PyPI:

```sh
pip install objectiv-modelhub
```

2. [Read how to get started in your notebook](https://objectiv.io/docs/modeling/get-started-in-your-notebook/) in the docs.

---

For more information, visit [objectiv.io](https://www.objectiv.io) or [Objectiv Docs](https://www.objectiv.io/docs) - Objectiv's official documentation..

---

This repository is part of the source code for Objectiv, which is released under the Apache 2.0 License. Please refer to [LICENSE.md](LICENSE.md) for details.
