import pandas as pd
from taipy.gui import Gui

# Step 1: Load Data from Multiple CSV Files with Encoding Handling
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

# Load CSV files into DataFrames with appropriate encoding
sales_2020_df = pd.read_csv(csv_files["sales_2020"], encoding='ISO-8859-1')
sales_2021_df = pd.read_csv(csv_files["sales_2021"], encoding='ISO-8859-1')
sales_2022_df = pd.read_csv(csv_files["sales_2022"], encoding='ISO-8859-1')
calendar_df = pd.read_csv(csv_files["calendar"], encoding='ISO-8859-1')
customer_df = pd.read_csv(csv_files["customer"], encoding='ISO-8859-1')
product_categories_df = pd.read_csv(csv_files["product_categories"], encoding='ISO-8859-1')
product_lookup_df = pd.read_csv(csv_files["product_lookup"], encoding='ISO-8859-1')
product_subcategories_df = pd.read_csv(csv_files["product_subcategories"], encoding='ISO-8859-1')
returns_df = pd.read_csv(csv_files["returns"], encoding='ISO-8859-1')

# Debugging: Print column names and first few rows to check
print("Columns in calendar_df:", list(calendar_df.columns))
print("Columns in product_lookup_df:", list(product_lookup_df.columns))
print(calendar_df.head())  # Check the first few rows

# Convert 'Date' to datetime
calendar_df['Date'] = pd.to_datetime(calendar_df['Date'], errors='coerce')

# Create 'Start of Month' from 'Date'
calendar_df['Start of Month'] = calendar_df['Date'].dt.to_period('M').dt.to_timestamp()

# Step 2: Data Preparation
# Convert date columns to datetime with error handling
sales_2020_df['OrderDate'] = pd.to_datetime(sales_2020_df['OrderDate'], errors='coerce')
sales_2021_df['OrderDate'] = pd.to_datetime(sales_2021_df['OrderDate'], errors='coerce')
sales_2022_df['OrderDate'] = pd.to_datetime(sales_2022_df['OrderDate'], errors='coerce')

# Combine sales data from all years
sales_df = pd.concat([sales_2020_df, sales_2021_df, sales_2022_df])

# Merge with Product Lookup to get Product Price
sales_df = sales_df.merge(product_lookup_df[['ProductKey', 'ProductPrice']], on='ProductKey', how='left')

# Calculate Total Revenue
sales_df['Revenue'] = sales_df['OrderQuantity'] * sales_df['ProductPrice']

# Ensure the datetime column is used as an index for resampling
sales_df.set_index('OrderDate', inplace=True)
returns_df['ReturnDate'] = pd.to_datetime(returns_df['ReturnDate'], errors='coerce')
returns_df.set_index('ReturnDate', inplace=True)

# Calculate monthly revenue, orders, and returns
monthly_data = sales_df.resample('M').agg(
    Total_Revenue=('Revenue', 'sum'),
    Total_Orders=('OrderNumber', 'nunique'),
).reset_index()

monthly_returns = returns_df.resample('M').agg(
    Total_Returns=('ReturnQuantity', 'sum')
).reset_index()

# Merge monthly data and returns
monthly_data = pd.merge(
    monthly_data, monthly_returns,
    left_on='OrderDate', right_on='ReturnDate', how='outer'
)

# Calculate Previous Month Values
monthly_data['Prev_Revenue'] = monthly_data['Total_Revenue'].shift(1)
monthly_data['Prev_Orders'] = monthly_data['Total_Orders'].shift(1)
monthly_data['Prev_Returns'] = monthly_data['Total_Returns'].shift(1)

# Step 3: Prepare Data for GUI
# Latest Month Data
latest_data = monthly_data.iloc[-1]
monthly_revenue = latest_data['Total_Revenue'] or 0
monthly_orders = latest_data['Total_Orders'] or 0
monthly_returns = latest_data['Total_Returns'] or 0

# Previous Month Values
prev_revenue = latest_data['Prev_Revenue'] or 0
prev_orders = latest_data['Prev_Orders'] or 0
prev_returns = latest_data['Prev_Returns'] or 0

# KPI Trends
revenue_trend = ((monthly_revenue - prev_revenue) / prev_revenue * 100) if prev_revenue else 0
orders_trend = ((monthly_orders - prev_orders) / prev_orders * 100) if prev_orders else 0
returns_trend = ((monthly_returns - prev_returns) / prev_returns * 100) if prev_returns else 0

# Step 4: Create Taipy GUI with KPI Indicators
layout = """
# KPI Dashboard

<|{monthly_revenue}|indicator|format=$,.2f|type=number|label=Revenue (Current Month)|>
Current Revenue: <|{monthly_revenue:,.2f}|text|prefix=$|>  
Trend: <|{revenue_trend:.2f}|text|suffix=%|>  
Previous Month: <|{prev_revenue:,.2f}|text|prefix=$|>

<|{monthly_orders}|indicator|format=,.0f|type=number|label=Orders (Current Month)|>
Current Orders: <|{monthly_orders:,.0f}|text|>  
Trend: <|{orders_trend:.2f}|text|suffix=%|>  
Previous Month: <|{prev_orders:,.0f}|text|>

<|{monthly_returns}|indicator|format=,.0f|type=number|label=Returns (Current Month)|>
Current Returns: <|{monthly_returns:,.0f}|text|>  
Trend: <|{returns_trend:.2f}|text|suffix=%|>  
Previous Month: <|{prev_returns:,.0f}|text|>
"""

gui = Gui(page=layout)
gui.run()
