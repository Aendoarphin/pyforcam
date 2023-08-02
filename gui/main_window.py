from PyQt6 import QtCore, QtGui, QtWidgets
from gui.settings_window import Ui_Dialog
from XML import XMLTagExtractor
from utils.logging import configure_logging
from utils.stylesheet import styles_main

class Ui_mainWindow(QtCore.QObject):
    def __init__(self):
        super().__init__()
        # XML Extractor object
        self.extractor = XMLTagExtractor()
        
        self.settings_window = QtWidgets.QDialog()
        self.ui_settings = Ui_Dialog()
        self.ui_settings.setupUi(self.settings_window)
        self.url_list = []
        self.machines = []
        
        # Create a QTimer instance
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.fetch_data_continuously)
        
        # Flag to indicate whether the data has been fetched
        self.data_fetched = False
        
        # Loading element for gui
        self.loading_dots = 0
        self.interval = 0
        self.loading_animation_running = False  # Add a flag to track the loading animation state
        
    def listen(self):
        self.actionOptions.triggered.connect(self.open_settings)
        self.btnStart.clicked.connect(self.start_fetching_data)
        self.btnStop.clicked.connect(self.stop_fetching_data)
        self.timer.start(1000)  # Start the timer initially
        
    def start_loading(self):
        if not self.loading_animation_running:  # Check if the animation is not already running
            # Create a QTimer instance for the animation
            self.loading_timer = QtCore.QTimer(self)
            self.loading_timer.timeout.connect(self.update_loading)
            # Start the timer with an interval of x milliseconds (adjust as needed)
            self.loading_timer.start(300)
            self.loading_animation_running = True  # Set the flag to indicate that the animation is running

    def stop_loading(self):
        if self.loading_animation_running:  # Check if the animation is running
            self.loading_timer.stop()
            self.notify("")  # Set the label to an empty string to clear the "Running..." message
            self.loading_animation_running = False  # Set the flag to indicate that the animation is not running

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
            # Start the timer to call fetch_data every 60 seconds
            self.timer.start(1000)
            # Set the data_fetched flag to True after starting the timer
            self.data_fetched = True
            self.notify("Operation initiated")
            
    def stop_fetching_data(self):
        if self.data_fetched:
            # Stop the timer
            self.timer.stop()
            # Set the data_fetched flag to False after stopping the timer
            self.data_fetched = False
            self.stop_loading()  # Stop the loading dots animation
            self.notify("Operation terminated")

    def fetch_data_continuously(self):
        if self.data_fetched:
            # Call the fetch_data method with the appropriate mode
            self.start_loading()  # Start the loading dots animation
            self.fetch_data()  # You can modify the mode as needed
        
    def closeEvent(self, event):
        # Override the closeEvent to stop the timer when the window is closed
        self.stop_fetching_data()
        event.accept()

    def fetch_data(self):
        configure_logging()
        # self.url_list = self.ui_settings.full_address_list
        self.url_list = [
            "192.168.1.248", 
            "192.168.1.248", 
            "192.168.1.248", 
            "192.168.1.248", 
            "192.168.1.248", 
            "192.168.1.248", 
            "192.168.1.248",
            "192.168.1.248",
            "192.168.1.248",
            "192.168.1.248",
            "192.168.1.248",
            "192.168.1.248",
            "192.168.1.248",
            "192.168.1.248",
            "192.168.1.248",
            "192.168.1.248",
            "192.168.1.248",
            "192.168.1.248",
            "192.168.1.248",
            "192.168.1.248",
            "192.168.1.248",
            ]
        
        self.extractor.fetch_data(self.url_list, "8000", id=1)
        self.machines = self.extractor.machines
        
        # Set the data_fetched flag to True after data is fetched
        self.data_fetched = True

        # Update the table when data is fetched
        self.update_table()

    def update_table(self):
        machine_count = len(self.machines)
        if machine_count == 0:
            return  # Do nothing if there are no machines in the list

        tool_count = len(self.machines[0].toolNum)

        # Clear the table completely before updating
        self.tableView.setRowCount(0)  # This will clear the table's model

        # Initialize variables to keep track of row and machine indices
        row_index = 0
        machine_index = 0

        # Add new rows with updated data
        for _ in range(machine_count):
            tool_num_list = self.machines[machine_index].toolNum
            tool_life_list = self.machines[machine_index].toolLife
            initial_list = self.machines[machine_index].initial

            for i in range(tool_count):
                # Insert a new row with the updated data
                self.tableView.insertRow(row_index)
                
                # Set values for each column in the current row
                self.tableView.setItem(row_index, 0, QtWidgets.QTableWidgetItem(str(tool_num_list[i])))
                self.tableView.setItem(row_index, 1, QtWidgets.QTableWidgetItem(str(self.machines[machine_index].id)))
                self.tableView.setItem(row_index, 2, QtWidgets.QTableWidgetItem(str(tool_life_list[i])))

                # Calculate and set the value for the fourth column
                tool_life = tool_life_list[i]
                initial_life = initial_list[i]
                critical = QtGui.QColor(255, 185, 185)
                warning = QtGui.QColor(255, 255, 153)
                if tool_life != 'N/A' and initial_life != 'N/A':
                    try:
                        tool_life_int = int(tool_life)
                        initial_life_int = int(initial_life)
                        if initial_life_int != 0:
                            progress = tool_life_int / initial_life_int
                            if progress == 0:
                                item = QtWidgets.QTableWidgetItem("{:.2f}".format(progress) + " NG")
                                item.setBackground(critical)
                            elif progress < self.ui_settings.percentage:
                                item = QtWidgets.QTableWidgetItem("{:.2f}".format(progress) + " OK")
                                item.setBackground(warning)
                            else:
                                item = QtWidgets.QTableWidgetItem("{:.2f}".format(progress))
                            self.tableView.setItem(row_index, 3, item)
                        else:
                            self.tableView.setItem(row_index, 3, QtWidgets.QTableWidgetItem("INITIAL LIFE 0").setBackground(critical))
                    except ValueError:
                        self.tableView.setItem(row_index, 3, QtWidgets.QTableWidgetItem("N/A"))
                else:
                    item = QtWidgets.QTableWidgetItem("N/A")
                    item.setBackground(critical)
                    self.tableView.setItem(row_index, 3, item)

                row_index += 1 # FIGURING OUT HOW TO GET THE TABLE TO POPULATE WHILE NOT ADDING DUPLICATE DATA

            # Move to the next machine
            machine_index += 1

        # Ensure that the table view is refreshed with the new data
        self.tableView.viewport().update()

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

