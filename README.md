# LLamaIndex Tour Planner

In this tutorial, we'll create a tour planner using LlamaIndex Workflow.

Stack Used:

- LlamaIndex workflow for orchestration.
- SerpAPI for finding hotels, flights and places to visit

Full tutorial 👇

[![LlamaIndex Tour Planner](https://img.youtube.com/vi/DJOJ4WD1XgY/maxresdefault.jpg)](https://www.youtube.com/watch?v=DJOJ4WD1XgY)

## How to use

- Clone the repo

```bash
git clone https://github.com/rsrohan99/llamaindex-trip-planner.git
cd llamaindex-trip-planner
```

- Install dependencies

```bash
pip install -r requirements.txt
```

- Create `.env` file and add `OPENAI_API_KEY` and `SERPAPI_KEY`

```bash
cp .env.example .env
```

- Run the workflow with the topic to research

```bash
python run.py "plan a trip to bali from paris next month"
```
