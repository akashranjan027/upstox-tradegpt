from src import auth

def main():
    access_token = input("Enter your Upstox access token: ")
    if auth.set_access_token(access_token):
        print("Access token set successfully!")
    else:
        print("Failed to set access token")

if __name__ == "__main__":
    main() 