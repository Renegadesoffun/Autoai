import os
import json
from typing import List
import pinecone
from google.protobuf.struct_pb2 import Struct
from google.protobuf.json_format import MessageToJson, ParseDict, MessageToDict

vector_dimension = 1024
full_message_history = []
permanent_memory = []  # Initialize the AI's permanent memory
token_limit = 2048  # Define the token limit for the API call
prompt = "Hello God"  # Define the AI prompt

index_name = "autoai-index"
pinecone.init(api_key="009bdc93-a6f5-4b02-ad3c-0bd900e9de91", environment="us-west1-gcp")
index = pinecone.Index(index_name)

def save_ai_instance_role_and_goals(ai_name, role, goals, permanent_memory):
    metadata = {
        "ai_name": ai_name,
        "role": role,
        "goals": goals
    }
    save_ai_instance_metadata(ai_name, metadata)
    save_ai_instance_memory(ai_name, permanent_memory, role, goals)


def create_new_ai_instance(ai_name, ai_role=None, ai_goals=None):
    # Check if the AI instance already exists
    existing_instance = index.fetch(ids=[ai_name])
    if ai_name in existing_instance:
        print(f"AI instance '{ai_name}' already exists.")
        return existing_instance[ai_name].metadata

    initial_metadata = {
        'ai_name': ai_name,  # Include the AI instance's name
        'role': ai_role or 'Entrepreneur-GPT',
        'goals': ai_goals or [
            'Increase net worth',
            'Grow Twitter Account',
            'Develop and manage multiple businesses autonomously',
        ],
        'memory': []  # Initialize memory as an empty list
    }
    index.upsert(vectors=[(ai_name, [0.0] * vector_dimension, initial_metadata)])

    print(f"Created new AI instance: {ai_name}")  # Add this print statement
    return ai_name  # Return the AI name

def get_ai_list():
    return index.describe_index_stats().index_stats.keys()

def save_ai_instance_role_and_goals(ai_name: str, role: str, goals: List[str], permanent_memory: List[str]):
    metadata = {
        "ai_name": ai_name,  # Include the AI instance's name
        "role": role,
        "goals": goals,
        "memory": permanent_memory  # Save the permanent memory
    }
    index.upsert(vectors=[(ai_name, [0.0] * vector_dimension, metadata)])



def save_ai_instance_memory(ai_name: str, permanent_memory: str, ai_role: str, ai_goals:str,):
    memory_struct = Struct()
    ParseDict({"memory": permanent_memory}, memory_struct)
    memory_json = json.dumps(MessageToDict(memory_struct))
    metadata = {
        "ai_name": ai_name,
        "role": ai_role,
        "goals": ai_goals,
        "memory": memory_json
    }
    index.upsert(vectors=[(ai_name, [0.0] * vector_dimension, metadata)])

def check_if_ai_exists_in_pinecone(ai_name: str) -> bool:
    result = index.fetch(ids=[ai_name])
    if ai_name in result:
        return True
    else:
        return False

def load_ai_instance(ai_name: str):
    result = index.fetch(ids=[ai_name])

    if ai_name not in result:
        print(f"Error: AI instance '{ai_name}' not found in Pinecone.")
        return []

def save_ai_instance_metadata(ai_name, metadata):
    index.upsert(vectors=[(ai_name, [0.0] * vector_dimension, metadata)])

def load_ai_instance_metadata(ai_name: str) -> dict:
    result = index.fetch(ids=[ai_name])

    if ai_name in result:
        metadata = result[ai_name].metadata
        return metadata
    else:
        print(f"Error: AI instance '{ai_name}' not found in Pinecone results.")
        return {}

def load_ai_instance_role_and_goals(ai_name: str):
    metadata = load_ai_instance_metadata(ai_name)
    ai_role = metadata.get('role', '')
    ai_goals = metadata.get('goals', [])
    return ai_role, ai_goals

def check_if_ai_exists_in_pinecone(ai_name: str) -> bool:
    result = index.fetch(ids=[ai_name])
    if ai_name in result:
        return True
    else:
        return False

def update_ai_instance_metadata(ai_name: str, new_metadata: dict):
    if not check_if_ai_exists_in_pinecone(ai_name):
        print(f"Error: AI instance '{ai_name}' does not exist in Pinecone.")
        return

    current_metadata = load_ai_instance_metadata(ai_name)
    current_metadata.update(new_metadata)
    save_ai_instance_metadata(ai_name, current_metadata)

def load_ai_instance_memory(ai_name: str) -> List[str]:
    result = index.fetch(ids=[ai_name])
    if ai_name in result:
        metadata = result[ai_name].metadata
        memory_json = metadata.get('memory', '[]')
        permanent_memory = json.loads(memory_json)
        return permanent_memory
    else:
        print(f"Error: AI instance '{ai_name}' not found.")
        return []

def delete_ai_instance(ai_name: str):
    index.delete(ids=[ai_name])

def upsert_data_to_pinecone(ai_name: str, data: List):
    upsert_data = []
    for item in data:
        item_id, item_vector, item_metadata = item
        upsert_data.append((item_id, item_vector, item_metadata))

    index.upsert(vectors=upsert_data)

def fetch_data_from_pinecone(ai_name: str, ids: List[str]):
    fetched_data = index.fetch(ids=ids)
    return fetched_data

