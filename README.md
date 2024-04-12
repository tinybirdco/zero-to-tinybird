# The Zero-to-Tinybird Workshop 

This repository is a companion piece to the 'Zero-to-Tinybird` 90-minute workshop. The intended audience of this workshop are people who have no experience with Tinybird and are looking to learn the basics with 90 minutes of hands on content. The intent of this workshop is to teach the basics of creating Data Sources, building Pipes, designing Materialized Views, deploying API Endpoints with dynamic query parameters, and providing introductions to the Tinybird command-line interface (CLI) and working with Tinybird projects under version control. 

This repository includes resources to help attendees find documentation and other content focused on these topics. It also includes the Data Project used in the workshop. Workshop content is based on a real-time stream of mocked stock prices and a supporting dimensional table of company metadata. 

## Workshop sections

* Tinybird overview
* [Creating Data Sources](/content/sections/creating-data-sources.md)
* [Building data analysis pipelines](/content/sections/building-pipelines.md)
* [Introduction to Materialized Views](/content/sections/materialized-views.md)
* [Introduction to the Tinybird CLI](/content/sections/intro-to-cli.md)

## Prerequisites

* A free Tinybird account. Navigate to [tinybird.co/signup](https://www.tinybird.co/signup) and create a free account. Create a new Workspace (name it whatever you want).
* Basic knowledge of SQL, querying concepts, and the fundamentals of API endpoint design.

## Other resources:

* [Reference project GitHub Repository](https://github.com/jimmoffitt/kafka-to-analytics) - An example end-state of the project we will build. Complete with:
  * [Recent Pull request and branch history](https://github.com/jimmoffitt/kafka-to-analytics/pulls?q=is%3Apr+is%3Aclosed)
  * [GitHub Actions managed by Tinybird CI/CD integration](https://github.com/jimmoffitt/kafka-to-analytics/actions)
* Below you will find a PDF of the deck we used for our first workshop on February 13, 2024. 

## What are we building? 

For the workshop project we will start off and building on two data sources:

* `company_info` dimensional table with company metadata, including full name, creation date, economic sector, and stock symbol.

* `event_stream` live stream of stock prices for a set of ~80 mock companies. These prices are reported every few seconds and published on a Kafka-based stream hosted on Confluent Cloud. 

![Here is an example time-series](images/com.com.png)

This project includes the Python script used to generate the real-time data stream.  

Our intial **Tinybird data flow** will look like this: 

![Data flow diagram](images/data-flow-2.png)

Here we have the two *Data Sources*, and three data 'pipelines' based on them. These Tinybird *Pipes* illustrate fundamental SQL transformations: filtering, aggregating, and joining data sources. 

Then we will create a Materialized View to provide hourly statistics:

![Data flow diagram](images/data-flow-1.png)

## What topics will we be covering? 

* Creating Data Sources
  * Introduction to native connectors: Kafka/Confluent streams, AWS S3, BigQuery, and Snowflake.
  * Importing dimensional/fact tables. 
  * Connecting to a Confluent stream of real-time (mocked) stock prices. 

    [See more here.](/content/sections/creating-data-sources.md)

* Building data analysis pipelines
  * Getting started by developing SQL queries in Playgrounds.
  * Building our first Pipe and publishing an API Endpoint.
  * Building Pipes that filter, aggregate and join Data Sources.
  * Creating dynamic request parameters.   

    [See more here.](/content/sections/building-pipelines.md)

* Introduction to Materialized Views
    * Purpose and example use cases.
    * Improving performance by filtering and aggregating at ingest time, not query time. 
    * Temporal rollups.
    * State/Merge functions. 

    [See more here.](/content/sections/materialized-views.md)

* Introduction to the Tinybird CLI
  * Installing the CLI.
  * Exploring our Workspace with the CLI.
  * Touring available commands and preparing for managing projects under version control.

    [See more here.](/content/sections/intro-to-cli.md)

* Using version control with data projects
  * Read our blog post describing [why we built version control features into Tinybird](https://www.tinybird.co/blog-posts/version-control-for-real-time-data). 

    
    [See more here.](/content/sections/version-control.md)


## Workshop deck

![](images/deck.png)

[Workshop deck from March 28, 2024](/content/Kafka-to-Analytics-workshop.pdf)
[Workshop deck from February 13, 2024](/content/Kafka-to-Analytics-workshop.pdf)





