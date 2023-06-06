import sys
from PyQt5.QtWidgets import QShortcut,QApplication, QMainWindow, QTextEdit, QLineEdit, QPushButton
from PyQt5.QtGui import QKeySequence
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon

from neo4j_driver import Neo4jConnection, Node
from answer_search import AnswerSearcher
from question_parser import QuestionPaser
from question_classifier import QuestionClassifier
from PyQt5.QtGui import QPalette, QBrush, QPixmap, QPainter
from PyQt5.QtCore import Qt
from PyQt5 import QtGui


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        #问答变量
        g = Neo4jConnection('neo4j://localhost:7687/', 'neo4j', '12345678')
        self.classifier = QuestionClassifier()
        self.parser = QuestionPaser()
        self.searcher = AnswerSearcher(g)

        self.setWindowTitle("聊天窗口")
        self.setGeometry(100, 100, 1000, 700)
        self.setWindowIcon(QIcon('image/logo.png'))


        # 创建控件
        self.chat_box = QTextEdit(self)
        self.chat_box.setReadOnly(True)  # 聊天记录窗口只读
        self.chat_box.move(10, 10)
        self.chat_box.resize(640, 600)
        self.chat_box.setStyleSheet("font - size:14;")
        self.chat_box.setStyleSheet("background-color: transparent;")





        self.entry = QLineEdit(self)
        self.entry.move(10, 640)
        self.entry.resize(280, 30)

        self.button = QPushButton('发送', self)
        shortcut = QShortcut(QKeySequence(Qt.Key_Return), self.button)
        shortcut.activated.connect(self.click)
        self.button.move(400, 640)
        self.button.resize(80, 30)
        self.button.clicked.connect(self.click)

    def chat_main(self, sent):
        answer = '你好，如果没能回答上来是因为我的智能程度还不够，望见谅'
        res_classify = self.classifier.classify(sent)
        if not res_classify:
            return answer
        res_sql = self.parser.parser_main(res_classify)
        final_answers = self.searcher.search_main(res_sql)
        if not final_answers:
            return answer
        else:
            return '\n'.join(final_answers)

    def click(self):
        message = self.entry.text()
        if message=="":
            return
        self.chat_box.append("You: " + message)

        reply = self.chat_main(message)
        self.chat_box.append("Bot: " + reply)
        self.chat_box.append("******************")
        self.entry.clear()  # 清空输入框

    def paintEvent(self, a0: QtGui.QPaintEvent) -> None:
        painter = QPainter(self)
        pixmap = QPixmap("image/background.png")
        painter.drawPixmap(self.rect(), pixmap)




if __name__ == '__main__':

    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())