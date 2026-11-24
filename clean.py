"""
ISM2411 Lab 14 — Clean a Messy Sales CSV
Author: Ahraya Dalaq
Run with: python clean.py

Self-Assessment
---------------
1. Filling with the mean feels most ambiguous because it invents values that might not reflect real sales. 
I would want to know why the data is missing and how much it affects totals.



2. Yes, each comment explains the reason behind the step, not just the step itself. 
Someone new could follow why rows were dropped or filled.


3. I did not expect placeholder values like a quantity of 9,999 or negative revenues from returns.
 Without describe(), those would have quietly disorted the totals.

"""

import pandas as pd

# ---------------------------------------------------------------
# Exercise 1: Inspect
# ---------------------------------------------------------------
df = pd.read_csv("data/messy_sales.csv")
print("=== Exercise 1 ===")
df.info()
print(df.isnull().sum())

# Data quality issues observed (at least 3, be specific):
# 1. Several columns have missing values (see isnull().sum() counts).
#    Rows missing order_id or order_date can't be used.
# 2. Unit Price is dtype object but should be float. It's stored as text
#    with "$" and "," symbols.
# 3. Order Date is dtype object but should be datetime. Some dates use
#    different formats or junk text like "TBD".

# ---------------------------------------------------------------
# Exercise 2: Standardize column names
# ---------------------------------------------------------------
df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")
print("\n=== Exercise 2 ===")
print(df.columns.tolist())

# ---------------------------------------------------------------
# Exercise 3: Handle missing values
# ---------------------------------------------------------------
print("\n=== Exercise 3 ===")
print("Shape before:", df.shape)

# Drop rows missing order_id or order_date: an order with no ID or date
# can't be tracked, deduplicated, or placed on a timeline, and there is no
# honest way to guess those values.
df = df.dropna(subset=["order_id", "order_date"])

# Fill numeric columns with the column mean: only a few values are missing,
# so the mean keeps the rows without noticeably changing averages or totals.
numeric_cols = df.select_dtypes(include="number").columns
df[numeric_cols] = df[numeric_cols].fillna(df[numeric_cols].mean())

print("Shape after:", df.shape)
print(df.isnull().sum())

# ---------------------------------------------------------------
# Exercise 4: Fix types
# ---------------------------------------------------------------
print("\n=== Exercise 4 ===")

# Dates: anything pandas can't read (other formats or junk like "TBD")
# becomes NaT instead of crashing the script.
df["order_date"] = pd.to_datetime(df["order_date"], errors="coerce")
print("Dates that became NaT:", df["order_date"].isna().sum())

# Prices: strip "$" and the thousands "," so "$1,299.00" -> 1299.0
# and a return like "-$45.00" -> -45.0.
df["unit_price"] = (
    df["unit_price"]
    .astype(str)
    .str.strip()
    .str.replace("$", "", regex=False)
    .str.replace(",", "", regex=False)
    .replace({"nan": None, "": None})
    .astype(float)
)
# Any price still missing after conversion gets the mean, same reasoning
# as Exercise 3 (few missing values, keeps the rows).
df["unit_price"] = df["unit_price"].fillna(df["unit_price"].mean())

# Quantities: a quantity must be a whole number, so round any filled mean
# before converting to int.
df["quantity_sold"] = pd.to_numeric(df["quantity_sold"], errors="coerce")
df["quantity_sold"] = df["quantity_sold"].fillna(df["quantity_sold"].mean())
df["quantity_sold"] = df["quantity_sold"].round().astype(int)

# Revenue column used in Lab 15's charts.
df["revenue"] = (df["unit_price"] * df["quantity_sold"]).round(2)

print(df.dtypes)

# ---------------------------------------------------------------
# Exercise 5: Check duplicates
# ---------------------------------------------------------------
print("\n=== Exercise 5 ===")
print("Duplicate rows:", df.duplicated().sum())
# Duplicate rows would count the same sale twice and inflate revenue.
df = df.drop_duplicates()
print("Shape after removing duplicates:", df.shape)

# ---------------------------------------------------------------
# Exercise 6: Describe
# ---------------------------------------------------------------
print("\n=== Exercise 6 ===")
print(df.describe())

# Suspicious statistics (at least 2) and a business explanation for each:
# 1. revenue has a negative minimum. These are returns, real refunds to
#    customers, so they are kept.
# 2. quantity_sold has a max of 9,999, far above normal orders. This looks
#    like a placeholder someone typed, not a real sale.

# Why the quantity_sold == 9999 rows are dropped:
# 9,999 is a placeholder, not a real order. Keeping it would hugely inflate
# revenue totals.

print("Rows with quantity_sold == 9999:", (df["quantity_sold"] == 9999).sum())
df = df[df["quantity_sold"] != 9999]
print("Shape after dropping placeholder quantities:", df.shape)

# ---------------------------------------------------------------
# Exercise 7: Save
# ---------------------------------------------------------------
print("\n=== Exercise 7 ===")
df.to_csv("data/clean_sales.csv", index=False)

# Reload without parse_dates: order_date comes back as text (object),
# because a CSV file has no date type.
check = pd.read_csv("data/clean_sales.csv")
check.info()

# Reload WITH parse_dates: order_date is datetime64 again.
# Lab 15 should load the file with this same line.
check = pd.read_csv("data/clean_sales.csv", parse_dates=["order_date"])
check.info()