# Creating Data Sources from files


## Using "Remote URL" feature to load CSV

Navigate to add a Data Source, and select the "Remote URL" option. Paste the following URL into the text box:

```https://raw.githubusercontent.com/tinybirdco/zero-to-tinybird/main/data/company-info.csv?token=GHSAT0AAAAAACBNU2HVUFEKA6NDHUSSST2WZL4YHJQ```
 



## Loading CSV from a Github repository

The following command copies the contents of a hosted file and creates a Data Source with its schema and content. 

#### Example curl command
curl \
-H "Authorization: Bearer {TOKEN}" \
-X POST "https://api.tinybird.co/v0/datasources?name=company_info" \
-d url='https://raw.githubusercontent.com/jimmoffitt/zero-to-tinybird/main/data/stock-symbols.csv'
