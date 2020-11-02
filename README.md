# tfm
Simple file manager implemented in Qt for Python. This project aims to create a simple, desktop agnostic, unix file-manager.
The initial version is going to be implemented in Python, though this might change in a later version, if there are performance problemss.
The Project is in a proof of concept stage right now and it is not advised to use it at the moment.

## Features:
* basic directory traversal
* window layout with toolbar, statusbar, main table view, fs tree and bookmarks
* open files using xdg-open
* cut, copy, paste, delete (with confirmation), renaming
* named bookmarks to folders
* show/hide dotfiles

## How to install
Don't right now. Making packages is the next item on my list though.

## Screenshots
Are going to be here soon.

## Roadmap

### Next features to implement:
* show, mount and unmount devices using udevil or pmount
* xdg-trash
* drag and drop between windows
* handle multi selection statusbar information
* pasting status window on longer pastes
* link files
* basic cli, especially for being run by xdg-open

### Far away:
* optimize network mounts, especially SMB shares
* save config per dir
* open with dialog
* optional preview pane
* file previews
* context sensitive views and columns
* auto extract
* mount ISOs etc.
* file property dialog
* localization
* open multiple selected files
* statusbar directory informations
* rename in place
* search in folder
* make links visually distinguishable
* user configurable views and columns

### Infrastructure
* test suite with github actions
* proper error handling and logging
* complete pydoc style documentation
* python package
* voidlinux package
* archlinux package
* AppImage

## Non-Features
These features are going to be intentionally omitted:

* dependencies on specific desktop environments
* windows management like tabs, split views or similar
* plugins or script support
* a lot of configuration options

These features are not going to be implemented by me, but I wouldn't reject a good pull request for them:

* Windows support
