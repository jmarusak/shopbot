import os
import asyncio
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
    description: str

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

# Read LLM prompt from file
with open('prompt_jobs.txt', 'r') as file:
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
            print(job.description)
            print()
    else:
        print("No result found.")
    
    input('Press Enter to close the browser...')
    await browser.close()

if __name__ == '__main__':
    asyncio.run(main())
