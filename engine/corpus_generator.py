"""
Corpus Generator for "Search a Group Chat Properly"
Generates 4,200+ realistic, messy, code-mixed (Hinglish) group chat messages across 6 months
with 8 distinct participants, 3 major concrete decision threads, typos, forwarded text,
and one-word replies.
"""

import json
import random
import os
from datetime import datetime, timedelta

SEED = 42
random.seed(SEED)

PARTICIPANTS = [
    {"name": "Priya", "role": "Organizer/Planner", "style": "structured, asks for money/dates, uses Hinglish and English"},
    {"name": "Rahul", "role": "Enthusiastic instigator", "style": "slang heavy, typos, excitable, bro culture"},
    {"name": "Sneha", "role": "Pragmatic foodie/skeptic", "style": "asks about food, leaves, budget, cautious"},
    {"name": "Rohan", "role": "Logistics & tech", "style": "shares links, coordinates bookings, maps, car details"},
    {"name": "Amit", "role": "Busy / late replier", "style": "short replies, +1, haan, sorry in meetings, ok"},
    {"name": "Neha", "role": "Aesthetic / photographer", "style": "packing lists, cafe recommendations, gift ideas, emojis"},
    {"name": "Vikram", "role": "Negotiator & realist", "style": "bargains, talks about deposits, legal/rules, cost-cutting"},
    {"name": "Pooja", "role": "Peacemaker & summarizer", "style": "polls, resolving disputes, final summaries, supportive"}
]

