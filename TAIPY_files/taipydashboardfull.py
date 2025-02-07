import pandas as pd
import taipy.gui as tg

# Load Data from CSV Files
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

def load_csv(file_path):
    try:
        return pd.read_csv(file_path, encoding='utf-8')
    except UnicodeDecodeError:
        return pd.read_csv(file_path, encoding='ISO-8859-1')

# Load DataFrames
product_lookup = load_csv(csv_files["product_lookup"])
product_categories = load_csv(csv_files["product_categories"])
sales_2020 = load_csv(csv_files["sales_2020"])
sales_2021 = load_csv(csv_files["sales_2021"])
sales_2022 = load_csv(csv_files["sales_2022"])

# Preprocessing for Total Orders
product_lookup.columns = product_lookup.columns.str.strip().str.lower()
product_categories.columns = product_categories.columns.str.strip().str.lower()
sales_2020.columns = sales_2020.columns.str.strip().str.lower()
sales_2021.columns = sales_2021.columns.str.strip().str.lower()
sales_2022.columns = sales_2022.columns.str.strip().str.lower()

sales_data = pd.concat([sales_2020, sales_2021, sales_2022], ignore_index=True)
merged_orders = pd.merge(sales_data, product_lookup, on="productkey", how="left")
merged_orders = pd.merge(
    merged_orders,
    product_categories,
    left_on="productsubcategorykey",
    right_on="productcategorykey",
    how="left"
)

merged_orders['categoryname'] = merged_orders['categoryname'].str.strip().str.title()
total_orders = merged_orders.groupby("categoryname")["ordernumber"].nunique().reset_index()
total_orders.columns = ["categoryname", "total_orders"]

# Preprocessing for Revenue
merged_revenue = pd.merge(sales_data, product_lookup, on="productkey", how="left")
merged_revenue["total_revenue"] = merged_revenue["orderquantity"] * merged_revenue["productprice"]
merged_revenue["start_of_month"] = pd.to_datetime(merged_revenue["orderdate"]).dt.to_period("M").dt.start_time
revenue_data = merged_revenue.groupby("start_of_month", as_index=False)["total_revenue"].sum()
revenue_data["start_of_month"] = pd.to_datetime(revenue_data["start_of_month"])

# Define the Combined Layout using HTML-like Syntax
page = """
<|layout|columns=2|gap=10px|
<|{total_orders}|chart|type=bar|x=categoryname|y=total_orders|title=Total Orders by Category|x_title=Product Category|y_title=Total Orders|width=100%|>
<|{revenue_data}|chart|type=line|x=start_of_month|y=total_revenue|title=Total Revenue Over Time|x_title=Start of Month|y_title=Total Revenue|width=100%|>
|>
"""

# Run the GUI
gui = tg.Gui(page)
gui.run()
