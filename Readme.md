# Detailed Setup Guide for Gemini Trading Assistant

## Setting Up Google Gemini and Vertex AI

### Understanding Vertex AI and Gemini Access Options

#### Option 1: Vertex AI (Google Cloud Platform)
- **Cost**: Vertex AI is NOT completely free. It offers a free tier with $300 in credits for new Google Cloud users that expires after 90 days.
- **Pricing**: After the free credits, you pay per token for Gemini usage (typically $0.0001-$0.0007 per 1K input tokens and $0.0001-$0.0008 per 1K output tokens depending on the model).

#### Option 2: Google AI Studio (Free Alternative)
- **Cost**: Google AI Studio offers free access to Gemini models with certain limitations.
- **Limitations**: The free tier has daily quotas (currently up to 60 queries per minute, subject to change).
- **API Key**: You can get a free API key through Google AI Studio that can be used without Vertex AI.

### Detailed Setup for Google AI Studio (Free Option)

1. **Create a Google Account** (if you don't already have one)
   - Go to [accounts.google.com](https://accounts.google.com) and sign up

2. **Access Google AI Studio**
   - Visit [ai.google.dev](https://ai.google.dev/)
   - Click "Sign In" in the top right corner
   - Log in with your Google account

3. **Get an API Key**
   - Navigate to "Get API key" or directly go to [makersuite.google.com/app/apikey](https://makersuite.google.com/app/apikey)
   - Click "Create API key"
   - Copy and save your API key in a secure location (you won't be able to view it again)

4. **Install the Google Generative AI Python Library**
   ```bash
   pip install google-generativeai
   ```

5. **Configure your Python Environment**
   ```python
   import google.generativeai as genai
   
   # Configure the API key
   genai.configure(api_key="YOUR_API_KEY")
   ```

### Detailed Setup for Vertex AI (Paid Option with Free Credits)

1. **Create a Google Cloud Account**
   - Go to [cloud.google.com](https://cloud.google.com/)
   - Click "Get started for free"
   - Sign in with your Google account
   - Complete the registration process including adding credit card details (required even for free tier)
   - You'll receive $300 in free credits valid for 90 days

2. **Create a New Google Cloud Project**
   - Go to the [Google Cloud Console](https://console.cloud.google.com/)
   - In the top menu bar, click on the project dropdown
   - Click "New Project"
   - Name your project (e.g., "gemini-trading-assistant")
   - Click "Create"

3. **Enable the Vertex AI API**
   - In the Google Cloud Console, navigate to "APIs & Services" > "Library"
   - Search for "Vertex AI API"
   - Click on the result and then click "Enable"

4. **Create a Service Account and Download Credentials**
   - Go to "IAM & Admin" > "Service Accounts"
   - Click "Create Service Account"
   - Enter a name (e.g., "gemini-trading-sa")
   - Click "Create and Continue"
   - Assign the "Vertex AI User" role
   - Click "Continue" and then "Done"
   - Find your new service account in the list and click on its name
   - Navigate to the "Keys" tab
   - Click "Add Key" > "Create new key"
   - Choose JSON format and click "Create"
   - The key file will download automatically - save it securely

5. **Install the Vertex AI Python Library**
   ```bash
   pip install google-cloud-aiplatform
   ```

6. **Configure your Python Environment**
   ```python
   import os
   import vertexai
   
   # Set environment variable for credentials
   os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "path/to/your/service-account-key.json"
   
   # Initialize Vertex AI
   vertexai.init(project="your-project-id", location="us-central1")
   ```

## Setting Up Upstox SDK and Authentication

### Installing the Upstox Python SDK

1. **Install the Upstox Python SDK**
   ```bash
   pip install upstox-python-sdk
   ```

2. **Understanding Upstox API Requirements**
   - Upstox offers a Developer Platform that requires registration
   - You'll need a real Upstox trading account to access the API
   - There is no sandbox/testing environment without a real account

### Registering for Upstox Developer API Access

1. **Create an Upstox Trading Account**
   - Visit [upstox.com](https://upstox.com/) and sign up for a trading account
   - Complete the KYC process (this requires Indian residency and documentation)
   - Fund your account with the minimum required amount

2. **Register for Developer Access**
   - Log in to your Upstox account
   - Navigate to the Developer section (usually found in account settings)
   - Apply for API access by filling out the required information
   - Wait for approval (may take 1-7 business days)

3. **Create an Application in the Developer Portal**
   - Once approved, log in to the developer portal
   - Create a new application
   - Provide the required details:
     - Application name
     - Application type (select "Web Application")
     - Redirect URI (e.g., "http://localhost:8080/callback")
     - Homepage URL

4. **Get Your API Credentials**
   - After creating your application, you'll receive:
     - API Key
     - API Secret
   - Save these securely as they'll be needed for authentication

### Setting Up OAuth Authentication

The Upstox API uses OAuth 2.0 for authentication. Here's a step-by-step guide to implementing it:

1. **Create a Configuration File**
   ```python
   import json
   
   # Create a config.json file to store your credentials
   config = {
       "api_key": "YOUR_UPSTOX_API_KEY",
       "api_secret": "YOUR_UPSTOX_API_SECRET",
       "redirect_uri": "YOUR_REDIRECT_URI"  # Must match what you registered
   }
   
   with open('config.json', 'w') as f:
       json.dump(config, f)
   ```

2. **Implement the OAuth Flow**
   ```python
   import json
   import webbrowser
   from flask import Flask, request
   import upstox_client
   from upstox_client.api import LoginApi
   
   # Load the configuration
   with open('config.json', 'r') as f:
       config = json.load(f)
   
   # Create a Flask app to handle the callback
   app = Flask(__name__)
   
   # Store the access token here
   access_token = None
   
   @app.route('/callback')
   def callback():
       global access_token
       code = request.args.get('code')
       
       # Configure the API client
       configuration = upstox_client.Configuration()
       api_instance = LoginApi(upstox_client.ApiClient(configuration))
       
       # Exchange the authorization code for an access token
       token_request = {
           "code": code,
           "client_id": config["api_key"],
           "client_secret": config["api_secret"],
           "redirect_uri": config["redirect_uri"],
           "grant_type": "authorization_code"
       }
       
       try:
           # Get the access token
           api_response = api_instance.token(token_request)
           access_token = api_response.access_token
           
           # Save the token for future use
           with open('token.json', 'w') as f:
               json.dump({"access_token": access_token}, f)
               
           return "Authentication successful! You can close this window."
       except Exception as e:
           return f"Error: {str(e)}"
   
   def start_authentication():
       # Generate the authorization URL
       auth_url = (
           f"https://api.upstox.com/v2/login/authorization/dialog?"
           f"response_type=code&client_id={config['api_key']}"
           f"&redirect_uri={config['redirect_uri']}"
       )
       
       # Open the authorization URL in a browser
       webbrowser.open(auth_url)
       
       # Start the Flask app to handle the callback
       app.run(port=8080)
   
   if __name__ == "__main__":
       start_authentication()
   ```

3. **Using the Access Token**
   ```python
   import json
   import upstox_client
   from upstox_client.api.trading_api import TradingApi
   
   def get_upstox_client():
       # Load the access token
       try:
           with open('token.json', 'r') as f:
               token_data = json.load(f)
               access_token = token_data["access_token"]
       except:
           print("Access token not found. Please authenticate first.")
           return None
       
       # Configure the API client with the access token
       configuration = upstox_client.Configuration()
       configuration.access_token = access_token
       api_client = upstox_client.ApiClient(configuration)
       
       # Return the trading API instance
       return TradingApi(api_client)
   
   # Example: Get user profile
   trading_api = get_upstox_client()
   if trading_api:
       try:
           profile = trading_api.get_profile()
           print(f"Logged in as: {profile.data.user_name}")
       except Exception as e:
           print(f"Error: {str(e)}")
   ```

## Creating the Virtual Environment and Project Structure

1. **Create a Virtual Environment**
   ```bash
   # For macOS/Linux
   python -m venv gemini-trading-env
   source gemini-trading-env/bin/activate
   
   # For Windows
   python -m venv gemini-trading-env
   gemini-trading-env\Scripts\activate
   ```

2. **Install All Required Dependencies**
   ```bash
   pip install google-generativeai upstox-python-sdk flask pandas matplotlib seaborn
   
   # If using Vertex AI instead of Google AI Studio
   pip install google-cloud-aiplatform
   ```

3. **Create Project Directory Structure**
   ```
   gemini-trading-assistant/
   ├── config/
   │   ├── config.json        # API credentials
   │   └── token.json         # Access token (generated during auth)
   ├── src/
   │   ├── __init__.py
   │   ├── auth.py            # Authentication module
   │   ├── trading.py         # Trading functions
   │   ├── market_data.py     # Market data functions
   │   └── gemini.py          # Gemini integration
   ├── .gitignore
   ├── auth_setup.py          # Initial authentication script
   └── main.py                # Main application
   ```

## Complete Code for Integration with Google AI Studio (Free Option)

### auth.py
```python
import json
import webbrowser
from flask import Flask, request
import upstox_client
from upstox_client.api import LoginApi
import os

def load_config():
    config_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'config.json')
    with open(config_path, 'r') as f:
        return json.load(f)

def save_token(token):
    token_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'token.json')
    with open(token_path, 'w') as f:
        json.dump({"access_token": token}, f)

def get_token():
    token_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'token.json')
    try:
        with open(token_path, 'r') as f:
            token_data = json.load(f)
            return token_data["access_token"]
    except:
        return None

def start_authentication():
    config = load_config()
    app = Flask(__name__)
    
    @app.route('/callback')
    def callback():
        code = request.args.get('code')
        
        configuration = upstox_client.Configuration()
        api_instance = LoginApi(upstox_client.ApiClient(configuration))
        
        token_request = {
            "code": code,
            "client_id": config["api_key"],
            "client_secret": config["api_secret"],
            "redirect_uri": config["redirect_uri"],
            "grant_type": "authorization_code"
        }
        
        try:
            api_response = api_instance.token(token_request)
            save_token(api_response.access_token)
            return "Authentication successful! You can close this window."
        except Exception as e:
            return f"Error: {str(e)}"
    
    # Generate the authorization URL
    auth_url = (
        f"https://api.upstox.com/v2/login/authorization/dialog?"
        f"response_type=code&client_id={config['api_key']}"
        f"&redirect_uri={config['redirect_uri']}"
    )
    
    # Open the authorization URL in a browser
    webbrowser.open(auth_url)
    
    # Start the Flask app to handle the callback
    app.run(port=8080)

def get_upstox_client():
    access_token = get_token()
    if not access_token:
        print("No access token found. Please authenticate first.")
        return None
    
    configuration = upstox_client.Configuration()
    configuration.access_token = access_token
    api_client = upstox_client.ApiClient(configuration)
    
    return api_client
```

### market_data.py
```python
from upstox_client.api.market_data_api import MarketDataApi
from upstox_client.rest import ApiException
import pandas as pd
import datetime
from . import auth

def get_market_data(symbol, timeframe="1D", days=30):
    """Get historical market data for a given symbol"""
    api_client = auth.get_upstox_client()
    if not api_client:
        return {"error": "Authentication required"}
    
    market_api = MarketDataApi(api_client)
    
    try:
        # Calculate date range
        end_date = datetime.datetime.now()
        start_date = end_date - datetime.timedelta(days=days)
        
        # Format dates as required by Upstox API
        from_date = start_date.strftime("%Y-%m-%d")
        to_date = end_date.strftime("%Y-%m-%d")
        
        # Get historical data
        response = market_api.get_historical_candle_data(
            instrument_key=symbol,
            interval=timeframe,
            from_date=from_date,
            to_date=to_date
        )
        
        # Convert to pandas DataFrame for easier analysis
        data = []
        for candle in response.data.candles:
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
        return {"error": f"Exception when calling MarketDataApi: {e}"}

def get_current_price(symbol):
    """Get current market price for a given symbol"""
    api_client = auth.get_upstox_client()
    if not api_client:
        return {"error": "Authentication required"}
    
    market_api = MarketDataApi(api_client)
    
    try:
        response = market_api.get_full_market_quote([symbol])
        return response.data[symbol].last_price
    except ApiException as e:
        return {"error": f"Exception when calling MarketDataApi: {e}"}
```

### trading.py
```python
from upstox_client.api.trading_api import TradingApi
from upstox_client.rest import ApiException
from . import auth

def place_buy_order(symbol, quantity, price=None, order_type="MARKET"):
    """Place a buy order for a given symbol"""
    api_client = auth.get_upstox_client()
    if not api_client:
        return {"error": "Authentication required"}
    
    trading_api = TradingApi(api_client)
    
    try:
        # Prepare order request
        order_request = {
            "instrument_token": symbol,
            "quantity": quantity,
            "product": "I",  # Intraday
            "validity": "DAY",
            "price": price,
            "order_type": order_type,
            "transaction_type": "BUY",
            "disclosed_quantity": 0,
            "trigger_price": 0,
            "is_amo": False
        }
        
        # Place order
        response = trading_api.place_order(order_request)
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
    
    trading_api = TradingApi(api_client)
    
    try:
        # Prepare order request
        order_request = {
            "instrument_token": symbol,
            "quantity": quantity,
            "product": "I",  # Intraday
            "validity": "DAY",
            "price": price,
            "order_type": order_type,
            "transaction_type": "SELL",
            "disclosed_quantity": 0,
            "trigger_price": 0,
            "is_amo": False
        }
        
        # Place order
        response = trading_api.place_order(order_request)
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
    
    trading_api = TradingApi(api_client)
    
    try:
        response = trading_api.get_portfolio_holdings()
        holdings = []
        
        for holding in response.data:
            holdings.append({
                "instrument_name": holding.instrument_name,
                "quantity": holding.quantity,
                "average_price": holding.average_price,
                "last_price": holding.last_price,
                "pnl": holding.pnl
            })
        
        return holdings
        
    except ApiException as e:
        return {"error": f"Exception when calling TradingApi: {e}"}
```

### gemini.py (with Google AI Studio - Free)
```python
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
    return genai.GenerativeModel('gemini-pro')

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
    
    return None

def trading_assistant(user_input):
    """Process user input and generate response using Gemini"""
    model = setup_gemini()
    
    # First, let's give context to the model
    system_prompt = """
    You are a trading assistant that helps users analyze stocks and execute trades.
    You can use the following functions:
    
    1. get_market_data(symbol, timeframe="1D", days=30)
       - Gets historical market data for analysis
    
    2. place_buy_order(symbol, quantity, price=None, order_type="MARKET")
       - Places a buy order for a stock
    
    3. place_sell_order(symbol, quantity, price=None, order_type="MARKET")
       - Places a sell order for a stock
    
    4. get_portfolio()
       - Gets current portfolio holdings
    
    If you need to use these functions, write them in the format:
    FUNCTION: function_name(parameter1: value1, parameter2: value2)
    
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
```

### main.py
```python
from src import gemini, auth

def main():
    """Main function to run the AI trading assistant"""
    print("🤖 AI Trading Assistant is starting...")
    
    # Check if authentication is required
    if not auth.get_token():
        print("Authentication required. Opening browser...")
        auth.start_authentication()
    
    print("🤖 AI Trading Assistant is ready!")
    print("Type 'exit' to quit")
    
    while True:
        user_input = input("\n👤 You: ")
        
        if user_input.lower() == "exit":
            print("Goodbye!")
            break
        
        try:
            response = gemini.trading_assistant(user_input)
            print(f"\n🤖 Assistant: {response}")
        except Exception as e:
            print(f"\n🚨 Error: {str(e)}")

if __name__ == "__main__":
    main()
```

### auth_setup.py
```python
from src import auth

if __name__ == "__main__":
    print("Starting Upstox authentication process...")
    print("A browser window will open. Please log in to your Upstox account and authorize the application.")
    auth.start_authentication()
```

### config/config.json (template)
```json
{
    "api_key": "YOUR_UPSTOX_API_KEY",
    "api_secret": "YOUR_UPSTOX_API_SECRET",
    "redirect_uri": "http://localhost:8080/callback",
    "gemini_api_key": "YOUR_GEMINI_API_KEY"
}
```

### .gitignore
```
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
*.egg-info/
.installed.cfg
*.egg

# Virtual Environment
gemini-trading-env/
venv/
ENV/

# Credentials and tokens
config/*.json
*.pem
*.key

# Logs
*.log

# IDE specific files
.idea/
.vscode/
*.swp
*.swo

# OS specific files
.DS_Store
Thumbs.db
```

## Getting Started

1. **Set Up Configuration**
   - Create the project structure as shown above
   - Fill in your API keys in `config/config.json`

2. **Run Initial Authentication**
   ```bash
   python auth_setup.py
   ```
   - Follow the browser prompts to authenticate with Upstox

3. **Start the Trading Assistant**
   ```bash
   python main.py
   ```

4. **Example Interactions**
   - "Analyze the recent performance of RELIANCE stock"
   - "Should I buy INFY shares based on current market conditions?"
   - "Buy 5 shares of HDFCBANK at market price"
   - "Show me my current portfolio"

## Important Notes

1. **Upstox Requirements:**
   - An Upstox trading account is required (only available to Indian residents)
   - API access requires approval from Upstox
   - There are no sandbox/demo environments for testing without a real account

2. **Free Gemini Alternatives:**
   - Google AI Studio provides free access to Gemini with daily quotas
   - No credit card is required for Google AI Studio
   - Free tier lacks some advanced features like structured function calling

3. **Risk Management:**
   - Start with small trade quantities
   - Set up stop-loss orders
   - Consider implementing a "paper trading" mode initially
   - Never deploy without thorough testing

4. **Local Development Tips:**
   - Keep your API keys secure and never commit them to version control
   - Regularly refresh your access tokens
   - Implement error handling for API rate limits
   - Test extensively before using real funds