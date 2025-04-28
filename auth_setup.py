from src import auth

if __name__ == "__main__":
    print("Starting Upstox authentication process...")
    print("A browser window will open. Please log in to your Upstox account and authorize the application.")
    auth.start_authentication() 