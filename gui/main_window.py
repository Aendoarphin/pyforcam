from PyQt6 import QtCore, QtGui, QtWidgets
from gui.settings_window import Ui_Dialog
from XML import XMLTagExtractor
from utils.logging import configure_logging
from utils.stylesheet import styles_main
import traceback

class Ui_mainWindow(QtCore.QObject):
    def __init__(self):
        super().__init__()
        self.settings_window = QtWidgets.QDialog()
        self.ui_settings = Ui_Dialog()
        self.ui_settings.setupUi(self.settings_window)
        self.extracted_data = {}
        self.table_headers = ["Tool No.", "Machine", "Life Remaining", "State"]
        self.table_data = {}
        self.machines = []
        # Create a QTimer instance
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.fetch_data_continuously)
        # Flag to indicate whether the data has been fetched
        self.data_fetched = False
        self.loading_dots = 0
        self.interval = 0
        self.loading_animation_running = False  # Add a flag to track the loading animation state
        
    def listen(self):
        self.actionOptions.triggered.connect(self.open_settings)
        self.btnStart.clicked.connect(self.start_fetching_data)
        self.btnStop.clicked.connect(self.stop_fetching_data)
        self.timer.start(2000)  # Start the timer initially
        
    def start_loading(self):
        if not self.loading_animation_running:  # Check if the animation is not already running
            # Create a QTimer instance for the animation
            self.loading_timer = QtCore.QTimer(self)
            self.loading_timer.timeout.connect(self.update_loading)
            # Start the timer with an interval of 500 milliseconds (adjust as needed)
            self.loading_timer.start(300)
            self.loading_animation_running = True  # Set the flag to indicate that the animation is running

    def stop_loading(self):
        if self.loading_animation_running:  # Check if the animation is running
            self.loading_timer.stop()
            self.notify("")  # Set the label to an empty string to clear the "Running..." message
            self.loading_animation_running = False  # Set the flag to indicate that the animation is not running

    def stop_fetching_data(self):
        if self.data_fetched:
            # Stop the timer
            self.timer.stop()
            # Set the data_fetched flag to False after stopping the timer
            self.data_fetched = False
            self.stop_loading()  # Stop the loading dots animation
            self.notify("Operation terminated")

    def update_loading(self):
        # Increment the number of dots in the animation
        self.loading_dots += 1
        if self.loading_dots > 3:
            self.loading_dots = 1
        # Update the label with the loading dots
        self.notify("Running" + "." * self.loading_dots)

    def notify(self, message):
        self.lblLogDesc.setText(message)
    
    def start_fetching_data(self):
        if not self.data_fetched:
            # Start the timer to call fetch_data every 5 seconds
            self.timer.start(2000)
            # Set the data_fetched flag to True after starting the timer
            self.data_fetched = True
            self.notify("Operation initiated")

    def fetch_data_continuously(self):
        if self.data_fetched:
            # Call the fetch_data method with the appropriate mode
            self.start_loading()  # Start the loading dots animation
            self.fetch_data("test")  # You can modify the mode as needed
        
    def closeEvent(self, event):
        # Override the closeEvent to stop the timer when the window is closed
        self.stop_fetching_data()
        event.accept()

    def fetch_data(self, mode=None):
        configure_logging()

        if mode == "test":
            print("TESTING STARTED")
            addresses = [
                "https://static.staticsave.com/testingforcam/assets.xml",
            ]
            user_tags = ["ProgramToolNumber", "ToolLife"]
            user_attributes = ["initial"]
            get_content = True

            extractor = XMLTagExtractor(addresses, user_tags, user_attributes, get_content)
            extractor.extract_xml_tag_content()
            self.machines = extractor.machines
        else:
            addresses = [
                "192.168.1.82"
            ]
            user_tags = ["ProgramToolNumber", "ToolLife"]
            user_attributes = ["initial"]
            get_content = True

            extractor = XMLTagExtractor(addresses, user_tags, user_attributes, get_content)
            extractor.extract_xml_tag_content()
        # Set the data_fetched flag to True after data is fetched
        self.data_fetched = True

        # Update the table when data is fetched
        self.update_table()

    def update_table(self):
        if not self.data_fetched:
            return

        # Clear the existing rows in the table
        self.tableView.clearContents()

        # try:
        #     max_indexes = max(len(machine.toolLife) for machine in self.machines)
        #     print(max_indexes)
        # except ValueError as e:
        #     traceback.print_tb(e.__traceback__)
        #     self.ui_settings.message.setText("Something went wrong")
        #     self.ui_settings.message.setIcon(QtWidgets.QMessageBox.Icon.Critical)
        #     self.ui_settings.message.exec()
        #     self.stop_fetching_data()
        #     return
        
        max_indexes = max(len(machine.toolLife) for machine in self.machines)

        # Set the number of rows in the table
        self.tableView.setRowCount(max_indexes)

        # Loop through the indexes and add the data to the table
        for row in range(max_indexes):
            for col in range(4):  # We have 4 columns (tool_num, address, tool_life, status)
                # Find the machine object that has data at the current index
                valid_machines = [machine for machine in self.machines if len(machine.toolLife) > row]

                if not valid_machines:
                    # No machines have data at this index, leave the cells empty
                    item = QtWidgets.QTableWidgetItem("")
                else:
                    # Use the first valid machine for the current index (you can adjust the logic as needed)
                    machine = valid_machines[0]

                    if col == 0:
                        # Tool Number
                        item = QtWidgets.QTableWidgetItem(str(machine.toolNum[row]) if len(machine.toolNum) > row else "")
                    elif col == 1:
                        # Address
                        item = QtWidgets.QTableWidgetItem(str(machine.address))
                    elif col == 2:
                        # Tool Life
                        item = QtWidgets.QTableWidgetItem(str(machine.toolLife[row]) if len(machine.toolLife) > row else "")
                    else:
                        # Status
                        initial = machine.initial[row] if len(machine.initial) > row else 1
                        tool_life = machine.toolLife[row] if len(machine.toolLife) > row else 0

                        if int(tool_life) / int(initial) < 0.15:
                            item = QtWidgets.QTableWidgetItem("NG")
                        else:
                            item = QtWidgets.QTableWidgetItem("OK")

                # Set the item in the current row and column
                self.tableView.setItem(row, col, item)
            
    def open_settings(self):
        self.settings_window.show()
        
    def setupUi(self, mainWindow):
        mainWindow.setObjectName("mainWindow")
        mainWindow.setWindowModality(QtCore.Qt.WindowModality.NonModal)
        mainWindow.resize(865, 840)
        mainWindow.setMinimumSize(QtCore.QSize(865, 840))
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("./test/files\\../../resources/window-icon.jpg"), QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.Off)
        mainWindow.setWindowIcon(icon)
        mainWindow.setStyleSheet(styles_main)
        mainWindow.setDocumentMode(False)
        mainWindow.setTabShape(QtWidgets.QTabWidget.TabShape.Rounded)
        self.centralwidget = QtWidgets.QWidget(parent=mainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayout_3 = QtWidgets.QGridLayout(self.centralwidget)
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.gridLayout_2 = QtWidgets.QGridLayout()
        self.gridLayout_2.setObjectName("gridLayout_2")
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Minimum)
        self.gridLayout_2.addItem(spacerItem, 0, 2, 1, 1)
        self.lblLog = QtWidgets.QLabel(parent=self.centralwidget)
        self.lblLog.setMinimumSize(QtCore.QSize(27, 0))
        self.lblLog.setMaximumSize(QtCore.QSize(27, 16777215))
        font = QtGui.QFont()
        font.setBold(True)
        self.lblLog.setFont(font)
        self.lblLog.setObjectName("lblLog")
        self.gridLayout_2.addWidget(self.lblLog, 0, 0, 1, 1)
        self.btnStop = QtWidgets.QPushButton(parent=self.centralwidget)
        self.btnStop.setMaximumSize(QtCore.QSize(149, 149))
        self.btnStop.setStyleSheet("background-color: rgb(255, 184, 185);")
        self.btnStop.setObjectName("btnStop")
        self.gridLayout_2.addWidget(self.btnStop, 0, 4, 1, 1)
        self.tableView = QtWidgets.QTableWidget(parent=self.centralwidget)
        self.tableView.setTabletTracking(False)
        self.tableView.setLayoutDirection(QtCore.Qt.LayoutDirection.LeftToRight)
        self.tableView.setStyleSheet("")
        self.tableView.setFrameShape(QtWidgets.QFrame.Shape.NoFrame)
        self.tableView.setSizeAdjustPolicy(QtWidgets.QAbstractScrollArea.SizeAdjustPolicy.AdjustIgnored)
        self.tableView.setAutoScroll(True)
        self.tableView.setAlternatingRowColors(True)
        self.tableView.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.NoSelection)
        self.tableView.setTextElideMode(QtCore.Qt.TextElideMode.ElideLeft)
        self.tableView.setShowGrid(True)
        self.tableView.setRowCount(20)
        self.tableView.setColumnCount(4)
        self.tableView.setObjectName("tableView")
        self.tableView.setEditTriggers(QtWidgets.QAbstractItemView.EditTrigger.NoEditTriggers)
        item = QtWidgets.QTableWidgetItem()
        font = QtGui.QFont()
        font.setBold(True)
        font.setItalic(False)
        font.setUnderline(True)
        font.setKerning(False)
        item.setFont(font)
        item.setBackground(QtGui.QColor(165, 191, 218))
        self.tableView.setHorizontalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        font = QtGui.QFont()
        font.setBold(True)
        font.setUnderline(True)
        font.setKerning(False)
        item.setFont(font)
        item.setBackground(QtGui.QColor(165, 191, 218))
        self.tableView.setHorizontalHeaderItem(1, item)
        item = QtWidgets.QTableWidgetItem()
        font = QtGui.QFont()
        font.setBold(True)
        font.setUnderline(True)
        font.setKerning(False)
        item.setFont(font)
        item.setBackground(QtGui.QColor(165, 191, 218))
        self.tableView.setHorizontalHeaderItem(2, item)
        item = QtWidgets.QTableWidgetItem()
        font = QtGui.QFont()
        font.setBold(True)
        font.setUnderline(True)
        font.setKerning(False)
        item.setFont(font)
        item.setBackground(QtGui.QColor(165, 191, 218))
        self.tableView.setHorizontalHeaderItem(3, item)
        item = QtWidgets.QTableWidgetItem()
        font = QtGui.QFont()
        font.setUnderline(False)
        item.setFont(font)
        brush = QtGui.QBrush(QtGui.QColor(165, 191, 218))
        brush.setStyle(QtCore.Qt.BrushStyle.NoBrush)
        item.setBackground(brush)
        self.tableView.setItem(0, 0, item)
        self.tableView.horizontalHeader().setCascadingSectionResizes(True)
        self.tableView.horizontalHeader().setDefaultSectionSize(215)
        self.tableView.horizontalHeader().setSortIndicatorShown(True)
        self.tableView.horizontalHeader().setStretchLastSection(True)
        self.tableView.verticalHeader().setVisible(False)
        self.tableView.verticalHeader().setCascadingSectionResizes(True)
        self.tableView.verticalHeader().setDefaultSectionSize(30)
        self.tableView.verticalHeader().setHighlightSections(True)
        self.tableView.verticalHeader().setSortIndicatorShown(True)
        self.tableView.verticalHeader().setStretchLastSection(True)
        self.gridLayout_2.addWidget(self.tableView, 1, 0, 1, 5)
        self.btnStart = QtWidgets.QPushButton(parent=self.centralwidget)
        self.btnStart.setMaximumSize(QtCore.QSize(149, 149))
        self.btnStart.setStyleSheet("background-color: rgb(212, 255, 210)")
        self.btnStart.setObjectName("btnStart")
        self.gridLayout_2.addWidget(self.btnStart, 0, 3, 1, 1)
        self.lblLogDesc = QtWidgets.QLabel(parent=self.centralwidget)
        self.lblLogDesc.setMinimumSize(QtCore.QSize(500, 0))
        self.lblLogDesc.setMaximumSize(QtCore.QSize(500, 16777215))
        self.lblLogDesc.setText("")
        self.lblLogDesc.setObjectName("lblLogDesc")
        self.gridLayout_2.addWidget(self.lblLogDesc, 0, 1, 1, 1)
        self.gridLayout_3.addLayout(self.gridLayout_2, 0, 1, 1, 1)
        mainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(parent=mainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 865, 22))
        self.menubar.setObjectName("menubar")
        self.menuFile = QtWidgets.QMenu(parent=self.menubar)
        self.menuFile.setObjectName("menuFile")
        mainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(parent=mainWindow)
        self.statusbar.setAutoFillBackground(False)
        self.statusbar.setSizeGripEnabled(True)
        self.statusbar.setObjectName("statusbar")
        mainWindow.setStatusBar(self.statusbar)
        self.actionOptions = QtGui.QAction(parent=mainWindow)
        self.actionOptions.setObjectName("actionOptions")
        self.actionExit = QtGui.QAction(parent=mainWindow)
        self.actionExit.setObjectName("actionExit")
        self.menuFile.addAction(self.actionOptions)
        self.menuFile.addAction(self.actionExit)
        self.menubar.addAction(self.menuFile.menuAction())

        self.retranslateUi(mainWindow)
        
        self.actionOptions.triggered.connect(self.open_settings)
        self.listen()
        
        QtCore.QMetaObject.connectSlotsByName(mainWindow)

    def retranslateUi(self, mainWindow):
        _translate = QtCore.QCoreApplication.translate
        mainWindow.setWindowTitle(_translate("mainWindow", "FORCAM Utility"))
        self.lblLog.setText(_translate("mainWindow", "Log:"))
        self.btnStop.setText(_translate("mainWindow", "Stop"))
        self.tableView.setSortingEnabled(True)
        item = self.tableView.horizontalHeaderItem(0)
        item.setText(_translate("mainWindow", "Tool No."))
        item = self.tableView.horizontalHeaderItem(1)
        item.setText(_translate("mainWindow", "Machine"))
        item = self.tableView.horizontalHeaderItem(2)
        item.setText(_translate("mainWindow", "Life Remaining"))
        item = self.tableView.horizontalHeaderItem(3)
        item.setText(_translate("mainWindow", "State"))
        __sortingEnabled = self.tableView.isSortingEnabled()
        self.tableView.setSortingEnabled(False)
        self.tableView.setSortingEnabled(__sortingEnabled)
        self.btnStart.setText(_translate("mainWindow", "Start"))
        self.menuFile.setTitle(_translate("mainWindow", "File"))
        self.actionOptions.setText(_translate("mainWindow", "Options"))
        self.actionExit.setText(_translate("mainWindow", "Exit"))

