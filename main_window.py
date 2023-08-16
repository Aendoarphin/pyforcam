from PyQt6 import QtCore, QtGui, QtWidgets
from settings_window import Ui_Dialog
from XML import XMLTagExtractor
from stylesheet import styles_main
from background import BackgroundImageWidget
from log import configure_logging
from class_utils import NumericTableWidgetItem
import datetime as dt
import sys, os, logging

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
        self.logger = logging.getLogger(__name__)
        configure_logging()
        self.extractor = XMLTagExtractor()
        self.settings_window = QtWidgets.QDialog()
        self.ui_settings = Ui_Dialog()
        self.ui_settings.setupUi(self.settings_window)
        self.ui_settings.has_ip.connect(self.enable_buttons)
        self.address_list = []
        self.machines = []
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.fetch_data_continuously)
        self.data_fetched = False
        self.loading_dots = 0
        self.loading_animation_running = False
        self.table_percent = 0
        self.sort_mode = QtCore.Qt.SortOrder.AscendingOrder
        self.sorted_column = 2
        
    def listen(self):
        self.btnSortOrder.setEnabled(False)
        self.comboColumn.setEnabled(False)
        self.tableView.hideColumn(3)
        self.ui_settings.check_ip()
        self.extractor.timed_out.connect(lambda message: [self.stop_fetching_data(message)])
        self.actionOptions.triggered.connect(lambda: [self.update_settings_list(), self.open_settings()])
        self.btnStart.clicked.connect(self.start_fetching_data)
        self.btnStop.clicked.connect(self.stop_fetching_data)
        self.btnSortOrder.clicked.connect(lambda: [self.change_sort_order()])
        self.comboColumn.currentTextChanged.connect(lambda: [self.change_sort_type()])
        
    def change_sort_order(self):
        selected = self.comboColumn.currentText()
        if selected == "Tool Life": self.sorted_column = 2
        elif selected == "Percentage": self.sorted_column = 3
        else: self.sorted_column = 1
        if self.btnSortOrder.text() == "↑":
            self.sort_mode = QtCore.Qt.SortOrder.DescendingOrder
            self.btnSortOrder.setText("↓")
        else:
            self.sort_mode = QtCore.Qt.SortOrder.AscendingOrder
            self.btnSortOrder.setText("↑")
        self.fetch_data()
        
    def change_sort_type(self):
        selected = self.comboColumn.currentText()
        if selected == "Tool Life": self.sorted_column = 2
        elif selected == "Percentage": self.sorted_column = 3
        else: self.sorted_column = 1
        self.fetch_data()
       
    def update_settings_list(self):
        stored_ips = self.ui_settings.ip_list
        stored_machine_names = self.ui_settings.machine_name_list
        temp_items = self.ui_settings.listAddress.findItems("", QtCore.Qt.MatchFlag.MatchContains)
        
        for widget_item in temp_items:
            ip_address, machine_name = self.parse_item_text(widget_item.text())
            
            if ip_address not in stored_ips or machine_name not in stored_machine_names:
                row = self.ui_settings.listAddress.row(widget_item)
                self.ui_settings.listAddress.takeItem(row)

    def parse_item_text(self, item_text):
        parts = item_text.split(', Machine Name: ')
        ip_address = parts[0].replace("IP: ", "")
        machine_name = parts[1]
        return ip_address, machine_name

    def enable_buttons(self, signal):
        self.btnStart.setEnabled(signal)
        self.btnStop.setEnabled(signal)
            
    def start_loading(self):
        if not self.loading_animation_running:
            self.loading_timer = QtCore.QTimer(self)
            self.loading_timer.timeout.connect(self.update_loading)
            self.loading_timer.start(300)
            self.loading_animation_running = True

    def stop_loading(self):
        if self.loading_animation_running:
            self.loading_timer.stop()
            self.notify("")
            self.loading_animation_running = False

    def update_loading(self):
        self.loading_dots += 1
        if self.loading_dots > 3:
            self.loading_dots = 1
        self.notify("Running" + "." * self.loading_dots)

    def notify(self, message):
        self.lblLogDesc.setText(message)
            
    def start_fetching_data(self):
        if not self.data_fetched:
            self.notify("Operation initiated")
            self.fetch_data()
            self.data_fetched = True
            self.btnSortOrder.setEnabled(True)
            self.comboColumn.setEnabled(True)
            self.timer.start(self.ui_settings.interval * 1000)
            self.set_timestamp()
            
    def stop_fetching_data(self, custom_message=None):
        if self.data_fetched:
            self.timer.stop()
            self.data_fetched = False
            self.stop_loading()
            self.btnSortOrder.setEnabled(False)
            self.comboColumn.setEnabled(False)
            if custom_message in [None, False]:
                self.notify("Operation terminated")
            else:
                self.notify(f"Operation terminated. {custom_message}")


    def fetch_data_continuously(self):
        if self.data_fetched:
            self.start_loading()
            self.fetch_data()
            self.set_timestamp()

    def set_timestamp(self):
        current_time = dt.datetime.now()
        hour = current_time.hour
        minute = current_time.minute
        self.lblTimeStamp.setText(f"Last Data Request: {hour:02d}:{minute:02d}")
         
    def closeEvent(self, event):
        self.stop_fetching_data()
        event.accept()

    def fetch_data(self):
        self.extractor.machine_names = self.ui_settings.machine_name_list
        self.address_list = self.ui_settings.ip_list
        # self.address_list = [
        #     "192.168.1.222",
        #     "192.168.1.222",
        #     "192.168.1.222",
        #     "192.168.1.222",
        #     ]
        self.extractor.fetch_data(self.address_list, "5000", 1, self.extractor.machine_names)
        self.machines = self.extractor.machines
        self.data_fetched = True
        self.update_table(show_yellow=self.ui_settings.yellow)

    def update_table(self, show_yellow=False):
        machine_count = len(self.machines)
        if machine_count == 0:
            self.logger.info("No machines detected")
            return
        self.tableView.setRowCount(0)
        row_index = 0

        for machine_index in range(machine_count):
            tool_num_list = self.machines[machine_index].toolNum
            tool_count = len(tool_num_list)
            tool_life_list = self.machines[machine_index].toolLife
            initial_list = self.machines[machine_index].initial

            for i in range(tool_count):
                tool_life = tool_life_list[i]
                initial_life = initial_list[i]
                if tool_life != 'NULL' and initial_life != 'NULL':
                    try:
                        tool_life_int = int(tool_life)
                        initial_life_int = int(initial_life)
                        if initial_life_int != 0:
                            float_percent = tool_life_int / initial_life_int
                            tn_item = QtWidgets.QTableWidgetItem(tool_num_list[i])
                            m_item = QtWidgets.QTableWidgetItem(self.machines[machine_index].machine_name)
                            tl_item = NumericTableWidgetItem(tool_life_list[i])

                            self.tableView.insertRow(row_index)
                            self.tableView.setRowHeight(row_index, 75)
                            self.tableView.setItem(row_index, 0, tn_item)
                            self.tableView.setItem(row_index, 1, m_item)
                            self.tableView.setItem(row_index, 2, tl_item)

                            critical = QtGui.QColor(255, 185, 185, 190)
                            warning = QtGui.QColor(255, 255, 153, 190)
                            item = QtWidgets.QTableWidgetItem("NULL")
                            item2 = QtWidgets.QTableWidgetItem("NULL")
                            percent_item = QtWidgets.QTableWidgetItem()
                            percent_item.setBackground(critical)

                            for twi in [tn_item, m_item, tl_item, item, item2, percent_item]:
                                twi.setTextAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)

                            if float_percent <= 0:
                                state_item = QtWidgets.QTableWidgetItem("NG")
                                percent_item.setBackground(critical)
                            elif float_percent <= self.ui_settings.percentage * 0.01:
                                state_item = QtWidgets.QTableWidgetItem("OK")
                                percent_item.setBackground(warning)
                            else:
                                state_item = QtWidgets.QTableWidgetItem("OK")
                                percent_item.setBackground(QtGui.QColor(0, 0, 0, 0))

                            item.setText("{:.2f}".format(float_percent))
                            if state_item:
                                state_item.setTextAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
                                self.tableView.setItem(row_index, 5, state_item)

                            self.tableView.setItem(row_index, 3, item)
                            percent_item.setText("{:.0%}".format(float_percent))
                            self.tableView.setItem(row_index, 4, percent_item)

                            if show_yellow:
                                if float_percent < self.ui_settings.percentage * 0.01 and float_percent > 0:
                                    self.tableView.showRow(row_index)
                                else:
                                    self.tableView.hideRow(row_index)
                            else:
                                self.tableView.showRow(row_index)

                        row_index += 1

                    except ValueError:
                        pass
                else:
                    pass

        self.tableView.viewport().update()
        # Tool No. 0, Machine 1, Tool Life 2, % 3
        self.tableView.sortByColumn(self.sorted_column, self.sort_mode)
        self.tableView.setSortingEnabled(False)
        self.logger.info(f"Table updated | Total IP Addresses: {len(self.address_list)}")

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
        
        self.comboColumn = QtWidgets.QComboBox(parent=self.centralwidget)
        self.comboColumn.addItems(["Tool Life", "Percentage", "Machine Name"])
        self.comboColumn.setObjectName("comboColumn")
        self.gridLayout_2.addWidget(self.comboColumn, 0, 3, 1, 1)
        
        self.btnSortOrder = QtWidgets.QPushButton(parent=self.centralwidget)
        self.btnSortOrder.setMaximumSize(QtCore.QSize(149, 149))
        self.btnSortOrder.setObjectName("btnSortOrder")
        self.gridLayout_2.addWidget(self.btnSortOrder, 0, 4, 1, 1)
        
        self.btnStop = QtWidgets.QPushButton(parent=self.centralwidget)
        self.btnStop.setMaximumSize(QtCore.QSize(149, 149))
        self.btnStop.setStyleSheet("background-color: rgb(255, 184, 185);")
        self.btnStop.setObjectName("btnStop")
        self.gridLayout_2.addWidget(self.btnStop, 0, 6, 1, 1)

        
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
        self.gridLayout_2.addWidget(self.tableView, 1, 0, 1, 7)        
        self.btnStart = QtWidgets.QPushButton(parent=self.centralwidget)
        self.btnStart.setMaximumSize(QtCore.QSize(149, 149))
        self.btnStart.setStyleSheet("background-color: rgb(212, 255, 210)")
        self.btnStart.setObjectName("btnStart")
        self.gridLayout_2.addWidget(self.btnStart, 0, 5, 1, 1)
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
        self.actionAppearance = QtGui.QAction(parent=mainWindow)
        self.actionAppearance.setObjectName("actionAppearance")
        self.actionExit = QtGui.QAction(parent=mainWindow)
        self.actionExit.setObjectName("actionExit")
        self.menuFile.addAction(self.actionOptions)
        self.menuFile.addAction(self.actionAppearance)
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
        self.btnSortOrder.setText(_translate("mainWindow", "↑"))
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
        self.actionAppearance.setText(_translate("mainWindow", "Appearance"))
        self.actionExit.setText(_translate("mainWindow", "Exit"))

def main():
    app = QtWidgets.QApplication(sys.argv)
    mainWindow = QtWidgets.QMainWindow()
    ui = Ui_mainWindow()
    ui.setupUi(mainWindow)
    mainWindow.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    configure_logging()  # Configure the logger
    logger = logging.getLogger(__name__)
    try:
        main()
    except Exception:
        # Log the full exception traceback at the ERROR level
        logger.exception("An error occurred")