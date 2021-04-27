import os

from typing import List, Dict


class bookmarks:
    """
    Handles the bookmarks as file and as list of dicts.
    """

    def __init__(self, path_to_bookmark_file: str):
        """
        Reads bookmarks from file to internal list of dicts or creates the
        file if it doesn't exist yet. The file should have the format of one
        bookmark per line and the individual lines should have the format:

        bookmark name|/path/to/bookmark

        :param path_to_bookmark_file: Path to the file, in which the bookmarks
                                      are saved
        :type path_to_bookmark_file: str
        """
        self.list = []
        if os.path.exists(path_to_bookmark_file):
            self.list = self.get_bookmarks_from_file(path_to_bookmark_file)
        else:
            open(path_to_bookmark_file, 'a').close()
        self.path_to_bookmark_file = path_to_bookmark_file

    def get_bookmarks_from_file(self, path: str) -> List[Dict[str, str]]:
        """
        Gets bookmarks from a file.

        :param path: Path to the file, in which the bookmarks are saved.
        :type path: str
        :return: List of dicts containing name and path of the bookmarks.
                 The dicts follow this structure: {'name': '', 'path': ''}
        :rtype: List[Dict[str, str]]
        """
        list = []
        with open(path) as bookmarks:
            for bookmark in bookmarks:
                list.append({'name': bookmark.split('|')[0],
                             'path': bookmark.split('|')[1].rstrip()})
        return list

    def add_bookmark(self, name: str, path: str):
        """
        Adds a new bookmark. Does nothing, if another bookmark with the same
        name already exists or the | character is in the chosen name. The
        bookmark will be saved to the bookmark file that was chosen on
        instantiation of this class.

        :param name: The name of the new bookmark. This will be shown in the
                     UI.
        :type name: str
        :param path: Path which the bookmark should lead to.
        :type path: str
        """
        # TODO: error handling
        if not self.bookmark_exists(name) and '|' not in name:
            self.list.append({'name': name, 'path': path})
            with open(self.path_to_bookmark_file, 'a') as bookmarks:
                bookmarks.write(name + '|' + path + '\n')

    def remove_bookmark(self, name: str):
        """
        Removes a bookmark from the internal bookmark list. It also rewrites
        the updated list to the bookmark file chosen on class instatiation.
        :param name: The name of the bookmark that should be deleted.
        :type name: str
        """
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
        """
        Returns the path that is registered with the given bookmark name. If
        the name doesn't exist, it returns False.

        :param name: The of the bookmark to which the path is requested.
        :type name: str
        :return: The path registered with the given bookmark name, or False,
                 if the name doesn't exist
        :rtype: str | bool
        """
        for bookmark in self.list:
            if name == bookmark['name']:
                return bookmark['path']
        return False

    def bookmark_exists(self, name: str) -> bool:
        """
        Returns True if the bookmark with the given name exists and False, if
        it doesn't.

        :param name: Name of the bookmark to check for.
        :type name: str
        :return: True if bookmark exists, False if it doesn't.
        :rtype: bool
        """
        for bookmark in self.list:
            if name == bookmark['name']:
                return True
        return False

    def get_all(self) -> List[Dict[str, str]]:
        """
        Returns all bookmarks as a list of dicts.

        :return: List of dicts of all bookmarks. The dicts follows the format
                 {'name': '', 'path': ''}
        :rtype: List[Dict[str, str]]
        """
        return self.list
