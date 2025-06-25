from flask import Flask, request, render_template_string, send_from_directory, redirect, url_for
import os
import requests
from werkzeug.utils import secure_filename
from io import BytesIO
from PIL import Image

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = './uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

@app.route('/', methods=['GET', 'POST'])
def upload_avatar():
    message = ''
    image_url = ''
    uploaded_image = ''
    if request.method == 'POST':
        url = request.form.get('avatar_url', '').strip()
        file = request.files.get('avatar_file')

        if url:
            if '169.254.169.254' in url:
                message = "Mocked AWS Metadata:\nAccessKeyId: ASIA...MOCKED\nSecretAccessKey: mocksecret\nToken: MockedToken\nExpiration: 2025-12-31T23:59:59Z"
            elif '127.0.0.1' in url:
                try:
                    port = int(url.split(":")[-1])
                    if port in [80, 443, 22]:
                        message = f"Mocked: Connection to port {port} successful."
                    else:
                        message = f"Mocked: Connection to port {port} failed."
                except Exception:
                    message = "Invalid localhost format."
            else:
                try:
                    r = requests.get(url, timeout=3)
                    content_type = r.headers.get('Content-Type', '')
                    if 'image' in content_type:
                        image_url = url
                        message = "Image loaded successfully from URL."
                    else:
                        message = f"Fetched data:\n{r.text[:300]}"
                except Exception as e:
                    message = f"Failed to fetch URL: {e}"

        elif file and file.filename:
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            uploaded_image = filename
            message = "Image uploaded successfully from local computer."

    return render_template_string('''
    <html>
    <head>
        <title>Avatar Upload</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; }
            input[type="text"] { width: 80%; padding: 10px; margin: 10px 0; }
            input[type="file"] { margin: 10px 0; }
            textarea { width: 80%; height: 150px; }
        </style>
    </head>
    <body>
        <h2>Upload Your Avatar</h2>
        <form method="POST" enctype="multipart/form-data">
            <label>From URL:</label><br>
            <input type="text" name="avatar_url" placeholder="https://example.com/avatar.png"><br>
            <label>Or choose from computer:</label><br>
            <input type="file" name="avatar_file"><br><br>
            <input type="submit" value="Upload Avatar">
        </form>
        <br>
        {% if image_url %}
            <h3>Avatar from URL:</h3>
            <img src="{{ image_url }}" width="200"><br>
        {% endif %}
        {% if uploaded_image %}
            <h3>Avatar from local upload:</h3>
            <img src="{{ url_for('uploaded_file', filename=uploaded_image) }}" width="200"><br>
        {% endif %}
        <br>
        <h3>Server Response:</h3>
        <textarea readonly>{{ message }}</textarea>
    </body>
    </html>
    ''', image_url=image_url, uploaded_image=uploaded_image, message=message)

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

app.run(port=5005)
