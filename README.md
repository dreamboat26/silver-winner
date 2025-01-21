# LLamaIndex Tour Planner

We'll create a tour planner using LlamaIndex Workflow.

Stack Used:

- LlamaIndex workflow for orchestration.
- SerpAPI for finding hotels, flights and places to visit

![LlamaIndex Tour Planner](https://img.youtube.com/vi/DJOJ4WD1XgY/maxresdefault.jpg)

## How to use

- Clone the repo

```bash
git clone https://github.com/dreamboat26/silver-winner.git
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
