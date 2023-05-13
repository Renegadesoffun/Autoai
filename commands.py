import browse
import json
import openai
import os
import urllib.request
import pinecone  # Import the Pinecone module
from Pinecone import upsert_data_to_pinecone, vector_dimension

from shared import ai_instances
from typing import List
from sentence_transformers import SentenceTransformer

# Load a pre-trained sentence transformer model
model = SentenceTransformer('paraphrase-distilroberta-base-v1')

def convert_to_vector(text: str):
    # Use the pre-trained sentence transformer model to convert text to vector
    vector = model.encode([text])[0]
    return vector

def search_pinecone(user_input: str, ai_name: str) -> List[str]:
    index_name = "autoai-index"  # Use the same index name you used in create_new_ai_instance
    if index_name not in pinecone.list_indexes():
        print(f"Error: Index '{index_name}' not found.")
        return []
    index = pinecone.Index(index_name=index_name)
    
    # Convert user_input to a vector using an appropriate method (e.g., an embedding model)
    query_vector = convert_to_vector(user_input)
    
    # Perform the search using the query vector
    search_results = index.query(queries=[query_vector], top_k=10)
    
    # Filter search results based on AI instance name (metadata)
    relevant_data = []
    for item_id, item_data in search_results.items():
        if item_data.metadata.get("ai_name") == ai_name:
            relevant_data.append(item_data)
    
    return relevant_data

    return relevant_data

def search_pinecone(user_input: str) -> List[str]:
    ai_name = "autoai-index"  # Replace this with the name of your AI instance
    if ai_name not in ai_instances:
        print(f"Error: AI instance '{ai_name}' not found.")
        return []
    index = ai_instances[ai_name]
    # Convert user_input to a vector using an appropriate method (e.g., an embedding model)
    query_vector = convert_to_vector(user_input)
    # Perform the search using the query vector
    relevant_data = pinecone.deployment.query(queries=[query_vector], top_k=10, index_name=ai_name)
    return relevant_data



def get_relevant_data(relevant_data):
    data_strings = []
    for data in relevant_data:
        data_strings.append(data["content"])
    return data_strings

# Define a global variable to store the AI's information
ai_info = {
    "name": None,
    "role": None,
    "goals": None
}

# Define the set_ai function to set the AI's information
def set_ai(name, role, goals):
    global ai_info
    ai_info["name"] = name
    ai_info["role"] = role
    ai_info["goals"] = goals
    return "AI information set successfully."


# Define the get_ai_info function to retrieve the AI's information
def get_ai_info():
    global ai_info
    return ai_info

def analyze_sentiment(text):
    # Implement sentiment analysis here
    pass

def summarize_article(url):
    # Implement article summarization here
    pass

def generate_text(prompt):
    # Implement text generation here
    pass

def answer_question(question, context):
    # Implement question-answering here
    pass

def classify_text(text, categories):
    # Implement text classification here
    pass


def self () :
    return "Self is "


def create_file(filename):
    if not os.path.exists(filename):
        open(filename, 'w').close()
        return f"File {filename} created successfully."
    else:
        return f"Error: File {filename} already exists."

def open_file(filename):
    if not os.path.exists(filename):
        return f"Error: File {filename} does not exist."
    elif os.path.isdir(filename):
        return f"Error: {filename} is a directory."
    else:
        os.startfile(filename)
        return f"Opening {filename}"
    

    
def suggest_command(user_input):
    if "google search" in user_input.lower():
        query = user_input.replace("google search", "").strip()
        return json.dumps({"name": "google_search", "args": {"query": query}})
    # Use OpenAI's GPT-3.5 Turbo model to generate a suggested command
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  # Use the correct model name
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": user_input}
            ]
        )
        suggestion = response.choices[0].message['content'].strip()
        return suggestion
    except Exception as e:
        return f"Error: {str(e)}"


def open_folder(foldername):
    if not os.path.exists(foldername):
        return f"Error: Folder {foldername} does not exist."
    elif not os.path.isdir(foldername):
        return f"Error: {foldername} is not a directory."
    else:
        os.startfile(foldername)
        return f"Opening {foldername}"
    
def get_ai_list():
    ai_list = pinecone.ai_instances.keys()
    return list(ai_list)

