#! /usr/bin/env python3

import sys

from PySide6.QtWidgets import QApplication

from tfm import tfm


def main():
    app = QApplication(sys.argv)
    QApplication.setApplicationName("tfm")
    QApplication.setApplicationVersion("0.3.3-ALPHA")

    # TODO: create clean CLI
    # TODO: document CLI
    window = tfm.tfm(sys.argv)
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
