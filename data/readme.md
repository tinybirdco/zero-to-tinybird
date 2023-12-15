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
