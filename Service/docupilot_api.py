from flask import Flask, jsonify, request

# import the lib from parent directory
import sys
sys.path.append('../')
from Core.openai_helper import infer_docs_from_llm
# Create Flask application instance
app = Flask(__name__)


@app.route('/docufy', methods=['POST'])
def get_info():
    filename = request.form.get('filename')
    diff_file = request.files.get('diff')
    content_file = request.files.get('content')

    if not all([filename, diff_file, content_file]):
        return jsonify({"error": "Missing form data"}), 400

    diff = diff_file.read().decode('utf-8')
    content = content_file.read().decode('utf-8')

    patch = infer_docs_from_llm(filename, content, diff)
    print(f"Generated patch for {filename}:\n{patch}")
    return patch



@app.errorhandler(404)
def not_found(error):
    """
    Handle 404 errors with a custom JSON response.
    
    Args:
        error: The error object
        
    Returns:
        tuple: JSON response and status code
    """
    return jsonify({
        "error": "Not Found",
        "message": "The requested endpoint does not exist",
        "status_code": 404
    }), 404

@app.errorhandler(500)
def internal_error(error):
    """
    Handle 500 errors with a custom JSON response.
    
    Args:
        error: The error object
        
    Returns:
        tuple: JSON response and status code
    """
    return jsonify({
        "error": "Internal Server Error",
        "message": "Something went wrong on the server",
        "status_code": 500
    }), 500

if __name__ == '__main__':
    print("Starting DocuBuddy Simple Flask Server...")
    print("Available endpoints:")
    print("  - GET  /")
    print("  - GET  /api/health")
    print("  - GET  /api/info")
    print("  - GET  /api/echo")
    print("  - POST /api/echo")
    print("\nServer running at: http://localhost:5000")
    
    # Run the Flask application
    app.run(
        host='0.0.0.0',  # Allow external connections
        port=5000,       # Default Flask port
        debug=True       # Enable debug mode for development
    )
