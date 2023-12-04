from openai import OpenAI
import time
import tkinter as tk
from tkinter import scrolledtext
from tkinter import ttk

client = OpenAI(api_key="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")
ASSISTANT_ID = "asst_vJ36o3cI1KmaUrznlW66zKZh"

global root
root = None

# Function to wait for the run to complete (from your existing code)
def wait_on_run(run, thread):
    while run.status == "queued" or run.status == "in_progress":
        run = client.beta.threads.runs.retrieve(
            thread_id=thread.id,
            run_id=run.id,
        )
        time.sleep(0.5)
    return run

last_two_tutor_messages = []

# Function to send message and receive response from OpenAI (integrated with GUI)
def send_message():
    global last_two_tutor_messages
    user_message = entry_field.get("1.0", tk.END).strip()

    if user_message.lower() == 'mark' and len(last_two_tutor_messages) == 2:
        with open('Marked Questions.txt', 'a', encoding='utf-8') as file:
            for msg in last_two_tutor_messages:
                file.write(msg+ '\n' + '\n')

        popup = tk.Toplevel()
        popup.title("Notice")
        popup.geometry("200x100")
        tk.Label(popup, text="Marked", font=("Arial", 12)).pack(pady=15)
        tk.Button(popup, text="Ok", command=popup.destroy).pack()        

    if user_message.lower() != 'mark':
        # Add user message to conversation history in GUI
        conversation_history.config(state=tk.NORMAL)
        
        conversation_history.insert(tk.END, "You: ")
        conversation_history.tag_add("bold", "end-1c linestart", "end-1c linestart + 5c")
        conversation_history.insert(tk.END, "\n" + user_message + "\n" + "\n")
        
        conversation_history.yview(tk.END)

        # Existing logic to send user's input to the assistant
        client.beta.threads.messages.create(
            thread_id=thread.id,
            role="user",
            content=user_message
        )

        # Existing logic to run the assistant and wait for response (modified for GUI)
        run = client.beta.threads.runs.create(
            thread_id=thread.id,
            assistant_id=ASSISTANT_ID
        )
        run = wait_on_run(run, thread)

        # Displaying AI's response in GUI
        messages = client.beta.threads.messages.list(thread_id=thread.id)
        latest_message = messages.data[0].content[0].text.value
        
        last_two_tutor_messages.append(latest_message)
        if len(last_two_tutor_messages) > 2:
            last_two_tutor_messages.pop(0)

        conversation_history.insert(tk.END, "Tutor: ")
        conversation_history.tag_add("bold", "end-1c linestart", "end-1c linestart + 7c")
        conversation_history.insert(tk.END, "\n" + latest_message + "\n" + "\n")

        conversation_history.yview(tk.END)
        
        conversation_history.config(state=tk.DISABLED)

    # Clear the entry field in GUI
    entry_field.delete("1.0", tk.END)

def generate_next_response():
    
    user_message = "next question on the same topic with the same difficulty"

    client.beta.threads.messages.create(
            thread_id=thread.id,
            role="user",
            content=user_message
        )
    
    # Assuming the existing logic for generating a response can be reused
    run = client.beta.threads.runs.create(
        thread_id=thread.id,
        assistant_id=ASSISTANT_ID
    )
    run = wait_on_run(run, thread)

    # Displaying AI's response in GUI
    messages = client.beta.threads.messages.list(thread_id=thread.id)
    latest_message = messages.data[0].content[0].text.value
    
    conversation_history.config(state=tk.NORMAL)
    conversation_history.insert(tk.END, "Tutor: ")
    conversation_history.tag_add("bold", "end-1c linestart", "end-1c linestart + 7c")
    conversation_history.insert(tk.END, "\n" + latest_message + "\n" + "\n")
    conversation_history.yview(tk.END)
    conversation_history.config(state=tk.DISABLED)


def go_back():
    # Hide the main window and show the welcome window
    root.withdraw()
    welcome_win.deiconify()

# Start a new conversation thread (from existing code)
thread = client.beta.threads.create()

# Modern and sleek color scheme
background_color = "#F5F5F5"  # Light grey background
text_color = "#333333"  # Dark grey text for contrast
font_style = "Roboto, sans-serif"  # Modern font
font_size = 12

def show_marked_questions():
    # Create a new window
    mq_window = tk.Toplevel()
    mq_window.title("Marked Questions")

    # Set the grid layout for the window
    mq_window.grid_rowconfigure(0, weight=1)
    mq_window.grid_columnconfigure(0, weight=1)

    # Create a scrolled text widget to display the file content
    text_area = scrolledtext.ScrolledText(mq_window, wrap=tk.WORD, width=100, height=40)
    text_area.grid(row=0, column=0, sticky="nsew")  # Sticky to all sides

    # Read and display the file content
    with open("Marked Questions.txt", "r", encoding='utf-8') as file:
        text_area.insert(tk.INSERT, file.read())

def main_window():
    # Creating the GUI window
    global entry_field
    global conversation_history
    global root

    if root is None:
        root = tk.Tk()
        root.title("LIGN 101 Tutor")
        root.configure(bg=background_color)

        # GUI elements with enhanced styling
        conversation_history = scrolledtext.ScrolledText(root, state=tk.DISABLED, font=(font_style, 12))
        conversation_history.grid(row=0, column=0, columnspan=2, sticky="nsew", padx=10, pady=10)
        conversation_history.tag_config("bold", font=("Helvetica", 12, "bold"))

        conversation_history.config(font=(font_style, font_size), bg=background_color, fg=text_color)

        entry_field = tk.Text(root, height=3, font=("Helvetica", 12))
        entry_field.grid(row=1, column=0, sticky="nsew", padx=10, pady=10, columnspan=1)
        entry_field.config(font=(font_style, font_size), bg=background_color, fg=text_color)
        entry_field.focus()  # Set focus to the entry field

        send_button = tk.Button(root, text="Send", command=send_message, bg="light grey", font=("Helvetica", 14))
        send_button.grid(row=1, column=2, sticky="nsew", padx=10, pady=10)

        back_button = tk.Button(root, text="Back", command=go_back, bg="light grey", font=("Helvetica", 14))
        back_button.grid(row=2, column=0, columnspan=2, sticky="nsew", padx=10, pady=10)

        next_button = tk.Button(root, text="Next", command=generate_next_response, bg="light grey", font=("Helvetica", 14))
        next_button.grid(row=1, column=1, sticky="nsew", padx=10, pady=10)

        # Configure grid rows and columns
        root.grid_rowconfigure(0, weight=1)  # Makes the conversation history expandable
        root.grid_rowconfigure(1, weight=0)  # Keeps the entry field and send button fixed in size
        root.grid_rowconfigure(2, weight=0)  # Keeps the exit button fixed in size
        root.grid_columnconfigure(0, weight=1)  # Allows the first column to expand
        root.grid_columnconfigure(1, weight=0)  # Keeps the second column fixed in size

    else:
        root.deiconify()

    root.mainloop()

def welcome_window():
    global welcome_win
    welcome_win = tk.Tk()
    welcome_win.title("LIGN101 Tutor")

    welcome_label = tk.Label(welcome_win, text="Welcome to LIGN101 Tutor", font=("Arial", 24))
    welcome_label.pack(pady=20)

    # Start button
    def on_start():
        welcome_win.withdraw()
        main_window()

    start_button = tk.Button(welcome_win, text="Start", command=on_start)
    start_button.pack(pady=20)

    mq_button = tk.Button(welcome_win, text="Marked Questions", command=show_marked_questions)
    mq_button.pack(pady=20)

    welcome_win.mainloop()

welcome_window()
main_window()