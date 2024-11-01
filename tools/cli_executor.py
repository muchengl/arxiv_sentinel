# cli_executor.py

import subprocess

def execute_cli_command(command):
    try:
        result = subprocess.run(command, shell=True, check=True, text=True, capture_output=True)
        print(f"Command Output:\n{result.stdout}")
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"Command execution failed:\n{e.stderr}")
        return e.stderr
