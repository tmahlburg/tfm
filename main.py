# This Python file uses the following encoding: utf-8
import sys

from PySide2.QtWidgets import QApplication

from tfm import tfm

if __name__ == "__main__":
    app = QApplication()
    # TODO: create clean CLI
    # TODO: document CLI
    if len(sys.argv) > 1:
        default_path = sys.argv[1]
    else:
        default_path = ''
    window = tfm(default_path)
    window.show()
    sys.exit(app.exec_())
