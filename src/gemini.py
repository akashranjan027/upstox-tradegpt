# src/gemini.py
import google.genai as genai
# Explicitly import necessary types
from google.genai.types import (
    Tool, FunctionDeclaration, FunctionResponse, Part,
    GenerateContentConfig, Content # Added Content for history management
)
import json
import os
import csv
import requests
# The direct imports below might still be used by other functions or for other purposes.
# For the wrapped functions, we'll be using requests to call MCP servers.
from . import market_data, trading # Assuming these modules exist

# --- Function Definitions for Gemini ---

def get_market_data_wrapper(symbol: str, days: int = 30, **kwargs):
    """
    Retrieves historical market data for a given NSE stock symbol via MCP server.
    Input:
       - symbol: NSE stock symbol (format: NSE_EQ|<isin_code>)
       - days: Number of days of historical data (default 30)
       - kwargs: Can include 'timeframe'
    Returns: Historical market data for analysis.
    """
    timeframe = kwargs.get("timeframe", "1d")
    print(f"--- Calling MCP: get_market_data(symbol={symbol}, days={days}, timeframe={timeframe}) ---")
    payload = {"symbol": symbol, "days": days, "timeframe": timeframe}
    try:
        response = requests.get(
            "http://localhost:5001/mcp/market/get_historical_data",
            params=payload,
            timeout=15
        )
        response.raise_for_status()  # Raises HTTPError for 4xx/5xx responses
        return response.json()
    except requests.exceptions.HTTPError as http_err:
        error_msg = f"HTTP error calling MCP get_market_data: {http_err} - Response: {http_err.response.text if http_err.response else 'No response'}"
        print(error_msg)
        return {"error": error_msg}
    except requests.exceptions.RequestException as req_err: # Catches network errors, timeouts, etc.
        error_msg = f"Request error calling MCP get_market_data: {str(req_err)}"
        print(error_msg)
        return {"error": error_msg}
    except json.JSONDecodeError:
        error_msg = "Invalid JSON response from MCP get_market_data"
        print(error_msg)
        return {"error": error_msg}

