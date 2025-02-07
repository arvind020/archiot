import pandas as pd
import taipy.gui as tg  # Correct import for Taipy GUI
import matplotlib.pyplot as plt

# Load your CSV dataset
data = pd.read_csv('C:/Users/Aravind/Downloads/Car_sales.csv')  # Replace with your actual dataset path

# Example: Assuming 'Model' is the X-axis and 'Sales_in_thousands' is the Y-axis
x_column = 'Model'  # Column for X-axis
y_column = 'Sales_in_thousands'  # Column for Y-axis

# Function to generate the bar chart plot
def bar_chart_view():
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.bar(data[x_column], data[y_column])
    ax.set_xlabel(x_column)
    ax.set_ylabel(y_column)
    ax.set_title(f"{y_column} by {x_column}")
    return fig

# Taipy GUI setup
page = """
<|{data}|chart|type=bar|x=Model|y=Sales_in_thousands|title=Sales by Car Model|>
"""

# Creating and running the GUI
tg.Gui(page=page).run()
