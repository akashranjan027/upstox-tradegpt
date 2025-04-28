import google.generativeai as genai
import json
import os
from . import market_data, trading

def load_gemini_api_key():
    config_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'config.json')
    with open(config_path, 'r') as f:
        config = json.load(f)
    return config.get("gemini_api_key")

def setup_gemini():
    """Set up Gemini model with API key"""
    api_key = load_gemini_api_key()
    genai.configure(api_key=api_key)
    #return genai.GenerativeModel('gemini-2.5-pro-exp-03-25')
    return genai.GenerativeModel('gemini-2.5-flash-preview-04-17')

def process_function_calls(function_text):
    """Parse and process function calls from Gemini's response"""
    # Function call parsing logic
    # This is a simplified example - in a real implementation, you'd need to
    # parse the function name and arguments from the text
    
    if "get_market_data" in function_text:
        # Extract parameters (simplified)
        symbol = "NSE_RELIANCE"  # Default example
        if "symbol:" in function_text:
            start = function_text.find("symbol:") + 7
            end = function_text.find(",", start)
            if end == -1:
                end = function_text.find(")", start)
            symbol = function_text[start:end].strip().strip('"\'')
        
        days = 30
        if "days:" in function_text:
            start = function_text.find("days:") + 5
            end = function_text.find(",", start)
            if end == -1:
                end = function_text.find(")", start)
            days = int(function_text[start:end].strip())
        
        return {"function": "get_market_data", "result": market_data.get_market_data(symbol, days=days)}
    
    elif "place_buy_order" in function_text:
        # Extract parameters (simplified)
        symbol = "NSE_RELIANCE"
        if "symbol:" in function_text:
            start = function_text.find("symbol:") + 7
            end = function_text.find(",", start)
            symbol = function_text[start:end].strip().strip('"\'')
        
        quantity = 1
        if "quantity:" in function_text:
            start = function_text.find("quantity:") + 9
            end = function_text.find(",", start)
            if end == -1:
                end = function_text.find(")", start)
            quantity = int(function_text[start:end].strip())
        
        return {"function": "place_buy_order", "result": trading.place_buy_order(symbol, quantity)}
    
    elif "place_sell_order" in function_text:
        # Extract parameters (simplified)
        symbol = "NSE_RELIANCE"
        if "symbol:" in function_text:
            start = function_text.find("symbol:") + 7
            end = function_text.find(",", start)
            symbol = function_text[start:end].strip().strip('"\'')
        
        quantity = 1
        if "quantity:" in function_text:
            start = function_text.find("quantity:") + 9
            end = function_text.find(",", start)
            if end == -1:
                end = function_text.find(")", start)
            quantity = int(function_text[start:end].strip())
        
        return {"function": "place_sell_order", "result": trading.place_sell_order(symbol, quantity)}
    
    elif "get_portfolio" in function_text:
        return {"function": "get_portfolio", "result": trading.get_portfolio()}

    elif "get_current_price" in function_text:
        # Extract the symbol argument
        symbol = None
        if "symbol:" in function_text:
            start = function_text.find("symbol:") + len("symbol:")
            # find end of value at comma or closing paren
            end = function_text.find(",", start)
            if end == -1:
                end = function_text.find(")", start)
            symbol = function_text[start:end].strip().strip('"\'')

        # Call your market_data function
        price = market_data.get_current_price(symbol)
        return {"function": "get_current_price", "result": price}

    return None

def trading_assistant(user_input):
    """Process user input and generate response using Gemini"""
    model = setup_gemini()
    
    # First, let's give context to the model
    system_prompt = """
    You are a trading assistant that helps users analyze stocks and execute trades on NSE India.

    Important: For any stock-related query, get the ISIN code if not provided.
    The symbol format for NSE stocks should be: NSE_EQ_<SYMBOL>
    Example: For Reliance with ISIN INE002A01018, use "NSE_EQ|INE002A01018"

    Available Functions:

    1. get_market_data(symbol: str, days: int = 30)
       Input:
       - symbol: NSE stock symbol (format: NSE_EQ|<isin_code>)
       - days: Number of days of historical data (default 30)
       Returns: Historical market data for analysis

    2. place_buy_order(symbol: str, quantity: int)
       Input:
       - symbol: NSE stock symbol (format: NSE_EQ|<isin_code>)
       - quantity: Number of shares to buy
       Returns: Order confirmation details

    3. place_sell_order(symbol: str, quantity: int)
       Input:
       - symbol: NSE stock symbol (format: NSE_EQ|<isin_code>)
       - quantity: Number of shares to sell
       Returns: Order confirmation details

    4. get_portfolio()
       Returns: Current portfolio holdings

    5. get_current_price(symbol: str)
       Input:
       - symbol: NSE stock symbol (format: NSE_EQ|<isin_code>)
       Returns: Current market price

    Function Call Format:
    FUNCTION: function_name(parameter1: value1, parameter2: value2)

    Always verify the ISIN and construct proper NSE_EQ symbol before making function calls.
    After getting results, provide your analysis or confirmation.
    """
    
    # Send the user input to Gemini
    response = model.generate_content([
        system_prompt,
        user_input
    ])
    
    response_text = response.text
    
    # Check if the response contains function calls
    if "FUNCTION:" in response_text:
        # Extract function calls
        start_idx = response_text.find("FUNCTION:")
        end_idx = response_text.find("\n", start_idx)
        if end_idx == -1:
            end_idx = len(response_text)
        
        function_text = response_text[start_idx:end_idx]
        
        # Process the function call
        function_result = process_function_calls(function_text)
        
        if function_result:
            # Send the function result back to Gemini for interpretation
            final_response = model.generate_content([
                system_prompt,
                user_input,
                f"Function result for {function_result['function']}:\n{json.dumps(function_result['result'], default=str)}"
            ])
            
            return final_response.text
    
    # If no function calls or processing failed, return the original response
    return response_text 