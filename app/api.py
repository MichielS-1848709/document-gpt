from flask import Flask, jsonify, request
from search_engine import preprocess_and_segment, create_segment_embeddings, save_and_index, search, create_summary

app = Flask(__name__)

"""
Health check endpoint
Just to check if the API is up and running
"""
@app.route('/health', methods=['GET'])
def health():
    return jsonify({"message": "Healthy"}), 200

"""
Upload a new document in the form of text
"""
@app.route('/upload', methods=['POST'])
def upload_document():

    document = request.json["document"]

    if document is None:
        return jsonify({"error": "Please provide a valid document."}), 400

    segments = preprocess_and_segment(document)
    embeddings = create_segment_embeddings(segments)

    save_and_index(segments, embeddings)

    return jsonify({"message": "Document uploaded and indexed successfully."}), 200

"""
Ask a question based on the uploaded documents
"""
@app.route('/ask', methods=['POST'])
def query_document():

    question = request.json["question"]

    if question is None:
        return jsonify({"error": "Please provide a valid question."}), 400

    results = search(question)

    if len(results) == 0:
        return jsonify({"error": "No document found that can answer your question"}), 400

    answer, references, knowledge = create_summary(results[:3], question)

    return jsonify({"question": question, "answer": answer, "references": references, "knowledge": knowledge}), 200

if __name__ == "__main__":
    app.run(port=9090, debug=True, host='0.0.0.0')