def place_buy_order_wrapper(symbol: str, quantity: int, **kwargs):
    """
    Places a buy order for a specified quantity of an NSE stock via MCP server.
    Input:
       - symbol: NSE stock symbol (format: NSE_EQ|<isin_code>)
       - quantity: Number of shares to buy
       - kwargs: Can include 'order_type' and 'price'
    Returns: Order confirmation details.
    """
    order_type = kwargs.get("order_type", "MARKET")
    price = kwargs.get("price")
    print(f"--- Calling MCP: place_buy_order(symbol={symbol}, quantity={quantity}, order_type={order_type}, price={price}) ---")
    payload = {
        "symbol": symbol,
        "quantity": quantity,
        "order_type": order_type,
        "price": price
    }
    try:
        response = requests.post(
            "http://localhost:5002/mcp/trading/place_buy_order",
            headers={'Content-Type': 'application/json'},
            data=json.dumps(payload),
            timeout=15
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as http_err:
        error_msg = f"HTTP error calling MCP place_buy_order: {http_err} - Response: {http_err.response.text if http_err.response else 'No response'}"
        print(error_msg)
        return {"error": error_msg}
    except requests.exceptions.RequestException as req_err:
        error_msg = f"Request error calling MCP place_buy_order: {str(req_err)}"
        print(error_msg)
        return {"error": error_msg}
    except json.JSONDecodeError:
        error_msg = "Invalid JSON response from MCP place_buy_order"
        print(error_msg)
        return {"error": error_msg}

def place_sell_order_wrapper(symbol: str, quantity: int, **kwargs):
    """
    Places a sell order for a specified quantity of an NSE stock via MCP server.
    Input:
       - symbol: NSE stock symbol (format: NSE_EQ|<isin_code>)
       - quantity: Number of shares to sell
       - kwargs: Can include 'order_type' and 'price'
    Returns: Order confirmation details.
    """
    order_type = kwargs.get("order_type", "MARKET")
    price = kwargs.get("price")
    print(f"--- Calling MCP: place_sell_order(symbol={symbol}, quantity={quantity}, order_type={order_type}, price={price}) ---")
    payload = {
        "symbol": symbol,
        "quantity": quantity,
        "order_type": order_type,
        "price": price
    }
    try:
        response = requests.post(
            "http://localhost:5002/mcp/trading/place_sell_order",
            headers={'Content-Type': 'application/json'},
            data=json.dumps(payload),
            timeout=15
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as http_err:
        error_msg = f"HTTP error calling MCP place_sell_order: {http_err} - Response: {http_err.response.text if http_err.response else 'No response'}"
        print(error_msg)
        return {"error": error_msg}
    except requests.exceptions.RequestException as req_err:
        error_msg = f"Request error calling MCP place_sell_order: {str(req_err)}"
        print(error_msg)
        return {"error": error_msg}
    except json.JSONDecodeError:
        error_msg = "Invalid JSON response from MCP place_sell_order"
        print(error_msg)
        return {"error": error_msg}

def get_portfolio_wrapper(**kwargs): # Added **kwargs for consistency, though not used by MCP
    """
    Retrieves the current user's portfolio holdings via MCP server.
    Returns: Current portfolio holdings.
    """
    print("--- Calling MCP: get_portfolio() ---")
    try:
        response = requests.get(
            "http://localhost:5002/mcp/trading/get_portfolio",
            timeout=15
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as http_err:
        error_msg = f"HTTP error calling MCP get_portfolio: {http_err} - Response: {http_err.response.text if http_err.response else 'No response'}"
        print(error_msg)
        return {"error": error_msg}
    except requests.exceptions.RequestException as req_err:
        error_msg = f"Request error calling MCP get_portfolio: {str(req_err)}"
        print(error_msg)
        return {"error": error_msg}
    except json.JSONDecodeError:
        error_msg = "Invalid JSON response from MCP get_portfolio"
        print(error_msg)
        return {"error": error_msg}

def get_current_price_wrapper(symbol: str, **kwargs): # Added **kwargs for consistency
    """
    Retrieves the current market price for a given NSE stock symbol via MCP server.
    Input:
       - symbol: NSE stock symbol (format: NSE_EQ|<isin_code>)
    Returns: Current market price.
    """
    print(f"--- Calling MCP: get_current_price(symbol={symbol}) ---")
    payload = {"symbol": symbol}
    try:
        response = requests.get(
            "http://localhost:5001/mcp/market/get_current_price",
            params=payload,
            timeout=15
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as http_err:
        error_msg = f"HTTP error calling MCP get_current_price: {http_err} - Response: {http_err.response.text if http_err.response else 'No response'}"
        print(error_msg)
        return {"error": error_msg}
    except requests.exceptions.RequestException as req_err:
        error_msg = f"Request error calling MCP get_current_price: {str(req_err)}"
        print(error_msg)
        return {"error": error_msg}
    except json.JSONDecodeError:
        error_msg = "Invalid JSON response from MCP get_current_price"
        print(error_msg)
        return {"error": error_msg}


def get_isin_for_symbol_wrapper(stock_symbol: str, exchange: str = None):
    """
    Retrieves the ISIN for a given stock symbol using the FMP API.

    Args:
        stock_symbol: The stock ticker symbol (e.g., 'AAPL').
        exchange: Optional specific stock exchange (e.g., 'NASDAQ').

    Returns:
        A dictionary containing the ISIN if found, or an error message.
        Example success: {"isin": "US0378331005"}
        Example not found: {"error": "ISIN not found for symbol AAPL on NASDAQ"}
        Example API error: {"error": "API request failed: [reason]"}
    """
    FMP_API_KEY = os.environ.get("FMP_API_KEY", "2m4oRMEn5iRCIHabFCuOp4JdPshLqyGO")
    BASE_URL = "https://financialmodelingprep.com/api"
    SEARCH_ENDPOINT = "/v3/search"
    if not FMP_API_KEY or FMP_API_KEY == "YOUR_DEFAULT_API_KEY_FOR_TESTING":
         return {"error": "FMP API key not configured on the backend."}

    api_url = f"{BASE_URL}{SEARCH_ENDPOINT}"
    params = {
        'query': stock_symbol,
        'limit': 5, # Limit results to avoid excessive data
        'apikey': FMP_API_KEY
    }
    if exchange:
        params['exchange'] = exchange

    print(f"--- Executing Tool: get_isin_for_symbol ---")
    print(f"   Symbol: {stock_symbol}, Exchange: {exchange}")

    try:
        response = requests.get(api_url, params=params)
        response.raise_for_status() # Raise HTTPError for bad responses (4xx or 5xx)
        data = response.json()

        if not data:
            not_found_msg = f"No results found for symbol '{stock_symbol}'"
            if exchange:
                not_found_msg += f" on exchange '{exchange}'"
            print(f"   Result: {not_found_msg}")
            return {"error": not_found_msg}

        # Find the exact match if possible, preferring the specified exchange
        found_isin = None
        for security in data:
            if security.get('symbol') == stock_symbol and security.get('isin'):
                 # If exchange was specified, prioritize match on that exchange
                if exchange and security.get('exchangeShortName') == exchange:
                    found_isin = security['isin']
                    break 
                elif not exchange:
                    found_isin = security['isin']
                    break


        if found_isin:
            print(f"   Result: Found ISIN {found_isin}")
            return {"isin": found_isin}
        else:
            not_found_msg = f"ISIN not found within results for exact symbol '{stock_symbol}'"
            if exchange:
                 not_found_msg += f" on exchange '{exchange}'"
            print(f"   Result: {not_found_msg}")
            return {"error": not_found_msg}

    except requests.exceptions.HTTPError as http_err:
        error_msg = f"API request failed: {http_err}"
        print(f"   Error: {error_msg}")
        return {"error": error_msg}
    except requests.exceptions.RequestException as req_err:
        error_msg = f"API connection error: {req_err}"
        print(f"   Error: {error_msg}")
        return {"error": error_msg}
    except ValueError as json_err: # Includes JSONDecodeError
        error_msg = f"Failed to parse API response: {json_err}"
        print(f"   Error: {error_msg}")
        return {"error": error_msg}
    except Exception as e:
        error_msg = f"An unexpected error occurred: {e}"
        print(f"   Error: {error_msg}")
        return {"error": error_msg}
    
def get_isin_from_csv_wrapper(symbol: str):
    """
    Retrieves the ISIN code for a given NSE stock symbol from the local CSV file.
    """
    csv_path = os.path.join(os.path.dirname(__file__), '..', 'NSE-cm03MAY2021bhav.csv')
    
    print(f"--- Executing Tool: get_isin_from_csv ---")
    print(f"   Symbol: {symbol}")
    
    try:
        # Check if file exists
        if not os.path.exists(csv_path):
            error_msg = f"CSV file not found at {csv_path}"
            print(f"   Error: {error_msg}")
            return {"error": error_msg}
        
        # Read the CSV file
        symbol = symbol.upper()  # Convert to uppercase for case-insensitive comparison
        
        # First check the file format by examining the first few lines
        with open(csv_path, 'r') as file:
            first_lines = [file.readline().strip() for _ in range(5)]
        
        # Check if this is a semicolon or comma separated file
        delimiter = ',' if ',' in first_lines[0] else ';'
        
        # Try to open and read the file with the correct delimiter
        with open(csv_path, 'r') as file:
            sample = file.read(4096)  # Read a sample to determine format
            
            # Reset file pointer
            file.seek(0)
            
            # Try different delimiters if comma doesn't work
            if delimiter == ',' and sample.count(',') < 5:
                if sample.count(';') > 5:
                    delimiter = ';'
                elif sample.count('\t') > 5:
                    delimiter = '\t'
            
            # Create reader with detected delimiter
            csv_reader = csv.reader(file, delimiter=delimiter)
            
            # Try to read headers
            headers = next(csv_reader)
            print(f"   Using delimiter: '{delimiter}'")
            print(f"   Headers found: {headers}")
            
            # Since we don't know the structure, let's try to find columns with 'SYMBOL' or 'ISIN' in them
            symbol_idx = None
            isin_idx = None
            
            # Try to find the symbol column
            for i, col in enumerate(headers):
                if symbol.upper() in col.upper():
                    # If the symbol itself is in a header, this might be a column-name style CSV
                    continue
                    
                if any(keyword in col.upper() for keyword in ['SYMBOL', 'NAME', 'TICKER']):
                    symbol_idx = i
                    print(f"   Found symbol column: {col} at index {i}")
                    break
            
            # Try to find the ISIN column
            for i, col in enumerate(headers):
                if 'ISIN' in col.upper() or 'CODE' in col.upper():
                    isin_idx = i
                    print(f"   Found ISIN column: {col} at index {i}")
                    break
            
            # If we couldn't find columns by name, try to determine by examining data
            if symbol_idx is None or isin_idx is None:
                print("   Trying to determine columns by data patterns...")
                
                # Read a few rows to analyze
                rows = [next(csv_reader) for _ in range(10) if csv_reader]
                
                # Look for columns that match ISIN pattern (12 alphanumeric chars)
                for i, col in enumerate(headers):
                    # Check if column values match ISIN pattern
                    isin_pattern = all(len(row[i]) == 12 and row[i].isalnum() for row in rows if i < len(row))
                    if isin_pattern:
                        isin_idx = i
                        print(f"   Found likely ISIN column at index {i}")
                        break
                
                # Look for columns that might be symbols (typically shorter, all caps)
                if symbol_idx is None:
                    for i, col in enumerate(headers):
                        # Skip ISIN column if already found
                        if i == isin_idx:
                            continue
                        # Check if column values look like symbols
                        symbol_pattern = all(len(row[i]) < 20 and not row[i].isdigit() for row in rows if i < len(row))
                        if symbol_pattern:
                            symbol_idx = i
                            print(f"   Found likely symbol column at index {i}")
                            break
            
            # If still not found, print detailed debug info
            if symbol_idx is None or isin_idx is None:
                print("   Could not identify columns automatically. File contents sample:")
                file.seek(0)
                for i, line in enumerate(file):
                    if i < 5:  # Print first 5 lines
                        print(f"   Line {i}: {line.strip()}")
                
                error_msg = "CSV file format is not valid, couldn't identify symbol and ISIN columns"
                print(f"   Error: {error_msg}")
                return {"error": error_msg}
            
            # Reset file pointer to search for the symbol
            file.seek(0)
            next(csv_reader)  # Skip header row
            
            # Search for the symbol
            for row in csv_reader:
                if len(row) > max(symbol_idx, isin_idx):
                    csv_symbol = row[symbol_idx].strip().upper()
                    if csv_symbol == symbol:
                        isin = row[isin_idx]
                        print(f"   Result: Found ISIN {isin} for symbol {symbol}")
                        return {"isin": isin, "symbol": symbol, "nse_format": f"NSE_EQ|{isin}"}
            
            # Symbol not found
            error_msg = f"Symbol '{symbol}' not found in CSV file"
            print(f"   Result: {error_msg}")
            return {"error": error_msg}
            
    except Exception as e:
        error_msg = f"Error reading CSV file: {str(e)}"
        print(f"   Error: {error_msg}")
        return {"error": error_msg}

# --- Gemini Configuration and Interaction ---

def load_gemini_api_key():
    """Loads the Gemini API key from the config file."""
    config_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'config.json')
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
        api_key = config.get("gemini_api_key")
        if not api_key:
            print("Warning: gemini_api_key not found in config.json. "
                  "Ensure GOOGLE_API_KEY environment variable is set.")
        return api_key
    except FileNotFoundError:
        print(f"Info: Config file not found at {config_path}. "
              "Ensure GOOGLE_API_KEY environment variable is set.")
        return None
    except json.JSONDecodeError:
        raise ValueError(f"Error decoding JSON from {config_path}")

def setup_environment_api_key():
    """
    Ensures the Gemini API key is available as an environment variable.
    """
    api_key = load_gemini_api_key()
    if not os.getenv('GOOGLE_API_KEY'):
        if api_key:
            print("Info: Setting GOOGLE_API_KEY environment variable from config file.")
            os.environ['GOOGLE_API_KEY'] = api_key
        else:
            raise ValueError("Gemini API Key configuration error: "
                             "Set the GOOGLE_API_KEY environment variable or "
                             "provide 'gemini_api_key' in config/config.json.")
    print("Gemini client configured (using GOOGLE_API_KEY environment variable).")


# Define the function declarations
function_declarations = [
    FunctionDeclaration(
        name="get_market_data",
        description="Retrieves historical market data for a given NSE stock symbol.",
        parameters={
            "type": "object",
            "properties": {
                'symbol': {"type": "string", "description": "NSE stock symbol (format: NSE_EQ|<isin_code>)"},
                'days': {"type": "integer", "description": "Number of days of historical data (default 30)"}
            },
            "required": ['symbol']
        }
    ),
    # ... (other function declarations remain the same) ...
    FunctionDeclaration(
        name="place_buy_order",
        description="Places a buy order for a specified quantity of an NSE stock.",
        parameters={
            "type": "object",
            "properties": {
                'symbol': {"type": "string", "description": "NSE stock symbol (format: NSE_EQ|<isin_code>)"},
                'quantity': {"type": "integer", "description": "Number of shares to buy"}
            },
            "required": ['symbol', 'quantity']
        }
    ),
    FunctionDeclaration(
        name="place_sell_order",
        description="Places a sell order for a specified quantity of an NSE stock.",
        parameters={
            "type": "object",
            "properties": {
                'symbol': {"type": "string", "description": "NSE stock symbol (format: NSE_EQ|<isin_code>)"},
                'quantity': {"type": "integer", "description": "Number of shares to sell"}
            },
            "required": ['symbol', 'quantity']
        }
    ),
    FunctionDeclaration(
        name="get_portfolio",
        description="Retrieves the current user's portfolio holdings.",
        parameters={"type": "object", "properties": {}}
    ),
    FunctionDeclaration(
        name="get_current_price",
        description="Retrieves the current market price for a given NSE stock symbol.",
        parameters={
            "type": "object",
            "properties": {
                'symbol': {"type": "string", "description": "NSE stock symbol (format: NSE_EQ|<isin_code>)"}
            },
            "required": ['symbol']
        }
    ),
    FunctionDeclaration(
        name= "get_isin_for_symbol",
        description= "Retrieves the International Securities Identification Number (ISIN) for a given stock ticker symbol using the Financial Modeling Prep (FMP) API. Can optionally filter by a specific stock exchange.",
        parameters= {
           "type": "object",
           "properties": {
           "stock_symbol": {
            "type": "string",
            "description": "The stock ticker symbol to look up (e.g., 'AAPL', 'MSFT', 'GOOGL')."
          },
          "exchange": {
            "type": "string",
            "description": "Optional: The specific stock exchange (e.g., 'NASDAQ', 'NYSE', 'LSE') where the stock symbol trades. Helps narrow down results if the symbol exists on multiple exchanges."
          }
        },
        "required": ['stock_symbol']
      }
    ),
    FunctionDeclaration(
        name="get_isin_from_csv",
        description="Retrieves the ISIN code for a given NSE stock symbol from the local database.",
        parameters={
            "type": "object",
            "properties": {
                "symbol": {
                    "type": "string",
                    "description": "The stock symbol to look up (e.g., 'RELIANCE', 'TCS', 'INFY')."
                }
            },
            "required": ['symbol']
        }
    )

]

# Map function names to actual Python functions
available_functions = {
    "get_market_data": get_market_data_wrapper,
    "place_buy_order": place_buy_order_wrapper,
    "place_sell_order": place_sell_order_wrapper,
    "get_portfolio": get_portfolio_wrapper,
    "get_current_price": get_current_price_wrapper,
    "get_isin_for_symbol":get_isin_for_symbol_wrapper,
    "get_isin_from_csv": get_isin_from_csv_wrapper
}

# System prompt (can be included in the 'contents' or potentially a separate param if supported)
# Note: System prompts in generate_content are handled differently than in GenerativeModel.
# Often, you prepend it to the 'contents' list with role 'system'.
system_prompt_text = """
You are a trading assistant that helps users analyze stocks and execute trades on NSE India.

Before calling any function that requires a stock symbol, you MUST find the accurate ISIN code using:
 get_isin_from_csv - Look up symbol in local database (faster, NSE symbols only), VERY IMPORTANT:search for the exact symbol given by the user ONLY
Example: If the user asks about Reliance and csv search reveals ISIN INE002A01018, use "NSE_EQ|INE002A01018" in function calls.

Use the available functions to fulfill user requests for market data, trading, portfolio information, and current prices. Always use the correct NSE_EQ|<isin_code> format for symbols.

After executing a function, present the result clearly to the user, along with any relevant analysis or confirmation. If search fails to find an ISIN, inform the user.
"""

def trading_assistant(user_input):
    """Process user input using client.models.generate_content."""
    setup_environment_api_key()
    client = genai.Client()
    model_id = "gemini-2.5-flash-preview-04-17"

    # Tool Configuration
    function_tool = Tool(function_declarations=function_declarations)
    all_tools = [function_tool]

    print(f"\nUser Input: {user_input}")

    # Initialize conversation history
    conversation = [
        {"role": "user", "parts": [{"text": user_input}]}
    ]

    while True:
        try:
            response = client.models.generate_content(
                model=model_id,
                contents=conversation,
                config=GenerateContentConfig(
                    tools=all_tools,
                    system_instruction=system_prompt_text
                )
            )

            if not response or not response.candidates:
                print("Error: Empty response from Gemini")
                return "I apologize, but I received an empty response. Please try again."

            candidate = response.candidates[0]
            if not candidate.content or not candidate.content.parts:
                print("Error: Empty content/parts in response")
                return "I apologize, but I received an invalid response. Please try again."

            first_part = candidate.content.parts[0]
            conversation.append({"role": "model", "parts": candidate.content.parts})

            # Check for function call
            if hasattr(first_part, 'function_call') and first_part.function_call and first_part.function_call.name:
                function_call = first_part.function_call
                function_name = function_call.name
                args = function_call.args
                print(f"Gemini requested function call: {function_name}({dict(args)})")

                if function_name not in available_functions:
                    error_msg = f"Function '{function_name}' is not available"
                    print(f"Error: {error_msg}")
                    conversation.append({
                        "role": "function",
                        "parts": [{
                            "function_response": {
                                "name": function_name,
                                "response": {"error": error_msg}
                            }
                        }]
                    })
                    continue

                try:
                    function_response_data = available_functions[function_name](**dict(args))
                    conversation.append({
                        "role": "function",
                        "parts": [{
                            "function_response": {
                                "name": function_name,
                                "response": {"result": function_response_data}
                            }
                        }]
                    })
                    print(f"Function {function_name} executed successfully")
                except Exception as e:
                    error_msg = f"Error executing {function_name}: {str(e)}"
                    print(f"Error: {error_msg}")
                    conversation.append({
                        "role": "function",
                        "parts": [{
                            "function_response": {
                                "name": function_name,
                                "response": {"error": error_msg}
                            }
                        }]
                    })
                continue

            # Extract final text response
            final_text = ""
            for part in candidate.content.parts:
                if hasattr(part, 'text') and part.text is not None:
                    final_text += part.text

            if not final_text.strip():
                print("Warning: Empty text response")
                return "I apologize, but I couldn't generate a proper response. Please try again."

            print(f"Gemini Final Response: {final_text}")
            return final_text

        except Exception as e:
            error_msg = f"Error processing response: {str(e)}"
            print(error_msg)
            print(f"Raw response: {response}")
            return f"I encountered an error while processing your request: {error_msg}"