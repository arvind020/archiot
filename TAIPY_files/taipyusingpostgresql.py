import psycopg2
import pandas as pd
import taipy.gui as tg
import taipy.gui.builder as tgb

# Database connection settings
db_config = {
    "dbname": "new_db",
    "user": "postgres",
    "password": "Animal@123",
    "host": "localhost",
    "port": "5432"
}

# Fetch data from PostgreSQL database
def fetch_data():
    # Establish connection to the database
    conn = psycopg2.connect(**db_config)
    query = """
        SELECT 
            j.job_title, 
            COUNT(e.employee_id) AS employee_count
        FROM 
            jobs j
        LEFT JOIN 
            employees e 
        ON 
            j.job_id = e.job_id
        GROUP BY 
            j.job_title
        ORDER BY 
            employee_count DESC;
    """
    # Execute the query and load data into a Pandas DataFrame
    data = pd.read_sql_query(query, conn)
    conn.close()
    return data

# Fetch the aggregated data
data = fetch_data()

# Define the Taipy GUI page
page = tgb.Page(
    tgb.chart(
        "{data}",
        type="bar",
        x="job_title",
        y="employee_count",
        title="Number of Employees by Job Title",
        x_title="Job Title",
        y_title="Number of Employees",
    )
)

# Running the Taipy GUI with the page
tg.Gui(page).run()
