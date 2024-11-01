# agent.py

import os
import openai

# Import the tools
from tools import (
    lib,
    open_webpage,
    call_api,
    execute_cli_command,
    get_user_input,
    output_information,
    read_file
)

# Set up OpenAI API key
# openai.api_key = 'your-api-key'  # Replace with your OpenAI API key


class Agent:
    def __init__(self):
        self.conversation_history = []
        self.system_prompt = """
You are an LLM Agent helping users manage a project called arXiv Sentinel.
This project consists of a serverless function deployed on Vercel, which can regularly download papers from a specified topic on arXiv, summarize the papers using LLM, and generate a report for the user.
You need to obtain the user's intention, plan independently, and help the user complete the task.

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
    
    Step04, Local test vercel function
    
    Step05, Deploy function in the cloud


Note that this is not a fixed step, you need to understand it according to the task.

You can take actions in the following format:

Action: ActionName(param1='value1', param2='value2')

Available Actions:
- GetLib(), Get the help information library, which contains predefined necessary information
- OpenWebpage(url='...')
- CallAPI(url='...', params={...})
- ExecuteCLICommand(command='...')
- GetUserInput(prompt='...')
- OutputInformation(info='...')
- ReadFile(file_path='...')

Example 01:
Action: OpenWebpage(url='arxiv.org')
Action: OutputInformation(info='I already help you open the arXiv website')
Action: GetUserInput(prompt='Please provide me with the arXiv topic you like')

Example 02:
Action: ExecuteCLICommand(command='vercel env pull')
Action: ReadFile(command='.env.local')
Action: OutputInformation(info='Vercel env variables: {.env.local content}')

Note: 
Respond only with actions, and do not include any additional text.
"""
        self.conversation_history.append({"role": "system", "content": self.system_prompt})

    def get_llm_response(self, prompt):
        # Add the user's input to the conversation
        self.conversation_history.append({"role": "user", "content": prompt})

        # Get response from the LLM
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=self.conversation_history
        )

        # Extract the assistant's reply
        assistant_reply = response['choices'][0]['message']['content']

        # Update conversation history
        self.conversation_history.append({"role": "assistant", "content": assistant_reply})

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
                action_line = line[len("Action:"):].strip()
                actions.append(action_line)
        return actions

    def execute_action(self, action_str):
        """
        Executes the given action string by mapping it to the appropriate tool.
        """
        try:
            if action_str.startswith("OpenWebpage"):
                # Extract URL
                params = self.extract_params(action_str)
                url = params.get('url')
                if url:
                    open_webpage(url)
                else:
                    print("URL parameter missing in OpenWebpage action.")
            elif action_str.startswith("CallAPI"):
                params = self.extract_params(action_str)
                url = params.get('url')
                api_params = params.get('params', {})
                if url:
                    response = call_api(url, params=api_params)
                    print(f"API Response: {response}")
                else:
                    print("URL parameter missing in CallAPI action.")
            elif action_str.startswith("ExecuteCLICommand"):
                params = self.extract_params(action_str)
                command = params.get('command')
                if command:
                    execute_cli_command(command)
                else:
                    print("Command parameter missing in ExecuteCLICommand action.")
            elif action_str.startswith("GetUserInput"):
                params = self.extract_params(action_str)
                prompt = params.get('prompt', "Please enter input: ")
                user_input = get_user_input(prompt)
                # Optionally, you can send the user input back to the LLM or store it
            elif action_str.startswith("OutputInformation"):
                params = self.extract_params(action_str)
                info = params.get('info')
                if info:
                    output_information(info)
                else:
                    print("Info parameter missing in OutputInformation action.")
            elif action_str.startswith("ReadFile"):
                params = self.extract_params(action_str)
                file_path = params.get('file_path')
                if file_path:
                    content = read_file(file_path)
                    # Optionally, you can send the content back to the LLM or process it
                else:
                    print("File path parameter missing in ReadFile action.")
            else:
                print(f"Unknown action: {action_str}")
        except Exception as e:
            print(f"Error executing action '{action_str}': {e}")

    def extract_params(self, action_str):
        """
        Extracts parameters from an action string into a dictionary.
        """
        import ast

        # Find the first '(' and the last ')'
        start = action_str.find('(')
        end = action_str.rfind(')')
        params_str = action_str[start+1:end]
        params_str = params_str.strip()

        # Convert the parameters string into a dictionary
        params = {}
        if params_str:
            try:
                # Safely evaluate the parameters string
                params = ast.literal_eval(f"dict({params_str})")
            except Exception as e:
                print(f"Error parsing parameters: {e}")
        return params

    def run(self):
        print("Agent is running. Type 'exit' to quit.\n")
        while True:
            user_input = input("User: ")
            if user_input.lower() == 'exit':
                break

            # Get response from LLM
            assistant_reply = self.get_llm_response(user_input)
            print(f"Assistant:\n{assistant_reply}\n")

            # Parse actions from assistant's reply
            actions = self.parse_actions(assistant_reply)

            # Execute actions
            for action in actions:
                self.execute_action(action)

# Main execution
if __name__ == "__main__":
    agent = Agent()
    agent.run()