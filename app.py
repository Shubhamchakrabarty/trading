from flask import Flask, jsonify, request
from flask_cors import CORS
import yfinance as yf
import pandas as pd

app = Flask(__name__)
CORS(app)  # Allow WordPress to access this API

# Full Nifty 50 Tickers (Yahoo Finance format uses .NS)
NIFTY_50_TICKERS = [
    "ADANIENT.NS", "ADANIPORTS.NS", "APOLLOHOSP.NS", "ASIANPAINT.NS", "AXISBANK.NS",
    "BAJAJ-AUTO.NS", "BAJFINANCE.NS", "BAJAJFINSV.NS", "BPCL.NS", "BHARTIARTL.NS",
    "BRITANNIA.NS", "CIPLA.NS", "COALINDIA.NS", "DIVISLAB.NS", "DRREDDY.NS",
    "EICHERMOT.NS", "GRASIM.NS", "HCLTECH.NS", "HDFCBANK.NS", "HDFCLIFE.NS",
    "HEROMOTOCO.NS", "HINDALCO.NS", "HINDUNILVR.NS", "ICICIBANK.NS", "ITC.NS",
    "INDUSINDBK.NS", "INFY.NS", "JSWSTEEL.NS", "KOTAKBANK.NS", "LTIM.NS",
    "LT.NS", "M&M.NS", "MARUTI.NS", "NESTLEIND.NS", "NTPC.NS",
    "ONGC.NS", "POWERGRID.NS", "RELIANCE.NS", "SBILIFE.NS", "SBIN.NS",
    "SUNPHARMA.NS", "TCS.NS", "TATACONSUM.NS", "TATAMOTORS.NS", "TATASTEEL.NS",
    "TECHM.NS", "TITAN.NS", "ULTRACEMCO.NS", "UPL.NS", "WIPRO.NS"
]

@app.route('/nifty50', methods=['GET'])
def get_nifty50():
    try:
        # Bulk download for speed
        # using period='1d' to get the latest close (CMP)
        data = yf.download(NIFTY_50_TICKERS, period="1d", group_by='ticker', threads=True)
        
        result = []
        for ticker in NIFTY_50_TICKERS:
            try:
                # Extract Single Day Data
                ticker_data = data[ticker]
                if not ticker_data.empty:
                    # Get the last available row
                    last_quote = ticker_data.iloc[-1]
                    cmp = round(last_quote['Close'], 2)
                    
                    result.append({
                        "symbol": ticker,
                        "cmp": cmp
                    })
            except Exception as e:
                continue # Skip if data missing for specific ticker
                
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/history', methods=['GET'])
def get_history():
    symbol = request.args.get('symbol')
    if not symbol:
        return jsonify({"error": "No symbol provided"}), 400
        
    try:
        # Fetch last 5 days
        stock = yf.Ticker(symbol)
        hist = stock.history(period="5d")
        
        data = []
        for date, row in hist.iterrows():
            data.append({
                "date": date.strftime('%Y-%m-%d'),
                "open": round(row['Open'], 2),
                "high": round(row['High'], 2),
                "low": round(row['Low'], 2),
                "close": round(row['Close'], 2)
            })
            
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
