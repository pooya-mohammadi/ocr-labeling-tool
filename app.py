import shutil
from flask import Flask, render_template, request, redirect, url_for
import os
from cursor import Cursor
from settings import DATA_PATH, TEXT_MAX_LEN, RESULTS_PATH, PORT, USE_CASE
from deep_utils import remove_create, log_print, get_logger, split_extension

os.makedirs(RESULTS_PATH, exist_ok=True)

app = Flask(__name__)
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = -1
app.jinja_env.auto_reload = True
app.config['TEMPLATES_AUTO_RELOAD'] = True


@app.after_request
def add_header(r):
    r.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    r.headers["Pragma"] = "no-cache"
    r.headers["Expires"] = "0"
    r.headers['Cache-Control'] = 'public, max-age=0'
    return r


# fetch cursor file
cursor = Cursor(data_dir=DATA_PATH)
logger = get_logger("app", split_extension(cursor.cursor_path, extension=".log"))


# app routes
@app.route('/index')
@app.route('/')
def index():
    cursor.reload_file()
    text = os.path.splitext(cursor['images'][str(cursor['file_index_to_read'])])[0]
    min_length = cursor['min_length']
    max_length = cursor['max_length']
    if USE_CASE.lower() == "plate":
        text = text.split("_")[-1]
        text_01 = text[:2]
        text_02 = text[2]
        text_03 = text[3:]
    elif USE_CASE.lower() == "ocr":
        text_01 = text.split("_")[-1]
        text_02 = ""
        text_03 = ""
    else:
        raise ValueError("USE_CASE type is not valid")
    remove_create("static/ocr_images")
    image_name = cursor['images'][str(cursor['file_index_to_read'])]
    photo = os.path.join(DATA_PATH, image_name)
    dst = os.path.join("static/ocr_images", image_name)
    shutil.copy(photo, dst)
    return render_template('index.html', text_01=text_01, text_02=text_02, text_03=text_03, text=text, photo=image_name,
    min_length=min_length, max_length=max_length)


@app.route('/action', methods=['POST', 'GET'])
def action():
    if request.method == 'POST':
        if request.form['action'] == "Save":
            if USE_CASE == "plate":
                text = request.form.get('text_01') + request.form.get("text_02") + request.form.get("text_03")
            elif USE_CASE == "OCR":
                text = request.form.get('text_01')
            else:
                raise ValueError()
            if len(text) <= TEXT_MAX_LEN:
                index = cursor['file_index_to_read']
                img_path = os.path.join(DATA_PATH, cursor['images'][str(index)])
                # get file extension e.g. jpg, png
                img_extension = os.path.splitext(img_path)[1]
                # copy file with a new name!
                shutil.copy(img_path, f"{RESULTS_PATH}/{index}_{text}{img_extension}")
                log_print(logger, f"Wrote image to {RESULTS_PATH}/{index}_{text}{img_extension}")
                # update index to read in cursor
                cursor.increase_index()
        # go to next image if skip is entered
        elif request.form['action'] == "Skip":
            cursor.increase_index()
        # jump to a specific index, choose from indexes under 'images' key in cursor.json
        elif request.form['action'] == "Jump":
            try:
                jump_index = int(request.form['jump_index'])
                if jump_index == 0:
                    raise ValueError("Index starts from 1.")
                cursor.set_index(jump_index)
            except ValueError:
                return redirect(url_for('index'))
        elif request.form['action'] == "Set":
            cursor.save_lengths(request.form['text_min_len'], request.form['text_max_len'])
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(port=PORT)
