import sys
import asyncio
import subprocess

from dotenv import load_dotenv

from llama_index.utils.workflow import draw_all_possible_flows
from llama_index.llms.openai import OpenAI

from workflow import TourPlannerWorkflow


async def main():
    load_dotenv()
    llm = OpenAI(model="gpt-4o-mini")
    workflow = TourPlannerWorkflow(llm=llm, verbose=False, timeout=240.0)
    # draw_all_possible_flows(workflow, filename="workflow.html")
    query = sys.argv[1]
    result = await workflow.run(query=query)
    if ".pdf" in result:
        subprocess.run(["open", result])


if __name__ == "__main__":
    asyncio.run(main())
