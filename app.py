from os import name
import tkinter as tk
from tkinter import ttk, Text, Scrollbar
import Pinecone
from Pinecone import (
    save_ai_instance_role_and_goals,
    delete_ai_instance,
    load_ai_instance_role_and_goals,
    load_ai_instance_memory   
)
from main import get_ai_response, chat_with_ai
from ttkthemes import ThemedTk

import commands



class Application(tk.Frame):
    def __init__(self, master=None, get_ai_list_func=None, save_ai_metadata_func=None, remove_ai_func=None, chat_with_ai_func=None, get_ai_response_func=None, save_ai_instance_role_and_goals_func=None):
        super().__init__(master)
        self.chat_with_ai_func = chat_with_ai_func
        self.get_ai_response_func = get_ai_response_func
        self.master = master
        self.get_ai_list_func = get_ai_list_func
        self.save_ai_metadata_func = save_ai_metadata_func
        self.save_ai_instance_role_and_goals_func = save_ai_instance_role_and_goals_func
        self.remove_ai_func = remove_ai_func
        self.master.title("Auto-GPT")
        self.master.geometry("900x700")
        self.pack(fill=tk.BOTH, expand=True)
        self.create_widgets()
        self.token_limit = 100
        self.full_message_history = []

        # Load the "azure.tcl" file
        self.master.tk.call("source", "azure.tcl")
        # Set the theme to "light"
        self.master.tk.call("set_theme", "light")

        # Load all AI instances when the GUI is opened
        self.update_ai_list()


        

    def send_message(self, event=None):
        message = self.input_entry.get()
        if message:
            self.chat_area.insert(tk.END, "You: " + message + "\n")
            self.input_entry.delete(0, tk.END)
            self.chat_area.see(tk.END)
            ai_name = self.name_entry.get()
            permanent_memory = Pinecone.load_ai_instance_memory(ai_name)  # Load the AI instance's memory
            self.full_message_history.append(message)  # Append the new message to the history
            ai_response = get_ai_response(ai_name, self.chat_with_ai_func, message, self.full_message_history, permanent_memory, self.token_limit)
            self.chat_area.insert(tk.END, "AI: " + ai_response + "\n")
            self.chat_area.see(tk.END)




    def full_message_history(self, message):
        full_message_history.append(message)

    def token_limit(self):
        return 100

    def load_ai_info(self, event):
        ai_name = self.ai_dropdown.get()
        if not ai_name:
            return  # Do nothing if ai_name is empty or None
        ai_role, ai_goals = Pinecone.load_ai_instance_metadata(ai_name)
        permanent_memory = Pinecone.load_ai_instance_memory(ai_name)  # Load the AI instance's memory
        self.name_entry.delete(0, tk.END)
        self.name_entry.insert(0, ai_name)
        self.role_entry.delete(0, tk.END)
        self.role_entry.insert(0, ai_role)
        self.goals_entry.delete(0, tk.END)
        self.goals_entry.insert(0, ', '.join(ai_goals))
        # Display the AI instance's memory (optional)
        self.memory_entry.delete(0, tk.END)
        self.memory_entry.insert(0, ', '.join(permanent_memory))
        self.display_current_ai_info(ai_name, ai_role, ', '.join(ai_goals))


    def update_ai_metadata(self):
        ai_name = self.name_entry.get()
        ai_role = self.role_entry.get()
        ai_goals = [goal.strip() for goal in self.goals_entry.get().split(',')]
        permanent_memory = Pinecone.load_ai_instance_memory(ai_name)  # Load the AI instance's memory
        if ai_name in self.get_ai_list_func():
            self.save_ai_instance_role_and_goals_func(ai_name, ai_role, ai_goals, permanent_memory)
            Pinecone.save_ai_instance_memory(ai_name, permanent_memory, ai_role, ai_goals)  # Save the AI instance's memory
        else:
            # Create new AI instance
            ai_name = Pinecone.create_new_ai_instance(ai_name, ai_role, ai_goals)  # Store the returned AI name
            self.save_ai_instance_role_and_goals_func(ai_name, ai_role, ai_goals, permanent_memory)
            Pinecone.save_ai_instance_memory(ai_name, permanent_memory, ai_role, ai_goals)  # Save the AI instance's memory
            self.update_ai_list()  # Update the dropdown list
        self.update_ai_list()
        self.display_current_ai_info(ai_name, ai_role, ', '.join(ai_goals))
        self.ai_dropdown.set(ai_name)  # Set the dropdown menu to the newly created AI instance





    def remove_ai_instance(self):
        ai_name = self.name_entry.get()
        if ai_name:
            self.remove_ai_func(ai_name)
        self.update_ai_list()
        self.clear_definition()
        self.display_current_ai_info("", "", "")

    def create_widgets(self):
        self.top_frame = ttk.Frame(self)
        self.top_frame.pack(side="top", pady=20, padx=30, fill=tk.X)

        self.ai_dropdown_label = ttk.Label(self.top_frame, text="Select AI Instance:")
        self.ai_dropdown_label.grid(row=0, column=0, padx=(0, 10))

        ai_list = self.get_ai_list_func()
        self.ai_dropdown = ttk.Combobox(self.top_frame, values=ai_list, state="readonly")
        if ai_list:
            self.ai_dropdown.bind("<<ComboboxSelected>>", self.load_ai_info)
        self.ai_dropdown.grid(row=0, column=1, padx=(0, 10))

        self.remove_metadata_button = ttk.Button(self.top_frame, text="Remove AI", command=self.remove_ai_instance)
        self.remove_metadata_button.grid(row=0, column=3, padx=(0, 10))

        self.ai_definition_frame = ttk.Frame(self)
        self.ai_definition_frame.pack(side="top", pady=20, padx=30, fill=tk.X)

        self.name_label = ttk.Label(self.ai_definition_frame, text="AI Name:")
        self.name_label.grid(row=0, column=0, padx=(0, 10))
    
        self.name_entry = ttk.Entry(self.ai_definition_frame)
        self.name_entry.grid(row=0, column=1, padx=(0, 10))

        self.role_label = ttk.Label(self.ai_definition_frame, text="Role:")
        self.role_label.grid(row=1, column=0, padx=(0, 10))
        self.role_entry = ttk.Entry(self.ai_definition_frame)
        self.role_entry.grid(row=1, column=1, padx=(0, 10))

        self.goals_label = ttk.Label(self.ai_definition_frame, text="Goals:")
        self.goals_label.grid(row=2, column=0, padx=(0, 10))
        self.goals_entry = ttk.Entry(self.ai_definition_frame)
        self.goals_entry.grid(row=2, column=1, padx=(0, 10))

        self.save_metadata_button = ttk.Button(self.ai_definition_frame, text="Save", command=self.update_ai_metadata)
        self.save_metadata_button.grid(row=3, column=1, padx=(0, 10))

        self.current_ai_info = Text(self.ai_definition_frame, wrap=tk.WORD, height=3)
        self.current_ai_info.grid(row=0, column=2, rowspan=3, padx=(0, 10))
        self.current_ai_info_scrollbar = Scrollbar(self.ai_definition_frame, command=self.current_ai_info.yview)
        self.current_ai_info_scrollbar.grid(row=0, column=3, rowspan=3, sticky=tk.N+tk.S)
        self.current_ai_info["yscrollcommand"] = self.current_ai_info_scrollbar.set
        self.chat_frame = ttk.Frame(self)
        self.chat_frame.pack(side="top", pady=20, padx=30, fill=tk.BOTH, expand=True)

        self.chat_area = Text(self.chat_frame, wrap=tk.WORD)
        self.chat_area.pack(side="left", fill=tk.BOTH, expand=True)

        self.chat_scrollbar = Scrollbar(self.chat_frame, command=self.chat_area.yview)
        self.chat_scrollbar.pack(side="right", fill=tk.Y)

        self.chat_area["yscrollcommand"] = self.chat_scrollbar.set

        self.bottom_frame = ttk.Frame(self)
        self.bottom_frame.pack(side="bottom", pady=20, padx=30, fill=tk.X)

        self.input_label = ttk.Label(self.bottom_frame, text="Input:")
        self.input_label.grid(row=0, column=0, padx=(0, 10))

        self.input_entry = ttk.Entry(self.bottom_frame)
        self.input_entry.grid(row=0, column=1, padx=(0, 10), sticky=tk.W+tk.E)
        self.input_entry.bind("<Return>", self.send_message)

        self.send_button = ttk.Button(self.bottom_frame, text="Send", command=self.send_message)
        self.send_button.grid(row=0, column=2, padx=(0, 10))
       
        

        

    def display_current_ai_info(self, ai_name, ai_role, ai_goals):
        self.current_ai_info.delete(1.0, tk.END)
        self.current_ai_info.insert(tk.END, f"Current AI: {ai_name}\nRole: {ai_role}\nGoals: {ai_goals}\n")
        self.current_ai_info.see(tk.END)

    def clear_definition(self):
        self.name_entry.delete(0, tk.END)
        self.role_entry.delete(0, tk.END)
        self.goals_entry.delete(0, tk.END)

    def update_ai_list(self):
        self.ai_dropdown["values"] = self.get_ai_list_func()

