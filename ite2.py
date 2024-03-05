import openai
import re
import io
import contextlib
from termcolor import colored

# Read API Key from external file
def read_api_key(file_path):
    with open(file_path, 'r') as f:
        return f.read().strip()

API_KEY = read_api_key("api_key.txt")
print(f"Debug - API Key: {API_KEY}")  # Debugging line

MODEL_ENGINE = "gpt-4"
GOAL = "The goal is to remain in the realm of Python and create code."
PRINT_STATEMENT_REMINDER = "Please include a print statement in the code that outputs the result."

# Initialize OpenAI API
openai.api_key = API_KEY

# Initialize context
context = ""

def execute_python_code(code):
    captured_output = ""
    try:
        with contextlib.redirect_stdout(io.StringIO()) as new_stdout:
            exec(code)
        captured_output = new_stdout.getvalue()
        return colored(captured_output, 'red'), {}
    except Exception as e:
        return str(e), None

def apiCall(prompt, iteration, max_iterations):
    global context  # Declare context as global to modify it
    if iteration > max_iterations:
        return

    print(f"Starting iteration {iteration}...")

    # Update context
    context += f"\nIteration {iteration} - Previous Prompt: {prompt}"
    new_prompt = f"{prompt}\n{PRINT_STATEMENT_REMINDER}"
    response = openai.ChatCompletion.create(
        model=MODEL_ENGINE,
        messages=[
            {'role': 'system', 'content': f'{GOAL}\n{context}'},
            {'role': 'user', 'content': new_prompt}
        ],
        max_tokens=1500
    )
    full_response = response['choices'][0]['message']['content']

    # Extract code enclosed in triple quotes
    code_match = re.search(r'```python(.*?)```', full_response, re.DOTALL)
    execution_output, _ = "", {}
    if code_match:
        executable_code = code_match.group(1).strip()
        execution_output, _ = execute_python_code(executable_code)

    print(f"Iteration {iteration} - API Response: {full_response}")
    print(f"Execution Output: {execution_output}")

    print(f"Ending iteration {iteration}...\n")

    # Recursive call
    apiCall(full_response, iteration + 1, max_iterations)

if __name__ == "__main__":
    initial_prompt = "Initial prompt for API call"
    apiCall(initial_prompt, 1, 3)
