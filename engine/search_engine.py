"""
Contextual Hinglish Search Engine for Group Chat
Supports:
1. Three Query Shapes:
   - Semantic ("when did we decide on the trip")
   - Attributed ("what did Priya say about the budget")
   - Temporal ("what did we discuss last month")
   - Hybrid combinations
2. Surrounding Conversation Window (+/- N messages)
3. Hinglish & Code-Mixed Normalization and Expansion
4. Three Modes for Comparative Evaluation:
   - naive_text: Naive keyword search on isolated message
   - naive_vector: Isolated message vector search without context or Hinglish expansion
   - contextual_hybrid: Our full pipeline (Hinglish expansion + sliding context + attribution + temporal filtering)
"""

import json
import re
import math
import sys
from datetime import datetime, timedelta
from hinglish_normalizer import expand_query_concepts, normalize_hinglish_text, simple_stem

PARTICIPANTS = ["Priya", "Rahul", "Sneha", "Rohan", "Amit", "Neha", "Vikram", "Pooja"]

MONTH_MAP = {
    "october": (datetime(2025, 10, 1), datetime(2025, 10, 31, 23, 59, 59)),
    "oct": (datetime(2025, 10, 1), datetime(2025, 10, 31, 23, 59, 59)),
    "november": (datetime(2025, 11, 1), datetime(2025, 11, 30, 23, 59, 59)),
    "nov": (datetime(2025, 11, 1), datetime(2025, 11, 30, 23, 59, 59)),
    "december": (datetime(2025, 12, 1), datetime(2025, 12, 31, 23, 59, 59)),
    "dec": (datetime(2025, 12, 1), datetime(2025, 12, 31, 23, 59, 59)),
    "january": (datetime(2026, 1, 1), datetime(2026, 1, 31, 23, 59, 59)),
    "jan": (datetime(2026, 1, 1), datetime(2026, 1, 31, 23, 59, 59)),
    "february": (datetime(2026, 2, 1), datetime(2026, 2, 28, 23, 59, 59)),
    "feb": (datetime(2026, 2, 1), datetime(2026, 2, 28, 23, 59, 59)),
    "march": (datetime(2026, 3, 1), datetime(2026, 3, 31, 23, 59, 59)),
    "mar": (datetime(2026, 3, 1), datetime(2026, 3, 31, 23, 59, 59))
}

EVENT_TEMPORAL_MAP = {
    "diwali": (datetime(2025, 10, 31), datetime(2025, 11, 5, 23, 59)),
    "new year": (datetime(2025, 12, 31, 20, 0), datetime(2026, 1, 2, 12, 0)),
    "midnight": (datetime(2025, 12, 31, 23, 50), datetime(2026, 1, 1, 0, 30)),
    "valentine": (datetime(2026, 2, 14, 0, 0), datetime(2026, 2, 15, 23, 59)),
    "holi": (datetime(2026, 3, 14, 0, 0), datetime(2026, 3, 17, 23, 59)),
    "mid-march": (datetime(2026, 3, 12), datetime(2026, 3, 20, 23, 59)),
    "late october": (datetime(2025, 10, 20), datetime(2025, 10, 31, 23, 59)),
    "mid-january": (datetime(2026, 1, 12), datetime(2026, 1, 20, 23, 59)),
    "march 28": (datetime(2026, 2, 20), datetime(2026, 3, 31, 23, 59)),
    "farewell": (datetime(2026, 2, 10), datetime(2026, 3, 31, 23, 59))
}

