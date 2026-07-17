import json

notebook = {
 "cells": [
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "# Phase 1: Data Cleaning & Merging\n",
    "\n",
    "In this notebook, we load the raw Kaggle datasets, merge them into a unified view, handle missing values, and parse dates. This sets the foundation for our analytical models."
   ]
  },
  {
   "cell_type": "code",
   "execution_count": None,
   "metadata": {},
   "outputs": [],
   "source": [
    "import pandas as pd\n",
    "import numpy as np\n",
    "import os\n",
    "\n",
    "# Set options for pandas\n",
    "pd.set_option('display.max_columns', None)"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "## 1. Load the Datasets\n",
    "We load the core relational tables needed for customer and operational analytics."
   ]
  },
  {
   "cell_type": "code",
   "execution_count": None,
   "metadata": {},
   "outputs": [],
   "source": [
    "raw_dir = '../data/raw/'\n",
    "\n",
    "orders = pd.read_csv(os.path.join(raw_dir, 'olist_orders_dataset.csv'))\n",
    "items = pd.read_csv(os.path.join(raw_dir, 'olist_order_items_dataset.csv'))\n",
    "customers = pd.read_csv(os.path.join(raw_dir, 'olist_customers_dataset.csv'))\n",
    "sellers = pd.read_csv(os.path.join(raw_dir, 'olist_sellers_dataset.csv'))\n",
    "reviews = pd.read_csv(os.path.join(raw_dir, 'olist_order_reviews_dataset.csv'))\n",
    "products = pd.read_csv(os.path.join(raw_dir, 'olist_products_dataset.csv'))\n",
    "translation = pd.read_csv(os.path.join(raw_dir, 'product_category_name_translation.csv'))\n",
    "\n",
    "print(f\"Orders: {orders.shape}\")\n",
    "print(f\"Items: {items.shape}\")\n",
    "print(f\"Customers: {customers.shape}\")"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "## 2. Translate Product Categories\n",
    "Convert Portuguese category names to English."
   ]
  },
  {
   "cell_type": "code",
   "execution_count": None,
   "metadata": {},
   "outputs": [],
   "source": [
    "products = products.merge(translation, on='product_category_name', how='left')\n",
    "# Drop the portuguese column and rename the english one\n",
    "products.drop('product_category_name', axis=1, inplace=True)\n",
    "products.rename(columns={'product_category_name_english': 'product_category_name'}, inplace=True)"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "## 3. Merge the Data\n",
    "Merge the datasets around the `order_id`."
   ]
  },
  {
   "cell_type": "code",
   "execution_count": None,
   "metadata": {},
   "outputs": [],
   "source": [
    "# Start with orders\n",
    "df = orders.merge(customers, on='customer_id', how='left')\n",
    "df = df.merge(items, on='order_id', how='left')\n",
    "df = df.merge(sellers, on='seller_id', how='left')\n",
    "df = df.merge(products, on='product_id', how='left')\n",
    "\n",
    "# Reviews can have multiple entries per order. We keep the most recent review per order to avoid duplicates.\n",
    "reviews_dedup = reviews.sort_values('review_creation_date').drop_duplicates('order_id', keep='last')\n",
    "df = df.merge(reviews_dedup, on='order_id', how='left')\n",
    "\n",
    "print(f\"Merged Dataset Shape: {df.shape}\")"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "## 4. Datetime Formatting & Feature Engineering\n",
    "Convert string dates to `datetime` objects, and calculate operational KPIs like delivery delay."
   ]
  },
  {
   "cell_type": "code",
   "execution_count": None,
   "metadata": {},
   "outputs": [],
   "source": [
    "datetime_cols = [\n",
    "    'order_purchase_timestamp', 'order_approved_at', \n",
    "    'order_delivered_carrier_date', 'order_delivered_customer_date', \n",
    "    'order_estimated_delivery_date', 'review_creation_date', \n",
    "    'review_answer_timestamp'\n",
    "]\n",
    "\n",
    "for col in datetime_cols:\n",
    "    df[col] = pd.to_datetime(df[col])\n",
    "\n",
    "# Calculate delay: Actual Delivery - Estimated Delivery\n",
    "# If delay > 0, it was delivered late.\n",
    "df['delivery_delay_days'] = (df['order_delivered_customer_date'] - df['order_estimated_delivery_date']).dt.total_seconds() / (24 * 3600)\n",
    "\n",
    "# Flag delayed orders\n",
    "df['is_delayed'] = df['delivery_delay_days'] > 0\n",
    "\n",
    "df[['order_delivered_customer_date', 'order_estimated_delivery_date', 'delivery_delay_days', 'is_delayed']].head()"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "## 5. Handling Missing Values\n",
    "Identify columns with missing values and handle them appropriately."
   ]
  },
  {
   "cell_type": "code",
   "execution_count": None,
   "metadata": {},
   "outputs": [],
   "source": [
    "missing_percentages = df.isnull().sum() / len(df) * 100\n",
    "print(\"Missing Values (>0%):\")\n",
    "print(missing_percentages[missing_percentages > 0].sort_values(ascending=False))\n",
    "\n",
    "# For items where product_id/seller_id is null (e.g. cancelled orders before fulfillment)\n",
    "# We will keep them for overall revenue tracking but they won't have product details.\n",
    "# Review scores that are missing can be filled with median or left as NaN.\n",
    "# We will leave them as NaN so they are ignored in averages rather than skewed.\n"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "## 6. Export Processed Data\n",
    "Save the master cleaned dataset to `data/processed/`."
   ]
  },
  {
   "cell_type": "code",
   "execution_count": None,
   "metadata": {},
   "outputs": [],
   "source": [
    "output_path = '../data/processed/merged_olist_data.csv'\n",
    "df.to_csv(output_path, index=False)\n",
    "print(f\"Data successfully exported to {output_path}\")"
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

with open('/Users/manav/Library/CloudStorage/OneDrive-MSFT/Codes/olist-ecommerce-analytics/notebooks/01_data_cleaning.ipynb', 'w') as f:
    json.dump(notebook, f, indent=1)

print("Notebook generated successfully!")
