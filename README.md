# Data Cleaning & Reporting Automation

## Overview

This project was developed as part of my Data Science Internship at Thiranex.

The goal of this project is to automate data cleaning and reporting workflows using Python and Streamlit. The system processes raw datasets, removes data quality issues, generates cleaned datasets, and creates analytical reports for better decision-making.

---

## Features

* Automated Data Cleaning
* Missing Value Detection and Handling
* Duplicate Record Removal
* Data Standardization
* Data Quality Analysis
* Automated Report Generation
* Interactive Dashboard
* Cleaned Dataset Download Option

---

## Project Workflow

Raw Data → Data Cleaning → Report Generation → Dashboard Visualization

The project automatically:

1. Reads raw data from `raw_data.csv`
2. Cleans the dataset using `cleaner.py`
3. Generates `cleaned_data.csv`
4. Creates summary reports in `report.csv`
5. Displays results through an interactive Streamlit dashboard

---

## Files Included

* `app.py` – Streamlit Dashboard
* `raw_data.csv` – Original Dataset
* `cleaned_data.csv` – Cleaned Dataset
* `report.csv` – Generated Data Quality Report
* `generate_data.py` – Sample Dataset Generator
* `cleaner.py` – Data Cleaning Script

---

## Technologies Used

* Python
* Pandas
* NumPy
* Plotly
* Streamlit

---

## Dashboard Features

### KPIs

* Total Records
* Duplicates Removed
* Missing Values Fixed
* Final Clean Records

### Visualizations

* Missing Values Analysis
* Data Quality Report
* Purchase Amount Distribution
* City-wise Analysis

---

## How to Run

Install dependencies:

```bash
pip install -r requirements.txt
```

Run the dashboard:

```bash
streamlit run app.py
```

---

## Learning Outcomes

Through this project, I gained practical experience in:

* Data Cleaning Techniques
* Data Preprocessing
* Data Quality Management
* Reporting Automation
* Dashboard Development
* Business Data Analysis

---

## Author

Keerthanadharshini K
