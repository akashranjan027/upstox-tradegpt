from upstox_client import OrderApi, PortfolioApi
from upstox_client.rest import ApiException
from . import auth

class TradingAPI:
    def __init__(self, api_client):
        self.api = OrderApi(api_client)
        self.portfolio_api = PortfolioApi(api_client)

def place_buy_order(symbol, quantity, price=None, order_type="MARKET"):
    """Place a buy order for a given symbol with a given quantity"""
    api_client = auth.get_upstox_client()
    if not api_client:
        return {"error": "Authentication required"}

    trading_api = TradingAPI(api_client)

    try:
        # Create order request object
        order_request = {
            "instrument_token": symbol,
            "quantity": quantity,
            "product": "I",  # Intraday
            "validity": "DAY",
            "order_type": order_type,
            "transaction_type": "BUY",
            "disclosed_quantity": 0,
            "trigger_price": 0,
            "is_amo": False
        }

        # Add price only if it's a limit order
        if order_type == "LIMIT" and price is not None:
            order_request["price"] = price

        # Place order
        response = trading_api.api.place_order(order_request, api_version="2.0")
        return {
            "status": "success",
            "order_id": response.data.order_id,
            "message": f"Buy order placed for {quantity} shares of {symbol}"
        }

    except ApiException as e:
        return {"error": f"Exception when calling TradingApi: {e}"}

def place_sell_order(symbol, quantity, price=None, order_type="MARKET"):
    """Place a sell order for a given symbol"""
    api_client = auth.get_upstox_client()
    if not api_client:
        return {"error": "Authentication required"}

    trading_api = TradingAPI(api_client)

    try:
        # Create order request object
        order_request = {
            "instrument_token": symbol,
            "quantity": quantity,
            "product": "I",  # Intraday
            "validity": "DAY",
            "order_type": order_type,
            "transaction_type": "SELL",
            "disclosed_quantity": 0,
            "trigger_price": 0,
            "is_amo": False
        }

        # Add price only if it's a limit order
        if order_type == "LIMIT" and price is not None:
            order_request["price"] = price

        # Place order
        response = trading_api.api.place_order(order_request, api_version="2.0")
        return {
            "status": "success",
            "order_id": response.data.order_id,
            "message": f"Sell order placed for {quantity} shares of {symbol}"
        }

    except ApiException as e:
        return {"error": f"Exception when calling TradingApi: {e}"}

def get_portfolio():
    """Get current portfolio holdings"""
    api_client = auth.get_upstox_client()
    if not api_client:
        return {"error": "Authentication required"}

    trading_api = TradingAPI(api_client)

    try:
        response = trading_api.portfolio_api.get_holdings(api_version="2.0")
        holdings = []

        for holding in response.data:
            holdings.append({
                "tradingsymbol": holding.tradingsymbol,
                "quantity": holding.quantity,
                "average_price": holding.average_price,
                "last_price": holding.last_price,
                "pnl": holding.pnl,
                "exchange": holding.exchange
            })

        return holdings

    except ApiException as e:
        return {"error": f"Exception when calling PortfolioApi: {e}"} 