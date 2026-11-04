"""A web research chat agent that remembers the conversation.

Unlike single_query_agent.py (one question, then exit), this version keeps
asking for questions until you type "exit". LangGraph's InMemorySaver stores
the chat history, so you can ask follow-ups like "tell me more about the
second one".

Usage:
    python src/research_agent/chat_agent.py
"""

import os
import sys

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain_openai import ChatOpenAI
from langchain_tavily import TavilySearch
from langgraph.checkpoint.memory import InMemorySaver

OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"

SYSTEM_PROMPT = """You are a web research assistant.
Use the tavily_search tool to find current, reliable information before answering.
Use the earlier conversation to understand follow-up questions.
Write a clear, concise answer. Cite sources inline as [1], [2], ... and finish
with a "Sources" list of the URLs you used. If the results do not answer the
question, say so instead of guessing."""


def build_agent():
    """Create the agent: an OpenRouter chat model, the Tavily search tool, and memory."""
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

    # Memory: saves every message so the agent can see the whole conversation.
    # It lives in RAM only, so the history is lost when the program exits.
    memory = InMemorySaver()

    return create_agent(model=llm, tools=[search], system_prompt=SYSTEM_PROMPT, checkpointer=memory)


def main() -> None:
    agent = build_agent()

    # The thread_id names this conversation. Messages sent with the same
    # thread_id are remembered together.
    config = {"configurable": {"thread_id": "chat-1"}}

    print("Web research agent. Ask me anything (type 'exit' to quit).\n")

    while True:
        try:
            question = input("You: ").strip()
        except (KeyboardInterrupt, EOFError):  # Ctrl+C or Ctrl+D
            break

        if question.lower() in ("exit", "quit", "bye"):
            break
        if not question:
            continue  # ignore empty lines

        print("Researching...\n")
        # We only send the new question; the memory adds the earlier messages.
        result = agent.invoke({"messages": [{"role": "user", "content": question}]}, config)
        print(f"Agent: {result['messages'][-1].text}\n")

    print("\nGoodbye!")


if __name__ == "__main__":
    main()
