import pandas as pd
from taipy.gui import Gui
import matplotlib.pyplot as plt
import seaborn as sns

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
dfs = {key: pd.read_csv(path, encoding='ISO-8859-1') for key, path in csv_files.items()}

# Extract relevant dataframes
sales_df_2020 = dfs["sales_2020"]
sales_df_2021 = dfs["sales_2021"]
sales_df_2022 = dfs["sales_2022"]
returns_df = dfs["returns"]
product_lookup_df = dfs["product_lookup"]

# Combine sales data from all years
sales_df = pd.concat([sales_df_2020, sales_df_2021, sales_df_2022], ignore_index=True)

# Step 2: Merge Sales Data with Product Lookup to get the necessary columns (Product Price and Product Cost)
sales_df = sales_df.merge(product_lookup_df[['ProductKey', 'ProductPrice', 'ProductCost']], on='ProductKey', how='left')

# Fill missing product price and cost
sales_df['ProductPrice'].fillna(0, inplace=True)
sales_df['ProductCost'].fillna(0, inplace=True)

# Step 3: Calculate Total Revenue, Total Cost, Total Profit, Total Orders, and Return Rate
sales_df['Revenue'] = sales_df['OrderQuantity'] * sales_df['ProductPrice']
total_revenue = sales_df['Revenue'].sum()

sales_df['Cost'] = sales_df['OrderQuantity'] * sales_df['ProductCost']
total_cost = sales_df['Cost'].sum()

total_profit = total_revenue - total_cost
total_orders = sales_df['OrderNumber'].nunique()

total_quantity_returned = returns_df['ReturnQuantity'].sum()
total_quantity_sold = sales_df['OrderQuantity'].sum()

# Calculate return rate
return_rate = f"{(total_quantity_returned / total_quantity_sold):.2%}" if total_quantity_sold > 0 else "No Sales"

# Step 4: Prepare Monthly Data and Trend Calculations
sales_df['OrderDate'] = pd.to_datetime(sales_df['OrderDate'], errors='coerce')
sales_df.set_index('OrderDate', inplace=True)

monthly_data = sales_df.resample('M').agg(
    Total_Revenue=('Revenue', 'sum'),
    Total_Orders=('OrderNumber', 'nunique')
).reset_index()

returns_df['ReturnDate'] = pd.to_datetime(returns_df['ReturnDate'], errors='coerce')
returns_df.set_index('ReturnDate', inplace=True)

monthly_returns = returns_df.resample('M').agg(
    Total_Returns=('ReturnQuantity', 'sum')
).reset_index()

monthly_data = pd.merge(
    monthly_data, monthly_returns,
    left_on='OrderDate', right_on='ReturnDate', how='outer'
)

monthly_data.fillna(0, inplace=True)

latest_data = monthly_data.iloc[-1]
monthly_revenue = latest_data['Total_Revenue']
monthly_orders = latest_data['Total_Orders']
monthly_returns = latest_data['Total_Returns']

prev_revenue = monthly_data['Total_Revenue'].shift(1).iloc[-1]
prev_orders = monthly_data['Total_Orders'].shift(1).iloc[-1]
prev_returns = monthly_data['Total_Returns'].shift(1).iloc[-1]

# Calculate trends
revenue_trend = ((monthly_revenue - prev_revenue) / prev_revenue * 100) if prev_revenue else 0
orders_trend = ((monthly_orders - prev_orders) / prev_orders * 100) if prev_orders else 0
returns_trend = ((monthly_returns - prev_returns) / prev_returns * 100) if prev_returns else 0

# Step 5: Plotting Line Chart for Revenue and Bar Plot for Orders

# Line Chart for Revenue
plt.figure(figsize=(8, 6))
sns.lineplot(x=monthly_data['OrderDate'], y=monthly_data['Total_Revenue'], marker='o', color='blue')
plt.title('Monthly Revenue')
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig("revenue_linechart.png")  # Save line chart for revenue

# Bar Plot for Total Orders
plt.figure(figsize=(8, 6))
sns.barplot(x=monthly_data['OrderDate'].dt.strftime('%Y-%m'), y=monthly_data['Total_Orders'], color='green')
plt.title('Monthly Total Orders')
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig("orders_barplot.png")  # Save bar plot for orders

# Step 6: Create Taipy GUI layout
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

## Monthly Revenue Line Chart
<|revenue_linechart.png|image|size=500x300|label=Monthly Revenue Line Chart|>

## Monthly Orders Bar Plot
<|orders_barplot.png|image|size=500x300|label=Monthly Total Orders Bar Plot|>

## KPI Dashboard for Current Month
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

# Step 7: Run the Taipy GUI
gui = Gui(page=layout)
gui.run()