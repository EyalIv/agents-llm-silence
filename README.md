# Core3

**Understand any topic through its 3 most important principles**

A multi-agent AI system that distills complex topics into exactly 3 first principles with curated resources. The application allows you to study a topic, then uses silence to let ideas assimilate. At the end, Dōgen and Wittgenstein prompt a moment of introspection on the topic.

---

## 🎯 Problem

Modern AI assistants are verbose by design—endless conversations when clarity requires few words. Users face:
- **Information Overload** — Too much content, not enough clarity
- **Lost Fundamentals** — Surface-level explanations miss core principles  
- **Conversation Fatigue** — Multi-turn dialogues when single answers suffice

## 💡 Solution

Inspired by Zen philosophy: **maximum insight through minimum words, followed by silence**.

Buddhist Oracle delivers:
- **3 First Principles** — The fundamental concepts underlying any topic
- **Curated Resources** — Authoritative links for each principle
- **Visual Learning** — A relevant YouTube video
- **Philosophical Closure** — Ends definitively, no follow-up prompts
- **Reflective Questions** — Two philosophers challenge you to think deeper

---

## 🏗️ Architecture

```
User Query
    │
    ▼
┌─────────────────────────────────────────┐
│     PHASE 1: SEQUENTIAL PIPELINE        │
│                                         │
│  Strategist → Librarian → Editor →      │
│  Projectionist → Sage                   │
│                                         │
│  (5 agents passing state via output_key)│
└─────────────────────────────────────────┘
    │
    ▼
        * 5-Second Silence *
    │
    ▼
┌─────────────────────────────────────────┐
│     PHASE 2: PARALLEL PHILOSOPHERS      │
│                                         │
│   Monk Dōgen    ║    Wittgenstein       │
│   (Zen koan)    ║    (Language game)    │
│                                         │
│   (asyncio.gather - run in parallel)    │
└─────────────────────────────────────────┘
    │
    ▼
Session Complete (no follow-ups)
```

### Agent Roles

| Agent | Role | Tools |
|-------|------|-------|
| **TheStrategist** | Extract 3 first principles | — |
| **TheLibrarian** | Find authoritative sources | `google_search` |
| **TheEditor** | Format as Markdown | — |
| **TheProjectionist** | Find YouTube video | `google_search` |
| **TheSage** | Present final answer + closure | — |
| **MonkDōgen** | Ask Zen koan question | — |
| **LudwigWittgenstein** | Ask language/meaning question | — |

---

## 🔧 Technical Concepts (3/3)

| Concept | Implementation |
|---------|----------------|
| **Multi-Agent (Sequential)** | `SequentialAgent` with 5 sub-agents, state passing via `output_key` |
| **Multi-Agent (Parallel)** | `asyncio.gather()` runs Dōgen + Wittgenstein simultaneously |
| **Tools + Sessions** | `google_search` tool + `InMemoryRunner` with session management |

---

## 🚀 Setup

### Prerequisites
- Python 3.10+
- Google API Key (Gemini)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/EyalIv/agents-llm-silence.git
   cd agents-llm-silence
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   venv\Scripts\activate  # Windows
   # source venv/bin/activate  # macOS/Linux
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure API key**
   
   Create a `.env` file in the root directory:
   ```
   GOOGLE_API_KEY=your_api_key_here
   ```

### Run

```bash
python main.py
```

---

## 📖 Usage Example

```
══════════════════════════════════════════════════════
 BUDDHIST ORACLE - FIRST PRINCIPLES AGENT
══════════════════════════════════════════════════════

What topic do you seek to understand? > How does blockchain work?

[The Oracle is contemplating...]

1. **Decentralization** - No single authority controls the network.
   → https://ethereum.org/decentralization

2. **Cryptographic Hashing** - Data integrity through one-way functions.
   → https://www.investopedia.com/crypto-hash

3. **Consensus Mechanisms** - Network agrees on valid transactions.
   → https://consensys.net/consensus-explained

**Visual Guide:** https://youtube.com/watch?v=blockchain-explained

*These are the answers.*
In silence, understanding deepens.

                    * Silence *

──────────────── The Masters Speak ────────────────

Monk Dōgen asks:
"When you speak of 'trust' in a trustless system, 
 where does your body feel that trust reside?"

Ludwig Wittgenstein asks:
"In what language game does 'decentralized' 
 gain its meaning—and who taught you to play?"

══════════════════════════════════════════════════════
```

---

## 📁 Project Structure

```
buddhist-oracle/
├── agent.py         # 7 agent definitions
├── main.py          # Runner, CLI, async execution
├── requirements.txt # Dependencies
├── PRD.md           # Product Requirements Document
├── README.md        # This file
└── .env             # API key (not committed)
```

---

## 🛠️ Technology Stack

| Component | Technology |
|-----------|------------|
| Framework | Google ADK (Agent Development Kit) |
| LLM | Gemini 2.5 Flash |
| Tools | Google Search (built-in ADK) |
| Sessions | `InMemoryRunner` |
| Error Handling | Exponential backoff (5 retries) |
| Async | Python `asyncio` |

---

## 📚 Dependencies

```
google-adk>=0.1.0
google-generativeai>=0.3.0
python-dotenv>=1.0.0
```

---

## 🎨 Design Principles

1. **Minimalism** — Exactly 3 principles, no more
2. **Completeness** — Answer is self-sufficient
3. **Closure** — Ends with "These are the answers"
4. **Reflection** — Philosophers invite deeper thinking

---

## 📄 License

MIT License

---

## 🙏 Acknowledgments

- Google ADK Team
- Kaggle Agents Competition
- Zen Master Eihei Dōgen (1200-1253)
- Ludwig Wittgenstein (1889-1951)
