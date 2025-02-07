import pandas as pd
from taipy.gui import Gui

# Step 1: Load all the data files
csv_files = {
    "calendar": "C:/Users/Aravind/Desktop/AdventureWorks Raw Data/AdventureWorks Calendar Lookup.csv",
    "customer": "C:/Users/Aravind/Desktop/AdventureWorks Raw Data/AdventureWorks Customer Lookup.csv",
    "product_categories": "C:/Users/Aravind/Desktop/AdventureWorks Raw Data/AdventureWorks Product Categories Lookup.csv",
    "product_lookup": "C:/Users/Aravind/Desktop/AdventureWorks Raw Data/AdventureWorks Product Lookup.csv",
    "product_subcategories": "C:/Users/Aravind/Desktop/AdventureWorks Raw Data/AdventureWorks Product Subcategories Lookup.csv",
    "returns": "C:/Users/Aravind/Desktop/AdventureWorks Raw Data/AdventureWorks Returns Data.csv",
    "sales_2020": "C:/Users/Aravind/Desktop/AdventureWorks Raw Data/AdventureWorks Sales Data 2020.csv",
    "sales_2021": "C:/Users/Aravind/Desktop/AdventureWorks Raw Data/AdventureWorks Sales Data 2021.csv",
    "sales_2022": "C:/Users/Aravind/Desktop/AdventureWorks Raw Data/AdventureWorks Sales Data 2022.csv",
    "unpivot_demo": "C:/Users/Aravind/Desktop/AdventureWorks Raw Data/Product Category Sales (Unpivot Demo).csv"
}

# Load all data into a dictionary of dataframes
dfs = {key: pd.read_csv(path, encoding='ISO-8859-1') for key, path in csv_files.items()}

# Extract relevant dataframes
sales_df_2020 = dfs["sales_2020"]
sales_df_2021 = dfs["sales_2021"]
sales_df_2022 = dfs["sales_2022"]
returns_df = dfs["returns"]
product_lookup_df = dfs["product_lookup"]

# Combine the sales data from 2020, 2021, and 2022
sales_df = pd.concat([sales_df_2020, sales_df_2021, sales_df_2022], ignore_index=True)

# Step 2: Merge Sales Data with Product Lookup to get the necessary columns (Product Price and Product Cost)
sales_df = sales_df.merge(product_lookup_df[['ProductKey', 'ProductPrice', 'ProductCost']], on='ProductKey', how='left')

# Check for missing values in product lookup (ProductPrice and ProductCost)
sales_df['ProductPrice'].fillna(0, inplace=True)  # Or handle missing data accordingly
sales_df['ProductCost'].fillna(0, inplace=True)   # Or handle missing data accordingly

# Step 3: Calculate Total Revenue, Total Cost, Total Profit, Total Orders, and Return Rate

# Total Revenue: SUMX('Sales Data', 'Sales Data'[OrderQuantity] * RELATED('Product Lookup'[ProductPrice]))
sales_df['Revenue'] = sales_df['OrderQuantity'] * sales_df['ProductPrice']
total_revenue = sales_df['Revenue'].sum()

# Total Cost: SUMX('Sales Data', 'Sales Data'[OrderQuantity] * RELATED('Product Lookup'[ProductCost]))
sales_df['Cost'] = sales_df['OrderQuantity'] * sales_df['ProductCost']
total_cost = sales_df['Cost'].sum()

# Total Profit: [Total Revenue] - [Total Cost]
total_profit = total_revenue - total_cost

# Total Orders: DISTINCTCOUNT('Sales Data'[OrderNumber])
total_orders = sales_df['OrderNumber'].nunique()

# Quantity Returned: SUM('Returns Data'[ReturnQuantity])
total_quantity_returned = returns_df['ReturnQuantity'].sum()

# Quantity Sold: SUM('Sales Data'[OrderQuantity])
total_quantity_sold = sales_df['OrderQuantity'].sum()

# Return Rate: DIVIDE([Quantity Returned], [Quantity Sold], "No Sales")
if total_quantity_sold > 0:
    return_rate = total_quantity_returned / total_quantity_sold
    return_rate = f"{return_rate:.2%}"  # Format as percentage
else:
    return_rate = "No Sales"

# Step 4: Create the Taipy GUI layout
layout = f"""
# Business Metrics Dashboard

## Total Revenue
<| {total_revenue:,.2f} | indicator | label=Total Revenue |>

## Total Profit
<| {total_profit:,.2f} | indicator | label=Total Profit |>

## Total Orders
<| {total_orders:,} | indicator | label=Total Orders |>

## Return Rate
<| {return_rate} | indicator | label=Return Rate |>
"""

# Step 5: Run the Taipy GUI
gui = Gui(page=layout)
gui.run()
