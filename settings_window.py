from PyQt6 import QtCore, QtGui, QtWidgets
from stylesheet import styles_settings
import json, os, re


class Ui_Dialog(QtCore.QObject):
    has_ip = QtCore.pyqtSignal(bool)
    def __init__(self):
        super().__init__()
        self.network = ""
        self.host = ""
        self.full_address = ""
        self.ip_list = []
        self.machine_name = ""
        self.machine_name_list = []
        
        self.percentage = .3
        self.interval = 0
        self.yellow = False
        self.data = {}
        
        self.normal = "background-color: rgb(255,255,255)"
        self.error = "background-color: rgb(255,185,185)"
        
        self.var_info = ""
        
        self.message = QtWidgets.QMessageBox()
    
    def listen(self, Dialog):
        self.txtHost.setEnabled(False)
        self.txtMachineName.setEnabled(False)
        self.load_settings()
        self.interval = int(self.spinInterval.value())
        self.percentage = self.spinPercent.value()
        
        self.spinInterval.valueChanged.connect(lambda value: self.set_interval(value))
        self.spinPercent.valueChanged.connect(lambda value: self.set_percentage(value))
        
        
        self.btnSetModular.clicked.connect(lambda: self.enable_network_input())

        self.btnPlus.clicked.connect(lambda: self.update_list(self.btnPlus.text()))
        self.btnMinus.clicked.connect(lambda: self.update_list(self.btnMinus.text()))
        self.checkYellow.stateChanged.connect(lambda: self.set_yellow())
        self.var_info = f"Interval: {self.interval}s\nPercentage:{self.percentage}"

        self.buttonBox.button(QtWidgets.QDialogButtonBox.StandardButton.Apply).clicked.connect(lambda: 
            [
                self.show_message(), 
                self.show_message(self.var_info, True), 
                self.save_settings(), 
                self.check_ip(), 
                Dialog.accept()
             ])
        
        self.buttonBox.button(QtWidgets.QDialogButtonBox.StandardButton.RestoreDefaults).clicked.connect(lambda:
            [
                self.clear_inputs()
            ])
        
        self.buttonBox.rejected.connect(Dialog.reject)
        
    def clear_inputs(self):
        self.txtNetwork1.clear()
        self.txtNetwork2.clear()
        self.txtNetwork3.clear()
        self.txtHost.clear()
        self.txtMachineName.clear()
        self.spinPercent.setValue(30)
        self.spinInterval.setValue(30)
        self.listAddress.clear()
        self.ip_list.clear()
        self.machine_name_list.clear()
        self.checkYellow.setChecked(False)
    
    def set_interval(self, value):
        self.interval = int(value)
        self.update_display()
    def set_percentage(self, value):
        self.percentage = value
        self.update_display()
        
    def set_yellow(self):
        if self.checkYellow.isChecked(): self.yellow = True
        else: self.yellow = False
        
    def update_display(self):
        self.var_info = f"Interval: {self.interval}s\nPercentage: {self.percentage}"
        
    def show_message(self, message=None, custom=None):
        if custom == True:
            self.message.setText(message)
        else:
            self.message.setText(f"Link format: http://(ADDRESS):5000/assets\nAddresses: {self.ip_list}")
        self.message.setIcon(QtWidgets.QMessageBox.Icon.Information)
        self.message.exec()
        
    def update_list(self, mode: str):
        self.host = self.txtHost.text()
        self.machine_name = self.txtMachineName.text()
        self.full_address = self.network + self.host
        if mode == "+":
            if self.network != "" and self.host != "" and self.machine_name != "":
                self.listAddress.addItem(f"IP: {self.full_address}, Machine Name: {self.machine_name}")
                self.ip_list.append(self.full_address)
                self.machine_name_list.append(self.machine_name)
                self.txtHost.clear()
                self.txtMachineName.clear()
                self.txtHost.setStyleSheet(self.normal)
                self.txtMachineName.setStyleSheet(self.normal)
                self.print_list()
                print(f"ADDRESS WAS ADDED: {self.ip_list}")
                print(f"MACHINE NAME WAS ADDED: {self.machine_name_list}")
                self.full_address = ""
                self.host = ""
                self.machine_name = ""
            else: 
                self.txtHost.setStyleSheet(self.error)
                self.txtMachineName.setStyleSheet(self.error)

        if mode == "-":
            self.remove_sel()
            self.print_list()
            print(f"ITEM REMOVED")
    
    def print_list(self):
        print("\nDATA:\n")
        for ip in self.ip_list:
            print(ip)
        for m in self.machine_name_list:
            print(m)

    def remove_sel(self):
        # Retrieve the selected items from the QListWidget
        selected_items = self.listAddress.selectedItems()
        
        # If no items are selected, return without doing anything
        if not selected_items:
            return
        
        # Iterate through each selected item and remove it from the QListWidget and lists
        for item in selected_items:
            # Get the text of the selected item
            item_text = item.text()
            
            # Split the item text into IP address and machine name
            ip_address, machine_name = item_text.split(', Machine Name: ', 1)
            
            # Remove the IP address from the ip_list if it exists
            if ip_address in self.ip_list:
                self.ip_list.remove(ip_address)
            
            # Remove the machine name from the machine_name_list if it exists
            if machine_name in self.machine_name_list:
                self.machine_name_list.remove(machine_name)
            
            # Remove the item from the QListWidget
            row = self.listAddress.row(item)
            self.listAddress.takeItem(row)
        
        # Clear the selected items list
        self.listAddress.clearSelection()

        
    def enable_network_input(self):
        input_value = [self.txtNetwork1.text(), self.txtNetwork2.text(), self.txtNetwork3.text()]
        input_obj = [self.txtNetwork1, self.txtNetwork2, self.txtNetwork3]
        # If any of fields are empty
        if "" in input_value:
            for obj in input_obj:
                obj.setStyleSheet(self.error)
            if self.txtNetwork1.isEnabled() == True : 
                self.txtHost.setEnabled(False)
                self.txtMachineName.setEnabled(False)
            self.network = ""
            print(f"NETWORK ADDRESS WAS RESET: {self.network}")
        elif all(input != "" for input in input_value):
            if self.btnSetModular.text() == "Change":
                for obj in input_obj:
                    obj.setStyleSheet(self.normal)
                    obj.setEnabled(True)
                    obj.setText("")
                self.txtHost.setEnabled(False)
                self.txtMachineName.setEnabled(False)
                self.btnSetModular.setText("Set")
                self.network = ""
            else:
                for obj in input_obj:
                    obj.setStyleSheet(self.normal)
                    obj.setEnabled(False)
                self.network = self.txtNetwork1.text() + "." + self.txtNetwork2.text() + "." + self.txtNetwork3.text() + "."
                self.txtHost.setEnabled(True)
                self.txtMachineName.setEnabled(True)
                self.btnSetModular.setText("Change")
                print(f"NETWORK ADDRESS WAS SET: {self.network}")
    
    def save_settings(self):
        self.data = {
            "network": self.network,
            "ip_list": self.ip_list,
            "percentage": self.percentage,
            "interval": self.interval,
            "machine_name_list": self.machine_name_list,
            "show_yellow": self.yellow
        }
        # Create the directory if it doesn't exist
        directory = "./config"
        os.makedirs(directory, exist_ok=True)

        # Write the data to the file
        with open("./config/settings.json", "w") as f:
            json.dump(self.data, f)

    def load_settings(self):
        try:
            with open("./config/settings.json", "r") as f:
                self.data = json.load(f)

            # Update attributes with values from the loaded data
            self.network = self.data.get("network", self.network)
            if self.network != "":
                parts = self.network.split(".")
                self.txtNetwork1.setText(parts[0])
                self.txtNetwork2.setText(parts[1])
                self.txtNetwork3.setText(parts[2])
            
            # Load the ip_list and machine_name_list from the loaded data
            self.ip_list = self.data.get("ip_list", self.ip_list)
            self.machine_name_list = self.data.get("machine_name_list", self.machine_name_list)
            
            # Populate the QListWidget with items from ip_list and machine_name_list
            for ip, machine_name in zip(self.ip_list, self.machine_name_list):
                item_text = f"{ip}, Machine Name: {machine_name}"
                self.listAddress.addItem(item_text)
            
            # Load other settings
            self.percentage = self.data.get("percentage", self.percentage)
            if self.percentage != "":
                try:
                    num_float = float(self.percentage)
                    num_int = int(num_float)
                    self.spinPercent.setValue(num_int)
                except ValueError:
                    # Not a valid float, set the value as is
                    self.spinPercent.setValue(self.percentage)
            
            self.interval = self.data.get("interval", self.interval)
            if self.interval != "": self.spinInterval.setValue(self.interval)
                
            self.yellow = self.data.get("show_yellow", self.yellow)
            if self.yellow in [True, False]: self.checkYellow.setChecked(self.yellow)
            else: self.checkYellow.setChecked(False)
            
            current_settings = f"Network:{self.network}\nIP List: {self.ip_list}\nMachine Name List: {self.machine_name_list}\nPercentage: {self.percentage}\nInterval: {self.interval}\nData: {self.data}"
            self.show_message(current_settings, True)
        except FileNotFoundError:
            # If settings.json is not found, continue with default values
            self.show_message("No settings detected. Assign addresses in settings", True)
            print("Settings file not found. Using default settings.")
                
    def check_ip(self):
        # Set the flag to check presence of ip addresses
        if self.ip_list != []:
            self.has_ip.emit(True)
        else:
            self.has_ip.emit(False)
    
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.setWindowModality(QtCore.Qt.WindowModality.ApplicationModal)
        Dialog.resize(510, 428)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Preferred, QtWidgets.QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(Dialog.sizePolicy().hasHeightForWidth())
        Dialog.setSizePolicy(sizePolicy)
        Dialog.setMinimumSize(QtCore.QSize(0, 0))
        Dialog.setMaximumSize(QtCore.QSize(16777215, 16777215))
        Dialog.setStyleSheet(styles_settings)
        self.gridLayout_2 = QtWidgets.QGridLayout(Dialog)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.gridLayout = QtWidgets.QGridLayout()
        self.gridLayout.setObjectName("gridLayout")
        self.horizontalLayout_8 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_8.setObjectName("horizontalLayout_8")
        self.lblNetwork = QtWidgets.QLabel(parent=Dialog)
        self.lblNetwork.setObjectName("lblNetwork")
        self.horizontalLayout_8.addWidget(self.lblNetwork)
        self.txtNetwork1 = QtWidgets.QLineEdit(parent=Dialog)
        self.txtNetwork1.setMaximumSize(QtCore.QSize(44, 16777215))
        self.txtNetwork1.setInputMask("")
        self.txtNetwork1.setText("")
        self.txtNetwork1.setMaxLength(3)
        self.txtNetwork1.setFrame(True)
        self.txtNetwork1.setObjectName("txtNetwork1")
        self.horizontalLayout_8.addWidget(self.txtNetwork1)
        self.dot = QtWidgets.QLabel(parent=Dialog)
        self.dot.setObjectName("dot")
        self.horizontalLayout_8.addWidget(self.dot)
        self.txtNetwork2 = QtWidgets.QLineEdit(parent=Dialog)
        self.txtNetwork2.setMaximumSize(QtCore.QSize(44, 16777215))
        self.txtNetwork2.setText("")
        self.txtNetwork2.setMaxLength(3)
        self.txtNetwork2.setFrame(True)
        self.txtNetwork2.setObjectName("txtNetwork2")
        self.horizontalLayout_8.addWidget(self.txtNetwork2)
        self.dot2 = QtWidgets.QLabel(parent=Dialog)
        self.dot2.setObjectName("dot2")
        self.horizontalLayout_8.addWidget(self.dot2)
        self.txtNetwork3 = QtWidgets.QLineEdit(parent=Dialog)
        self.txtNetwork3.setMaximumSize(QtCore.QSize(44, 16777215))
        self.txtNetwork3.setText("")
        self.txtNetwork3.setMaxLength(3)
        self.txtNetwork3.setFrame(True)
        self.txtNetwork3.setObjectName("txtNetwork3")
        self.horizontalLayout_8.addWidget(self.txtNetwork3)
        self.btnSetModular = QtWidgets.QPushButton(parent=Dialog)
        self.btnSetModular.setMinimumSize(QtCore.QSize(82, 0))
        self.btnSetModular.setObjectName("btnSetModular")
        self.horizontalLayout_8.addWidget(self.btnSetModular)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Minimum)
        self.horizontalLayout_8.addItem(spacerItem)
        self.label = QtWidgets.QLabel(parent=Dialog)
        self.label.setObjectName("label")
        self.horizontalLayout_8.addWidget(self.label)
        self.spinPercent = QtWidgets.QSpinBox(parent=Dialog)
        self.spinPercent.setMinimumSize(QtCore.QSize(65, 0))
        self.spinPercent.setMaximumSize(QtCore.QSize(65, 16777215))
        self.spinPercent.setMinimum(1)
        self.spinPercent.setMaximum(100)
        self.spinPercent.setProperty("value", 30)
        self.spinPercent.setDisplayIntegerBase(10)
        self.spinPercent.setObjectName("spinPercent")
        self.spinPercent.setEnabled(True)
        self.horizontalLayout_8.addWidget(self.spinPercent)
        self.gridLayout.addLayout(self.horizontalLayout_8, 1, 0, 1, 1)
        self.lblHeading = QtWidgets.QLabel(parent=Dialog)
        self.lblHeading.setObjectName("lblHeading")
        self.gridLayout.addWidget(self.lblHeading, 0, 0, 1, 1)
        self.line = QtWidgets.QFrame(parent=Dialog)
        self.line.setFrameShape(QtWidgets.QFrame.Shape.HLine)
        self.line.setFrameShadow(QtWidgets.QFrame.Shadow.Sunken)
        self.line.setObjectName("line")
        self.gridLayout.addWidget(self.line, 3, 0, 1, 1)
        self.buttonBox = QtWidgets.QDialogButtonBox(parent=Dialog)
        self.buttonBox.setOrientation(QtCore.Qt.Orientation.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.StandardButton.Cancel|QtWidgets.QDialogButtonBox.StandardButton.Apply|QtWidgets.QDialogButtonBox.StandardButton.RestoreDefaults)
        self.buttonBox.setObjectName("buttonBox")
        self.gridLayout.addWidget(self.buttonBox, 10, 0, 1, 1)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.gridLayout.addLayout(self.horizontalLayout_2, 6, 0, 1, 1)
        self.horizontalLayout_9 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_9.setObjectName("horizontalLayout_9")
        self.lblHost = QtWidgets.QLabel(parent=Dialog)
        self.lblHost.setMinimumSize(QtCore.QSize(48, 0))
        self.lblHost.setWordWrap(False)
        self.lblHost.setObjectName("lblHost")
        self.horizontalLayout_9.addWidget(self.lblHost)
        self.txtHost = QtWidgets.QLineEdit(parent=Dialog)
        self.txtHost.setMinimumSize(QtCore.QSize(30, 0))
        self.txtHost.setMaximumSize(QtCore.QSize(30, 16777215))
        self.txtHost.setMaxLength(3)
        self.txtHost.setObjectName("txtHost")
        self.txtMachineName = QtWidgets.QLineEdit(parent=Dialog)
        self.txtMachineName.setMinimumSize(QtCore.QSize(60, 0))
        self.txtMachineName.setMaximumSize(QtCore.QSize(60, 16777215))
        self.txtMachineName.setMaxLength(10)
        self.txtMachineName.setObjectName("txtMachineName")
        self.horizontalLayout_9.addWidget(self.txtHost)
        self.horizontalLayout_9.addWidget(self.txtMachineName)
        self.btnPlus = QtWidgets.QPushButton(parent=Dialog)
        self.btnPlus.setMinimumSize(QtCore.QSize(38, 0))
        self.btnPlus.setMaximumSize(QtCore.QSize(38, 16777215))
        self.btnPlus.setObjectName("btnPlus")
        self.horizontalLayout_9.addWidget(self.btnPlus)
        self.btnMinus = QtWidgets.QPushButton(parent=Dialog)
        self.btnMinus.setMinimumSize(QtCore.QSize(38, 0))
        self.btnMinus.setMaximumSize(QtCore.QSize(38, 16777215))
        self.btnMinus.setObjectName("btnMinus")
        self.horizontalLayout_9.addWidget(self.btnMinus)
        spacerItem2 = QtWidgets.QSpacerItem(1, 20, QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Minimum)
        self.horizontalLayout_9.addItem(spacerItem2)
        self.label_2 = QtWidgets.QLabel(parent=Dialog)
        self.label_2.setObjectName("label_2")
        self.horizontalLayout_9.addWidget(self.label_2)
        self.spinInterval = QtWidgets.QDoubleSpinBox(parent=Dialog)
        self.spinInterval.setMinimumSize(QtCore.QSize(65, 0))
        self.spinInterval.setMaximumSize(QtCore.QSize(65, 16777215))
        self.spinInterval.setDecimals(0)
        self.spinInterval.setMinimum(5.0)
        self.spinInterval.setMaximum(3600.0)
        self.spinInterval.setProperty("value", 30)
        self.spinInterval.setObjectName("spinInterval")
        self.spinInterval.setEnabled(True)
        self.horizontalLayout_9.addWidget(self.spinInterval)
        self.gridLayout.addLayout(self.horizontalLayout_9, 2, 0, 1, 1)
        self.checkYellow = QtWidgets.QCheckBox(parent=Dialog)
        self.checkYellow.setText("Show Yellows Only")
        self.checkYellow.setObjectName("checkYellow")
        self.gridLayout.addWidget(self.checkYellow, 8, 0, 1, 1)
        self.listAddress = QtWidgets.QListWidget(parent=Dialog)
        self.listAddress.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.ExtendedSelection)
        self.listAddress.setObjectName("listAddress")
        self.gridLayout.addWidget(self.listAddress, 9, 0, 1, 1)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.gridLayout.addLayout(self.horizontalLayout, 5, 0, 1, 1)
        self.gridLayout_2.addLayout(self.gridLayout, 0, 0, 1, 1)
        txtboxes = [self.txtNetwork1, self.txtNetwork2, self.txtNetwork3, self.txtHost]
        int_validator = QtGui.QIntValidator(self)
        for w in txtboxes: w.setValidator(int_validator)

        self.retranslateUi(Dialog)
        
        self.listen(Dialog)
        
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Machine IP Configuration"))
        self.lblNetwork.setText(_translate("Dialog", "Network:"))
        self.txtNetwork1.setToolTip(_translate("Dialog", "<html><head/><body><p>The network address, i.e. <span style=\" font-weight:700;\">192.168.1.</span>HOST</p></body></html>"))
        self.txtNetwork1.setPlaceholderText(_translate("Dialog", "192"))
        self.dot.setText(_translate("Dialog", "."))
        self.txtNetwork2.setToolTip(_translate("Dialog", "<html><head/><body><p>The network address, i.e. <span style=\" font-weight:700;\">192.168.1.</span>HOST</p></body></html>"))
        self.txtNetwork2.setPlaceholderText(_translate("Dialog", "168"))
        self.dot2.setText(_translate("Dialog", "."))
        self.txtNetwork3.setToolTip(_translate("Dialog", "<html><head/><body><p>The network address, i.e. <span style=\" font-weight:700;\">192.168.1.</span>HOST</p></body></html>"))
        self.txtNetwork3.setPlaceholderText(_translate("Dialog", "1"))
        self.btnSetModular.setText(_translate("Dialog", "Set"))
        self.label.setText(_translate("Dialog", "Percentage: "))
        self.spinPercent.setToolTip(_translate("Dialog", "Value determines when color indicator activates"))
        self.spinPercent.setSuffix(_translate("Dialog", " %"))
        self.lblHeading.setText(_translate("Dialog", "Modular"))
        self.lblHost.setText(_translate("Dialog", "Host/Machine Name:"))
        self.txtHost.setToolTip(_translate("Dialog", "<html><head/><body><p>The host, i.e. NETWORK.<span style=\" font-weight:700;\">82</span></p></body></html>"))
        self.txtHost.setPlaceholderText(_translate("Dialog", "82"))
        self.txtMachineName.setPlaceholderText(_translate("Dialog", "MA-$"))
        self.btnPlus.setText(_translate("Dialog", "+"))
        self.btnMinus.setText(_translate("Dialog", "-"))
        self.label_2.setText(_translate("Dialog", "Fetch interval: "))
        self.spinInterval.setToolTip(_translate("Dialog", "Value determines time between data requests"))
        self.spinInterval.setSuffix(_translate("Dialog", " s"))
        self.listAddress.setSortingEnabled(True)

if __name__ == '__main__':
    import sys
    app = QtWidgets.QApplication(sys.argv)
    dialog = QtWidgets.QDialog()
    ui = Ui_Dialog()
    ui.setupUi(dialog)
    dialog.show()
    sys.exit(app.exec())
