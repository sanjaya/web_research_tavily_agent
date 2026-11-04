"""A simple one-shot web research agent built with LangChain and Tavily.

The user asks a single question; the agent searches the web with Tavily,
writes a cited answer, prints it, and exits.

Usage:
    python src/research_agent/agent.py "What is the latest development in AI"
    python src/research_agent/agent.py          # prompts for the question
"""

import os
import sys

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain_openai import ChatOpenAI
from langchain_tavily import TavilySearch

OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"

SYSTEM_PROMPT = """You are a web research assistant.
Use the tavily_search tool to find current, reliable information before answering.
Search more than once if the first results are incomplete.
Write a clear, concise answer. Cite sources inline as [1], [2], ... and finish
with a "Sources" list of the URLs you used. If the results do not answer the
question, say so instead of guessing."""


def build_agent():
    """Create the LangChain agent: an OpenRouter chat model plus the Tavily search tool."""
    load_dotenv()

    missing = [k for k in ("OPENROUTER_API_KEY", "LLM_MODEL", "TAVILY_API_KEY") if not os.getenv(k)]
    if missing:
        sys.exit(f"Missing environment variables: {', '.join(missing)} (see .env.example)")

    llm = ChatOpenAI(
        model=os.environ["LLM_MODEL"],
        api_key=os.environ["OPENROUTER_API_KEY"],
        base_url=OPENROUTER_BASE_URL,
        temperature=0,
    )
    search = TavilySearch(max_results=5)  # reads TAVILY_API_KEY from the environment

    # Build an agent loop: the LLM calls Tavily search as needed, then writes the final answer.
    return create_agent(model=llm, tools=[search], system_prompt=SYSTEM_PROMPT)


def research(question: str) -> str:
    """Run the agent once on a single question and return the final answer text."""
    agent = build_agent()
    result = agent.invoke({"messages": [{"role": "user", "content": question}]})
    return result["messages"][-1].text


def main() -> None:
    question = " ".join(sys.argv[1:]).strip() or input("Ask your research question: ").strip()
    if not question:
        sys.exit("No question given.")

    print("Researching...\n", file=sys.stderr)
    print(research(question))


if __name__ == "__main__":
    main()
