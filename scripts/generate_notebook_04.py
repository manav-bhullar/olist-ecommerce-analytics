import json

notebook = {
 "cells": [
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "# Phase 4: Revenue & Category Analysis (SQL)\n",
    "\n",
    "In this notebook, we use DuckDB to run high-performance SQL queries directly against our processed CSV data. This allows us to extract business-critical KPIs using standard SQL."
   ]
  },
  {
   "cell_type": "code",
   "execution_count": None,
   "metadata": {},
   "outputs": [],
   "source": [
    "import duckdb\n",
    "import pandas as pd\n",
    "import matplotlib.pyplot as plt\n",
    "import seaborn as sns\n",
    "\n",
    "sns.set_theme(style=\"whitegrid\")"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "## 1. Connect to DuckDB"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": None,
   "metadata": {},
   "outputs": [],
   "source": [
    "conn = duckdb.connect(database=':memory:')\n",
    "\n",
    "# Read the CSV into a DuckDB relation\n",
    "conn.execute(\"\"\"\n",
    "    CREATE VIEW orders AS \n",
    "    SELECT * FROM read_csv_auto('../data/processed/merged_olist_data.csv')\n",
    "\"\"\")\n",
    "print(\"View 'orders' created successfully.\")"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "## 2. Top 10 Product Categories by Revenue"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": None,
   "metadata": {},
   "outputs": [],
   "source": [
    "query = \"\"\"\n",
    "SELECT \n",
    "    product_category_name AS Category,\n",
    "    SUM(price) AS Total_Revenue,\n",
    "    COUNT(DISTINCT order_id) AS Total_Orders\n",
    "FROM orders\n",
    "WHERE product_category_name IS NOT NULL\n",
    "GROUP BY Category\n",
    "ORDER BY Total_Revenue DESC\n",
    "LIMIT 10;\n",
    "\"\"\"\n",
    "top_categories = conn.execute(query).df()\n",
    "top_categories"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "## 3. Month-over-Month Revenue Growth"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": None,
   "metadata": {},
   "outputs": [],
   "source": [
    "query = \"\"\"\n",
    "WITH monthly_revenue AS (\n",
    "    SELECT \n",
    "        DATE_TRUNC('month', CAST(order_purchase_timestamp AS TIMESTAMP)) AS Month,\n",
    "        SUM(price) AS Revenue\n",
    "    FROM orders\n",
    "    WHERE order_purchase_timestamp IS NOT NULL\n",
    "    GROUP BY Month\n",
    ")\n",
    "SELECT \n",
    "    Month,\n",
    "    Revenue,\n",
    "    LAG(Revenue) OVER (ORDER BY Month) AS Previous_Month_Revenue,\n",
    "    ((Revenue - LAG(Revenue) OVER (ORDER BY Month)) / LAG(Revenue) OVER (ORDER BY Month)) * 100 AS MoM_Growth_Pct\n",
    "FROM monthly_revenue\n",
    "ORDER BY Month;\n",
    "\"\"\"\n",
    "mom_growth = conn.execute(query).df()\n",
    "mom_growth.dropna().head(10)"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "## 4. Average Order Value (AOV) by State"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": None,
   "metadata": {},
   "outputs": [],
   "source": [
    "query = \"\"\"\n",
    "WITH order_totals AS (\n",
    "    SELECT \n",
    "        order_id,\n",
    "        customer_state,\n",
    "        SUM(price + freight_value) AS Order_Total\n",
    "    FROM orders\n",
    "    WHERE customer_state IS NOT NULL\n",
    "    GROUP BY order_id, customer_state\n",
    ")\n",
    "SELECT \n",
    "    customer_state AS State,\n",
    "    AVG(Order_Total) AS AOV,\n",
    "    COUNT(order_id) AS Total_Orders\n",
    "FROM order_totals\n",
    "GROUP BY State\n",
    "HAVING COUNT(order_id) > 1000\n",
    "ORDER BY AOV DESC;\n",
    "\"\"\"\n",
    "aov_state = conn.execute(query).df()\n",
    "aov_state"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "## 5. Seller Performance Ranking"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": None,
   "metadata": {},
   "outputs": [],
   "source": [
    "query = \"\"\"\n",
    "SELECT \n",
    "    seller_id,\n",
    "    COUNT(DISTINCT order_id) AS Total_Orders_Fulfilled,\n",
    "    SUM(price) AS Total_Revenue,\n",
    "    AVG(delivery_delay_days) AS Avg_Delivery_Delay,\n",
    "    AVG(review_score) AS Avg_Review_Score\n",
    "FROM orders\n",
    "WHERE seller_id IS NOT NULL\n",
    "GROUP BY seller_id\n",
    "HAVING COUNT(DISTINCT order_id) > 100\n",
    "ORDER BY Avg_Review_Score DESC, Total_Orders_Fulfilled DESC\n",
    "LIMIT 10;\n",
    "\"\"\"\n",
    "top_sellers = conn.execute(query).df()\n",
    "top_sellers"
   ]
  }
 ],
 "metadata": {
  "kernelspec": {
   "display_name": "Python 3",
   "language": "python",
   "name": "python3"
  },
  "language_info": {
   "codemirror_mode": {
    "name": "ipython",
    "version": 3
   },
   "file_extension": ".py",
   "mimetype": "text/x-python",
   "name": "python",
   "nbconvert_exporter": "python",
   "pygments_lexer": "ipython3",
   "version": "3.9.0"
  }
 },
 "nbformat": 4,
 "nbformat_minor": 4
}

with open('/Users/manav/Library/CloudStorage/OneDrive-MSFT/Codes/olist-ecommerce-analytics/notebooks/04_revenue_sql_analysis.ipynb', 'w') as f:
    json.dump(notebook, f, indent=1)

print("Notebook 04 generated successfully!")
