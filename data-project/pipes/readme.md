## Fundamental patterns


### Filtering data

```sql
SELECT * 
FROM stock_price_stream
WHERE stock_symbol = 'TTM'
ORDER BY date DESC
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
```

```sql
```

### Joining data

```sql
```

```sql
```
