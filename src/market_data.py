import upstox_client
from upstox_client.rest import ApiException
import pandas as pd
import datetime
from . import auth
import traceback

def get_market_data(symbol, timeframe='1d', days=30):
    """Get historical market data for a given symbol"""
    api_client = auth.get_upstox_client()
    if not api_client:
        return {"error": "Authentication required"}
    api_version='2.0'
    market_api = upstox_client.MarketQuoteApi(api_client)

    try:
        # Calculate date range
        end_date = datetime.datetime.now()
        start_date = end_date - datetime.timedelta(days=days)

        # Format dates as required by Upstox API
        from_date = start_date.strftime("%Y-%m-%d")
        to_date = end_date.strftime("%Y-%m-%d")

        # Get historical data
        response = market_api.get_market_quote_ohlc(symbol,timeframe,api_version)
            

        if not response or not hasattr(response, 'data') or not hasattr(response.data, 'candles'):
            return {"error": "Invalid response format from API"}

        # Convert to pandas DataFrame for easier analysis
        data = []
        for candle in response.data.candles:
            if len(candle) >= 6:  # Validate candle data structure
                data.append({
                    'timestamp': candle[0],
                    'open': candle[1],
                    'high': candle[2],
                    'low': candle[3],
                    'close': candle[4],
                    'volume': candle[5]
                })

        return pd.DataFrame(data)

    except ApiException as e:
        return {"error": f"Exception when calling MarketData API: {e}"}
    except Exception as e:
        return {"error": f"Unexpected error: {str(e)}"}

def get_current_price(symbol):
    """Get current market price for a given symbol"""
    api_client = auth.get_upstox_client()
    if not api_client:
        return {"error": "Authentication required"}

    market_api = upstox_client.MarketQuoteApi(api_client)
    api_version = '2.0'
    print(f"Fetching LTP for symbol: {symbol} using API version: {api_version}")

    try:
        response = market_api.ltp(symbol, api_version)
        print(f"API Response: {response}")  # Debug print

        # Convert response to dictionary if needed
        if hasattr(response, 'to_dict'):
            response_dict = response.to_dict()
        else:
            response_dict = response

        # Extract data safely
        if 'data' not in response_dict:
            return {"error": "No data found in response"}

        data = response_dict['data']
        if not data:
            return {"error": "Empty data in response"}

        # Get instrument info
        instrument_key = list(data.keys())[0]
        instrument_data = data[instrument_key]

        if 'last_price' not in instrument_data:
            return {"error": "Last price not found in response"}

        last_price = instrument_data['last_price']
        print(f"Last price for {symbol}: {last_price}")  # Debug print
        return last_price

    except ApiException as e:
        return {"error": f"Exception when calling MarketQuoteApi: {e}"}
    except Exception as e:
        return {"error": f"Unexpected error: {str(e)}"}

        