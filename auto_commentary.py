"""


How to use :: 
python auto_commentary.py python script_with_path.py
python -m py_compile script_with_path.py

e.g.

python auto_commentary.py 01.py
python -m py_compile 01.py

First command will add docstrings to the functions and classes in the specified Python script.
Second command will compile the script to check for syntax errors after adding docstrings.



"""
import ast
import argparse
import os
import sys
from typing import List, Tuple
import autopep8
from llm_config import *
import itertools


def detect_indentation(filepath):
    """
    Detects the indentation style used in a Python file.

    Args:
        filepath (str): The path to the Python file.

    Returns:
        str: A description of the indentation style (e.g., "Tabs", "4 spaces",
             "Mixed spaces and tabs", "No consistent indentation found",
             "File not found", "Error reading file").
    """
    if not os.path.exists(filepath):
        return "File not found."

    indentation_type = None  # Can be 'tabs', 'spaces', or 'mixed'
    space_count = None       # Stores the number of spaces if 'spaces' is detected

    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                # Skip empty lines or lines with only whitespace
                if not line.strip():
                    continue

                # Find the leading whitespace
                leading_whitespace = ""
                for char in line:
                    if char == ' ' or char == '\t':
                        leading_whitespace += char
                    else:
                        break

                # If the line has no leading whitespace, it's not useful for detection
                if not leading_whitespace:
                    continue

                # Check for tabs
                if '\t' in leading_whitespace:
                    if indentation_type == 'spaces':
                        return "Mixed spaces and tabs detected."
                    indentation_type = 'tabs'
                # Check for spaces
                elif ' ' in leading_whitespace:
                    if indentation_type == 'tabs':
                        return "Mixed spaces and tabs detected."
                    indentation_type = 'spaces'

                    current_space_count = len(leading_whitespace)

                    # If this is the first indentation we've seen, set the count
                    if space_count is None:
                        space_count = current_space_count
                    # If we've seen indentation before, check for consistency
                    elif current_space_count > 0: # Only compare if there's actual indentation
                        # If the current space count is not a multiple of the initial count,
                        # or if it's not the same as the initial count for the first level,
                        # it might indicate inconsistent spacing.
                        # A common pattern is 2 or 4 spaces.
                        # This logic tries to infer the base unit.
                        if current_space_count % space_count != 0 and current_space_count != space_count:
                             # This is a heuristic; more advanced detection might be needed for complex cases
                             # For simplicity, if a new non-zero space count doesn't align, we flag it.
                            pass # Keep the current space_count, but allow for deeper indentation
                        elif current_space_count < space_count:
                            # If a line indents less than the established `space_count`
                            # but still uses spaces, it suggests `space_count` might be too high
                            # or there's inconsistency. Let's assume the smallest non-zero
                            # indentation unit found is the base.
                            space_count = min(space_count, current_space_count)
                        elif space_count == 0 and current_space_count > 0:
                            space_count = current_space_count

    except Exception as e:
        return f"Error reading file: {e}"

    if indentation_type == 'tabs':
        return "\t"
    elif indentation_type == 'spaces':
        if space_count is not None and space_count > 0:
            return ' ' * space_count
        else:
            return "Spaces are used for indentation, but the exact count could not be determined (possibly no indented lines)."
    else:
        return "No consistent indentation found (or file is empty/has no indented lines)."

# def find_shortest_string(strings):
#     if not strings:
#         return None
#     shortest = min(strings, key=len)
#     return shortest

# def get_indentation_sequence(file_path):
#     tmp_indentations = []
#     with open(file_path, 'r') as file:
#         for line_number, line in enumerate(file, start=1):
#             # Extract leading whitespace characters
#             indentation = ''.join(itertools.takewhile(str.isspace, line))
#             tmp_indentations.append(indentation)
#             print(f"Line {line_number}: Indentation sequence = {repr(indentation)}")
#     tmp_indentations = list(set(tmp_indentations))  # Remove duplicates
#     tmp_indentations.remove('')  # Remove empty strings if any
#     tmp_indentations.remove('\n') 
#     final_value = find_shortest_string(tmp_indentations)
#     return find_shortest_string(final_value)
    
