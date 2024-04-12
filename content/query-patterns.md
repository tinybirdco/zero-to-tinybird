# Query patterns

A collection of SQL patterns. An evolving WIP... 



## Data schema

Project SQL examples are built with two simple data schemas that describe the data sets used in the workshop. 

`event_stream` - a real-time stream of (mock) stock price events generated with a Python script, publishing to either a Kafka stream or writing event JSON directly to Tinybird using the Events API. 

```
`price` Float32 `json:$.price` ,
`timestamp` DateTime `json:$.timestamp` ,
`symbol` String `json:$.symbol` ,
```

`company_info` - Mock data about ~85 fictional companies. These metadata is imported into a Tinybird Data Source at the beginning of the Workshop. 

```
`symbol` String,
`name` String,
`creation_date` Date,
`sector` String,
```
The common attribute `symbol` is used to JOIN the two data sources. 

## Working with time

Real-time event data are based on date and time objects. When working with real-time events, the time of when the event happened is integral to vast majority of all questions asked of the data. How many times has something happened in that month, day, hour, minute, or second? How have the temporal patterns of an event evolved and formed over time?  

So, most of the queries you build in Tinybird will have time details built into them. To gain a wide prespective of how to work with timetamps in Tinybird, these guides are critical:
* https://www.tinybird.co/docs/guides/working-with-time.html
* https://www.tinybird.co/docs/guides/best-practices-for-timestamps.html

