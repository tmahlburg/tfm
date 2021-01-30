# tfm
Simple file manager implemented in Qt for Python. This project aims to create a simple, desktop agnostic, unix file-manager.
The initial version is going to be implemented in Python, though this might change in a later version, if there are performance problemss.
The Project is in a proof of concept stage right now and it is not advised to use it at the moment.
If you still want to try it, a python package is available in the ```dist``` directory of this repository

## Features
* basic directory traversal
* window layout with toolbar, statusbar, main table view, fs tree and bookmarks
* open files using xdg-open
* cut, copy, paste, renaming
* named bookmarks to folders
* show/hide dotfiles
* throw files and dirs in the trash
* drag and drop (always moves)
* cli to open via path or file url
* show, mount and unmount devices using udevil

## How to install
Don't right now. Making packages is the next item on my list though.

## Screenshots
Are going to be here soon.

## Roadmap

### Before 0.1
#### functionality
* pasting status window on longer pastes
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
* link files
#### ui
* drag and drop folders as bookmarks in the bookmark view
#### infrastructure
* port to Qt6

### Beyond 0.2
#### functinality
* search in folder
* restore from trash (should be implemented via a custom model/view)
* delete from trash (should be implemented via a custom model/view)
#### ui
* save config per dir
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
These features are going to be intentionally omitted:

* dependencies on specific desktop environments
* windows management like tabs, split views or similar
* plugins or script support
* a lot of configuration options
