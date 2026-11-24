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
    
   

sql_prompt = """
            you are a sql prompt generator as per the users question, when user asks a quesiton you need to generate the sql query which 
            then can be directly used quire sql of menu.db, where columns are category: one of starter, main, side, dessert, drink
price: in GBP (£)
is_vegetarian, is_vegan, contains_nuts, contains_gluten, contains_dairy: 1 = yes, 0 = no
spice_level: 0 (not spicy) to 3 (hot)
cuisine: Indian, Mediterranean or British.

The rules:
Return only the SQL, inside <SQL></SQL> tags.
Always use SELECT *.
Use LIKE '%...%' when searching dish names, since customers won't type exact names.
Always add LIMIT 10.
If the question isn't about the menu, return <SQL>NONE</SQL>.
When searching for a dish or ingredient, always search BOTH name and description, like this:
  WHERE (name LIKE '%word%' OR description LIKE '%word%')
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

for q in [
    "vegan mains under 11 pounds",
    "what is your spiciest dish?",
    "desserts without nuts",
    "anything with paneer?",
    "anything with spinach?",
    "what time do you open?",
]:
    print(q, "->", generate_sql(q))