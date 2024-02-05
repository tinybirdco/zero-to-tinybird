# Data Sources

Workshop content is based on these two data sources:
* A real-time stream of (mocked) stock price updates. 
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
  `timestamp` DateTime `json:$.date`,
  `symbol` String `json:$.stock_symbol`,
  `price` Float32 `json:$.amount`
```

## Materialized Views

```
ENGINE "AggregatingMergeTree"
```

```bash
  `symbol` String,
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
