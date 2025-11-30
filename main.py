import asyncio
import time
import os
import random
from dotenv import load_dotenv
from google.api_core.exceptions import ResourceExhausted
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
    max_retries = 5

    for attempt in range(max_retries):
        try:
            async for event in runner.run_async(user_id="user", session_id=session_id, new_message=message):
                # Only capture the FINAL response, not intermediate agent outputs
                if hasattr(event, "is_final_response") and event.is_final_response():
                    content = getattr(event, "content", None)
                    if content and getattr(content, "parts", None):
                        text_parts = [part.text for part in content.parts if getattr(part, "text", None)]
                        if text_parts:
                            output_text = "".join(text_parts)
            
            # If successful, break the retry loop
            break

        except ResourceExhausted:
            if attempt == max_retries - 1:
                raise  # Re-raise the exception if we've run out of retries
            
            # Base wait time: 2, 4, 8, 16, 32 seconds
            wait_time = (2 ** attempt) 
            # Add random jitter (0-1 sec) to prevent synchronized retries
            actual_wait = wait_time + random.random()
            
            print(f"Rate limit hit for {session_id}. Retrying in {actual_wait:.2f} seconds...")
            await asyncio.sleep(actual_wait)

    return output_text

async def main():
    # Get user input
    print("\n" + "="*80)
    print(" Core3 - Multi-agent AI that know the important of silence for reflection")
    print("="*80)
    user_query = input("\nWhat topic do you seek to understand? > ")
    
    print("\n[We are working on it...]\n")

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
