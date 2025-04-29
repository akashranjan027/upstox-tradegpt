# This file makes the src directory a Python package 
import requests
import json # Optional: for pretty printing the raw response if needed

# --- Configuration ---
# Replace with your actual FMP API key
# Get one from: https://financialmodelingprep.com/developer/docs/
API_KEY = "2m4oRMEn5iRCIHabFCuOp4JdPshLqyGO"

# Replace with the stock symbol you want to look up
SYMBOL_TO_FIND = "MSFT"

# Optional: Specify exchange to narrow results (e.g., "NASDAQ", "NYSE")
# Leave as None to search all exchanges
EXCHANGE = "NASDAQ"

# Optional: Limit the number of results returned
LIMIT = 5

# --- API Endpoint ---
BASE_URL = "https://financialmodelingprep.com/api"
SEARCH_ENDPOINT = "/v3/search"
API_URL = f"{BASE_URL}{SEARCH_ENDPOINT}"

# --- Prepare Request Parameters ---
params = {
    'query': SYMBOL_TO_FIND,
    'limit': LIMIT,
    'apikey': API_KEY
}

# Add exchange to parameters if specified
if EXCHANGE:
    params['exchange'] = EXCHANGE

# --- Make the API Call ---
print(f"Searching for symbol: {SYMBOL_TO_FIND}" + (f" on exchange: {EXCHANGE}" if EXCHANGE else ""))

try:
    response = requests.get(API_URL, params=params)
    # Raise an exception if the request returned an error status code (4xx or 5xx)
    response.raise_for_status()

    # Parse the JSON response
    data = response.json()

    # --- Process the Response ---
    if not data:
        print(f"No results found for symbol '{SYMBOL_TO_FIND}'" + (f" on {EXCHANGE}" if EXCHANGE else ""))
    else:
        found_isin = False
        print("\n--- Search Results ---")
        for security in data:
            symbol = security.get('symbol', 'N/A')
            name = security.get('name', 'N/A')
            exchange = security.get('exchangeShortName', 'N/A')
            isin = security.get('isin', 'N/A') # Use .get() for safe access

            print(f"- Symbol: {symbol}, Name: {name}, Exchange: {exchange}, isin: {isin}")

            # Check if the symbol matches exactly (case-sensitive) and ISIN exists
            # Adjust the symbol comparison if case-insensitivity is needed:
            # if symbol.upper() == SYMBOL_TO_FIND.upper() and isin:
            if symbol == SYMBOL_TO_FIND and isin:
                print(f"  >>> Found ISIN: {isin} <<<")
                found_isin = True
                # You might want to break here if you only need the first exact match
                # break
            elif isin:
                 print(f"  - Contains ISIN: {isin} (but symbol might differ slightly or be from a different primary listing)")


        if not found_isin:
             print(f"\nISIN not found in the results for the exact symbol '{SYMBOL_TO_FIND}'" + (f" on {EXCHANGE}" if EXCHANGE else "."))
             print("Note: ISIN might be missing for this security type or not available in FMP data.")
             # Optional: Print the first full result for detailed inspection
             # print("\n--- First Result Details ---")
             # print(json.dumps(data[0], indent=2))


except requests.exceptions.RequestException as e:
    print(f"\nAn error occurred during the API request: {e}")
    # You might want to inspect response.text for more details from FMP if available
    # try:
    #     print("Error Response Body:", response.text)
    # except NameError: # If response object wasn't created
    #     pass
except ValueError as e: # Includes JSONDecodeError
    print(f"\nAn error occurred parsing the JSON response: {e}")
    print("Raw Response Text:", response.text) # Print raw text for debugging
except Exception as e:
    print(f"\nAn unexpected error occurred: {e}")