def google_search(ai_name, query, num_results=3):
    search_results = []
    for j in browse.search(query, num_results=num_results):
        search_results.append(j)

    # Convert search results to JSON string
    search_results_json = json.dumps(search_results, ensure_ascii=False, indent=4)

    # Upsert search results as metadata to Pinecone
    upsert_data_to_pinecone(ai_name, [(ai_name, [0.0] * vector_dimension, search_results_json)])

    return search_results_json

    suggestion = response.choices[0].text.strip()
    # Ask the user if they want to execute the suggested command
    response = input(f"Suggested command: {suggestion}. Do you want to execute it? (y/n) ")
    if response.lower() == "y":
        return suggestion
    else:
        return None

def transcribe_summarise(url):
    text = browse.scrape_main_content(url)
    summary = browse.summarize_text(text)
    return """ "Result" : """ + summary

def check_news(source):
    print("Checking news from BBC world instead of " + source)
    _text= transcribe_summarise("https://www.bbc.com/news/world")
    return _text

def commit_memory(string):
    # Use Pinecone to commit memory
    pinecone.commit_memory(string)
    return f"Committing memory with string {string}"

def delete_memory(key):
    # Use Pinecone to delete memory
    result = pinecone.delete_memory(key)
    return result

def overwrite_memory(key, string):
    # Use Pinecone to overwrite memory
    result = pinecone.overwrite_memory(key, string)
    return result

def download_file(url, filename):
    if not os.path.exists('D:\\AutoGPT\\Auto-GPT\\AutonomousAI\\workshop'):
        os.makedirs('D:\\AutoGPT\\Auto-GPT\\AutonomousAI\\workshop')
    if not os.path.exists(f"D:\\AutoGPT\\Auto-GPT\\AutonomousAI\\workshop\\{filename}"):
        try:
            response = input(f"This command may modify or delete files on your computer. Do you want to proceed? (yes/no) ")
            if response.lower() == "yes":
                urllib.request.urlretrieve(url, f"D:\\AutoGPT\\Auto-GPT\\AutonomousAI\\workshop\\{filename}")
                return f"File {filename} downloaded successfully."
            else:
                return "Command cancelled."
        except Exception as e:
            return f"Error downloading file from {url}: {str(e)}"
    else:
        return f"Error: File {filename} already exists in workshop folder."


def execute_command(user_input):
    # Retrieve the suggested command
    suggested_command = suggest_command(user_input)

    if suggested_command.startswith("Error") or suggested_command.startswith("Command not implemented yet"):
        return suggested_command

    try:
        command = json.loads(suggested_command)
        command_name = command["name"]
        arguments = command["args"]

        if command_name == "create_file":
            return create_file(arguments["filename"])
        elif command_name == "open_file":
            return open_file(arguments["filename"])
        elif command_name == "open_folder":
            return open_folder(arguments["foldername"])
        elif command_name == "download_file":
            return download_file(arguments["url"], arguments["filename"])

        if command_name == "google":
            return google_search(arguments["input"])
        elif command_name == "google_search":
            return google_search(ai_info["name"], arguments["query"], arguments.get("num_results", 3))
        elif command_name == "check_news":
            return check_news(arguments["source"])
        elif command_name == "check_notifications":
            return check_notifications(arguments["website"])
        elif command_name == "memory_add":
            return commit_memory(arguments["string"])
        elif command_name == "memory_del":
            return delete_memory(arguments["key"])
        elif command_name == "memory_ovr":
            return overwrite_memory(arguments["key"], arguments["string"])
        elif command_name == "start_instance":
            return start_instance(arguments["name"], arguments["prompt"])
        elif command_name == "manage_instances":
            return manage_instances(arguments["action"])
        elif command_name == "navigate_website":
            return navigate_website(arguments["action"], arguments["username"])
        elif command_name == "register_account":
            return register_account(arguments["username"], arguments["website"])
        elif command_name == "transcribe_summarise":
            return transcribe_summarise(arguments["url"])

        else:
            return f"unknown command {command_name}"
    except KeyError:
        return "Error: Invalid command format"
    except Exception as e:
        return f"Error: {str(e)}"




### TODO: Not Yet Implemented: ###

def start_instance(name, prompt):
    _text = "Starting instance with name " + name + " and prompt " + prompt
    print(_text)
    return "Command not implemented yet."

def manage_instances(action):
    _text = "Managing instances with action " + action
    print(_text)
    return _text

def navigate_website(action, username):
    _text = "Navigating website with action " + action + " and username " + username
    print(_text)
    return "Command not implemented yet."

def register_account(username, website):
    _text = "Registering account with username " + username + " and website " + website
    print(_text)
    return "Command not implemented yet."

def check_notifications(website):
    _text = "Checking notifications from " + website
    print(_text)
    return "Command not implemented yet."