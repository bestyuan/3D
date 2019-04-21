# -*- coding: utf-8 -*-

"""
Module implementing Action.
"""

from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QMainWindow, QApplication, QMessageBox
from Ui_3D import Ui_MainWindow
import sys

import requests
from bs4 import BeautifulSoup
import os
import copy
# from pandas import DataFrame,ExcelWriter
import pandas as pd
class Action(QMainWindow, Ui_MainWindow):
    """
    Class documentation goes here.
    """

    def __init__(self, parent=None):
        """
        Constructor

        @param parent reference to the parent widget
        @type QWidget
        """
        super(Action, self).__init__(parent)
        self.setupUi(self)

        self.prefix = "http://e.17500.cn/getData/3d.TXT"
        self.save_dir = 'data'
        self.data = []
        self.verse_data = []  ##将原始数据列表顺序取反
        self.twelve_data = []  # 前12期
        self.falg = "false"  # 判断能否找到目标数据
        self.createxel = 'false'
        self.refresh_data.clicked.connect(self.showMessage_refresh)
        self.pushButton_2.clicked.connect(self.showMessage_twelve)

    @pyqtSlot()
    def on_refresh_data_clicked(self):
        if not os.path.exists(self.save_dir):
            os.makedirs(self.save_dir)
        if len(self.data)==0:
            html = requests.get(self.prefix).text
            soup = BeautifulSoup(html, 'lxml')
            all_list = soup.text
            linelist = all_list.split(('\n'))
            for i in linelist:
                if len(i):  # 最后一个为空格；
                    self.data.append(i.split(' '))
            name =['开奖期号','开奖日期','开','奖','号','试','机','号','机','球','投注总额',
                   '单选注数','金额','组三注数','金额','组六注数','金额']
            origin_data = pd.DataFrame(data=self.data, columns=name)
            writer = pd.ExcelWriter(self.save_dir + "./origin_data.xlsx")
            origin_data.to_excel(writer, "sheet1",index=None)
            writer.save()


    @pyqtSlot()
    def on_pushButton_2_clicked(self):
        # 取反方便计算 这里需要注意取反了前面的原始数据也会取反。
        if len(self.twelve_data)==0:
            self.verse_data = copy.deepcopy(self.data)
            self.verse_data.reverse()
            for i in range(0, 100):
                line = []
                line.append(self.verse_data[i + 11][2] + self.verse_data[i + 11][3] + self.verse_data[i + 11][4])  ###前12期
                line.append(self.verse_data[i][2] + self.verse_data[i][3] + self.verse_data[i][4])  ##本期
                for j in range(i + 11, i + 20):
                    strlocal = []
                    strpre = []
                    line.append(j - i + 1)
                    strlocal.append(self.verse_data[i][2])
                    strlocal.append(self.verse_data[i][3])
                    strlocal.append(self.verse_data[i][4])
                    strpre.append(self.verse_data[j][2])
                    strpre.append(self.verse_data[j][3])
                    strpre.append(self.verse_data[j][4])
                    retA = [k for k in strlocal if k in strpre]
                    if len(retA) > 0:
                        line.append('yes')
                    else:
                        line.append('no')

                self.twelve_data.append(line)
            self.find_target_data(self.twelve_data)
            self.twelve_data.reverse()
            name = ['前12期', '本期', '前12期', '12yes/no', '前13期', '13yes/no', '前14期', '14yes/no',
                    '前15期', '15yes/no', '前16期', '16yes/no', '前17期', '17yes/no', '前18期', '18yes/no',
                    '前19期', '19yes/no', '前20期', '20yes/no']
            if self.flag == 'true':
                name.append('结果')
            twelve = pd.DataFrame(data=self.twelve_data, columns=name)
            writer = pd.ExcelWriter(self.save_dir + "./pre_twelve.xlsx")
            twelve.to_excel(writer, "sheet1",index=None)
            writer.save()
            self.createxel = 'true'
        pass

    def find_target_data(self, table):
        for k in range(1, 10):
            for i in range(0, len(table)):
                count = 0
                if table[i][2 * k + 1] == 'no':
                    for j in range(i + 1, len(table)):
                        if (table[j][2 * k + 1] == table[i][2 * k + 1]):
                            count += 1
                            if (count == 5):
                                table[i].append(table[i + k - 1][0])  ##将第一列(表示前多少期)的结果append
                                self.flag = 'true'
                        else:
                            count = 0
                            break

    def showMessage_refresh(self):
        if len(self.data) > 0:
            QMessageBox.about(self, '数据', "原始数据已更新")
			
    def showMessage_twelve(self):
        if self.createxel == 'true':
            QMessageBox.about(self, '数据', "已生成文件")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    action = Action()
    action.show()
    sys.exit(app.exec_())