def ai_goals(self):
        ai_name = self.name_entry.get()
        ai_role = self.role_entry.get()
        ai_goals = [goal.strip() for goal in self.goals_entry.get().split(',')]
        if ai_name in self.get_ai_list_func():
            # Update existing AI instance
            self.save_ai_metadata_func(ai_name, ai_role, ai_goals)
        else:
            # Create new AI instance
            Pinecone.create_new_ai_instance(ai_name, ai_role, ai_goals)
            self.save_ai_metadata_func(ai_name, ai_role, ai_goals)
        self.update_ai_list()
        self.display_current_ai_info(ai_name, ai_role, ', '.join(ai_goals))

def ai_role(self):
        ai_name = self.name_entry.get()
        ai_role = self.role_entry.get()
        ai_goals = [goal.strip() for goal in self.goals_entry.get().split(',')]
        if ai_name in self.get_ai_list_func():
            # Update existing AI instance
            self.save_ai_metadata_func(ai_name, ai_role, ai_goals)
        else:
            # Create new AI instance
            Pinecone.create_new_ai_instance(ai_name, ai_role, ai_goals)
            self.save_ai_metadata_func(ai_name, ai_role, ai_goals)
        self.update_ai_list()
        self.display_current_ai_info(ai_name, ai_role, ', '.join(ai_goals))

