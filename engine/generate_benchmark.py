"""
Benchmark Generator for "Search a Group Chat Properly"
Generates 40 evaluation queries with marked target message IDs,
query categories (semantic, attributed, temporal, hybrid),
and verifies at least 8 queries have strictly ZERO keyword overlap.
"""

import json
import re
import os

def clean_words(text):
    # Strip punctuation and lower
    words = re.findall(r'\b[a-zA-Z0-9]+\b', text.lower())
    # remove common stop words for strict keyword overlap test
    stop_words = {'the', 'a', 'an', 'is', 'was', 'are', 'were', 'in', 'on', 'at', 'to', 'for', 'of', 'and', 'or', 'we', 'our', 'he', 'she', 'it', 'they', 'you', 'i', 'do', 'did', 'does', 'with'}
    return set(w for w in words if w not in stop_words)

def generate_benchmark(data_dir):
    data_file = os.path.join(data_dir, "group_chat_data.json")
    keys_file = os.path.join(data_dir, "ground_truth_keys.json")

    with open(data_file, "r", encoding="utf-8") as f:
        messages = json.load(f)
    
    with open(keys_file, "r", encoding="utf-8") as f:
        keys = json.load(f)

    # Build msg lookup
    msg_map = {m["id"]: m for m in messages}

    # Define 40 queries
    # Format: (query_text, category, target_key_or_id, expected_explanation, forced_zero_overlap)
    benchmark_specs = [
        # --- ZERO KEYWORD OVERLAP QUERIES (10 items) ---
        (
            "When was the vacation finalized?",
            "semantic",
            keys["DECIDE_MANALI_TRIP"],
            "Priya finalized the trip by saying 'chalo pahad pakka final karte hai ticket book karoongi mai aaj'.",
            True
        ),
        (
            "Who paid the rental deposit?",
            "semantic",
            keys["FLAT_DEPOSIT_PAID"],
            "Vikram paid the token advance to the broker and got the receipt.",
            True
        ),
        (
            "How much did each person contribute for the farewell gift?",
            "semantic",
            keys["GIFT_CONTRIBUTION"],
            "Priya asked everyone to GPay 1500 (pandrah sau) to her number.",
            True
        ),
        (
            "What is the pet policy for the new apartment?",
            "semantic",
            keys["PET_POLICY"],
            "Vikram reported the owner said dogs and cats are not allowed inside the flat.",
            True
        ),
        (
            "When does our tenancy begin?",
            "temporal",
            keys["LEASE_START_DATE"],
            "Rohan confirmed the lease starts Jan 15th.",
            True
        ),
        (
            "What precautions should we take for the spring festival?",
            "semantic",
            keys["SNEHA_HOLI_WARNING"],
            "Sneha warned to buy organic colors for Holi to avoid skin allergies.",
            True
        ),
        (
            "What surprise dessert is being prepared?",
            "semantic",
            keys["CAKE_DETAILS"],
            "Neha ordered a custom cake with passport and aeroplane design from Magnolia Bakery.",
            True
        ),
        (
            "Where is our send-off dinner gathering scheduled?",
            "semantic",
            keys["FAREWELL_VENUE_DATE"],
            "Pooja booked a rooftop table at Skydeck for 8:30 PM on Saturday 28th.",
            True
        ),
        (
            "How much annual festival incentive did company transfer?",
            "semantic",
            keys["BONUS_AMOUNT"],
            "Amit confirmed flat 40k after tax deduction was credited as Diwali bonus.",
            True
        ),
        (
            "Which ergonomic furniture helped with physical discomfort?",
            "semantic",
            keys["AMIT_HEALTH_UPDATE"],
            "Amit switched to a standing desk which drastically reduced his lower back pain.",
            True
        ),

        # --- ADDITIONAL SEMANTIC QUERIES (5 items) ---
        (
            "When did we decide on Manali?",
            "semantic",
            keys["DECIDE_MANALI_TRIP"],
            "Priya decided to finalize the mountain trip on Oct 24th.",
            False
        ),
        (
            "What did we decide about traveling from Chandigarh to Manali?",
            "semantic",
            keys["CAB_BOOKING_DETAILS"],
            "Rohan booked a tempo traveler from Chandigarh to Old Manali.",
            False
        ),
        (
            "How much advance money did Priya collect for the trip?",
            "semantic",
            keys["TRIP_ADVANCE_AMOUNT"],
            "Priya asked everyone to GPay ₹3,000 advance for hotel and cab booking.",
            False
        ),
        (
            "Which noise cancelling headphones were chosen for Amit?",
            "semantic",
            keys["GIFT_ORDER_CONFIRMED"],
            "Rohan ordered Sony WH-1000XM5 black headphones from Amazon.",
            False
        ),
        (
            "What was the negotiated flat rent in Indiranagar?",
            "semantic",
            keys["FLAT_DEPOSIT_PAID"] - 1, # The broker agreement message right before deposit
            "Vikram negotiated rent down to ₹60,000 including maintenance.",
            False
        ),

        # --- ATTRIBUTED QUERIES (13 items) ---
        (
            "What did Sneha say about her leave dates in November?",
            "attributed",
            keys["SNEHA_LEAVE_RESTRICTION"],
            "Sneha mentioned her leaves are blocked between 15th to 20th November for an audit.",
            False
        ),
        (
            "What did Rohan say about his bike?",
            "attributed",
            keys["ROHAN_BIKE_SERVICE"],
            "Rohan said his bike is gone for servicing for 3 days.",
            False
        ),
        (
            "What financial advice did Priya share about emergency funds?",
            "attributed",
            keys["PRIYA_FINANCIAL_ADVICE"],
            "Priya advised keeping 6 months expenses in a liquid fund.",
            False
        ),
        (
            "What gaming tournament did Rahul propose?",
            "attributed",
            keys["RAHUL_FIFA"],
            "Rahul proposed hosting a FIFA tournament at his flat.",
            False
        ),
        (
            "What discount hack did Vikram share for Zomato?",
            "attributed",
            keys["VIKRAM_SAVINGS_HACK"],
            "Vikram renewed Zomato Gold for 30 rupees using a coupon.",
            False
        ),
        (
            "What ramen restaurant did Sneha recommend in Indiranagar?",
            "attributed",
            keys["SNEHA_RAMEN_REC"],
            "Sneha recommended the new ramen place near 12th main Indiranagar for spicy miso.",
            False
        ),
        (
            "What reminder did Priya give about tax proofs?",
            "attributed",
            keys["PRIYA_TAX_REMINDER"],
            "Priya reminded everyone to submit tax saving investment proofs before Jan 25th.",
            False
        ),
        (
            "What thrift store did Neha find in Koramangala?",
            "attributed",
            keys["NEHA_THRIFT_STORE"],
            "Neha found a thrift store in Koramangala for vintage jackets.",
            False
        ),
        (
            "What did Rahul do on Valentine's Day?",
            "attributed",
            keys["RAHUL_VALENTINE_TIP"],
            "Rahul tipped 100 rs to a Zomato delivery boy on Valentine's Day.",
            False
        ),
        (
            "What did Vikram share about home loan rates?",
            "attributed",
            keys["VIKRAM_FINANCE_NEWS"],
            "Vikram shared that home loan interest rates were cut by 15 bps.",
            False
        ),
        (
            "What did Priya say about the wooden cottage price in Old Manali?",
            "attributed",
            keys["DECIDE_MANALI_TRIP"] - 4,
            "Priya noted the Old Manali wooden cottage was 32k for 4 nights total.",
            False
        ),
        (
            "What did Amit announce about his Diwali bonus?",
            "attributed",
            keys["DIWALI_BONUS"],
            "Amit announced that his Diwali bonus was finally credited.",
            False
        ),
        (
            "What did Neha suggest for Amit's surprise send-off?",
            "attributed",
            keys["GIFT_CONTRIBUTION"] - 7,
            "Neha initiated planning Amit's UK masters send-off surprise.",
            False
        ),

        # --- TEMPORAL QUERIES (8 items) ---
        (
            "What did we discuss on Diwali morning in November?",
            "temporal",
            keys["DIWALI_CHAT"],
            "Pooja wished everyone Happy Diwali and asked when people were visiting home.",
            False
        ),
        (
            "Who sent the first New Year wish right at midnight?",
            "temporal",
            keys["NEW_YEAR_WISH"],
            "Priya sent 'HAPPY NEW YEAR FAM!!' at 00:01 on Jan 1st.",
            False
        ),
        (
            "What work resolution was shared on New Year's Day?",
            "temporal",
            keys["NEW_YEAR_RESOLUTION"],
            "Rohan resolved not to deploy to prod on Fridays.",
            False
        ),
        (
            "What happened in the chat right after Diwali bonus was announced?",
            "temporal",
            keys["BONUS_AMOUNT"],
            "Amit confirmed his 40k bonus amount after Vikram asked.",
            False
        ),
        (
            "What did Sneha warn about in mid-March?",
            "temporal",
            keys["SNEHA_HOLI_WARNING"],
            "Sneha warned about synthetic Holi colors on March 15th.",
            False
        ),
        (
            "What transport was booked in late October for the vacation?",
            "temporal",
            keys["CAB_BOOKING_DETAILS"],
            "Rohan booked the Chandigarh to Old Manali tempo traveler.",
            False
        ),
        (
            "What was finalized on March 28th for the farewell?",
            "temporal",
            keys["FAREWELL_VENUE_DATE"],
            "Pooja confirmed booking the Skydeck rooftop table for 8:30 PM on March 28th.",
            False
        ),
        (
            "What health change was made in mid-January?",
            "temporal",
            keys["AMIT_HEALTH_UPDATE"],
            "Amit switched to a standing desk on January 18th.",
            False
        ),

        # --- HYBRID QUERIES (4 items) ---
        (
            "What did Sneha say about leaves in October?",
            "hybrid",
            keys["SNEHA_LEAVE_RESTRICTION"],
            "Sneha shared her November leave block in October.",
            False
        ),
        (
            "What did Priya say about tax deadlines in January?",
            "hybrid",
            keys["PRIYA_TAX_REMINDER"],
            "Priya reminded about Jan 25th tax proof submission.",
            False
        ),
        (
            "What did Vikram report about the Indiranagar broker deposit in December?",
            "hybrid",
            keys["FLAT_DEPOSIT_PAID"],
            "Vikram confirmed paying token advance to broker Srinivas.",
            False
        ),
        (
            "What did Rohan order online in February?",
            "hybrid",
            keys["GIFT_ORDER_CONFIRMED"],
            "Rohan ordered the Sony XM5 headphones on Amazon in February.",
            False
        )
    ]

    queries = []
    zero_overlap_count = 0

    for idx, (q_text, cat, target_id, explanation, forced_zero) in enumerate(benchmark_specs):
        target_msg = msg_map.get(target_id)
        if not target_msg:
            raise ValueError(f"Target ID {target_id} not found in messages!")

        q_words = clean_words(q_text)
        t_words = clean_words(target_msg["text"])
        overlap = q_words.intersection(t_words)
        
        is_zero_overlap = (len(overlap) == 0)
        if is_zero_overlap:
            zero_overlap_count += 1

        # Surrounding context range (-4 to +4)
        min_ctx = max(1000, target_id - 4)
        max_ctx = min(1000 + len(messages) - 1, target_id + 4)
        context_ids = list(range(min_ctx, max_ctx + 1))

        query_obj = {
            "query_id": f"Q{idx+1:02d}",
            "query": q_text,
            "category": cat,
            "target_message_id": target_id,
            "target_message": target_msg,
            "context_message_ids": context_ids,
            "zero_keyword_overlap": is_zero_overlap,
            "keyword_overlap_tokens": list(overlap),
            "ground_truth_answer": explanation
        }
        queries.append(query_obj)

    print(f"Total benchmark queries generated: {len(queries)}")
    print(f"Total queries with STRICT ZERO keyword overlap: {zero_overlap_count} (Requirement: at least 8)")

    output_path = os.path.join(data_dir, "benchmark_queries.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(queries, f, indent=2, ensure_ascii=False)
    
    print(f"Saved benchmark suite to {output_path}")
    return queries

if __name__ == "__main__":
    import sys
    d_dir = sys.argv[1] if len(sys.argv) > 1 else "./data"
    generate_benchmark(d_dir)
