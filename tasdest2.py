
import openai
import subprocess
import re
import io
import sys
import contextlib
from Sep5thStart.config2 import RED, RESET, API_KEY, MODEL_ENGINE, CONSTANT

print(f"Debug - API Key: {API_KEY}")  # Debugging line

# Initialize OpenAI API
openai.api_key = API_KEY

# Initialize exec_globals
exec_globals = {}

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

def apiCall(prompt):
    model_engine = MODEL_ENGINE  # Replace with the actual GPT-4 engine ID when available
    response = openai.ChatCompletion.create(
        model=model_engine,
        messages=[
            {'role': 'system', 'content': '''You are a helpful assistant focused on generating Python code and making API calls.
            You have the ability to output code that will be run by the user, please output the code and the user will run it. PLease suggest and implement changes.'''},
            {'role': 'user', 'content': first_prompt}
        ],
        max_tokens=1500
    )
    full_response = response['choices'][0]['message']['content']
    print(f"Debug - Full Response: {full_response}") 

    # Extract code enclosed in triple quotes
    code_match = re.search(r'"""(.*?)"""', full_response, re.DOTALL)
    execution_output, exec_globals = "", {}
    if code_match:
        executable_code = code_match.group(1).strip()
        # Execute the code using your function
        execution_output, exec_globals = execute_python_code(executable_code)
        
    return full_response, execution_output, exec_globals  # Return the full response along with the execution output and globals

dialogues=''
def dynamicMemory(prompt):
    "summaryOfPreviousDialogues via a new API call"
    
    model_engine = MODEL_ENGINE  # Replace with the actual GPT-4 engine ID when available
    response = openai.ChatCompletion.create(
        model=model_engine,
        messages=[
            {'role': 'system', 'content': 'Please summarize the following dialogues?'},
            {'role': 'user', 'content': dialogues}
        ],
        max_tokens=1500
    )
    dynamicMemoryDialogue = response['choices'][0]['message']['content']
    print(f"Debug - Full Response: {dynamicMemoryDialogue}") 



# First API call
first_prompt = """Please consider the following:"""
#additional text goes here:
first_prompt += f"""\nPlease use the following API Key for OpenAI API calls: 
{API_KEY}\nThe model engine to use is: {MODEL_ENGINE}"""


with open("Sep5thStart/tasdest2.py", "r") as f:
    first_prompt = f.read()
# print(first_prompt)

first_response, execution_output, exec_globals = apiCall(first_prompt)
print(f"First Response: {first_response}")
print(f"Execution Output: {execution_output}")
print(f"Execution Globals: {exec_globals}")

# Loop for n times
n = 2
first_prompt = first_response
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
    new_prompt += f"\nPlease use the following API Key for OpenAI API calls: {API_KEY}"
    new_prompt += f"\nThe model engine to use is: {MODEL_ENGINE}"
    new_prompt += f"\n{CONSTANT}"  # Append the constant
    
    response, _, _ = apiCall(new_prompt)
    print(f"Iteration {i+1} - New Prompt: {new_prompt}\nResponse: {response}\n")
    
    # Update the prompt for the next iteration
    prompt = response



