from qdrant_client import QdrantClient
from qdrant_client.http import models
import os
import sys
import csv


def main(query_string):
    # Connect to Qdrant
    qdrant = QdrantClient(
        url="http://qdrant-database:6333", api_key=os.getenv("APIKEY"))

    # Create a collection
    books = [*csv.DictReader(open('/usr/local/dataset/dataset.csv'))]

    documents: list[dict[str, any]] = []
    metadata: list[dict[str, any]] = []
    ids: list[int] = []

    for idx, doc in enumerate(books):
        ids.append(idx)
        documents.append(doc["description"])
        metadata.append(
            {
                "title": doc["title"],
                "author": doc["author"],
                "publishDate": doc["publishDate"],
            }
        )

    # Add my_books to the collection 
    qdrant.add(collection_name="my_books", documents=documents, metadata=metadata, ids=ids, parallel=2)

    # Query the collection
    results = qdrant.query(
        collection_name="my_books",
        query_text=query_string,
        limit=2,
    )
    for result in results:
        print("Title:", result.metadata["title"], "\nAuthor:", result.metadata["author"])
        print("Description:", result.metadata["document"], "Published:", result.metadata["publishDate"], "\nScore:", result.score)
        print("-----")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        query_string = " ".join(sys.argv[1:])
        print("Querying qdrant for: ", query_string)
        main(query_string)
    else:
        print("Please provide a query string as an argument.")