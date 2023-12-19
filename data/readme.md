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

# Creating a real-time event stream of mocked data

* Head to https://mockingbird.tinybird.co/ and configure the details after selecting `Tinybird Events API`. 
  * Be sure to select the `Host` that matches where your Workspace resides. 
  * Copy in your admin Auth Token associated with your email.
  * Set the `Events Per Second` setting to something between 10 and 100.
* In the `Schema Designer` section, copy in the contents provided in the [stock-price-stream.mockingbird](https://raw.githubusercontent.com/tinybirdco/zero-to-tinybird/main/data/stock-price-stream.mockingbird?token=GHSAT0AAAAAACBNU2HUVJP6MGXCXH4KCWH4ZL4Y3KA) file. This JSON object describes the data structure of streamed event data. The defined stock symbols match what is in the `company-info.csv` file.
* Click on the `Preview` button and confirm that the schema is set-up OK. You should see something like:
```json
{
    "amount": 0.5859901180956513,
    "date": "2023-12-15T20:38:55",
    "stock_symbol": "NEX"
}
```
* Click the 'Start Generating!` button to start the event stream. 
* Return to your Tinybird Workspace and confirm that data is arriving. It may take a few seconds to see the updates. 

