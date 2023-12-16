# Query patterns

A collection of SQL patterns. A WIP! 

These queries have been constructed in reference to these two schemas:

`stock_price_stream` - a real-time stream of stock price events generated with Mockingbird and written to the Events API. 

```
`amount` Float32 `json:$.amount` ,
`date` DateTime `json:$.date` ,
`stock_symbol` String `json:$.stock_symbol` ,
```
- [ ] Mockingbird emits JSON and the schema indicates how that JSON is parsed by key to extract the values.  
- [ ] For `amount`, update Mockingbird type to `#####.##` currency and rename to `price`? Or just update Data Source schema, `price` Decimal(10,2) `json:$amount`?
  
`company_info` - Mock data about ~85 fictional companies. 

```
`symbol` String,
`name` String,
`creation_date` Date,
`sector` String,
```

## Working with time

To gain a wide prespective of how to work with timetamps in Tinybird, these guides are critical:
* https://www.tinybird.co/docs/guides/working-with-time.html
* https://www.tinybird.co/docs/guides/best-practices-for-timestamps.html

### Data from the most recent hour
```sql
SELECT * 
FROM stock_price_stream
WHERE toDateTime(date) BETWEEN addHours(NOW(),-1) AND NOW()
```

### Data between explicit dates
```sql
SELECT * 
FROM stock_price_stream
WHERE toDateTime(date) BETWEEN '2023-12-07 17:22:00' AND '2023-12-07 17:23:00'
```

### Selecting most recent data within an explicit time window

This query is hardcoded to 'look back' sixty minutes. 

```sql
%
WITH RankedData AS (
    SELECT
        symbol,
        timestamp,
        amount,
        ROW_NUMBER() OVER (PARTITION BY symbol ORDER BY timestamp DESC) AS row_num
    FROM
        stock_price_stream
     WHERE timestamp > NOW() - INTERVAL 60 MINUTE
)
SELECT
    symbol,
    timestamp,
    amount
FROM
    RankedData
WHERE
    row_num = 1

```

## JOIN patterns

```sql
SELECT sps.date, ci.symbol, ci.name, sps.amount 
FROM company_info ci, stock_price_stream sps
WHERE ci.symbol = sps.stock_symbol
ORDER BY date DESC
LIMIT 10
```

```sql
SELECT sps.date, ci.symbol, ci.name, sps.amount 
FROM company_info ci
JOIN stock_price_stream sps
ON ci.symbol = sps.stock_symbol
WHERE sps.stock_symbol = 'SUN'
ORDER BY date DESC
LIMIT 10
```

## Calculating slope

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

## Anomaly detection with SQL

### Interquartile Range

Based on a time window (defaulting here to a 10-minute window), calculate the lower quartile, the medium, and the upper quartile. The IQR is then set to (uper quartile - lower quartile) * 1.5.

Based on the IQR, lower and upper bounds are set for determining data outliers:
* lower bound = lower quartile - IQR
* upper bound = upper quartile - IQR


```sql
WITH stats AS (SELECT symbol
quantileExact(0.25) (amount) AS lower_quartile,
quantileExact(0.5) (amount) AS mid_quartile,
quantileExact(0.75) (amount) AS upper_quartile,
(upper_quartile - lower_quartile) * 1.5 AS IQR
FROM stock_price_stream
WHERE timestamp >= toDate(NOW()) - INTERVAL 10 MINUTES
GROUP BY symbol
LIMIT 10
)
 SELECT DISTINCT timestamp, 
    symbol, 
    amount, 
    ROUND((stats.lower_quartile - stats.IQR),2) AS lower_bound, 
    ROUND((stats.upper_quartile + stats.IQR),2) AS upper_bound 
 FROM stock_price_stream
 JOIN stats ON incoming_data.symbol = stats.symbol
 WHERE timestamp >= toDate(NOW()) - INTERVAL 10 MINUTES
 AND (amount > (stats.upper_quartile + stats.IQR)
 OR amount < (stats.lower_quartile - stats.IQR))
 ORDER BY timestamp DESC
```

### Z-Score

This implements a simple algorith based on a time-series average and standard deviation over a minute-scale window of data. Each incoming data point, x, has a Z-Score calculated in this way:  

`zscore = (x - avg) / stddev`

Currently, this Pipe is based on two time windows: 
First, the statistics are calculated across the `_stats_time_window_minutes`.
Second, anomalies are scanned for using the `_anomaly_scan_time_window_seconds` window.

The `zscore_multiplier` parameter was added recently and defaults to 2. 
These parameters, could be promoted to API Endpoint query parameters.

```sql
%
{% set _stats_time_window_minutes=10 %}
{% set _anomaly_scan_time_window_seconds=30 %}

WITH stats AS (
    SELECT symbol,
        avg(amount) AS average,
        stddevPop(amount) AS stddev
    FROM stock_price_stream
    WHERE date BETWEEN NOW() - INTERVAL {{Int16(_stats_time_window_minutes)}} MINUTE AND NOW()
    GROUP BY symbol  
)
SELECT sps.date, 
     sps.symbol, 
     sps.amount, 
     (sps.amount - stats.average)/stats.stddev AS zscore,
     stats.average,
     stats.stddev,
     {{Int16(zscore_multiplier, 2, description="Z-Score multipler to identify anomalies.")}} AS zscore_multiplier
FROM stock_price_stream sps
JOIN stats s ON s.symbol = sps.symbol
WHERE date BETWEEN NOW() - interval {{Int16(_anomaly_scan_time_window_seconds)}} SECOND AND NOW()
ORDER BY date desc

```

### Comparing data with thresholds


```sql
SELECT *, 0.75 AS min_value, 1.0 AS max_value 
FROM stock_price_stream
WHERE (amount < 200 OR amount > 2000)
LIMIT 10
```



#### Other things

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