def token_limit(self):
        ai_name = self.name_entry.get()
        ai_role = self.role_entry.get()
        ai_goals = [goal.strip() for goal in self.goals_entry.get().split(',')]
        if ai_name in self.get_ai_list_func():
            # Update existing AI instance
            self.save_ai_metadata_func(ai_name, ai_role, ai_goals)
        else:
            # Create new AI instance
            Pinecone.create_new_ai_instance(ai_name, ai_role, ai_goals)
            self.save_ai_metadata_func(ai_name, ai_role, ai_goals)
        self.update_ai_list()
        self.display_current_ai_info(ai_name, ai_role, ', '.join(ai_goals))

def full_message_history(self):
        ai_name = self.name_entry.get()
        ai_role = self.role_entry.get()
        ai_goals = [goal.strip() for goal in self.goals_entry.get().split(',')]
        if ai_name in self.get_ai_list_func():
            # Update existing AI instance
            self.save_ai_metadata_func(ai_name, ai_role, ai_goals)
        else:
            # Create new AI instance
            Pinecone.create_new_ai_instance(ai_name, ai_role, ai_goals)
            self.save_ai_metadata_func(ai_name, ai_role, ai_goals)
        self.update_ai_list()
        self.display_current_ai_info(ai_name, ai_role, ', '.join(ai_goals))
        


def main():
    root = tk.Tk(theme="azure")  # Use ThemedTk instead of tk.Tk
    app = Application(master=root,
        get_ai_list_func=Pinecone.get_ai_list,
        remove_ai_func=Pinecone.delete_ai_instance,
        token_limit=100,
        save_ai_metadata_func=save_ai_instance_role_and_goals,
        update_ai_list_func=Pinecone.update_ai_list,
        full_message_history = Pinecone.get_full_message_history(),
        chat_with_ai_func=chat_with_ai)
        
    app.mainloop()






