from dotenv import load_dotenv # load .env into environment
import os
import re
import openai
from duckduckgo_search import ddg

import requests
from bs4 import BeautifulSoup

load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")

class ChatBot:
    def __init__(self, system=""):
        self.system = system
        self.messages = []
        if self.system:
            self.messages.append({"role": "system", "content": system})

            print("> {}".format(system))
            print()

            result = self.execute()

            print(">> {}".format(result))
            print()
    
    def __call__(self, message):
        self.messages.append({"role": "user", "content": message.strip()})
        print("> {}".format(message.strip()))
        print()

        result = self.execute()

        self.messages.append({"role": "assistant", "content": result})

        print(">> {}".format(result.strip()))
        print()

        return result
    
    def execute(self):
        completion = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=self.messages)

        # Uncomment this to print out token usage each time, e.g.
        # {"completion_tokens": 86, "prompt_tokens": 26, "total_tokens": 112}
        # print(completion.usage)

        if completion.choices[0].finish_reason != "stop":
            return completion.choices[0].finish_reason

        return completion.choices[0].message.content

most_recent_search_results = None

def search_online(args):
    global most_recent_search_results

    most_recent_search_results = ddg(args[0].replace('"', ''), max_results=3)

    if len(most_recent_search_results) == 0:
        return "No results found."

    to_return = ''
    
    for i, result in enumerate(most_recent_search_results):
        to_return += '{}: {} - {} - {}\n'.format(
            i,
            result['title'],
            result['href'],
            result['body']
        )

    return to_return

def read_result(args):
    try:
        search_result = most_recent_search_results[int(args[0])]
        response = requests.get(search_result['href'])

        soup = BeautifulSoup(response.content, 'html.parser')

        page_content = soup.get_text()
        clean_text = " ".join(page_content.split())

        return clean_text
    except ValueError:
        return "ERROR: {} is not an integer".format(args)

def call(args):
    return "call is not yet implemented"


initialPrompt = ''
with open('starting_prompt.md', encoding='utf-8') as f: initialPrompt = f.read()
initialPrompt = str.join(' ', initialPrompt.splitlines())

userMsg = '''
What is the phone number of Seaway Car Wash in Burlington, Vermont?
'''

searchBot = ChatBot(initialPrompt)

resp = searchBot(userMsg)

print(resp)

msg_count = 3

while msg_count != 0:
    match = re.search('/(\w+) (.+)', resp)

    if match:
        cmd_name = match.group(1)
        cmd_args = match.group(2).split(",,")

        print('{} = {}'.format(cmd_name, cmd_args))

        options = {
            "search_online": search_online,
            "read_result": read_result,
            "call": call,
        }

        cmd_result = options[cmd_name](cmd_args)

        print("COMMAND RESULT: {}".format(cmd_result))

        resp = searchBot(cmd_result)

    else:
        user_msg = input("> ")
        resp = searchBot(user_msg)

    msg_count -= 1
