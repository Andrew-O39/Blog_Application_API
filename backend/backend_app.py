from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # This will enable CORS for all routes

POSTS = [
    {"id": 1, "title": "First post", "content": "This is the first post."},
    {"id": 2, "title": "Second post", "content": "This is the second post."},
]

next_id = 3  # start from 3 since we have two posts

@app.route('/api/posts', methods=['GET'])
def get_posts():
    sort_field = request.args.get('sort')
    direction = request.args.get('direction', 'asc')

    # Validate sort field if provided
    if sort_field and sort_field not in ['title', 'content']:
        return jsonify({"error": "Invalid sort field. Must be 'title' or 'content'."}), 400

    # Validate direction
    if direction not in ['asc', 'desc']:
        return jsonify({"error": "Invalid direction. Must be 'asc' or 'desc'."}), 400

    # Apply sorting if needed
    sorted_posts = POSTS
    if sort_field:
        reverse = direction == 'desc'
        sorted_posts = sorted(POSTS, key=lambda x: x[sort_field].lower(), reverse=reverse)

    return jsonify(sorted_posts), 200


@app.route('/api/posts', methods=['POST'])
def create_post():
    global next_id
    data = request.get_json()

    # Check for missing fields
    missing_fields = []
    if not data or "title" not in data:
        missing_fields.append("title")
    if not data or "content" not in data:
        missing_fields.append("content")

    if missing_fields:
        return jsonify({"error": f"Missing fields: {', '.join(missing_fields)}"}), 400

    new_post = {
        "id": next_id,
        "title": data["title"],
        "content": data["content"]
    }
    POSTS.append(new_post)
    next_id += 1
    return jsonify(new_post), 201


@app.route('/api/posts/<int:post_id>', methods=['DELETE'])
def delete_post(post_id):
    global POSTS
    post_to_delete = next((post for post in POSTS if post["id"] == post_id), None)

    if post_to_delete is None:
        return jsonify({"error": f"Post with id {post_id} not found."}), 404

    POSTS = [post for post in POSTS if post["id"] != post_id]
    return jsonify({"message": f"Post with id {post_id} has been deleted successfully."}), 200


@app.route('/api/posts/<int:post_id>', methods=['PUT'])
def update_post(post_id):
    data = request.get_json()

    if data is None:
        return jsonify({"error": "Invalid JSON body."}), 400  # Check to ensure the request body is a valid JSOn to avoid NoneType errors

    for post in POSTS:
        if post["id"] == post_id:
            post["title"] = data.get("title", post["title"])
            post["content"] = data.get("content", post["content"])
            return jsonify(post), 200

    return jsonify({"error": f"Post with id {post_id} not found."}), 404


@app.route('/api/posts/search', methods=['GET'])
def search_posts():
    title_query = request.args.get('title', '').lower()
    content_query = request.args.get('content', '').lower()

    results = []
    for post in POSTS:
        matches_title = title_query in post['title'].lower() if title_query else True
        matches_content = content_query in post['content'].lower() if content_query else True

        if matches_title and matches_content:
            results.append(post)

    return jsonify(results), 200


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5002, debug=True)