# Real-world Hinglish chit-chat templates
CHIT_CHAT = [
    ("{p}", "Good morning guys!"),
    ("{p}", "Gm"),
    ("{p}", "koi utha hai kya?"),
    ("{p}", "bhai coffee peena hai"),
    ("{p}", "aaj office aara koi?"),
    ("{p}", "wfh today"),
    ("{p}", "traffic is insane on silk board"),
    ("{p}", "arre yaar Bangalore rain never ends"),
    ("{p}", "kya chal raha hai"),
    ("{p}", "weekend ke kya plans"),
    ("{p}", "koi movie dekhne chal raha?"),
    ("{p}", "Dune rewatch anyone?"),
    ("{p}", "bhai mai abhi utha hu"),
    ("{p}", "lunch order kare?"),
    ("{p}", "biryani mangwao Meghana se"),
    ("{p}", "diet chal rahi hai meri"),
    ("{p}", "lol ek din cheat day kar le"),
    ("{p}", "mai to salad khaa raha hu"),
    ("{p}", "kaunsa salad bhai ghaas phoos mat khao"),
    ("{p}", "gym kaun kaun jaa raha sham ko"),
    ("{p}", "leg day skip nahi karna"),
    ("{p}", "bhai leg day pe death ho jati hai"),
    ("{p}", "check this reel"),
    ("{p}", "[Forwarded]: Bangalore metro green line delay alert for today"),
    ("{p}", "[Forwarded]: 10 signs you need a mountain trip right now"),
    ("{p}", "haha so true"),
    ("{p}", "ded"),
    ("{p}", "lmao"),
    ("{p}", "rofl"),
    ("{p}", "haan"),
    ("{p}", "nope"),
    ("{p}", "k"),
    ("{p}", "ok"),
    ("{p}", "done"),
    ("{p}", "thikkk"),
    ("{p}", "cool"),
    ("{p}", "sortedd"),
    ("{p}", "sahi hai"),
    ("{p}", "+1"),
    ("{p}", "same here"),
    ("{p}", "kal milte hai sham ko"),
    ("{p}", "where?"),
    ("{p}", "Indiranagar 12th main"),
    ("{p}", "Third Wave chalte hai"),
    ("{p}", "waha parking nahi milti"),
    ("{p}", "cab kar lena bhai"),
    ("{p}", "uber prices are crazy high"),
    ("{p}", "rapido zindabad"),
    ("{p}", "barish me rapido kon leta hai bhai bheeg jayega"),
    ("{p}", "raincoat pehan ke jao lol"),
    ("{p}", "guys ek quick question"),
    ("{p}", "bolo"),
    ("{p}", "sun na"),
    ("{p}", "haan bol jaldi"),
    ("{p}", "ek badia mechanical keyboard suggest karo under 5k"),
    ("{p}", "Keychron K2 lele chup chap"),
    ("{p}", "Rk84 is better value for money"),
    ("{p}", "brown switches lena blue bohot shor machate hai"),
    ("{p}", "haan office call pe sab mute karne bolte hai"),
    ("{p}", "haha true that"),
    ("{p}", "meeting started bye"),
    ("{p}", "brb in 30 mins"),
    ("{p}", "client call extended, hate Mondays"),
    ("{p}", "Monday blues are real"),
    ("{p}", "Friday kab aayega bhai"),
    ("{p}", "abhi to Tuesday hi hua hai"),
    ("{p}", "pain"),
    ("{p}", "sed lyf"),
    ("{p}", "<image omitted: swiggy_order.jpg>"),
    ("{p}", "<voice note 0:12>"),
    ("{p}", "<voice note 0:24>"),
    ("{p}", "kya bola voice note me koi summarize karo"),
    ("{p}", "bol raha hai kal time se aana"),
    ("{p}", "haha mai kabhi late nahi hota"),
    ("{p}", "sabse pehle tu hi late hota hai Amit lol"),
    ("{p}", "call out ho gaya seedha"),
    ("{p}", "sham ko badminton chalte hai playo pe court book kar du?"),
    ("{p}", "slot available hai 8 to 9 pm"),
    ("{p}", "count me in"),
    ("{p}", "mai aa raha hu"),
    ("{p}", "shoes leke aana"),
    ("{p}", "rackets mere paas 2 hai extra"),
    ("{p}", "perfect scene hai"),
    ("{p}", "chalo milte hai"),
    ("{p}", "aaj bohot thand hai yaar"),
    ("{p}", "Bangalore weather is best though"),
    ("{p}", "better than Mumbai humidity"),
    ("{p}", "Delhi pollution se to lakh guna better hai"),
    ("{p}", "sach me AQI 400+ ho gaya waha"),
    ("{p}", "ghar wale bol rahe the bahar nikalna mushkil hai"),
    ("{p}", "take care everyone"),
    ("{p}", "chai peete hai chalo"),
    ("{p}", "tapri pe 5 min me aao"),
    ("{p}", "already reached where are you guys"),
    ("{p}", "2 mins away"),
    ("{p}", "Google maps bol raha 4 mins"),
    ("{p}", "on the way")
]

# Typo variations to inject messiness
TYPOS = {
    "tomorrow": ["tmrw", "tmmrw", "kal", "kl"],
    "please": ["plz", "plzz", "please", "pls"],
    "manali": ["manali", "mnaali", "mnli"],
    "budget": ["bgt", "kharcha", "rokda", "budget"],
    "meeting": ["mtg", "meetin", "call"],
    "theek": ["thik", "thikkk", "theek", "thekk"],
    "achha": ["acha", "achha", "achhaa"],
    "kuch": ["kch", "kuch", "kchbhi"],
    "bahut": ["bohot", "bht", "boht"],
    "nahi": ["nhi", "nai", "nahi"],
    "bhai": ["bhaiii", "bhayi", "bro", "bhai"]
}

def inject_noise(text):
    words = text.split()
    new_words = []
    for w in words:
        low = w.lower()
        if low in TYPOS and random.random() < 0.25:
            new_words.append(random.choice(TYPOS[low]))
        else:
            new_words.append(w)
    return " ".join(new_words)

