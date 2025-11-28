import asyncio
import time
import os
from dotenv import load_dotenv
from google.adk.runners import InMemoryRunner
from google.genai import types
from agent import dogen_agent, wittgenstein_agent, strategist_agent, librarian_agent, editor_agent, projectionist_agent, sage_agent
from google.adk.agents import SequentialAgent

# Load environment variables
load_dotenv()

async def run_agent(agent, user_query, session_id):
    # Use app_name="agents" to match where SequentialAgent is loaded from, silencing the warning
    runner = InMemoryRunner(agent=agent, app_name="agents")
    # Create session asynchronously
    await runner.session_service.create_session(session_id=session_id, user_id="user", app_name="agents")
    
    message = types.Content(parts=[types.Part(text=user_query)])
    
    output_text = ""
    async for event in runner.run_async(user_id="user", session_id=session_id, new_message=message):
        # Attempt to extract text from the event. 
        if hasattr(event, 'text') and event.text:
             output_text = event.text
        elif hasattr(event, 'response') and hasattr(event.response, 'text') and event.response.text:
             output_text = event.response.text

    return output_text

async def main():
    # Get user input
    print("\n" + "="*50)
    print(" BUDDHIST ORACLE - FIRST PRINCIPLES AGENT")
    print("="*50)
    user_query = input("\nWhat topic do you seek to understand? > ")
    
    print("\n[The Oracle is contemplating...]\n")

    # 1. Run the Oracle Sequence
    oracle_sequence = SequentialAgent(
        name="OracleCore",
        sub_agents=[strategist_agent, librarian_agent, editor_agent, projectionist_agent, sage_agent]
    )
    
    # Run Oracle
    try:
        oracle_output = await run_agent(oracle_sequence, user_query, "session_oracle")
        print(oracle_output)
    except Exception as e:
        print(f"Error running Oracle: {e}")

    # 2. The Silence (5 seconds)
    print("\n" + " "*20 + "* Silence *" + " "*20 + "\n")
    time.sleep(5)
    
    # 3. Run Dogen and Wittgenstein (Parallel-ish)
    print("-" * 20 + " The Masters Speak " + "-" * 20 + "\n")
    
    try:
        dogen_task = run_agent(dogen_agent, user_query, "session_dogen")
        wittgenstein_task = run_agent(wittgenstein_agent, user_query, "session_wittgenstein")
        
        dogen_result, wittgenstein_result = await asyncio.gather(dogen_task, wittgenstein_task)
        
        print(f"Monk Dōgen asks:\n\"{dogen_result.strip()}\"\n")
        print(f"Ludwig Wittgenstein asks:\n\"{wittgenstein_result.strip()}\"\n")
    except Exception as e:
        print(f"Error running Masters: {e}")
    
    print("="*50 + "\n")

if __name__ == "__main__":
    asyncio.run(main())
