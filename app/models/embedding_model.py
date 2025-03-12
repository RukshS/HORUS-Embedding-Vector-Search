from sentence_transformers import SentenceTransformer
from pymongo import MongoClient
import os
from dotenv import load_dotenv
from pathlib import Path
import sys
import csv

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
	client_other = MongoClient(MONGODB_URL)
	database = client_other.get_database("privileged_database")
	modules_collection_other = database.get_collection("tracking_modules")
except Exception as e:
	print(f"Error connecting to MongoDB: {e}", file=sys.stderr)
	sys.exit(1)

model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2') 

def embed():
    for module in modules_collection_other.find({"description":{"$exists": True}}):
        module["description_embedding"] = model.encode(module["description"])
        result = modules_collection_other.update_one(
        {"_id": module["_id"]},
        {"$set": module}
    )
    
		
