from flask import Flask, request, jsonify
from sentence_transformers import SentenceTransformer, util


# Initialize Flask app
app = Flask(__name__)

# Load the SentenceTransformer model
# model = SentenceTransformer("./models/instructor-base")
model = SentenceTransformer("hkunlp/instructor-base")
print("Model loaded successfully!")


@app.route('/')
def home():
    return jsonify(
        {"message": "Welcome to the Sentence Transformer API!"}
    ), 200


@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "healthy"}), 200


@app.errorhandler(405)
def method_not_allowed(e):
    return jsonify(
        {"message": "This endpoint only supports POST requests"}
    ), 405


@app.route('/predict', methods=['POST'])
def predict():
    # Parse request data
    data = request.get_json()
    queries = data.get('queries', [])
    product_descriptions = data.get('product_descriptions', [])

    # Validate inputs
    if not queries or not product_descriptions:
        return jsonify(
            {"error": "'query' and 'product_descriptions' must be provided."}
        ), 400

    # Validate types
    if not isinstance(queries, list) or not isinstance(product_descriptions, list):
        return jsonify(
            {"error": "'query' and 'product_descriptions' \
             must be lists."}
        ), 400

    # Encode queries and product descriptions
    query_embeddings = model.encode(
        queries,
        convert_to_tensor=True
    )
    product_embeddings = model.encode(
        product_descriptions,
        convert_to_tensor=True
    )

    # Compute cosine similarities
    hits = util.semantic_search(
        query_embeddings,
        product_embeddings
    )

    # Format results
    results = []
    for idx, hit_group in enumerate(hits):
        result = [
            {
                "query": queries[idx],
                "product_description": product_descriptions[
                    hit['corpus_id']
                ],
                "score": round(hit['score'], 4),
            }
            for hit in hit_group
        ]
        results.append(result)

    return jsonify(results), 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
