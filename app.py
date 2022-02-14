from flask import Flask, render_template, send_from_directory, request, redirect, url_for
import os
from PIL import Image
from cursor import Cursor
from desktopify import launch_gui

app = Flask(__name__)

# define app common configs
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
app.config['CURSOR_FILE'] = './cursor.json'
app.config['DATA_FOLDER'] = './data'
app.config['RESULTS_FOLDER'] = './results'
app.config['TEXT_MAX_LEN'] = 24
# fetch cursor file
cursor = Cursor(path=app.config['CURSOR_FILE'], app=app)


# app routes
@app.route('/index')
@app.route('/')
def index():
    cursor.reload_file()
    text = os.path.splitext(cursor['images'][str(cursor['file_index_to_read'])])[0]
    return render_template('index.html', text=text)


@app.route('/get_next_image', methods=['GET'])
def get_next_image():
    index = cursor['file_index_to_read']
    if index >= len(cursor):
        index = len(cursor)
    image_file = cursor['images'][str(index)]
    # sends 'image_file' from app.config['DATA_FOLDER'] directory
    return send_from_directory(app.config["DATA_FOLDER"], filename=image_file, cache_timeout=-1)


@app.route('/action', methods=['POST', 'GET'])
def action():
    if request.method == 'POST':
        if request.form['action'] == "Save":
            text = request.form.get('text')
            if len(text) <= app.config['TEXT_MAX_LEN']:
                index = cursor['file_index_to_read']
                img_path = os.path.join(app.config['DATA_FOLDER'], cursor['images'][str(index)])
                # get file extension e.g. jpg, png
                img_extension = os.path.splitext(img_path)[1]
                # save file to disk
                pil_img = Image.open(img_path)
                # add index & underlines to text for regex
                pil_img.save(f"{app.config['RESULTS_FOLDER']}/{index}_{text}{img_extension}")
                print(f"worte image to {app.config['RESULTS_FOLDER']}/{index}_{text}{img_extension}")
                # update index to read in cursor
                cursor.increase_index()
        # go to next image if skip is entered
        if request.form['action'] == "Skip":
            cursor.increase_index()
        # jump to a specific index, choose from indexes under 'images' key in cursor.json
        if request.form['action'] == "Jump":
            try:
                jump_index = int(request.form['jump_index'])
                cursor.set_index(jump_index)
            except ValueError:
                return redirect(url_for('index'))
    return redirect(url_for('index'))


if __name__ == '__main__':
    launch_gui(app, port=5000)
