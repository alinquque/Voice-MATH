import json

import matplotlib.ticker
import pyaudio

import sympy
from vosk import Model, KaldiRecognizer

from PyQt6 import QtWidgets, QtCore, QtSvgWidgets, QtGui
from PyQt6.QtWidgets import QApplication, QMainWindow, QHBoxLayout, QFrame, QPushButton, \
    QGraphicsOpacityEffect, QVBoxLayout
from PyQt6.QtCore import Qt, QPoint, QEasingCurve, QParallelAnimationGroup, QPropertyAnimation, pyqtProperty
from PyQt6.QtGui import QFont, QIcon, QColor

import numpy as np
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

from matplotlib.figure import Figure

import latex2sympy2

from sympy.solvers import solve
from sympy import Symbol
from sympy import latex, lambdify

import sys
import pymorphy2

morph = pymorphy2.MorphAnalyzer()

MEDIUM_SIZE = 20
matplotlib.rc('axes', labelsize=MEDIUM_SIZE)

# подключение модели
model = Model('new_small_model')
rec = KaldiRecognizer(model, 16000)
p = pyaudio.PyAudio()
stream = p.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=8000)
stream.start_stream()

# выводимый на экран текст
res = ''
# выдвинута ли шторка меню
is_swiped = False
# произошел ли выход из приветсвенного окна
greeted = False
# включен ли режим подсказок
hints = True
# статус записи
rec_cond = 'stop'
# предыдущий статус записи
old_rec_cond = ''

old_text = ''

equation = ''
solvation = None

help_window_is_opened = False

b = 0
e = ''

symb = 'x'

delta = 0.1

k = 0

# тип вводимой задачи
b_type = 1  # 0 - вычисление, 1 - уравнение, 2 - дифференцирование
old_b_type = 1

# массив слов
mas = []

# массив для строки latex
lat_mas = []
lat_str = ''

word_transform = {
    'ноль': '0',
    'нуль': '0',
    'один': '1',
    'два': '2',
    'три': '3',
    'четыре': '4',
    'пять': '5',
    'шесть': '6',
    'семь': '7',
    'восемь': '8',
    'девять': '9',
    'десять': '10',
    'одиннадцать': '11',
    'двенадцать': '12',
    'тринадцать': '13',
    'четырнадцать': '14',
    'пятнадцать': '15',
    'шестнадцать': '16',
    'семнадцать': '17',
    'восемнадцать': '18',
    'девятнадцать': '19',
    'двадцать': '20',
    'тридцать': '30',
    'сорок': '40',
    'пятьдесят': '50',
    'шестьдесят': '60',
    'семьдесят': '70',
    'восемьдесят': '80',
    'девяносто': '90',
    'сто': '100',
    'двести': '200',
    'триста': '300',
    'четыреста': '400',
    'пятьсот': '500',
    'шестьсот': '600',
    'семьсот': '700',
    'восемьсот': '800',
    'девятьсот': '900',
    'тысяча': '1000',
    'миллион': '1000000',
    'миллиард': '1000000000',
    'x': 'x',
    'х': 'x',
    'икс': 'x',
    'y': 'y',
    'у': 'y',
    'игрек': 'y',
    'нет': 'z',
    'вэд': 'z',
    'вед': 'z',
    'вет': 'z',
    'зет': 'z',
    'зэт': 'z',
    'зэд': 'z',
    'зед': 'z',
    'z': 'z',
    'т': 't',
    'тэ': 't',
    'те': 't',
    't': 't',
    'дробь': '\\frac',
    'числитель': '{',
    'знаменатель': '{',
    'далее': '}',
    'плюс': '+',
    'минус': '-',
    'минут': '-',
    'умножить': '',
    'на': '*',
    'синус': '\\sin{',
    'косинус': '\\cos{',
    'тангенс': '\\tan{',
    'котангенс': '\\cot{',
    'арксинус': '\\arcsin{',
    'арккосинус': '\\arccos{',
    'арктангенс': '\\arctan{',
    'пи': '\\pi',
    'корень': '\\sqrt',
    'квадратный': '[2]',
    'степени': '^{',
    'степень': '^{',
    'из': '{',
    'равно': '=',
    'равняется': '=',
    'равняться': '=',
    'в': '',
    'квадрате': '^{2}',
    'квадрат': '^{2}',
    'открываться': '\\left(',
    'открывается': '\\left(',
    'открываются': '\\left(',
    'закрываться': '\\right)',
    'закрываются': '\\right)',
    'закрывается': '\\right)',
}

scrollstyle = ('''
            /* VERTICAL SCROLLBAR */
            QScrollBar:vertical {
                border: none;
                width: 14px;
                margin: 15px 0 15px 0;
                border-radius: 0px;
            }
            /*  HANDLE BAR VERTICAL */
            QScrollBar::handle:vertical {
                background-color: rgb(182, 107, 196);
                min-height: 30px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: rgb(98, 126, 154);
            }
            QScrollBar::handle:vertical:pressed {
                background-color: rgb(98, 126, 154);
            }
            /* BTN TOP - SCROLLBAR */
            QScrollBar::sub-line:vertical {
                border: none;
                background-color: rgb(182, 107, 196);
                height: 15px;
                border-top-left-radius: 7px;
                border-top-right-radius: 7px;
                subcontrol-position: top;
                subcontrol-origin: margin;
            }
            QScrollBar::sub-line:vertical:hover {
                background-color: rgb(98, 126, 154);
            }
            QScrollBar::sub-line:vertical:pressed {
                background-color: rgb(98, 126, 154);
            }

            /* BTN BOTTOM - SCROLLBAR */
            QScrollBar::add-line:vertical {
                border: none;
                background-color: rgb(182, 107, 196);
                height: 15px;
                border-bottom-left-radius: 7px;
                border-bottom-right-radius: 7px;
                subcontrol-position: bottom;
                subcontrol-origin: margin;
            }
            QScrollBar::add-line:vertical:hover {
                background-color: rgb(98, 126, 154);
            }
            QScrollBar::add-line:vertical:pressed { 
                background-color: rgb(98, 126, 154);
            }

            QScrollBar::up-arrow:horizontal, QScrollBar::down-arrow:horizontal {
                background: none;
            }
            QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {
                background: none;
            }

            /* RESET ARROW */
            QScrollBar::up-arrow:vertical, QScrollBar::down-arrow:vertical {
                background: none;
            }
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
                background: none;
            }''')


# преобразование прописных числительных в символьные
def num_true_form(word):
    word1 = word
    pp = morph.parse(word1)[0]
    pp1 = pp.normal_form
    if pp1 in word_transform:
        trans_word = word_transform.get(pp1)
        if trans_word.isdigit():
            word1 = pp1
    return word1


def word2latex(word):
    res = ''
    try:
        if word in word_transform:
            res = word_transform.get(word)
        else:
            res = ''
    except KeyError as e:
        # можно также присвоить значение по умолчанию вместо бросания исключения
        res = ''

    return res

buttonShift = None;

class Button(QPushButton):
    def __init__(self, *args, **kwargs):
        super(Button, self).__init__(*args, **kwargs)
        global buttonShift
        buttonShift = QPropertyAnimation(self, b'pos')

    def enterEvent(self, event):
        super(Button, self).enterEvent(event)
        pos = self.pos()
        if pos.y() == 20:
            buttonShift.setStartValue(pos)
            buttonShift.setEndValue(QPoint(pos.x(), pos.y() + 10))
            buttonShift.setEasingCurve(QEasingCurve.Type.InOutCubic)
            buttonShift.setDuration(200)
            buttonShift.start()

    def leaveEvent(self, event):
        super(Button, self).leaveEvent(event)
        pos = self.pos()
        if pos.y() == 30:
            buttonShift.setStartValue(pos)
            buttonShift.setEndValue(QPoint(pos.x(), pos.y() - 10))
            buttonShift.setEasingCurve(QEasingCurve.Type.InOutCubic)
            buttonShift.setDuration(150)
            buttonShift.start()

scroll = None

