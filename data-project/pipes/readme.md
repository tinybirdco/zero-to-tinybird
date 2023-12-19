## Fundamental patterns

Here we explore three fundamental patterns of how SQL is used to explore and transform data:  filtering, aggregating, and joining.

### Filtering data

Here we filter on events that have a stock symboi of interest. This query helps illustrate a common structure: SELECT | FROM | WHERE | ORDER. 

```sql
SELECT * 
FROM stock_price_stream
WHERE stock_symbol = 'TTM'
ORDER BY date DESC
```

While learning SQL (and even if you are an 'expert', it is recommended to to also use a `LIMIT` statement to *limit* the number of events/objects/results to return. For the above query, if only the 100 most recent events are of interest, you can add the `LIMIT` statement:

```sql
SELECT * 
FROM stock_price_stream
WHERE stock_symbol = 'TTM'
ORDER BY date DESC
LIMIT 100
```

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

```sql
SELECT
    toStartOfDay(date) AS hour,
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

```sql
toStartOfHour(date) AS hour
```

```sql
toStartOfMinute(date) AS hour
```

### Joining data

```sql
SELECT sps.date, ci.symbol, ci.name, sps.amount 
FROM company_info ci, stock_price_stream sps
WHERE ci.symbol = sps.stock_symbol
ORDER BY date DESC
LIMIT 10
```

```sql
```
