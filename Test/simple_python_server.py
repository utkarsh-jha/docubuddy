from flask import Flask, jsonify
# Create Flask application instance
app = Flask(__name__)


@app.route('/docufy')
def get_info():
    """
    Information endpoint that returns server details.
    
    Returns:
        dict: Server information
    """
    
    patch: str = '''
        diff --git a/src/perform_analysis.py b/src/perform_analysis.py
        index e69de29..7f5c4c3 100644
        --- a/src/perform_analysis.py
        +++ b/src/perform_analysis.py
        @@ -2,0 +3,4 @@
        +
        +def add(x: float, y: float) -> float:
        +    """Return the sum of two numbers."""
        +    return x + y
        ```
    '''
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
