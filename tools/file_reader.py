# file_reader.py

def read_file(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        print(f"Successfully read file: {file_path}")
        return content
    except Exception as e:
        err = f"Failed to read file: {e}"
        print(err)
        return err
