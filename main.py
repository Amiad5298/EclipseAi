import os
import uuid
from dotenv import load_dotenv
from flask import Flask, request, send_file, render_template, redirect, url_for, flash, jsonify, session
import zipfile
import tempfile
import threading
from image_generator_business import BackgroundImageCreator

load_dotenv()

app = Flask(__name__)
app.secret_key = 'supersecretkey'  # Replace with a secure key in production

progress = {}  # Store progress for different tasks
output_dirs = {}  # Store output directories for each task
progress_lock = threading.Lock()  # Create a lock for thread safety

# Flask routes
@app.route('/')
def home():
    api_key = session.get('api_key', '')  # Get the API key from session, default to an empty string if not set
    return render_template('index.html', api_key=api_key)

@app.route('/set_api_key', methods=['POST'])
def set_api_key():
    api_key = request.form['api_key']
    if not api_key:
        flash('API Key is required.', 'danger')
        return redirect(url_for('home'))
    session['api_key'] = api_key
    flash('API Key set successfully. You can now upload an Excel file.', 'success')
    return redirect(url_for('home'))

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'api_key' not in session:
        flash('Please set your OpenAI API key before uploading a file.', 'danger')
        return redirect(url_for('home'))

    api_key = session['api_key']  # Extract API key from session

    if 'file' not in request.files:
        flash('No file part', 'danger')
        return redirect(request.url)
    file = request.files['file']
    if file.filename == '':
        flash('No selected file', 'danger')
        return redirect(request.url)
    if file:
        task_id = str(uuid.uuid4())  # Unique task ID for progress tracking
        with progress_lock:
            progress[task_id] = {"percentage": 0, "generated": 0, "total": 0, "status": "in-progress"}  # Initialize progress
        print(f"Task ID {task_id} initialized with progress 0%")

        with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
            file.save(tmp_file.name)
            output_dir = tempfile.mkdtemp()
            output_dirs[task_id] = output_dir  # Save output directory for later use

            def process_task():
                try:
                    # Pass the API key directly instead of accessing the session in the thread
                    background_image_creator = BackgroundImageCreator(api_key=api_key, excel_file_path=tmp_file.name, output_dir=output_dir, task_id=task_id, progress=progress, progress_lock=progress_lock)
                    saved_images = background_image_creator.process()

                    zip_path = os.path.join(output_dir, 'background_images.zip')
                    with zipfile.ZipFile(zip_path, 'w') as zipf:
                        for image_path in saved_images:
                            zipf.write(image_path, os.path.basename(image_path))

                    with progress_lock:
                        progress[task_id] = {
                            "percentage": 100,
                            "generated": len(saved_images),
                            "total": len(saved_images),
                            "status": "done"
                        }
                    print(f"Task ID {task_id} completed with progress: {progress[task_id]}")
                except ValueError as e:
                    with progress_lock:
                        progress[task_id] = {
                            "percentage": 0,
                            "generated": 0,
                            "total": 0,
                            "status": "error",
                            "error_message": str(e)
                        }
                    print(f"Task ID {task_id} failed with error: {str(e)}")

            # Run the processing in a separate thread
            threading.Thread(target=process_task).start()
            return jsonify({"task_id": task_id})


@app.route('/progress/<task_id>', methods=['GET'])
def get_progress(task_id):
    with progress_lock:
        if task_id in progress:
            progress_data = progress[task_id]

            # Check if progress_data is unexpectedly a string and handle it
            if not isinstance(progress_data, dict):
                print(f"Unexpected non-dict value in progress for task {task_id}, removing from progress.")
                del progress[task_id]
                return jsonify({"progress": "not found"}), 404

            # Log for debugging
            print(f"Sending progress data for task {task_id}: {progress_data}")

            return jsonify(progress_data)
        else:
            return jsonify({"progress": "not found"}), 404

@app.route('/cancel/<task_id>', methods=['POST'])
def cancel_task(task_id):
    with progress_lock:
        if task_id in progress and progress[task_id]["status"] == "in-progress":
            progress[task_id]["status"] = "canceled"
            print(f"Task ID {task_id} has been canceled.")
            return jsonify({"message": "Task has been canceled."})
        else:
            return jsonify({"message": "Task not found or already completed."}), 404

@app.route('/download/<task_id>', methods=['GET'])
def download_file(task_id):
    with progress_lock:
        if task_id in output_dirs:
            output_dir = output_dirs[task_id]
            zip_path = os.path.join(output_dir, 'background_images.zip')
            if os.path.exists(zip_path):
                return send_file(zip_path, as_attachment=True)
            else:
                return "File not found", 404
        else:
            return "Invalid task ID", 404

if __name__ == "__main__":
    app.run(debug=True)
