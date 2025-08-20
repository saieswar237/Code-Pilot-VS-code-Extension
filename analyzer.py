#
# Code-Pilot: The Real-Time Coding Mentor
# Smarter Brain Version: Now detects empty if/else blocks!
#

import ast
import sys
import json

def analyze_code_line(code_line):
    """
    Analyzes a single line of Python code for common beginner errors.
    """
    code_to_parse = code_line
    stripped_line = code_line.strip()
    keywords_needing_body = ('if ', 'for ', 'while ', 'def ', 'class ', 'else:')
    
    if stripped_line.endswith(':') and stripped_line.startswith(keywords_needing_body):
        code_to_parse = code_line + "\n    pass"

    try:
        tree = ast.parse(code_to_parse)
        for node in ast.walk(tree):
            # --- RULE 1: Assignment in 'if' ---
            if isinstance(node, ast.If):
                if isinstance(node.test, ast.Assign):
                    return (
                        "Mistake found! Are you trying to compare a value? "
                        "To check for equality, use '==' (double equals). "
                        "A single '=' is only for assigning values."
                    )
            
            # --- RULE 2: len() on a number ---
            if isinstance(node, ast.Call):
                if hasattr(node.func, 'id') and node.func.id == 'len':
                    if node.args:
                        first_arg = node.args[0]
                        if isinstance(first_arg, ast.Constant) and isinstance(first_arg.value, (int, float)):
                            return (
                                "Learning opportunity! The 'len()' function is for things that have a length, "
                                "like strings or lists. Numbers don't have a length."
                            )
            
            # --- NEW RULE 4: Empty 'if' or 'else' block ---
            # This checks if an 'if' or 'else' block contains only a 'pass' statement,
            # which is what our temporary code does. This means the original was empty.
            if isinstance(node, ast.If):
                # Check the 'if' body
                if len(node.body) == 1 and isinstance(node.body[0], ast.Pass):
                     return "Learning opportunity! This 'if' statement is empty. Make sure to add some code inside it."
                # Check the 'else' body (if it exists)
                if node.orelse and len(node.orelse) == 1 and isinstance(node.orelse[0], ast.Pass):
                    # This rule will trigger on an 'else:' line if it's empty
                    if 'else' in code_line:
                        return "Learning opportunity! This 'else' block is empty. Make sure to add some code inside it."


    except SyntaxError as e:
        if "Maybe you meant '==' or ':=' instead of '='" in str(e):
             return (
                "Mistake found! Are you trying to compare a value? "
                "To check for equality, use '==' (double equals). "
                "A single '=' is only for assigning values."
            )
        # --- RULE 3: Missing colon ---
        if "expected ':'" in str(e):
            return (
                "It looks like you're missing a colon ':' at the end of the line. "
                "Lines that start with 'if', 'for', 'while', 'def', or 'class' almost always need a colon!"
            )
        return None
    return None

# --- Main part of the script ---
if __name__ == "__main__":
    if len(sys.argv) > 1:
        full_code = sys.argv[1]
    else:
        full_code = ""
    
    lines = full_code.splitlines()
    all_errors = []

    for idx, line in enumerate(lines):
        if not line.strip():
            continue
            
        error_message = analyze_code_line(line)
        
        if error_message:
            error_info = {
                "line": idx,
                "message": error_message
            }
            all_errors.append(error_info)
            
    print(json.dumps(all_errors))
