import shutil

from flask import Flask, render_template, send_from_directory, request, redirect, url_for
import os
from PIL import Image
from cursor import Cursor
from desktopify import launch_gui
from settings import CURSOR_FILE, DATA_FOLDER, TEXT_MAX_LEN, RESULTS_FOLDER, PORT

os.makedirs(RESULTS_FOLDER, exist_ok=True)

app = Flask(__name__)
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = -1
app.jinja_env.auto_reload = True
app.config['TEMPLATES_AUTO_RELOAD'] = True

# fetch cursor file
cursor = Cursor(path=CURSOR_FILE, data_dir=DATA_FOLDER, cursor_path=CURSOR_FILE)


# app routes
@app.route('/index')
@app.route('/')
def index():
    cursor.reload_file()
    text = os.path.splitext(cursor['images'][str(cursor['file_index_to_read'])])[0]
    text = text.split("_")[0]
    text_01 = text[:2]
    text_02 = text[2]
    text_03 = text[3:]
    # photo = os.path.join(DATA_FOLDER, cursor['images'][str(cursor['file_index_to_read'])])
    return render_template('index.html', text_01=text_01, text_02=text_02, text_03=text_03, text=text)


@app.route('/get_next_image', methods=['GET'])
def get_next_image():
    index = cursor['file_index_to_read']
    image_file = cursor['images'][str(index)]
    return send_from_directory(DATA_FOLDER, path=image_file, max_age=-1)


@app.route('/action', methods=['POST', 'GET'])
def action():
    if request.method == 'POST':
        if request.form['action'] == "Save":
            text = request.form.get('text_01') + request.form.get("text_02") + request.form.get("text_03")
            if len(text) <= TEXT_MAX_LEN:
                index = cursor['file_index_to_read']
                img_path = os.path.join(DATA_FOLDER, cursor['images'][str(index)])
                # get file extension e.g. jpg, png
                img_extension = os.path.splitext(img_path)[1]
                # copy file with a new name!
                shutil.copy(img_path, f"{RESULTS_FOLDER}/{index}_{text}{img_extension}")
                print(f"[INFO] Wrote image to {RESULTS_FOLDER}/{index}_{text}{img_extension}")
                # update index to read in cursor
                cursor.increase_index()
        # go to next image if skip is entered
        elif request.form['action'] == "Skip":
            cursor.increase_index()
        # jump to a specific index, choose from indexes under 'images' key in cursor.json
        elif request.form['action'] == "Jump":
            try:
                jump_index = int(request.form['jump_index'])
                cursor.set_index(jump_index)
            except ValueError:
                return redirect(url_for('index'))
    return redirect(url_for('index'))


if __name__ == '__main__':
    launch_gui(app, port=PORT)
