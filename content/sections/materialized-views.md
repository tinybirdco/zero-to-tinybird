# An introduction to Materialized Views
  
What we will do in this session:     
  * Review their purpose.  
  * Discuss example use cases.
  * Build an example.

  * Topics:
    * Filtering and aggregating at ingest time, not query time. 
    * Temporal rollups.
    * State/Merge functions. 

### Screencasts:

* [Optimize query performance with Materialized Views](https://youtu.be/inhCgVU4dKY)

### Documentation

* [Core concepts: Materialized Views](https://www.tinybird.co/docs/concepts/materialized-views.html)
* [Improve Endpoint Performance With Materialized Views](https://www.tinybird.co/docs/guides/materialized-views.html)
* [Master Materialized Views](https://www.tinybird.co/docs/guides/master-materialized-views.html)
* [Calculating data on ingestion with Materialized Views](https://www.tinybird.co/docs/guides/materialized-columns.html)

### Blog posts
* [What are Materialized Views and why do they matter for real-time?](https://www.tinybird.co/blog-posts/what-are-materialized-views-and-why-do-they-matter-for-realtime)
* [Roll up data with Materialized Views](https://www.tinybird.co/blog-posts/roll-up-data-with-materialized-views)

## Building Materialized Views

Materialized Views are made of three components:
1) Pipe that applies SQL transformations and writes to a Data Source.
2) Data Source that stores intermediate states arriving from that Pipe and along with the already-processed contents.  
3) Pipe that reads from Data Source, using the -Merge function operator to merge intermediate states with previous state and deliver the 'final', up-to-the-second version. 

In the workshop project, these components are:
1) `feed_hourly_mv` Pipe.
2) `hourly_stats_mv` Data Source.
2) `hourly_stats` Pipe. 

See the next section for details on how those are built. 

## Workshop SQL 

### `feed_hourly_mv` Pipe

This is the first piece of the Materialized View (MV) workflow. In this Pipe, we will generate the hourly statistics (average, minimum, maximum, and standard deviation) as data arrives and write to the `hourly_stats_mv` Data Source. 

This pipe consists of a single `feed_mv_with_state` Node. This Node using the `-State` operator with the statistical functions to write intermediate states to the `hourly_stats_mv` Data Source, essentially keeping the current hour statistics up-to-date as new data arrive.  

#### Building a Node named `feed_mv_with_state`

##### Starting with `aggregate` query:
```sql
SELECT
    toStartOfHour(timestamp) AS time,  
    symbol,
    avg(price) AS price_avg,
    min(price) AS price_min,
    max(price) AS price_max
FROM event_stream
GROUP BY symbol, time
ORDER BY time DESC, symbol ASC    
```
##### Final query

* Adding -State operation to these avg/min/max functions.
* Adding standard deviation function `stddevPopState(price) AS price_stddev` (don't forget the preceeding comma)
* Removing `ORDER BY` clause. We are not publishing the results of this transformation yet.

```sql
SELECT
    symbol,
    toStartOfHour(timestamp) AS timestamp,
    avgState(price) AS price_avg,
    minState(price) AS price_min,
    maxState(price) AS price_max,
    stddevPopState(price) AS price_stddev
FROM event_stream
GROUP BY symbol, timestamp 
 ```

### Creating `hourly_stats_mv` Data Source

When creating a Materialized view from the `feed_mv_with_state` Node, the `AggregatingMergeTree` *Database Engine* is used. When *Materializing* the `feed_mv_with_staate` Node with the UI, the new Data Source will automatically use this engine. This is reflected in the resulting `hourly_stats_mv` definitional file:

```bash
# Data Source created from Pipe 'feed_hourly_mv'

SCHEMA >
    `symbol` String,
    `timestamp` DateTime,
    `price_avg` AggregateFunction(avg, Float32),
    `price_min` AggregateFunction(min, Float32),
    `price_max` AggregateFunction(max, Float32),
    `price_stddev` AggregateFunction(stddevPop, Float32)

ENGINE "AggregatingMergeTree"
ENGINE_PARTITION_KEY "toYear(timestamp)"
ENGINE_SORTING_KEY "timestamp, symbol"
```

### `hourly_stats` Pipe

This is the third, and final piece of the Materialized View workflow.  Its query uses the **-Merge** operator when generating the hourly statistics. The -Merge operator triggers the assembly of a up-to-day data set based on 'just arrived' intermediate states and the already-processed state. 

This Pipe consists of three Nodes. The first Node performs the merge, the second provides a `company` query parameter, and the third provides `start_time` and `end_time` query parameters. 

####  `merge_from_mv` Node

```sql
SELECT timestamp, symbol, 
ROUND(avgMerge(price_avg),2) AS price_avg,
minMerge(price_min) as price_min,
maxMerge(price_max) as price_max,
ROUND(stddevPopMerge(price_stddev),2) AS price_stddev
FROM hourly_stats_mv
GROUP BY timestamp, symbol 
ORDER BY symbol ASC, timestamp DESC

```

####  `filter_by_symbol` Node

By now, a familiar pattern for filtering by `company` symbol.

```sql
%
SELECT * 
FROM merge_from_mv
WHERE 1=1
{% if defined(company) %}               
    AND symbol == {{ String(company,description='description',required=False)}}
{% end %}    
ORDER BY timestamp DESC

```

####  `endpoint` Node

Here we support flexible handling of `start_time` and `end_time` query parameters. See [HERE](https://github.com/tinybirdco/zero-to-tinybird/blob/main/content/query-patterns.md#providing-flexible-query-parameters) for more details.


```sql
%
SELECT * 
FROM filter_by_symbol
WHERE 1=1 
{% if defined(start_time) and defined(end_time) %}
      AND toDateTime(timestamp) BETWEEN parseDateTimeBestEffort({{ DateTime(start_time, description="'YYYY-MM-DD HH:mm:ss'. UTC. Optional and defaults to 7 days ago. Defines the start of the period of interest. ") }}) AND parseDateTimeBestEffort({{ DateTime(end_time, description="'YYYY-MM-DD HH:mm:ss'. UTC. Optional and defaults to time of request. Defines the end of the period of interest.") }})
   {% end %}
 {% if not defined(start_time) and not defined(end_time) %}
    AND toDateTime(timestamp) BETWEEN addDays(now(),-7) AND NOW()
 {% end %}
 {% if defined(start_time) and not defined(end_time) %}
     AND toDateTime(timestamp) BETWEEN parseDateTimeBestEffort({{ DateTime(start_time) }}) AND now()
 {% end %}
 {% if not defined(start_time) and defined(end_time) %}
     AND toDateTime(timestamp) BETWEEN addDays(toDateTime(parseDateTimeBestEffort({{DateTime(end_time)}})),-7) AND parseDateTimeBestEffort({{ DateTime(end_time) }})
 {% end %}

```
