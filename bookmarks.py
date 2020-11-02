# This Python file uses the following encoding: utf-8
import os


class bookmarks:
    def __init__(self, path_to_bookmark_file: str):
        self.list = []
        if os.path.exists(path_to_bookmark_file):
            self.list = self.get_bookmarks_from_file(path_to_bookmark_file)
        else:
            open(path_to_bookmark_file, 'a').close()
        self.path_to_bookmark_file = path_to_bookmark_file

    def get_bookmarks_from_file(self, path):
        list = []
        with open(path) as bookmarks:
            for bookmark in bookmarks:
                list.append({'name': bookmark.split('|')[0],
                             'path': bookmark.split('|')[1].rstrip()})
        return list

    def add_bookmark(self, name: str, path: str):
        # TODO: error handling
        if not self.bookmark_exists(name) and '|' not in name:
            self.list.append({'name': name, 'path': path})
            with open(self.path_to_bookmark_file, 'a') as bookmarks:
                bookmarks.write(name + '|' + path + '\n')

    def remove_bookmark(self, name: str):
        new_list = []
        for bookmark in self.list:
            if bookmark['name'] != name:
                new_list.append(bookmark)
        self.list = new_list
        with open(self.path_to_bookmark_file, 'w') as bookmarks:
            for bookmark in self.list:
                bookmarks.write(bookmark['name']
                                + '|'
                                + bookmark['path']
                                + '\n')

    def get_path_from_name(self, name: str):
        for bookmark in self.list:
            if name == bookmark['name']:
                return bookmark['path']
        return False

    def bookmark_exists(self, name: str):
        for bookmark in self.list:
            if name == bookmark['name']:
                return True
        return False

    def get_all(self):
        return self.list
