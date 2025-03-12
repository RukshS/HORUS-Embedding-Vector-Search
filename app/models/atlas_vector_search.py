import pymongo
from pymongo.operations import SearchIndexModel
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
model = SentenceTransformer(model_path_str)

# Define function to generate embeddings
def get_embedding(text):
    return model.encode(text).tolist()

# # Create your index model, then create the search index
# search_index_model = SearchIndexModel(
#   definition = {
#     "fields": [
#       {
#         "type": "vector",
#         "numDimensions": 1024,
#         "path": "embeddings",
#         "similarity": "dotProduct"
#       }
#     ]
#   },
#   name = "tracking_modules_vector_index",
#   type = "vectorSearch" 
# )

# modules_collection_other.create_search_index(model=search_index_model)

# Function to get the results of a vector search query
def get_query_results(query):
   query_embedding = get_embedding(query)

   pipeline = [
      {
            "$vectorSearch": {
               "index": "tracking_modules_vector_index",
               "queryVector": query_embedding,
               "path": "embeddings",
               "exact": True, 
               "limit": 4
            }
      }, {
            "$project": {
               "_id": 0,
               "module_id": 1,
               "module_name": 1,
               "description": 1,
               "score": {
                  "$meta": "vectorSearchScore"
               }
            }
      }
   ]

   results = modules_collection_other.aggregate(pipeline)

   array_of_results = []
   for doc in results:
      array_of_results.append(doc)
   return array_of_results
