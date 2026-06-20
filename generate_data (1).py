"""
generate_data.py
----------------
Generates raw_data.csv with 500 realistic but intentionally dirty records.
Includes: missing values, duplicates, inconsistent text, invalid records.
Run this once before launching the Streamlit app.
"""

import pandas as pd
import numpy as np
import random
import os

random.seed(42)
np.random.seed(42)

# ── Reference data ────────────────────────────────────────────────────────────
FIRST_NAMES = [
    "Aarav", "Priya", "Rahul", "Sneha", "Vikram", "Ananya", "Arjun", "Kavya",
    "Rohan", "Divya", "Kiran", "Meera", "Aditya", "Pooja", "Sanjay", "Neha",
    "Rajesh", "Sunita", "Amit", "Deepa", "Carlos", "Maria", "James", "Emily",
    "Mohammed", "Sara", "Li", "Wei", "Yuki", "Chen", "Oliver", "Sophie",
    "Liam", "Emma", "Noah", "Olivia", "Ethan", "Ava", "Mason", "Isabella",
]

LAST_NAMES = [
    "Sharma", "Patel", "Kumar", "Singh", "Gupta", "Mehta", "Joshi", "Nair",
    "Reddy", "Iyer", "Verma", "Shah", "Rao", "Pillai", "Menon", "Bose",
    "Garcia", "Martinez", "Johnson", "Williams", "Brown", "Jones", "Davis",
    "Wilson", "Taylor", "Anderson", "Thomas", "Jackson", "White", "Harris",
    "Lee", "Wang", "Zhang", "Liu", "Chen", "Yang", "Kim", "Park", "Nguyen",
]

CITIES_CLEAN = [
    "Mumbai", "Delhi", "Bangalore", "Chennai", "Hyderabad", "Pune", "Kolkata",
    "Ahmedabad", "Jaipur", "Lucknow", "New York", "Los Angeles", "Chicago",
    "Houston", "Phoenix", "London", "Manchester", "Tokyo", "Osaka", "Sydney",
]

# Messy city variants (same cities, inconsistent casing/spacing)
CITIES_MESSY = CITIES_CLEAN + [
    "mumbai", "DELHI", "bangalore", "CHENNAI", "hyderabad", "  Pune",
    "kolkata ", " Ahmedabad ", "JAIPUR", "lucknow", "new york", "NEW YORK",
    "los angeles", "LOS ANGELES", "chicago ", " Chicago", "HOUSTON",
    "phoenix", "LONDON", "manchester", "TOKYO", "osaka ", " Sydney",
]


def random_name(messy: bool = False) -> str:
    """Return a full name, optionally with inconsistent casing."""
    first = random.choice(FIRST_NAMES)
    last = random.choice(LAST_NAMES)
    full = f"{first} {last}"
    if messy:
        variant = random.randint(0, 3)
        if variant == 0:
            return full.upper()
        elif variant == 1:
            return full.lower()
        elif variant == 2:
            return f"  {full}  "   # extra whitespace
    return full


def random_age(invalid: bool = False):
    """Return a realistic age, or an invalid/missing sentinel."""
    if invalid:
        return random.choice([-5, 0, 150, 999, "N/A", "unknown"])
    return random.randint(18, 75)


def random_sales(invalid: bool = False):
    """Return a realistic sales value, or an invalid/missing sentinel."""
    if invalid:
        return random.choice([-999, -1, "free", "N/A", "#REF!"])
    # log-normal to create realistic skew
    return round(np.random.lognormal(mean=6.5, sigma=1.2), 2)


# ── Build base records ────────────────────────────────────────────────────────
records = []
for i in range(1, 451):                     # 450 base records → ~500 after duplication
    messy = random.random() < 0.25          # 25 % of rows have dirty text
    invalid = random.random() < 0.08        # 8 % of rows have invalid values

    record = {
        "Customer ID": f"CUST-{i:04d}",
        "Name":        random_name(messy=messy),
        "Age":         random_age(invalid=invalid),
        "City":        random.choice(CITIES_MESSY if messy else CITIES_CLEAN),
        "Sales":       random_sales(invalid=invalid),
    }

    # Randomly null-out individual fields (5 % per field)
    for col in ["Name", "Age", "City", "Sales"]:
        if random.random() < 0.05:
            record[col] = np.nan

    records.append(record)

df = pd.DataFrame(records)

# ── Inject duplicates (≈50 extra rows = ~10 %) ───────────────────────────────
duplicate_indices = random.sample(range(len(df)), 50)
duplicates = df.iloc[duplicate_indices].copy()
df = pd.concat([df, duplicates], ignore_index=True)

# Shuffle so duplicates aren't all at the end
df = df.sample(frac=1, random_state=42).reset_index(drop=True)

# ── Save ──────────────────────────────────────────────────────────────────────
out_path = os.path.join(os.path.dirname(__file__), "raw_data.csv")
df.to_csv(out_path, index=False)
print(f"✅  raw_data.csv saved → {len(df)} rows  ({out_path})")
