# coding:utf-8
from PyQt5.QtCore import Qt, QRectF
from PyQt5.QtGui import QPixmap, QPainter, QColor, QBrush, QPainterPath, QLinearGradient
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel

from qfluentwidgets import ScrollArea, isDarkTheme, FluentIcon
from ..common.config import REPO_URL
from ..common.worker import Worker
from ..common.icon import Icon, FluentIconBase
from ..components.link_card import LinkCardView
from ..components.button_card import ButtonCardView
from ..common.style_sheet import StyleSheet
from .logger_interface import LoggerInterface


class BannerWidget(QWidget):
    """Banner widget"""

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setFixedHeight(336)

        self.vBoxLayout = QVBoxLayout(self)
        self.galleryLabel = QLabel("黑月无人驾驶", self)
        self.banner = QPixmap(":/gallery/images/header1.png")
        self.linkCardView = LinkCardView(self)

        self.galleryLabel.setObjectName("galleryLabel")

        self.vBoxLayout.setSpacing(0)
        self.vBoxLayout.setContentsMargins(0, 20, 0, 0)
        self.vBoxLayout.addWidget(self.galleryLabel)
        self.vBoxLayout.addWidget(self.linkCardView, 1, Qt.AlignBottom)
        self.vBoxLayout.setAlignment(Qt.AlignLeft | Qt.AlignTop)

        self.linkCardView.addCard(
            FluentIcon.GITHUB, "GitHub repo", "黑月无人驾驶", REPO_URL
        )

    def paintEvent(self, e):
        super().paintEvent(e)
        painter = QPainter(self)
        painter.setRenderHints(QPainter.SmoothPixmapTransform | QPainter.Antialiasing)
        painter.setPen(Qt.NoPen)

        path = QPainterPath()
        path.setFillRule(Qt.WindingFill)
        w, h = self.width(), self.height()
        path.addRoundedRect(QRectF(0, 0, w, h), 10, 10)
        path.addRect(QRectF(0, h - 50, 50, 50))
        path.addRect(QRectF(w - 50, 0, 50, 50))
        path.addRect(QRectF(w - 50, h - 50, 50, 50))
        path = path.simplified()

        # init linear gradient effect
        gradient = QLinearGradient(0, 0, 0, h)

        # draw background color
        if not isDarkTheme():
            gradient.setColorAt(0, QColor(207, 216, 228, 255))
            gradient.setColorAt(1, QColor(207, 216, 228, 0))
        else:
            gradient.setColorAt(0, QColor(0, 0, 0, 255))
            gradient.setColorAt(1, QColor(0, 0, 0, 0))

        painter.fillPath(path, QBrush(gradient))

        # draw banner image
        pixmap = self.banner.scaled(self.size(), transformMode=Qt.SmoothTransformation)
        painter.fillPath(path, QBrush(pixmap))


class HomeInterface(ScrollArea):
    """Home interface"""

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.workers = {}  # 用于存储活动的 Worker 实例

        self.banner = BannerWidget(self)
        self.view = QWidget(self)
        self.vBoxLayout = QVBoxLayout(self.view)

        self.__initWidget()
        self.loadSamples()

    def __initWidget(self):
        self.view.setObjectName("view")
        self.setObjectName("homeInterface")
        StyleSheet.HOME_INTERFACE.apply(self)

        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setWidget(self.view)
        self.setWidgetResizable(True)

        self.vBoxLayout.setContentsMargins(0, 0, 0, 36)
        self.vBoxLayout.setSpacing(40)
        self.vBoxLayout.addWidget(self.banner)
        self.vBoxLayout.setAlignment(Qt.AlignTop)

    def loadSamples(self):
        """load samples"""
        # basic input samples
        basicInputView = ButtonCardView("开始运行", self.view)

        self.run = basicInputView.addSampleCard(
            icon=":/gallery/images/controls/Button.png",
            title="运行",
            content="运行测试版本",
            func=self._run,
            routekey="LoggerInterface",
        )

        self.vBoxLayout.addWidget(basicInputView)

    def _run(self):
        """运行自动化程序"""
        if self.run.titleLabel.text() == "运行":
            self.run.titleLabel.setText("停止")
            from main import run, stop
            
            worker = Worker(run, stop)
            self.workers["run"] = worker
            worker.finished.connect(lambda: self.on_worker_finished(worker))
            worker.start()
        else:
            self.run.titleLabel.setText("运行")
            self.workers["run"].stop()

    def on_worker_finished(self, worker: Worker):
        # 线程完成时调用
        self.run.titleLabel.setText("运行")
        worker.deleteLater()  # 安全删除Worker对象
        del self.workers["run"]