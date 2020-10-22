# tfm
Simple file manager implemented in Qt for Python. This project aims to create a simple, desktop agnostic, unix file-manager.
The initial version is going to be implemented in Python, though this might change in a later version, if there are performance problems.
The Project is in a proof of concept stage right now and it is not advise to use it at the moment.

## Wishlist
These are the features, I would like to implement. Everything in italics is already implemented in some way.
### Essential:
* window layout:
  * top: *toolbar* with: old Opera style menu button, *navigation controls (up and back/forward through the navigation history)*, new {file|dir}, *adress bar*
  * middle:
    * left (individually hideable): *fs tree*, favorites / bookmarks
    * *right: current dir file listing*
  * *bottom: statusbar with item count, selcted file size, free space on disk*
* *xdg-open*
* *cut*, *copy*, paste, link, delete (with confirmation)
* *file context menu*
* dotfile handling

### Wanted:
* show, mount and unmount devices using udevil or pmount
* xdg-trash
* user configurable views and columns
* drag and drop between windows
* handle multi selection statusbar information

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

### Infrastructure

* test suite with github actions
* proper error handling and logging
* complete pydoc style documentation

## Unwishlist

These features are going to be intentionally omitted:

* dependencies on specific desktop environments
* windows management like tabs, split views or similar
* plugins or script support
* a lot of configuration options

These features are not going to be implemented by me, but I wouldn't reject a good pull request for them:

* Windows support
