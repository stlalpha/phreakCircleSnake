import subprocess
import json
import time
import openai
import os
import curses
from curses import wrapper
from enum import Enum

# Define the name of the program
PROGRAM_NAME = "CircleSnake"

# Set up OpenAI credentials
with open('creds.json') as f:
    data = json.load(f)
    openai.api_key = data['openai_davinci_key']
# Define the warm-up prompt to instruct the AI on how to interact with CircleSnake
WARM_UP_PROMPT = """Hi Davinci, welcome to our Python programming session! As a quick warm-up exercise, can you please write a non-interactive Python snippet prefixed with "@PYTHON@" that takes two integers as input and calculates their sum? Please note that if your code produces any errors or outputs to stdout, we will be able to see them in our console, so make sure to test your code thoroughly. Thanks!"

Example #1

DaVinci: @PYTHON@ Print('Hello, world!')
User: Exit code: 0. Output: Hello, world!

Example #2

DaVinci: @PYTHON@ f = lambda x: [[y for j, y in enumerate(set(x)) if (i >> j) & 1] for i in range(2**len(set(x)))];f([10,9,1,10,9,1,1,1,10,9,7])


."""


conversation_history = []

# Define the possible states for the session


class SessionState(Enum):
    INITIALIZING = 0
    WAITING_FOR_PROMPT = 1
    PROCESSING_PROMPT = 2
    EXECUTING_PYTHON = 3
# Define a color scheme for the status messages


class StatusColor(Enum):
    DEFAULT = 0
    INITIALIZING = 1
    WAITING_FOR_PROMPT = 2
    PROCESSING_PROMPT = 3
    CONVERSATION_ITEM = 4


stdscr = curses.initscr()
curses.start_color()
curses.use_default_colors()
curses.noecho()
curses.cbreak()
stdscr.keypad(True)
# Set up the curses color pairs
curses.init_pair(StatusColor.INITIALIZING.value,
                 curses.COLOR_YELLOW, curses.COLOR_BLACK)
curses.init_pair(StatusColor.WAITING_FOR_PROMPT.value,
                 curses.COLOR_GREEN, curses.COLOR_BLACK)
curses.init_pair(StatusColor.PROCESSING_PROMPT.value,
                 curses.COLOR_CYAN, curses.COLOR_BLACK)
curses.init_pair(StatusColor.CONVERSATION_ITEM.value,
                 curses.COLOR_WHITE, curses.COLOR_BLACK)

# Define a function to send a prompt to the AI and return the response


def send_prompt(prompt):
    response = openai.Completion.create(
        engine="text-davinci-002",
        prompt=prompt,
        max_tokens=1024,
        n=1,
        stop=None,
        temperature=0.5
    )
    return response.choices[0].text.strip()


