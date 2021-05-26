#! /usr/bin/env python3

import sys

from PySide2.QtWidgets import QApplication

from tfm import tfm

if __name__ == "__main__":
    app = QApplication()
    # TODO: create clean CLI
    # TODO: document CLI
    window = tfm.tfm(sys.argv)
    window.show()
    sys.exit(app.exec_())
