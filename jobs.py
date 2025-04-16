import os
import asyncio
import sys
from typing import List

from browser_use import Agent, Browser, BrowserConfig, Controller
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from pydantic import BaseModel, SecretStr

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise ValueError("GEMINI_API_KEY environment variable not set.")

class Job(BaseModel):
    title: str

class Jobs(BaseModel):
    jobs: List[Job]

controler = Controller(output_model=Jobs)

# Configure the browser to connect to your Chrome instance
browser = Browser(
    config=BrowserConfig(
        chrome_instance_path= '/usr/bin/google-chrome'
    ),
)

# Initialize the model
llm = ChatGoogleGenerativeAI(model='gemini-2.0-flash', api_key=SecretStr(api_key))

# Read LLM prompt from file, use default if not provided
prompt_file = sys.argv[1] if len(sys.argv) > 1 else 'prompt_jobs.txt'
with open(prompt_file, 'r') as file:
    prompt = file.read()

# Create agent with the model
agent = Agent(
    task=prompt,
    llm=llm,
    browser=browser,
    controller=controler,
)

async def main():
    print("Agent is exploring the website...")
    
    history = await agent.run()
    
    result = history.final_result()

    if result:
        parsed: Jobs = Jobs.model_validate_json(result)

        for job in parsed.jobs:
            print(job.title)
            print()
    else:
        print("No result found.")
    
    input('Press Enter to close the browser...')
    await browser.close()

if __name__ == '__main__':
    asyncio.run(main())
