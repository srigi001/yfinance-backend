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
        ticker = yf.Ticker(symbol)
        info = ticker.info

        if not info or 'shortName' not in info:
            return jsonify({'error': f'No profile data found for {symbol}'}), 404

        return jsonify({
            'symbol': symbol,
            'name': info.get('shortName'),
            'sector': info.get('sector'),
            'industry': info.get('industry'),
            'country': info.get('country'),
            'website': info.get('website'),
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3001)
