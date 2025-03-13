import pymongo
from sentence_transformers import SentenceTransformer
import os
from dotenv import load_dotenv
from pathlib import Path
import sys
from pymongo.operations import SearchIndexModel
import time


def setup_model():
    # Your model setup code here
    # Find the project root directory (2 levels up from current file)
    # Find the project root directory (2 levels up from current file)
    current_file = Path(__file__)
    project_root = current_file.parent.parent
    env_path = project_root / ".env"  # Path to .env file

    # Load the embedding model (https://huggingface.co/sentence-transformers/mixedbread-ai/mxbai-embed-large-v1)
    model_path = project_root / "models"
    # Convert Path to string (important for Windows compatibility)
    model_path_str = str(model_path)
    model = SentenceTransformer('mixedbread-ai/mxbai-embed-large-v1')
    # model.save(model_path_str)
    # model = SentenceTransformer(model_path_str)
    return model

# Define function to generate embeddings
def get_embedding(text, model):
    return model.encode(text).tolist()

def update_embeddings_and_index():
   model = setup_model()

   current_file = Path(__file__)
   project_root = current_file.parent.parent
   env_path = project_root / ".env"  # Path to .env file
   # Load environment variables from parent directory's .env file
   load_dotenv(dotenv_path=env_path)
   # Connect to your Atlas deployment
   MONGODB_URL = os.getenv("MONGODB_URL")
   
   if not MONGODB_URL:
       print("Error: MONGODB_URL environment variable not set.", file=sys.stderr); sys.exit(1)
         
   # connect to your Atlas cluster 
   client_other = pymongo.MongoClient(MONGODB_URL)
   
   modules_collection_other = client_other["privileged_database"]["tracking_modules"]
   
   # Filters for only documents with a summary field and without an embeddings field
   filter = { '$and': [ { 'description': { '$exists': True, '$ne': None } }, { 'embeddings': { '$exists': False } } ] }
   # Creates embeddings for subset of the collection
   updated_doc_count = 0
   for document in modules_collection_other.find(filter).limit(50):
       text = document['description']
       embedding = get_embedding(text, model)
       modules_collection_other.update_one({ '_id': document['_id'] }, { "$set": { 'embeddings': embedding } }, upsert=True)
       updated_doc_count += 1
   
   print("Documents updated: {}".format(updated_doc_count))
   
  #  # Specify a new index definition
  #  definition={
  #      "fields": [
  #        {
  #          "type": "vector",
  #          "path": "embeddings",
  #          "numDimensions": 1024,
  #          "similarity": "dotProduct",
  #          "quantization": "scalar"
  #        }
  #      ]
  #  }
   
  #  result = modules_collection_other.update_search_index("tracking_modules_vector_index", definition)
  #  print("Search index is updating.")
  #  # Wait for initial sync to complete
  #  print("Polling to check if the index is ready. This may take up to a minute.")
  #  predicate=None
  #  if predicate is None:
  #    predicate = lambda index: index.get("queryable") is True
  #  while True:
  #    indices = list(modules_collection_other.list_search_indexes(result))
  #    if len(indices) and predicate(indices[0]):
  #      break
  #    time.sleep(5)
  #  print(str(result) + " is ready for querying.")
   client_other.close()