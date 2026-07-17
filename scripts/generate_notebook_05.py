import json

notebook = {
 "cells": [
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "# Phase 5: Final Export for Tableau\n",
    "\n",
    "In this final notebook, we prepare the dataset for our Tableau Public dashboard by ensuring all KPIs (RFM Segments, Delivery Delays, etc.) are correctly formatted."
   ]
  },
  {
   "cell_type": "code",
   "execution_count": None,
   "metadata": {},
   "outputs": [],
   "source": [
    "import pandas as pd\n",
    "\n",
    "df = pd.read_csv('../data/processed/merged_olist_data.csv')\n",
    "print(f\"Final dataset contains {df.shape[0]:,} rows and {df.shape[1]} columns.\")"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "## 1. Select Columns for Tableau\n",
    "We don't need all 40 columns. We will trim down the dataset to only what's required for the dashboard to optimize performance."
   ]
  },
  {
   "cell_type": "code",
   "execution_count": None,
   "metadata": {},
   "outputs": [],
   "source": [
    "tableau_cols = [\n",
    "    'order_id', 'customer_unique_id', 'seller_id', 'product_id',\n",
    "    'order_purchase_timestamp', 'price', 'freight_value',\n",
    "    'customer_state', 'customer_city',\n",
    "    'seller_state', 'seller_city',\n",
    "    'product_category_name',\n",
    "    'review_score',\n",
    "    'delivery_delay_days', 'is_delayed',\n",
    "    'Segment' # RFM Segment\n",
    "]\n",
    "\n",
    "df_tableau = df[[col for col in tableau_cols if col in df.columns]].copy()\n",
    "\n",
    "# Ensure date is properly formatted\n",
    "df_tableau['order_purchase_timestamp'] = pd.to_datetime(df_tableau['order_purchase_timestamp']).dt.date\n",
    "\n",
    "df_tableau.head()"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "## 2. Export to CSV"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": None,
   "metadata": {},
   "outputs": [],
   "source": [
    "df_tableau.to_csv('../data/processed/tableau_export.csv', index=False)\n",
    "print(\"tableau_export.csv generated successfully for Tableau Public!\")"
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

with open('/Users/manav/Library/CloudStorage/OneDrive-MSFT/Codes/olist-ecommerce-analytics/notebooks/05_final_export_and_eda.ipynb', 'w') as f:
    json.dump(notebook, f, indent=1)

print("Notebook 05 generated successfully!")
