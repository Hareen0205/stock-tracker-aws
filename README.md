# 📈 Stock Watch: AI-Powered Serverless Stock Watch


## The System
I architected this end-to-end data pipeline to demonstrate cloud scalability and event-driven design.
* **Serverless Compute:** AWS Lambda (Python 3.12) automated via EventBridge.
* **NoSQL Storage:** Amazon DynamoDB time-series schema (Sydney Region).
* **AI Intelligence:** Integrated TextBlob NLP for real-time news sentiment analysis.
* **Automated Alerts:** AWS SNS configured for instant email notifications on price drops.

## Tech Stack
- **Cloud:** AWS (Lambda, DynamoDB, SNS, EventBridge)
- **Frontend:** Streamlit with Custom CSS 
- **Data:** Python, Pandas, Plotly, Yahoo Finance API

## Engineering Highlights
- **Performance:** Optimized DynamoDB reads by replacing `Scan` with `Query` operations.
- **Resilience:** Implemented custom User-Agent headers to bypass API rate-limiting.
- **Cost-Efficiency:** Entire architecture runs within the AWS Free Tier ($0.00/mo).
