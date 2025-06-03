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


@app.route('/api/latest-price')
def latest_price():
    symbol = request.args.get('symbol')

    if not symbol:
        return jsonify({'error': 'Missing symbol'}), 400

    try:
        ticker = yf.Ticker(symbol)
        fast_info = ticker.fast_info
        price = fast_info.get('last_price')

        # Fallback to history if price is not available
        if price is None:
            hist = ticker.history(period="1d", interval="1m")
            if not hist.empty:
                price = hist['Close'].dropna()[-1]
            else:
                return jsonify({'error': f'No recent price data for {symbol}'}), 404

        # Try to detect correct currency
        currency = (
            fast_info.get("currency")
            or ticker.info.get("currency")
            or "USD"
        )

        # Convert to USD if needed using Frankfurter
        if currency != "USD":
            try:
                fx_url = f"https://api.frankfurter.app/latest?from={currency}&to=USD"
                fx_response = requests.get(fx_url)
                fx_data = fx_response.json()
                fx_rate = fx_data.get("rates", {}).get("USD")

                if fx_rate:
                    converted_price = price * fx_rate
                else:
                    converted_price = None
            except Exception as fx_err:
                fx_rate = None
                converted_price = None
        else:
            fx_rate = 1.0
            converted_price = price

        return jsonify({
            'symbol': symbol,
            'raw_price': round(price, 4),
            'currency': currency,
            'fx_rate': round(fx_rate, 6) if fx_rate else None,
            'converted_price_usd': round(converted_price, 4) if converted_price else None
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3001)
