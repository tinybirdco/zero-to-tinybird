# Creating Data Sources from files



## Loading CSV from a Github repository

The following command copies the contents of a hosted file and creates a Data Source with its schema and content. 

#### Example curl command
curl \
-H "Authorization: Bearer {TOKEN}" \
-X POST "https://api.tinybird.co/v0/datasources?name=company_info" \
-d url='https://raw.githubusercontent.com/jimmoffitt/zero-to-tinybird/main/data/stock-symbols.csv'