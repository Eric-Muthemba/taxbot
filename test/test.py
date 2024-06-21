from flask import Flask, request, jsonify
import os

app = Flask(__name__)

# Configure a secret key to enable the Flask session cookies
app.config['SECRET_KEY'] = 'your_secret_key_here'

# Define the upload directory and allowed file types
UPLOAD_FOLDER = './uploads'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


# Function to check if a file has an allowed extension
def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# Route to handle file upload
@app.route('/upload', methods=['POST'])
def upload_file():
    # Check if the post request has the file part
    if 'file' not in request.files:
        return jsonify({'error': 'No file part in the request'}), 400

    file = request.files['file']

    # If user does not select a file, browser also submits an empty part without filename
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    # If the file exists and is allowed, save it
    if file and allowed_file(file.filename):
        # Create the uploads folder if it doesn't exist
        if not os.path.exists(app.config['UPLOAD_FOLDER']):
            os.makedirs(app.config['UPLOAD_FOLDER'])

        # Save the file to the specified upload directory
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], file.filename))

        return jsonify({'message': 'File uploaded successfully', 'filename': file.filename}), 200

    # If the file type is not allowed, return an error
    else:
        return jsonify({'error': 'File type not allowed'}), 400


if __name__ == '__main__':
    app.run(debug=True)
