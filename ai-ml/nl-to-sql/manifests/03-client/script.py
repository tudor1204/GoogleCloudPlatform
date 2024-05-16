import psycopg
import os
from tabulate import tabulate
from langchain_community.llms import HuggingFaceTextGenInference
from langchain_core.prompts import PromptTemplate

conn = psycopg.connect(
    dbname=os.environ.get("DATABASE_NAME"),
    host=os.environ.get("POSTGRES_URL"),
    user=os.environ.get("OWNERUSERNAME"),
    password=os.environ.get("OWNERPASSWORD"),
    autocommit=True)

db_schema = conn.execute("SELECT table_name, column_name as Columns, data_type as DataTypes FROM  information_schema.columns where table_name NOT LIKE 'pg_stat%' AND table_schema='public' order by table_name,column_name;")
colnames = [desc[0] for desc in db_schema.description]
db_schema_formatted=tabulate(db_schema.fetchall(), headers=colnames, tablefmt='psql')

llm = HuggingFaceTextGenInference(
    inference_server_url=os.environ.get("LLM_ENDPOINT"),
    temperature=0.9,
)

sql_prompt_template = PromptTemplate.from_template("""
<|begin_of_text|><|start_header_id|>system<|end_header_id|>
You are a helpful AI assistant that can transform user queries into SQL commands to retrieve the data from the Postgresql database. The database has the next tables schema:
{db_schema}

Please prepare and return only the SQL command, based on the user query, without any formatting or newlines. The answer must contain only valid SQL command.<|eot_id|><|start_header_id|>user<|end_header_id|>
{query}<|eot_id|><|start_header_id|>assistant<|end_header_id|>
""")

final_prompt_template = PromptTemplate.from_template("""
<|begin_of_text|><|start_header_id|>system<|end_header_id|>
You are a helpful AI assistant that can understand Postgresql replies and explain this data to the user. The database has the next tables schema:
{db_schema}

User query: {query}

Postgresql reply:
{postgres_reply}

Please prepare and return the answer, based on the user question and Postgresql reply. It should be easy to understand your answer. Don't add any introductory words, start answering right away. Keep your answer to a one or two sentences (if possible) that specifically answers the user's question. If not - try to keep the answer short, summarizing the returned data.
If you do not know the answer or Postgres reply is empty, response with "I don't know".
<|eot_id|><|start_header_id|>assistant<|end_header_id|>
""")

def handle_query(query):
    sql_query=llm.invoke(sql_prompt_template.format(db_schema=db_schema_formatted, query=query))
    try:
        postgres_reply = conn.execute(sql_query)
    except psycopg.Error as e:
        print("Unable to process query: ", query)
        return "Try another query"
    colnames = [desc[0] for desc in postgres_reply.description]
    postgres_reply_formatted=tabulate(postgres_reply.fetchall(), headers=colnames, tablefmt='psql')
    # debug section
    # print(sql_query)
    # print(postgres_reply_formatted)
    # end of debug section
    return llm.invoke(final_prompt_template.format(db_schema=db_schema_formatted, query=query, postgres_reply=postgres_reply_formatted))

print(handle_query("Please calculate the total sum of all John transactions."))
print(handle_query("Which woman spent more money in 2023 and how much?"))
print(handle_query("Who let the dogs out?"))
