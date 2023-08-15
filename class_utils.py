from PyQt6 import QtWidgets, QtCore

class NumericTableWidgetItem(QtWidgets.QTableWidgetItem):
    def __lt__(self, other):
        if isinstance(other, QtWidgets.QTableWidgetItem):
            my_value_str = self.data(QtCore.Qt.ItemDataRole.EditRole)
            other_value_str = other.data(QtCore.Qt.ItemDataRole.EditRole)
            
            try:
                my_value = int(my_value_str)
                other_value = int(other_value_str)

                return my_value < other_value
            except ValueError:
                # Handle the case where the conversion to int fails
                pass

        return super(NumericTableWidgetItem, self).__lt__(other)