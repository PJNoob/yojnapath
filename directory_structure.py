import os

def print_directory_structure(start_path, indent_level=0, excluded_dirs=None):
    """
    Recursively prints the directory structure starting from start_path,
    excluding specified directories.
    """
    if excluded_dirs is None:
        excluded_dirs = {"__pycache__", "env", "assets", "recordings",".git"}

    try:
        items = os.listdir(start_path)
    except PermissionError:
        print(" " * indent_level + "[Permission Denied]")
        return

    for item in items:
        item_path = os.path.join(start_path, item)

        # Skip excluded directories
        if os.path.isdir(item_path) and item in excluded_dirs:
            continue

        # Print the item with indentation
        print(" " * indent_level + "|-- " + item)

        # If the item is a directory, recursively print its structure
        if os.path.isdir(item_path):
            print_directory_structure(item_path, indent_level + 4, excluded_dirs)

# Specify the starting path (current directory by default)
start_directory = "."
print(f"Directory structure of: {os.path.abspath(start_directory)}")
print_directory_structure(start_directory)
