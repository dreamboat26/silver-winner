We'll use LlamaIndex Instrumentation module to send intermediate steps in a RAG pipeline to the frontend for an intuitive user experience.

![Stream Intermediate events in RAG](https://img.youtube.com/vi/JOM8WgmNCvI/maxresdefault.jpg)

We use Server-Sent Events which will be recieved by Vercel AI SDK on the frontend.

## Getting Started

First clone the repo:

```bash
git clone https://github.com/dreamboat26/silver-winner.git

cd rag-stream-intermediate-events-tutorial
```

## Start the Backend

`cd` into the `backend` directory

```bash
cd backend
```

### First create `.env` from `.env.example`

```bash
cp .env.example .env
```

### Set the OpenAI key in .env

```bash
OPENAI_API_KEY=****
```

### Install the dependencies

```bash
poetry install
```

### Generate the Index for the first time

```bash
poetry run python app/engine/generate.py
```

### Start the backend server

```bash
poetry run python main.py
```

## Start the Frontend

`cd` into the `frontend` directory

```bash
cd frontend
```

### First create `.env` from `.env.example`

```bash
cp .env.example .env
```

### Install the dependencies

```bash
npm i
```

### Start the frontend server

```bash
npm run dev
```
