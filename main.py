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