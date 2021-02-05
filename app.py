#!/usr/bin/env python3

import sys
from main import Secrets
from PyQt5.QtWidgets import QMainWindow, QApplication, QWidget, QAction, QTableWidget,QTableWidgetItem,QVBoxLayout
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import pyqtSlot

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
        self.populate_table(self.secrets)
        
    def init_ui(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)
        
        self.create_table()

        # Add box layout, add table to box layout and add box layout to widget
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.tableWidget) 
        self.setLayout(self.layout) 

        # Show widget
        self.show()
        self.add_row_to_table()
        self.show()

    def create_table(self):
        # Create table
        self.tableWidget = QTableWidget()
        self.tableWidget.setRowCount(0)
        self.tableWidget.setColumnCount(len(self.cols))
        self.tableWidget.move(0,0)

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

 
if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()
    sys.exit(app.exec_())  

