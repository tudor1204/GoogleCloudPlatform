from langchain_google_vertexai import VertexAIEmbeddings
from langchain_google_vertexai import VertexAI
from langchain_qdrant import Qdrant
from langchain_community.document_loaders import JSONLoader
import os
import random
from pprint import pprint
from langchain_core.prompts import PromptTemplate
from langchain_core.prompts import format_document

#helper func for json loader
def metadata_func(record: dict, metadata: dict) -> dict:
    metadata["category"] = record.get("category")
    metadata["description"] = record.get("description")
    metadata["gender"] = record.get("gender")
    metadata["brand"] = record.get("brand")
    metadata["color"] = "".join( c for c in record.get("color") if c not in "[]'" )
    return metadata

#load and parse json
loader = JSONLoader(
    file_path='/usr/local/dataset/dataset.json',
    jq_schema='.[]',
    content_key='title',
    metadata_func=metadata_func)
data = loader.load()

#configure prompts
llm_prompt_template = PromptTemplate.from_template("""
    You're a helpful assistant who can recommend things in addition to those already chosen.
    Already chosen item:
    {chosen_item}

    Available items:
    {available_items}

    Please check all available items and find the most corresponding item to the chosen one.
    Try to ensure that the recommended item matches the brand, color and purpose well.
    Your answer should contain the chosen item, the recommendation and the example how use them together.
    Generate a draft response using the selected information.
    It should be easy to understand your answer. Start your answer with the phrase: "For <chosen_item> I would recommend <recommended_item>:"
    Keep your answer to a four or five sentences if possible. If not - try to keep the answer short.
    Generate your final response after adjusting it to increase accuracy and relevance.
    Now only show your final response!""")

data_format_prompt_template = PromptTemplate.from_template("| {page_content} | Category: {category} | Color: {color} | Gender: {gender} | Brand: {brand} | Description: {description} |\n")

def format_data(documents):
    result=""
    for doc in documents:
        result += format_document(doc, data_format_prompt_template)
    return result

#declare AI stuff
embeddings = VertexAIEmbeddings("textembedding-gecko@001")
llm = VertexAI(model_name="gemini-pro")

#qdrant part
qdrant = Qdrant.from_documents(
    data,
    embeddings,
    url=os.environ.get("QDRANT_ENDPOINT"),
    prefer_grpc=True,
    api_key=os.environ.get("QDRANT_APIKEY"),
    collection_name="products",
    force_recreate=True
)

#recommendation engine
def recommendation_engine(original_item):
    original_item_formatted=format_data([original_item])
    print("---------\nChosen item:\n"+original_item_formatted)
    found_docs = qdrant.max_marginal_relevance_search(
        original_item.metadata['description'] + ", Color: " + original_item.metadata['color'] + ", Brand: " + original_item.metadata['brand']+ ", Gender: " + original_item.metadata['gender'],
        k=5, 
        fetch_k=15
    )
    found_docs_formatted=format_data(found_docs)
    print("--------\n"+found_docs_formatted+"\n---------")
    llm_prompt = llm_prompt_template.format(chosen_item=original_item_formatted, available_items=found_docs_formatted)
    print("-----------\nllm answer:\n")
    output = llm.invoke(llm_prompt)
    print(output)
    print("-----------")

#give recommendations 5 times for random items
for i in range(5):
    recommendation_engine(data[i*15])
