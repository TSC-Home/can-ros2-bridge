"""Signal mapping table widget."""

from PySide6.QtWidgets import QTreeWidget, QTreeWidgetItem, QLineEdit
from PySide6.QtCore import Qt


class SignalTable(QTreeWidget):
    """Tree table showing messages and their signals with checkboxes."""

    def __init__(self):
        super().__init__()
        self.setHeaderLabels(["Name", "Bits", "Scale", "Unit", "ROS2 Topic"])
        self.setColumnWidth(0, 200)
        self.setColumnWidth(1, 80)
        self.setColumnWidth(2, 80)
        self.setColumnWidth(3, 60)
        self.setColumnWidth(4, 250)
        self.topic_editors: dict[str, QLineEdit] = {}

    def load_messages(self, messages: list[dict]) -> None:
        """Populate tree with DBC messages and signals."""
        self.clear()
        self.topic_editors.clear()

        for msg in messages:
            msg_item = QTreeWidgetItem([
                f"{msg['name']} (0x{msg['id']:X})", "", "", "", ""
            ])
            msg_item.setFlags(msg_item.flags() | Qt.ItemIsUserCheckable)
            msg_item.setCheckState(0, Qt.Checked)
            self.addTopLevelItem(msg_item)

            for sig in msg["signals"]:
                sig_item = QTreeWidgetItem([
                    sig["name"],
                    f"{sig['start_bit']}:{sig['length']}",
                    str(sig["scale"]),
                    sig.get("unit", ""),
                    "",
                ])
                sig_item.setFlags(sig_item.flags() | Qt.ItemIsUserCheckable)
                sig_item.setCheckState(0, Qt.Checked)
                sig_item.setData(0, Qt.UserRole, sig)
                sig_item.setData(0, Qt.UserRole + 1, msg)
                msg_item.addChild(sig_item)

                topic = f"/{msg['name'].lower()}/{sig['name'].lower()}"
                editor = QLineEdit(topic)
                self.setItemWidget(sig_item, 4, editor)
                key = f"{msg['id']}_{sig['name']}"
                self.topic_editors[key] = editor

            msg_item.setExpanded(True)

    def get_selected_mappings(self) -> list[dict]:
        """Return list of checked signal mappings with topics."""
        mappings = []
        for i in range(self.topLevelItemCount()):
            msg_item = self.topLevelItem(i)
            for j in range(msg_item.childCount()):
                sig_item = msg_item.child(j)
                if sig_item.checkState(0) != Qt.Checked:
                    continue
                sig = sig_item.data(0, Qt.UserRole)
                msg = sig_item.data(0, Qt.UserRole + 1)
                key = f"{msg['id']}_{sig['name']}"
                topic = self.topic_editors[key].text()
                mappings.append({"message": msg, "signal": sig, "topic": topic})
        return mappings