# класс окна с подсказками
class HelpWindow(QtWidgets.QWidget):
    global rec_cond

    def __init__(self):
        super(HelpWindow, self).__init__()

        self.resize(450, 305)

        # скрытие titlebar
        self.setWindowFlag(QtCore.Qt.WindowType.FramelessWindowHint)

        self.center()

        self.setStyleSheet('background-color: rgb(70, 70, 70)')

        # положение поверх всех окон
        self.setWindowFlag(QtCore.Qt.WindowType.WindowStaysOnTopHint)

        # позиция курсора на окне приложения
        self.oldPos = None

        global old_text
        global scroll

        formLayout = QtWidgets.QFormLayout()
        groupBox = QtWidgets.QGroupBox()

        formLayout.setHorizontalSpacing(70)
        formLayout.setVerticalSpacing(10)

        label_0 = QtWidgets.QLabel('           ВИД')
        label_0.setStyleSheet('color: rgb(98, 126, 154); font-size: 20px')
        label_0.setFont(QFont('Impact'))
        label_01 = QtWidgets.QLabel('ЗАПИСЬ')
        label_01.setStyleSheet('color: rgb(98, 126, 154); font-size: 20px')
        label_01.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label_01.setFont(QFont('Impact'))
        formLayout.addRow(label_0, label_01)

        icon_1 = QPushButton('', self)
        icon_1.setStyleSheet('''
                                            QPushButton {border: none; background-color: rgb(70, 70, 70); border-radius: 15px}
                                            QPushButton:hover {border: none; background-color: rgb(182, 107, 196); border-radius: 15px}
                                            QPushButton:pressed {border: none; background-color: rgb(98, 126, 154); border-radius: 15px}
                                        ''')
        icon_1.setIcon(QIcon('icon_help/x.png'))
        icon_1.setFixedSize(120, 50)
        icon_1.setIconSize(QtCore.QSize(30, 30))
        icon_1.clicked.connect(self.icon_1_clicked)
        label_1 = QtWidgets.QLabel('икс')
        label_1.setStyleSheet('color: #ECF0F1; font-size: 17px')
        label_1.setFont(QFont('Impact'))
        formLayout.addRow(icon_1, label_1)

        icon_2 = QPushButton('', self)
        icon_2.setStyleSheet('''
                                                    QPushButton {border: none; background-color: rgb(70, 70, 70); border-radius: 15px}
                                                    QPushButton:hover {border: none; background-color: rgb(182, 107, 196); border-radius: 15px}
                                                    QPushButton:pressed {border: none; background-color: rgb(98, 126, 154); border-radius: 15px}
                                                ''')
        icon_2.setIcon(QIcon('icon_help/y.png'))
        icon_2.setFixedSize(120, 50)
        icon_2.setIconSize(QtCore.QSize(30, 30))
        icon_2.clicked.connect(self.icon_2_clicked)
        label_2 = QtWidgets.QLabel('игрек')
        label_2.setStyleSheet('color: #ECF0F1; font-size: 17px')
        label_2.setFont(QFont('Impact'))
        formLayout.addRow(icon_2, label_2)

        icon_3 = QPushButton('', self)
        icon_3.setStyleSheet('''
                                                    QPushButton {border: none; background-color: rgb(70, 70, 70); border-radius: 15px}
                                                    QPushButton:hover {border: none; background-color: rgb(182, 107, 196); border-radius: 15px}
                                                    QPushButton:pressed {border: none; background-color: rgb(98, 126, 154); border-radius: 15px}
                                                ''')
        icon_3.setIcon(QIcon('icon_help/z.png'))
        icon_3.setFixedSize(120, 50)
        icon_3.setIconSize(QtCore.QSize(30, 30))
        icon_3.clicked.connect(self.icon_3_clicked)
        label_3 = QtWidgets.QLabel('зэт')
        label_3.setStyleSheet('color: #ECF0F1; font-size: 17px')
        label_3.setFont(QFont('Impact'))
        formLayout.addRow(icon_3, label_3)

        icon_4 = QPushButton('', self)
        icon_4.setStyleSheet('''
                                                    QPushButton {border: none; background-color: rgb(70, 70, 70); border-radius: 15px}
                                                    QPushButton:hover {border: none; background-color: rgb(182, 107, 196); border-radius: 15px}
                                                    QPushButton:pressed {border: none; background-color: rgb(98, 126, 154); border-radius: 15px}
                                                ''')
        icon_4.setIcon(QIcon('icon_help/t.png'))
        icon_4.setFixedSize(120, 50)
        icon_4.setIconSize(QtCore.QSize(30, 30))
        icon_4.clicked.connect(self.icon_4_clicked)
        label_4 = QtWidgets.QLabel('тэ')
        label_4.setStyleSheet('color: #ECF0F1; font-size: 17px')
        label_4.setFont(QFont('Impact'))
        formLayout.addRow(icon_4, label_4)

        icon_5 = QPushButton('', self)
        icon_5.setStyleSheet('''
                                                    QPushButton {border: none; background-color: rgb(70, 70, 70); border-radius: 15px}
                                                    QPushButton:hover {border: none; background-color: rgb(182, 107, 196); border-radius: 15px}
                                                    QPushButton:pressed {border: none; background-color: rgb(98, 126, 154); border-radius: 15px}
                                                ''')
        icon_5.setIcon(QIcon('icon_help/plus.png'))
        icon_5.setFixedSize(120, 50)
        icon_5.setIconSize(QtCore.QSize(40, 40))
        icon_5.clicked.connect(self.icon_5_clicked)
        label_5 = QtWidgets.QLabel('плюс')
        label_5.setStyleSheet('color: #ECF0F1; font-size: 17px')
        label_5.setFont(QFont('Impact'))
        formLayout.addRow(icon_5, label_5)

        icon_6 = QPushButton('', self)
        icon_6.setStyleSheet('''
                                                    QPushButton {border: none; background-color: rgb(70, 70, 70); border-radius: 15px}
                                                    QPushButton:hover {border: none; background-color: rgb(182, 107, 196); border-radius: 15px}
                                                    QPushButton:pressed {border: none; background-color: rgb(98, 126, 154); border-radius: 15px}
                                                ''')
        icon_6.setIcon(QIcon('icon_help/minus.png'))
        icon_6.setFixedSize(120, 50)
        icon_6.setIconSize(QtCore.QSize(40, 40))
        icon_6.clicked.connect(self.icon_6_clicked)
        label_6 = QtWidgets.QLabel('минус')
        label_6.setStyleSheet('color: #ECF0F1; font-size: 17px')
        label_6.setFont(QFont('Impact'))
        formLayout.addRow(icon_6, label_6)

        icon_7 = QPushButton('', self)
        icon_7.setStyleSheet('''
                                                    QPushButton {border: none; background-color: rgb(70, 70, 70); border-radius: 15px}
                                                    QPushButton:hover {border: none; background-color: rgb(182, 107, 196); border-radius: 15px}
                                                    QPushButton:pressed {border: none; background-color: rgb(98, 126, 154); border-radius: 15px}
                                                ''')
        icon_7.setIcon(QIcon('icon_help/mult.png'))
        icon_7.setFixedSize(120, 50)
        icon_7.setIconSize(QtCore.QSize(40, 40))
        icon_7.clicked.connect(self.icon_7_clicked)
        label_7 = QtWidgets.QLabel('умножить на')
        label_7.setStyleSheet('color: #ECF0F1; font-size: 17px')
        label_7.setFont(QFont('Impact'))
        formLayout.addRow(icon_7, label_7)

        icon_8 = QPushButton('', self)
        icon_8.setStyleSheet('''
                                                    QPushButton {border: none; background-color: rgb(70, 70, 70); border-radius: 15px}
                                                    QPushButton:hover {border: none; background-color: rgb(182, 107, 196); border-radius: 15px}
                                                    QPushButton:pressed {border: none; background-color: rgb(98, 126, 154); border-radius: 15px}
                                                ''')
        icon_8.setIcon(QIcon('icon_help/frac.png'))
        icon_8.setFixedSize(120, 50)
        icon_8.setIconSize(QtCore.QSize(40, 40))
        icon_8.clicked.connect(self.icon_8_clicked)
        label_8 = QtWidgets.QLabel('дробь числитель a далее\nзнаменатель b далее')
        label_8.setStyleSheet('color: #ECF0F1; font-size: 17px')
        label_8.setFont(QFont('Impact'))
        formLayout.addRow(icon_8, label_8)

        icon_9 = QPushButton('', self)
        icon_9.setStyleSheet('''
                                                    QPushButton {border: none; background-color: rgb(70, 70, 70); border-radius: 15px}
                                                    QPushButton:hover {border: none; background-color: rgb(182, 107, 196); border-radius: 15px}
                                                    QPushButton:pressed {border: none; background-color: rgb(98, 126, 154); border-radius: 15px}
                                                ''')
        icon_9.setIcon(QIcon('icon_help/sin.png'))
        icon_9.setFixedSize(120, 50)
        icon_9.setIconSize(QtCore.QSize(50, 50))
        icon_9.clicked.connect(self.icon_9_clicked)
        label_9 = QtWidgets.QLabel('синус x далее')
        label_9.setStyleSheet('color: #ECF0F1; font-size: 17px')
        label_9.setFont(QFont('Impact'))
        formLayout.addRow(icon_9, label_9)

        icon_10 = QPushButton('', self)
        icon_10.setStyleSheet('''
                                                            QPushButton {border: none; background-color: rgb(70, 70, 70); border-radius: 15px}
                                                            QPushButton:hover {border: none; background-color: rgb(182, 107, 196); border-radius: 15px}
                                                            QPushButton:pressed {border: none; background-color: rgb(98, 126, 154); border-radius: 15px}
                                                        ''')
        icon_10.setIcon(QIcon('icon_help/cos.png'))
        icon_10.setFixedSize(120, 50)
        icon_10.setIconSize(QtCore.QSize(50, 50))
        icon_10.clicked.connect(self.icon_10_clicked)
        label_10 = QtWidgets.QLabel('косинус x далее')
        label_10.setStyleSheet('color: #ECF0F1; font-size: 17px')
        label_10.setFont(QFont('Impact'))
        formLayout.addRow(icon_10, label_10)

        icon_11 = QPushButton('', self)
        icon_11.setStyleSheet('''
                                                                    QPushButton {border: none; background-color: rgb(70, 70, 70); border-radius: 15px}
                                                                    QPushButton:hover {border: none; background-color: rgb(182, 107, 196); border-radius: 15px}
                                                                    QPushButton:pressed {border: none; background-color: rgb(98, 126, 154); border-radius: 15px}
                                                                ''')
        icon_11.setIcon(QIcon('icon_help/tan.png'))
        icon_11.setFixedSize(120, 50)
        icon_11.setIconSize(QtCore.QSize(50, 50))
        icon_11.clicked.connect(self.icon_11_clicked)
        label_11 = QtWidgets.QLabel('тангенс x далее')
        label_11.setStyleSheet('color: #ECF0F1; font-size: 17px')
        label_11.setFont(QFont('Impact'))
        formLayout.addRow(icon_11, label_11)

        icon_12 = QPushButton('', self)
        icon_12.setStyleSheet('''
                                                                    QPushButton {border: none; background-color: rgb(70, 70, 70); border-radius: 15px}
                                                                    QPushButton:hover {border: none; background-color: rgb(182, 107, 196); border-radius: 15px}
                                                                    QPushButton:pressed {border: none; background-color: rgb(98, 126, 154); border-radius: 15px}
                                                                ''')
        icon_12.setIcon(QIcon('icon_help/cotan.png'))
        icon_12.setFixedSize(120, 50)
        icon_12.setIconSize(QtCore.QSize(60, 60))
        icon_12.clicked.connect(self.icon_12_clicked)
        label_12 = QtWidgets.QLabel('котангенс x далее')
        label_12.setStyleSheet('color: #ECF0F1; font-size: 17px')
        label_12.setFont(QFont('Impact'))
        formLayout.addRow(icon_12, label_12)

        icon_13 = QPushButton('', self)
        icon_13.setStyleSheet('''
                                                                    QPushButton {border: none; background-color: rgb(70, 70, 70); border-radius: 15px}
                                                                    QPushButton:hover {border: none; background-color: rgb(182, 107, 196); border-radius: 15px}
                                                                    QPushButton:pressed {border: none; background-color: rgb(98, 126, 154); border-radius: 15px}
                                                                ''')
        icon_13.setIcon(QIcon('icon_help/arcsin.png'))
        icon_13.setFixedSize(120, 50)
        icon_13.setIconSize(QtCore.QSize(70, 70))
        icon_13.clicked.connect(self.icon_13_clicked)
        label_13 = QtWidgets.QLabel('арксинус x далее')
        label_13.setStyleSheet('color: #ECF0F1; font-size: 17px')
        label_13.setFont(QFont('Impact'))
        formLayout.addRow(icon_13, label_13)

        icon_14 = QPushButton('', self)
        icon_14.setStyleSheet('''
                                                                            QPushButton {border: none; background-color: rgb(70, 70, 70); border-radius: 15px}
                                                                            QPushButton:hover {border: none; background-color: rgb(182, 107, 196); border-radius: 15px}
                                                                            QPushButton:pressed {border: none; background-color: rgb(98, 126, 154); border-radius: 15px}
                                                                        ''')
        icon_14.setIcon(QIcon('icon_help/arccos.png'))
        icon_14.setFixedSize(120, 50)
        icon_14.setIconSize(QtCore.QSize(70, 70))
        icon_14.clicked.connect(self.icon_14_clicked)
        label_14 = QtWidgets.QLabel('арккосинус x далее')
        label_14.setStyleSheet('color: #ECF0F1; font-size: 17px')
        label_14.setFont(QFont('Impact'))
        formLayout.addRow(icon_14, label_14)

        icon_15 = QPushButton('', self)
        icon_15.setStyleSheet('''
                                                                            QPushButton {border: none; background-color: rgb(70, 70, 70); border-radius: 15px}
                                                                            QPushButton:hover {border: none; background-color: rgb(182, 107, 196); border-radius: 15px}
                                                                            QPushButton:pressed {border: none; background-color: rgb(98, 126, 154); border-radius: 15px}
                                                                        ''')
        icon_15.setIcon(QIcon('icon_help/arctan.png'))
        icon_15.setFixedSize(120, 50)
        icon_15.setIconSize(QtCore.QSize(70, 70))
        icon_15.clicked.connect(self.icon_15_clicked)
        label_15 = QtWidgets.QLabel('арктангенс x далее')
        label_15.setStyleSheet('color: #ECF0F1; font-size: 17px')
        label_15.setFont(QFont('Impact'))
        formLayout.addRow(icon_15, label_15)

        icon_17 = QPushButton('', self)
        icon_17.setStyleSheet('''
                                                                            QPushButton {border: none; background-color: rgb(70, 70, 70); border-radius: 15px}
                                                                            QPushButton:hover {border: none; background-color: rgb(182, 107, 196); border-radius: 15px}
                                                                            QPushButton:pressed {border: none; background-color: rgb(98, 126, 154); border-radius: 15px}
                                                                        ''')
        icon_17.setIcon(QIcon('icon_help/x_2.png'))
        icon_17.setFixedSize(120, 50)
        icon_17.setIconSize(QtCore.QSize(30, 30))
        icon_17.clicked.connect(self.icon_17_clicked)
        label_17 = QtWidgets.QLabel('x в квадрате')
        label_17.setStyleSheet('color: #ECF0F1; font-size: 17px')
        label_17.setFont(QFont('Impact'))
        formLayout.addRow(icon_17, label_17)

        icon_18 = QPushButton('', self)
        icon_18.setStyleSheet('''
                                                                            QPushButton {border: none; background-color: rgb(70, 70, 70); border-radius: 15px}
                                                                            QPushButton:hover {border: none; background-color: rgb(182, 107, 196); border-radius: 15px}
                                                                            QPushButton:pressed {border: none; background-color: rgb(98, 126, 154); border-radius: 15px}
                                                                        ''')
        icon_18.setIcon(QIcon('icon_help/x_a.png'))
        icon_18.setFixedSize(120, 50)
        icon_18.setIconSize(QtCore.QSize(30, 30))
        icon_18.clicked.connect(self.icon_18_clicked)
        label_18 = QtWidgets.QLabel('x в степени a далее')
        label_18.setStyleSheet('color: #ECF0F1; font-size: 17px')
        label_18.setFont(QFont('Impact'))
        formLayout.addRow(icon_18, label_18)

        icon_19 = QPushButton('', self)
        icon_19.setStyleSheet('''
                                                                            QPushButton {border: none; background-color: rgb(70, 70, 70); border-radius: 15px}
                                                                            QPushButton:hover {border: none; background-color: rgb(182, 107, 196); border-radius: 15px}
                                                                            QPushButton:pressed {border: none; background-color: rgb(98, 126, 154); border-radius: 15px}
                                                                        ''')
        icon_19.setIcon(QIcon('icon_help/sqrt.png'))
        icon_19.setFixedSize(120, 50)
        icon_19.setIconSize(QtCore.QSize(40, 40))
        icon_19.clicked.connect(self.icon_19_clicked)
        label_19 = QtWidgets.QLabel('корень квадратный\nиз x далее')
        label_19.setStyleSheet('color: #ECF0F1; font-size: 17px')
        label_19.setFont(QFont('Impact'))
        formLayout.addRow(icon_19, label_19)

        icon_20 = QPushButton('', self)
        icon_20.setStyleSheet('''
                                                                            QPushButton {border: none; background-color: rgb(70, 70, 70); border-radius: 15px}
                                                                            QPushButton:hover {border: none; background-color: rgb(182, 107, 196); border-radius: 15px}
                                                                            QPushButton:pressed {border: none; background-color: rgb(98, 126, 154); border-radius: 15px}
                                                                        ''')
        icon_20.setIcon(QIcon('icon_help/sqrt_a.png'))
        icon_20.setFixedSize(120, 50)
        icon_20.setIconSize(QtCore.QSize(40, 40))
        icon_20.clicked.connect(self.icon_20_clicked)
        label_20 = QtWidgets.QLabel('корень степени a\nдалее из x далее')
        label_20.setStyleSheet('color: #ECF0F1; font-size: 17px')
        label_20.setFont(QFont('Impact'))
        formLayout.addRow(icon_20, label_20)

        icon_21 = QPushButton('', self)
        icon_21.setStyleSheet('''
                                                                            QPushButton {border: none; background-color: rgb(70, 70, 70); border-radius: 15px}
                                                                            QPushButton:hover {border: none; background-color: rgb(182, 107, 196); border-radius: 15px}
                                                                            QPushButton:pressed {border: none; background-color: rgb(98, 126, 154); border-radius: 15px}
                                                                        ''')
        icon_21.setIcon(QIcon('icon_help/pi.png'))
        icon_21.setFixedSize(120, 50)
        icon_21.setIconSize(QtCore.QSize(30, 30))
        icon_21.clicked.connect(self.icon_21_clicked)
        label_21 = QtWidgets.QLabel('пи')
        label_21.setStyleSheet('color: #ECF0F1; font-size: 17px')
        label_21.setFont(QFont('Impact'))
        formLayout.addRow(icon_21, label_21)

        icon_22 = QPushButton('', self)
        icon_22.setStyleSheet('''
                                                                            QPushButton {border: none; background-color: rgb(70, 70, 70); border-radius: 15px}
                                                                            QPushButton:hover {border: none; background-color: rgb(182, 107, 196); border-radius: 15px}
                                                                            QPushButton:pressed {border: none; background-color: rgb(98, 126, 154); border-radius: 15px}
                                                                        ''')
        icon_22.setIcon(QIcon('icon_help/left.png'))
        icon_22.setFixedSize(120, 50)
        icon_22.setIconSize(QtCore.QSize(30, 30))
        icon_22.clicked.connect(self.icon_22_clicked)
        label_22 = QtWidgets.QLabel('скобка открывается')
        label_22.setStyleSheet('color: #ECF0F1; font-size: 17px')
        label_22.setFont(QFont('Impact'))
        formLayout.addRow(icon_22, label_22)

        icon_23 = QPushButton('', self)
        icon_23.setStyleSheet('''
                                                                            QPushButton {border: none; background-color: rgb(70, 70, 70); border-radius: 15px}
                                                                            QPushButton:hover {border: none; background-color: rgb(182, 107, 196); border-radius: 15px}
                                                                            QPushButton:pressed {border: none; background-color: rgb(98, 126, 154); border-radius: 15px}
                                                                        ''')
        icon_23.setIcon(QIcon('icon_help/right.png'))
        icon_23.setFixedSize(120, 50)
        icon_23.setIconSize(QtCore.QSize(30, 30))
        icon_23.clicked.connect(self.icon_23_clicked)
        label_23 = QtWidgets.QLabel('скобка закрывается')
        label_23.setStyleSheet('color: #ECF0F1; font-size: 17px')
        label_23.setFont(QFont('Impact'))
        formLayout.addRow(icon_23, label_23)

        groupBox.setLayout(formLayout)
        groupBox.setStyleSheet('border: none; background-color: rgb(50, 50, 50)')

        scroll = QtWidgets.QScrollArea()
        scroll.setWidget(groupBox)
        scroll.setWidgetResizable(True)

        scroll.verticalScrollBar().setSingleStep(240)

        layout = QVBoxLayout(self)
        layout.addWidget(scroll)

        scroll.setStyleSheet('''
            QScrollBar:vertical {
                border: none;
                background: rgb(90, 90, 90);
            }''')

        scroll.setFrameStyle(QtWidgets.QFrame.Shape.NoFrame)

        self.light = QFrame(self)
        self.light.setStyleSheet(
            "background-color: rgb(182, 107, 196)")
        self.light.move(150, 0)
        self.light.resize(50, 294)

        self.line = QFrame(self)
        self.line.setStyleSheet(
            "background-color: rgb(70, 70, 70)")
        self.line.move(415, 0)
        self.line.resize(10, 305)

        self.description = QFrame(self)
        self.description.setStyleSheet("background-color: rgb(70, 70, 70)")
        self.description.resize(425, 45)
        self.horizontalLayout = QHBoxLayout(self.description)

        self.description_1 = QtWidgets.QLabel(self)
        self.description_1.setText('ВИД')
        self.description_1.setFont(QFont('Verdana', weight=QtGui.QFont.Weight.Bold))
        self.description_1.resize(150, 45)
        self.description_1.move(5, 0)
        self.description_1.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.description_1.setStyleSheet('color: #ECF0F1; font-size: 20px')
        self.description_2 = QtWidgets.QLabel(self)
        self.description_2.setText('ЗАПИСЬ')
        self.description_2.setStyleSheet('color: #ECF0F1; font-size: 20px')
        self.description_2.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.description_2.setFont(QFont('Verdana', weight=QtGui.QFont.Weight.Bold))
        self.description_2.move(195, 0)
        self.description_2.resize(225, 45)
        self.description_2.setAlignment(Qt.AlignmentFlag.AlignCenter)

    # прокручивание окна вниз
    def scroll_down(self):
        global scroll
        scroll.verticalScrollBar().triggerAction(QtWidgets.QAbstractSlider.SliderAction.SliderSingleStepAdd)

    # прокручивание окна вверх
    def scroll_up(self):
        global scroll
        scroll.verticalScrollBar().triggerAction(QtWidgets.QAbstractSlider.SliderAction.SliderSingleStepSub)

    # перемещение окна (функция нажатия)
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.oldPos = event.globalPosition().toPoint()

    # перемещение окна (вызывается при отпускании кнопки мыши)
    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.oldPos = None

    # перемещение окна (вызывается всякий раз, когда мышь нажата и происходит перемещение)
    def mouseMoveEvent(self, event):
        if not self.oldPos:
            return
        delta = QPoint(event.globalPosition().toPoint() - self.oldPos)
        self.move(self.x() + delta.x(), self.y() + delta.y())
        self.oldPos = event.globalPosition().toPoint()

    # центрирование окна
    def center(self):
        qr = self.frameGeometry()
        cp = QtGui.QGuiApplication.primaryScreen().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def icon_1_clicked(self):
        if rec_cond == 'stop':
            window.form_widget.set_label_text(old_text + 'икс ')

    def icon_2_clicked(self):
        if rec_cond == 'stop':
            window.form_widget.set_label_text(old_text + 'игрек ')

    def icon_3_clicked(self):
        if rec_cond == 'stop':
            window.form_widget.set_label_text(old_text + 'зэт ')

    def icon_4_clicked(self):
        if rec_cond == 'stop':
            window.form_widget.set_label_text(old_text + 'тэ ')

    def icon_5_clicked(self):
        if rec_cond == 'stop':
            window.form_widget.set_label_text(old_text + 'плюс ')

    def icon_6_clicked(self):
        if rec_cond == 'stop':
            window.form_widget.set_label_text(old_text + 'минус ')

    def icon_7_clicked(self):
        if rec_cond == 'stop':
            window.form_widget.set_label_text(old_text + 'умножить на ')

    def icon_8_clicked(self):
        if rec_cond == 'stop':
            window.form_widget.set_label_text(old_text + 'дробь числитель a далее знаменатель b далее ')

    def icon_9_clicked(self):
        if rec_cond == 'stop':
            window.form_widget.set_label_text(old_text + 'синус x далее ')

    def icon_10_clicked(self):
        if rec_cond == 'stop':
            window.form_widget.set_label_text(old_text + 'косинус x далее ')

    def icon_11_clicked(self):
        if rec_cond == 'stop':
            window.form_widget.set_label_text(old_text + 'тангенс x далее ')

    def icon_12_clicked(self):
        if rec_cond == 'stop':
            window.form_widget.set_label_text(old_text + 'котангенс x далее ')

    def icon_13_clicked(self):
        if rec_cond == 'stop':
            window.form_widget.set_label_text(old_text + 'арксинус x далее ')

    def icon_14_clicked(self):
        if rec_cond == 'stop':
            window.form_widget.set_label_text(old_text + 'арккосинус x далее ')

    def icon_15_clicked(self):
        if rec_cond == 'stop':
            window.form_widget.set_label_text(old_text + 'арктангенс x далее ')

    def icon_17_clicked(self):
        if rec_cond == 'stop':
            window.form_widget.set_label_text(old_text + 'икс в квадрате ')

    def icon_18_clicked(self):
        if rec_cond == 'stop':
            window.form_widget.set_label_text(old_text + 'икс в степени a далее ')

    def icon_19_clicked(self):
        if rec_cond == 'stop':
            window.form_widget.set_label_text(old_text + 'корень квадратный из x далее ')

    def icon_20_clicked(self):
        if rec_cond == 'stop':
            window.form_widget.set_label_text(old_text + 'корень степени a далее из x далее ')

    def icon_21_clicked(self):
        if rec_cond == 'stop':
            window.form_widget.set_label_text(old_text + 'пи ')

    def icon_22_clicked(self):
        if rec_cond == 'stop':
            window.form_widget.set_label_text(old_text + 'скобка открывается ')

    def icon_23_clicked(self):
        if rec_cond == 'stop':
            window.form_widget.set_label_text(old_text + 'скобка закрывается ')


