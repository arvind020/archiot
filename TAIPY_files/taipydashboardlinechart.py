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

# Step 2: Clean and preprocess data
product_lookup.columns = product_lookup.columns.str.strip().str.lower()
sales_2020.columns = sales_2020.columns.str.strip().str.lower()
sales_2021.columns = sales_2021.columns.str.strip().str.lower()
sales_2022.columns = sales_2022.columns.str.strip().str.lower()

# Step 3: Combine Sales Data
sales_data = pd.concat([sales_2020, sales_2021, sales_2022], ignore_index=True)

# Step 4: Merge Sales Data with Product Lookup to Calculate Total Revenue
merged_data = pd.merge(
    sales_data,
    product_lookup,
    on="productkey",  # Ensure correct column name
    how="left"
)

# Step 5: Calculate Total Revenue using the DAX formula in Python
merged_data["total_revenue"] = merged_data["orderquantity"] * merged_data["productprice"]

# Step 6: Aggregate Revenue by Start of Month
merged_data["start_of_month"] = pd.to_datetime(merged_data["orderdate"]).dt.to_period("M").dt.start_time
revenue_data = merged_data.groupby("start_of_month", as_index=False)["total_revenue"].sum()

# Ensure correct data types for plotting
revenue_data["start_of_month"] = pd.to_datetime(revenue_data["start_of_month"])
revenue_data["total_revenue"] = pd.to_numeric(revenue_data["total_revenue"], errors='coerce')

# Step 7: Create a Chart in Taipy GUI using the requested format
page = tgb.Page(
    tgb.chart(
        "{revenue_data}",  # Pass data directly as a string
        mode="lines",  # Line chart mode
        x="start_of_month",  # X-axis column
        y__1="total_revenue",  # Y-axis column (Total Revenue)
        line__1="solid",  # Line style (solid line)
        color__1="blue",  # Line color
        title="Total Revenue Over Time",  # Title of the chart
        x_title="Start of Month",  # X-axis title
        y_title="Total Revenue",  # Y-axis title
        width="50%",
        margin_left="5%"
    )
)

# Step 8: Running the Taipy GUI with the page
tg.Gui(page).run()
