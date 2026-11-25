from semantic_router import Route, IndexedRouter
from semantic_router.encoders import HuggingFaceEncoder

encoder = HuggingFaceEncoder(name="sentence-transformers/all-MiniLM-L6-v2")

policy = Route(
    name="policy",
    utterances=[
        # opening hours and bookings
        "What time do you open?",
        "Are you open on Mondays?",
        "What time does the kitchen close?",
        "Can I book a table for 10 people?",
        "Do you have a private dining room?",
        "Is there parking nearby?",
        "Can I bring my dog?",
        # allergens and dietary rules
        "Is your meat halal?",
        "Can you make a dish completely nut free?",
        "Do you have gluten free options for coeliacs?",
        # delivery and takeaway
        "Do you deliver to my area?",
        "How much is the delivery fee?",
        "How long does delivery take?",
        "Are you on Deliveroo or Uber Eats?",
        # refunds and cancellations
        "Can I get a refund if my order is missing?",
        "How do I cancel my booking?",
        "How do I make a complaint?",
        # offers
        "Do you have a student discount?",
        "Is there a lunch deal?",
        "How does the loyalty card work?",
        "Can I buy a gift voucher?",
    ],
)

menu = Route(
    name="menu",
    utterances=[
        "Show me vegan mains",
        "Do you have vegetarian options?",
        "What are your cheapest dishes?",
        "Any desserts under 5 pounds?",
        "What is your spiciest dish?",
        "Something mild for kids",
        "Which dishes have paneer?",
        "Do you have anything with chicken?",
        "Show me starters without nuts",
        "What drinks do you have?",
        "Low calorie dishes please",
        "What Mediterranean food do you serve?",
    ],
)

small_talk = Route(
    name="small_talk",
    utterances=[
        "hi",
        "hello",
        "hey there",
        "good evening",
        "how are you?",
        "thank you",
        "thanks a lot",
        "who are you?",
        "what can you do?",
        "bye",
    ],
)

router = IndexedRouter(routes=[policy, menu, small_talk], encoder=encoder)


if __name__ == "__main__":
    tests = [
        "Do you deliver on Sundays?",       # policy
        "Show me spicy mains",              # menu
        "hello",                            # small_talk
        "Do you have vegan options?",       # menu
        "Can I cancel my order?",           # policy
        "Anything with spinach?",           # menu
        "Is the butter chicken halal?",     # policy (halal rules are in the policy documents)
        "Is the butter chicken nut free?",  # tricky: needs the menu AND the allergen policy
    ]
    for q in tests:
        print(f"{q:40} -> {router(q).name}")