# математическое выражение
class MathTextLabel(QtWidgets.QWidget):

    def __init__(self, mathText, parent=None, **kwargs):
        super(QtWidgets.QWidget, self).__init__(parent, **kwargs)

        frml = QVBoxLayout(self)
        frml.setContentsMargins(0, 0, 0, 0)

        self.figure = Figure(facecolor='#323232')
        self.canvas = FigureCanvas(self.figure)
        frml.addWidget(self.canvas)
        self.figure.clear()
        text = self.figure.suptitle(
            mathText,
            x=0.0,
            y=1.0,
            horizontalalignment='left',
            verticalalignment='top',
            color='#ECF0F1',
            size=QtGui.QFont().pointSize() * 2.5
        )

        self.canvas.draw()

        (x0, y0), (x1, y1) = text.get_window_extent().get_points()
        w = x1 - x0
        h = y1 - y0

        self.setFixedSize(int(w), int(h))


# вывод ответа
class Answer(QtWidgets.QWidget):

    def __init__(self, mathText, parent=None, **kwargs):
        super(QtWidgets.QWidget, self).__init__(parent, **kwargs)

        ans = QVBoxLayout(self)
        ans.setContentsMargins(0, 0, 0, 0)

        self.figure = Figure(facecolor='#323232')
        self.canvas = FigureCanvas(self.figure)
        ans.addWidget(self.canvas)
        self.figure.clear()
        text = self.figure.suptitle(
            mathText,
            x=0.0,
            y=1.0,
            horizontalalignment='left',
            verticalalignment='top',
            color='#ECF0F1',
            size=QtGui.QFont().pointSize() * 2.5
        )

        self.canvas.draw()

        (x0, y0), (x1, y1) = text.get_window_extent().get_points()
        w = x1 - x0
        h = y1 - y0

        self.setFixedSize(int(w), int(h))


# график
class Plot(QtWidgets.QWidget):

    def __init__(self, parent=None, **kwargs):
        super(QtWidgets.QWidget, self).__init__(parent, **kwargs)
        global equation
        global solvation
        global delta
        global symb
        global b_type
        solvation_1 = []

        plot = QVBoxLayout(self)

        self.figure = Figure(figsize=(8, 6), dpi=55, facecolor='none')
        self.canvas = FigureCanvas(self.figure)
        plot.addWidget(self.canvas)
        self.figure.clear()

        self.ax = self.canvas.figure.subplots()

        k = 1

        if b_type == 1:
            if equation != '':
                for i in range(len(solvation)):
                    if solvation[i].is_real:
                        solvation_1.append(float(solvation[i]))

                if len(solvation_1) > 0:
                    min_xx = min(solvation_1)
                    max_xx = max(solvation_1)
                    m = 0
                    if abs(max_xx) > abs(min_xx):
                        m = abs(max_xx)
                    else:
                        m = abs(min_xx)
                    mm = m
                    if mm >= 1:
                        while mm > 0:
                            mm = mm // 10
                            k += 1
                    elif mm != 0:
                        while mm / 10 == 0:
                            k += 1
                            mm *= 10

                    if min_xx == 0 and max_xx == 0:
                        delta = 0.25
                    else:
                        delta = m / 10 ** k

                    if min_xx > 0:
                        xx = np.arange(0 - delta * 4, max_xx + delta * 4, delta/4)
                    elif max_xx < 0:
                        xx = np.arange(min_xx - delta * 4, 0 + delta * 4, delta/4)
                    else:
                        xx = np.arange(min_xx - delta * 4, max_xx + delta * 4, delta/4)

                    x = Symbol(symb)
                    f = lambdify(x, equation, 'numpy')
                    min_f = min(f(xx))
                    max_f = max(f(xx))
                    if min_xx > 0:
                        self.ax.hlines(0, float(0 - delta * 4), float(max_xx + delta * 4), color='#627E9A',
                                       linewidth=3)
                    elif max_xx < 0:
                        self.ax.hlines(0, float(min_xx - delta * 4), float(0 + delta * 4), color='#627E9A',
                                       linewidth=3)
                    else:
                        self.ax.hlines(0, float(min_xx - delta * 4), float(max_xx + delta * 4), color='#627E9A',
                                       linewidth=3)

                    self.ax.vlines(0, float(min_f), float(max_f), color='#627E9A', linewidth=3)

                    self.ax.plot(xx, f(xx), '#C83214', linewidth=8)


            for label in (self.ax.get_xticklabels() + self.ax.get_yticklabels()):
                label.set_fontsize(17)

            a = round(abs(max(self.ax.get_ylim())), 1) + round(abs(min(self.ax.get_ylim())), 1)
            b = len(self.ax.get_yticks())

            if equation != '' and len(solvation_1) > 0:
                for i in range(len(solvation_1)):
                    self.ax.plot((float(solvation_1[i])), 0, marker="o", markersize=20,
                                 markerfacecolor='#ECF0F1', markeredgecolor='#ECF0F1')
                    self.ax.text((float(solvation_1[i])), a / b,
                                 '[' + str(round(float(solvation_1[i]), 2)) + ', 0]',
                                 fontsize=15, color='#ECF0F1', ha='center',
                                 bbox=dict(boxstyle="round", ec='#323232', fc='#464646'))

        self.ax.grid(alpha=0.25, linewidth=3)

        tick_spacing = round(float((delta/4) * 10 ** k), (k+1))

        self.ax.xaxis.set_major_locator(matplotlib.ticker.MultipleLocator(tick_spacing))

        if symb == 'x':
            self.ax.set(xlabel='x', ylabel='f(x)', facecolor='none')
        elif symb == 'y':
            self.ax.set(xlabel='y', ylabel='f(y)', facecolor='none')
        elif symb == 'z':
            self.ax.set(xlabel='z', ylabel='f(z)', facecolor='none')
        elif symb == 't':
            self.ax.set(xlabel='t', ylabel='f(t)', facecolor='none')

        self.ax.spines['bottom'].set_color('none')
        self.ax.spines['top'].set_color('none')
        self.ax.spines['left'].set_color('none')
        self.ax.spines['right'].set_color('none')

        self.ax.xaxis.label.set_color('#ECF0F1')
        self.ax.yaxis.label.set_color('#ECF0F1')

        self.ax.tick_params(axis='x', colors='#ECF0F1')
        self.ax.tick_params(axis='y', colors='#ECF0F1')

        (x0, y0), (x1, y1) = self.figure.get_window_extent().get_points()
        w = x1 - x0
        h = y1 - y0

        self.setFixedSize(int(w) + 100, int(h))


