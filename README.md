<img src="https://user-images.githubusercontent.com/82152911/159266790-19e0e3d4-0d10-4c58-9da7-16edde9ec05a.svg#gh-light-mode-only" alt="objectiv_logo_light" title="Objectiv Logo">
<img src="https://user-images.githubusercontent.com/82152911/159266895-39f52604-83c1-438d-96bd-9a6d66e74b08.svg#gh-dark-mode-only" alt="objectiv_logo_dark" title="Objectiv Logo">


[Objectiv](https://objectiv.io/) is an integrated set of data collection and modeling tools to quickly build & run models for any product analytics use case.

Self-hosted, free to use & open-source.

---

## Getting started

1. Install the open model hub from PyPI:

```sh
pip install objectiv-modelhub
```

2. [Read how to get started in your notebook](https://objectiv.io/docs/modeling/get-started-in-your-notebook/) in the docs.

### See also:

* [Demo notebooks](https://objectiv.io/docs/modeling/example-notebooks) - See Objectiv in action.
* [Objectiv Docs](https://www.objectiv.io/docs) - Technical documentation.
* [Objectiv on Slack](https://objectiv.io/join-slack) - Learn & share about Objectiv and product analytics modeling.

---

## What's in the box?

* **A taxonomy** to give your datasets a generic & strict event structure designed for modeling.
* **Tracking SDKs** for modern front-end frameworks to collect error-free user behavior data.
* **An open model hub** with pre-built product analytics models & operations.
* **A modeling library** to create reusable models that run on your full dataset.

![objectiv_stack](https://user-images.githubusercontent.com/82152911/184146312-dca08dfc-33b9-4f3a-8356-2f0ff8563b1d.svg#gh-light-mode-only "Objectiv Stack")
![objectiv_stack_dark](https://user-images.githubusercontent.com/82152911/184146420-92ac1db7-4b09-476c-abc5-c67d5a970c75.svg#gh-dark-mode-only "Objectiv Stack")

### The open analytics taxonomy

Objectiv is built around an [open analytics taxonomy](https://www.objectiv.io/docs/taxonomy): a universal structure for analytics data that has been designed and tested with UIs and analytics use cases of over 50 companies. It ensures your dataset covers a wide range of common analytics use cases and is structured with modeling in mind. You can extend it to cover custom requirements as well.

[![taxonomy](https://user-images.githubusercontent.com/82152911/162000133-1eea0192-c882-4121-a866-8c1a3f8ffee3.svg)](https://www.objectiv.io/docs/taxonomy)

Datasets that embrace the taxonomy are highly consistent. As a result, models built on one dataset can be deployed and run on another.

We're continuously expanding the coverage of the open analytics taxonomy. Support for marketing campaign analysis has been added recently, and areas like payments & CRM are on the roadmap.

### Tracking SDKs

Supports front-end engineers to [implement tracking instrumentation](https://www.objectiv.io/docs/tracking) that embraces the open analytics taxonomy.

* Provides validation and end-to-end testing tooling to set up error-free instrumentation.
* Support for React, React Native, Angular & JS, and expanding.
 
### Open model hub

A [growing collection of pre-built product analytics models and functions](https://objectiv.io/docs/modeling/open-model-hub/). You can take and run them directly, or incorporate them into your own custom models.

* Covers a wide range of use cases: from basic product analytics to predictive analysis with ML.
* Works with any dataset that embraces the open analytics taxonomy.
* New models & functions are added continuously.

### Bach modeling library

A pandas-like [modeling library](https://www.objectiv.io/docs/modeling/bach/) to build models that run on the full SQL dataset.

* Includes specific operations to easily work with datasets that embrace the open analytics taxonomy.
* Pandas-compatible: use popular pandas ML libraries in your models.
* Output models to production SQL directly, to simplify data debugging & delivery to BI tools, dbt, etc. 

---

## Compatible data stores

Objectiv currently supports PostgreSQL and Google BigQuery (through Snowplow).  Amazon Athena is next, and more data stores coming.

---

This repository is part of the source code for Objectiv, which is released under the Apache 2.0 License. Please refer to [LICENSE.md](LICENSE.md) for details.