def extract_definitions(source_code: str) -> List[Tuple[str, ast.AST]]:
    """
    Parses the source code and extracts all function and class definitions.
    Returns a list of tuples containing the type ('function' or 'class') and the AST node.
    """
    tree = ast.parse(source_code)
    definitions = []
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            definitions.append(('function', node))
        elif isinstance(node, ast.ClassDef):
            definitions.append(('class', node))
    return definitions

def generate_docstring(def_type: str, node: ast.AST) -> str:
    """
    Generates a docstring for the given function or class node.
    """
    print(f"Generating docstring  {node}")
    if def_type == 'function':
        func_node: ast.FunctionDef = node
        args = [arg.arg for arg in func_node.args.args]
        docstring = "\nDescription: " + str(llm_generate_summary(str(ast.unparse(node)))) + "\n"
    elif def_type == 'class':
        docstring = "\nDescription: " + str(llm_generate_summary(str(ast.unparse(node)))) + "\n"
    else:
        docstring = "\nDescription: " + str(llm_generate_summary(str(ast.unparse(node)))) + "\n"
    return docstring

def insert_docstrings(source_lines, definitions, ind_char):
    """
    Inserts or appends generated docstrings into the source code lines at appropriate positions,
    ensuring a blank line follows each docstring.
    """
    definitions_sorted = sorted(definitions, key=lambda x: x[1].lineno, reverse=True)
    for def_type, node in definitions_sorted:
        lineno = node.lineno - 1  # Convert to 0-based index
        indent = ' ' * (len(source_lines[lineno]) - len(source_lines[lineno].lstrip()))
        docstring = generate_docstring(def_type, node)
        insertion_point = lineno + 1
        if (insertion_point < len(source_lines)) and (source_lines[insertion_point].strip().startswith('"""')):
            # Append to existing docstring
            end_line = insertion_point
            while end_line < len(source_lines):
                if source_lines[end_line].strip().endswith('"""'):
                    break
                end_line += 1
            # Remove the closing triple quotes
            source_lines[end_line] = source_lines[end_line].rstrip().rstrip('"""')
            # Append the new docstring content
            source_lines[end_line] += docstring + '\n' + indent + '"""' + '\n'
            # Ensure a blank line after the docstring
            if end_line + 1 < len(source_lines) and source_lines[end_line + 1].strip() != '':
                source_lines.insert(end_line + 1, '\n')
        else:
            # Insert new docstring
            docstring_lines = [indent + line for line in (ind_char+'"""' + docstring + '"""').split('\n')]
            source_lines[insertion_point:insertion_point] = docstring_lines + ['\n']
    return source_lines


# def process_file(file_path: str):
#     """
#     Reads the Python file, inserts or appends docstrings, and writes back to the file.
#     """
#     with open(file_path, 'r', encoding='utf-8') as f:
#         source_lines = f.readlines()
#     source_code = ''.join(source_lines)
#     definitions = extract_definitions(source_code)
#     if not definitions:
#         print(f"No functions or classes found in {file_path}.")
#         return
#     updated_lines = insert_docstrings(source_lines, definitions)
#     with open(file_path, 'w', encoding='utf-8') as f:
#         f.writelines(updated_lines)
#     print(f"Docstrings updated in {file_path}.")




def process_and_indent_file(file_path, ind_char):
    """
    Reads the Python file, inserts or appends docstrings, formats the code,
    and writes back to the file.
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        source_lines = f.readlines()
    source_code = ''.join(source_lines)
    definitions = extract_definitions(source_code)
    if not definitions:
        print(f"No functions or classes found in {file_path}.")
        return
    updated_lines = insert_docstrings(source_lines, definitions, ind_char)
    updated_code = ''.join(updated_lines)
    # Apply autopep8 formatting
    formatted_code = updated_code
    #formatted_code = autopep8.fix_code(updated_code, options={'aggressive': 2})
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(formatted_code)
    print(f"Docstrings updated and code formatted in {file_path}.")

def main():
    parser = argparse.ArgumentParser(description='Automatically add or append docstrings to Python functions and classes.')
    parser.add_argument('file', help='Path to the Python file to process.')
    args = parser.parse_args()
    if not os.path.isfile(args.file):
        print(f"Error: File '{args.file}' does not exist.")
        sys.exit(1)
    ind_char = detect_indentation(args.file)
    #print(ind_char)
    process_and_indent_file(args.file, ind_char)
    #process_and_indent_file(args.file)

if __name__ == '__main__':
    main()
