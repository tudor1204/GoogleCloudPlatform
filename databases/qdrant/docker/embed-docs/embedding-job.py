from langchain.embeddings import VertexAIEmbeddings
from langchain.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import Qdrant
from google.cloud import storage
import os

bucketname = os.getenv("BUCKET_NAME")
filename = os.getenv("FILE_NAME")

storage_client = storage.Client()
bucket = storage_client.bucket(bucketname)
blob = bucket.blob(filename)
blob.download_to_filename("/documents/" + filename)

loader = PyPDFLoader("/documents/" + filename)
text_splitter = RecursiveCharacterTextSplitter(chunk_size=1500, chunk_overlap=0)
documents = loader.load_and_split(text_splitter)

embeddings = VertexAIEmbeddings()
qdrant = Qdrant.from_documents(
    documents, embeddings,
    collection_name="training-docs",
    url=os.getenv("QDRANT_URL"), 
    api_key=os.getenv("APIKEY"),
    shard_number=6,
    replication_factor=2
)

print(filename + " was successfully embedded") 
print(f"# of vectors = {len(documents)}")
 
