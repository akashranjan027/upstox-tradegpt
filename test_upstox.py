# test_upstox.py

from src import auth
from src import market_data
from src import trading
import json

def test_authentication():
    """Test if authentication is working properly"""
    print("Testing Upstox authentication...")
    
    # Check if we have a token
    token = auth.get_token()
    if not token:
        print("No token found. Starting authentication process...")
        auth.start_authentication()
        token = auth.get_token()
        
    if token:
        print("✅ Authentication successful!")
    else:
        print("❌ Authentication failed!")
    
    return token is not None

def test_market_data():
    """Test market data retrieval functions"""
    print("\nTesting market data retrieval...")

    try:
        # Test with a popular stock (Reliance)
        symbol = 'NSE_EQ|INE669E01016'

        # Get market data
        print(f"Getting market data for {symbol}...")
        data = market_data.get_market_data(symbol, days=7)

        # Check for null data
        if data is None:
            print("❌ Received null data from market_data API")
            return False

        # Check for error dictionary
        if isinstance(data, dict) and "error" in data:
            print(f"❌ Failed to get market data: {data['error']}")
            return False

        print(f"✅ Successfully retrieved market data!")
        print(f"Latest 3 data points:")
        print(data.tail(3))

        # Get current price with error handling
        print(f"\nGetting current price for {symbol}...")
        price = market_data.get_current_price(symbol)

        if price is None:
            print("❌ Received null price from market_data API")
            return False

        if isinstance(price, dict) and "error" in price:
            print(f"❌ Failed to get current price: {price['error']}")
            return False

        print(f"✅ Current price for {symbol}: {price}")

        return True

    except Exception as e:
        import traceback
        print(f"❌ Exception occurred in test_market_data: {str(e)}")
        print("Traceback:")
        print(traceback.format_exc())
        return False

def test_portfolio():
    """Test portfolio retrieval"""
    print("\nTesting portfolio retrieval...")

    holdings = trading.get_portfolio()

    if isinstance(holdings, dict) and "error" in holdings:
        print(f"❌ Failed to get portfolio: {holdings['error']}")
        return False

    print("✅ Successfully retrieved portfolio!")

    if not holdings:
        print("No holdings in portfolio.")
    else:
        print(f"Found {len(holdings)} holdings:")
        for holding in holdings:
            pnl = (holding['last_price'] - holding['average_price']) * holding['quantity']
            print(f"- {holding['tradingsymbol']}")
            print(f"  Quantity: {holding['quantity']} shares")
            print(f"  Last Price: ₹{holding['last_price']:.2f}")
            print(f"  Average Price: ₹{holding['average_price']:.2f}")
            print(f"  P&L: ₹{pnl:.2f}")
            print()

    return True

def paper_trade_test():
    """Simulate a trade without actually executing it"""
    print("\nTesting paper trading simulation...")

    # Use the exact instrument key format from the working example
    symbol = 'NSE_EQ|INE040A01034' # Using the symbol from the example
    quantity = 1

    print(f"Getting current price for {symbol}...")
    price = market_data.get_current_price(symbol)

    if isinstance(price, dict) and "error" in price:
        # Print the detailed error message from the function
        print(f"❌ Failed to get current price: {price['error']}")
        return False

    # Check if price is a valid number before proceeding
    if not isinstance(price, (int, float)):
        print(f"❌ Received invalid price data: {price}")
        return False

    print(f"✅ Current price retrieved: ₹{price:.2f}") # Format price for display
    print(f"Simulating BUY order: {quantity} shares at ₹{price:.2f}")
    total_cost = price * quantity
    print(f"Total cost would be: ₹{total_cost:.2f}")

    print("✅ Paper trade simulation completed (no actual order placed)")
    return True

def main():
    print("=== UPSTOX API TEST SCRIPT ===")
    
    # Run authentication test first
    auth_success = test_authentication()
    if not auth_success:
        print("\n❌ Authentication failed. Cannot proceed with further tests.")
        return
    
    # Test options menu
    while True:
        print("\nChoose a test to run:")
        print("1. Test market data retrieval")
        print("2. Test portfolio retrieval")
        print("3. Test paper trading (simulation)")
        print("4. Run all tests")
        print("0. Exit")
        
        choice = input("\nEnter your choice (0-4): ")
        
        if choice == "1":
            test_market_data()
        elif choice == "2":
            test_portfolio()
        elif choice == "3":
            paper_trade_test()
        elif choice == "4":
            test_market_data()
            test_portfolio()
            paper_trade_test()
        elif choice == "0":
            print("Exiting test script.")
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()