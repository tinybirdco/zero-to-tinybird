# Query patterns

A collection of SQL patterns. A WIP! 

These queries have been constructed in reference to these two schemas:

`stock_price_stream` - a real-time stream of stock price events generated with Mockingbird and written to the Events API. 

```
`amount` Float32 `json:$.amount` ,
`date` DateTime `json:$.date` ,
`stock_symbol` String `json:$.stock_symbol` ,
```
  [] Mockingbird emits JSON and the schema indicates what 
  [] For `amount`, update Mockingbird type to `#####.##` currency and rename to `price`? Or just update Data Source schema, `price` Decimal(10,2) `json:$amount`?
  
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
WHERE toDateTime(date) BETWEEN addHours(now(),-1) AND NOW()
```

### Data between explicit dates
```sql
SELECT * 
FROM stock_price_stream
WHERE toDateTime(date) BETWEEN '2023-12-07 17:22:00' AND '2023-12-07 17:23:00'
```

### Selecting most recent data within an explicit time window

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
     WHERE timestamp > NOW() - interval {{Int16(time_window_minutes, 10, description="Results will be based on this number of minutes of data history. ")}} MINUTE
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






#### Other things

When pulling these objects from API Endpoints, here is what these `stock price" and "comapny info" look like: 

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
