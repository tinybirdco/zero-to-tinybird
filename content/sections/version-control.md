### Using version control with data projects

'Under the hood', Tinybird Data Sources and Pipes are represented as configuration files. For this reason, Tinybird projects are made up of a collection of configuration files that can be managed as code. For this reason, using version control systems can be very useful for managing projects. 

For example, this project includes a `company_info` Data Source. Here is its representation in a *.datasource file:

```
SCHEMA >
    `symbol` String,
    `name` String,
    `creation_date` Date,
    `sector` LowCardinality(String)

ENGINE "MergeTree"
ENGINE_PARTITION_KEY "toYear(creation_date)"
ENGINE_SORTING_KEY "symbol, sector, name"
```

And here is a the representation of the 'filter` Pipe in a *.pipe file:

```
TOKEN "filter_endpoint_read" READ

NODE filter_by_symbol
SQL >

    %
    SELECT timestamp, symbol, price
    FROM event_stream
    WHERE 1=1
    {% if defined(company) %}
      AND symbol = {{ String(company,description = 'String. Three-character stock symbol of interest.') }}
    {% end %}
    ORDER BY timestamp DESC
    LIMIT 100 
```

