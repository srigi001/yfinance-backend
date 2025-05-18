from flask import Flask, request, jsonify
import yfinance as yf
import requests
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/api/price-history')
def price_history():
    symbol = request.args.get('symbol')
    period = request.args.get('period', '5y')
    interval = request.args.get('interval', '1d')

    if not symbol:
        return jsonify({'error': 'Missing symbol'}), 400

    try:
        data = yf.download(symbol, period=period, interval=interval)

        if data.empty or 'Close' not in data:
            return jsonify({'error': f'No data for symbol: {symbol}'}), 404

        prices = data['Close'].dropna().values.tolist()
        return jsonify({'symbol': symbol, 'prices': prices})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/profile')
def profile():
    symbol = request.args.get('symbol')
    if not symbol:
        return jsonify({'error': 'Missing symbol'}), 400

    try:
        url = f"https://query1.finance.yahoo.com/v10/finance/quoteSummary/{symbol}?modules=assetProfile"
        headers = {
            "User-Agent": "Mozilla/5.0"
        }
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()

        result = data.get("quoteSummary", {}).get("result")
        if result:
            profile = result[0].get("assetProfile", {})
            return jsonify(profile)
        else:
            return jsonify({'error': 'Profile not found'}), 404

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3001)
