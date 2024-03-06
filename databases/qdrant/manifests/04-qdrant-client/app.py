# Copyright 2024 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# [START imports]
from qdrant_client import QdrantClient
from qdrant_client.http import models
import os
import sys
import csv
# [END imports]
def main(query_string):
# [START create_client]
    qdrant = QdrantClient(
        url="http://qdrant-database:6333", api_key=os.getenv("APIKEY"))
# [END reate_client]

# [START create_collection]
    books = [*csv.DictReader(open('/usr/local/dataset/dataset.csv'))]
# [END collection]

# [START prepare_doc]
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
# [END prepare_doc]

# [START add_to_collection]
    # Add my_books to the collection 
    qdrant.add(collection_name="my_books", documents=documents, metadata=metadata, ids=ids, parallel=2)
# [END add_to_collection]

    # Query the collection
# [START query_collection]
    results = qdrant.query(
        collection_name="my_books",
        query_text=query_string,
        limit=2,
    )
    for result in results:
        print("Title:", result.metadata["title"], "\nAuthor:", result.metadata["author"])
        print("Description:", result.metadata["document"], "Published:", result.metadata["publishDate"], "\nScore:", result.score)
        print("-----")
# [END query_collection]
if __name__ == "__main__":
    if len(sys.argv) > 1:
        query_string = " ".join(sys.argv[1:])
        print("Querying qdrant for: ", query_string)
        main(query_string)
    else:
        print("Please provide a query string as an argument.")
