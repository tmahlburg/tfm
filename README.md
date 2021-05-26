# tfm
Simple file manager implemented in Qt for Python (Qt5). This project aims to create a simple, desktop agnostic, unix file-manager.
The initial version is going to be implemented in Python, though this might change in a later version, if there are performance problems.
The project is in a pre alpha stage right now and thus it is not advised to use it at the moment.
If you still want to try it, a python package is available in the ```dist``` directory of this repository

## Features
* basic directory traversal
* window layout with toolbar, statusbar, main table view, fs tree and bookmarks
* open files using xdg-open
* cut, copy, paste (with progress information), renaming
* named bookmarks to directories
* show/hide dotfiles
* throw files and directories in the trash
* drag and drop (always moves)
* cli to open with a path or file url supplied
* show, mount and unmount devices using udevil

## How to install
There are experimental python packages in dist/. Install at your own risk using:
```
pip install tfm
```

## Screenshots
Coming soon.

## Roadmap

### Before 0.1
#### infrastructure
* proper error handling and logging
* voidlinux package
* AppImage
* add more tests

### Before 0.2
#### functionality
* implement network mounts, especially SMB shares
* mount ISOs
* auto extract
* open multiple selected files
* statusbar directory information
* differentiate default dropAction by destination
* handle file links
#### ui
* drag and drop folders as bookmarks in the bookmark view
#### infrastructure
* port to Qt6

### Beyond 0.2
#### functionality
* fuzzy search in folder
* restore from trash (should be implemented via a custom model/view)
* delete from trash (should be implemented via a custom model/view)
* mount MTP devices
#### ui
* optional preview pane
* open with dialog
* file previews
* context sensitive views and columns
* make links visually distinguishable
* file property dialog
* user configurable views and columns
* bookmark order configurable in the UI
#### accessability
* localization

## Non-Features
These features are never going to be part of tfm:

* dependencies on specific desktop environments
* window management like tabs, split views or similar
* plugins or script support
* a lot of configuration options
