from PyQt6 import QtCore, QtGui, QtWidgets
from settings_window import Ui_Dialog
from XML import XMLTagExtractor
from stylesheet import styles_main
import datetime as dt
import sys, os
from background import BackgroundImageWidget

def resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller."""
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

class Ui_mainWindow(QtCore.QObject):
    def __init__(self):
        super().__init__()
        # XML Extractor object
        self.extractor = XMLTagExtractor()
        self.settings_window = QtWidgets.QDialog()
        self.ui_settings = Ui_Dialog()
        self.ui_settings.setupUi(self.settings_window)
        self.address_list = []
        self.machines = []
        # Create a QTimer instance
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.fetch_data_continuously)
        # Flag to indicate whether the data has been fetched
        self.data_fetched = False
        # Loading element for gui
        self.loading_dots = 0
        self.loading_animation_running = False  # Add a flag to track the loading animation state
        # Enables/disables start/stop buttons based on signal
        self.ui_settings.has_ip.connect(self.enable_buttons)
        # Store float value of machine completion percentage
        self.table_percent = 0
        
    def listen(self):
        self.tableView.hideColumn(3)
        self.ui_settings.check_ip()
        self.extractor.timed_out.connect(lambda message: [self.stop_fetching_data(message)])
        self.actionOptions.triggered.connect(lambda: [self.update_settings_list(), self.open_settings()])
        self.btnStart.clicked.connect(self.start_fetching_data)
        self.btnStop.clicked.connect(self.stop_fetching_data)
        # self.timer.start(self.ui_settings.interval*1000)  # Start the timer initially
       
    def update_settings_list(self):
        stored_ips = self.ui_settings.ip_list
        temp_items = self.ui_settings.listAddress.findItems("", QtCore.Qt.MatchFlag.MatchContains)  # Get all items in the list widget
        
        for widget_item in temp_items:
            if widget_item.text() not in stored_ips:
                row = self.ui_settings.listAddress.row(widget_item)  # Get the row index of the item
                self.ui_settings.listAddress.takeItem(row)  # Remove the item from the list widget

    def enable_buttons(self, signal):
        self.btnStart.setEnabled(signal)
        self.btnStop.setEnabled(signal)
            
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
            # Call the fetch_data method to fetch data immediately
            self.fetch_data()
            self.timer.start(self.ui_settings.interval*1000)  # Start the timer initially
            self.set_timestamp()
            # Set the data_fetched flag to True
            self.data_fetched = True
            self.notify(f"Operation initiated")
            
    def stop_fetching_data(self, custom_message=None):
        if self.data_fetched:
            # Stop the timer
            self.timer.stop()
            # Set the data_fetched flag to False after stopping the timer
            self.data_fetched = False
            self.stop_loading()  # Stop the loading dots animation
            if custom_message != None:
                if custom_message == False:
                    self.notify("Operation terminated")
                else: self.notify(f"Operation terminated. Error: {custom_message}")
            else: self.notify("Operation terminated")

    def fetch_data_continuously(self):
        if self.data_fetched:
            # Call the fetch_data method with the appropriate mode
            self.start_loading()  # Start the loading dots animation
            self.fetch_data()  # You can modify the mode as needed
            self.set_timestamp()
            
    def set_timestamp(self):
        current_time = dt.datetime.now()
        hour = current_time.hour
        minute = current_time.minute
        self.lblTimeStamp.setText(f"Last Data Request: {hour:02d}:{minute:02d}")
        
    def closeEvent(self, event):
        # Override the closeEvent to stop the timer when the window is closed
        self.stop_fetching_data()
        event.accept()

    def fetch_data(self):
        self.address_list = self.ui_settings.ip_list
        # self.address_list = [
        #     "192.168.1.248", 
        #     "192.168.1.248",
        #     ]

        self.extractor.fetch_data(self.address_list, "5000", id=1)
        
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
        self.tableView.setRowCount(0)
        row_index = 0

        for machine_index in range(machine_count):
            tool_num_list = self.machines[machine_index].toolNum
            tool_life_list = self.machines[machine_index].toolLife
            initial_list = self.machines[machine_index].initial

            for i in range(tool_count):
                self.tableView.insertRow(row_index)
                self.tableView.setRowHeight(row_index, 75)
                tn_item = QtWidgets.QTableWidgetItem(str(tool_num_list[i]))
                m_item = QtWidgets.QTableWidgetItem("MA " + str(self.machines[machine_index].id))
                tl_item = QtWidgets.QTableWidgetItem(str(tool_life_list[i]))
                for twi in [tn_item, m_item, tl_item]: 
                    twi.setTextAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
                self.tableView.setItem(row_index, 0, tn_item)
                self.tableView.setItem(row_index, 1, m_item)
                self.tableView.setItem(row_index, 2, tl_item)
                tool_life = tool_life_list[i]
                initial_life = initial_list[i]
                critical = QtGui.QColor(255, 185, 185, 190)
                warning = QtGui.QColor(255, 255, 153, 190)
                item = QtWidgets.QTableWidgetItem("N/A")
                visible_item = QtWidgets.QTableWidgetItem()
                visible_item.setBackground(critical)
                visible_item.setTextAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)

                if tool_life != 'N/A' and initial_life != 'N/A':
                    try:
                        print(self.ui_settings.percentage)
                        tool_life_int = int(tool_life)
                        initial_life_int = int(initial_life)
                        if initial_life_int != 0:
                            float_percent = tool_life_int / initial_life_int
                            if float_percent <= 0:
                                state_item = QtWidgets.QTableWidgetItem("NG")
                                visible_item.setBackground(critical)
                            elif float_percent <= self.ui_settings.percentage * .01:
                                print(f"float_percent: {float_percent}\nsettings.percentage: {self.ui_settings.percentage}")
                                state_item = QtWidgets.QTableWidgetItem("OK")
                                visible_item.setBackground(warning)
                            elif float_percent > self.ui_settings.percentage * .01:
                                state_item = QtWidgets.QTableWidgetItem("OK")
                                visible_item.setBackground(QtGui.QColor(0,0,0,0))
                            else:
                                state_item = None
                            item.setText("{:.2f}".format(float_percent))
                            if state_item:
                                state_item.setTextAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
                                self.tableView.setItem(row_index, 5, state_item)
                        else:
                            visible_item.setText("INITIAL LIFE 0")
                        self.tableView.setItem(row_index, 3, item)
                        visible_item.setText("{:.0%}".format(float_percent))
                        self.tableView.setItem(row_index, 4, visible_item)
                    except ValueError:
                        self.tableView.setItem(row_index, 3, item)
                else:
                    self.tableView.setItem(row_index, 3, item)

                row_index += 1

        self.tableView.viewport().update()
        self.tableView.sortByColumn(3, QtCore.Qt.SortOrder.AscendingOrder)
        self.tableView.sortItems(4, QtCore.Qt.SortOrder.AscendingOrder)
        

    def open_settings(self):
        self.settings_window.show()
        
    def setupUi(self, mainWindow):
        mainWindow.setObjectName("mainWindow")
        mainWindow.setWindowModality(QtCore.Qt.WindowModality.NonModal)
        mainWindow.resize(1200, 700)
        mainWindow.setMinimumSize(QtCore.QSize(500, 500))
        icon = QtGui.QIcon()
        image_path = resource_path("resources/window-icon.jpg")
        icon.addPixmap(QtGui.QPixmap(image_path), QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.Off)
        mainWindow.setWindowIcon(icon)
        mainWindow.setStyleSheet(styles_main)
        mainWindow.setDocumentMode(False)
        mainWindow.setTabShape(QtWidgets.QTabWidget.TabShape.Rounded)

        self.centralwidget = BackgroundImageWidget(resource_path("resources/table-bg.png"))
        self.centralwidget.setObjectName("centralwidget")

        self.gridLayout_1 = QtWidgets.QGridLayout(self.centralwidget)
        self.gridLayout_1.setObjectName("gridLayout_1")        

        self.gridLayout_2 = QtWidgets.QGridLayout()
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.gridLayout_1.addLayout(self.gridLayout_2, 0, 0, 1, 1)

        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Minimum)
        self.gridLayout_2.addItem(spacerItem, 0, 2, 1, 1)

        self.lblLog = QtWidgets.QLabel(self.centralwidget, minimumSize=QtCore.QSize(27, 0), maximumSize=QtCore.QSize(27, 16777215))

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
        self.tableView.setSortingEnabled(True)
        
        self.tableView.setLayoutDirection(QtCore.Qt.LayoutDirection.LeftToRight)
        self.tableView.setFrameShape(QtWidgets.QFrame.Shape.NoFrame)
        self.tableView.setSizeAdjustPolicy(QtWidgets.QAbstractScrollArea.SizeAdjustPolicy.AdjustIgnored)
        self.tableView.setAutoScroll(True)
        self.tableView.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.NoSelection)
        self.tableView.setTextElideMode(QtCore.Qt.TextElideMode.ElideMiddle)
        self.tableView.setShowGrid(True)
        self.tableView.setColumnCount(6)
        self.tableView.setObjectName("tableView")
        self.tableView.setEditTriggers(QtWidgets.QAbstractItemView.EditTrigger.NoEditTriggers)

        def create_header_item():
            item = QtWidgets.QTableWidgetItem()
            font = QtGui.QFont("Segoe UI", 20, QtGui.QFont.Weight.DemiBold)
            font.setBold(True)
            item.setFont(font)
            item.setBackground(QtGui.QColor(165, 191, 218))
            return item

        self.tableView.setHorizontalHeaderItem(0, create_header_item()) # Tool No.
        self.tableView.setHorizontalHeaderItem(2, create_header_item()) # Machine
        self.tableView.setHorizontalHeaderItem(3, create_header_item()) # Life remaining
        self.tableView.setHorizontalHeaderItem(1, create_header_item()) # Percent (hidden)
        self.tableView.setHorizontalHeaderItem(4, create_header_item()) # Percent (visible)
        self.tableView.setHorizontalHeaderItem(5, create_header_item()) # State

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
        self.tableView.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.ResizeMode.Stretch)
        self.tableView.verticalHeader().setVisible(False)
        self.tableView.verticalHeader().setCascadingSectionResizes(True)
        self.tableView.verticalHeader().setDefaultSectionSize(30)
        self.tableView.verticalHeader().setHighlightSections(True)
        self.tableView.verticalHeader().setStretchLastSection(True)
        self.gridLayout_2.addWidget(self.tableView, 1, 0, 1, 5)        
        self.btnStart = QtWidgets.QPushButton(parent=self.centralwidget)
        self.btnStart.setMaximumSize(QtCore.QSize(149, 149))
        self.btnStart.setStyleSheet("background-color: rgb(212, 255, 210)")
        self.btnStart.setObjectName("btnStart")
        self.gridLayout_2.addWidget(self.btnStart, 0, 3, 1, 1)
        self.lblLogDesc = QtWidgets.QLabel(parent=self.centralwidget)
        self.lblLogDesc.setMinimumSize(QtCore.QSize(0, 0))
        self.lblLogDesc.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.lblLogDesc.setText("")
        self.lblLogDesc.setObjectName("lblLogDesc")
        self.lblTimeStamp = QtWidgets.QLabel(parent=self.centralwidget)
        self.lblTimeStamp.setMinimumSize(QtCore.QSize(0, 0))
        self.lblTimeStamp.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.lblTimeStamp.setText("")
        self.lblTimeStamp.setObjectName("lblTimeStamp")
        self.gridLayout_2.addWidget(self.lblLogDesc, 0, 2, 1, 1)
        self.gridLayout_2.addWidget(self.lblTimeStamp, 0, 1, 1, 1)
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
        self.actionExit.triggered.connect(mainWindow.close)
        self.listen()
        
        QtCore.QMetaObject.connectSlotsByName(mainWindow)

    def retranslateUi(self, mainWindow):
        _translate = QtCore.QCoreApplication.translate
        mainWindow.setWindowTitle(_translate("mainWindow", "Tool Life Utility"))
        self.lblLog.setText(_translate("mainWindow", "Log:"))
        self.btnStop.setText(_translate("mainWindow", "Stop"))
        item = self.tableView.horizontalHeaderItem(0)
        item.setText(_translate("mainWindow", "Tool No."))
        item = self.tableView.horizontalHeaderItem(1)
        item.setText(_translate("mainWindow", "Machine"))
        item = self.tableView.horizontalHeaderItem(2)
        item.setText(_translate("mainWindow", "Life Remaining"))
        item = self.tableView.horizontalHeaderItem(3)
        item.setText(_translate("mainWindow", "%"))
        item = self.tableView.horizontalHeaderItem(4)
        item.setText(_translate("mainWindow", "%"))
        item = self.tableView.horizontalHeaderItem(5)
        item.setText(_translate("mainWindow", "State"))
        self.btnStart.setText(_translate("mainWindow", "Start"))
        self.menuFile.setTitle(_translate("mainWindow", "File"))
        self.actionOptions.setText(_translate("mainWindow", "Options"))
        self.actionExit.setText(_translate("mainWindow", "Exit"))

if __name__ == '__main__':
    import sys
    app = QtWidgets.QApplication(sys.argv)
    mainWindow = QtWidgets.QMainWindow()
    ui = Ui_mainWindow()
    ui.setupUi(mainWindow)
    mainWindow.show()
    sys.exit(app.exec())