import pymongo
from sentence_transformers import SentenceTransformer
import time
import os
from dotenv import load_dotenv
from pathlib import Path
import sys
import csv
from bson.binary import Binary

# Connect to MongoDB
# Find the project root directory (2 levels up from current file)
current_file = Path(__file__)
project_root = current_file.parent.parent
env_path = project_root / ".env"  # Path to .env file

# Load environment variables from parent directory's .env file
load_dotenv(dotenv_path=env_path)
# Connect to your Atlas deployment
MONGODB_URL = os.getenv("MONGODB_URL")

if not MONGODB_URL:
	print("Error: MONGODB_URL environment variable not set.", file=sys.stderr)
	sys.exit(1)
     
# connect to your Atlas cluster
client_other = pymongo.MongoClient(MONGODB_URL)

modules_collection_other = client_other["privileged_database"]["tracking_modules"]


# Load the embedding model (https://huggingface.co/sentence-transformers/mixedbread-ai/mxbai-embed-large-v1)
model_path = project_root / "models"
# Convert Path to string (important for Windows compatibility)
model_path_str = str(model_path)
model = SentenceTransformer('mixedbread-ai/mxbai-embed-large-v1')
model.save(model_path_str)
model = SentenceTransformer(model_path_str)

# Define function to generate embeddings
def get_embedding(text):
    return model.encode(text).tolist()

# Filters for only documents with a summary field and without an embeddings field
filter = { '$and': [ { 'description': { '$exists': True, '$ne': None } }, { 'embeddings': { '$exists': False } } ] }
# Creates embeddings for subset of the collection
updated_doc_count = 0
for document in modules_collection_other.find(filter).limit(50):
    text = document['description']
    embedding = get_embedding(text)
    modules_collection_other.update_one({ '_id': document['_id'] }, { "$set": { 'embeddings': embedding } }, upsert=True)
    updated_doc_count += 1

print("Documents updated: {}".format(updated_doc_count))
client_other.close()

# # Connect to MongoDB
# # Find the project root directory (2 levels up from current file)
# current_file = Path(__file__)
# project_root = current_file.parent.parent
# env_path = project_root / ".env"  # Path to .env file

# # Load environment variables from parent directory's .env file
# load_dotenv(dotenv_path=env_path)
# # Connect to your Atlas deployment
# MONGODB_URL = os.getenv("MONGODB_URL")

# if not MONGODB_URL:
# 	print("Error: MONGODB_URL environment variable not set.", file=sys.stderr)
# 	sys.exit(1)
     
# try:
# 	client_other = MongoClient(MONGODB_URL)
# 	database = client_other.privileged_database
# 	modules_collection_other = database["tracking_modules"]
# except Exception as e:
# 	print(f"Error connecting to MongoDB: {e}", file=sys.stderr)
# 	sys.exit(1)


# # Create your index model, then create the search index
# search_index_model = SearchIndexModel(
#   definition={
#     "fields": [
#       {
#         "type": "vector",
#         "path": "module_embedding",
#         "numDimensions": 1536,
#         "similarity": "dotProduct",
#         "quantization": "scalar"
#       }
#     ]
#   },
#   name="vector_index",
#   type="vectorSearch",
# )

# result = modules_collection_other.create_search_index(model=search_index_model)
# print("New search index named " + result + " is building.")

# # Wait for initial sync to complete
# print("Polling to check if the index is ready. This may take up to a minute.")
# predicate=None
# if predicate is None:
#   predicate = lambda index: index.get("queryable") is True

# while True:
#   indices = list(modules_collection_other.list_search_indexes(result))
#   if len(indices) and predicate(indices[0]):
#     break
#   time.sleep(5)
# print(result + " is ready for querying.")

# client_other.close()
