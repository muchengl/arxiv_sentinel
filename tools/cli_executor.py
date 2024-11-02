import subprocess


def execute_cli_command(command):
    c = input(f"Executing command: {command} \n(y/n) :")
    if c == "n":
        return "User refused to execute this command"

    try:
        process = subprocess.Popen(command, shell=True, text=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE)

        while True:
            output = process.stdout.readline()
            if output == '' and process.poll() is not None:
                break
            if output:
                print(output.strip())

                if "Enter input" in output:
                    user_input = input("Enter your response: ")
                    process.stdin.write(user_input + "\n")
                    process.stdin.flush()

        stderr_output = process.stderr.read()
        if stderr_output:
            print(f"Command execution failed:\n{stderr_output}")
            return stderr_output

    except subprocess.CalledProcessError as e:
        print(f"Command execution failed:\n{e.stderr}")
        return e.stderr

    return "Command executed successfully."


# # cli_executor.py
#
# import subprocess
#
# def execute_cli_command(command):
#     c = input(f"Executing command: {command}. (y/n)")
#     if c == "n":
#         return "User refused to execute this command"
#
#     try:
#         result = subprocess.run(command, shell=True, check=True, text=True, capture_output=True)
#         print(f"Command Output:\n{result.stdout}")
#         return result.stdout
#     except subprocess.CalledProcessError as e:
#         print(f"Command execution failed:\n{e.stderr}")
#         return e.stderr
