

styles_main = """

    QMainWindow {
        background-color: rgb(255, 255, 255);
    }

    QPushButton {
        border: 1px solid;
        border-radius: 5px;
        padding: 0 10px 0 10px;
    }
    
    QPushButton[objectName='btnSortOrder'], QPushButton[objectName='btnStart'] {
        border-radius: 0px
    }
    
    QPushButton[objectName='btnStop'] {
        border-top-left-radius: 0px;
        border-bottom-left-radius: 0px;
    }
    
    QComboBox {
        width: 100px;
        border: 1px solid;
        border-top-left-radius: 5px;
        border-bottom-left-radius: 5px;
    }

    QTableWidget {
        border: 1px solid black;
    }

    QPushButton:pressed {
        margin-top: 1px;
    }
    
    QTableWidget {
        font-size: 25pt;
        font-weight: 63;
        background-color: transparent;
        gridline-color: lightgray;
        background-repeat: no-repeat; 
        background-position: center; 
        background-attachment: fixed;
        border: 0px solid white;
    }
    
    QHeaderView::section {
        background-color: lightgray;
        border-radius: 0px;
    }
    
    QLabel[objectName='lblTimeStamp'] { 
        border-right: 1px solid black; 
        border-left: 0px solid black;
        border-bottom: 0px solid black;
        border-top: 0px solid black;
        padding-right: 5px;
    }
"""

styles_settings = """

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
"""