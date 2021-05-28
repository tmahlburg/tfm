import tfm.utility as u

import os


def test_handle_args():
    # File URL
    assert(u.handle_args(['a', 'file:///usr/bin/']) == '/usr/bin/')
    # Path
    assert(u.handle_args(['b', '/usr/bin/']) == '/usr/bin/')
    # Handle too few arguments
    assert(u.handle_args(['123']) == os.getenv('HOME'))
    # Handle too many arguments
    assert(u.handle_args(['/boot/', '/etc/', '/boot']) == '/etc/')
    # Handle irregular arguments
    assert(u.handle_args(['', 'not a dir']) == os.getenv('HOME'))
    # Handle non existant dirs
    assert(u.handle_args(['-100', '/non/existing/dir']) == os.getenv('HOME'))
