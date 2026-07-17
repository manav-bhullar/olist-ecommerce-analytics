import json

notebook = {
 "cells": [
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "# Phase 2: RFM Customer Segmentation\n",
    "\n",
    "RFM (Recency, Frequency, Monetary) analysis is a proven marketing model for behavior-based customer segmentation. It groups customers based on their transaction history:\n",
    "- **Recency**: How recently a customer has made a purchase\n",
    "- **Frequency**: How often they purchase\n",
    "- **Monetary**: How much they spend"
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
    "import matplotlib.pyplot as plt\n",
    "import seaborn as sns\n",
    "\n",
    "# Set plotting style\n",
    "sns.set_theme(style=\"whitegrid\")\n",
    "plt.rcParams['figure.figsize'] = (10, 6)"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "## 1. Load Processed Data"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": None,
   "metadata": {},
   "outputs": [],
   "source": [
    "df = pd.read_csv('../data/processed/merged_olist_data.csv')\n",
    "df['order_purchase_timestamp'] = pd.to_datetime(df['order_purchase_timestamp'])\n",
    "print(f\"Loaded {df.shape[0]:,} rows.\")"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "## 2. Calculate RFM Metrics"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": None,
   "metadata": {},
   "outputs": [],
   "source": [
    "now = df['order_purchase_timestamp'].max() + pd.Timedelta(days=1)\n",
    "df['total_value'] = df['price'].fillna(0) + df['freight_value'].fillna(0)\n",
    "\n",
    "rfm = df.groupby('customer_unique_id').agg({\n",
    "    'order_purchase_timestamp': lambda x: (now - x.max()).days, # Recency\n",
    "    'order_id': 'nunique',                                      # Frequency\n",
    "    'total_value': 'sum'                                        # Monetary\n",
    "}).reset_index()\n",
    "\n",
    "rfm.columns = ['customer_unique_id', 'Recency', 'Frequency', 'Monetary']\n",
    "rfm.head()"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "## 3. RFM Scoring"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": None,
   "metadata": {},
   "outputs": [],
   "source": [
    "r_labels = range(4, 0, -1)\n",
    "r_quartiles = pd.qcut(rfm['Recency'], q=4, labels=r_labels)\n",
    "rfm['R'] = r_quartiles.astype(str)\n",
    "\n",
    "f_bins = [0, 1, 2, 3, np.inf]\n",
    "f_labels = ['1', '2', '3', '4']\n",
    "rfm['F'] = pd.cut(rfm['Frequency'], bins=f_bins, labels=f_labels).astype(str)\n",
    "\n",
    "m_labels = range(1, 5)\n",
    "m_quartiles = pd.qcut(rfm['Monetary'].rank(method='first'), q=4, labels=m_labels)\n",
    "rfm['M'] = m_quartiles.astype(str)\n",
    "\n",
    "rfm['RFM_Segment'] = rfm['R'] + rfm['F'] + rfm['M']\n",
    "rfm.head()"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "## 4. Customer Segmentation"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": None,
   "metadata": {},
   "outputs": [],
   "source": [
    "def segment_customer(row):\n",
    "    r = int(row['R'])\n",
    "    f = int(row['F'])\n",
    "    if r >= 4 and f >= 3:\n",
    "        return 'Champions'\n",
    "    elif r >= 3 and f >= 2:\n",
    "        return 'Loyal'\n",
    "    elif r <= 2 and f >= 2:\n",
    "        return 'At-Risk'\n",
    "    elif r <= 2 and f == 1:\n",
    "        return 'Lost'\n",
    "    else:\n",
    "        return 'New/Recent'\n",
    "\n",
    "rfm['Segment'] = rfm.apply(segment_customer, axis=1)\n",
    "segment_counts = rfm['Segment'].value_counts().reset_index()\n",
    "segment_counts.columns = ['Segment', 'Count']\n",
    "segment_counts['Percentage'] = (segment_counts['Count'] / segment_counts['Count'].sum()) * 100\n",
    "segment_counts"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "## 5. Visualizing Segments"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": None,
   "metadata": {},
   "outputs": [],
   "source": [
    "plt.figure(figsize=(10, 6))\n",
    "sns.barplot(x='Segment', y='Count', data=segment_counts, hue='Segment', palette='viridis', legend=False)\n",
    "plt.title('Customer Segment Distribution')\n",
    "plt.ylabel('Number of Customers')\n",
    "plt.xlabel('Segment')\n",
    "for i, v in enumerate(segment_counts['Percentage']):\n",
    "    plt.text(i, segment_counts['Count'].iloc[i] + 500, f'{v:.1f}%', ha='center', fontweight='bold')\n",
    "plt.show()"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "## 6. Save RFM Data"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": None,
   "metadata": {},
   "outputs": [],
   "source": [
    "df = df.merge(rfm[['customer_unique_id', 'Segment']], on='customer_unique_id', how='left')\n",
    "df.to_csv('../data/processed/merged_olist_data.csv', index=False)\n",
    "print(\"RFM Segments merged and dataset updated.\")"
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

with open('/Users/manav/Library/CloudStorage/OneDrive-MSFT/Codes/olist-ecommerce-analytics/notebooks/02_rfm_analysis.ipynb', 'w') as f:
    json.dump(notebook, f, indent=1)

print("Notebook 02 generated successfully!")
