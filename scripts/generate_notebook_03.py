import json

notebook = {
 "cells": [
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "# Phase 3: Delivery Delay vs Review Score Analysis\n",
    "\n",
    "In this notebook, we quantify the impact of operational delays on customer satisfaction by analyzing the relationship between delivery delays and customer review scores."
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
    "sns.set_theme(style=\"whitegrid\")\n",
    "plt.rcParams['figure.figsize'] = (10, 6)"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "## 1. Load the Dataset"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": None,
   "metadata": {},
   "outputs": [],
   "source": [
    "df = pd.read_csv('../data/processed/merged_olist_data.csv')\n",
    "print(f\"Loaded {df.shape[0]:,} rows.\")"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "## 2. Prepare Delay Metrics"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": None,
   "metadata": {},
   "outputs": [],
   "source": [
    "# Drop rows where delivery date or review score is missing\n",
    "df_ops = df.dropna(subset=['delivery_delay_days', 'review_score']).copy()\n",
    "\n",
    "def categorize_delay(days):\n",
    "    if days <= 0:\n",
    "        return 'On Time / Early'\n",
    "    elif days <= 2:\n",
    "        return '1-2 Days Late'\n",
    "    elif days <= 5:\n",
    "        return '3-5 Days Late'\n",
    "    else:\n",
    "        return '6+ Days Late'\n",
    "\n",
    "df_ops['delay_category'] = df_ops['delivery_delay_days'].apply(categorize_delay)\n",
    "df_ops['delay_category'] = pd.Categorical(df_ops['delay_category'], \n",
    "                                          categories=['On Time / Early', '1-2 Days Late', '3-5 Days Late', '6+ Days Late'], \n",
    "                                          ordered=True)\n",
    "df_ops[['delivery_delay_days', 'delay_category', 'review_score']].head()"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "## 3. Analyze Impact on Review Scores"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": None,
   "metadata": {},
   "outputs": [],
   "source": [
    "impact = df_ops.groupby('delay_category').agg({\n",
    "    'review_score': ['mean', 'count']\n",
    "}).reset_index()\n",
    "impact.columns = ['Delay Category', 'Average Review Score', 'Number of Orders']\n",
    "\n",
    "baseline_score = impact.loc[impact['Delay Category'] == 'On Time / Early', 'Average Review Score'].values[0]\n",
    "impact['Score Drop vs Baseline'] = impact['Average Review Score'] - baseline_score\n",
    "impact"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "## 4. Visualizing the Impact"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": None,
   "metadata": {},
   "outputs": [],
   "source": [
    "fig, ax1 = plt.subplots(figsize=(12, 6))\n",
    "\n",
    "sns.barplot(x='Delay Category', y='Average Review Score', data=impact, ax=ax1, palette='coolwarm')\n",
    "ax1.set_ylim(0, 5)\n",
    "ax1.set_ylabel('Average Review Score')\n",
    "ax1.set_title('Impact of Delivery Delay on Customer Reviews')\n",
    "\n",
    "for i, row in impact.iterrows():\n",
    "    ax1.text(i, row['Average Review Score'] - 0.3, f\"{row['Average Review Score']:.2f}\", color='white', ha='center', fontweight='bold')\n",
    "\n",
    "plt.show()"
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

with open('/Users/manav/Library/CloudStorage/OneDrive-MSFT/Codes/olist-ecommerce-analytics/notebooks/03_operational_analysis.ipynb', 'w') as f:
    json.dump(notebook, f, indent=1)

print("Notebook 03 generated successfully!")