# Define a function to run a code snippet in CircleSnake and return the output
def run_code(code):
    subprocess_proc = subprocess.Popen(
        ['python'], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    stdout, stderr = subprocess_proc.communicate(code.encode())

    return stdout.decode()

# Define a function to add a conversation item to the conversation history


def add_conversation_item(speaker, prompt, conversation_history):
    conversation_history.append({
        "speaker": speaker,
        "prompt": prompt,
        "timestamp": time.time()
    })

# Define a function to display the session status message


def display_status_message(stdscr, session_state, conversation_history):
    # Set up the color scheme for the session state
    if session_state == SessionState.INITIALIZING:
        color = StatusColor.INITIALIZING
        status_text = "INITIALIZING"
    elif session_state == SessionState.WAITING_FOR_PROMPT:
        color = StatusColor.WAITING_FOR_PROMPT
        status_text = "WAITING FOR PROMPT"
    elif session_state == SessionState.PROCESSING_PROMPT:
        color = StatusColor.PROCESSING_PROMPT
        status_text = "PROCESSING PROMPT"
    elif session_state == SessionState.EXECUTING_PYTHON:
        color = StatusColor.PROCESSING_PROMPT
        status_text = "EXECUTING PYTHON"

    # Get the last conversation item
    last_item = conversation_history[-1] if conversation_history else None

    # Set the status message based on the current system state and the last conversation item
    if session_state == SessionState.WAITING_FOR_PROMPT:
        if last_item is not None and last_item["speaker"] == PROGRAM_NAME:
            status_message = "SYSTEM: PYTHON SNIPPET EXECUTED. AWAITING PROMPT."
        else:
            status_message = "SYSTEM STATUS: RUNNING. ENTER PROMPT."
    elif session_state == SessionState.PROCESSING_PROMPT:
        status_message = "SYSTEM: PROCESSING PROMPT. PLEASE WAIT."
    elif session_state == SessionState.EXECUTING_PYTHON:
        status_message = "SYSTEM: EXECUTING PYTHON SNIPPET. PLEASE WAIT."
    else:
        print("ERROR: INVALID SESSION STATE.")
        print(session_state)
        status_message = "SYSTEM: ERROR. PLEASE CONTACT SUPPORT."

    # Clear the status line
    stdscr.move(0, 0)
    stdscr.clrtoeol()

    # Display the status message and session state in color
    stdscr.attron(curses.color_pair(color.value))
    stdscr.addstr(0, 0, f"{status_message} ({status_text})")
    stdscr.attroff(curses.color_pair(color.value))

    # Refresh the screen
    stdscr.refresh()


# Define a function to display the conversation history


def display_conversation_history(stdscr, conversation_history):
    # Clear the screen
    stdscr.clear()

    # Display each item in the conversation history
    for i, item in enumerate(conversation_history):
        speaker = item["speaker"]
        prompt = item["prompt"]
        timestamp = item["timestamp"]

        # Set up the color scheme for the conversation item
        # Set up the color scheme for the conversation item
        if speaker == PROGRAM_NAME:
            color = StatusColor.CONVERSATION_ITEM
        else:
            color = StatusColor.DEFAULT

        # Display the conversation item in color
        stdscr.attron(curses.color_pair(color.value))
        stdscr.addstr(i+1, 0, f"{speaker}: {prompt} ({timestamp})")
        stdscr.attroff(curses.color_pair(color.value))

    # Refresh the screen
    stdscr.refresh()

session_state = SessionState.INITIALIZING
# Define the main function for the program
def main(stdscr, conversation_history):
    # Set up the session state
    session_state = SessionState.INITIALIZING
    # Set up the conversation history

    # Display the initial status message
    display_status_message(stdscr, session_state, conversation_history)

    # Warm up the AI
    response = send_prompt(WARM_UP_PROMPT)
    add_conversation_item(PROGRAM_NAME, WARM_UP_PROMPT, conversation_history)
    add_conversation_item("OpenAI", response, conversation_history)

    # Display the conversation history
    display_conversation_history(stdscr, conversation_history)

    # Set the session state to waiting for a prompt
    session_state = SessionState.WAITING_FOR_PROMPT
    display_status_message(stdscr, session_state, conversation_history)


# Set up the session state
session_state = SessionState.INITIALIZING

# Display the initial status message
display_status_message(stdscr, session_state, conversation_history)

# Warm up the AI
response = send_prompt(WARM_UP_PROMPT)
add_conversation_item(PROGRAM_NAME, WARM_UP_PROMPT, conversation_history)
add_conversation_item("OpenAI", response, conversation_history)

# Display the conversation history
display_conversation_history(stdscr, conversation_history)

# Set the session state to waiting for a prompt
session_state = SessionState.WAITING_FOR_PROMPT
display_status_message(stdscr, session_state, conversation_history)

# Enter the main loop for the program
while True:
    
    # Wait for user input
    user_input = stdscr.getstr().decode()
    #exit if user enters q
    if user_input == '[Qq]':
        break

    # Send the prompt to the AI and get the response
    response = send_prompt(user_input)

    # Add the prompt and response to the conversation history
    add_conversation_item("Moderator", user_input, conversation_history)
    add_conversation_item("OpenAI", response, conversation_history)

    # Display the conversation history
    display_conversation_history(stdscr, conversation_history)

    # Refresh the screen
    stdscr.refresh()
    
    # Wait for user input
    user_input = stdscr.getstr().decode()

    if session_state == SessionState.WAITING_FOR_PROMPT:
        # Send the prompt to the AI and get the response
        response = send_prompt(user_input)

        # If the response contains the trigger prefix "@PYTHON@", extract the code and run it
        if "@PYTHON@" in response:
            code = response.split("@PYTHON@")[-1].strip()
            output = run_code(code)

            # Add the code and output to the conversation history
            add_conversation_item("OpenAI", response, conversation_history)
            add_conversation_item(PROGRAM_NAME, output, conversation_history)

            # Display the conversation history
            display_conversation_history(stdscr, conversation_history)
        else:
            # Add the prompt and response to the conversation history
            add_conversation_item("Moderator", user_input,
                                  conversation_history)
            add_conversation_item("OpenAI", response, conversation_history)

            # Display the conversation history
            display_conversation_history(stdscr, conversation_history)

        # Set the session state to processing the prompt
        session_state = SessionState.PROCESSING_PROMPT
        display_status_message(stdscr, session_state)

        # Set the session state back to waiting for a prompt
        session_state = SessionState.WAITING_FOR_PROMPT
        display_status_message(stdscr, session_state)


# Start the program
wrapper(main, conversation_history, session_state)