# поток, отвечающий за запись текста
class MyThread(QtCore.QObject):
    newLabelText = QtCore.pyqtSignal(str)
    b_begin = QtCore.pyqtSignal()
    button_swipe = QtCore.pyqtSignal()
    button_eq = QtCore.pyqtSignal()
    button_dif = QtCore.pyqtSignal()
    button_calc = QtCore.pyqtSignal()
    button_rec = QtCore.pyqtSignal()
    button_pause = QtCore.pyqtSignal()
    button_stop = QtCore.pyqtSignal()
    button_help = QtCore.pyqtSignal()
    down_scrolling = QtCore.pyqtSignal()
    up_scrolling = QtCore.pyqtSignal()

    def run(self):
        global res
        global greeted
        global rec_cond
        global old_rec_cond
        while True:
            data = stream.read(4000, exception_on_overflow=False)
            if (rec.AcceptWaveform(data)) and (len(data) > 0):
                answer = json.loads(rec.Result())
                res = old_text
                if answer['text']:
                    res1 = answer['text']
                    if (not greeted) and (
                            res1 == 'привет' or res1 == 'приветик' or res1 == 'хай' or res1 == 'здравствуй'
                            or res1 == 'здравствуйте' or res1 == 'здрасте' or res1 == 'физкульт-привет'
                            or res1 == 'доброе утро' or res1 == 'добрый день' or res1 == 'добрый вечер'
                            or res1 == 'доброй ночи'):
                        self.b_begin.emit()
                        greeted = True
                    elif res1 == 'удалить' or res1 == 'удались' or res1 == 'удали':
                        res_mas = res.split(' ')
                        res = ''
                        for i in range(len(res_mas) - 2):
                            res += res_mas[i] + ' '
                    elif res1 == 'стереть' or res1 == 'сотри':
                        res = ''
                    elif res1 == 'пауза' or res1 == 'паузы' or res1 == 'пауз':
                        self.button_pause.emit()
                    elif res1 == 'клавиатура':
                        self.button_stop.emit()
                    elif (res1 == 'продолжить' or res1 == 'продолжим' or res1 == 'продолжил') and rec_cond != 'rec':
                        self.button_rec.emit()
                    elif res1 == 'начать':
                        res = ''
                        self.button_rec.emit()
                    elif res1 == 'помощь':
                        self.button_help.emit()
                    elif res1 == 'меню':
                        self.button_swipe.emit()
                    elif res1 == 'уравнение' or res1 == 'решить уравнение' or res1 == 'реши уравнение' \
                            or res1 == 'уравнения' or res1 == 'равнине':
                        self.button_eq.emit()
                    elif res1 == 'дифференцирование' or res1 == 'продифференцируй' or res1 == 'производная' \
                            or res1 == 'вычисли производную' or res1 == 'вычислить производную' \
                            or res1 == 'дифференцирования':
                        self.button_dif.emit()
                    elif res1 == 'вычислить' or res1 == 'вычисление' or res1 == 'калькулятор' or res1 == 'вычисли' \
                            or res1 == 'вычисления':
                        self.button_calc.emit()
                    elif res1 == 'вниз' or res1 == 'опустить':
                        self.down_scrolling.emit()
                    elif res1 == 'вверх' or res1 == 'поднять' or res1 == 'верх':
                        self.up_scrolling.emit()
                    else:
                        if rec_cond == 'rec':
                            res1_mas = res1.split(' ')
                            for word in res1_mas:
                                if word == 'катан':
                                    k = res1_mas.index(word)
                                    res1_mas[k] = 'котангенс'
                                    res1_mas[k + 1] = ''

                                if word == 'арк' or word == 'арт' or word == 'арков' or word == 'ар' or word == 'ак'\
                                        or word == 'арка':
                                    k = res1_mas.index(word)
                                    if res1_mas[k+1] == 'катан':
                                        res1_mas[k+1] = 'котангенс'
                                        res1_mas[k+2] = ''

                                    if res1_mas[k] == 'арка':
                                        res1_mas[k] = 'арккотангенс'
                                        res1_mas[k+1] = ''
                                    else:
                                        res1_mas[k] = 'арк' + res1_mas[k+1]
                                        res1_mas[k+1] = ''

                            for word in res1_mas:
                                a = morph.parse(word)[0]
                                if a.normal_form in word_transform:
                                    res += word + ' '
                                else:
                                    res += ''
            if rec_cond == 'rec':
                self.newLabelText.emit(res)

            QtCore.QThread.msleep(1)


# окно приложения
class Window(QMainWindow):
    global is_swiped

    def __init__(self, parent=None):
        super(Window, self).__init__(parent)

        self.form_widget = FormWidget(self)
        self.setCentralWidget(self.form_widget)

        # разрешение окна приложения
        self.resize(1280, 750)

        # центрирование окна
        self.center()

        # задний фон
        self.color1 = QColor()

        self.animation = QPropertyAnimation(self, b'color')
        self.animation.setDuration(20000)
        self.animation.setKeyValueAt(0, QColor(107, 196, 166))
        self.animation.setKeyValueAt(0.25, QColor(98, 126, 154))
        self.animation.setKeyValueAt(0.5, QColor(182, 107, 196))
        self.animation.setKeyValueAt(0.75, QColor(98, 126, 154))
        self.animation.setKeyValueAt(1, QColor(107, 196, 166))
        self.animation.setLoopCount(-1)
        self.animation.start()

        # скрытие titlebar
        self.setWindowFlag(QtCore.Qt.WindowType.FramelessWindowHint)

        # создание панели toolbar
        self.toolbar = QFrame(self)
        self.toolbar.setStyleSheet("background-color: rgb(50, 50, 50)")
        self.toolbar.resize(1280, 30)
        self.horizontalLayout = QHBoxLayout(self.toolbar)

        # название приложения
        self.program_name = QtWidgets.QLabel(self)
        # self.program_name.setText('VoiceMath')
        self.pixmap = QtGui.QPixmap('VoiceMath.png').scaled(80, 80, Qt.AspectRatioMode.KeepAspectRatio, QtCore.Qt.TransformationMode.SmoothTransformation)
        self.program_name.setPixmap(self.pixmap)
        self.program_name.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.program_name.resize(1280, 30)
        self.program_name.setFont(QFont('Verdana'))
        self.program_name.setObjectName('program_name')
        self.program_name.setStyleSheet('QLabel#program_name {color: #ECF0F1; background-color: rgba(0, 0, 0, 0); '
                                        'font-size: 17px}')

        # создание кнопки "закрыть"
        self.button_close = QPushButton('', self)
        self.button_close.setStyleSheet('''
                                QPushButton {border: none; background-color: rgb(50, 50, 50)}
                                QPushButton:hover {border: none; background-color: rgb(200, 50, 20)}
                                QPushButton:pressed {border: none; background-color: rgb(255, 0, 0)}
                                ''')
        self.button_close.setIcon(QIcon('close.png'))
        self.button_close.move(1250, 0)
        self.button_close.resize(30, 30)
        self.button_close.clicked.connect(self.button_close_clicked)

        # создание кнопки "свернуть"
        self.button_minimize = QPushButton('', self)
        self.button_minimize.setStyleSheet('''
                                        QPushButton {border: none; background-color: rgb(50, 50, 50)}
                                        QPushButton:hover {border: none; background-color: rgb(70, 70, 70)}
                                        QPushButton:pressed {border: none; background-color: rgb(90, 90, 90)}
                                        ''')
        self.button_minimize.setIcon(QIcon('minimize.png'))
        self.button_minimize.move(0, 0)
        self.button_minimize.resize(30, 30)
        self.button_minimize.clicked.connect(self.button_minimize_clicked)

        # позиция курсора на окне приложения
        self.oldPos = None

    # перемещение окна (функция нажатия)
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton and event.pos().y() <= 30:
            self.oldPos = event.globalPosition().toPoint()

    # перемещение окна (вызывается при отпускании кнопки мыши)
    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton and event.pos().y() <= 30:
            self.oldPos = None

    # перемещение окна (вызывается всякий раз, когда мышь нажата и происходит перемещение)
    def mouseMoveEvent(self, event):
        if not self.oldPos:
            return
        delta = QPoint(event.globalPosition().toPoint() - self.oldPos)
        self.move(self.x() + delta.x(), self.y() + delta.y())
        self.oldPos = event.globalPosition().toPoint()

    # закрыть
    def button_close_clicked(self):
        exit()

    # свернуть
    def button_minimize_clicked(self):
        self.showMinimized()

    # центрирование окна
    def center(self):
        qr = self.frameGeometry()
        cp = QtGui.QGuiApplication.primaryScreen().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    # передача значения цвета заднего фона
    def get_color1(self):
        return self.color1

    # задание градиента заднего фона
    def set_color1(self, col1):
        self.color1 = col1
        self.setStyleSheet('background-color: qlineargradient(spread:pad, x1:0.21895, y1:0.068, x2:0.800995, y2:0.931, '
                           'stop:0 rgb({}, {}, {}), stop:1 rgb(98, 126, 154))'.format(col1.red(), col1.green(),
                                                                                      col1.blue()))

    # применение градиента
    color = pyqtProperty(QColor, fget=get_color1, fset=set_color1)


