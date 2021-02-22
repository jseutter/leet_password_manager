#!/usr/bin/env python3

import sys
from main import Secrets
from PyQt5.QtWidgets import (QMainWindow, QApplication, QWidget, QAction, QTableWidget,QTableWidgetItem,QVBoxLayout,
    QShortcut, QMessageBox, QTableView)
from PyQt5.QtGui import QIcon, QKeySequence, QStandardItemModel, QStandardItem
from PyQt5.QtCore import pyqtSlot, QAbstractTableModel, Qt, QVariant

class App(QWidget):

    def __init__(self):
        super().__init__()
        self.title = 'Leet Password Manager'
        self.left = 0
        self.top = 0
        self.width = 300
        self.height = 200
        self.cols = ['id', 'title', 'username', 'password']
        self.init_ui()
        self.secrets = Secrets('vault.yml', 'password')
        self.secrets.read()
        #self.populate_table(self.secrets)
        
    def init_ui(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)
        
        self.create_table()

        # Add box layout, add table to box layout and add box layout to widget
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.tableWidget) 
        self.setLayout(self.layout) 

        self.pwdSc = QShortcut(QKeySequence('Ctrl+C'), self)
#        self.pwdSc.activated.connect(lambda : QMessageBox.information(self,
#            'Message', 'Ctrl + C initiated'))
        self.pwdSc.activated.connect(lambda: self.copy_password())

        self.userSc = QShortcut(QKeySequence('Ctrl+B'), self)
        self.userSc.activated.connect(lambda: self.copy_username())

        # Show widget
        self.show()
        #self.add_row_to_table()
        self.show()

    def create_table(self):
        # Create table
#        self.tableWidget = QTableWidget()
#        self.tableWidget.setRowCount(0)
#        self.tableWidget.setColumnCount(len(self.cols))
#        self.tableWidget.move(0,0)
        self.tableWidget = QTableView()
#        self.tableModel = TableModel([['0', 'hi', 'mom'], ['1', 'hello', 'dad']])
        self.tableModel = TableModel()
        self.tableModel.add_data([['0000', 'hi', 'mom'], ['1111', 'hello', 'dad']])
        self.tableModel.setHorizontalHeaderLabels(['id', 'username', 'password'])
        self.tableWidget.setModel(self.tableModel)
        self.tableWidget.hideColumn(0)

        # table selection change
        self.tableWidget.doubleClicked.connect(self.on_click)

    def add_row_to_table(self):
        last_row = self.tableWidget.rowCount()
        self.tableWidget.insertRow(last_row)
        self.tableWidget.setItem(last_row, 0, QTableWidgetItem("Hi mom"))

    def populate_table(self, secrets):
        row = self.tableWidget.rowCount()
        for entry in secrets.entries():
            self.tableWidget.insertRow(row)
            col_idx = 0
            for col in self.cols:
                self.tableWidget.setItem(row, col_idx, QTableWidgetItem(entry[col]))
                col_idx += 1

    @pyqtSlot()
    def on_click(self):
        print("\n")
        for currentQTableWidgetItem in self.tableWidget.selectedItems():
            print(currentQTableWidgetItem.row(), currentQTableWidgetItem.column(), currentQTableWidgetItem.text())

    def copy_password(self):
        # Copy the password to the paste buffer
        cb = QApplication.clipboard()
        cb.clear(mode=cb.Clipboard)

        item = self.currently_selected()
        print(item)
        cb.setText("Clipboard text", mode=cb.Clipboard)

    def copy_username(self):
        cb = QApplication.clipboard()
        cb.clear(mode=cb.Clipboard)

        item = self.currently_selected()
        print(item)
        cb.setText("Clipboard text", mode=cb.Clipboard)

    def currently_selected(self):
        # Returns the currently selected row id.
        indices = self.tableWidget.selectedIndexes()
        row_num = indices[0].row()
        row_id = self.tableModel.data(indices[0], Qt.UserRole)
        return row_id


#class TableModel(QAbstractTableModel):
#    def __init__(self, data):
#        super(TableModel, self).__init__()
#        self.data = data
#
#    def data(self, index, role):
#        if role == Qt.DisplayRole:
#            return self.data[index.row()][index.column()]
#
#    def rowCount(self, index):
#        return len(self.data)
#
#    def columnCount(self, index):
#        return len(self.data[0])
class TableModel(QStandardItemModel):
    def add_data(self, data):
        for row_num in range(0, len(data)):
            for col_num in range(0, len(data[0])):
                item = QStandardItem(data[row_num][col_num])
                item.setData(QVariant(data[row_num][0]), Qt.UserRole)
                self.setItem(row_num, col_num, item)

 
if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()
    sys.exit(app.exec_())  

