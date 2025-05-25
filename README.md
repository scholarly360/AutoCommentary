# AutoCommentary
AutoCommentary is a Python script that automates the process of adding or updating docstrings for functions and classes within your Python code. It leverages the power of Large Language Models (LLMs) to generate concise and informative summaries, enhancing code readability and maintainability.

# Features
## Automated Docstring Generation: Automatically generates docstrings for Python functions and classes.
## LLM-Powered Summaries: It uses OpenAI's GPT-4o-mini model to create intelligent and relevant docstring content.
## Indentation Detection: Automatically detects the indentation style (tabs or spaces) of your Python files to maintain consistent formatting.
## Existing Docstring Appending: If a function or class already has a docstring, AutoCommentary appends the new generated summary to it.
## Code Formatting (via autopep8): Integrates with autopep8 to ensure your code remains PEP 8 compliant after docstring insertion.

# How to Use
## Prerequisites
Before using AutoCommentary, ensure you have the following:

Python 3.x installed.
An OpenAI API key. Set this as an environment variable or configure it within llm_config.py.
Install the required Python packages:

>> pip install openai autopep8 python-dotenv

# Running AutoCommentary

>> python auto_commentary.py your_script_with_path.py
e.g.
>> python auto_commentary.py 01.py


# Compile and Check for Errors (Optional but Recommended): 
After adding docstrings, it's good practice to compile your script to check for any syntax errors introduced.

>> python -m py_compile your_script_with_path.py
e.g.
>> python -m py_compile 01.py
