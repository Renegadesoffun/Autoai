import os
import datetime
import openai
import keys
import memory as mem
from Pinecone import save_ai_instance_memory, json
import Pinecone
import pinecone
from ttkthemes import ThemedTk
from typing import List
from commands import search_pinecone, get_relevant_data, execute_command  
from sentiment_analysis import analyze
import rl_agent
import sentiment_analysis
import advanced_memory
import cmd as commands
import app 
import tensorflow as tf
import argparse
import numpy as np
from commands import search_pinecone, get_relevant_data
from shared import ai_instances
from Pinecone import (
    create_new_ai_instance,
    save_ai_instance_role_and_goals,
    load_ai_instance_role_and_goals,
    load_ai_instance_memory,
    save_ai_instance_memory,
    delete_ai_instance,
)



# Initialize variables
full_message_history = []
ai_name = None  # Initialize ai_name to None
prompt = "Your AI prompt here"  # Define the AI prompt
permanent_memory = []  # Initialize the AI's permanent memory
token_limit = 2048
openai.api_key = keys.OPENAI_API_KEY

index_name = "autoai-index"


# Initialize Pinecone
pinecone.init(api_key=keys.PINECONE_API_KEY, environment=keys.PINECONE_ENVIRONMENT)
pinecone_index = pinecone.Index(index_name)
pinecone = Pinecone


# Initialize the reinforcement learning agent, sentiment analysis model, and memory management system
rl_agent.init()
sentiment_analysis.init()
advanced_memory.init()



def get_ai_response(ai_name: str, chat_with_ai_func, user_input: str, full_message_history: List[str], permanent_memory: List[str], token_limit: int) -> str:
    # Call the chat_with_ai function passed as a parameter and pass the necessary parameters
    ai_response = chat_with_ai_func(ai_name, user_input, full_message_history, permanent_memory, token_limit)
    return ai_response



def get_current_state():
    # Replace this function with your actual implementation
    return None

def take_action(action):
    # Replace this function with your actual implementation
    reward = None
    next_state = None
    done = False
    return reward, next_state, done

def suggest_command(user_input):
    # Replace this function with your actual implementation
    return None

def done():
    # Replace this function with your actual implementation
    return False

class DQN:
    def __init__(self, state_dim, action_dim, hidden_dim=64, learning_rate=1e-3, gamma=0.99):
        self.state_dim = state_dim
        self.action_dim = action_dim
        self.hidden_dim = hidden_dim
        self.learning_rate = learning_rate
        self.gamma = gamma

        # Initialize Q-Network
        self.q_network = tf.keras.Sequential([
            tf.keras.layers.Dense(hidden_dim, activation="relu", input_dim=state_dim),
            tf.keras.layers.Dense(hidden_dim, activation="relu"),
            tf.keras.layers.Dense(action_dim)
        ])
        self.optimizer = tf.keras.optimizers.Adam(learning_rate)

    def predict(self, state):
        return self.q_network.predict(np.array([state]))

    def update(self, state, action, reward, next_state, done):
        state = np.array([state])
        next_state = np.array([next_state])
        target = self.predict(state)
        next_q_value = self.predict(next_state).max()
        target[0][action] = reward + self.gamma * next_q_value * (not done)
        self.q_network.fit(state, target, verbose=0)

def train_dqn():
    # Train the DQN using the replay buffer
    pass

def query_dqn(state):
    # Query the DQN for the best action to take based on the current state
    pass

# Initialize the DQN
state_dim = 4 # replace with actual state dimension
action_dim = 2 # replace with actual action dimension
dqn = DQN(state_dim, action_dim)

# In your interaction loop, you can update the DQN and query it for the best action to take
def interaction_loop():
    while True:
        # Get the current state
        state = get_current_state()

        # Query the DQN for the best action to take
        action = query_dqn(state)

        # Take the action and get the reward and next state
        reward, next_state, done = take_action(action)
        
        # Update the DQN with the experience
        dqn.update(state, action, reward, next_state, done)

        # Train the DQN using the replay buffer
        train_dqn()

