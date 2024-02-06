### Creating Data Sources

Screencasts:

* [Ingest data from a file](https://youtu.be/1R0G1EolSEM)
* [Generate mock data streams for your next data project]()
* [Stream data using the Events API]()
* [Sync BigQuery tables to Tinybird]()
* [Edit a Data Source schema with the CLI](https://youtu.be/gzpuQfk3Byg)
* [Sync files from S3 into Tinybird](https://youtu.be/JIo50NGc-BA)

Documentation:

* [Core concept](https://www.tinybird.co/docs/main-concepts.html#data-sources)
* [Data Sources API](https://www.tinybird.co/docs/ingest/datasource-api.html)
* [Events API](https://www.tinybird.co/docs/ingest/events-api.html)


* The `event_stream` data stream has this concise data schema:

```
`id` Int16 
`price` Float32 
`symbol` String 
`timestamp` DateTime 
```
 
* The `company_info` 'dimensional' (or 'fact') table containing metadata for a set of ~80 companies, including their full name, creation date, sector, and stock symbol.

```
`symbol` String
`name` String
`creation_date` Date
`sector` LowCardinality(String)
```
