# buddhist-oracle/agent.py
from google.adk.agents import Agent, SequentialAgent
from google.adk.models.google_llm import Gemini
from google.adk.tools import google_search
from google.genai import types

retry_config = types.HttpRetryOptions(attempts=5, exp_base=7, initial_delay=1, http_status_codes=[429, 500, 503, 504])

# 1. The Strategist
strategist_agent = Agent(
    name="TheStrategist",
    model=Gemini(model="gemini-2.0-flash-exp", retry_options=retry_config),
    output_key="raw_concepts",
    instruction="""
    You are an expert consultant. Identify exactly 3 fundamental First Principles for the user's request.
    Be practical and concrete.
    Output ONLY the 3 topic titles, one per line.
    """
)

# 2. The Librarian
librarian_agent = Agent(
    name="TheLibrarian",
    model=Gemini(model="gemini-2.0-flash-exp", retry_options=retry_config),
    tools=[google_search],
    output_key="verified_links",
    instruction="""
    You are a research librarian.
    Input: 3 topics from TheStrategist.
    For each topic:
    - Search Google and find one high-quality article/guide.
    - Fallback search URL if unsure: https://www.google.com/search?q=[Topic]+guide
    - Write one short sentence explaining it.
    Output format (exactly):
    Topic Name - One-sentence explanation - Link
    """
)

# 3. The Editor
editor_agent = Agent(
    name="TheEditor",
    model=Gemini(model="gemini-2.0-flash-exp", retry_options=retry_config),
    output_key="triad_text",
    instruction="Format the input into a clean Markdown numbered list with bold titles."
)

# 4. The Projectionist (YouTube)
projectionist_agent = Agent(
    name="TheProjectionist",
    model=Gemini(model="gemini-2.0-flash-exp", retry_options=retry_config),
    tools=[google_search],
    output_key="video_link",
    instruction="""
    Find ONE highly viewed YouTube video (>100k views preferred) related to the user's original question.
    If no perfect match, return a YouTube search URL: https://www.youtube.com/results?search_query=[User Question]
    Output ONLY the URL.
    """
)

# 5. The Sage
sage_agent = Agent(
    name="TheSage",
    model=Gemini(model="gemini-2.0-flash-exp", retry_options=retry_config),
    instruction="""
    You are a wise sage who speaks few words.
    Inputs: triad_text and video_link.
    Task:
    1. Present the triad_text clearly as a Markdown list.
    2. Add a section called "Visual Guide" with the video_link.
    3. End with exactly this sentence: "These are the answers."
    4. Add one final short wise sentence about silence and reflection.
    """
)

# Main agent (must be named root_agent)
root_agent = SequentialAgent(
    name="BuddhistOracle",
    sub_agents=[strategist_agent, librarian_agent, editor_agent, projectionist_agent, sage_agent]
)