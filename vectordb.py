import pprint
import re
import chromadb
from chromadb.config import Settings
from chromadb.utils import embedding_functions


RELOAD_DB = True

chroma_client = chromadb.PersistentClient(path="chroma.db",
                                          settings=Settings(
                                              anonymized_telemetry=False
                                          ))

# Define a new embedding function
embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")
# Use the new embedding function when creating or getting the collection
collection = chroma_client.get_or_create_collection(
    name="chess",
    embedding_function=embedding_function
)



def query_source_data():
    with open("rules.txt") as f:
        content = f.read()
    chess_moves = content.split("\n")
    return [re.sub(' +', ' ', chess_move.replace("\n", "")) for chess_move in chess_moves]


def load_data(results: list):
    collection.upsert(
        documents=results,
        ids=[f"id{num}" for num in range(1, len(results) + 1)]
    )


def run_query(query: str):
    results = collection.query(
        query_texts=[query],
        n_results=3
    )
    return results


def main():
    
    if RELOAD_DB:
        results = query_source_data()
        load_data(results)
    questions = [
        "What happens if a pawn reaches the other side of the board?",
    ]
    for question in questions:
        findings = run_query(question)
        print(question)
        pprint.pprint(findings)
        print("-" * len(question), "\n")


if __name__ == "__main__":
    main()
