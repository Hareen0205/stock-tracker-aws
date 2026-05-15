# 📈 Market Watch: AI-Powered Serverless Sentinel

A proactive, cloud-native monitoring system that bridges global market data (US Tech & Bursa Malaysia) with AI-driven sentiment analysis. 

## 🏗️ System Architecture
The system is built entirely on **AWS Serverless Architecture** to ensure scalability and cost-efficiency:
* **Data Ingestion:** Python-based **AWS Lambda** functions triggered by **EventBridge** every 15 minutes.
* **Intelligence:** **TextBlob NLP** integrated into the pipeline for real-time news sentiment analysis.
* **Storage:** **Amazon DynamoDB** (NoSQL) optimized for time-series financial data.
* **Alerting:** **AWS SNS** for instant email notifications based on custom price thresholds.
* **Hosting:** Publicly deployed **Streamlit** dashboard hosted on a **Linux EC2 (t3.micro)** instance.

## 🚀 Live Demo
Check out the live dashboard here: `http://54.252.165.148:8501` 
*(Note: Hosted on AWS Free Tier)*

## 🛠️ Tech Stack
* **Language:** Python 3.11
* **Cloud:** AWS (Lambda, DynamoDB, SNS, EventBridge, EC2)
* **Libraries:** Boto3, Pandas, Plotly, Streamlit, TextBlob
* **OS:** Ubuntu 24.04 LTS

## 🔧 Installation & Setup
1. Clone the repo: `git clone https://github.com/Hareen0205/stock-tracker-aws.git`
2. Install dependencies: `pip install -r requirements.txt`
3. Configure AWS CLI: `aws configure`
4. Run locally: `streamlit run src/app.py`
