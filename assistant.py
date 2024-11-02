# agent.py
import ast
import re

from loguru import logger
import os
import openai

from tools.search import search
from utils.llm import invoke_local_llm, invoke_llm_, invoke_llm

# Import the tools
from tools import (
    get_lib,
    open_webpage,
    call_api,
    execute_cli_command,
    get_user_input,
    output_information,
    read_file
)

logger.remove()
logger.add("log/run.log", rotation="10 MB", retention="10 days", compression="zip")

class Agent:
    def __init__(self):
        self.conversation_history = []
        self.system_prompt = """
You are an AI assistant helping users manage a project called arXiv Sentinel.
This project consists of a serverless function deployed on Vercel, which can regularly download papers from a specified topic on arXiv, summarize the papers using LLM, and generate a report for the user.
You need to obtain the user's intention, plan independently, and help the user complete the task.

Example 01:
The high level process of deploying this project:
    Step01, Basic information acquisition:
    The user needs to register a Vercel Account
    In order to send emails, the user needs to obtain the App password from Google
    In order to use LLM, the user needs to have an OpenAI API Key
    In order to download papers, the user needs to set an arXiv topic.
    
    Step02, Basic information acquisition:
    After the user has completed the acquisition of this information, you need to collect these information.
    
    Step03, Configure vercel environment variables:
    EMAIL_ADDRESS="send_from_email_address"
    EMAIL_PASSWORD="google_app_password"
    OPENAI_API_KEY="your_opanai_API_key"
    PAPER_TOPIC="arXiv_topic"
    TARGET_ADDRESS="email_address_to_get_report"
    
    Step04, Deploy function in the cloud

Example 02:
    Action: OpenWebpage(url='arxiv.org')
    Action: OutputInformation(info='I already help you open the arXiv website, now you can find all topics')
    Action: GetUserInput(prompt='Please provide me with the arXiv topic you like')

Example 03:
    Action: ExecuteCLICommand(command='vercel env pull')
    Action: ReadFile(command='.env.local')
    Action: OutputInformation(info='Vercel env variables: {.env.local content}')

Note that this is not a fixed step, you need to understand it according to the task.

You can take actions in the following format:

Action: ActionName(param1='value1', param2='value2')

Available Actions:
- OpenWebpage(url='...')
- CallAPI(url='...', params={...})
- ExecuteCLICommand(command='...')
- GetUserInput(prompt='...')
- OutputInformation(info='...')
- ReadFile(file_path='...')
- Search(query='...', cse_id='...', api_key='...')
- QUIT 

Note, To ensure success: 
    1. Respond only with actions, and do not include any additional text.
    2. Respond only one action at a time
    
"""
        self.conversation_history.append({
            "role": "system",
            "content": self.system_prompt
        })

        self.conversation_history.append({
            "role": "system",
            "content": f"knowledge base: \n\n{get_lib()}"
        })

        self.conversation_history.append({
            "role": "system",
            "content": "You can't execute actions directly. You need to first collect user needs and then perform tasks based on the needs."
        })

    def get_llm_response(self, prompt=""):
        if prompt == "":
            # Add the user's input to the conversation
            self.conversation_history.append({
                "role": "user",
                "content": prompt
            })

        # assistant_reply = invoke_local_llm(self.conversation_history)
        assistant_reply = invoke_llm_(self.conversation_history)

        # Update conversation history
        self.conversation_history.append({
            "role": "assistant",
            "content": assistant_reply
        })

        logger.info(f"LLM response: {assistant_reply}")

        return assistant_reply

    def parse_actions(self, assistant_reply):
        """
        Parses the assistant's reply to extract actions.
        Assumes each action is on a new line starting with 'Action:'.
        """
        actions = []
        lines = assistant_reply.strip().split('\n')
        for line in lines:
            if line.startswith("Action:"):
                logger.info(f"Action: {line}")
                action_line = line[len("Action:"):].strip()
                actions.append(action_line)
                # print(f"{action_line}")
        return actions

    def execute_action(self, action_str) -> str:

        # print(f"Execute action: {action_str}")
        logger.info(f"Execute action: {action_str}")


        err = ""

        try:
            if action_str == "GetLib":
                self.conversation_history.append({
                    "role": "system",
                    "content": get_lib()
                })

            elif action_str.startswith("OpenWebpage"):
                # Extract URL
                params = self.extract_params(action_str)
                url = params.get('url')
                if url:
                    open_webpage(url)
                else:
                    err = "URL parameter missing in OpenWebpage action."

            elif action_str.startswith("CallAPI"):
                params = self.extract_params(action_str)
                url = params.get('url')
                api_params = params.get('params', {})
                if url:
                    response = call_api(url, params=api_params)
                    print(f"API Response: {response}")

                    self.conversation_history.append({
                        "role": "user",
                        "content": f"API response: \n\n{response}"
                    })
                else:
                    err = "URL parameter missing in CallAPI action."

            elif action_str.startswith("ExecuteCLICommand"):
                params = self.extract_params(action_str)
                command = params.get('command')
                if command:
                    execute_cli_command(command)
                else:
                    err = "Command parameter missing in ExecuteCLICommand action."

            elif action_str.startswith("GetUserInput"):

                params = self.extract_params(action_str)

                prompt = params.get('prompt')
                # print(prompt)

                if prompt is None or prompt == '':
                    err = "Prompt parameter missing in GetUserInput action."

                user_input = get_user_input(prompt)
                self.conversation_history.append({
                    "role": "user",
                    "content": user_input
                })

            elif action_str.startswith("OutputInformation"):
                params = self.extract_params(action_str)
                info = params.get('info')
                if info:
                    output_information(info)
                else:
                    err = "Info parameter missing in OutputInformation action."

            elif action_str.startswith("ReadFile"):
                params = self.extract_params(action_str)
                file_path = params.get('file_path')
                if file_path:
                    content = read_file(file_path)

                    self.conversation_history.append({
                        "role": "user",
                        "content": f"File content: \n\n{content}"
                    })
                else:
                    err = "File path parameter missing in ReadFile action."

            elif action_str.startswith("Search"):
                params = self.extract_params(action_str)

                query = params.get('query')
                cse_id = params.get('cse_id')
                api_key = params.get('api_key')

                if query:
                    content = search(query, cse_id, api_key)
                    self.conversation_history.append({
                        "role": "user",
                        "content": f"Search result: \n\n{content}"
                    })
                else:
                    err = "Query parameter missing in Search action."

            else:
                err = f"Unknown action: {action_str}"

        except Exception as e:
            err = f"Error executing action '{action_str}': {e}"

        if err!="":
            logger.error(err)
        return err

    import re
    import ast

    def extract_params(self, action_str):
        """
        Extracts parameters from an action string into a dictionary.
        Handles values with special characters and nested structures.
        """
        # Find the first '(' and the last ')'
        start = action_str.find('(')
        end = action_str.rfind(')')
        params_str = action_str[start + 1:end].strip()

        # Regex to match key-value pairs (supports values with '=' and other special chars)
        param_pattern = re.compile(r"(\w+)\s*=\s*(.+?)(?=\s*,\s*\w+\s*=|\s*$)")
        matches = param_pattern.findall(params_str)

        params = {}
        for key, value in matches:
            try:
                # Attempt to parse value as Python literal (e.g., string, dict, list)
                params[key] = ast.literal_eval(value)
            except (ValueError, SyntaxError):
                # If it fails, keep it as a string
                params[key] = value.strip("'\"")

        return params

    # def extract_params(self, action_str):
    #     """
    #     Extracts parameters from an action string into a dictionary.
    #     """
    #     import ast
    #
    #     # Find the first '(' and the last ')'
    #     start = action_str.find('(')
    #     end = action_str.rfind(')')
    #     params_str = action_str[start+1:end]
    #     params_str = params_str.strip()
    #     # print(params_str)
    #
    #     params_str = params_str.split(',')
    #
    #     params = {}
    #     for param in params_str:
    #         param = param.strip()
    #         key, value = param.split('=')
    #         params[key] = value.replace("'","")
    #
    #     return params

    def run(self, prompt=""):
        print("Agent is running.\n")
        while True:
            print("\n====================================================\n")
            assistant_reply = self.get_llm_response()
            if "QUIT" in assistant_reply:
                break

            logger.info(f"Assistant:\n{assistant_reply}\n")

            actions = self.parse_actions(assistant_reply)

            for action in actions:

                output = self.execute_action(action)

                if output != "":
                    self.conversation_history.append({
                        "role": "user",
                        "content": output
                    })
                else:
                    self.conversation_history.append({
                        "role": "user",
                        "content": "Action Executed"
                    })

if __name__ == "__main__":
    agent = Agent()

    print("Welcome to arXiv Sentinel! You can use this AI assistant to help you complete various tasks like:")
    print("Please help me deploy the project.")
    print("Please help me get all existing environment variables in the vercel account.")
    print()
    # prompt = input("What do you want to do today? \n")
    prompt=''
    agent.run(prompt)