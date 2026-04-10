import json
import boto3
import yfinance as yf
from datetime import datetime
from decimal import Decimal

# Initialize DynamoDB
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('StockPrices')

def lambda_handler(event, context):
    symbol = event.get('ticker', 'NVDA') # Default to NVIDIA
    
    try:
        # Fetch Stock Data
        ticker = yf.Ticker(symbol)
        data = ticker.history(period="1d")
        latest_price = data['Close'].iloc[-1]
        
        # DynamoDB doesn't like floats, so convert to Decimal
        formatted_price = Decimal(str(round(latest_price, 2)))
        timestamp = datetime.now().isoformat()
        
        # Save to Database
        table.put_item(
            Item={
                'ticker': symbol,
                'timestamp': timestamp,
                'price': formatted_price
            }
        )
        
        return {
            'statusCode': 200,
            'body': json.dumps(f"Stored {symbol} price: ${formatted_price}")
        }
    except Exception as e:
        return {'statusCode': 500, 'body': json.dumps(str(e))}