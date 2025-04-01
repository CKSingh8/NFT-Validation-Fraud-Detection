import os
from dotenv import load_dotenv

# Load .env file
load_dotenv()

# Access variables
ALCHEMY_API_URL = os.getenv("https://eth-mainnet.g.alchemy.com/v2/6KiPVliVjkpALZDTzOrsrEvLZbwzZZRZ")
print("Alchemy URL:", ALCHEMY_API_URL)  # Check if it's loaded