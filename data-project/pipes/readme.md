## Fundamental query patterns

Here we explore three fundamental patterns of how SQL is used to explore and transform data:  filtering, aggregating, and joining.

### Filtering data

Here we filter on events that have a stock symboi of interest. This query helps illustrate a common structure: `SELECT | FROM | WHERE | ORDER`. 

```sql
SELECT * 
FROM stock_price_stream
WHERE stock_symbol = 'TTM'
ORDER BY date DESC
```

While learning SQL (and even if you are an 'expert'), it is recommended to to also use a `LIMIT` statement to *limit* the number of events/objects/results to return. For the above query, if only the 100 most recent events are of interest, you can add the `LIMIT` statement, for a `SELECT | FROM | WHERE | ORDER | LIMIT` structure:

```sql
SELECT * 
FROM stock_price_stream
WHERE stock_symbol = 'TTM'
ORDER BY date DESC
LIMIT 100
```

Next we have that same query, except that it now supports *dynamic query parameters* that can be used when requesting data via an API Endpoint published from the Pipe. These request parameters enable filtering the data by a `stock_symbol` of interest and limiting the number of results to a `max_results` maximum. 

Since we are making the use of `stock_symbol` optional with the `if defined(stock_symbol)` templating syntax, we need to use the `1=1` convention in the `WHERE` clause, since it prevents an empty `WHERE` clause if the user does not specify a symbol. 

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

### Aggregating data

Here we are generating a daily time-series of average, minimum, and maximum values. 

This query relies on the ClickHouse `toStartOfDay` function to aggregate across full (midnight-to-midnight UTC) days. It also uses the `ROUND` function to format the floating point that result from calculating the stats. 

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

Check out this documentation on [ClickHouse date and time functions](https://clickhouse.com/docs/en/sql-reference/functions/date-time-functions).

### Joining data

In this query, we are using an *implicit* JOIN, which defaults to an `INNER` join. This means only rows where the symbol exists in both the ci and sps tables will be included. Depending on your intent, this might not be the desired behavior. 

```sql
SELECT sps.date, ci.symbol, ci.name, sps.amount 
FROM company_info ci, stock_price_stream sps
WHERE ci.symbol = sps.stock_symbol
ORDER BY date DESC
LIMIT 10
```

If you want all symbols from ci regardless of whether they have price data in sps, you should use a lrft outer join:

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