def generate_corpus():
    start_date = datetime(2025, 10, 1, 9, 0, 0)
    end_date = datetime(2026, 3, 31, 23, 0, 0)
    total_seconds = int((end_date - start_date).total_seconds())

    # Define 3 Concrete Decision Threads with ground truth markers
    # Thread 1: Manali Trip (Oct 15 - Nov 20, 2025)
    trip_thread = [
        {"sender": "Rahul", "time_offset": 14 * 86400 + 36000, "text": "Guys end of year break me kahi chalte hai na, bohot burnout ho gaya"},
        {"sender": "Sneha", "time_offset": 14 * 86400 + 36300, "text": "Goa chalte hai beach pe chill karenge"},
        {"sender": "Rohan", "time_offset": 14 * 86400 + 36600, "text": "Goa December me overcrowded aur double expensive hota hai bro"},
        {"sender": "Priya", "time_offset": 14 * 86400 + 37200, "text": "True, Goa flights are 18k return right now. What about Himachal?"},
        {"sender": "Neha", "time_offset": 14 * 86400 + 37500, "text": "Snow dekhna hai mujhe! Manali ya Kasol?"},
        {"sender": "Vikram", "time_offset": 14 * 86400 + 38000, "text": "Budget kitna hoga per head? Pehle max ceiling decide karo"},
        {"sender": "Pooja", "time_offset": 14 * 86400 + 38500, "text": "Poll daalti hu dates and destination ke liye"},
        {"sender": "Amit", "time_offset": 14 * 86400 + 39000, "text": "+1 for mountains, Goa is too loud"},
        {"sender": "Rohan", "time_offset": 22 * 86400 + 72000, "text": "Looked up 4 cottages in Old Manali near Clubhouse road, wooden interiors and bonfire scene"},
        {"sender": "Priya", "time_offset": 22 * 86400 + 72500, "text": "Old Manali wooden cottage is 32k for 4 nights total for all 8 of us. Super reasonable"},
        {"sender": "Sneha", "time_offset": 22 * 86400 + 72800, "text": "Dates confirm karo boss, mujhe leaves apply karni hai portal pe"},
        {"sender": "Pooja", "time_offset": 22 * 86400 + 73100, "text": "December 18 to December 23 is winning the poll with 7 votes"},
        {"sender": "Vikram", "time_offset": 22 * 86400 + 73500, "text": "Per person budget ₹9,500 me sab ho jayega including Delhi to Chandigarh cab"},
        # CRUCIAL DECISION MOMENT (Zero keyword overlap with "When did we decide on the vacation?")
        {"sender": "Priya", "time_offset": 23 * 86400 + 75000, "text": "chalo pahad pakka final karte hai ticket book karoongi mai aaj", "is_key": "DECIDE_MANALI_TRIP"},
        {"sender": "Rahul", "time_offset": 23 * 86400 + 75200, "text": "YEAHHH sorted! Himachal it is!"},
        {"sender": "Amit", "time_offset": 23 * 86400 + 75400, "text": "Done deal"},
        {"sender": "Neha", "time_offset": 23 * 86400 + 75600, "text": "Yayyy jacket shopping shuru karte hai!"},
        {"sender": "Rohan", "time_offset": 24 * 86400 + 36000, "text": "Chandigarh to Old Manali tempo traveler booked, driver details sent on email", "is_key": "CAB_BOOKING_DETAILS"},
        {"sender": "Priya", "time_offset": 24 * 86400 + 37000, "text": "Sab log ₹3,000 advance GPay kar do mujhe for hotel and cab booking", "is_key": "TRIP_ADVANCE_AMOUNT"}
    ]

    # Thread 2: 3BHK Flat Hunting & Lease Agreement (Dec 1, 2025 - Jan 10, 2026)
    flat_thread = [
        {"sender": "Vikram", "time_offset": 62 * 86400 + 36000, "text": "Guys January se current lease khatam ho rahi hai, we need a 3BHK in Indiranagar or HSR"},
        {"sender": "Rohan", "time_offset": 62 * 86400 + 37000, "text": "Indiranagar near 80ft road would be central for everyone's offices"},
        {"sender": "Rahul", "time_offset": 62 * 86400 + 38000, "text": "bhai 3BHK Indiranagar me kidney mangte hai deposit me"},
        {"sender": "Vikram", "time_offset": 68 * 86400 + 40000, "text": "Visited 3 places today with broker Srinivas. First one in 6th main is asking 68k, second is 62k plus maintenance"},
        {"sender": "Pooja", "time_offset": 68 * 86400 + 40500, "text": "Balcony kisme badia hai? Natural sunlight is mandatory"},
        {"sender": "Vikram", "time_offset": 68 * 86400 + 41000, "text": "The 62k one has huge east facing balcony, 2 car parkings, and power backup"},
        {"sender": "Sneha", "time_offset": 68 * 86400 + 41500, "text": "Did you ask about pets? Neha might bring her cat sometimes"},
        # KEY MOMENT: Pet restriction (Zero keyword overlap with "What is the pet policy for the new apartment?")
        {"sender": "Vikram", "time_offset": 68 * 86400 + 42000, "text": "owner ne bola billi kutte allow nahi karenge flat ke andar", "is_key": "PET_POLICY"},
        {"sender": "Neha", "time_offset": 68 * 86400 + 42300, "text": "Aww man that sucks, but the flat looks gorgeous"},
        {"sender": "Rahul", "time_offset": 70 * 86400 + 45000, "text": "Rent bargain hua kya? Try pushing for 58k or 60k flat"},
        {"sender": "Vikram", "time_offset": 71 * 86400 + 50000, "text": "Broker agreed at ₹60,000 including maintenance, deposit is 5 months down to 3 lakhs"},
        # KEY MOMENT: Deposit paid (Zero keyword overlap with "Who paid the rental deposit?")
        {"sender": "Vikram", "time_offset": 72 * 86400 + 54000, "text": "broker ko token advance bhej diya maine kal sham ko receipt bhi aagayi", "is_key": "FLAT_DEPOSIT_PAID"},
        {"sender": "Rohan", "time_offset": 72 * 86400 + 54300, "text": "Lease starts Jan 15th, agreement draft will come on Monday", "is_key": "LEASE_START_DATE"},
        {"sender": "Amit", "time_offset": 72 * 86400 + 55000, "text": "House warming party kab hai fir?"}
    ]

    # Thread 3: Surprise Farewell & Reunion Gift (Feb 10 - Mar 25, 2026)
    gift_thread = [
        {"sender": "Neha", "time_offset": 133 * 86400 + 36000, "text": "Guys listen, Amit is leaving for his UK masters next month! We need to plan a proper send-off surprise!"},
        {"sender": "Sneha", "time_offset": 133 * 86400 + 36500, "text": "Omg yes! He has no idea we are planning anything, don't mention in the other group"},
        {"sender": "Priya", "time_offset": 133 * 86400 + 37000, "text": "What gift should we get him? Something he will actually use every day there"},
        {"sender": "Rahul", "time_offset": 134 * 86400 + 40000, "text": "Noise cancelling headphones! London tube me ro ro ke commute karega bina ANC ke"},
        {"sender": "Rohan", "time_offset": 134 * 86400 + 41000, "text": "Sony XM5 vs Bose QuietComfort? Sony has better battery for long international flights"},
        {"sender": "Pooja", "time_offset": 134 * 86400 + 42000, "text": "Sony XM5 is currently on card discount for ₹24,000 on Amazon"},
        {"sender": "Vikram", "time_offset": 135 * 86400 + 44000, "text": "If 7 of us pitch in, plus cake and dinner decoration, what is the split?"},
        # KEY MOMENT: Contribution amount (Zero keyword overlap with "How much did each person contribute for the farewell gift?")
        {"sender": "Priya", "time_offset": 135 * 86400 + 45000, "text": "sab log pandrah sau gpay kar do priya ke number pe", "is_key": "GIFT_CONTRIBUTION"},
        {"sender": "Rahul", "time_offset": 135 * 86400 + 45300, "text": "Sent 1500 to Priya UPI ref 93849"},
        {"sender": "Sneha", "time_offset": 135 * 86400 + 45600, "text": "Transferred ₹1,500 done"},
        {"sender": "Rohan", "time_offset": 140 * 86400 + 48000, "text": "Sony WH-1000XM5 black color order kar diya hai Amazon se Friday ko deliver hoga", "is_key": "GIFT_ORDER_CONFIRMED"},
        {"sender": "Neha", "time_offset": 145 * 86400 + 50000, "text": "Custom cake with passport and aeroplane design ordered from Magnolia Bakery", "is_key": "CAKE_DETAILS"},
        {"sender": "Pooja", "time_offset": 148 * 86400 + 52000, "text": "Skydeck rooftop table booked for 8:30 PM on Saturday 28th", "is_key": "FAREWELL_VENUE_DATE"}
    ]

    thread_items = []
    for item in trip_thread:
        thread_items.append((start_date + timedelta(seconds=item["time_offset"]), item["sender"], item["text"], item.get("is_key", None), "manali_trip"))
    for item in flat_thread:
        thread_items.append((start_date + timedelta(seconds=item["time_offset"]), item["sender"], item["text"], item.get("is_key", None), "flat_hunt"))
    for item in gift_thread:
        thread_items.append((start_date + timedelta(seconds=item["time_offset"]), item["sender"], item["text"], item.get("is_key", None), "farewell_gift"))

    # Additional ground-truth milestones
    random_events = [
        (datetime(2025, 11, 1, 10, 0), "Pooja", "Happy Diwali everyone! Ghar kab jaa rahe sab?", "DIWALI_CHAT"),
        (datetime(2025, 11, 2, 19, 2), "Amit", "Diwali bonus aagaya company se finally", "DIWALI_BONUS"),
        (datetime(2025, 11, 2, 19, 10), "Amit", "Flat 40k after tax deduction credited", "BONUS_AMOUNT"),
        (datetime(2026, 1, 1, 0, 1), "Priya", "HAPPY NEW YEAR FAM!! ❤️🎉", "NEW_YEAR_WISH"),
        (datetime(2026, 1, 1, 0, 5), "Rohan", "New year resolution: no deploying to prod on Friday", "NEW_YEAR_RESOLUTION"),
        (datetime(2025, 10, 8, 14, 20), "Sneha", "Guys meri leaves 15th to 20th November ke beech blocked hai audit ke chakkar me", "SNEHA_LEAVE_RESTRICTION"),
        (datetime(2025, 10, 12, 11, 15), "Rohan", "Meri bike servicing pe gayi hai 3 din ke liye", "ROHAN_BIKE_SERVICE"),
        (datetime(2025, 11, 8, 16, 45), "Priya", "Emergency fund reminder: always keep 6 months expenses in liquid fund", "PRIYA_FINANCIAL_ADVICE"),
        (datetime(2025, 11, 15, 20, 10), "Rahul", "bhai FIFA tournament rakhte hai weekend pe mere flat pe", "RAHUL_FIFA"),
        (datetime(2025, 11, 28, 13, 30), "Vikram", "Zomato gold renew kar liya 30 rupay me coupon laga ke", "VIKRAM_SAVINGS_HACK"),
        (datetime(2025, 12, 10, 17, 0), "Sneha", "The new ramen place near 12th main Indiranagar has the best spicy miso", "SNEHA_RAMEN_REC"),
        (datetime(2026, 1, 18, 15, 30), "Amit", "Switched to standing desk, lower back pain drastically reduced", "AMIT_HEALTH_UPDATE"),
        (datetime(2026, 1, 22, 18, 45), "Priya", "Don't forget to submit tax saving investment proofs before Jan 25th", "PRIYA_TAX_REMINDER"),
        (datetime(2026, 2, 5, 12, 10), "Neha", "Found an amazing thrift store in Koramangala for vintage jackets", "NEHA_THRIFT_STORE"),
        (datetime(2026, 2, 14, 21, 0), "Rahul", "Valentine's day pe Zomato delivery boy ko 100 rs tip diya, he looked so happy", "RAHUL_VALENTINE_TIP"),
        (datetime(2026, 3, 5, 16, 20), "Vikram", "Home loan interest rates reduced by 15 bps today", "VIKRAM_FINANCE_NEWS"),
        (datetime(2026, 3, 15, 19, 45), "Sneha", "Holi ke colors organic hi khareedna skin allergy ho jati hai chemical se", "SNEHA_HOLI_WARNING")
    ]

    for dt, sender, text, key in random_events:
        thread_items.append((dt, sender, text, key, "event"))

    # Target: 4,250 messages
    target_count = 4250
    delta_step = total_seconds / target_count

    all_raw = []
    for dt, sender, text, key, thread_type in thread_items:
        all_raw.append({"timestamp": dt, "sender": sender, "text": text, "is_key": key, "thread": thread_type})

    for i in range(target_count - len(thread_items)):
        sec_offset = int(i * delta_step + random.randint(-60, 60))
        sec_offset = max(0, min(total_seconds - 1, sec_offset))
        msg_time = start_date + timedelta(seconds=sec_offset)
        hour = msg_time.hour
        if hour < 8:
            msg_time = msg_time.replace(hour=8 + random.randint(0, 3))
        
        participant = random.choice(PARTICIPANTS)["name"]
        template_speaker, text = random.choice(CHIT_CHAT)
        formatted_text = text.replace("{p}", participant)
        
        noisy_text = inject_noise(formatted_text) if not formatted_text.startswith(("[Forwarded]", "<image", "<voice")) else formatted_text

        all_raw.append({
            "timestamp": msg_time,
            "sender": participant,
            "text": noisy_text,
            "is_key": None,
            "thread": "general"
        })

    # Sort strictly chronologically
    all_raw.sort(key=lambda x: x["timestamp"])

    final_messages = []
    keys_map = {}

    for idx, item in enumerate(all_raw):
        mid = 1000 + idx
        msg_obj = {
            "id": mid,
            "timestamp": item["timestamp"].strftime("%Y-%m-%d %H:%M:%S"),
            "iso_timestamp": item["timestamp"].isoformat(),
            "sender": item["sender"],
            "text": item["text"],
            "thread": item["thread"]
        }
        if item.get("is_key"):
            keys_map[item["is_key"]] = mid
            msg_obj["key_marker"] = item["is_key"]
            
        final_messages.append(msg_obj)

    return final_messages, keys_map

