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
    "sales_2021": "C:/Users/Aravind/Desktop/AdventureWorks Raw Data/AdventureWorks Sales Data 2020.csv",
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
product_categories = load_csv(csv_files["product_categories"])
sales_2020 = load_csv(csv_files["sales_2020"])
sales_2021 = load_csv(csv_files["sales_2021"])
sales_2022 = load_csv(csv_files["sales_2022"])

# Step 2: Clean and preprocess data
product_lookup.columns = product_lookup.columns.str.strip().str.lower()
product_categories.columns = product_categories.columns.str.strip().str.lower()
sales_2020.columns = sales_2020.columns.str.strip().str.lower()
sales_2021.columns = sales_2021.columns.str.strip().str.lower()
sales_2022.columns = sales_2022.columns.str.strip().str.lower()

# Step 3: Combine Sales Data
sales_data = pd.concat([sales_2020, sales_2021, sales_2022], ignore_index=True)

# Step 4: Merge Sales Data with Product Lookup to get Product Category Key
merged_data = pd.merge(
    sales_data,
    product_lookup,
    on="productkey",  # Ensure correct column name
    how="left"
)

# Step 5: Merge Sales Data with Product Categories to get Category Name
merged_data = pd.merge(
    merged_data,
    product_categories,
    left_on="productsubcategorykey",  # Assuming the correct column is 'productsubcategorykey' in merged_data
    right_on="productcategorykey",  # Assuming the correct key in product_categories is 'productcategorykey'
    how="left"
)

# Step 6: Inspect Category Names for Debugging
# Checking if "Accessories" and other categories are present
print("Unique category names in merged_data before cleaning:")
print(merged_data['categoryname'].unique())

# Clean the 'categoryname' column to avoid issues with spaces or casing differences
merged_data['categoryname'] = merged_data['categoryname'].str.strip().str.title()

# Check again after cleaning
print("\nUnique category names in merged_data after cleaning:")
print(merged_data['categoryname'].unique())

# Step 7: Calculate Total Orders using DISTINCTCOUNT equivalent (using pd.nunique for distinct count)
total_orders = merged_data.groupby("categoryname")["ordernumber"].nunique().reset_index()
total_orders.columns = ["categoryname", "total_orders"]

# Step 8: Create the Page with Bar Chart

# Define the layout with bar chart
page = tgb.Page(
    tgb.chart(
        "{total_orders}",  # Bar chart for total orders by category
        type="bar",  # Bar chart mode
        x="categoryname",  # X-axis column (Product Category)
        y="total_orders",  # Y-axis column (Total Orders)
        title="Total Orders by Category",  # Title of the chart
        x_title="Product Category",  # X-axis title
        y_title="Total Orders",  # Y-axis title
        width="80%",
        margin_left="5%"
    )
)

# Step 9: Running the Taipy GUI with the page
tg.Gui(page).run()
