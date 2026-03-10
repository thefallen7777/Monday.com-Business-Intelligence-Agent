# Monday.com Business Intelligence Agent

An AI-powered Business Intelligence agent that answers founder-level questions by dynamically querying data from **monday.com boards** containing sales pipeline and operational work order information.

The agent interprets natural language questions, retrieves live data from monday.com, cleans inconsistent business data, computes key metrics, and returns executive-level insights.

Built by **Mahadev Manoj (6BTAIML)** for the **Skylark Drones Technical Assessment**.

---

# Overview

Founders often ask questions like:

- *How is our pipeline looking this quarter?*
- *What sectors are performing best?*
- *Which work orders have billing risk?*
- *How much receivable is pending?*

Answering these normally requires:

- pulling data manually
- cleaning messy spreadsheets
- joining multiple sources
- generating ad-hoc analysis

This project automates that process using an **AI agent integrated with monday.com**.

---

# Core Features

### Monday.com Integration
The agent connects to monday.com using the **monday GraphQL API** and retrieves data dynamically from boards.

Data is never hardcoded into the application.

---

### Data Resilience

Real-world business data is messy. The system handles:

- missing values
- inconsistent formats
- text-based numeric fields
- irregular sector naming
- incomplete records

The pipeline normalizes this data before analysis.

---

### Query Understanding

User questions are interpreted using an LLM-based query router that extracts:

- business intent
- sector filters
- timeframe
- metrics requested


---

### Business Intelligence Metrics

The agent calculates metrics such as:

- Open pipeline value
- Weighted pipeline
- Deal stage distribution
- Sector performance
- Work order execution status
- Billing risk
- Receivable totals

The system combines **Deals and Work Orders boards** to provide full business context.

---

### Executive-Level Answers

Instead of returning raw numbers, the system generates structured responses including:

- direct answers
- supporting insights
- sector breakdowns
- operational risks
- data quality caveats

---

## Monday.com Setup Instructions

Before running the agent, the monday.com environment must be configured with two boards that contain the provided datasets.

### Step 1: Create Boards

Create two boards in your monday.com workspace with the following names:

- **Deals**
- **Work Orders**

The agent dynamically queries these boards using the monday API.

---

### Step 2: Import the Datasets

Import the provided CSV files into the boards:

| Board Name | CSV File |
|-------------|-------------|
| Deals | Deal_funnel_Data.csv |
| Work Orders | Work_Order_Tracker_Data.csv |

This can be done in monday by selecting:
Board Menu → Import → CSV


---

### Step 3: Column Configuration

When importing the CSV files, monday will request column types.  
Suggested column types are:

#### Deals Board

| Column | Type |
|------|------|
Deal Name | Item Name
Deal Status | Status
Deal Stage | Status
Closure Probability | Numbers
Masked Deal Value | Numbers
Tentative Close Date | Date
Close Date (A) | Date
Sector/service | Dropdown
Created Date | Date

#### Work Orders Board

| Column | Type |
|------|------|
Deal Name Masked | Item Name
Execution Status | Status
Billing Status | Status
Collection Status | Status
Probable Start Date | Date
Probable End Date | Date
Amount Columns | Numbers
Receivable Amount | Numbers
Sector | Dropdown

The agent includes normalization logic to handle inconsistencies in column types if needed.

---

### Step 4: Obtain Monday API Token

To allow the agent to access board data:

1. Open monday.com
2. Click your **profile icon**
3. Go to **Developers**
4. Open **API Tokens**
5. Copy your personal API token

---

### Step 5: Configure Environment Variables

Create a `.env` file in the project root with the following variables:
MONDAY_API_TOKEN=your_monday_api_token
DEALS_BOARD_NAME=Deals
WORK_ORDERS_BOARD_NAME=Work Orders


The agent will use these values to dynamically retrieve data from monday.com.

---

### Step 6: Verify Setup

After configuration, ensure that:

- Both boards exist
- Data rows are visible in monday
- The API token has access to the workspace

Once completed, the agent will be able to query the boards dynamically and generate business insights.




# Architecture
User Question
↓
FastAPI Backend
↓
Query Router (LLM)
↓
Monday API Data Retrieval
↓
Data Normalization (pandas)
↓
Metric Computation
↓
Answer Generation
↓
Frontend Chat Interface


---

# Technology Stack

Backend
- FastAPI
- Python
- Pandas

AI Layer
- LLM for query routing and answer synthesis

Integration
- monday.com GraphQL API

Frontend
- Lightweight HTML + JavaScript chat interface

Deployment
- Render

---

# Project Structure
monday-bi-agent
│
├── app
│ ├── main.py
│ ├── config.py
│ ├── models.py
│ ├── prompts.py
│ │
│ ├── services
│ │ ├── monday_client.py
│ │ ├── normalizer.py
│ │ ├── metrics.py
│ │ ├── query_router.py
│ │ └── answer_writer.py
│ │
│ └── static
│ └── index.html
│
├── requirements.txt
├── render.yaml
└── README.md


---

# Monday Board Setup

Two boards must exist in monday.com.

### Deals Board

Contains pipeline information such as:

- Deal Name
- Deal Status
- Closure Probability
- Deal Value
- Tentative Close Date
- Sector
- Deal Stage

---

### Work Orders Board

Contains operational and billing information such as:

- Execution Status
- Billing Status
- Collection Status
- Receivable Amount
- Work Order Sector
- Delivery Dates

---

# Environment Configuration

Create a `.env` file in the project root.

Example:
LLM_API_KEY=your_llm_key
LLM_BASE_URL=provider_endpoint
LLM_MODEL=model_name

MONDAY_API_TOKEN=your_monday_token
MONDAY_API_URL=https://api.monday.com/v2

DEALS_BOARD_NAME=Deals
WORK_ORDERS_BOARD_NAME=Work Orders


---

# Running the Agent Locally

Activate the virtual environment:


.venv\Scripts\activate

Start the server:

uvicorn app.main:app --reload --port 8000

Open the interface:


http://127.0.0.1:8000


---

# Example Queries

Users can ask questions such as:
How is our pipeline looking this quarter?
How is our pipeline looking for energy sector this quarter?
Which work orders have billing risk?
What is the weighted pipeline by sector?
Prepare a leadership update for this quarter.


---

# Leadership Updates Feature

The agent can generate concise leadership summaries based on live monday data.

Example output includes:

- pipeline snapshot
- operational performance
- sector highlights
- billing risks
- receivables overview

This enables quick preparation of executive updates.

---

# Error Handling

The system gracefully handles:

- missing sector labels
- incomplete deal values
- API failures
- empty datasets
- inconsistent data types

Warnings are included in responses when data quality may affect insights.

---

# Deployment

The application can be deployed using **Render**.

Steps:

1. Push the repository to GitHub
2. Create a new Web Service on Render
3. Connect the repository
4. Configure environment variables
5. Deploy

Render will automatically run:
uvicorn app.main:app


---



# Future Improvements

If more time were available, the following enhancements would be implemented:

- automatic board discovery
- sector synonym learning
- caching for large boards
- chart-based visualizations
- Slack / Teams integration
- scheduled leadership reports

---

# Author

**Mahadev Manoj**  
B.Tech Artificial Intelligence & Machine Learning  
Section: 6BTAIML  Reg: 2363040
Christ University, Kengeri Campus, Bangalore

Developed for the **Skylark Drones Technical Assessment**.