def export_whatsapp_text(messages, filepath):
    with open(filepath, "w", encoding="utf-8") as f:
        for m in messages:
            dt = datetime.strptime(m["timestamp"], "%Y-%m-%d %H:%M:%S")
            wa_date = dt.strftime("%d/%m/%y, %H:%M:%S")
            f.write(f"[{wa_date}] {m['sender']}: {m['text']}\n")

if __name__ == "__main__":
    import sys
    out_dir = sys.argv[1] if len(sys.argv) > 1 else "./data"
    os.makedirs(out_dir, exist_ok=True)
    
    print(f"Generating synthetic group chat messages (Seed={SEED})...")
    messages, keys_map = generate_corpus()
    
    json_path = os.path.join(out_dir, "group_chat_data.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(messages, f, indent=2, ensure_ascii=False)
    
    txt_path = os.path.join(out_dir, "group_chat_export.txt")
    export_whatsapp_text(messages, txt_path)
    
    keys_path = os.path.join(out_dir, "ground_truth_keys.json")
    with open(keys_path, "w", encoding="utf-8") as f:
        json.dump(keys_map, f, indent=2)

    print(f"Successfully generated {len(messages)} messages.")
    print(f"Saved JSON: {json_path}")
    print(f"Saved WhatsApp Export: {txt_path}")
    print(f"Key ground truth anchors saved: {keys_map}")
