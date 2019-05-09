# -*- coding: utf-8 -*-

import sys
from PyQt4 import QtCore, QtGui
from SynAly import compile_main

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_dialog(QtGui.QMainWindow):
    def setupUi(self, dialog):
        dialog.setObjectName(_fromUtf8("dialog"))
        dialog.resize(1063, 552)
        self.textEdit_Mediate = QtGui.QTextEdit(dialog)
        self.textEdit_Mediate.setGeometry(QtCore.QRect(30, 290, 271, 231))
        self.textEdit_Mediate.setObjectName(_fromUtf8("textEdit_Mediate"))
        self.textEdit_Input = QtGui.QTextEdit(dialog)
        self.textEdit_Input.setGeometry(QtCore.QRect(30, 30, 271, 231))
        self.textEdit_Input.setObjectName(_fromUtf8("textEdit_Input"))
        self.textEdit_Aimcode = QtGui.QTextEdit(dialog)
        self.textEdit_Aimcode.setGeometry(QtCore.QRect(400, 290, 271, 231))
        self.textEdit_Aimcode.setObjectName(_fromUtf8("textEdit_Aimcode"))
        self.textEdit_Word = QtGui.QTextEdit(dialog)
        self.textEdit_Word.setGeometry(QtCore.QRect(400, 30, 271, 231))
        self.textEdit_Word.setObjectName(_fromUtf8("textEdit_word"))
        self.Button_Open = QtGui.QPushButton(dialog)
        self.Button_Open.setGeometry(QtCore.QRect(310, 70, 81, 31))
        self.Button_Open.setObjectName(_fromUtf8("Button_Open"))
        self.Button_Word = QtGui.QPushButton(dialog)
        self.Button_Word.setGeometry(QtCore.QRect(310, 160, 81, 31))
        self.Button_Word.setObjectName(_fromUtf8("Button_Word"))
        self.Button_Mediate = QtGui.QPushButton(dialog)
        self.Button_Mediate.setGeometry(QtCore.QRect(310, 340, 81, 31))
        self.Button_Mediate.setObjectName(_fromUtf8("Button_Mediate"))
        self.Button_Aimcode = QtGui.QPushButton(dialog)
        self.Button_Aimcode.setGeometry(QtCore.QRect(310, 440, 81, 31))
        self.Button_Aimcode.setObjectName(_fromUtf8("Button_Aimcode"))
        self.textEdit_Syn = QtGui.QTextEdit(dialog)
        self.textEdit_Syn.setGeometry(QtCore.QRect(720, 30, 311, 491))
        self.textEdit_Syn.setObjectName(_fromUtf8("textEdit_Syn"))
        self.Button_Syn = QtGui.QPushButton(dialog)
        self.Button_Syn.setGeometry(QtCore.QRect(310, 250, 81, 31))
        self.Button_Syn.setObjectName(_fromUtf8("Button_Syn"))

        self.retranslateUi(dialog)
        QtCore.QObject.connect(self.Button_Word, QtCore.SIGNAL(_fromUtf8("clicked()")), self.show_word)
        QtCore.QObject.connect(self.Button_Syn, QtCore.SIGNAL(_fromUtf8("clicked()")), self.show_syn)
        QtCore.QObject.connect(self.Button_Mediate, QtCore.SIGNAL(_fromUtf8("clicked()")), self.show_mediate)
        QtCore.QObject.connect(self.Button_Aimcode, QtCore.SIGNAL(_fromUtf8("clicked()")), self.show_code)
        QtCore.QObject.connect(self.Button_Open, QtCore.SIGNAL(_fromUtf8("clicked()")), self.open_files)
        QtCore.QMetaObject.connectSlotsByName(dialog)

    def retranslateUi(self, dialog):
        dialog.setWindowTitle(_translate("dialog", "类C编译器", None))
        self.Button_Open.setText(_translate("dialog", "打开文件", None))
        self.Button_Word.setText(_translate("dialog", "词法分析", None))
        self.Button_Mediate.setText(_translate("dialog", "语义分析", None))
        self.Button_Aimcode.setText(_translate("dialog", "目标代码", None))
        self.Button_Syn.setText(_translate("dialog", "语法分析", None))

    def open_files(self):
        filename = QtGui.QFileDialog.getOpenFileName(self, 'Open file', '/')
        filename = unicode(filename)       # 打开文件
        fname = open(filename, 'r')        # 读入文件
        data = fname.read()  # 根据编码查看是否选择不同的解码方式
        ret[0] = compile_main(filename)
        self.textEdit_Input.setPlainText(data)
        self.textEdit_Input.show()
        fname.close()  # 关闭文件

    def show_word(self):
        if ret[0] is None:
            f = open(u'测试结果/词法分析.txt', 'r')
            data = f.read()
            f.close()
            self.textEdit_Word.clear()
            self.textEdit_Word.setPlainText(data)
            self.textEdit_Word.show()
        else:
            QtGui.QMessageBox.warning(self, self.trUtf8("警告!"), self.trUtf8(ret[0]))

    def show_syn(self):
        if ret[0] is None:
            f = open(u'测试结果/语法分析.txt', 'r')
            data = f.read()
            f.close()
            self.textEdit_Syn.clear()
            self.textEdit_Syn.setPlainText(data)
            self.textEdit_Syn.show()
        else:
            QtGui.QMessageBox.warning(self, self.trUtf8("警告!"), self.trUtf8(ret[0]))

    def show_mediate(self):
        if ret[0] is None:
            f = open(u'测试结果/中间代码.txt', 'r')
            data = f.read()
            f.close()
            self.textEdit_Mediate.clear()
            self.textEdit_Mediate.setPlainText(data)
            self.textEdit_Mediate.show()
        else:
            QtGui.QMessageBox.warning(self, self.trUtf8("警告!"), self.trUtf8(ret[0]))

    def show_code(self):
        if ret[0] is None:
            f = open(u'测试结果/目标代码.txt', 'r')
            data = f.read()
            f.close()
            self.textEdit_Aimcode.clear()
            self.textEdit_Aimcode.setPlainText(data)
            self.textEdit_Aimcode.show()
        else:
            QtGui.QMessageBox.warning(self, self.trUtf8("警告!"), self.trUtf8(ret[0]))


if __name__ == "__main__":
    ret = [None]
    app = QtGui.QApplication(sys.argv)
    MainWindow = QtGui.QMainWindow()
    ui = Ui_dialog()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())