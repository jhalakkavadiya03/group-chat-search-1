# 💬 Search a Group Chat Properly

> *"When did we decide on Manali?"* You know the message exists. It is somewhere in four thousand messages, across six months, and you do not remember the words that were used — someone probably typed *"chalo pahad pakka final karte hai"* and searching for *"Manali"* returns two hundred results. Text search fails at exactly the moment you need it, which is when you have forgotten the wording but remember the meaning.

This project implements an intelligent, context-aware conversational search engine designed specifically for realistic, messy, code-mixed (**Hinglish**) group chats.

---

## 🌟 Key Features

1. **Three Distinct Query Shapes**:
   - **Semantic Queries**: Concept-driven search without keyword reliance (*"When was the vacation finalized?"*, *"Who suggested the mountain trip?"*).
   - **Attributed Queries**: Grammar-aware speaker resolution boosting messages from or directed to specific participants (*"What did Priya say about the budget?"*, *"What discount hack did Vikram share?"*).
   - **Temporal Queries**: Relative and calendar-based interval extraction (*"What did we discuss on Diwali morning in November?"*, *"What was the New Year resolution?"*).
   - **Hybrid Queries**: Multi-condition search combining speaker, timeframe, and topic (*"What did Sneha say about leaves in October?"*).

2. **Surrounding Conversational Context Window**:
   - Group chats are staccato (*"haan"*, *"done"*, *"wahi wala"*). A single message out of context is meaningless.
   - Every search result returns the target message anchored within its **chronological conversation window ($\pm 4$ messages)** with timestamps, participant badges, and thread metadata.

3. **Hinglish & Code-Mixed Understanding**:
   - Seamlessly handles colloquial Romanized Hindi idioms (*"jugaad"*, *"rokda"*, *"kharcha"*, *"pakka"*, *"safar"*, *"pahad"*).
   - Bridges vernacular terminology with formal English queries (e.g., *"vacation"* $\leftrightarrow$ *"pahad"*, *"deposit"* $\leftrightarrow$ *"token advance bhej diya"*, *"1500"* $\leftrightarrow$ *"pandrah sau"*).
   - Resilient against typos (*"mnaali"*, *"kl"*, *"bgt"*, *"thikkk"*).

4. **Rigorous Benchmark with Zero-Keyword Overlap**:
   - 40 ground-truth evaluation queries across all query shapes.
   - **17 queries with strictly 0% keyword overlap** between the query and the target message.

---

## 📊 Benchmark Evaluation Results

Evaluated across all **40 ground-truth queries** on the 4,250-message corpus:

| Search Mode | Hit@1 (Accuracy) | Hit@5 (Recall) | Mean Reciprocal Rank (MRR) | Zero-Keyword Hit@5 | Avg Latency |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **1. Naive Keyword Search** | 22.5% | 40.0% | 0.282 | **0.0%** | 0.12 ms |
| **2. Naive Isolated Vector Search** | 22.5% | 40.0% | 0.282 | **0.0%** | 0.10 ms |
| **3. Contextual Hinglish Hybrid (Ours)** | **62.5%** | **90.0%** | **0.712** | **76.5%** | **2.54 ms** |

> **Key Takeaway**: Naive keyword search has a **0.0% success rate** on zero-keyword queries because real people write *"chalo pahad pakka final karte hai"* instead of literal English. Our contextual hybrid pipeline scores **76.5% on zero-keyword queries** and **90.0% recall overall**.

---

## 🏗️ System Architecture

```
User Query: "When was the vacation finalized?"
                      │
       ┌──────────────┴──────────────┐
       ▼                             ▼
 [Speaker Attribution]     [Temporal Resolver]
 • Target: None            • Range: None
       │                             │
       └──────────────┬──────────────┘
                      ▼
        [Hinglish Concept Normalizer]
 • "vacation" -> "trip", "pahad", "ghoomne", "Manali", "himachal"
 • "finalized" -> "pakka", "final", "lock", "done", "book", "karoongi"
                      │
       ┌──────────────┴──────────────┐
       ▼                             ▼
 [Sliding Context Index]       [Subword Token BM25]
 ([-6, +2] message chunking)    (Typo & exact match resilience)
       │                             │
       └──────────────┬──────────────┘
                      ▼
         [Hybrid Fusion & Filtering]
 • Context score + Exact token score + Attribution boost + Temporal decay
                      │
                      ▼
      [Context Window Re-assembler]
 • Target message highlighted + surrounding [-4 ... +4] conversation bubbles
                      │
                      ▼
         [Grounded Chatbot Answer]
 • Direct synthesized answer citing timestamp, sender, and message ID
```

---

## 📂 Project Structure

```
group_chat_search/
├── data/
│   ├── group_chat_data.json       # 4,250 messages in structured JSON
│   ├── group_chat_export.txt      # Standard WhatsApp export format
│   ├── benchmark_queries.json     # 40 ground-truth queries (17 zero-KW)
│   ├── ground_truth_keys.json     # Decision thread milestone IDs
│   └── evaluation_results.json    # Complete benchmark run metrics
├── engine/
│   ├── corpus_generator.py        # Seeded synthetic chat generator
│   ├── generate_benchmark.py      # Benchmark query builder & verifier
│   ├── hinglish_normalizer.py     # Bilingual concept clusters & stemming
│   ├── search_engine.py           # Contextual sliding-window search engine
│   └── chatbot.py                 # Grounded QA synthesizer
├── web/
│   └── index.html                 # Sleek WhatsApp-style interactive UI
├── evaluate.py                    # Automated 40-query benchmark runner
├── app.py                         # Local web application server
├── README.md                      # Documentation & architecture guide
└── .gitignore                     # Git ignore rules
```

---

## 🚀 Quickstart Guide

### 1. Run the Benchmark Evaluator
Run the automated test suite comparing all 3 search paradigms across the 40 queries:
```bash
python evaluate.py data
```

### 2. Launch the Web Interface
Start the local search app:
```bash
python app.py 8080
```
Then open [http://localhost:8080](http://localhost:8080) in your web browser.

### 3. Interactive Generative UI
Open the standalone interactive artifact directly in your browser or Antigravity viewer:
```
file:///C:/Users/Harshita/.gemini/antigravity/brain/d5de7e4d-4ed9-47af-9c20-480b933c8249/group_chat_search_app.html
```

---

## 🌐 Publishing to GitHub

To publish this project to your public GitHub profile:

1. Initialize the remote repository on GitHub:
```bash
# Using GitHub CLI:
gh repo create group-chat-search --public --source=. --remote=origin --push

# OR using standard Git:
git remote add origin https://github.com/<your-username>/group-chat-search.git
git branch -M main
git push -u origin main
```
