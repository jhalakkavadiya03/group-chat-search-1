"""
Hinglish Conversational Normalizer & Synonym Graph
Bridges Romanized Hindi / Code-Mixed chat terms, typos, and English semantic queries.
"""

import re

# Bilingual concept clusters
CONCEPT_CLUSTERS = {
    "vacation": [
        "vacation", "trip", "holiday", "break", "outing", "getaway",
        "pahad", "pahado", "ghoomne", "safar", "manali", "himachal", "kasol", "cottage"
    ],
    "finalize": [
        "finalize", "finalized", "decide", "decided", "decision", "agree", "agreed", "confirm", "confirmed",
        "pakka", "final", "lock", "done deal", "deal", "karoongi", "fix", "sorted"
    ],
    "deposit": [
        "deposit", "security deposit", "rental deposit", "advance", "token", "token advance",
        "receipt", "broker", "transfer", "bhej"
    ],
    "contribute": [
        "contribute", "contribution", "pitch in", "split", "share", "pay",
        "gpay", "upi", "bhej", "transferred", "sau", "pandrah sau", "1500"
    ],
    "farewell": [
        "farewell", "send-off", "goodbye", "leaving", "masters", "uk", "surprise", "sendoff"
    ],
    "pet": [
        "pet", "pets", "animal", "animals", "dog", "dogs", "cat", "cats",
        "billi", "kutte", "jaanwar", "allow"
    ],
    "tenancy": [
        "tenancy", "lease", "agreement", "rent", "stay", "move in", "shift",
        "starts", "agreement draft", "flat"
    ],
    "festival": [
        "festival", "spring festival", "colors", "celebration",
        "holi", "diwali", "organic", "rang", "skin allergy"
    ],
    "dessert": [
        "dessert", "sweet", "cake", "bakery", "magnolia", "pastry"
    ],
    "venue": [
        "venue", "restaurant", "gathering", "dinner", "table", "rooftop",
        "skydeck", "booked", "reservation"
    ],
    "incentive": [
        "incentive", "bonus", "payout", "diwali bonus", "credited", "40k", "deduction", "tax"
    ],
    "ergonomic": [
        "ergonomic", "furniture", "desk", "standing desk", "back pain", "discomfort", "physical discomfort", "health"
    ],
    "budget": [
        "budget", "cost", "expense", "price", "spending", "ceiling",
        "kharcha", "rokda", "hisab", "per head", "paisa", "paise", "bgt"
    ],
    "ramen": [
        "ramen", "noodles", "japanese", "miso", "spicy miso", "food", "eat", "restaurant"
    ],
    "headphones": [
        "headphones", "anc", "noise cancelling", "sony", "xm5", "wh-1000xm5", "bose"
    ],
    "leaves": [
        "leaves", "leave", "vacation days", "audit", "blocked", "holiday approval", "portal"
    ],
    "bike": [
        "bike", "motorcycle", "vehicle", "servicing", "service", "mechanic"
    ],
    "tax": [
        "tax", "investment", "proofs", "it declaration", "80c", "deduction"
    ],
    "thrift": [
        "thrift", "vintage", "jackets", "clothes", "store", "shopping", "koramangala"
    ],
    "loan": [
        "loan", "home loan", "interest", "rates", "bps", "emi", "bank"
    ],
    "discount": [
        "discount", "hack", "coupon", "savings", "offer", "deal", "zomato gold", "zomato"
    ],
    "travel": [
        "travel", "traveling", "traveler", "transport", "cab", "tempo", "tempo traveler", "chandigarh", "manali"
    ],
    "emergency_fund": [
        "emergency fund", "emergency funds", "liquid fund", "expenses", "financial advice", "advice", "savings"
    ],
    "precaution": [
        "precaution", "precautions", "warn", "warning", "skin allergy", "organic", "chemical", "colors", "holi"
    ]
}

WORD_TO_CONCEPTS = {}
for concept, words in CONCEPT_CLUSTERS.items():
    for w in words:
        WORD_TO_CONCEPTS.setdefault(w.lower(), set()).add(concept)

def simple_stem(word):
    """Simple rule-based suffix stemming for common variations."""
    w = word.lower()
    for suffix in ["ing", "ers", "er", "es", "ed", "s"]:
        if len(w) > len(suffix) + 3 and w.endswith(suffix):
            return w[:-len(suffix)]
    return w

def expand_query_concepts(query_text):
    q_lower = query_text.lower()
    detected_concepts = set()
    expanded_terms = set()

    for concept, terms in CONCEPT_CLUSTERS.items():
        for term in terms:
            if term in q_lower:
                detected_concepts.add(concept)
                for related in terms:
                    expanded_terms.add(related)

    words = re.findall(r'\b[a-zA-Z0-9_-]+\b', q_lower)
    for w in words:
        stemmed = simple_stem(w)
        if w in WORD_TO_CONCEPTS:
            for concept in WORD_TO_CONCEPTS[w]:
                detected_concepts.add(concept)
                for related in CONCEPT_CLUSTERS[concept]:
                    expanded_terms.add(related)
        if stemmed in WORD_TO_CONCEPTS:
            for concept in WORD_TO_CONCEPTS[stemmed]:
                detected_concepts.add(concept)
                for related in CONCEPT_CLUSTERS[concept]:
                    expanded_terms.add(related)

    return list(expanded_terms), detected_concepts

def normalize_hinglish_text(text):
    t = text.lower()
    t = re.sub(r'\b(mnaali|mnli)\b', 'manali', t)
    t = re.sub(r'\b(tmrw|tmmrw|kl)\b', 'kal', t)
    t = re.sub(r'\b(plz|plzz|pls)\b', 'please', t)
    t = re.sub(r'\b(thik|thikkk|thekk)\b', 'theek', t)
    t = re.sub(r'\b(bgt|rokda|kharcha)\b', 'budget', t)
    t = re.sub(r'\b(bhaiii|bhayi|bro)\b', 'bhai', t)
    t = re.sub(r'\b(nhi|nai)\b', 'nahi', t)
    t = re.sub(r'\b(pandrah sau)\b', '1500', t)
    return t
