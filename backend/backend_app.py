from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # This will enable CORS for all routes

# In-memory list of blog posts (used instead of a database)
POSTS = [
    {"id": 1, "title": "First post", "content": "This is the first post."},
    {"id": 2, "title": "Second post", "content": "This is the second post."},
]

next_id = 3  # Used to assign new post IDs. It starts from 3 since we have two posts already

@app.route('/api/posts', methods=['GET'])
def get_posts():
    """
    Retrieve all blog posts.
    Optional query parameters:
    - sort: 'title' or 'content'
    - direction: 'asc' or 'desc'
    Returns a list of posts, optionally sorted.
    400 Bad Request if sort/direction are invalid.
    """
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
        reverse = direction == 'desc'  # Determine sort direction
        sorted_posts = sorted(POSTS, key=lambda x: x[sort_field].lower(), reverse=reverse)

    return jsonify(sorted_posts), 200


@app.route('/api/posts', methods=['POST'])
def create_post():
    """
    Create a new blog post.
    Returns:
    201 Created: New post.
    400 Bad Request: If title or content is missing.
    """
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
    """
    Delete a blog post by ID.
    Returns:
    200 OK: If deletion is successful.
    404 Not Found: If post with given ID does not exist.
    """
    global POSTS
    post_to_delete = next((post for post in POSTS if post["id"] == post_id), None)

    if post_to_delete is None:
        return jsonify({"error": f"Post with id {post_id} not found."}), 404

    POSTS = [post for post in POSTS if post["id"] != post_id]
    return jsonify({"message": f"Post with id {post_id} has been deleted successfully."}), 200


@app.route('/api/posts/<int:post_id>', methods=['PUT'])
def update_post(post_id):
    """
    Update an existing post by ID.
    Returns:
    200 OK: Updated post.
    400 Bad Request: If body is invalid.
    404 Not Found: If post with given ID does not exist.
    """
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
    """
    Search posts by title and/or content.
    Query Parameters:
    - title (optional): Filter by title substring (case-insensitive)
    - content (optional): Filter by content substring (case-insensitive)
    Returns:
    200 OK: List of matched posts (can be empty).
    """
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
