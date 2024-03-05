# This is your Python script. Feel free to edit and run it.
import openai
import subprocess
import re
import io
import sys
import contextlib
from modified_config_v4 import RED, RESET, API_KEY, MODEL_ENGINE, CONSTANT, DYNAMICMEMORY
import os

print(f"Debug - API Key: {API_KEY}")  # Debugging line

# Initialize exec_globals
exec_globals = {}

def general_api_call(prompt, extract_code=False, dialogues=None):
    system_content = 'You are a helpful assistant focused on generating Python code and making API calls.' if extract_code else 'Please summarize the following dialogues?'
    user_content = prompt if not dialogues else dialogues

    # Make the API call
    response = openai.Completion.create(
        model=MODEL_ENGINE,
        prompt=[
            {'role': 'system', 'content': system_content},
            {'role': 'user', 'content': user_content}
        ],
        max_tokens=1500
    )

    full_response = response['choices'][0]['message']['content']
    print(f"Debug - Full Response: {full_response}")

    execution_output, exec_globals = "", {}
    
    # Extract code if needed
    if extract_code:
        code_match = re.search(r'"""(.*?)"""', full_response, re.DOTALL)
        if code_match:
            executable_code = code_match.group(1).strip()
            # Execute the code using your function (assuming you have a function named execute_python_code)
            execution_output, exec_globals = execute_python_code(executable_code)

    return full_response, execution_output, exec_globals
summary_response, _, _ = general_api_call(prompt='Summarize the following conversation:\n\n' + DYNAMICMEMORY)


def execute_python_code(code):
    exec_globals = {}
    captured_output = ""
    try:
        with contextlib.redirect_stdout(io.StringIO()) as new_stdout:
            exec(code, exec_globals)
        captured_output = new_stdout.getvalue()
        return f"{RED}{captured_output}{RESET}", exec_globals
    except Exception as e:
        return str(e), None

def get_current_filename():
    return os.path.basename(__file__)

print("The name of this file is:", get_current_filename())

def write_to_dynamic_memory(content):
    with open("DYNAMICMEMORY.txt", "a") as f:
        f.write(content[0] + "\n") 

# Read the content of jaw.py into a string
with open("modified_user_python_script_v4.py", "r") as f:
    file_content = f.read()

# Summarize the content
summary_response, _, _ = general_api_call("Summarize the following: " + file_content, extract_code=False, dialogues=None)

# Write the summary to the dynamic memory file
write_to_dynamic_memory(summary_response)

with open("modified_user_python_script_v10.py", "r") as f:
    first_prompt = f.read()
# print(first_prompt)

first_response, execution_output, exec_globals = general_api_call(first_prompt, extract_code=True)
print(f"First Response: {first_response}")
print(f"Execution Output: {execution_output}")
print(f"Execution Globals: {exec_globals}")

# Loop for n times
n = 2
first_prompt = first_response
"""Recursion Time!""" 
for i in range(n):
    # Extract code from the previous response and execute it
    code_match = re.search(r'```python(.*?)```', first_prompt, re.DOTALL)
    if code_match:
        executable_code = code_match.group(1).strip()
        code_output, _ = execute_python_code(executable_code)
    else:
        code_output = "No executable code found in the previous response."
    
    print(f"Code Output: {code_output}")

    # Use the code output and previous response as input for the next API call
    new_prompt = f"Previous Response: {first_prompt}\nCode Output: {code_output}"
    
    # Append the API key, model engine, and your constant to the new prompt
    
    new_prompt += f"Consider that we have been doing the following:\n{DYNAMICMEMORY}"
    new_prompt += f"\nPlease use the following API Key for OpenAI API calls: {API_KEY}"
    new_prompt += f"\nThe model engine to use is: {MODEL_ENGINE}"
    new_prompt += f"\n{CONSTANT}"  # Append the constant
    
    response, _, _ = general_api_call(new_prompt, extract_code=True)
    print(f"Iteration {i+1} - New Prompt: {new_prompt}\nResponse: {response}\n")
    
    # Update the prompt for the next iteration
    first_prompt = response


