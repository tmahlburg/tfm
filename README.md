# tfm
Simple file manager implemented in Qt for Python (Qt6). This project aims to create a simple, desktop agnostic, unix file-manager.
The initial version is going to be implemented in Python, though this might change in a later version, if there are performance problems.
The project is in an alpha stage right now and thus it is not advised to use it at the moment.
If you still want to try it, see below.

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
There are python packages for the alpha version to download on pypi. Install at your own risk using:
```
pip install tfm
```

## Screenshots
Coming soon.

## Roadmap

### Before 1.0
#### functionality
* auto extract | PARTIAL, needs better progress indication
* select last opened folder after returning from that folder to the last position
* open multiple selected files
* statusbar directory information
* differentiate default dropAction by destination
* handle file links
* allow multiple pastes at the same time
* give choices on handling existing files on paste
* open files with return key | DONE
* find maintained alternative to udevil -> probably pmount or udisks2
* implement network mounts, especially SMB shares
* mount ISOs
#### ui
* drag and drop folders as bookmarks in the bookmark view
#### infrastructure
* port to Qt6 | DONE

### Beyond 1.0 (most of these are maybes)
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
