"""Dialog used to persist several memory layers in one batch."""

import os

from qgis.PyQt.QtCore import Qt
from qgis.PyQt.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFileDialog,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QVBoxLayout,
)

try:
    from .translation import tr
except ImportError:
    from translation import tr


FORMATS = {
    "GPKG": {
        "label": "GeoPackage (*.gpkg)",
        "extension": ".gpkg",
        "container": True,
    },
    "ESRI Shapefile": {
        "label": "ESRI Shapefile (*.shp)",
        "extension": ".shp",
        "container": False,
    },
    "KML": {
        "label": "KML (*.kml)",
        "extension": ".kml",
        "container": True,
    },
    "OpenFileGDB": {
        "label": "File Geodatabase (*.gdb)",
        "extension": ".gdb",
        "container": True,
    },
}


class BatchTemporaryLayerExportDialog(QDialog):
    """Collect all options for a batch export without repeated file dialogs."""

    def __init__(self, layers, initial_dir="", parent=None):
        super().__init__(parent)
        self.layers = list(layers)
        self._paths = {}
        self._current_driver = "GPKG"
        self._initial_dir = initial_dir or os.path.expanduser("~")

        self.setWindowTitle(tr("批量保存临时图层"))
        self.resize(620, 460)

        root = QVBoxLayout(self)
        root.addWidget(QLabel(tr("共选择 {} 个临时图层。取消勾选可跳过对应图层。").format(len(self.layers))))

        self.layer_list = QListWidget()
        for layer in self.layers:
            item = QListWidgetItem(layer.name())
            item.setData(Qt.ItemDataRole.UserRole, layer.id())
            item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
            item.setCheckState(Qt.CheckState.Checked)
            self.layer_list.addItem(item)
        root.addWidget(self.layer_list)

        form = QFormLayout()
        self.format_combo = QComboBox()
        for driver, details in FORMATS.items():
            self.format_combo.addItem(details["label"], driver)
        form.addRow(tr("输出格式："), self.format_combo)

        destination_row = QHBoxLayout()
        self.destination_edit = QLineEdit()
        self.browse_button = QPushButton(tr("浏览…"))
        destination_row.addWidget(self.destination_edit, 1)
        destination_row.addWidget(self.browse_button)
        form.addRow(tr("目标位置："), destination_row)

        self.destination_hint = QLabel()
        self.destination_hint.setWordWrap(True)
        form.addRow("", self.destination_hint)

        self.conflict_combo = QComboBox()
        self.conflict_combo.addItem(tr("自动重命名"), "rename")
        self.conflict_combo.addItem(tr("覆盖同名图层"), "overwrite")
        self.conflict_combo.addItem(tr("跳过同名图层"), "skip")
        form.addRow(tr("名称冲突："), self.conflict_combo)

        self.replace_checkbox = QCheckBox(tr("写入并验证成功后，用新图层替换原临时图层"))
        self.replace_checkbox.setChecked(True)
        form.addRow("", self.replace_checkbox)
        root.addLayout(form)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        root.addWidget(buttons)

        self.format_combo.currentIndexChanged.connect(self._format_changed)
        self.browse_button.clicked.connect(self._browse)
        self.destination_edit.textChanged.connect(self._remember_path)
        self._format_changed()

    def _suggested_path(self, driver):
        details = FORMATS[driver]
        if not details["container"]:
            return self._initial_dir
        return os.path.join(self._initial_dir, tr("临时图层") + details["extension"])

    def _remember_path(self, path):
        self._paths[self._current_driver] = path

    def _format_changed(self):
        old_driver = self._current_driver
        self._paths[old_driver] = self.destination_edit.text()
        self._current_driver = self.format_combo.currentData()
        details = FORMATS[self._current_driver]
        self.destination_edit.setText(
            self._paths.get(self._current_driver) or self._suggested_path(self._current_driver)
        )
        if details["container"]:
            self.destination_hint.setText(tr("所有勾选图层将作为独立图层写入同一个容器。"))
        else:
            self.destination_hint.setText(tr("每个图层将生成一组 Shapefile，并统一保存到该文件夹。"))

    def _browse(self):
        driver = self.format_combo.currentData()
        details = FORMATS[driver]
        current = self.destination_edit.text() or self._initial_dir
        if not details["container"]:
            path = QFileDialog.getExistingDirectory(self, tr("选择 Shapefile 保存文件夹"), current)
        else:
            path, _ = QFileDialog.getSaveFileName(
                self,
                tr("选择批量保存位置"),
                current,
                details["label"],
            )
            if path and not path.lower().endswith(details["extension"]):
                path += details["extension"]
        if path:
            self.destination_edit.setText(path)

    def selected_layer_ids(self):
        selected_ids = []
        for row in range(self.layer_list.count()):
            item = self.layer_list.item(row)
            if item.checkState() == Qt.CheckState.Checked:
                selected_ids.append(item.data(Qt.ItemDataRole.UserRole))
        return selected_ids

    def export_options(self):
        driver = self.format_combo.currentData()
        destination = self.destination_edit.text().strip()
        details = FORMATS[driver]
        if details["container"] and destination and not destination.lower().endswith(
            details["extension"]
        ):
            destination += details["extension"]
        return {
            "layer_ids": self.selected_layer_ids(),
            "driver": driver,
            "destination": destination,
            "conflict": self.conflict_combo.currentData(),
            "replace": self.replace_checkbox.isChecked(),
        }
