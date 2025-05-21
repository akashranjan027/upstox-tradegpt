from flask import Flask, request, jsonify
import pandas as pd
# Assuming your project structure allows this import path
# If src is a package, it might be: from . import market_data, auth
# Or if your PYTHONPATH is set up: import market_data, auth
try:
    from . import market_data
    from . import auth
except ImportError:
    # Fallback for direct execution if src is not treated as a package
    # and files are in the same directory or PYTHONPATH is configured.
    import market_data
    import auth


app = Flask(__name__)

@app.route('/mcp/market/get_historical_data', methods=['GET'])
def get_historical_data_mcp():
    symbol = request.args.get('symbol')
    timeframe = request.args.get('timeframe', '1d')
    try:
        days = int(request.args.get('days', 30))
    except ValueError:
        return jsonify({"error": "Invalid 'days' parameter. Must be an integer."}), 400

    if not symbol:
        return jsonify({"error": "Missing 'symbol' parameter"}), 400

    # Ensure Upstox client is available via auth module
    # This part is crucial and assumes auth.get_upstox_client() works in this context
    # and that the underlying functions in market_data use it.
    
    data = market_data.get_market_data(symbol=symbol, timeframe=timeframe, days=days)

    if isinstance(data, pd.DataFrame):
        return jsonify(data.to_dict(orient='records'))
    elif isinstance(data, dict) and "error" in data:
        return jsonify(data), 500 # Or an appropriate error code based on error type
    else:
        return jsonify({"error": "Unexpected data format received"}), 500

@app.route('/mcp/market/get_current_price', methods=['GET'])
def get_current_price_mcp():
    symbol = request.args.get('symbol')

    if not symbol:
        return jsonify({"error": "Missing 'symbol' parameter"}), 400

    price_data = market_data.get_current_price(symbol=symbol)

    if isinstance(price_data, dict) and "error" in price_data:
        return jsonify(price_data), 500 # Or an appropriate error code
    elif isinstance(price_data, (float, int)):
        return jsonify({"last_price": price_data})
    else:
        # Handle cases where price_data might be an unexpected type
        return jsonify({"error": "Unexpected data format for price"}), 500

if __name__ == '__main__':
    # Note: This requires config/config.json to be accessible relative to where this script is run from,
    # or auth.py needs to be robust enough to find it.
    # For development, you might run this script from the root of the project.
    app.run(debug=True, port=5001)
