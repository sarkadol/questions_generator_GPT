import requests
import json
import random
from pathlib import Path
from src.methods import *


# Function to query the embedder API
def query_embedder(question: str, top_k: int, embedder_url: str):
    data = {"query": question, "top_k": top_k}
    HEADERS = {"Content-Type": "application/json"}
    response = requests.post(embedder_url, headers=HEADERS, json=data, verify=False)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error: {response.status_code}, Response: {response.text}")
        return None


# Function to evaluate the embedder
def evaluate_embedder(json_file, q, k, d, lang, embedder, output_file):
    embedder_url = load_url(embedder)

    with open(json_file, 'r', encoding='utf-8') as f:
        questions_mapping = json.load(f)

    results = {"embedder_url": embedder_url, "evaluations": []}
    selected_docs = random.sample(list(questions_mapping.keys()), min(d, len(questions_mapping)))

    for doc_title in selected_docs:
        questions = random.sample(questions_mapping[doc_title], min(q, len(questions_mapping[doc_title])))

        for question in questions:
            response_data = query_embedder(question, k, embedder_url)
            if not response_data or "similarities" not in response_data:
                print(f"No valid response for question: {question}")
                continue

            retrieved_docs = []
            for similarity in response_data.get("similarities", []):
                metadata = similarity.get("metadata", {})
                extracted_title = metadata.get("title")

                if extracted_title:
                    retrieved_docs.append({
                        "score": similarity.get("score", "N/A"),
                        "ID": similarity.get("id", "N/A"),
                        "metadata": {key: value for key, value in metadata.items() if key != "data"}
                    })
                else:
                    print(f"Warning: No title extracted from metadata: {metadata}")

            results["evaluations"].append({
                "question": question,
                "correct_document": doc_title,
                "retrieved_documents": retrieved_docs
            })

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=4)

    print(f"Results saved to {output_file}")


if __name__ == "__main__":
    # ----------------------------------------------
    q = 5  # Number of questions per document
    k = 5  # Number of top retrieved documents
    d = 1  # Number of documents to test
    lang = "english"  # Language of the questions ("czech" or "english")
    embedder = 1  # Change this to 2 for embedder_2
    # ----------------------------------------------

    output_file = f"embedder_{embedder}/results_{embedder}.json"  # Output file for results

    json_file = "questions_mapping_czech.json" if lang == "czech" else "questions_mapping_english.json"
    evaluate_embedder(json_file, q, k, d, lang, embedder, output_file)
