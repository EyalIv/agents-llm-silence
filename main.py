import asyncio
import time
import os
import random
import re
from datetime import datetime
from dotenv import load_dotenv
from google.api_core.exceptions import ResourceExhausted
from google.adk.runners import InMemoryRunner
from google.genai import types
from agent import dogen_agent, wittgenstein_agent, strategist_agent, librarian_agent, editor_agent, projectionist_agent, sage_agent
from google.adk.agents import SequentialAgent

# Load environment variables
load_dotenv()

# Output directory for markdown files
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "outputs")
os.makedirs(OUTPUT_DIR, exist_ok=True)


def sanitize_filename(query: str) -> str:
    """Convert user query to a safe filename."""
    # Take first 50 chars, replace spaces with underscores, remove special chars
    clean = re.sub(r'[^\w\s-]', '', query[:50]).strip()
    clean = re.sub(r'[\s]+', '_', clean)
    return clean.lower() or "query"


def extract_sage_output(raw_output: str) -> str:
    """Extract only the Sage's final formatted output from accumulated pipeline text."""
    # Look for the start of Sage's formatted output (### 1. **)
    # This marks where the clean, final output begins
    marker = "### 1. **"
    if marker in raw_output:
        return raw_output[raw_output.index(marker):]
    # Fallback: return everything if marker not found
    return raw_output


def save_markdown_output(query: str, oracle_output: str, dogen_result: str, wittgenstein_result: str) -> str:
    """Save the complete output as a formatted Markdown file."""
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"{timestamp}_{sanitize_filename(query)}.md"
    filepath = os.path.join(OUTPUT_DIR, filename)
    
    # Extract only the Sage's clean output
    clean_output = extract_sage_output(oracle_output)
    
    md_content = f"""# Buddhist Oracle Results

**Query:** {query}  
**Date:** {datetime.now().strftime("%B %d, %Y at %H:%M")}

---

## 📚 The Three Principles

{clean_output}

---

## 🧘 The Masters Speak

### Monk Dōgen asks:
> {dogen_result.strip()}

### Ludwig Wittgenstein asks:
> {wittgenstein_result.strip()}

---

*In silence, understanding deepens.*
"""
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(md_content)
    
    return filepath

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
            chunks = []
            async for event in runner.run_async(user_id="user", session_id=session_id, new_message=message):
                # ADK events expose streaming deltas as well as the final response payload.
                chunk = None

                if hasattr(event, "text") and event.text:
                    chunk = event.text
                elif hasattr(event, "delta") and getattr(event.delta, "text", None):
                    chunk = event.delta.text
                elif hasattr(event, "is_final_response") and event.is_final_response():
                    content = getattr(event, "content", None)
                    if content and getattr(content, "parts", None):
                        text_parts = [part.text for part in content.parts if getattr(part, "text", None)]
                        if text_parts:
                            chunk = "".join(text_parts)

                if chunk:
                    chunks.append(chunk)
            
            if chunks:
                output_text = "".join(chunks)
            
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

    # Initialize results
    oracle_output = ""
    dogen_result = ""
    wittgenstein_result = ""

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
        oracle_output = f"Error: {e}"

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
        dogen_result = dogen_result or "Error retrieving question"
        wittgenstein_result = wittgenstein_result or "Error retrieving question"
    
    print("="*50 + "\n")

    # 4. Save results to Markdown file
    filepath = save_markdown_output(user_query, oracle_output, dogen_result, wittgenstein_result)
    print(f"📄 Results saved to: {filepath}\n")

if __name__ == "__main__":
    asyncio.run(main())
