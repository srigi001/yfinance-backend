from flask import Flask, request, jsonify
import yfinance as yf
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

        if data.empty:
            return jsonify({'error': f'No data for symbol: {symbol}'}), 404

        close_prices = data['Close']
        if close_prices is None or close_prices.empty:
            return jsonify({'error': f'No close price data for symbol: {symbol}'}), 404

        prices = close_prices.dropna().to_list()
        return jsonify({'symbol': symbol, 'prices': prices})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3001)
