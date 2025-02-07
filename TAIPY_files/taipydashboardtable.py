import pandas as pd
import taipy.gui as tg
import taipy.gui.builder as tgb

# Step 1: Load Data from Multiple CSV Files
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

# Load each CSV file into individual DataFrames with error handling for encoding
def load_csv(file_path):
    try:
        return pd.read_csv(file_path, encoding='utf-8')
    except UnicodeDecodeError:
        return pd.read_csv(file_path, encoding='ISO-8859-1')

# Loading the data
product_lookup = load_csv(csv_files["product_lookup"])
sales_2020 = load_csv(csv_files["sales_2020"])
sales_2021 = load_csv(csv_files["sales_2021"])
sales_2022 = load_csv(csv_files["sales_2022"])
returns_data = load_csv(csv_files["returns"])

# Step 2: Clean and preprocess data
product_lookup.columns = product_lookup.columns.str.strip().str.lower()
sales_2020.columns = sales_2020.columns.str.strip().str.lower()
sales_2021.columns = sales_2021.columns.str.strip().str.lower()
sales_2022.columns = sales_2022.columns.str.strip().str.lower()
returns_data.columns = returns_data.columns.str.strip().str.lower()

# Step 3: Combine Sales Data
sales_data = pd.concat([sales_2020, sales_2021, sales_2022], ignore_index=True)

# Step 4: Calculate Measures
# Total Orders: DISTINCTCOUNT('Sales Data'[OrderNumber])
sales_data['distinct_order'] = sales_data['ordernumber']
total_orders = sales_data.groupby('productkey')['distinct_order'].nunique()

# Quantity Sold: SUM('Sales Data'[OrderQuantity])
quantity_sold = sales_data.groupby('productkey')['orderquantity'].sum()

# Quantity Returned: SUM('Returns Data'[ReturnQuantity])
quantity_returned = returns_data.groupby('productkey')['returnquantity'].sum()

# Merge sales and product lookup data
merged_data = pd.merge(sales_data, product_lookup, on="productkey", how="left")

# Total Revenue: SUMX('Sales Data', 'Sales Data'[OrderQuantity] * RELATED('Product Lookup'[ProductPrice]))
merged_data['total_revenue'] = merged_data['orderquantity'] * merged_data['productprice']

# Return Rate: DIVIDE([Quantity Returned], [Quantity Sold], "No Sales")
return_rate = (quantity_returned / quantity_sold).fillna("No Sales")

# Step 5: Create a Summary Table
summary_table = pd.DataFrame({
    'ProductName': product_lookup.set_index('productkey').loc[total_orders.index, 'productname'],
    'TotalOrders': total_orders.values,
    'TotalRevenue': merged_data.groupby('productkey')['total_revenue'].sum().values,
    'ReturnRate': return_rate.reindex(total_orders.index, fill_value="No Sales").values
}).reset_index(drop=True)

# Select the top 10 products and required columns
top_10_products = summary_table[['ProductName', 'TotalOrders', 'TotalRevenue', 'ReturnRate']].head(10)

# Step 6: Create a Table Visualization in Taipy GUI
page = tgb.Page(
    tgb.table(
        "{top_10_products}",  # Data binding
        title="Top 10 Products",  # Title of the table
        headers=["Product Name", "Total Orders", "Total Revenue", "Return Rate"],  # Table headers
        width="80%",  # Table width
        margin_left="10%"  # Center alignment
    )
)

# Step 7: Run the Taipy GUI
gui = tg.Gui(page)
gui.run()
