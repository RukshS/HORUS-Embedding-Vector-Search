from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv
from pathlib import Path
import sys

# Connect to MongoDB
# Find the project root directory (2 levels up from current file)
current_file = Path(__file__)
project_root = current_file.parent.parent
env_path = project_root / ".env"  # Path to .env file

# Load environment variables from parent directory's .env file
load_dotenv(dotenv_path=env_path)
MONGODB_URL = os.getenv("MONGODB_URL")

if not MONGODB_URL:
	print("Error: MONGODB_URL environment variable not set.", file=sys.stderr)
	sys.exit(1)


try:
	client = AsyncIOMotorClient(MONGODB_URL)
	# Database and collections
	privileged_database = client.privileged_database
	modules_collection = privileged_database["tracking_modules"]
except Exception as e:
	print(f"Error connecting to MongoDB: {e}", file=sys.stderr)
	sys.exit(1)