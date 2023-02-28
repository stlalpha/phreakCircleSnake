import openai
import json
import ast
import subprocess
import itertools
from threading import Thread
import time
from typing import List, Dict, Any
from typing import Tuple, Optional
from queue import Queue
import io
from contextlib import redirect_stdout, redirect_stderr

# Set up OpenAI API credentials
with open('creds.json') as f:
    data = json.load(f)
    openai.api_key = data['openai_davinci_key']

# establish default session warm-up prompt.
default_prompt = "Let's work together to create some Python code. What do you want to make?"

# Send prompt to OpenAI API


def generate_response(prompt: str) -> str:
    response = openai.Completion.create(engine="text-davinci-002", prompt=prompt, max_tokens=50,
                                        n=1, stop=None, temperature=0.6, presence_penalty=0.6, frequency_penalty=0.5)
    bot_response = response.choices[0].text.strip()
    print(f"Generated response: {bot_response}")
    return bot_response


def parse_python_code(input_string: str) -> Optional[ast.Module]:
    try:
        # Parse the input string into an AST tree
        tree = ast.parse(input_string)
        valid_code = ast.unparse(tree).strip()
        print("The input string contains valid Python code: ", valid_code)
        if isinstance(tree, ast.Module) and len(tree.body) > 0:
            return tree
    except SyntaxError:
        print("The input string does not contain valid Python code.")
    return None





def read_output() -> Tuple[str, str]:
    stdout_output = ''
    stderr_output = ''
    while True:
        stdout_line = process.stdout.readline().decode('utf-8')
        stderr_line = process.stderr.readline().decode('utf-8')
        if not stdout_line and not stderr_line and process.poll() is not None:
            break
        if stdout_line:
            stdout_output += stdout_line
        if stderr_line:
            stderr_output += stderr_line
    return stdout_output, stderr_output




def run_code(input_string: str, imports: List[str] = []) -> Optional[Tuple[str, str]]:
    # Parse the input string into an AST tree
    tree = parse_python_code(input_string)
    if tree is not None:
        # Create a custom namespace to use as the global and local scope
        namespace = {}
        # Add any necessary imports to the namespace
        for import_stmt in imports:
            exec(import_stmt, namespace)
        # Redirect the output of print statements to a StringIO object
        with io.StringIO() as stdout_buffer, io.StringIO() as stderr_buffer:
            with redirect_stdout(stdout_buffer), redirect_stderr(stderr_buffer):
                # Execute the modified code represented by the AST tree in the custom namespace
                exec(compile(tree, "<string>", "exec"), namespace)
                stdout_output, stderr_output = stdout_buffer.getvalue(), stderr_buffer.getvalue()
        print('stdout_output:', stdout_output)  # added
        print('stderr_output:', stderr_output)  # added
        return stdout_output.strip(), stderr_output.strip()
    else:
        print("The input string does not contain valid Python code.")
        return None







def warm_up_prompt() -> str:
    print("Let's start with a warm-up prompt to get the conversation going.")
    print("Type your warm-up prompt to the bot or press Enter to use the default prompt.")
    user_input = input()
    if user_input == "":
        print("Using default prompt.")
        prompt = default_prompt
    else:
        prompt = user_input
    return prompt


def main() -> None:
    prompt = warm_up_prompt()
    imports = []
    while True:
        print("User:", end=" ")
        user_input = input()
        if user_input.lower() == 'quit':
            print('Goodbye!')
            break

        bot_response = generate_response(prompt + "\n" + user_input)

        output = run_code(bot_response, imports)

        # If the output is an import statement, add it to the list of imports
        if output and ("import" in output or "from" in output):
            imports.append(output)
        else:
            print("Bot:", output)
            prompt = bot_response




if __name__ == "__main__":
    main()
