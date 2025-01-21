import sys
import asyncio
import argparse

from dotenv import load_dotenv

from llama_index.utils.workflow import draw_all_possible_flows
from llama_index.llms.openai import OpenAI

from workflow import PresenterWorkflow
from agents.video_creator import PresenterVideoCreaterWorkflow


async def main():
    load_dotenv()
    parser = argparse.ArgumentParser(
        description="Presenter - Create beautiful presentations using AI.",
        usage="python run.py <topic> [--export-video] [-h]",
    )
    parser.add_argument("topic", type=str, help="The topic of the presentation")
    parser.add_argument(
        "--export-video",
        action="store_true",
        help="Export a video of the presentation with voiceover",
    )
    args = parser.parse_args()
    llm = OpenAI(model="gpt-4o-mini")
    workflow = PresenterWorkflow(llm=llm, verbose=False, timeout=240.0)
    # draw_all_possible_flows(workflow, filename="workflow.html")
    topic = args.topic
    presentation_dir = await workflow.run(query=topic)
    video_creator_workflow = PresenterVideoCreaterWorkflow(
        model="eleven_flash_v2_5",
        voice="9BWtsMINqrJLrRacOk9x",
        verbose=False,
        timeout=240.0,
    )
    if args.export_video:
        print("\n> Exporting video of the presentation with voiceover...\n")
        await video_creator_workflow.run(presentation_dir=presentation_dir)


if __name__ == "__main__":
    asyncio.run(main())
