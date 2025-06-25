from flask import Flask, request, render_template_string, send_file
import requests
import os
from urllib.parse import urlparse

app = Flask(__name__)
UPLOAD_FOLDER = './uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

HTML_PAGE = """
<!doctype html>
<title>Avatar Upload</title>
<h1>Upload your avatar</h1>
<form method=post enctype=multipart/form-data>
  <label>Upload from your computer:</label><br>
  <input type=file name=file><br><br>
  <label>Or provide an external URL:</label><br>
  <input type=text name=url size=80><br><br>
  <input type=submit value=Upload>
</form>
{% if result %}
<h2>Result:</h2>
<pre>{{ result }}</pre>
{% endif %}
"""

def mock_check_port(port):
    if port in [80, 443, 22]:
        return f"Connection to port {port} successful"
    else:
        return f"Connection to port {port} failed"

def mock_aws_metadata():
    return """{
  "AccessKeyId": "ASIA...MOCKED",
  "SecretAccessKey": "mockedsecret123",
  "Token": "MockedSessionToken",
  "Expiration": "2025-12-31T23:59:59Z"
}"""

@app.route('/', methods=['GET', 'POST'])
def upload_avatar():
    result = None
    if request.method == 'POST':
        file = request.files.get('file')
        url = request.form.get('url')

        if file:
            filepath = os.path.join(UPLOAD_FOLDER, file.filename)
            file.save(filepath)
            result = f"File uploaded to {filepath}"

        elif url:
            try:
                parsed = urlparse(url)
                host = parsed.hostname
                port = parsed.port or 80

                if host == '169.254.169.254':
                    result = f"Fetched AWS Metadata:\n{mock_aws_metadata()}"
                elif host == '127.0.0.1' or host == 'localhost':
                    result = mock_check_port(port)
                else:
                    r = requests.get(url, timeout=3)
                    result = f"Fetched remote content:\n{r.text[:300]}..."
            except Exception as e:
                result = f"Error: {str(e)}"

    return render_template_string(HTML_PAGE, result=result)

if __name__ == '__main__':
    app.run(debug=True, port=5005)
