# Creating Data Sources from files

## Creating Data Sources from CSV files

### Using "Remote URL" feature to load CSV file

Navigate to add a Data Source, and select the "Remote URL" option. Paste the following URL into the text box:

```https://raw.githubusercontent.com/tinybirdco/zero-to-tinybird/main/data/company-info.csv?token=GHSAT0AAAAAACBNU2HVUFEKA6NDHUSSST2WZL4YHJQ```
 
### Using a CURL command
curl \
-H "Authorization: Bearer {TOKEN}" \
-X POST "https://api.tinybird.co/v0/datasources?name=company_info" \
-d url='https://raw.githubusercontent.com/jimmoffitt/zero-to-tinybird/main/data/stock-symbols.csv'

# Setting up real-time stream of mock stock price data

`stock-price-stream.py` is used to generate an event stream of mock stock price data. It reads in the content of the `company-info.csv` file and creates a *sensor object* for each company, including a three-character stock symbol. This script then generates new prices for each object and publishes them to a Kafka stream hosted on Confluent Cloud. To publish the data, you will need a Confluence Cloud account and a Kafka stream and topic configured. 

Script configuration includes what interval to run on, with a default of publishing new prices every 20 seconds. 

The script has logic to 'manage' the time-series values, and supports both 'normal' changes between reports and larger 'step' changes. If the Tinybird Workspace receiving the data has a `most_recent` API Endpoint, on start-up, the script will retrieve these values and initiate the sensors with those. 

Script configuration is provided by the `settings.yaml` file, and includes the interval setting (in seconds) and setting to *tune* the change patterns in the generated time-series data.    

![Example](../images/com.com.png)

The `stock-price-stream.py` script imports configuration details from a local `settings.yaml` file. 

These settings help *tune* time-series patterns:

```yaml
sleep_seconds: 20    # How long to pause between sensor value updates... 
num_iterations: 1000000 # A guard rail for only running so long. With this number (and this interval) it will run for many weeks. 

# We have 'normal' changes, and some precentage of larger 'step' changes.
value_max_normal_change: 1 

percent_step: 2
percent_step_trend: 2

step_change_min: 3
step_change_max: 6
```

This script is a simplified version of a data generator used to create time-series with prescribed anomalies. 




 






