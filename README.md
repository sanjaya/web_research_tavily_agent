# Web Research Agent (LangChain + Tavily)

A simple command-line agent that answers **one** research question using live web
search. You ask a question; the agent searches the web with Tavily, writes a
concise answer with sources, prints it, and exits.

## How it works

```
question ──► LLM (via OpenRouter) ──► tavily_search ──► results
                 ▲                                        │
                 └──────── searches again if needed ◄─────┘
                 │
                 └──► final answer + "Sources" list of URLs
```

- **Model:** any chat model on [OpenRouter](https://openrouter.ai), called through
  LangChain's `ChatOpenAI` (OpenRouter uses an OpenAI-compatible API).
- **Search tool:** `TavilySearch` from `langchain-tavily`, returning the top 5 results.
- **Agent loop:** LangChain's `create_agent` lets the model decide when to search
  and when it has enough to answer.
- **One-shot:** each run handles a single question. There is no chat history or
  follow-up.

## Requirements

- Python 3.10+
- An [OpenRouter API key](https://openrouter.ai/keys)
- A [Tavily API key](https://app.tavily.com)

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Then fill in `.env`:

```env
OPENROUTER_API_KEY=your_openrouter_key
LLM_MODEL=openai/gpt-4o-mini        # any OpenRouter model ID that supports tool calling
TAVILY_API_KEY=your_tavily_key
```

| Variable | Purpose |
|---|---|
| `OPENROUTER_API_KEY` | Authenticates with OpenRouter |
| `LLM_MODEL` | OpenRouter model ID; it must support tool/function calling |
| `TAVILY_API_KEY` | Authenticates with Tavily search |

If any of these is missing, the agent stops with a message naming the missing variable.

## Usage

Pass the question as an argument:

```bash
python src/research_agent/agent.py "What is the latest stable release of Python?"
```

Or run it with no arguments and type the question when prompted:

```bash
python src/research_agent/agent.py
Ask your research question: What is the latest development in AI?
```

The "Researching..." status line goes to stderr and the answer goes to stdout, so
you can save only the answer:

```bash
python src/research_agent/agent.py "Compare the top open-source vector databases" > answer.md
```

### Use from Python

```python
import sys
sys.path.insert(0, "src")

from research_agent.agent import research

print(research("Who won the most recent Nobel Prize in Physics?"))
```

## Project layout

```
.
├── src/research_agent/agent.py   # the agent: model, Tavily tool, prompt, CLI entry point
├── requirements.txt              # Python dependencies
├── .env.example                  # template for API keys and model name
└── README.md
```

## Customizing

All settings are in [`src/research_agent/agent.py`](src/research_agent/agent.py):

- **Number of search results:** change `TavilySearch(max_results=5)`.
- **Answer style:** edit `SYSTEM_PROMPT`.
- **Creativity:** change `temperature=0` on the model.

## Notes

- Answer quality depends on the model you choose and on which pages Tavily
  returns. Check the listed sources for anything important.
- Each run uses OpenRouter and Tavily API credits.
- `.env` holds your keys. Keep it out of version control.

## Prompt to generate this project
Framework used : Role → Context → Task → Constraints → Output Format 

Paste this into an AI coding assistant to recreate the project:

```text
Role: You are a Python developer who writes simple, beginner-friendly code.
Context: I'm a student building a web research agent with LangChain and Tavily, using an LLM via OpenRouter.
Task: Build a CLI agent that takes one question, searches the web with Tavily, prints a cited answer, and exits.
Constraints: Use the latest LangChain (create_agent), read API keys from a .env file, and keep the code in one small file.
Output: The code, requirements.txt, .env.example, and short steps to run it.
```
