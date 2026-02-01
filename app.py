import os
from flask.app import Flask
from flask.helpers import send_from_directory
from flask import request
import requests

app = Flask(__name__)

@app.route('/')
def serve_index():
    return send_from_directory('.', 'index.html')

@app.route('/camera-proxy')
def camera_proxy():
    """Proxy endpoint to fetch camera streams and bypass CORS"""
    camera_url = request.args.get('url')
    if not camera_url:
        return "No camera URL provided", 400
    
    try:
        # Fetch the camera stream
        response = requests.get(camera_url, stream=True, timeout=10)
        response.raise_for_status()
        
        # Return the stream with appropriate headers
        def generate():
            for chunk in response.iter_content(chunk_size=1024):
                if chunk:
                    yield chunk
        
        return app.response_class(
            generate(),
            mimetype=response.headers.get('content-type', 'application/octet-stream'),
            headers={
                'Content-Type': response.headers.get('content-type', 'application/octet-stream'),
                'Cache-Control': 'no-cache, no-store, must-revalidate',
                'Pragma': 'no-cache',
                'Expires': '0'
            }
        )
    except Exception as e:
        return f"Error fetching camera stream: {str(e)}", 500

@app.route('/<path:path>')
def serve_files(path):
    return send_from_directory('.', path)

if __name__ == '__main__':
    try:
        from waitress import serve
        print("Starting AxisScope server on port 3000...")
        serve(app, host='0.0.0.0', port=3000)
    except Exception as e:
        print(f"Error starting server: {e}")
        exit(1)