def get_ai_list():
    return list(ai_instances.keys())

def update_gui(app_instance, ai_name, ai_role, ai_goals):
    app_instance.display_current_ai_info(ai_name, ai_role, ai_goals)

def start_gui(get_ai_list_func):
    app_instance = app.Application(
    master=ThemedTk(theme="azure"),
    get_ai_list_func=get_ai_list,
    save_ai_metadata_func=save_ai_instance_role_and_goals,
    remove_ai_func=delete_ai_instance,
    chat_with_ai_func=chat_with_ai,
    get_ai_response_func=get_ai_response,
    
)


    app_instance.get_ai_list_func = get_ai_list_func
    app_instance.get_ai_list_func = get_ai_list
    app_instance.save_ai_metadata_func = save_ai_instance_memory

    app_instance.mainloop()  # Start the GUI event loop


command_list = []

def get_datetime():
    return "Current date and time: " + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def create_chat_message(role: str, content: str) -> dict:
    return {"role": role, "content": content}

def chat_with_ai(ai_name: str, user_input: str, full_message_history: List[dict], permanent_memory: List[str], token_limit: int) -> str:

    # Search Pinecone for relevant data
    relevant_data = search_pinecone(user_input)
    relevant_data_strings = get_relevant_data(relevant_data)
    
    current_context = [create_chat_message("system", prompt), create_chat_message("system", f"Permanent memory: {' '.join(permanent_memory)}")]
    current_context.extend(full_message_history[-(token_limit - len(prompt) - len(permanent_memory) - 10):])
    current_context.extend([create_chat_message("user", user_input)])

    sentiment = analyze(user_input)
    current_context.append(create_chat_message("system", f"Sentiment: {sentiment}"))

    # Check if user input contains a predefined command
    command_response = execute_command(user_input)
    if command_response is not None:
        return command_response
    else:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  # Use GPT-3.5-turbo model
            messages=current_context,
        )
        assistant_reply = response.choices[0].message["content"]
        rl_agent.update(assistant_reply)
        return assistant_reply

def interaction_loop(ai_name, save_ai_instance_memory_func):
    permanent_memory = load_ai_instance_memory(ai_name)
    ai_role, ai_goals = load_ai_instance_role_and_goals(ai_name)  # Load the AI instance's role and goals

    while True:
        user_input = input("You: ")
        ai_response = get_ai_response(ai_name, chat_with_ai, user_input, permanent_memory)
        print(f"AI: {ai_response}")
        full_message_history.append({"role": "system", "content": ai_response})
        permanent_memory.append(ai_response)
        save_ai_instance_memory_func(ai_name, ai_role, ai_goals, permanent_memory) 



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Run the AI in GUI mode or terminal mode.')
    parser.add_argument('--gui', action='store_true', help='Run in GUI mode')
    args = parser.parse_args()

    ai_name = "my-ai-instance"  # Replace with the name of your AI instance
    ai_role = "Entrepreneur-GPT"  # Replace with the role of your AI instance
    ai_goals = ["Increase net worth", "Grow Twitter Account", "Develop and manage multiple businesses autonomously"]  # Replace with the goals of your AI instance

    if args.gui:
        app_instance = app.Application(
        master=ThemedTk(theme="azure"),
        get_ai_list_func=get_ai_list,
        save_ai_metadata_func=save_ai_instance_role_and_goals,
        remove_ai_func=delete_ai_instance,
        chat_with_ai_func=chat_with_ai,
        get_ai_response_func=get_ai_response,
       
)


        app_instance.mainloop() 
    else:
        if not Pinecone.check_if_ai_exists_in_pinecone(ai_name):
            Pinecone.create_new_ai_instance(ai_name, ai_role, ai_goals)
        interaction_loop(ai_name, Pinecone.save_ai_instance_memory)
