from pathlib import Path
from langchain_text_splitters import RecursiveCharacterTextSplitter
import chromadb
from chromadb.utils import embedding_functions
import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()
groq_client = Groq()

ef = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

BASE_FILE = Path(__file__).parent
FILES = BASE_FILE/"data"/"policies"

splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)

docs = []

for files in FILES.glob("*.txt"):
    content = files.read_text(encoding="utf-8")
    source = files.stem
    to_append = {"text":content, "source": source}
    docs.append(to_append)

chunks = []

for doc in docs:
    pieces = splitter.split_text(doc["text"])
    for piece in pieces:
        chunks.append({"text":piece,"source":doc["source"]})

print(len(chunks), "chunks")
print(chunks[0])

chroma_client = chromadb.PersistentClient(path=str(BASE_FILE / "chroma_db"))
collection = chroma_client.get_or_create_collection(name="policies", embedding_function=ef)

if collection.count() > 0:
    print("Already ingested")
else:
    collection.add(
        documents= [chunk['text'] for chunk in chunks],
        metadatas=[{"source": chunk["source"]} for chunk in chunks],
        ids = [ f"id_{i}" for i in range(len(chunks))]
    )

    print(f"added {len(chunks)} chunks")

def policy_chain(question):
    results =   collection.query(query_texts=[question], n_results=3)

    texts = []
    sources = []
    for text, meta, dist in zip(results['documents'][0], results['metadatas'][0], results['distances'][0]):
        if dist<0.6:
            texts.append(text) 
            sources.append(meta['source'])
        
    if not texts:
        return "I dont know based on our restaurant policies", []
    context = "\n\n".join(texts) 

    prompt = f""" you are an freindly restaurant assistant who replies to user queries bases upon the context,
            you need to answer only based upon the context,if you dont know say I dont know based on our restaurant policies. 

            Context:{context}

            Question: {question}"""
    

    completion = groq_client.chat.completions.create(
    model=os.environ["GROQ_MODEL"],
    messages=[{"role": "user", "content": prompt}],
    temperature=0.2,
    max_tokens=1024,
    ) 
    answer = completion.choices[0].message.content

    return answer,list(dict.fromkeys(sources))


tests = [
    "Is your chicken halal?",
    "What time do you close on Saturday?",
    "Can I cancel my delivery order?",
    "Do students get a discount on Friday?",
    "What is the capital of France?",
]
for q in tests:
    answer, sources = policy_chain(q)
    print(f"\nQ: {q}\nA: {answer}\nSources: {sources}")