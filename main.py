#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
TSV to CSV converter

A programm to quickly change correct tsv files into csv file
with semicolon as a seperator

author: Joshua Menke
last edited: November 2016
"""

import sys
import logging
import csv
import os

from PyQt5 import QtWidgets


sniffer = csv.Sniffer()
logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)


class DataTable(QtWidgets.QTableWidget):

    def __init__(self, parent):
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.parent = parent

    def dragEnterEvent(self, e):
        if e.mimeData().hasUrls:
            logging.debug('Is file')
            e.accept()
        else:
            logging.warning('Is not a file: %s' % e.mimeData().formats())
            self.parent.statusBar().showMessage('This is not a file: %s' % e.mimeData().formats(), 15000)
            e.ignore()

    def dropEvent(self, e):
        p = e.mimeData().urls()
        if e.mimeData().hasUrls and os.path.splitext(e.mimeData().urls()[0].toLocalFile())[1] in [".csv", ".tsv"]:
            try:
                urlT = e.mimeData().urls()
                logging.debug("Dropped File: %s", urlT)
                with open(urlT[0].toLocalFile()) as fname:
                    delimiterT = sniffer.sniff(fname.read())
                    fname.seek(0)
                    logging.debug("Scheme: %s", urlT[0].scheme())
                    logging.debug("Delimiter: %s", delimiterT.delimiter)
                    dataList = list(csv.reader(fname, delimiter=delimiterT.delimiter))
                    self.setTableData(dataList)
                    self.parent.setWindowTitle("TSV to CSV Converter - %s" % urlT[0].toLocalFile())
                    self.parent.fileURL = urlT[0].toLocalFile()
            except UnicodeDecodeError as e:
                logging.error("Couldn't read file: %s", e)
                self.parent.statusBar().showMessage("Die Datei konnte nicht geöffnet werden: %s" % e, 15000)
            except csv.Error as e:
                logging.error("Not an csv: %s", e)
                self.parent.statusBar().showMessage("Die Datei ist keine valide CSV/TSV Datei: %s" % e, 15000)

    def dragMoveEvent(self, event):
        if event.mimeData().hasUrls:
            event.accept()
        else:
            event.ignore()

    def setTableData(self, dataList):
        self.setRowCount(len(dataList))
        self.setColumnCount(len(dataList[0]))
        for x, row in enumerate(dataList):
            for y, text in enumerate(row):
                self.setItem(x, y, QtWidgets.QTableWidgetItem(text))


class Example(QtWidgets.QMainWindow):

    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):

        self.dataTable = DataTable(self)
        self.setCentralWidget(self.dataTable)
        self.statusBar()
        self.fileURL = ""

        openFile = QtWidgets.QAction('&Open File', self)
        openFile.setShortcut('Ctrl+O')
        openFile.setStatusTip('Open new File')
        openFile.triggered.connect(self.showDialog)

        saveFile = QtWidgets.QAction("&Save File", self)
        saveFile.setShortcut("Ctrl+S")
        saveFile.setStatusTip('Save File')
        saveFile.triggered.connect(self.fileSave)

        menubar = self.menuBar()
        fileMenu = menubar.addMenu('&File')
        fileMenu.addAction(openFile)
        fileMenu.addAction(saveFile)

        self.setGeometry(300, 300, 1000, 500)
        self.setWindowTitle('TSV to CSV Converter')
        self.show()

    def fileSave(self):
        name = QtWidgets.QFileDialog.getSaveFileName(self, "Datei als CSV mit Semikolon speichern",
                                                     self.fileURL, 'CSV Files (*.csv)')
        if name[0]:
            try:
                with open(name[0],"w") as w_csv_file:
                    csv_writer = csv.writer(w_csv_file,delimiter=";", lineterminator='\n')
                    iColumns = self.dataTable.columnCount()
                    iRows = self.dataTable.rowCount()
                    tableData = [[self.dataTable.item(row, column).text() for column in range(iColumns)] for row in
                                 range(iRows)]
                    logging.debug("Tabledata: %s", tableData)
                    csv_writer.writerows(tableData)
            except Exception as e:
                logging.error("Datei konnte nicht gespeichert werden: %s", e)
                self.statusBar().showMessage("Datei konnte nicht gespeichert werden: %s"% e, 15000)

    def showDialog(self):

        fname = QtWidgets.QFileDialog.getOpenFileName(self, 'Datei öffnen', '/home', 'TSV and CSV Files (*.tsv *.csv)')
        if fname[0]:
            with open(fname[0], 'r') as f:
                # delimiterT = "\t" if fname[1] == "TSV File (*.tsv)" else ","
                delimiterT = sniffer.sniff(f.read())
                f.seek(0)
                logging.debug(delimiterT.delimiter)
                reader = csv.reader(f,delimiter=delimiterT.delimiter)
                listData = list(reader)
                logging.debug(listData)
                self.dataTable.setTableData(listData)
                self.setWindowTitle("TSV to CSV Converter - %s" % fname[0])
                self.fileURL = fname[0]


if __name__ == '__main__':

    app = QtWidgets.QApplication(sys.argv)
    ex = Example()
    sys.exit(app.exec_())