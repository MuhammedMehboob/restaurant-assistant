from rag import policy_chain
from sql import menu_chain
from router import router
from small_talk import talk

def ask(query):
    route = router(query).name

    if route== 'policy':
        answer, sources = policy_chain(query)
        reply = answer
        if sources:
            reply = reply + "\n\nSources: " + ", ".join(sources)
    elif route == 'menu':
        reply = menu_chain(query)
    elif route == 'small_talk':
        reply = talk(query)
    else:
        reply = "Sorry, I didn't understand that."    

    return reply    
            
if __name__ == "__main__":
    for q in ["hi", "What time do you close on Saturday?", "vegan mains under 11 pounds", "What is the capital of France?"]:
        print(f"\nQ: {q}\nA: {ask(q)}")            
