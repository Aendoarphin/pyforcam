styles_main = """

    QMainWindow {
        font-family: Helvetica;
        background-color: rgb(255, 255, 255);
    }

    QPushButton {
        border: 1px solid;
        border-radius: 5px;
        padding: 0 10px 0 10px;
    }

    QTableWidget {
        border: 1px solid black;
    }

    QPushButton:pressed {
        margin-top: 1px;
    }

    QProgressBar {
        text-align: center;
        border: 1px solid black;
        border-radius: 20px;
    }
"""

styles_settings = u"""

    QDialog {
        
        background-color: rgb(255, 255, 255);
    }

    QLineEdit QTextBrowser {
        background-color: whitesmoke;
    }

    QGroupBox {
        padding: 0px;
    }

    QLabel[objectName='lblHeading'], QLabel[objectName='lblHeading2']{
        font-weight: bold;
    }

    QLabel[objectName='lblColorIndicatorValue'] {
        border: 1px solid gray;
        background-color: rgb(255, 255, 127);
    }
"""