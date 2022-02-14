import os
from os.path import isfile, join
import json


class Cursor(object):
    def __init__(self, path, app):
        self.app = app
        self.path = path
        self._cursor_dict = self._initialize()
    
    def __str__(self) -> str:
        return str(self._cursor_dict)

    def __getitem__(self, key):
        return self._cursor_dict[key]

    def __len__(self):
        return len(self._cursor_dict.values())
    
    def __setitem__(self, key, data):
        self._cursor_dict[key] = data

    def _dump(self):
        """
        Writes cursor dict object to `cursor.json` file.
        """
        with open(self.path, 'w') as f:
            json.dump(self._cursor_dict, f)

    def _initialize(self):
        """
        Creates or loads the `cursor.json` file.
        """
        # Fetch or create cursor file
        if not os.path.exists(self.path):
            cursor = {'file_index_to_read': 1, 'images': {}}
            img_files = os.listdir(self.app.config['DATA_FOLDER'])
            index = 1
            for img_file in img_files:
                if str(img_file).endswith(('.jpg', '.png', '.jpeg')) and isfile(join(self.app.config['DATA_FOLDER'], img_file)):
                    cursor['images'][str(index)] = img_file
                index += 1
            with open(self.app.config['CURSOR_FILE'], 'w') as f:
                json.dump(cursor, f)
        # Open cursor file
        with open(self.app.config['CURSOR_FILE']) as f:
            cursor = json.load(f)
        return cursor

    def reload_file(self):
        """
        Reload cursor from disk. Main usage is when a parameter is changed
        by hand in `cursor.json` file. It's also called every time `index.html` is rendered.
        """
        # Open cursor file
        with open(self.app.config['CURSOR_FILE']) as f:
            cursor = json.load(f)
        self._cursor_dict = cursor

    def set_index(self, index: int):
        """
        Sets `file_index_to_read` to a specific index.
        If the given index is out of range, it falls back to 1.
        """
        if index > len(self):
            index = 1
        self._cursor_dict['file_index_to_read'] = index
        self._dump()

    def increase_index(self):
        self.set_index(self._cursor_dict['file_index_to_read'] + 1)
        self._dump()
