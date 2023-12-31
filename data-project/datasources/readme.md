# Data Sources

Workshop content is based on these two data sources:
* A real-time stream of stock price updates. 
* *Dimensional* metadata about the stock symbols, such as company names, economic sectors, and creation dates. 


See [HERE](https://github.com/tinybirdco/zero-to-tinybird/blob/main/data/readme.md) for details on creating these Data Sources.


## Company information 

```bash
  `symbol` String,
  `name` String,
  `creation_date` Date,
  `sector` String
```

## Real-time stream of events  

```bash
  `amount` Float32 `json:$.amount`,
  `date` DateTime `json:$.date`,
  `stock_symbol` String `json:$.stock_symbol`
```

## Materialized Views

```
ENGINE "AggregatingMergeTree"
```

```bash
  `stock_symbol` String,
  `total_events` AggregateFunction(count)
```

```bash
  `symbol` String,
  `timestamp` DateTime,
  `price_avg` AggregateFunction(avg, Float32),
  `price_min` AggregateFunction(min, Float32),
  `price_max` AggregateFunction(max, Float32),
  `price_stddev` AggregateFunction(stddevPop, Float32)
```
