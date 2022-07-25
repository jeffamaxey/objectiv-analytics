<img src="https://user-images.githubusercontent.com/82152911/159266790-19e0e3d4-0d10-4c58-9da7-16edde9ec05a.svg#gh-light-mode-only" alt="objectiv_logo_light" title="Objectiv Logo">
<img src="https://user-images.githubusercontent.com/82152911/159266895-39f52604-83c1-438d-96bd-9a6d66e74b08.svg#gh-dark-mode-only" alt="objectiv_logo_dark" title="Objectiv Logo">


[Objectiv](https://objectiv.io/) is ready-to-use infrastructure for advanced product analytics. Collect the best data for modeling, validate your tracking instrumentation, and run pre-built open-source models straight on your data warehouse.

Self hosted, open-source & built for those who like their data raw and models in code.

### Demo

Follow our [Quickstart Guide](https://objectiv.io/docs/home/quickstart-guide) to set up a fully functional dockerized demo in under 5 minutes.

### Go to

* [Objectiv Docs](https://www.objectiv.io/docs) - Objectiv's official documentation.
* [Objectiv on Slack](https://objectiv.io/join-slack) - Get help & join the discussion on where to take Objectiv next.
* [Objectiv.io](https://www.objectiv.io) - Objectiv's official website.

---

## What's in the box?
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

---

For more information, visit [objectiv.io](https://www.objectiv.io) or [Objectiv Docs](https://www.objectiv.io/docs) - Objectiv's official documentation..

---

This repository is part of the source code for Objectiv, which is released under the Apache 2.0 License. Please refer to [LICENSE.md](LICENSE.md) for details.