Note:
* The sooner you standardize on the UTC timezone for all things time, the better. Let the client display composer convert to local time if needed. If you are working with data generators, push the data already in UTC. For example, with Python, be sure to generate timestamps in UTC (`current_time = datetime.datetime.utcnow()`). 
* ClickHouse provides a set of time functions that make working with time data easier. Like most data environments, ClickHouse supports both Date and DateTime objects. Check out [this ClickHouse guide](https://clickhouse.com/docs/en/sql-reference/functions/date-time-functions) for the details (tere is also this ClickHouse [blog post](https://clickhouse.com/blog/working-with-time-series-data-and-functions-ClickHouse). Functions such as [toStartOfDay](https://clickhouse.com/docs/en/sql-reference/functions/date-time-functions#tostartofmonth) are fantastic for binning and processing time-series data. If you have ever needed to bin time data in SQL, you will really appreciate these functions.
* Your Tinybird will be configured to store data in UTC. 


### Go-to functions for working with time fields

* toDateTime(date)
* parseDateTimeBestEffort
* parseDateTimeBestEffortOrZero
* parseDateTimeBestEffortOrNull

[Learn more about the ClickHouse `parseDataTime` functions](https://clickhouse.com/docs/en/sql-reference/functions/type-conversion-functions#type_conversion_functions-parseDateTime).


### Time query patterns

#### Data from the most recent hour

```sql
SELECT symbol, timestamp, price  
FROM event_stream
WHERE timestamp >= NOW() - INTERVAL 1 HOUR
```

```sql
SELECT symbol, timestamp, price  
FROM event_stream
WHERE timestamp BETWEEN addHours(NOW(),-1) AND NOW()
```



#### Data between explicit dates
```sql
SELECT symbol, timestamp, price  
FROM event_stream
WHERE toDateTime(date) BETWEEN '2023-12-07 17:22:00' AND '2023-12-07 17:23:00'
```

#### Data from yesterday, midnight to midnight

This SQL uses ClickHouse `today`,`yesterday`, and `toStartofDate` functions.

```sql
SELECT symbol, timestamp, price 
FROM event_stream
WHERE
  timestamp >= toStartOfDay(toDateTime(yesterday()))
  AND timestamp < toStartOfDay(toDateTime(today()))
LIMIT 10000
```




#### Selecting most recent data 

To detect timeouts, the most recent data point from each sensor is looked up. This sounds simple enough, and it is one of the most simple detection methods. Like many things, there is more than one way to look most recent data.    

The following query sorts the data in reverse chronological order, and uses the `LIMIT BY` command to look up the most recent single (LIMIT 1) data for each sensor.

```sql

SELECT * 
FROM event_stream
ORDER BY timestamp DESC
LIMIT 1 BY id

```

Here is another SQL query for looking up the most recent data, which scans over partitions and also scans in reverse chronological order.  

```sql
WITH RankedData AS (
    SELECT
        id,
        timestamp,
        value,
        ROW_NUMBER() OVER (PARTITION BY id ORDER BY timestamp DESC) AS row_num
    FROM
        event_stream
)
SELECT
    id,
    timestamp,
    value
FROM
    RankedData
WHERE
    row_num = 1
```

These queries do not narrow down the time range of interest. With anomaly detection and real-time data, we typically have a set of *time windows* of interest. In general, our time range of interest ranged from data from the most recent 10 seconds, to generating statistics over the previous thirty minutes.

#### Scanning periods of interext

If you have a data source with sensors that normally report every few seconds, it's likely that going ten seconds without a new report is a sign that a sensor is off-line. 

To focus only on the last ten seconds of data the following WHERE clause can be added to each query (inside the inner RankedData query for the second example). 

```sql
WHERE timestamp > NOW() - INTERVAL 10 SECOND
```

When it comes to *timeout* anomalies, we wanted a system that would detect if a sensor stopped reporting in the past minute. Our data source emits data every few seconds for each sensor, so we started off with a system that would identify sensors that had not reported in the last minute. 

We also wanted to provide an API Endpoint for ad hoc timeout checks that supported the following query parameters:

* **seconds** - The 'timeout' duration in seconds. How many seconds since a sensor reporting gets you worried? 
* **time_window_minutes** - How many minutes to 'look back' from 'now'.
* **sensor_id** - Test on a sensor-by-sensor basis.

This [example Pipe file](https://github.com/tinybirdco/anomaly-detection/blob/main/data-project/pipes/timeout.pipe) illustrates how to build these dynamic parameters into the queries. 

#### Providing flexible query parameters

Tinybird provides a *templating* syntax for building *dynamic* query parameters into your Tinybird API Endpoints. As you design your API endpoints, it is important to consider how your users will want to specify important attributes of the objects your API is serving. 

When it comes to time, users typically want to pick a time *period* of interest, defined by start and end times. Four common modes for time requests include having the following start and end times provided:

+ Both start and end times. The user has specific time period of interest, and typically uses a second resolution. 
+ No start and end times. The most recent data is usually implied and it's up to the server to enforce limits. This usually means declaring a maximum duration to server, e.g. the last day, week, or month. Some maximum number of objects to return is recommended. 
+ Only start time. The user has a specific beginning time in mind, the beginning of some event of interest. 
+ Only end time. The user has a specific end of an event in mind, and wants data leading up to it. 

Here is a example template for providing these time request conventions. Here we support the convention of serving a maximum of 30 days if the user does not specify a start or end time. 

```sql
{% if defined(start_time) and defined(end_time) %}
   AND toDateTime(timestamp) BETWEEN parseDateTimeBestEffort({{ DateTime(start_time, description="'YYYY-MM-DD HH:mm:ss'. UTC. Optional and defaults to 30 days ago. Defines the start of the period of interest. ") }}) AND parseDateTimeBestEffort({{ DateTime(end_time, description="'YYYY-MM-DD HH:mm:ss'. UTC. Optional and defaults to time of request. Defines the end of the period of interest.") }})
{% end %}

{% if not defined(start_time) and not defined(end_time) %}
   AND toDateTime(timestamp) BETWEEN addDays(now(),-30) AND now()
{% end %}

{% if defined(start_time) and not defined(end_time) %}
   AND toDateTime(timestamp) BETWEEN parseDateTimeBestEffort({{ DateTime(start_time) }}) AND addDays(toDateTime(parseDateTimeBestEffort({{DateTime(start_time)}}),30)
{% end %}

{% if not defined(start_time) and defined(end_time) %}
   AND toDateTime(timestamp) BETWEEN addDays(toDateTime(parseDateTimeBestEffort({{DateTime(end_time)}}),-30) AND parseDateTimeBestEffort({{ DateTime(end_time) }})
{% end %}
```

p.s. Always use UTC. 

## JOIN patterns

Tinybird is built to help users unify their data sources. Our users want to combine their data sources in Tinybird so they can blend it all into their analysis and output. One of the most fundamental use cases for Tinybird is *enriching real-time data* with dimensional data. This is all made possible by *joining* the data. When you *JOIN* data in SQL you are linking, mapping, and associating common data attributes from two or more sources. 

### Explicit JOIN
```sql
SELECT es.timestamp, ci.symbol, es.price, ci.name, ci.sector
FROM company_info ci
JOIN event_stream es
ON ci.symbol = es.symbol
LIMIT 100
```

### Implicit JOIN
This form does not enable you to set the 'left' and 'right' JOINs, which is important when you have a high-volume event table and small dimensional tables.

```sql
SELECT es.timestamp, ci.symbol, es.price, ci.name, ci.sector
FROM company_info ci, event_stream es
WHERE ci.symbol = sps.symbol
LIMIT 100
```

## Calculating slope

Developing a recipe for calculating data slopes or rates of change is surprisingly complicated (at least to me). To calculate the slope of two consectutive data points depends on *window* functions. The recipe below depends on the ClickHouse `lagInFrame` function (See this discussion on [ClickHouse window functions](https://clickhouse.com/docs/en/sql-reference/window-functions#functions)), which requires the construction of time window specification, e.g. `(PARTITION BY symbol ORDER BY date ASC ROWS BETWEEN 1 PRECEDING AND 1 PRECEDING)`.

The general form looks like the following: 
 (**PARTITION BY** partition_columns_list [**ORDER BY** order_by_columns_list] frame_specification)

    Where: `frame_specification` in this case selects the previous, single value:  `ROWS BETWEEN 1 PRECEDING AND 1 PRECEDING`


```sql
%
{% set time_window_minutes=30 %}
{% set max_slope=3 %}

SELECT symbol, 
date, 
previous_timestamp,
(amount - previous_amount) / (date - previous_date) as slope,
amount, 
previous_amount,
(amount - previous_amount) as amount_diff,
(date - previous_date) as time_diff,
{{Int16(max_slope, 3, description="Integer. Maximum slope, any higher than this are returned.")}} as max_slope,
lagInFrame(timestamp, 1) OVER 
(PARTITION BY symbol ORDER BY date ASC ROWS BETWEEN 1 PRECEDING AND 1 PRECEDING) AS previous_date, 
lagInFrame(amount, 1) 
OVER (PARTITION BY symbol ORDER BY date ASC ROWS BETWEEN 1 PRECEDING AND 1 PRECEDING) AS previous_amount
FROM stock_price_stream
WHERE date > NOW() - INTERVAL time_window_minutes MINUTE
  ORDER BY date DESC

```

## Generating statistics with SQL

Learn more about [building real-time anomaly detection systems](https://www.tinybird.co/blog-posts/real-time-anomaly-detection).

[] - TODO: update/rewrite when anomaly detection tutorials are available. 

### Interquartile Range

Here we develop interquartile ranges (IQRs) with a SQL common-table-expresion (CTE) that generates quaritiles over a time window. 

The first step of the IQR method is calculating the first and third quartiles (Q1 and Q3). These quartiles are based on a moving time window of the recent data.

The difference between these two quartiles is referred to as the IQR, as in:

IQR = Q3 - Q1

Data points that are below or above some level based on a multiplier of this IQR are considered outliers. Commonly, this multiple is set to 1.5, so we are looking for cases where:

values < Q1 - (IQR * 1.5)
values > Q3 + (IQR * 1.5)

```sql
WITH stats AS (SELECT symbol
  quantileExact(0.25) (price) AS lower_quartile,
quantileExact(0.75) (price) AS upper_quartile,
(upper_quartile - lower_quartile) * 1.5 AS IQR
FROM event_stream
WHERE timestamp >= toDate(NOW()) - INTERVAL 10 MINUTES
GROUP BY symbol
LIMIT 10
)
 SELECT DISTINCT timestamp, 
    symbol, 
    price, 
    ROUND((stats.lower_quartile - stats.IQR),2) AS lower_bound, 
    ROUND((stats.upper_quartile + stats.IQR),2) AS upper_bound 
 FROM event_stream
 JOIN stats ON event_stream.symbol = stats.symbol
 WHERE timestamp >= toDate(NOW()) - INTERVAL 10 MINUTES
 AND (price > (stats.upper_quartile + stats.IQR)
 OR price < (stats.lower_quartile - stats.IQR))
 ORDER BY timestamp DESC
```

### Z-Score
Here we develop Z-scores with a SQL common-table-expresion (CTE) that generates averages and standard deviations over a time window to calculate the score. 

This implements a simple algorith based on a time-series average and standard deviation over a minute-scale window of data. Each incoming data point, x, has a Z-Score calculated in this way:  

`zscore = (x - avg) / stddev`

Currently, this Pipe is based on two time windows: 
First, the statistics are calculated across the `_stats_time_window_minutes`.
Second, anomalies are scanned for using the `_anomaly_scan_time_window_seconds` window.

The `zscore_multiplier` parameter was added recently and defaults to 2. 
These parameters, could be promoted to API Endpoint query parameters.

- [ ] This recipe depends on two queries. The first calculates the Z-score, the second show an example for comparing with a absolute Z-score to identify anomalies. 

```sql
%
{% set _stats_time_window_minutes=10 %}
{% set _anomaly_scan_time_window_seconds=30 %}

WITH stats AS (
    SELECT symbol,
        avg(price) AS average,
        stddevPop(price) AS stddev
    FROM event_stream
    WHERE date BETWEEN NOW() - INTERVAL _stats_time_window_minutes MINUTE AND NOW()
    GROUP BY symbol  
)
SELECT es.date, 
     es.symbol, 
     es.amount, 
     (es.price - stats.average)/stats.stddev AS zscore,
     stats.average,
     stats.stddev
FROM event_stream es
JOIN stats s ON s.symbol = es.symbol
WHERE date BETWEEN NOW() - INTERVAL _anomaly_scan_time_window_seconds SECOND AND NOW()
ORDER BY date DESC
```
## Pagination

Tinybird projects are typically built with massive amounts of data and require a pagination method to enable API Endpoint clients to request data in consumable chunks. API Endpoints will generate a maximum of 10 MB of data per request. API Endpoint clients are responsible for managing 'page' requests. 

Tinybird pagination is managed with `limit` and `offset` parameters. The `limit` is the maximum number of rows to return. The `offset` is the number of rows to skip before starting to return results. If you are requesting 50 MB of data, you will need to request one 'page' at a time, updating 'offset' each time, for a total of five requests. 

Here is an example query that uses the `LIMIT #, #` form to set the *offset* (first number) and the *maximum number* of rows (second number) to return:

```sql
  SELECT browser, uniqMerge(visits) AS visits, countMerge(hits) AS hits
  FROM analytics_sources_mv
  WHERE date >= '2024-01-01' AND date <= '2024-02-01'
  GROUP BY browser
  ORDER BY visits DESC
  LIMIT 0, 100
```
In this case, we want to start from the beginning (row 0). The second number (100) specifies the limit, which is the maximum number of rows to return. So, the query will return a maximum of 100 rows, starting from the first row (offset 0). Since the results rank the top number of visits (by ordering visits in descending order), this will return the top 100. If you want to request visits ranked 101-200, the LIMIT statement would be updated to `LIMIT 100, 100`.

Here is an example query snippet that establishes `events_per_page` and `page` query parameters:

```sql
%
SELECT * FROM previous_node
LIMIT {{Int32(events_per_page, 100)}}
OFFSET {{Int32(page, 0) * Int32(events_per_page, 100)}
```

If you want to use a single LIMIT statement: `LIMIT {{Int32(page, 0) * Int32(events_per_page, 100)},

Learn more about pagination [HERE](https://www.tinybird.co/docs/query/query-parameters.html#pagination).

# Other things


## Endpoint output objects

When pulling these objects from API Endpoints, here is what these `stock price" and "comapny info" objects look like: 

```json
{
    "symbol": "TTM",
    "name": "TechTrek Manufacturing",
    "creation_date": "2006-09-18",
    "sector": "Manufacturing"
}

```

```json
{
    "amount": 0.06580348,
    "date": "2023-12-04 16:40:10",
    "stock_symbol": "TTM"
}
```

## Renaming object attributes along the pipeline

As you develop new and iterate old projects, it's nice to land on a set of SQL query templates that feel portable between Tinybird Workspaces. Here are some thoughts around naming your schema fields, selecting data types, and curating reusable queries.   

### What's in a name (or data type)?

As we develop projects, a lot of time will be spent writing queries around three fundamental attributes of an event:
* Unique identifiers for the `sensors` that are emitting data.
* Exactly when the event was emitted. Usually down to the second, and always in UTC.
* The data value the sensor generated. This could be a 'delete' event from a CDC-connected database, a 'purchase' event from a mobile app, or a measurement from a weather station.

For this project we are using the following field names and types to describe our data schema for these attributes: 
* `symbol` String
* `timestamp` DateTime
* `price` Float32

For this project, we are working with sensors with a unique string identifier and floating-point numeric data values, hence the `Sting` and `Float32` declarations.

For the [Anomaly Detection project](https://github.com/tinybirdco/use-case-anomaly-detection), these fundamental fields were described as:
* `id` Int16
* `timestamp` DateTime
* `value` Float32

Although the *names* of the incoming floating-points are different (`price` and `value`), these labels can be easily altered and updated along the pipeline (see next section). The big difference is the different data types used as the unique sensor identifiers (`symbol` and `id`). Furthermore, it is common to have both sensor ids and data values be alphanumeric data types. 

Given these different data types, you can expect to rewrite SQL developed for one to work with the other. 

### Renaming attributes along the Pipeline.

As you build multiple Tinybird Workspaces, you will find yourself borrowing queries developed in previous projects. You are sure to curate a set of fundamental queries that fit in with nearly any of your Workspaces. A query that returns the *most recent* events from a set of sensors is an example of an universally useful query. So, it's great when the inherited SQL already matches your new data schema. 

As data travels from their source to your Pipe queries, you have several opportunities to customize the data attribute names you want to bake into your queries. Here are some places where you can update the names for object attributes:

* **When generated**. Sometimes it is possible to affect the attribute names at the object source. For this project, with its Python data generator, there is complete control on the names and data types used. 
* **In Data Source defintion**. Below is an example schema from a Data Source *definitional file* that maps an incoming JSON object to schema field names. Here we could instead have a line that updates a name: `value` Float32 `json:$.price` 

```bash
SCHEMA >
    `price` Float32 `json:$.price`,
    `symbol` String `json:$.symbol`,
    `timestamp` DateTime `json:$.timestamp`
```

* **In SQL queries**. With SQL you can use aliases to rename attributes in SELECT statements. Any aliases are referenced in the other SQL sections, such as WHERE clauses.

```sql
SELECT value AS price
WHERE price < 10
```

## More notes

### SQL helpers 

Formating numbers, trimming to 2 digits. 
`ROUND(x,2)`

Renaming attributes.
`MAX(price) AS max_price`

Comparing strings.
`LOWER(thisCityName) = 'london'` 
`UPPER(thisCityName) = 'LONDON'` 