# центральный форм-виджет
class FormWidget(QtWidgets.QWidget):
    def __init__(self, parent=None, **kwargs):
        super(QtWidgets.QWidget, self).__init__(parent, **kwargs)
        global symb

        # задник
        self.back = QFrame(self)
        self.back.resize(1230, 100)
        self.back.move(25, 75)
        self.back.setStyleSheet('background-color: rgba(98, 126, 154, 75); border: none; border-radius: 50')

        # задник_1
        self.back_1 = QFrame(self)
        self.back_1.resize(590, 450)
        self.back_1.move(25, 200)
        self.back_1.setStyleSheet('background-color: rgba(98, 126, 154, 75); border: none; border-radius: 50')

        # задник_2
        self.back_2 = QFrame(self)
        self.back_2.resize(590, 450)
        self.back_2.move(665, 200)
        self.back_2.setStyleSheet('background-color: rgba(98, 126, 154, 75); border: none; border-radius: 50')

        # поле ввода
        self.edit = QtWidgets.QLineEdit(self)
        self.edit.resize(1180, 50)
        self.edit.move(50, 100)
        self.edit.setStyleSheet('background-color: #ECF0F1; border: none; border-radius: 25; '
                                'color: rgb(220, 220, 220); font-size: 22px')
        self.edit.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.edit.setFont(QFont('Impact'))
        self.edit.setText('')
        self.edit.setPlaceholderText('Введите формулу')
        self.edit.textChanged.connect(self.text_is_changed)
        self.edit.placeholderText()

        self.viewer = QtSvgWidgets.QSvgWidget()
        self.viewer.setVisible(False)

        # поле вывода формулы
        self.frml_bg = QFrame(self)
        self.frml_bg.resize(540, 175)
        self.frml_bg.move(50, 225)
        self.frml_bg.setStyleSheet('background-color: rgb(50, 50, 50); border: none; border-radius: 50')
        self.frml_bg.setFocus()

        # поле вывода ответа
        self.ans_bg = QFrame(self)
        self.ans_bg.resize(540, 175)
        self.ans_bg.move(50, 450)
        self.ans_bg.setStyleSheet('background-color: rgb(50, 50, 50); border: none; border-radius: 50')

        # поле вывода графика
        self.plot_bg = QFrame(self)
        self.plot_bg.resize(540, 400)
        self.plot_bg.move(690, 225)
        self.plot_bg.setStyleSheet('background-color: rgb(50, 50, 50); border: none; border-radius: 30')

        # подпись "График"
        self.plot_label = QtWidgets.QLabel(self)
        self.plot_label.resize(540, 25)
        self.plot_label.move(690, 235)
        self.plot_label.setStyleSheet('background-color: rgba(50, 50, 50, 0); border: none; '
                                      'color: rgb(90, 90, 90); font-size: 20px')
        self.plot_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.plot_label.setFont(QFont('Verdana', weight=QtGui.QFont.Weight.Bold))
        self.plot_label.setText('ГРАФИК')

        # подпись "Выражение"
        self.calc_label = QtWidgets.QLabel(self)
        self.calc_label.resize(540, 25)
        self.calc_label.move(50, 235)
        self.calc_label.setStyleSheet('background-color: rgba(50, 50, 50, 0); border: none; '
                                      'color: rgb(90, 90, 90); font-size: 20px')
        self.calc_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.calc_label.setFont(QFont('Verdana', weight=QtGui.QFont.Weight.Bold))
        self.calc_label.setText('ВЫРАЖЕНИЕ')

        # подпись "Ответ"
        self.ans_label = QtWidgets.QLabel(self)
        self.ans_label.resize(540, 25)
        self.ans_label.move(50, 460)
        self.ans_label.setStyleSheet('background-color: rgba(50, 50, 50, 0); border: none; '
                                      'color: rgb(90, 90, 90); font-size: 20px')
        self.ans_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.ans_label.setFont(QFont('Verdana', weight=QtGui.QFont.Weight.Bold))
        self.ans_label.setText('ОТВЕТ')

        # график
        self.plot = QVBoxLayout(self.plot_bg)
        self.plot.addWidget(Plot(self))

        for i in reversed(range(self.plot.count())):
            widgetToRemove = self.plot.itemAt(i).widget()
            # remove it from the layout list
            self.plot.removeWidget(widgetToRemove)
            # remove it from the gui
            widgetToRemove.setParent(None)

        # слой с формулой
        self.frml = QVBoxLayout(self.frml_bg)

        # слой с ответом
        self.ans = QVBoxLayout(self.ans_bg)

        # затемнение для шторки
        self.black_0 = QFrame(self)
        black_0 = QGraphicsOpacityEffect(self.black_0)
        self.black_0.setGraphicsEffect(black_0)
        self.black_0_animation = QPropertyAnimation(black_0, b'opacity')

        # подсказка (шторка)
        self.help_1_background = QFrame(self)
        help_1_background = QGraphicsOpacityEffect(self.help_1_background)
        self.help_1_background.setGraphicsEffect(help_1_background)
        self.help_1_background_animation = QPropertyAnimation(help_1_background, b'opacity')
        self.help_1 = QtWidgets.QLabel(self)
        help_1 = QGraphicsOpacityEffect(self.help_1)
        self.help_1.setGraphicsEffect(help_1)
        self.help_1_animation = QPropertyAnimation(help_1, b'opacity')
        self.help_1_line = QtWidgets.QFrame(self)
        help_1_line = QGraphicsOpacityEffect(self.help_1_line)
        self.help_1_line.setGraphicsEffect(help_1_line)
        self.help_1_line_animation = QPropertyAnimation(help_1_line, b'opacity')

        # создание шторки выбора
        self.swipe_frame = QFrame(self)
        self.swipe_frame.setStyleSheet(
            "background-color: rgb(70, 70, 70); border-bottom-left-radius: 30px; border-bottom-right-radius: 30px")
        self.swipe_frame.move(100, -50)
        self.swipe_frame.resize(1080, 80)

        # кнопка взаимодействия со шторкой выбора
        self.button_swipe = Button('', self)
        self.button_swipe.setStyleSheet('''
                                QPushButton {border: none; background-color: rgb(70, 70, 70); border-bottom-left-radius: 30px; 
                                border-bottom-right-radius: 30px}
                                ''')
        self.button_swipe.setIcon(QIcon('down.png'))
        self.button_swipe.setIconSize(QtCore.QSize(30, 30))
        self.button_swipe.move(595, 20)
        self.button_swipe.resize(90, 40)
        is_swiped = False
        self.button_swipe.clicked.connect(self.button_swipe_clicked)

        # кнопка "вычисление"
        self.button_calculation = QPushButton('', self)
        self.button_calculation.setStyleSheet('''
                                   QPushButton {color: #ECF0F1; border: none; background-color: rgb(50, 50, 50); 
                                   border-radius: 25px; font-size: 20px}
                                   QPushButton:hover {color: #ECF0F1; border: none;
                                   background-color: rgb(182, 107, 196); border-radius: 25px; font-size: 20px}
                                   QPushButton:pressed {color: #ECF0F1; border: none; 
                                   background-color: rgb(98, 126, 154); border-radius: 25px; font-size: 20px}
                                   ''')
        self.button_calculation.move(145, -50)
        self.button_calculation.resize(300, 50)
        self.button_calculation.setText('ВЫЧИСЛЕНИЕ')
        self.button_calculation.setFont(QFont('Verdana', weight=QtGui.QFont.Weight.Bold))
        self.button_calculation.clicked.connect(self.button_calc_clicked)

        # кнопка "уравнение"
        self.button_equation = QPushButton('', self)
        self.button_equation.setStyleSheet('''
                                QPushButton {color: #ECF0F1; border: none; background-color: rgb(50, 50, 50); 
                                border-radius: 25px; font-size: 20px}
                                QPushButton:hover {color: #ECF0F1; border: none; background-color: rgb(182, 107, 196); 
                                border-radius: 25px; font-size: 20px}
                                QPushButton:pressed {color: #ECF0F1; border: none; background-color: rgb(98, 126, 154); 
                                border-radius: 25px; font-size: 20px}
                                ''')
        self.button_equation.move(490, -50)
        self.button_equation.resize(300, 50)
        self.button_equation.setText('УРАВНЕНИЕ')
        self.button_equation.setFont(QFont('Verdana', weight=QtGui.QFont.Weight.Bold))
        self.button_equation.clicked.connect(self.button_equation_clicked)

        # кнопка "дифференцирование"
        self.button_differentiation = QPushButton('', self)
        self.button_differentiation.setStyleSheet('''
                                                QPushButton {color: rgb(95, 95, 95); border: none; background-color: rgb(80, 80, 80); 
                                                border-radius: 25px; font-size: 20px}
                                                ''')
        # self.button_differentiation.setStyleSheet('''
        #                                 QPushButton {color: #ECF0F1; border: none; background-color: rgb(50, 50, 50);
        #                                 border-radius: 25px; font-size: 20px}
        #                                 QPushButton:hover {color: #ECF0F1; border: none; background-color: rgb(182, 107, 196);
        #                                 border-radius: 25px; font-size: 20px}
        #                                 QPushButton:pressed {color: #ECF0F1; border: none; background-color: rgb(98, 126, 154);
        #                                 border-radius: 25px; font-size: 20px}
        #                                 ''')
        self.button_differentiation.move(835, -50)
        self.button_differentiation.resize(300, 50)
        self.button_differentiation.setText('ДИФФЕРЕНЦИРОВАНИЕ')
        self.button_differentiation.setFont(QFont('Verdana', weight=QtGui.QFont.Weight.Bold))
        # self.button_differentiation.clicked.connect(self.button_dif_clicked)

        # затемнение для кнопок управления записью
        self.black_1 = QFrame(self)
        black_1 = QGraphicsOpacityEffect(self.black_1)
        self.black_1.setGraphicsEffect(black_1)
        self.black_1_animation = QPropertyAnimation(black_1, b'opacity')

        # подсказка (микрофон)
        self.help_2_background = QFrame(self)
        help_2_background = QGraphicsOpacityEffect(self.help_2_background)
        self.help_2_background.setGraphicsEffect(help_2_background)
        self.help_2_background_animation = QPropertyAnimation(help_2_background, b'opacity')
        self.help_2 = QtWidgets.QLabel(self)
        help_2 = QGraphicsOpacityEffect(self.help_2)
        self.help_2.setGraphicsEffect(help_2)
        self.help_2_animation = QPropertyAnimation(help_2, b'opacity')
        self.help_2_line = QtWidgets.QFrame(self)
        help_2_line = QGraphicsOpacityEffect(self.help_2_line)
        self.help_2_line.setGraphicsEffect(help_2_line)
        self.help_2_line_animation = QPropertyAnimation(help_2_line, b'opacity')

        # создание иконки "Запись"
        self.button_rec = QPushButton('', self)
        self.button_rec.setStyleSheet('''
                                    QPushButton {border: none; background-color: rgb(50, 50, 50); border-radius: 15px}
                                    QPushButton:hover {border: none; background-color: rgb(70, 70, 70); border-radius: 15px}
                                    QPushButton:pressed {border: none; background-color: rgb(90, 90, 90); border-radius: 15px}
                                ''')
        self.button_rec.setIcon(QIcon('rec.png'))
        self.button_rec.move(30, 690)
        self.button_rec.resize(30, 30)
        self.button_rec.clicked.connect(self.button_rec_clicked)

        # создание иконки "Запись на паузе"
        self.button_pause = QPushButton('', self)
        self.button_pause.setStyleSheet('''
                                    QPushButton {border: none; background-color: rgb(90, 90, 90); border-radius: 15px}
                                ''')
        self.button_pause.setIcon(QIcon('rec_pause.png'))
        self.button_pause.move(85, 690)
        self.button_pause.resize(30, 30)
        self.button_pause.clicked.connect(self.button_pause_clicked)

        # создание иконки "Запись остановлена"
        self.button_stop = QPushButton('', self)
        self.button_stop.setStyleSheet('''
                                    QPushButton {border: none; background-color: rgb(182, 107, 196); border-radius: 15px}
                                ''')
        self.button_stop.setIcon(QIcon('keyboard.png'))
        self.button_stop.move(140, 690)
        self.button_stop.resize(30, 30)
        self.button_stop.clicked.connect(self.button_stop_clicked)

        # создание иконки "Помощь"
        self.button_help = QPushButton('', self)
        self.button_help.setStyleSheet('''
                                    QPushButton {border: none; background-color: rgb(50, 50, 50); border-radius: 15px}
                                    QPushButton:hover {border: none; background-color: rgb(70, 70, 70); border-radius: 15px}
                                    QPushButton:pressed {border: none; background-color: rgb(90, 90, 90); border-radius: 15px}
                                ''')
        self.button_help.setIcon(QIcon('help.png'))
        self.button_help.move(1220, 690)
        self.button_help.resize(30, 30)
        self.button_help.clicked.connect(self.button_help_clicked)

        # затемнение для шторки
        self.black_2 = QFrame(self)
        black_2 = QGraphicsOpacityEffect(self.black_2)
        self.black_2.setGraphicsEffect(black_2)
        self.black_2_animation = QPropertyAnimation(black_2, b'opacity')

        # затемнение
        self.black = QFrame(self)
        self.black.setStyleSheet(
            "background-color: rgba(0, 0, 0, 200)")
        self.black.move(0, 30)
        self.black.resize(1280, 720)

        # анимация затемнения
        black = QGraphicsOpacityEffect(self.black)
        self.black.setGraphicsEffect(black)
        self.black_animation = QPropertyAnimation(black, b'opacity')
        self.black_animation.setDuration(500)
        self.black_animation.setStartValue(0)
        self.black_animation.setEndValue(1)
        self.black_animation.setEasingCurve(QEasingCurve.Type.InOutCubic)

        # создание окна приветствия
        self.begin = QFrame(self)
        self.begin.setStyleSheet(
            "background-color: rgb(107, 196, 166); border-radius: 30px")
        self.begin.move(360, 190)
        self.begin.resize(580, 400)
        self.begin_1 = QtWidgets.QLabel(self)
        self.begin_1.setStyleSheet(
            "background-color: rgb(50, 50, 50); border-radius: 30px; color: #ECF0F1; font-size: 22px")
        self.begin_1.move(400, 230)
        self.begin_1.resize(500, 280)
        self.begin_1.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        self.begin_1.setFont(QFont('Impact'))
        self.begin_1.setText('\nПривет!'
                             '\n'
                             '\nЯ твой голосовой помощник'
                             '\nдля решения математических задач'
                             '\n'
                             '\nПоздоровайся или нажми на кнопку ниже,'
                             '\nчтобы начать работу')
        self.begin_2 = QFrame(self)
        self.begin_2.setStyleSheet(
            "background-color: rgb(90, 90, 90); border-radius: 7px;")
        self.begin_2.move(440, 480)
        self.begin_2.resize(420, 15)

        # анимация окна приветствия
        begin = QGraphicsOpacityEffect(self.begin)
        self.begin.setGraphicsEffect(begin)
        self.begin_animation = QPropertyAnimation(begin, b'opacity')
        self.begin_animation.setDuration(2000)
        self.begin_animation.setStartValue(0)
        self.begin_animation.setEndValue(1)
        self.begin_animation.setEasingCurve(QEasingCurve.Type.InOutCubic)
        begin_1 = QGraphicsOpacityEffect(self.begin_1)
        self.begin_1.setGraphicsEffect(begin_1)
        self.begin_1_animation = QPropertyAnimation(begin_1, b'opacity')
        self.begin_1_animation.setDuration(2000)
        self.begin_1_animation.setStartValue(0)
        self.begin_1_animation.setEndValue(1)
        self.begin_1_animation.setEasingCurve(QEasingCurve.Type.InOutCubic)
        begin_2 = QGraphicsOpacityEffect(self.begin_2)
        self.begin_2.setGraphicsEffect(begin_2)
        self.begin_2_animation = QPropertyAnimation(begin_2, b'opacity')
        self.begin_2_animation.setDuration(2000)
        self.begin_2_animation.setStartValue(0)
        self.begin_2_animation.setEndValue(1)
        self.begin_2_animation.setEasingCurve(QEasingCurve.Type.InOutCubic)

        # создание кнопки "Окей" на окне приветствия
        self.button_okey = QPushButton('', self)
        self.button_okey.setStyleSheet('''
                                        QPushButton {color: #ECF0F1; border: none; background-color: rgb(50, 50, 50); 
                                        border-radius: 25px; font-size: 27px}
                                        QPushButton:hover {color: #ECF0F1; border: none; background-color: rgb(182, 107, 196); 
                                        border-radius: 25px; font-size: 27px}
                                        QPushButton:pressed {color: #ECF0F1; border: none; background-color: rgb(98, 126, 154); 
                                        border-radius: 25px; font-size: 27px}
                                        ''')
        self.button_okey.move(575, 525)
        self.button_okey.resize(150, 50)
        self.button_okey.setText('ОКЕЙ')
        self.button_okey.setFont(QFont('Verdana', weight=QtGui.QFont.Weight.Bold))
        self.button_okey.clicked.connect(self.button_begin)

        # анимация кнопки "Окей" на окне приветствия
        button_okey = QGraphicsOpacityEffect(self.button_okey)
        self.button_okey.setGraphicsEffect(button_okey)
        self.button_okey_animation = QPropertyAnimation(button_okey, b'opacity')
        self.button_okey_animation.setDuration(2000)
        self.button_okey_animation.setStartValue(0)
        self.button_okey_animation.setEndValue(1)
        self.button_okey_animation.setEasingCurve(QEasingCurve.Type.InOutCubic)

        # параллельная анимация всех элементов окна приветствия
        self.animation_group = QParallelAnimationGroup()
        self.animation_group.addAnimation(self.black_animation)
        self.animation_group.addAnimation(self.begin_animation)
        self.animation_group.addAnimation(self.begin_1_animation)
        self.animation_group.addAnimation(self.begin_2_animation)
        self.animation_group.addAnimation(self.button_okey_animation)
        self.animation_group.start()

        # версия приложения
        # self.program_version = QtWidgets.QLabel(self)
        # self.program_version.setText('Version 0.1')
        # self.program_version.move(1495, 900)
        # self.program_version.setFont(QFont('Verdana'))
        # self.program_version.setObjectName('program_version')
        # self.program_version.setStyleSheet('QLabel#program_version {color: rgba(255, 255, 255, 127); '
        #                                    'background-color: rgba(0, 0, 0, 0); font-size: 17px}')

        # инициализация потока
        self.thread = QtCore.QThread()
        self.myThread = MyThread()
        self.myThread.moveToThread(self.thread)
        self.myThread.newLabelText.connect(self.set_label_text)
        self.myThread.b_begin.connect(self.button_begin)
        self.myThread.button_swipe.connect(self.button_swipe_clicked)
        self.myThread.button_eq.connect(self.button_equation_clicked)
        self.myThread.button_dif.connect(self.button_dif_clicked)
        self.myThread.button_calc.connect(self.button_calc_clicked)
        self.myThread.button_rec.connect(self.button_rec_clicked)
        self.myThread.button_pause.connect(self.button_pause_clicked)
        self.myThread.button_stop.connect(self.button_stop_clicked)
        self.myThread.button_help.connect(self.button_help_clicked)
        self.myThread.down_scrolling.connect(self.help_scroll_down)
        self.myThread.up_scrolling.connect(self.help_scroll_up)
        self.thread.started.connect(self.myThread.run)
        self.thread.start()

    # функция проверки изменения текста
    def text_is_changed(self):
        global old_text
        global lat_str
        global f
        global k
        global symb
        global mas, lat_mas, b_type
        f = ''
        text = self.edit.text()
        current_text = str(text)
        sqrt_flag = False

        if self.edit.text() == '':
            self.edit.setStyleSheet('background-color: #ECF0F1; border: none; border-radius: 25; '
                                    'color: rgb(220, 220, 220); font-size: 22px')
            for i in reversed(range(self.frml.count())):
                widgetToRemove = self.frml.itemAt(i).widget()
                # remove it from the layout list
                self.frml.removeWidget(widgetToRemove)
                # remove it from the gui
                widgetToRemove.setParent(None)
            for i in reversed(range(self.ans.count())):
                widgetToRemove = self.ans.itemAt(i).widget()
                # remove it from the layout list
                self.ans.removeWidget(widgetToRemove)
                # remove it from the gui
                widgetToRemove.setParent(None)
            for i in reversed(range(self.plot.count())):
                widgetToRemove = self.plot.itemAt(i).widget()
                # remove it from the layout list
                self.plot.removeWidget(widgetToRemove)
                # remove it from the gui
                widgetToRemove.setParent(None)
        else:
            self.edit.setStyleSheet('background-color: #ECF0F1; border: none; border-radius: 25; '
                                    'color: rgb(70, 70, 70); font-size: 22px')

        if old_text != current_text and current_text != '':
            # добавление элемента
            lat_str = ''

            if len(current_text) == 1:
                lat_str = ''
                if self.latex_correct():
                    self.formula_change()
            else:
                if 'икс' in current_text:
                    symb = 'x'
                elif 'игрек' in current_text:
                    symb = 'y'
                elif 'зэт' in current_text or 'зет' in current_text or 'нет' in current_text:
                    symb = 'z'
                elif 'тэ' in current_text or 'те' in current_text:
                    symb = 't'

                lat_mas.clear()
                mas = current_text.split(' ')
                if current_text[len(current_text) - 1] == ' ':
                    mas.remove('')
                for i in range(0, len(mas)):
                    aa = num_true_form(mas[i])
                    aaa = word2latex(aa)
                    if aaa == '^{':
                        if lat_mas[len(lat_mas) - 1] == '\\sqrt':
                            lat_mas.append('[')
                            sqrt_flag = True
                        else:
                            lat_mas.append(aaa)
                    elif aa == 'далее':
                        if not sqrt_flag:
                            lat_mas.append(aaa)
                    elif aa == 'из':
                        if sqrt_flag:
                            lat_mas.append(']{')
                            sqrt_flag = False
                        else:
                            lat_mas.append(aaa)
                    else:
                        lat_mas.append(aaa)

                num_inds = []
                num_list = []
                for i in range(len(lat_mas)):

                    if lat_mas[i].isdigit():
                        if i == 0 or not lat_mas[i - 1].isdigit():
                            num_inds.append([i, i])
                        elif lat_mas[i - 1].isdigit():
                            num_inds[len(num_inds) - 1][1] += 1

                for i in range(len(num_inds)):
                    a1 = num_inds[i][0]
                    a2 = num_inds[i][1]
                    num_list.append(self.full_num(a1, a2))
                    lat_mas[a1] = num_list[i]
                    for k in range(a1 + 1, a2 + 1):
                        lat_mas[k] = ''

                for i in range(len(lat_mas)):
                    lat_str += lat_mas[i]

                if self.latex_correct():
                    self.formula_change()

        old_text = current_text

    # преобразование в полное числительное
    def full_num(self, a1, a2):
        global lat_mas
        new_mas = lat_mas[a1:a2 + 1]

        f_num = 0
        ind_bil = -1
        ind_mil = -1
        ind_th = -1
        start_ind = 0

        for i in range(len(new_mas)):
            if new_mas[i] == '1000000000':
                ind_bil = i
                t = 1
                if ind_bil > 0:
                    t = 0
                    for k in range(0, ind_bil):
                        t += int(new_mas[k])
                t *= 1000000000
                f_num += t
                start_ind = ind_bil + 1

            if new_mas[i] == '1000000':
                ind_mil = i
                t = 1
                if ind_mil > 0:
                    t = 0
                    for k in range(start_ind, ind_mil):
                        t += int(new_mas[k])
                t *= 1000000
                f_num += t
                start_ind = ind_mil + 1

            if new_mas[i] == '1000':
                ind_th = i
                t = 1
                if ind_th > 0:
                    t = 0
                    for k in range(start_ind, ind_th):
                        t += int(new_mas[k])
                start_ind = ind_th + 1
                t *= 1000
                f_num += t

        for k in range(start_ind, len(new_mas)):
            f_num += int(new_mas[k])

        return str(f_num)

    # функция проверки вывода записи latex
    def latex_correct(self):
        global lat_str
        global b
        global e
        binary_count = 0
        single_count = 0
        arc_count = 0
        scobs_count = 0
        other_count = 0
        pi_count = 0
        b = 0
        e = ''

        if lat_str != '\xa0':
            lat_str = lat_str.split()
            lat_str = ''.join(lat_str)

        binary_exp = ['frac', 'sum', 'int', 'over']
        single_exp = ['sqrt', 'lim', 'sin', 'cos', 'tan', 'cot', 'arc']
        arc = ['arc']
        scobs = ['left', 'right']
        other = ['^']
        pi = ['pi']

        is_correct = False

        for i in range(len(lat_str)):
            if (lat_str[i] == '{') or (lat_str[i] == '(') or (lat_str[i] == '['):
                b += 1
            elif (lat_str[i] == '}') or (lat_str[i] == ')') or (lat_str[i] == ']'):
                b -= 1

        for i in binary_exp:
            binary_count += lat_str.count(i)

        for i in single_exp:
            single_count += lat_str.count(i)

        for i in scobs:
            scobs_count += lat_str.count(i)

        for i in other:
            other_count += lat_str.count(i)

        for i in arc:
            arc_count += lat_str.count(i)

        for i in pi:
            pi_count += lat_str.count(i)



        if lat_str == '':
            is_correct = False
        elif lat_str.rfind('{}') != -1 or lat_str.rfind('{\}') != -1 \
                or lat_str.rfind('(\\\\') != -1 or lat_str.rfind('[]') != -1 \
                or lat_str.rfind('^-') != -1 or lat_str.rfind('^+') != -1 \
                or lat_str.rfind('^\\') != -1 or lat_str.rfind('^*') != -1 \
                or lat_str.rfind('$') != -1 or lat_str.rfind('-*') != -1 \
                or lat_str.rfind('+*') != -1 or lat_str.rfind('**') != -1 \
                or lat_str.rfind('\\*') != -1:
            e = 'error'
            self.edit.setStyleSheet('background-color: #ECF0F1; border: none; border-radius: 25; '
                                    'color: #C83214; font-size: 17px')
        elif lat_str[len(lat_str) - 1] != '\\' and lat_str[len(lat_str) - 1] != '^' \
                and lat_str[len(lat_str) - 1] != '_' \
                and b == 0 and e != 'error' \
                and lat_str.count('\\') == single_count + binary_count + scobs_count + pi_count - arc_count\
                and lat_str.count('}') + lat_str.count(')') == other_count + single_count + 2 * binary_count + \
                scobs_count / 2 - arc_count:
            is_correct = True

        return is_correct

    # функция записи формулы
    def formula_change(self):
        global equation
        global solvation
        global b_type
        global symb
        for i in reversed(range(self.frml.count())):
            widgetToRemove = self.frml.itemAt(i).widget()
            # remove it from the layout list
            self.frml.removeWidget(widgetToRemove)
            # remove it from the gui
            widgetToRemove.setParent(None)
        for i in reversed(range(self.ans.count())):
            widgetToRemove = self.ans.itemAt(i).widget()
            # remove it from the layout list
            self.ans.removeWidget(widgetToRemove)
            # remove it from the gui
            widgetToRemove.setParent(None)
        st = lat_str
        if b_type == 1:
            st += '=0'
        mathText = r'${}$'.format(st)
        self.frml.addWidget(MathTextLabel(mathText, self), alignment=Qt.AlignmentFlag.AlignHCenter)
        if b_type == 1:
            mathText = mathText.replace('=0', '')
        if mathText[len(mathText) - 2].isalpha() or mathText[len(mathText) - 2].isdigit() \
                or mathText[len(mathText) - 2] == '}':
            for i in reversed(range(self.plot.count())):
                widgetToRemove = self.plot.itemAt(i).widget()
                # remove it from the layout list
                self.plot.removeWidget(widgetToRemove)
                # remove it from the gui
                widgetToRemove.setParent(None)
            equation = latex2sympy2.latex2sympy(mathText)
            if b_type == 1:
                x = Symbol(symb)
                solvation = solve(equation, x)
                if len(solvation) > 1:
                    solvation_2 = latex(solvation)
                    solvation_2 = solvation_2.replace('[', '\\{')
                    solvation_2 = solvation_2.replace(']', '\\}')
                    if symb == 'x':
                        mathText = r'$x={}$'.format(solvation_2)
                    elif symb == 'y':
                        mathText = r'$y={}$'.format(solvation_2)
                    elif symb == 'z':
                        mathText = r'$z={}$'.format(solvation_2)
                    elif symb == 't':
                        mathText = r'$t={}$'.format(solvation_2)
                else:
                    solvation_2 = latex(solvation)
                    solvation_2 = solvation_2.replace('\\left[', '')
                    solvation_2 = solvation_2.replace('\\right]', '')
                    if symb == 'x':
                        mathText = r'$x={}$'.format(solvation_2)
                    elif symb == 'y':
                        mathText = r'$y={}$'.format(solvation_2)
                    elif symb == 'z':
                        mathText = r'$z={}$'.format(solvation_2)
                    elif symb == 't':
                        mathText = r'$t={}$'.format(solvation_2)
            else:
                solvation = sympy.N(equation)
                solvation_2 = latex(solvation)
                mathText = r'${}$'.format(solvation_2)

            self.ans.addWidget(Answer(mathText, self), alignment=Qt.AlignmentFlag.AlignHCenter)
            self.plot.addWidget(Plot(self))

    # функция нажатия на кнопку "Вычисление"
    @QtCore.pyqtSlot()
    def button_calc_clicked(self):
        global b_type
        global old_b_type
        global hints
        self.set_label_text('')
        self.button_color_change('grey')
        old_b_type = b_type
        b_type = 0
        self.button_color_change('violet')
        if hints:
            self.black_0_finished()

        if old_b_type != 0:
            self.anim_back_2 = QPropertyAnimation(self.back_2, b'pos')
            self.anim_back_2.setDuration(1000)
            self.anim_back_2.setStartValue(QPoint(665, 200))
            self.anim_back_2.setEndValue(QPoint(1475, 200))
            self.anim_back_2.setEasingCurve(QEasingCurve.Type.InOutCubic)
            self.anim_back_2.start()

            self.anim_plot_bg = QPropertyAnimation(self.plot_bg, b'pos')
            self.anim_plot_bg.setDuration(1000)
            self.anim_plot_bg.setStartValue(QPoint(690, 225))
            self.anim_plot_bg.setEndValue(QPoint(1500, 225))
            self.anim_plot_bg.setEasingCurve(QEasingCurve.Type.InOutCubic)
            self.anim_plot_bg.start()

            self.anim_plot_label = QPropertyAnimation(self.plot_label, b'pos')
            self.anim_plot_label.setDuration(1000)
            self.anim_plot_label.setStartValue(QPoint(690, 235))
            self.anim_plot_label.setEndValue(QPoint(1500, 235))
            self.anim_plot_label.setEasingCurve(QEasingCurve.Type.InOutCubic)
            self.anim_plot_label.start()

            self.anim_back_1 = QPropertyAnimation(self.back_1, b'size')
            self.anim_back_1.setDuration(1000)
            self.anim_back_1.setStartValue(QtCore.QSize(590, 450))
            self.anim_back_1.setEndValue(QtCore.QSize(1230, 450))
            self.anim_back_1.setEasingCurve(QEasingCurve.Type.InOutCubic)
            self.anim_back_1.start()

            self.anim_frml_bg = QPropertyAnimation(self.frml_bg, b'size')
            self.anim_frml_bg.setDuration(1000)
            self.anim_frml_bg.setStartValue(QtCore.QSize(540, 175))
            self.anim_frml_bg.setEndValue(QtCore.QSize(1180, 175))
            self.anim_frml_bg.setEasingCurve(QEasingCurve.Type.InOutCubic)
            self.anim_frml_bg.start()

            self.anim_ans_bg = QPropertyAnimation(self.ans_bg, b'size')
            self.anim_ans_bg.setDuration(1000)
            self.anim_ans_bg.setStartValue(QtCore.QSize(540, 175))
            self.anim_ans_bg.setEndValue(QtCore.QSize(1180, 175))
            self.anim_ans_bg.setEasingCurve(QEasingCurve.Type.InOutCubic)
            self.anim_ans_bg.start()

            self.anim_calc_label = QPropertyAnimation(self.calc_label, b'size')
            self.anim_calc_label.setDuration(1000)
            self.anim_calc_label.setStartValue(QtCore.QSize(540, 25))
            self.anim_calc_label.setEndValue(QtCore.QSize(1180, 25))
            self.anim_calc_label.setEasingCurve(QEasingCurve.Type.InOutCubic)
            self.anim_calc_label.start()

            self.anim_ans_label = QPropertyAnimation(self.ans_label, b'size')
            self.anim_ans_label.setDuration(1000)
            self.anim_ans_label.setStartValue(QtCore.QSize(540, 25))
            self.anim_ans_label.setEndValue(QtCore.QSize(1180, 25))
            self.anim_ans_label.setEasingCurve(QEasingCurve.Type.InOutCubic)
            self.anim_ans_label.start()

    # функция нажатия на кнопку "Уравнение"
    @QtCore.pyqtSlot()
    def button_equation_clicked(self):
        global b_type
        global old_b_type
        global hints
        self.set_label_text('')
        self.button_color_change('grey')
        old_b_type = b_type
        b_type = 1
        self.button_color_change('violet')
        if hints:
            self.black_0_finished()

        if old_b_type != 1:
            self.anim_back_2 = QPropertyAnimation(self.back_2, b'pos')
            self.anim_back_2.setDuration(1000)
            self.anim_back_2.setEndValue(QPoint(665, 200))
            self.anim_back_2.setStartValue(QPoint(1475, 200))
            self.anim_back_2.setEasingCurve(QEasingCurve.Type.InOutCubic)
            self.anim_back_2.start()

            self.anim_plot_bg = QPropertyAnimation(self.plot_bg, b'pos')
            self.anim_plot_bg.setDuration(1000)
            self.anim_plot_bg.setEndValue(QPoint(690, 225))
            self.anim_plot_bg.setStartValue(QPoint(1500, 225))
            self.anim_plot_bg.setEasingCurve(QEasingCurve.Type.InOutCubic)
            self.anim_plot_bg.start()

            self.anim_plot_label = QPropertyAnimation(self.plot_label, b'pos')
            self.anim_plot_label.setDuration(1000)
            self.anim_plot_label.setEndValue(QPoint(690, 235))
            self.anim_plot_label.setStartValue(QPoint(1500, 235))
            self.anim_plot_label.setEasingCurve(QEasingCurve.Type.InOutCubic)
            self.anim_plot_label.start()

            self.anim_back_1 = QPropertyAnimation(self.back_1, b'size')
            self.anim_back_1.setDuration(1000)
            self.anim_back_1.setEndValue(QtCore.QSize(590, 450))
            self.anim_back_1.setStartValue(QtCore.QSize(1230, 450))
            self.anim_back_1.setEasingCurve(QEasingCurve.Type.InOutCubic)
            self.anim_back_1.start()

            self.anim_frml_bg = QPropertyAnimation(self.frml_bg, b'size')
            self.anim_frml_bg.setDuration(1000)
            self.anim_frml_bg.setEndValue(QtCore.QSize(540, 175))
            self.anim_frml_bg.setStartValue(QtCore.QSize(1180, 175))
            self.anim_frml_bg.setEasingCurve(QEasingCurve.Type.InOutCubic)
            self.anim_frml_bg.start()

            self.anim_ans_bg = QPropertyAnimation(self.ans_bg, b'size')
            self.anim_ans_bg.setDuration(1000)
            self.anim_ans_bg.setEndValue(QtCore.QSize(540, 175))
            self.anim_ans_bg.setStartValue(QtCore.QSize(1180, 175))
            self.anim_ans_bg.setEasingCurve(QEasingCurve.Type.InOutCubic)
            self.anim_ans_bg.start()

            self.anim_calc_label = QPropertyAnimation(self.calc_label, b'size')
            self.anim_calc_label.setDuration(1000)
            self.anim_calc_label.setEndValue(QtCore.QSize(540, 25))
            self.anim_calc_label.setStartValue(QtCore.QSize(1180, 25))
            self.anim_calc_label.setEasingCurve(QEasingCurve.Type.InOutCubic)
            self.anim_calc_label.start()

            self.anim_ans_label = QPropertyAnimation(self.ans_label, b'size')
            self.anim_ans_label.setDuration(1000)
            self.anim_ans_label.setEndValue(QtCore.QSize(540, 25))
            self.anim_ans_label.setStartValue(QtCore.QSize(1180, 25))
            self.anim_ans_label.setEasingCurve(QEasingCurve.Type.InOutCubic)
            self.anim_ans_label.start()

    # функция нажатия на кнопку "Дифференцирование"
    @QtCore.pyqtSlot()
    def button_dif_clicked(self):
        global b_type
        global old_b_type
        global hints
        self.set_label_text('')
        self.button_color_change('grey')
        old_b_type = b_type
        b_type = 2
        self.button_color_change('violet')
        if hints:
            self.black_0_finished()

    # изменение цвета действующей кнопки
    def button_color_change(self, s):
        if b_type == 0:
            if (s == 'grey'):
                self.button_calculation.setStyleSheet('''
                    QPushButton {color: #ECF0F1; border: none; background-color: rgb(50, 50, 50); 
                    border-radius: 25px; font-size: 20px}
                    QPushButton:hover {color: #ECF0F1; border: none; background-color: rgb(182, 107, 196); 
                    border-radius: 25px; font-size: 20px}
                    QPushButton:pressed {color: #ECF0F1; border: none; background-color: rgb(98, 126, 154); 
                    border-radius: 25px; font-size: 20px}
                    ''')
            else:
                self.button_calculation.setStyleSheet('''
                    QPushButton {color: #ECF0F1; border: none; background-color: rgb(182, 107, 196); 
                    border-radius: 25px; font-size: 20px}
                    ''')
        elif b_type == 1:
            if (s == 'grey'):
                self.button_equation.setStyleSheet('''
                    QPushButton {color: #ECF0F1; border: none; background-color: rgb(50, 50, 50); border-radius: 25px; 
                    font-size: 20px}
                    QPushButton:hover {color: #ECF0F1; border: none; background-color: rgb(182, 107, 196); 
                    border-radius: 25px; font-size: 20px}
                    QPushButton:pressed {color: #ECF0F1; border: none; background-color: rgb(98, 126, 154); 
                    border-radius: 25px; font-size: 20px}
                    ''')
            else:
                self.button_equation.setStyleSheet('''
                    QPushButton {color: #ECF0F1; border: none; background-color: rgb(182, 107, 196); 
                    border-radius: 25px; font-size: 20px}
                    ''')
        elif b_type == 2:
            if (s == 'grey'):
                self.button_differentiation.setStyleSheet('''
                    QPushButton {color: #ECF0F1; border: none; background-color: rgb(50, 50, 50); 
                    border-radius: 25px; font-size: 20px}
                    QPushButton:hover {color: #ECF0F1; border: none; background-color: rgb(182, 107, 196); 
                    border-radius: 25px; font-size: 20px}
                    QPushButton:pressed {color: #ECF0F1; border: none; background-color: rgb(98, 126, 154); 
                    border-radius: 25px; font-size: 20px}
                    ''')
            else:
                self.button_differentiation.setStyleSheet('''
                    QPushButton {color: #ECF0F1; border: none; background-color: rgb(182, 107, 196); 
                    border-radius: 25px; font-size: 20px}
                    ''')

    # получение и вывод записанного в потоке текста
    @QtCore.pyqtSlot(str)
    def set_label_text(self, string1):
        if self.edit.text() != string1:
            self.edit.setText(string1)
            self.edit.adjustSize()
            self.edit.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.edit.resize(1180, 50)

    # функция нажатия на кнопку "Окей"
    @QtCore.pyqtSlot()
    def button_begin(self):
        global greeted
        self.black.setVisible(False)
        self.begin.setVisible(False)
        self.begin_1.setVisible(False)
        self.begin_2.setVisible(False)
        self.button_okey.setVisible(False)
        greeted = True

        self.black_0.setStyleSheet(
            "background-color: rgba(0, 0, 0, 200)")
        self.black_0.move(0, 30)
        self.black_0.resize(1280, 620)

        self.black_0_animation.setDuration(500)
        self.black_0_animation.setStartValue(0)
        self.black_0_animation.setEndValue(1)
        self.black_0_animation.setEasingCurve(QEasingCurve.Type.InOutCubic)
        self.black_0_animation.start()

        self.black_2.setStyleSheet(
            "background-color: rgba(0, 0, 0, 200)")
        self.black_2.move(0, 650)
        self.black_2.resize(1280, 100)

        self.black_2_animation.setDuration(500)
        self.black_2_animation.setStartValue(0)
        self.black_2_animation.setEndValue(1)
        self.black_2_animation.setEasingCurve(QEasingCurve.Type.InOutCubic)
        self.black_2_animation.start()

        self.help_1.setStyleSheet(
            "background-color: rgb(50, 50, 50); border-radius: 40px; color: #ECF0F1; font-size: 22px")
        self.help_1.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        self.help_1.setFont(QFont('Impact'))
        self.help_1.setText('\n'
                            'Выбери тип задачи'
                            '\n'
                            '\n(кликни или произнеси)')
        self.help_1.move(480, 305)
        self.help_1.resize(320, 170)

        self.help_1_background.setStyleSheet(
            "background-color: rgb(107, 196, 166); border-radius: 50px")
        self.help_1_background.move(440, 265)
        self.help_1_background.resize(400, 225)

        self.help_1_line.setStyleSheet(
            "background-color: rgb(90, 90, 90); border-radius: 7px;")
        self.help_1_line.move(520, 445)
        self.help_1_line.resize(240, 15)

        self.help_1_animation.setDuration(2000)
        self.help_1_animation.setStartValue(0)
        self.help_1_animation.setEndValue(1)
        self.help_1_animation.setEasingCurve(QEasingCurve.Type.InOutCubic)

        self.help_1_background_animation.setDuration(2000)
        self.help_1_background_animation.setStartValue(0)
        self.help_1_background_animation.setEndValue(1)
        self.help_1_background_animation.setEasingCurve(QEasingCurve.Type.InOutCubic)

        self.help_1_line_animation.setDuration(2000)
        self.help_1_line_animation.setStartValue(0)
        self.help_1_line_animation.setEndValue(1)
        self.help_1_line_animation.setEasingCurve(QEasingCurve.Type.InOutCubic)

        self.animation_group_help_1 = QParallelAnimationGroup()
        self.animation_group_help_1.addAnimation(self.help_1_animation)
        self.animation_group_help_1.addAnimation(self.help_1_background_animation)
        self.animation_group_help_1.addAnimation(self.help_1_line_animation)
        self.animation_group_help_1.start()
        self.button_swipe_clicked()

    # выключение затемнение для шторки
    def black_0_finished(self):
        global hints
        self.black_0.setVisible(False)
        self.black_2.setVisible(False)
        self.help_1.setVisible(False)
        self.help_1_background.setVisible(False)
        self.help_1_line.setVisible(False)
        self.button_swipe_clicked()
        self.black_1.setStyleSheet(
            "background-color: rgba(0, 0, 0, 200)")
        self.black_1.move(0, 30)
        self.black_1.resize(1280, 720)
        self.black_1_animation.setDuration(500)
        self.black_1_animation.setStartValue(0)
        self.black_1_animation.setEndValue(1)
        self.black_1_animation.setEasingCurve(QEasingCurve.Type.InOutCubic)
        self.black_1_animation.start()

        self.help_2.setStyleSheet(
            "background-color: rgb(50, 50, 50); border-radius: 40px; color: #ECF0F1; font-size: 18px")
        self.help_2.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        self.help_2.setFont(QFont('Impact'))
        self.help_2.setText('\n'
                            'Для начала записи, нажми на микрофон или скажи'
                            '\n«Начать»\n'
                            '\n'
                            'Чтобы приостановить запись, скажи или нажми'
                            '\nна кнопку «Пауза»\n'
                            '\n'
                            'Переключиться на ручной ввод можно произнеся'
                            '\nили нажав на значок «Клавиатура»\n'
                            '\n'
                            'Также вы можете ознакомиться с возможными'
                            '\nкомандами и кострукциями при помощи подсказки'
                            '\nв правом нижнем углу, нажав на нее или'
                            '\nсказав «Подсказка»')
        self.help_2.move(380, 213)
        self.help_2.resize(520, 355)

        self.help_2_background.setStyleSheet(
            "background-color: rgb(107, 196, 166); border-radius: 50px")
        self.help_2_background.move(340, 173)
        self.help_2_background.resize(600, 410)

        self.help_2_line.setStyleSheet(
            "background-color: rgb(90, 90, 90); border-radius: 7px;")
        self.help_2_line.move(420, 538)
        self.help_2_line.resize(440, 15)

        self.help_2_animation.setDuration(2000)
        self.help_2_animation.setStartValue(0)
        self.help_2_animation.setEndValue(1)
        self.help_2_animation.setEasingCurve(QEasingCurve.Type.InOutCubic)

        self.help_2_background_animation.setDuration(2000)
        self.help_2_background_animation.setStartValue(0)
        self.help_2_background_animation.setEndValue(1)
        self.help_2_background_animation.setEasingCurve(QEasingCurve.Type.InOutCubic)

        self.help_2_line_animation.setDuration(2000)
        self.help_2_line_animation.setStartValue(0)
        self.help_2_line_animation.setEndValue(1)
        self.help_2_line_animation.setEasingCurve(QEasingCurve.Type.InOutCubic)

        self.animation_group_help_2 = QParallelAnimationGroup()
        self.animation_group_help_2.addAnimation(self.help_2_animation)
        self.animation_group_help_2.addAnimation(self.help_2_background_animation)
        self.animation_group_help_2.addAnimation(self.help_2_line_animation)
        self.animation_group_help_2.start()

    # функция нажатия на кнопку "Помощь"
    @QtCore.pyqtSlot()
    def button_help_clicked(self):
        global help_window_is_opened
        if not help_window_is_opened:
            helpWindow.show()
            self.button_help.setStyleSheet(
                'QPushButton {border: none; background-color: rgb(182, 107, 196); border-radius: 15px}')
            help_window_is_opened = True
        else:
            helpWindow.close()
            self.button_help.setStyleSheet('''
                                    QPushButton {border: none; background-color: rgb(50, 50, 50); border-radius: 15px}
                                    QPushButton:hover {border: none; background-color: rgb(70, 70, 70); border-radius: 15px}
                                    QPushButton:pressed {border: none; background-color: rgb(90, 90, 90); border-radius: 15px}
                                    ''')
            help_window_is_opened = False

    # функция нажатия на кнопку "Запись"
    @QtCore.pyqtSlot()
    def button_rec_clicked(self):
        global rec_cond, old_rec_cond, res, hints
        self.black_1.setVisible(False)
        self.help_2.setVisible(False)
        self.help_2_background.setVisible(False)
        self.help_2_line.setVisible(False)
        hints = False
        old_rec_cond = rec_cond
        rec_cond = 'rec'
        self.button_pause.setStyleSheet('''
                        QPushButton {border: none; background-color: rgb(50, 50, 50); border-radius: 15px}
                        QPushButton:hover {border: none; background-color: rgb(70, 70, 70); border-radius: 15px}
                        QPushButton:pressed {border: none; background-color: rgb(90, 90, 90); border-radius: 15px}
                        ''')
        self.rec_cond_change()
        self.edit.setReadOnly(True)

    # функция нажатия на кнопку "Пауза"
    @QtCore.pyqtSlot()
    def button_pause_clicked(self):
        global rec_cond, old_rec_cond
        if rec_cond != 'stop':
            old_rec_cond = rec_cond
            rec_cond = 'pause'
            self.rec_cond_change()

    # функция нажатия на кнопку "Остановить запись"
    @QtCore.pyqtSlot()
    def button_stop_clicked(self):
        global rec_cond, old_rec_cond
        old_rec_cond = rec_cond
        rec_cond = 'stop'
        self.rec_cond_change()
        self.button_pause.setStyleSheet('''
                    QPushButton {border: none; background-color: rgb(90, 90, 90); border-radius: 15px}
                ''')
        self.edit.setReadOnly(False)

    # функция прокрутки вниз окна подсказки
    @QtCore.pyqtSlot()
    def help_scroll_down(self):
        helpWindow.scroll_down()

    # функция прокрутки вверх окна подсказки
    @QtCore.pyqtSlot()
    def help_scroll_up(self):
        helpWindow.scroll_up()

    # изменение статуса звукозаписи
    @QtCore.pyqtSlot()
    def rec_cond_change(self):
        global rec_cond, old_rec_cond
        if old_rec_cond == 'rec':
            self.button_rec.setStyleSheet('''
                        QPushButton {border: none; background-color: rgb(50, 50, 50); border-radius: 15px}
                        QPushButton:hover {border: none; background-color: rgb(70, 70, 70); border-radius: 15px}
                        QPushButton:pressed {border: none; background-color: rgb(90, 90, 90); border-radius: 15px}
                    ''')
        elif old_rec_cond == 'pause':
            self.button_pause.setStyleSheet('''
                        QPushButton {border: none; background-color: rgb(50, 50, 50); border-radius: 15px}
                        QPushButton:hover {border: none; background-color: rgb(70, 70, 70); border-radius: 15px}
                        QPushButton:pressed {border: none; background-color: rgb(90, 90, 90); border-radius: 15px}
                    ''')
        elif old_rec_cond == 'stop':
            self.button_stop.setStyleSheet('''
                        QPushButton {border: none; background-color: rgb(50, 50, 50); border-radius: 15px}
                        QPushButton:hover {border: none; background-color: rgb(70, 70, 70); border-radius: 15px}
                        QPushButton:pressed {border: none; background-color: rgb(90, 90, 90); border-radius: 15px}
                    ''')
        if rec_cond == 'rec':
            self.button_rec.setStyleSheet(
                'QPushButton {border: none; background-color: rgb(182, 107, 196); border-radius: 15px}')
        elif rec_cond == 'pause':
            self.button_pause.setStyleSheet(
                'QPushButton {border: none; background-color: rgb(182, 107, 196); border-radius: 15px}')
        elif rec_cond == 'stop':
            self.button_stop.setStyleSheet(
                'QPushButton {border: none; background-color: rgb(182, 107, 196); border-radius: 15px}')

    # функция выдвижения и задвижения шторки
    @QtCore.pyqtSlot()
    def button_swipe_clicked(self):
        global is_swiped
        global rec_cond
        if not is_swiped:
            self.anim_frame = QPropertyAnimation(self.swipe_frame, b'pos')
            self.anim_frame.setDuration(400)
            self.anim_frame.setStartValue(QPoint(100, -50))
            self.anim_frame.setEndValue(QPoint(100, 30))
            self.anim_frame.setEasingCurve(QEasingCurve.Type.InOutCubic)
            self.anim_frame.start()

            if self.button_swipe.pos().y() == 20:
                self.anim_button = QPropertyAnimation(self.button_swipe, b'pos')
                self.anim_button.setDuration(400)
                self.anim_button.setStartValue(QPoint(595, 20))
                self.anim_button.setEndValue(QPoint(595, 110))
                self.anim_button.setEasingCurve(QEasingCurve.Type.InOutCubic)
                self.anim_button.start()
            else:
                self.anim_button = QPropertyAnimation(self.button_swipe, b'pos')
                self.anim_button.setDuration(400)
                self.anim_button.setStartValue(QPoint(595, 30))
                self.anim_button.setEndValue(QPoint(595, 110))
                self.anim_button.setEasingCurve(QEasingCurve.Type.InOutCubic)
                self.anim_button.start()

            self.anim_calculation = QPropertyAnimation(self.button_calculation, b'pos')
            self.anim_calculation.setDuration(400)
            self.anim_calculation.setStartValue(QPoint(150, -50))
            self.anim_calculation.setEndValue(QPoint(150, 45))
            self.anim_calculation.setEasingCurve(QEasingCurve.Type.InOutCubic)
            self.anim_calculation.start()

            self.anim_equation = QPropertyAnimation(self.button_equation, b'pos')
            self.anim_equation.setDuration(400)
            self.anim_equation.setStartValue(QPoint(490, -50))
            self.anim_equation.setEndValue(QPoint(490, 45))
            self.anim_equation.setEasingCurve(QEasingCurve.Type.InOutCubic)
            self.anim_equation.start()

            self.anim_differentiation = QPropertyAnimation(self.button_differentiation, b'pos')
            self.anim_differentiation.setDuration(400)
            self.anim_differentiation.setStartValue(QPoint(835, -50))
            self.anim_differentiation.setEndValue(QPoint(835, 45))
            self.anim_differentiation.setEasingCurve(QEasingCurve.Type.InOutCubic)
            self.anim_differentiation.start()

            self.button_swipe.setIcon(QIcon('up.png'))
            self.horizontalLayout = QHBoxLayout(self.swipe_frame)

            is_swiped = True

        elif is_swiped:
            self.anim_frame = QPropertyAnimation(self.swipe_frame, b'pos')
            self.anim_frame.setDuration(300)
            self.anim_frame.setStartValue(QPoint(100, 30))
            self.anim_frame.setEndValue(QPoint(100, -50))
            self.anim_frame.setEasingCurve(QEasingCurve.Type.InOutCubic)
            self.anim_frame.start()

            self.button_swipe.setIcon(QIcon('down.png'))
            self.anim_button = QPropertyAnimation(self.button_swipe, b'pos')
            self.anim_button.setDuration(300)
            self.anim_button.setStartValue(QPoint(595, 110))
            self.anim_button.setEndValue(QPoint(595, 20))
            self.anim_button.setEasingCurve(QEasingCurve.Type.InOutCubic)
            self.anim_button.start()

            self.anim_calculation = QPropertyAnimation(self.button_calculation, b'pos')
            self.anim_calculation.setDuration(300)
            self.anim_calculation.setStartValue(QPoint(150, 45))
            self.anim_calculation.setEndValue(QPoint(150, -50))
            self.anim_calculation.setEasingCurve(QEasingCurve.Type.InOutCubic)
            self.anim_calculation.start()

            self.anim_equation = QPropertyAnimation(self.button_equation, b'pos')
            self.anim_equation.setDuration(300)
            self.anim_equation.setStartValue(QPoint(490, 45))
            self.anim_equation.setEndValue(QPoint(490, -50))
            self.anim_equation.setEasingCurve(QEasingCurve.Type.InOutCubic)
            self.anim_equation.start()

            self.anim_differentiation = QPropertyAnimation(self.button_differentiation, b'pos')
            self.anim_differentiation.setDuration(300)
            self.anim_differentiation.setStartValue(QPoint(835, 45))
            self.anim_differentiation.setEndValue(QPoint(835, -50))
            self.anim_differentiation.setEasingCurve(QEasingCurve.Type.InOutCubic)
            self.anim_differentiation.start()

            is_swiped = False


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setWindowIcon(QtGui.QIcon('logo.ico'))

    window = Window()
    window.show()
    window.setWindowIcon(QtGui.QIcon('logo.ico'))

    helpWindow = HelpWindow()

    app.setStyleSheet(scrollstyle)

    sys.exit(app.exec())
