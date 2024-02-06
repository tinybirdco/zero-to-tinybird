## Building data analysis pipelines

What we will do in this session: 
  * Getting started by developing SQL queries in Playgrounds.
  * Building our first Pipe and publishing an API Endpoint.
  * Building Pipes that filter, aggregate and join Data Sources.
  * Creating dynamic request parameters.   

Screencasts:

* [Add query parameters to your APIs](https://youtu.be/PbfNIeq06DA)

Documentation:

* Core concepts: 
  * [Pipes](https://www.tinybird.co/docs/main-concepts.html#data-sources) 
  * [Nodes](https://www.tinybird.co/docs/main-concepts.html#nodes)
  * [API Endpoints](https://www.tinybird.co/docs/main-concepts.html#api-endpoints)
* [Using Query parameters](https://www.tinybird.co/docs/query/query-parameters.html)
* 

## Example SQL 


### Filtering by symbol 

```sql
SELECT timestamp, symbol, price 
FROM event_stream
WHERE 
symbol = 'ALG'
ORDER BY timestamp DESC
LIMIT 100
```

### Generating hourly stats

This query uses the ClickHouse `toStartHour` to 'bin' the reports into hourly 'buckets'.

```sql
 SELECT
        toStartOfHour(timestamp) AS time,
        symbol,
        ROUND(avg(price), 2) AS price_avg,
        ROUND(min(price), 2) AS price_min,
        ROUND(max(price), 2) AS price_max
    FROM event_stream
    GROUP BY
        symbol, time
    ORDER BY
        time DESC,
        symbol ASC    
```

### Queries that JOIN two Data Sources

The first query is an implicit JOIN stemming from the `WHERE ci.symbol = es.symbol` statement. 

The second is an explicit JOIN with that keyword. 

```sql
SELECT es.timestamp, ci.symbol, ci.name, es.price, ci.sector 
FROM company_info ci, event_stream es
WHERE ci.symbol = es.symbol
ORDER BY timestamp DESC
LIMIT 100
```

```sql
SELECT es.timestamp, ci.symbol, ci.name, es.price, ci.sector 
FROM company_info ci
JOIN event_stream es
ON ci.symbol = es.symbol
LIMIT 10
```
