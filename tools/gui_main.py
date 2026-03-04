"""Main GUI window for DBC-to-XML mapping tool."""

import sys
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QHBoxLayout,
    QWidget, QPushButton, QFileDialog, QLabel, QMessageBox,
)
from parser import load_dbc, list_messages
from xml_export import export_config
from gui_table import SignalTable


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("CAN-ROS2 Bridge - DBC Mapper")
        self.setMinimumSize(800, 500)
        self.messages = []
        self._build_ui()

    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)

        top = QHBoxLayout()
        self.file_label = QLabel("No DBC file loaded")
        btn_open = QPushButton("Open DBC...")
        btn_open.clicked.connect(self._open_dbc)
        top.addWidget(self.file_label, 1)
        top.addWidget(btn_open)
        layout.addLayout(top)

        self.table = SignalTable()
        layout.addWidget(self.table, 1)

        bottom = QHBoxLayout()
        btn_all = QPushButton("Select All")
        btn_all.clicked.connect(lambda: self._toggle_all(True))
        btn_none = QPushButton("Select None")
        btn_none.clicked.connect(lambda: self._toggle_all(False))
        btn_export = QPushButton("Export XML...")
        btn_export.clicked.connect(self._export_xml)
        btn_export.setStyleSheet("font-weight: bold;")
        bottom.addWidget(btn_all)
        bottom.addWidget(btn_none)
        bottom.addStretch()
        bottom.addWidget(btn_export)
        layout.addLayout(bottom)

    def _open_dbc(self):
        path, _ = QFileDialog.getOpenFileName(self, "Open DBC", "", "DBC Files (*.dbc)")
        if not path:
            return
        db = load_dbc(path)
        self.messages = list_messages(db)
        self.table.load_messages(self.messages)
        self.file_label.setText(f"Loaded: {path} ({len(self.messages)} messages)")

    def _toggle_all(self, checked: bool):
        from PySide6.QtCore import Qt
        state = Qt.Checked if checked else Qt.Unchecked
        for i in range(self.table.topLevelItemCount()):
            msg = self.table.topLevelItem(i)
            msg.setCheckState(0, state)
            for j in range(msg.childCount()):
                msg.child(j).setCheckState(0, state)

    def _export_xml(self):
        mappings = self.table.get_selected_mappings()
        if not mappings:
            QMessageBox.warning(self, "No Selection", "No signals selected.")
            return
        path, _ = QFileDialog.getSaveFileName(self, "Save XML", "config.xml", "XML (*.xml)")
        if path:
            export_config(mappings, path)
            QMessageBox.information(self, "Saved", f"Config saved to {path}")


def run_gui():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app_exec = getattr(app, "exec")
    sys.exit(app_exec())


if __name__ == "__main__":
    run_gui()
