## Example Pipe definitions for filtering, aggregating, and joining data

### Pipe defintion files: 
+ *filter.pipe* 
+ *aggregate.pipe*
+ *join_data.pipe*

These Pipes explore three fundamental patterns of how SQL is used to explore and transform data: filtering, aggregating, and joining.

### Filtering data - *filter.pipe*

This query filters on events that have a stock symbol of interest. It returns the most recent events, and orders them in reverse chronological order. This query helps illustrate a common structure: `SELECT | FROM | WHERE | ORDER`. 

```sql
SELECT * 
FROM stock_price_stream
WHERE stock_symbol = 'TTM'
ORDER BY date DESC
```

While learning SQL (and even if you are an 'expert'), it is recommended to also use a `LIMIT` statement to *limit* the number of events/objects/results returned. With databases storing huge quantities of data comes the opportunity to make requests that require large amounts of resources to retrieve, write, and store. Using a 'LIMIT #' is a great insurance policy as you develop and test queries. 

For the above query, if only the 100 most recent events are of interest, you can add the `LIMIT` statement, for a `SELECT | FROM | WHERE | ORDER | LIMIT` structure:

```sql
SELECT * 
FROM stock_price_stream
WHERE stock_symbol = 'TTM'
ORDER BY date DESC
LIMIT 100
```

Next, we have that same query, except that it now supports *dynamic query parameters* that can be used when requesting data via API Endpoints published from Pipes. These request parameters enable filtering the data by a `stock_symbol` of interest and limiting the number of results to a maximum of `max_results`. 

A new feature of this SQL is the leading `%` symbol which triggers the query parser to handle any query parameters included in the API request. 

```sql
%

SELECT * 
FROM stock_price_stream
WHERE 1=1
{% if defined(stock_symbol) %}
    AND stock_symbol = {{ String(stock_symbol, description='Symbol of interest.') }}
{% end %}
ORDER BY date DESC
LIMIT {{ Int32(max_results, 10, description="The maximum number of reports to return per response.") }}
```
Since we are making the use of `stock_symbol` *optional* with the `if defined(stock_symbol)` templating syntax, we need to use the `1=1` convention in the `WHERE` clause, since it prevents an empty `WHERE` clause if the user does not specify a symbol. 

### Aggregating data - *aggregate.pipe*

Here we are generating time-series data consisting of average, minimum, and maximum values. In the examples below, we will generate event statistics on by-the-minute (minutely?), hourly, and daily intervals. 

This first query generates daily data and relies on the ClickHouse `toStartOfDay` function. This query aggregates across full (midnight-to-midnight UTC) days. It also uses the `ROUND` function to format floating-point numbers that result from generating the stats. 

```sql
SELECT
    toStartOfDay(date) AS day,
    stock_symbol,
    ROUND(avg(amount), 2) AS price_avg,
    ROUND(min(amount), 2) AS price_min,
    ROUND(max(amount), 2) AS price_max
FROM stock_price_stream
GROUP BY
    date,
    stock_symbol
ORDER BY
    date DESC,
    stock_symbol ASC    
```

To aggregate hourly data, the `toStartOfHour` function can be used. 

```sql
toStartOfHour(date) AS hour
```

To aggregate by-the-minute data, the `toStartOfMinute` function can be used. 

```sql
toStartOfMinute(date) AS minute
```

We're sure you see a pattern here. ClickHouse offers a suite of time and date function that help with core 'binning' concerns common with real-time data. Check out this documentation on [ClickHouse date and time functions](https://clickhouse.com/docs/en/sql-reference/functions/date-time-functions).

### Joining data - *join_data.pipe* 

In this query, we are using an *implicit* JOIN, which defaults to an `INNER` join. This means only rows where the symbol exists in both the ci and sps tables will be included. Depending on your intent, this might not be the desired behavior. 

```sql
SELECT sps.date, ci.symbol, ci.name, sps.amount 
FROM company_info ci, stock_price_stream sps
WHERE ci.symbol = sps.stock_symbol
ORDER BY date DESC
LIMIT 10
```

If you want all symbols from ci regardless of whether they have price data in sps, you should use a left outer join:

```sql
SELECT sps.date, ci.symbol, ci.name, sps.amount
FROM company_info ci
LEFT JOIN stock_price_stream sps ON ci.symbol = sps.stock_symbol
ORDER BY date DESC
LIMIT 10
```

#### Performance considerations

* Column indexes: Ensure you have indexes on the join columns (`symbol` in the `company_info` table, and `stock_symbol` in the other table) for optimal performance.

* Filtering: If you have additional filtering criteria, consider adding them to the WHERE clause before the join to reduce the number of rows involved.

## Materialized Views

* Documentation:
  + https://www.tinybird.co/docs/concepts/materialized-views.html
  + https://www.tinybird.co/docs/guides/materialized-views.html
* Blog posts:
  + https://www.tinybird.co/blog-posts/what-are-materialized-views-and-why-do-they-matter-for-realtime
* Screencasts:
  + https://www.youtube.com/watch?v=inhCgVU4dKY
  + https://www.youtube.com/watch?v=PJHPq0-08Wc

Materialize Views (MVs) consists of several components. For the workshop, we have three components:

* A Pipe that applies -State operations and writes them to a Data Source. These actions are triggered as data is ingested, and query results are written to a Materialized Data Source.  
  * `avgState(amount)` AS price_avg
* A Data Source that stores the state data. This is a collection of recently generated data partitions that are assembled when a 'calling' query is made.
  * `TYPE materialized`
  * `DATASOURCE daily_stats_mv`
  * `ENGINE "AggregatingMergeTree"`
* A Pipe that applies -Merge operations. These operations happen at query time. When an API Endpoint is deployed, this Pipe assembles (merges) and serves each request. 
  * `avgMerge(price_avg)` AS price_avg 



### Pipes that feed state data to Data Sources
+ *feed_counts_mv_with_state.pipe* 
+ *feed_daily_mv_with_state.pipe* 
+ *feed_hourly_mv_with_state.pipe* 

These Pipes apply SQL queries to data as it arrives and is *ingested*. For many use cases, processing data as it is ingested is much more efficient than processing data everytime a request arrives.  

Using `-State` operations, this query generates state snaphots of averages, minimums, and maximums as data arrives. 

```sql
 SELECT
    stock_symbol AS symbol,
    toStartOfDay(date) AS timestamp,
    avgState(amount) AS price_avg,
    minState(amount) AS price_min,
    maxState(amount) AS price_max,
    stddevPopState(amount) AS price_stddev
FROM stock_price_stream
GROUP BY symbol, timestamp
ORDER BY symbol ASC, timestamp ASC
```
### Data Sources for storing state data

+ *counts_mv.datasource* 
+ *daily_stats_mv.datasource* 
+ *hourly_stats_mv.datasource* 

MV configuration details for the Data Source include:

```bash
TYPE materialized
DATASOURCE daily_stats_mv
ENGINE "AggregatingMergeTree"
ENGINE_SORTING_KEY "stock_symbol"
```
### Requesting fresh data from MVs

+ *get_counts.pipe* 
+ *daily_stats.pipe* 
+ *hourly_stats.pipe* 

When MV data is requested, data is pulled from the associated MV Data Source and the `-Merge` operations are applied: 

```sql
SELECT timestamp, symbol, 
    avgMerge(price_avg) AS price_avg,
    minMerge(price_min) as price_min,
    maxMerge(price_max) as price_max,
    stddevPopMerge(price_stddev) AS price_stddev
FROM daily_stats_mv
GROUP BY timestamp, symbol
ORDER BY symbol ASC, timestamp ASC
```
