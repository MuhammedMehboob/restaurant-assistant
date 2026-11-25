import pandas as pd
from pathlib import Path
import sqlite3
import re
import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()
groq_client = Groq()

BASE_FILE = Path(__file__).parent
FILES = BASE_FILE/"data"/"menu.csv"

df  = pd.read_csv(FILES)

db_path = BASE_FILE / "menu.db"

with sqlite3.connect(db_path) as conn:
    df.to_sql("menu", conn, if_exists="replace", index=False)  
    
   

sql_prompt = """You convert a customer's question about a restaurant menu into a single SQLite query.

Table: menu
Columns:
- dish_id: integer, unique ID of the dish
- name: text, the dish name (e.g. "Butter Chicken", "Vegetable Samosa (2 pcs)")
- category: text, one of: starter, main, side, dessert, drink
- cuisine: text, one of: Indian, Mediterranean, British
- price: number, price in GBP (£)
- is_vegetarian: 1 = yes, 0 = no
- is_vegan: 1 = yes, 0 = no
- spice_level: integer from 0 to 3 (0 = not spicy, 1 = mild, 2 = medium, 3 = hot)
- calories: integer, calories per portion
- contains_nuts: 1 = yes, 0 = no
- contains_gluten: 1 = yes, 0 = no
- contains_dairy: 1 = yes, 0 = no
- description: text, a short description of the dish and its main ingredients

Rules:
- Always use SELECT * FROM menu.
- When searching for a dish or ingredient, always search BOTH name and description, like this:
  WHERE (name LIKE '%word%' OR description LIKE '%word%')- "Spicy" means spice_level >= 2. "Mild" means spice_level <= 1.
- "Mains" means category = 'main'.
- Always end the query with LIMIT 10.
- If the question is not about the menu, do not write SQL. Reply only with <SQL>NONE</SQL>.
- Return only the SQL query inside <SQL></SQL> tags, with no explanation.
"""


def generate_sql(question):
    completion = groq_client.chat.completions.create(
        model=os.environ["GROQ_MODEL"],
        messages=[
            {"role": "system", "content": sql_prompt},
            {"role": "user", "content": question},
        ],
        temperature=0,
        max_tokens=1024,
    )

    reply = completion.choices[0].message.content

    matches = re.findall(r"<SQL>(.*?)</SQL>", reply, re.DOTALL)
    if not matches or matches[0].strip().upper() == "NONE":
        return None
    return matches[0].strip()





def run_query(sql):
    if not sql.strip().upper().startswith("SELECT"):
        return None
    with sqlite3.connect(db_path) as conn:
        return pd.read_sql_query(sql, conn)


answer_prompt = """You are a friendly assistant for the Saffron & Olive restaurant.
You will be given a customer's question and the matching dishes from the menu.
Answer using only these dishes. List each dish on its own line as:
Dish name - £price (vegetarian/vegan if applicable, spice level if relevant): short description
If no dishes are given, say that nothing on the menu matches."""

def menu_chain(question):
    sql = generate_sql(question)

    if sql is None:
        return "Sorry, I can only help with questions about our menu."
    
    sql_answer = run_query(sql)
    if sql_answer is None:
        return "Sorry, I couldn't search the menu for that."
    if sql_answer.empty:
        return "Sorry, nothing on our menu matches that."
    
    data = sql_answer.to_dict(orient="records")    

    completion = groq_client.chat.completions.create(
        model=os.environ["GROQ_MODEL"],
        messages=[
            {"role": "system", "content": answer_prompt},
            {"role": "user", "content": f"Question: {question}\nDishes: {data}"},
        ],
        temperature=0.2,
        max_tokens=1024,
    )
    return completion.choices[0].message.content    

if __name__ == "__main__":
    for q in ["vegan mains under 11 pounds", "anything with spinach?", "vegan dishes with lamb", "what time do you open?"]:
        print(f"\nQ: {q}\nA: {menu_chain(q)}")

