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

## How to install
Don't right now. Making packages is the next item on my list though.

## Screenshots
Are going to be here soon.

## Roadmap

### Next features to implement
* show, mount and unmount devices using udevil or pmount
* restore from trash
* delete from trash
* handle multi selection statusbar information
* pasting status window on longer pastes
* link files
* cli, especially for being run by xdg-open -> support for file URLs

### Far away
#### functionality
* optimize network mounts, especially SMB shares
* mount ISOs etc.
* auto extract
* open multiple selected files
* statusbar directory informations
* search in folder
* differentiate dropAction by destination
#### ui
* save config per dir
* open with dialog
* optional preview pane
* file previews
* context sensitive views and columns
* file property dialog
* rename in place
* make links visually distinguishable
* user configurable views and columns
* bookmark order configurable in the U
#### accessability
* localization

### Infrastructure
* proper error handling and logging
* voidlinux package
* AppImage
* possibly archlinux package

## Non-Features
These features are going to be intentionally omitted:

* dependencies on specific desktop environments
* windows management like tabs, split views or similar
* plugins or script support
* a lot of configuration options

These features are not going to be implemented by me, but I wouldn't reject a good pull request for them:

* Windows support
