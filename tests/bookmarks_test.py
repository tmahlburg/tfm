from tfm.bookmarks_model import bookmarks_model as bookmarks

import os

import pytest


def setup_object(file_name: str) -> bookmarks:
    return bookmarks(bookmark_file_path=file_name)


def cleanup(file_name: str):
    os.remove(file_name)


def test_constructor():
    bookmark_file_content = """home|/home/user/
root|/
bookmark with spaces|/path with/spaces in it
"""
    bookmark_file_name = 'constructor'
    with open(bookmark_file_name, 'w') as f:
        f.write(bookmark_file_content)
    bookmark_list = setup_object(bookmark_file_name).get_all()

    assert(len(bookmark_list) == 3)
    assert(bookmark_list[0]['name'] == 'home')
    assert(bookmark_list[0]['path'] == '/home/user/')
    assert(bookmark_list[1]['name'] == 'root')
    assert(bookmark_list[1]['path'] == '/')
    assert(bookmark_list[2]['name'] == 'bookmark with spaces')
    assert(bookmark_list[2]['path'] == '/path with/spaces in it')

    cleanup(bookmark_file_name)


def test_add_bookmark():
    bookmark_file_name = 'add_bookmark'
    bm = setup_object(bookmark_file_name)

    bm.add_bookmark(name='home', path='/home/user')
    bm.add_bookmark(name='test',
                    path='/test/test/test/test/test/test/test/test/test/test/')
    bm.add_bookmark(name='', path='/empty/name')
    bm.add_bookmark(name='empty path', path='')

    expected_content = """home|/home/user
test|/test/test/test/test/test/test/test/test/test/test/
|/empty/name
empty path|
"""
    with open(bookmark_file_name) as f:
        read_content = f.read()
    assert(expected_content == read_content)

    expected_bookmark_list = [{'name': 'home', 'path': '/home/user'},
                              {'name': 'test',
                               'path': '/test/test/test/test/test/test/test/'
                                       'test/test/test/'},
                              {'name': '', 'path': '/empty/name'},
                              {'name': 'empty path', 'path': ''}]
    assert(expected_bookmark_list == bm.get_all())
    with pytest.raises(NameError):
        bm.add_bookmark(name='home', path='/home/')
    with pytest.raises(NameError):
        bm.add_bookmark(name='||', path='hallo')

    cleanup(bookmark_file_name)


def test_remove_bookmark():
    bookmark_file_name = 'remove_bookmark'
    bm = setup_object(bookmark_file_name)

    bm.add_bookmark(name='bm1', path='/test1')
    bm.add_bookmark(name='bm2', path='/test2')
    bm.remove_bookmark('bm1')

    expected_content = 'bm2|/test2\n'
    with open(bookmark_file_name) as f:
        read_content = f.read()
    assert(expected_content == read_content)

    expected_bookmark_list = [{'name': 'bm2', 'path': '/test2'}]
    assert(expected_bookmark_list == bm.get_all())

    cleanup(bookmark_file_name)


def test_get_path_from_name():
    bookmark_file_name = 'get_path_from_name'
    bm = setup_object(bookmark_file_name)

    bm.add_bookmark(name='exists', path='/path/to/exists')

    assert(not bm.get_path_from_name('does not exist'))
    assert(bm.get_path_from_name('exists') == '/path/to/exists')

    cleanup(bookmark_file_name)


def test_bookmark_exists():
    bookmark_file_name = 'bookmark_exists'
    bm = setup_object(bookmark_file_name)

    bm.add_bookmark(name='exists', path='/path/to/exists')

    assert(not bm.bookmark_exists('does not exist'))
    assert(bm.bookmark_exists('exists'))

    cleanup(bookmark_file_name)