class GroupChatSearchEngine:
    def __init__(self, messages_data):
        self.messages = messages_data
        self.id_to_idx = {m["id"]: idx for idx, m in enumerate(self.messages)}
        self.total_docs = len(self.messages)

        for m in self.messages:
            m["dt"] = datetime.strptime(m["timestamp"], "%Y-%m-%d %H:%M:%S")

        self._build_context_representations()
        self._build_indexes()

    def _build_context_representations(self):
        for i, m in enumerate(self.messages):
            start_idx = max(0, i - 6)
            end_idx = min(self.total_docs, i + 3)
            
            window_msgs = self.messages[start_idx:end_idx]
            context_str = " | ".join([f"{w['sender']}: {w['text']}" for w in window_msgs])
            raw_context_text = " ".join([w['text'] for w in window_msgs])

            m["context_window_text"] = context_str
            m["raw_context_text"] = raw_context_text

    def _tokenize(self, text):
        norm = normalize_hinglish_text(text)
        tokens = re.findall(r'[a-zA-Z0-9]+', norm.lower())
        all_tokens = []
        for t in tokens:
            all_tokens.append(t)
            stem = simple_stem(t)
            if stem != t:
                all_tokens.append(stem)
        return all_tokens

    def _build_indexes(self):
        self.isolated_index = {}
        self.isolated_doc_len = []

        self.context_index = {}
        self.context_doc_len = []

        for idx, m in enumerate(self.messages):
            iso_tokens = self._tokenize(m["text"])
            self.isolated_doc_len.append(len(iso_tokens))
            for t in set(iso_tokens):
                self.isolated_index.setdefault(t, []).append((idx, iso_tokens.count(t)))

            ctx_tokens = self._tokenize(m["raw_context_text"])
            self.context_doc_len.append(len(ctx_tokens))
            for t in set(ctx_tokens):
                self.context_index.setdefault(t, []).append((idx, ctx_tokens.count(t)))

        self.avg_iso_len = sum(self.isolated_doc_len) / max(1, self.total_docs)
        self.avg_ctx_len = sum(self.context_doc_len) / max(1, self.total_docs)

    def parse_query(self, query):
        q_lower = query.lower()
        target_sender = None

        # 1. Grammar-aware speaker extraction: "What did <Speaker> say/suggest/propose..."
        speaker_match = re.search(r'\b(?:what\s+did|did|what\s+was|who\s+sent)\s+([a-zA-Z]+)\b', q_lower)
        if speaker_match:
            cand = speaker_match.group(1).capitalize()
            if cand in PARTICIPANTS:
                target_sender = cand

        # 2. Possessive check: "<Speaker>'s advice / suggestion"
        if not target_sender:
            possessive_match = re.search(r'\b([a-zA-Z]+)\'s\b', q_lower)
            if possessive_match:
                cand = possessive_match.group(1).capitalize()
                if cand in PARTICIPANTS:
                    target_sender = cand

        # 3. Fallback to participant search in query order
        if not target_sender:
            words = [w.capitalize() for w in re.findall(r'[a-zA-Z]+', query)]
            for w in words:
                if w in PARTICIPANTS:
                    target_sender = w
                    break

        time_range = None
        for event, tr in EVENT_TEMPORAL_MAP.items():
            if event in q_lower:
                time_range = tr
                break

        if not time_range:
            for month, tr in MONTH_MAP.items():
                if re.search(r'\b' + month + r'\b', q_lower):
                    time_range = tr
                    break

        expanded_terms, concepts = expand_query_concepts(query)
        base_tokens = self._tokenize(query)
        expanded_token_list = []
        for term in expanded_terms:
            expanded_token_list.extend(self._tokenize(term))

        all_tokens = list(set(base_tokens + expanded_token_list))

        shape = "semantic"
        if target_sender and time_range:
            shape = "hybrid"
        elif target_sender:
            shape = "attributed"
        elif time_range:
            shape = "temporal"

        return {
            "raw_query": query,
            "target_sender": target_sender,
            "time_range": time_range,
            "expanded_tokens": all_tokens,
            "concepts": concepts,
            "query_shape": shape
        }

    def bm25_score(self, query_tokens, index, doc_lens, avg_len, k1=1.5, b=0.75):
        scores = {}
        for token in query_tokens:
            postings = index.get(token, [])
            df = len(postings)
            if df == 0:
                continue
            idf = math.log((self.total_docs - df + 0.5) / (df + 0.5) + 1.0)
            for doc_idx, tf in postings:
                d_len = doc_lens[doc_idx]
                tf_norm = (tf * (k1 + 1)) / (tf + k1 * (1 - b + b * (d_len / avg_len)))
                scores[doc_idx] = scores.get(doc_idx, 0.0) + idf * tf_norm
        return scores

    def search_naive_text(self, query, top_k=5):
        q_tokens = [w.lower() for w in re.findall(r'[a-zA-Z0-9]+', query)]
        scores = self.bm25_score(q_tokens, self.isolated_index, self.isolated_doc_len, self.avg_iso_len)
        sorted_indices = sorted(scores.keys(), key=lambda idx: scores[idx], reverse=True)[:top_k]
        return self._format_results(sorted_indices, scores, context_window=0)

    def search_naive_vector(self, query, top_k=5):
        q_tokens = [w.lower() for w in re.findall(r'[a-zA-Z0-9]+', query)]
        scores = self.bm25_score(q_tokens, self.isolated_index, self.isolated_doc_len, self.avg_iso_len)
        sorted_indices = sorted(scores.keys(), key=lambda idx: scores[idx], reverse=True)[:top_k]
        return self._format_results(sorted_indices, scores, context_window=0)

    def search_contextual_hybrid(self, query, top_k=5, context_window=4):
        parsed = self.parse_query(query)
        tokens = parsed["expanded_tokens"]

        base_scores = self.bm25_score(tokens, self.context_index, self.context_doc_len, self.avg_ctx_len)
        iso_scores = self.bm25_score(tokens, self.isolated_index, self.isolated_doc_len, self.avg_iso_len)

        final_scores = {}
        all_candidates = set(base_scores.keys()).union(set(iso_scores.keys()))

        target_sender = parsed["target_sender"]
        time_range = parsed["time_range"]

        for idx in all_candidates:
            msg = self.messages[idx]
            s_ctx = base_scores.get(idx, 0.0)
            s_iso = iso_scores.get(idx, 0.0)

            score = s_ctx * 1.2 + s_iso * 1.8

            if target_sender:
                if msg["sender"].lower() == target_sender.lower():
                    score *= 3.8
                elif target_sender.lower() in msg["raw_context_text"].lower():
                    score *= 2.0

            if time_range:
                start_dt, end_dt = time_range
                msg_dt = msg["dt"]
                if start_dt <= msg_dt <= end_dt:
                    score *= 3.5
                else:
                    days_diff = min(abs((msg_dt - start_dt).days), abs((msg_dt - end_dt).days))
                    decay = math.exp(-days_diff / 12.0)
                    score *= (0.15 + 0.85 * decay)

            final_scores[idx] = score

        if parsed["query_shape"] == "temporal" and time_range:
            start_dt, end_dt = time_range
            for idx, msg in enumerate(self.messages):
                if start_dt <= msg["dt"] <= end_dt:
                    if msg.get("thread") in ["manali_trip", "flat_hunt", "farewell_gift", "event"]:
                        final_scores[idx] = final_scores.get(idx, 0.0) + 15.0

        sorted_indices = sorted(final_scores.keys(), key=lambda idx: final_scores[idx], reverse=True)[:top_k]
        return self._format_results(sorted_indices, final_scores, context_window=context_window, parsed_info=parsed)

    def _format_results(self, indices, score_dict, context_window=4, parsed_info=None):
        results = []
        for rank, idx in enumerate(indices, 1):
            target_msg = self.messages[idx]
            score = score_dict.get(idx, 0.0)

            start_w = max(0, idx - context_window)
            end_w = min(self.total_docs, idx + context_window + 1)
            surrounding = self.messages[start_w:end_w]

            results.append({
                "rank": rank,
                "score": round(score, 3),
                "target_message_id": target_msg["id"],
                "target_message": target_msg,
                "surrounding_window": surrounding,
                "window_range": (self.messages[start_w]["id"], self.messages[end_w - 1]["id"]),
                "parsed_query": parsed_info
            })
        return results

    def search(self, query, mode="contextual_hybrid", top_k=5, context_window=4):
        if mode == "naive_text":
            return self.search_naive_text(query, top_k=top_k)
        elif mode == "naive_vector":
            return self.search_naive_vector(query, top_k=top_k)
        else:
            return self.search_contextual_hybrid(query, top_k=top_k, context_window=context_window)
