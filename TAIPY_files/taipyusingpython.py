import pandas as pd
import taipy.gui as tg  # Correct import for Taipy GUI
import taipy.gui.builder as tgb
import matplotlib.pyplot as plt
import io
import base64

# Load your CSV dataset
data = pd.read_csv('C:/Users/Aravind/Downloads/Car_sales.csv')  # Replace with your actual dataset path

# Function to create the bar chart with annotations using Matplotlib
def create_bar_chart():
    fig, ax = plt.subplots(figsize=(8, 6))
    bars = ax.bar(data['Model'], data['Sales_in_thousands'])
    ax.set_xlabel('Model')
    ax.set_ylabel('Sales in Thousands')
    ax.set_title('Sales by Car Model')

    # Add annotations on top of each bar
    for bar in bars:
        yval = bar.get_height()
        ax.text(bar.get_x() + bar.get_width() / 2, yval, round(yval, 2),
                ha='center', va='bottom', fontsize=10, color='black')

    # Save the plot to a BytesIO object to be used in Taipy
    img_buf = io.BytesIO()
    plt.savefig(img_buf, format='png')
    img_buf.seek(0)
    img_base64 = base64.b64encode(img_buf.read()).decode('utf-8')

    return img_base64

# Taipy GUI setup
# Create the bar chart with annotations using Matplotlib
img_base64 = create_bar_chart()

# Use tgb.chart() to display a Taipy bar chart and an image with annotations
page = tgb.Page(
    tgb.chart("{data}", type="bar", x="Model", y="Sales_in_thousands", title="Sales by Car Model"),
)

# Running the Taipy GUI with the page
tg.Gui(page).run()
