from flask import Flask, request, jsonify
# Assuming your project structure allows this import path
try:
    from . import trading
    from . import auth
    from . import market_data # Needed if place_buy_order calls get_current_price internally
except ImportError:
    # Fallback for direct execution
    import trading
    import auth
    import market_data

app = Flask(__name__)

@app.route('/mcp/trading/place_buy_order', methods=['POST'])
def place_buy_order_mcp():
    req_data = request.get_json()
    if not req_data:
        return jsonify({"error": "Missing JSON request body"}), 400

    symbol = req_data.get('symbol')
    quantity = req_data.get('quantity')
    order_type = req_data.get('order_type', 'MARKET')
    price = req_data.get('price') # Can be None

    if not symbol or quantity is None: # quantity can be 0, but not None
        return jsonify({"error": "Missing 'symbol' or 'quantity' in request body"}), 400
    
    try:
        quantity = int(quantity)
        if quantity <= 0:
             return jsonify({"error": "'quantity' must be a positive integer"}), 400
    except ValueError:
        return jsonify({"error": "'quantity' must be an integer"}), 400

    if order_type == "LIMIT" and price is None:
        # Option 1: Fetch price here (makes MCP tool more convenient but adds a network call)
        # current_price_data = market_data.get_current_price(symbol)
        # if isinstance(current_price_data, dict) and "error" in current_price_data:
        #     return jsonify({"error": f"Failed to fetch price for LIMIT order: {current_price_data['error']}"}), 500
        # price = current_price_data 
        # Option 2: Require price for LIMIT orders (simpler MCP tool contract)
        return jsonify({"error": "Missing 'price' for LIMIT order"}), 400
    
    if price is not None:
        try:
            price = float(price)
        except ValueError:
            return jsonify({"error": "'price' must be a valid number"}), 400


    result = trading.place_buy_order(
        symbol=symbol, 
        quantity=quantity, 
        order_type=order_type, 
        price=price
    )

    if isinstance(result, dict) and "error" in result:
        return jsonify(result), 500 # Or an appropriate error code
    else:
        return jsonify(result)

@app.route('/mcp/trading/place_sell_order', methods=['POST'])
def place_sell_order_mcp():
    req_data = request.get_json()
    if not req_data:
        return jsonify({"error": "Missing JSON request body"}), 400

    symbol = req_data.get('symbol')
    quantity = req_data.get('quantity')
    order_type = req_data.get('order_type', 'MARKET')
    price = req_data.get('price') # Can be None

    if not symbol or quantity is None:
        return jsonify({"error": "Missing 'symbol' or 'quantity' in request body"}), 400

    try:
        quantity = int(quantity)
        if quantity <= 0:
             return jsonify({"error": "'quantity' must be a positive integer"}), 400
    except ValueError:
        return jsonify({"error": "'quantity' must be an integer"}), 400

    if order_type == "LIMIT" and price is None:
         return jsonify({"error": "Missing 'price' for LIMIT order"}), 400
    
    if price is not None:
        try:
            price = float(price)
        except ValueError:
            return jsonify({"error": "'price' must be a valid number"}), 400

    result = trading.place_sell_order(
        symbol=symbol, 
        quantity=quantity, 
        order_type=order_type, 
        price=price
    )

    if isinstance(result, dict) and "error" in result:
        return jsonify(result), 500 # Or an appropriate error code
    else:
        return jsonify(result)

@app.route('/mcp/trading/get_portfolio', methods=['GET'])
def get_portfolio_mcp():
    result = trading.get_portfolio()

    if isinstance(result, dict) and "error" in result:
        return jsonify(result), 500 # Or an appropriate error code
    else:
        return jsonify(result)

if __name__ == '__main__':
    # Ensure config/config.json is accessible
    app.run(debug=True, port=5002)
