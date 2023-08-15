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
        
        self.percentage = .3
        self.interval = 0
        self.data = {}
        
        self.normal = "background-color: rgb(255,255,255)"
        self.error = "background-color: rgb(255,185,185)"
        
        self.var_info = ""
        
        self.message = QtWidgets.QMessageBox()
    
    def listen(self, Dialog):
        self.txtHost.setEnabled(False)
        self.load_settings()
        self.interval = int(self.spinInterval.value())
        self.percentage = self.spinPercent.value()
        # Events
        self.spinInterval.valueChanged.connect(lambda value: self.set_interval(value))
        self.spinPercent.valueChanged.connect(lambda value: self.set_percentage(value))
        
        self.btnSetModular.clicked.connect(lambda: self.enable_network_input())

        self.btnPlus.clicked.connect(lambda: self.update_list(self.btnPlus.text()))
        self.btnMinus.clicked.connect(lambda: self.update_list(self.btnMinus.text()))
        self.btnAddFull.clicked.connect(lambda: self.update_list(self.btnAddFull.text()))
        
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
        self.spinPercent.setValue(30)
        self.spinInterval.setValue(30)
        self.txtFullAddress.clear()
        self.listAddress.clear()
        self.ip_list.clear()
    
    def set_interval(self, value):
        self.interval = int(value)
        self.update_display()
    def set_percentage(self, value):
        self.percentage = value
        self.update_display()
        
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
        self.full_address = self.network + self.host
        full_addresses = self.txtFullAddress.text()
        if mode == "+":
            if self.network != "" and self.host != "":
                self.listAddress.addItem(self.full_address)
                self.ip_list.append(self.full_address)
                self.txtHost.clear()
                self.txtHost.setStyleSheet(self.normal)
                self.print_list()
                print(f"ADDRESS WAS ADDED: {self.network + self.host}")
                self.full_address = ""
                self.host = ""
            else: self.txtHost.setStyleSheet(self.error)
        if mode == "Add":
            list_from_text = self.get_list_from_text(self.txtFullAddress.text())
            if self.txtFullAddress.text() != "" and self.check_full_address(full_addresses):
                self.listAddress.addItems(list_from_text)
                self.ip_list.extend(list_from_text)  # Use 'extend' to append individual elements
                self.txtFullAddress.clear()
                self.txtFullAddress.setStyleSheet(self.normal)
                self.print_list()
                print(f"ADDRESSES WERE ADDED: {full_addresses}")
            else: 
                self.txtFullAddress.setStyleSheet(self.error)

        if mode == "-":
            self.txtFullAddress.setStyleSheet(self.normal)
            self.remove_sel()
            self.print_list()
            print(f"ITEM REMOVED")
            
    def check_full_address(self, address_input):
        # Split the input by commas and remove any leading/trailing whitespace
        addresses = [address.strip() for address in address_input.split(',')]
        
        # Use a regular expression to check each address separately
        for address in addresses:
            if not re.match(r'^(\d{1,3}\.){3}\d{1,3}$', address):
                return False
        
        return True
    
    def print_list(self):
        print("\nDATA:\n")
        for item in self.ip_list:
            print(f"{item}\n")
            
    def get_list_from_text(self, full_addresses: str):
        # Split the input string by comma and strip any whitespace around each IP address
        addresses = [address.strip() for address in full_addresses.split(',')]
        self.txtFullAddress.setStyleSheet(self.normal)

        # If there is only one IP address, return it as a list with a single item
        if len(addresses) == 1:
            self.txtFullAddress.setStyleSheet(self.normal)
            return addresses

        return addresses

    def remove_sel(self):
        # Retrieve the selected items from the QListWidget
        listItems = self.listAddress.selectedItems()
        
        # If no items are selected, return without doing anything
        if not listItems:
            return
        
        # Iterate through each selected item and remove it from the QListWidget
        for item in listItems:
            # Get the text of the selected item
            item_text = item.text()
            
            # Find the index of the item in the Python list and remove it
            if item_text in self.ip_list:
                self.ip_list.remove(item_text)
            
            # Remove the item from the QListWidget
            self.listAddress.takeItem(self.listAddress.row(item))
            del item
        
    def enable_network_input(self):
        input_value = [self.txtNetwork1.text(), self.txtNetwork2.text(), self.txtNetwork3.text()]
        input_obj = [self.txtNetwork1, self.txtNetwork2, self.txtNetwork3]
        # If any of fields are empty
        if "" in input_value:
            for obj in input_obj:
                obj.setStyleSheet(self.error)
            if self.txtNetwork1.isEnabled() == True : self.txtHost.setEnabled(False)
            self.network = ""
            print(f"NETWORK ADDRESS WAS RESET: {self.network}")
        elif all(input != "" for input in input_value):
            if self.btnSetModular.text() == "Change":
                for obj in input_obj:
                    obj.setStyleSheet(self.normal)
                    obj.setEnabled(True)
                    obj.setText("")
                self.txtHost.setEnabled(False)
                self.btnSetModular.setText("Set")
                self.network = ""
            else:
                for obj in input_obj:
                    obj.setStyleSheet(self.normal)
                    obj.setEnabled(False)
                self.network = self.txtNetwork1.text() + "." + self.txtNetwork2.text() + "." + self.txtNetwork3.text() + "."
                self.txtHost.setEnabled(True)
                self.btnSetModular.setText("Change")
                print(f"NETWORK ADDRESS WAS SET: {self.network}")
    
    def save_settings(self):
        self.data = {
            "network": self.network,
            "ip_list": self.ip_list,
            "percentage": self.percentage,
            "interval": self.interval
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
            self.ip_list = self.data.get("ip_list", self.ip_list)
            for item in self.ip_list:
                self.listAddress.addItem(item)
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
            if self.percentage != "":
                self.spinInterval.setValue(self.interval)
            current_settings = f"Network:{self.network}\nIP List: {self.ip_list}\nPercentage: {self.percentage}\nInterval: {self.interval}\nData: {self.data}"
            
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
        self.gridLayout.addWidget(self.buttonBox, 9, 0, 1, 1)
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
        self.txtHost.setMinimumSize(QtCore.QSize(162, 0))
        self.txtHost.setMaximumSize(QtCore.QSize(162, 16777215))
        self.txtHost.setMaxLength(3)
        self.txtHost.setObjectName("txtHost")
        self.horizontalLayout_9.addWidget(self.txtHost)
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
        self.lblHeading2 = QtWidgets.QLabel(parent=Dialog)
        self.lblHeading2.setObjectName("lblHeading2")
        self.gridLayout.addWidget(self.lblHeading2, 4, 0, 1, 1)
        self.listAddress = QtWidgets.QListWidget(parent=Dialog)
        self.listAddress.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.ExtendedSelection)
        self.listAddress.setObjectName("listAddress")
        self.gridLayout.addWidget(self.listAddress, 8, 0, 1, 1)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.lblFullAddress = QtWidgets.QLabel(parent=Dialog)
        self.lblFullAddress.setObjectName("lblFullAddress")
        self.lblFullAddress.setMinimumSize(60, 0)
        self.horizontalLayout.addWidget(self.lblFullAddress)
        self.txtFullAddress = QtWidgets.QLineEdit(parent=Dialog)
        self.txtFullAddress.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.txtFullAddress.setObjectName("txtFullAddress")
        self.horizontalLayout.addWidget(self.txtFullAddress)
        self.btnAddFull = QtWidgets.QPushButton(parent=Dialog)
        self.btnAddFull.setMinimumSize(QtCore.QSize(82, 0))
        self.btnAddFull.setObjectName("btnAddFull")
        self.horizontalLayout.addWidget(self.btnAddFull)
        self.gridLayout.addLayout(self.horizontalLayout, 5, 0, 1, 1)
        self.line_2 = QtWidgets.QFrame(parent=Dialog)
        self.line_2.setFrameShape(QtWidgets.QFrame.Shape.HLine)
        self.line_2.setFrameShadow(QtWidgets.QFrame.Shadow.Sunken)
        self.line_2.setObjectName("line_2")
        self.gridLayout.addWidget(self.line_2, 7, 0, 1, 1)
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
        self.lblHost.setText(_translate("Dialog", "Host:"))
        self.txtHost.setToolTip(_translate("Dialog", "<html><head/><body><p>The host, i.e. NETWORK.<span style=\" font-weight:700;\">82</span></p></body></html>"))
        self.txtHost.setPlaceholderText(_translate("Dialog", "82"))
        self.btnPlus.setText(_translate("Dialog", "+"))
        self.btnMinus.setText(_translate("Dialog", "-"))
        self.label_2.setText(_translate("Dialog", "Fetch interval: "))
        self.spinInterval.setToolTip(_translate("Dialog", "Value determines time between data requests"))
        self.spinInterval.setSuffix(_translate("Dialog", " s"))
        self.lblHeading2.setText(_translate("Dialog", "Full Address (separate multiple entries with comma i.e. ip1, ip2, ... ip10)"))
        self.listAddress.setSortingEnabled(True)
        self.lblFullAddress.setText(_translate("Dialog", "IP Address: "))
        self.txtFullAddress.setToolTip(_translate("Dialog", "<html><head/><body><p>Enter the full machine address, i.e. <span style=\" font-weight:700;\">192.168.1.82</span></p><p>For multiple addresses, separate by comma.</p></body></html>"))
        self.txtFullAddress.setPlaceholderText(_translate("Dialog", "192.168.1.82 OR 192.168.1.82, address_2, ... address_nth"))
        self.btnAddFull.setText(_translate("Dialog", "Add"))

if __name__ == '__main__':
    import sys
    app = QtWidgets.QApplication(sys.argv)
    dialog = QtWidgets.QDialog()
    ui = Ui_Dialog()
    ui.setupUi(dialog)
    dialog.show()
    sys.exit(app.exec())
