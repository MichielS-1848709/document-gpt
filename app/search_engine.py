import re

import openai
from annoy import AnnoyIndex
from database import DocumentDatabase
import os

openai.api_key = os.getenv("OPENAI_API_KEY")

# 1. Initial in-memory database
database = DocumentDatabase()

# 2. Generate an embedding for a prompt
def create_embeddings(prompt):
    text = prompt.replace("\n", " ")
    return openai.Embedding.create(input=[text], engine="text-embedding-ada-002")["data"][0]["embedding"]


# 3. Preprocess and segment the text
def preprocess_and_segment(text, max_segment_length=100):
    segments = []
    paragraphs = text.split("\n\n")
    for paragraph in paragraphs:
        sentences = re.split(r"(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?)\s", paragraph)
        segment = ""
        for sentence in sentences:
            if len(segment) + len(sentence) > max_segment_length:
                segments.append(segment.strip())
                segment = ""
            segment += f" {sentence}"
        segments.append(segment.strip())
    return segments


# 4. Create embeddings for text segments
def create_segment_embeddings(segments):
    embeddings = []
    for segment in segments:
        embedding = create_embeddings(segment)
        embeddings.append(embedding)
    return embeddings


# 5. Create a vector database using Annoy
def save_and_index(segments, embeddings, dimensions=1536, trees=10):

    merged_segments = []


    for i, segment in enumerate(segments):
        merged_segments.append({
            "embedding": embeddings[i],
            "text": segment
        })

    database.add_document(merged_segments)


# 6. Search the most relevant segment based on the query
def search(query, num_results=5):
    query_embedding = create_embeddings(query)
    return database.find_relevant_documents(query_embedding, num_results)


# 7. Combine all segments into a single text blob and return for each segment the document id
def get_text_and_reference(segments_with_id):
    text = []
    segment_ids = []

    for segment in segments_with_id:
        text.append(segment['text'])
        segment_ids.append(segment['id'])

    relevant_text = " ".join(text)
    references = database.get_document_ids(segment_ids)

    return relevant_text, references


# 8. Answer the question based on the most relevant segment
def create_summary(segments_with_id, question):

    text, references = get_text_and_reference(segments_with_id)

    prompt = f"Prompt: Given the following uploaded documents (which is the ground truth, disregard any other knowledge), please provide a summary that specifically addresses the question provided: \n Upload documents: {text} \n\n Question: {question} \n Please provide a concise summary that directly answers the question, using information solely from the provided uploaded documents, without any additional information or elaboration."
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "system", "content": prompt}],
        temperature=0.5,
        max_tokens=150
    )
    summary = response.choices[0].message

    return summary, references, text