"""
Chatbot QA Module
Synthesizes direct, grounded answers to user questions using retrieved group chat context,
citing exact senders, timestamps, and message bubbles.
"""

def generate_answer(query, search_results):
    if not search_results:
        return {
            "answer": "I couldn't find any relevant conversation matching your query.",
            "citations": [],
            "top_message": None
        }

    top_result = search_results[0]
    target_msg = top_result["target_message"]
    window = top_result["surrounding_window"]

    # Format surrounding context transcript
    context_lines = []
    for m in window:
        marker = "👉 " if m["id"] == target_msg["id"] else "   "
        context_lines.append(f"{marker}[{m['timestamp']}] {m['sender']}: {m['text']}")
    
    transcript_block = "\n".join(context_lines)

    # Grounded answer synthesis
    sender = target_msg["sender"]
    text = target_msg["text"]
    timestamp = target_msg["timestamp"]
    msg_id = target_msg["id"]

    answer_text = (
        f"Based on the conversation thread around **{timestamp}**, **{sender}** stated:\n"
        f"> *\"{text}\"* (Message #{msg_id})\n\n"
        f"**Context Summary:** This occurred in the context of the surrounding discussion:\n```text\n{transcript_block}\n```"
    )

    return {
        "answer": answer_text,
        "primary_sender": sender,
        "primary_timestamp": timestamp,
        "primary_message_id": msg_id,
        "primary_text": text,
        "surrounding_context": window
    }
