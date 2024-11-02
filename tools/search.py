import os
from langchain_core.tools import Tool
from langchain_google_community import GoogleSearchAPIWrapper

search = GoogleSearchAPIWrapper()

tool = Tool(
    name="google_search",
    description="Search Google for recent results.",
    func=search.run,
)

def search(query, cse_id, api_key):
    c = input(f"Google Search: {query} help\n(y/n)")
    if c == "n":
        return "User refused to search"

    os.environ["GOOGLE_CSE_ID"] = cse_id
    os.environ["GOOGLE_API_KEY"] = api_key

    try:
        result = tool.run(query)
    except Exception as e:
        print(e)
        return e

    return str(result)

if __name__ == '__main__':
    print(search("Obama's first name?"))
