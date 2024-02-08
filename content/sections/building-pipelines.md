# Building data analysis pipelines

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


## Workshop SQL 

### `filter` Pipe

This Pipe will have a single Node, named `filter_by_symbol`.

#### Starting query

```sql
SELECT timestamp, symbol, price 
FROM event_stream
WHERE symbol = 'ALG'
ORDER BY timestamp DESC
LIMIT 100
```

Next we introduce dynamic query parameters using the Tinybird templating syntax.

* Adding `max_results` and `company` API endpoint query paramters.
* Since the WHERE cause is dependent on the user providing the `company` query parameter, we need to handle when there are no user-triggered WHERE clauses and start with an always-true `WHERE 1=1` clause and AND onto that. 
* Adding `LOWER()` statement to make query case insensitive. 

#### Final query

##### Single `filter_by_symbol` Node

```sql
%
SELECT timestamp, symbol, price 
FROM event_stream
WHERE 
1=1
{% if defined(company) %}
  AND LOWER(symbol) = LOWER({{ String(company,description = 'String. Three-character stock symbol of interest.') }})
{% end %}
ORDER BY timestamp DESC
LIMIT {{ Int32(max_results,10,description="The maximum number of reports to return per response.") }}
```

### `aggregate` Pipe

This Pipe will have two Nodes, First one named `get_hourly_stats`, and a second that reads from the first one.

#### Starting query

##### `get_hourly_stats` Node

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

#### Final queries

##### `get_hourly_stats` Node

```sql
SELECT
    toStartOfHour(timestamp) AS time,
    symbol,
    ROUND(avg(price), 2) AS price_avg,
    ROUND(min(price), 2) AS price_min,
    ROUND(max(price), 2) AS price_max
FROM event_stream
GROUP BY symbol, time
ORDER BY time DESC, symbol ASC    
```

##### `endpoint` Node

```sql
%
SELECT * 
FROM get_hourly_stats
WHERE 
1=1
{% if defined(company) %}
  AND LOWER(symbol) = LOWER({{ String(company,description = 'String. Three-character symbol of interest. If not provided, all companies are retured. No default. ') }})
{% end %}
LIMIT {{ Int32(max_results,10,description="The maximum number of reports to return per response.") }}
```

### `join_data` Pipe

#### Explicit JOIN 

```sql
SELECT es.timestamp, ci.symbol, ci.name, es.price, ci.sector 
FROM company_info ci, event_stream es
WHERE ci.symbol = es.symbol
ORDER BY timestamp DESC
LIMIT 100
```

#### Implicit JOIN

```sql
SELECT es.timestamp, ci.symbol, ci.name, es.price, ci.sector 
FROM company_info ci
JOIN event_stream es
ON ci.symbol = es.symbol
LIMIT 100
```
