# The Zero-to-Tinybird Workshop 

This repository is a companion piece to the 'Zero-to-Tinybird` 90-minute workshop. The intended audience of this workshop are people who have no experience with Tinybird and are looking to learn the basics with 90 minutes of hands on content. The intent of this workshop is to teach the basics of creating Data Sources, building Pipes, designing Materialized Views, deploying API Endpoints with dynamic query parameters, and providing introductions to the Tinybird command-line interface (CLI) and Tinybird Versions. 

This repository includes resources to help attendees find documentation and other content focused on these topics. It also includes the Data Project used in the workshop. 

## Workshop sections

* Tinybird overview
* Creating Data Sources
* Building data analysis pipelines
* Materialized Views
* An introduction to the Tinybird CLI
* An introduction to Tinybird Versions

## Prerequisites

* A free Tinybird account. Navigate to [tinybird.co/signup](https://www.tinybird.co/signup) and create a free account. Create a new Workspace (name it whatever you want).
* Basic knowledge of SQL, querying concepts, and the fundamentals of API Endpoint design.

## Section details

### Tinybird overview
  * What is Tinybird?
  * Key Tinybird features. 
  * Why use Tinybird? Benefits of using Tinybird to implement build real-time architectures.
  * Tinybird glossary of terms, establish a common nomenclature for discussing real-time data and event-driven architectures. 

### Creating Data Sources
  * Introduction to native connectors: Kafka/Confluent streams, AWS S3, BigQuery, and Snowflake.
  * Importing dimensional/fact tables. 
  * Importing data with the Events API. 
  * Using Mockingbird to create real-time event streams.

### Building data analysis pipelines
  * Getting started by developing SQL queries in Playgrounds.
  * Building our first Pipe and publishing an API Endpoint.
  * Building Pipes that filter, aggregate and join Data Sources.
  * Creating dynamic request parameters.   

### Materialized Views
  * Purpose and example use cases.
    * Filtering and aggregating at ingest time, not query time. Temporal rollups.
  * State/Merge functions. 

### An introduction to the Tinybird CLI
  * Exploring our Workspace with the CLI.
  * Pulling Workspace resources to work with locally. 
  * Adding another Pipe and pushing to Tinybird. 

### An introduction to Tinybird Versions
  * The whys and hows of Versions.
  * Demonstrating adding new features in a development Environment, and using Git pull requests to trigger CI/CD testing and deployment. 
