from flask import Flask, request, jsonify
import yfinance as yf
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

def get_currency_multiplier(ticker_info):
    """
    Returns 0.01 if the currency is GBp (Pence), otherwise returns 1.0.
    """
    # Check both info and fast_info for currency
    currency = ticker_info.get('currency', 'USD')
    if currency == 'GBp':
        return 0.01
    return 1.0

@app.route('/api/price-history')
def price_history():
    symbol = request.args.get('symbol')
    period = request.args.get('period', '5y')
    interval = request.args.get('interval', '1d')

    if not symbol:
        return jsonify({'error': 'Missing symbol'}), 400

    try:
        ticker = yf.Ticker(symbol)
        data = ticker.history(period=period, interval=interval)

        if data.empty:
            return jsonify({'error': f'No data for symbol: {symbol}'}), 404

        # Get multiplier based on currency
        multiplier = get_currency_multiplier(ticker.info)
        
        # Apply multiplier to all prices
        prices = (data['Close'].dropna() * multiplier).tolist()
        
        return jsonify({'symbol': symbol, 'prices': prices, 'currency_adjusted': multiplier != 1.0})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/latest-price')
def latest_price():
    symbol = request.args.get('symbol')

    if not symbol:
        return jsonify({'error': 'Missing symbol'}), 400

    try:
        ticker = yf.Ticker(symbol)
        multiplier = get_currency_multiplier(ticker.info)
        
        # Try fast_info first
        price = ticker.fast_info.get('last_price')

        if price is None:
            hist = ticker.history(period="1d", interval="1m")
            if not hist.empty:
                price = hist['Close'].dropna().iloc[-1]
            else:
                return jsonify({'error': f'No recent price data for {symbol}'}), 404

        return jsonify({
            'symbol': symbol,
            'price': float(price * multiplier)
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

# (Profile route remains unchanged as it doesn't handle prices)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3001)
