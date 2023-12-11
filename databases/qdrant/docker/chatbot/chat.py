from langchain.chat_models import ChatVertexAI
from langchain.prompts import ChatPromptTemplate
from langchain.embeddings import VertexAIEmbeddings
from langchain.vectorstores import Qdrant
from qdrant_client import QdrantClient
import streamlit as st
import os

vertexAI = ChatVertexAI(streaming=True)
promt_template = ChatPromptTemplate.from_messages(
    [
        ("system", "You are a helpful AI bot. Your name is {name}."),
        ("human", """
        Use the provided context to answer the provided user query. Only use the provided context to answer the query. If you do not know the answer, response with "I don't know"

        CONTEXT:
        {context}

        QUERY:
        {query}
        """),
    ]
)

embedding_model = VertexAIEmbeddings()

client = QdrantClient(
    url=os.getenv("QDRANT_URL"),
    api_key=os.getenv("APIKEY"),
)
collection_name = os.getenv("COLLECTION_NAME")
qdrant = Qdrant(client, collection_name, embeddings=embedding_model)

def format_docs(docs):
    return "\n\n".join([d.page_content for d in docs])

st.title("🤖 Chatbot")
if "messages" not in st.session_state:
    st.session_state["messages"] = [{"role": "ai", "content": "How can I help you?"}]

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

if chat_input := st.chat_input():
    with st.chat_message("human"):
        st.write(chat_input)
        st.session_state.messages.append({"role": "human", "content": chat_input})

    found_docs = qdrant.similarity_search(chat_input)
    context = format_docs(found_docs)

    promt_value = promt_template.format_messages(name="Bob", query=chat_input, context=context)
    with st.chat_message("ai"):
        with st.spinner("Typing..."):
            content = ""
            with st.empty():
                for chunk in vertexAI.stream(promt_value):
                    content += chunk.content
                    st.write(content)
            st.session_state.messages.append({"role": "ai", "content": content})

