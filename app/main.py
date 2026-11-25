from rag import policy_chain
from sql import menu_chain
from router import router
from small_talk import talk
import streamlit as st


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

st.title("Restaurant Assistant Bot")

query = st.chat_input("Write your query")         

if "messages" not in st.session_state:
    st.session_state["messages"] = []

for message in st.session_state.messages:
    with st.chat_message(message['role']):
        st.markdown(message['content'])

if query:
    with st.chat_message("user"):
        st.markdown(query)
    st.session_state.messages.append({"role": "user", "content": query})          # ← save the question

    response = ask(query)
    with st.chat_message("assistant"):
        st.markdown(response)
    st.session_state.messages.append({"role": "assistant", "content": response})  # ← save the answer


# if __name__ == "__main__":
#     for q in ["hi", "What time do you close on Saturday?", "vegan mains under 11 pounds", "What is the capital of France?"]:
#         print(f"\nQ: {q}\nA: {ask(q)}")            
