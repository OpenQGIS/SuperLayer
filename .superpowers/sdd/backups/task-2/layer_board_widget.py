import os
import re
import csv
import datetime
from functools import partial

# Robust Qt Imports fallback
try:
    from PyQt5.QtCore import Qt, QCoreApplication, QSettings, QTranslator, QSize
    from PyQt5.QtGui import QIcon, QTextCursor, QBrush, QColor
    from PyQt5.QtWidgets import (
        QWidget, QVBoxLayout, QHBoxLayout, QSplitter, QTabWidget, QTableWidget,
        QTableWidgetItem, QPushButton, QLineEdit, QComboBox, QLabel, QTextEdit,
        QScrollArea, QMessageBox, QFileDialog, QApplication, QGroupBox
    )
except ImportError:
    try:
        from qtpy.QtCore import Qt, QCoreApplication, QSettings, QTranslator, QSize
        from qtpy.QtGui import QIcon, QTextCursor, QBrush, QColor
        from qtpy.QtWidgets import (
            QWidget, QVBoxLayout, QHBoxLayout, QSplitter, QTabWidget, QTableWidget,
            QTableWidgetItem, QPushButton, QLineEdit, QComboBox, QLabel, QTextEdit,
            QScrollArea, QMessageBox, QFileDialog, QApplication, QGroupBox
        )
    except ImportError:
        try:
            from PySide2.QtCore import Qt, QCoreApplication, QSettings, QTranslator, QSize
            from PySide2.QtGui import QIcon, QTextCursor, QBrush, QColor
            from PySide2.QtWidgets import (
                QWidget, QVBoxLayout, QHBoxLayout, QSplitter, QTabWidget, QTableWidget,
                QTableWidgetItem, QPushButton, QLineEdit, QComboBox, QLabel, QTextEdit,
                QScrollArea, QMessageBox, QFileDialog, QApplication, QGroupBox
            )
        except ImportError:
            try:
                from PySide6.QtCore import Qt, QCoreApplication, QSize
                from PySide6.QtGui import QAction, QIcon, QTextCursor, QBrush, QColor
                from PySide6.QtWidgets import (
                    QWidget, QVBoxLayout, QHBoxLayout, QSplitter, QTabWidget, QTableWidget,
                    QTableWidgetItem, QPushButton, QLineEdit, QComboBox, QLabel, QTextEdit,
                    QScrollArea, QMessageBox, QFileDialog, QApplication, QGroupBox
                )
            except ImportError:
                # Basic mocks for CLI testing
                class Qt:
                    ItemIsSelectable = 1
                    ItemIsEditable = 2
                    ItemIsEnabled = 4
                    EditRole = 2
                    yellow = 12
                    NoItemFlags = 0
                    Horizontal = 1
                    Vertical = 2
                class QSize:
                    def __init__(self, w, h): pass
                class QIcon:
                    def __init__(self, *args): pass
                class QTextCursor:
                    End = 1
                    MoveAnchor = 2
                class QBrush:
                    def __init__(self, color): pass
                class QColor:
                    def __init__(self, *args): pass
                class QWidget:
                    def __init__(self, parent=None):
                        self.layout = None
                    def setLayout(self, layout):
                        self.layout = layout
                    def setStyleSheet(self, style): pass
                class QVBoxLayout:
                    def __init__(self, parent=None):
                        self.widgets = []
                    def addWidget(self, widget, *args):
                        self.widgets.append(widget)
                    def addLayout(self, layout, *args): pass
                    def setContentsMargins(self, *args): pass
                    def setSpacing(self, s): pass
                class QHBoxLayout(QVBoxLayout): pass
                class QSplitter(QWidget):
                    def __init__(self, *args):
                        super().__init__()
                        self.widgets = []
                    def addWidget(self, w):
                        self.widgets.append(w)
                    def setStretchFactor(self, idx, f): pass
                class QTabWidget(QWidget):
                    def __init__(self, parent=None):
                        super().__init__()
                        self.tabs = []
                    def addTab(self, w, name):
                        self.tabs.append((w, name))
                    def currentIndex(self): return 0
                class QTableWidget(QWidget):
                    def __init__(self, parent=None):
                        super().__init__()
                        self.rows = 0
                        self.cols = 0
                        self.items = {}
                        self.horizontal_labels = []
                    def setRowCount(self, r): self.rows = r
                    def rowCount(self): return self.rows
                    def setColumnCount(self, c): self.cols = c
                    def columnCount(self): return self.cols
                    def setHorizontalHeaderLabels(self, labels): self.horizontal_labels = labels
                    def setItem(self, r, c, item): self.items[(r, c)] = item
                    def item(self, r, c): return self.items.get((r, c), None)
                    def removeRow(self, r): self.rows = max(0, self.rows - 1)
                    def clearSelection(self): pass
                    def setAlternatingRowColors(self, val): pass
                    class _Signal:
                        def connect(self, slot): pass
                        def disconnect(self): pass
                    itemChanged = _Signal()
                    def selectionModel(self):
                        class MockSM:
                            def selectedRows(self): return []
                        return MockSM()
                class QTableWidgetItem:
                    def __init__(self, text=""):
                        self._text = text
                        self._data = {}
                        self._flags = 0
                    def setFlags(self, f): self._flags = f
                    def setData(self, role, val): self._data[role] = val
                    def data(self, role): return self._data.get(role, self._text)
                    def setBackground(self, brush): pass
                    def setIcon(self, icon): pass
                    def setToolTip(self, text): pass
                class QPushButton(QWidget):
                    def __init__(self, text=""):
                        super().__init__()
                        self.text = text
                    class _Signal:
                        def connect(self, slot): pass
                    clicked = _Signal()
                    def setEnabled(self, e): pass
                class QLineEdit(QWidget):
                    def __init__(self, parent=None): super().__init__()
                    def text(self): return ""
                    def clear(self): pass
                    def setText(self, text): pass
                class QComboBox(QWidget):
                    def __init__(self, parent=None): super().__init__()
                    def clear(self): pass
                    def addItem(self, text, val=None): pass
                    def currentText(self): return ""
                    def setEnabled(self, e): pass
                class QLabel(QWidget):
                    def __init__(self, text=""):
                        super().__init__()
                        self._text = text
                    def setText(self, text): self._text = text
                class QTextEdit(QWidget):
                    def __init__(self, parent=None): super().__init__()
                    def clear(self): pass
                    def ensureCursorVisible(self): pass
                    def append(self, text): pass
                    def textCursor(self):
                        class MockCursor:
                            def movePosition(self, pos, anchor): pass
                        return MockCursor()
                    def setTextCursor(self, c): pass
                class QScrollArea(QWidget):
                    def __init__(self, parent=None): super().__init__()
                    def setWidget(self, w): pass
                    def setWidgetResizable(self, r): pass
                class QGroupBox(QWidget):
                    def __init__(self, title, parent=None): super().__init__()
                class QCoreApplication:
                    @staticmethod
                    def translate(context, message):
                        return message
                class QSettings:
                    def __init__(self, *args): pass
                    def value(self, key): return "en"
                class QTranslator:
                    def __init__(self, *args): pass
                    def load(self, path): return True
                class QMessageBox:
                    @classmethod
                    def information(cls, parent, title, text): pass
                    @classmethod
                    def warning(cls, parent, title, text): pass
                class QFileDialog:
                    @classmethod
                    def getSaveFileName(cls, *args): return "", ""
                class QApplication:
                    @classmethod
                    def setOverrideCursor(cls, cursor): pass
                    @classmethod
                    def restoreOverrideCursor(cls): pass

# QGIS Imports fallback
try:
    from qgis.core import (
        QgsProject, QgsMapLayer, QgsMapLayerModel, QgsCoordinateReferenceSystem,
        QgsVectorDataProvider, QgsVectorLayer, Qgis, QgsStyle, QgsLayerTreeUtils
    )
except ImportError:
    class Qgis:
        Critical = 1
    class QgsProject:
        _instance = None
        @classmethod
        def instance(cls):
            if cls._instance is None: cls._instance = cls()
            return cls._instance
        def mapLayers(self): return {}
        def mapLayer(self, layer_id): return None
        def removeMapLayer(self, layer_id): pass
        def setDirty(self, d): pass
    class QgsMapLayer:
        VectorLayer = 0
        RasterLayer = 1
        def type(self): return 0
        def id(self): return ""
        def name(self): return ""
        def title(self): return ""
        def abstract(self): return ""
        def shortName(self): return ""
        def crs(self):
            class MockCRS:
                def authid(self): return "EPSG:4326"
            return MockCRS()
        def extent(self):
            class MockExtent:
                def toString(self, dec): return "0,0,0,0"
            return MockExtent()
        def isSpatial(self): return True
        def maximumScale(self): return 0.0
        def minimumScale(self): return 0.0
        def toggleScaleBasedVisibility(self, b): pass
        def setMaximumScale(self, s): pass
        def setMinimumScale(self, s): pass
        def setCrs(self, crs): pass
        def triggerRepaint(self): pass
        def providerType(self): return "ogr"
    class QgsMapLayerModel:
        @classmethod
        def iconForLayer(cls, layer): return QIcon()
    class QgsCoordinateReferenceSystem:
        def __init__(self, *args): pass
        def createFromOgcWmsCrs(self, text): return True
        def authid(self): return "EPSG:4326"
    class QgsVectorDataProvider:
        CreateSpatialIndex = 1
    class QgsVectorLayer(QgsMapLayer):
        def isEditable(self): return False
        def dataProvider(self):
            class MockProvider:
                def name(self): return "ogr"
                def dataSourceUri(self): return "test_path"
                def availableEncodings(self): return ["UTF-8"]
            return MockProvider()
    class QgsStyle:
        @classmethod
        def defaultStyle(cls): return None
    class QgsLayerTreeUtils:
        @classmethod
        def countMapLayerInTree(cls, root, layer): return 1


class LayerBoardWidget(QWidget):
    """Integrated tabular editor and dashboard for QGIS vector/raster layers."""
    
    def __init__(self, iface, parent=None):
        super().__init__(parent)
        self.iface = iface
        
        # Attribute mappings & metadata schema
        self.layersTable = {
            'generic': {
                'attributes': [
                    {'key': 'id', 'label': self.tr('Id'), 'editable': False, 'spatial_only': False},
                    {'key': 'name', 'label': self.tr('Name'), 'editable': True, 'type': 'string', 'spatial_only': False},
                    {'key': 'crs', 'label': self.tr('CRS'), 'editable': False, 'type': 'crs', 'spatial_only': True},
                    {'key': 'maxScale', 'label': self.tr('Max scale'), 'editable': True, 'type': 'integer', 'spatial_only': True},
                    {'key': 'minScale', 'label': self.tr('Min scale'), 'editable': True, 'type': 'integer', 'spatial_only': True},
                    {'key': 'extent', 'label': self.tr('Extent'), 'editable': False, 'spatial_only': True},
                    {'key': 'title', 'label': self.tr('Title'), 'editable': True, 'type': 'string', 'spatial_only': False},
                    {'key': 'abstract', 'label': self.tr('Abstract'), 'editable': True, 'type': 'string', 'spatial_only': False},
                    {'key': 'shortname', 'label': self.tr('Short name'), 'editable': True, 'type': 'string', 'spatial_only': False},
                    {'key': 'ghost', 'label': self.tr('Ghost ?'), 'editable': False, 'type': 'string', 'spatial_only': False}
                ]
            },
            'vector': {
                'attributes': [
                    {'key': 'labelsEnabled', 'label': self.tr('Labels on'), 'editable': False, 'spatial_only': True},
                    {'key': 'featureCount', 'label': self.tr('Features count'), 'editable': False, 'spatial_only': False},
                    {'key': 'source|uri', 'label': self.tr('Datasource URI'), 'editable': True, 'spatial_only': False},
                    {'key': 'encoding', 'label': self.tr('Encoding'), 'editable': True, 'spatial_only': False},
                    {'key': 'styles_in_db', 'label': self.tr('Styles in DB'), 'editable': False, 'type': 'string', 'spatial_only': False},
                ],
            },
            'raster': {
                'attributes': [
                    {'key': 'width', 'label': self.tr('Width'), 'editable': False},
                    {'key': 'height', 'label': self.tr('Height'), 'editable': False},
                    {'key': 'rasterUnitsPerPixelX', 'label': self.tr('Units per pixel (X)'), 'editable': False},
                    {'key': 'rasterUnitsPerPixelY', 'label': self.tr('Units per pixel (Y)'), 'editable': False},
                    {'key': 'uri', 'label': self.tr('URI'), 'editable': False}
                ],
            }
        }
        
        self.layersAttributes = {}
        self.layerBoardChangedData = {'vector': {}, 'raster': {}}
        self.layerBoardData = {'vector': [], 'raster': []}
        
        self.csvDelimiter = ','
        self.csvQuotechar = '"'
        self.csvQuoting = csv.QUOTE_ALL
        
        self.styleWidget = None
        self.styleLayer = None
        
        self.init_ui()
        
    def tr(self, message):
        return QCoreApplication.translate('LayerBoardWidget', message)
        
    def init_ui(self):
        # 1. Main Layout
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(10, 10, 10, 10)
        self.main_layout.setSpacing(10)
        
        # 2. QSplitter (left-right split)
        self.splitter = QSplitter(Qt.Horizontal)
        self.main_layout.addWidget(self.splitter)
        
        # 3. Left Panel (Tab widget for vector and raster tables)
        self.left_container = QWidget()
        left_layout = QVBoxLayout(self.left_container)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(10)
        
        self.tab_widget = QTabWidget()
        left_layout.addWidget(self.tab_widget)
        
        # Vector Tab
        self.vector_tab = QWidget()
        vector_layout = QVBoxLayout(self.vector_tab)
        vector_layout.setContentsMargins(0, 0, 0, 0)
        vector_layout.setSpacing(6)
        
        self.vector_table = QTableWidget()
        self.vector_table.setAlternatingRowColors(True)
        vector_layout.addWidget(self.vector_table)
        
        self.vector_buttons_layout = QHBoxLayout()
        self.btn_commit_vector = QPushButton(self.tr("保存修改 (Commit)"))
        self.btn_discard_vector = QPushButton(self.tr("放弃修改 (Discard)"))
        self.vector_buttons_layout.addWidget(self.btn_commit_vector)
        self.vector_buttons_layout.addWidget(self.btn_discard_vector)
        vector_layout.addLayout(self.vector_buttons_layout)
        
        self.tab_widget.addTab(self.vector_tab, self.tr("矢量图层"))
        
        # Raster Tab
        self.raster_tab = QWidget()
        raster_layout = QVBoxLayout(self.raster_tab)
        raster_layout.setContentsMargins(0, 0, 0, 0)
        raster_layout.setSpacing(6)
        
        self.raster_table = QTableWidget()
        self.raster_table.setAlternatingRowColors(True)
        raster_layout.addWidget(self.raster_table)
        
        self.raster_buttons_layout = QHBoxLayout()
        self.btn_commit_raster = QPushButton(self.tr("保存修改 (Commit)"))
        self.btn_discard_raster = QPushButton(self.tr("放弃修改 (Discard)"))
        self.raster_buttons_layout.addWidget(self.btn_commit_raster)
        self.raster_buttons_layout.addWidget(self.btn_discard_raster)
        raster_layout.addLayout(self.raster_buttons_layout)
        
        self.tab_widget.addTab(self.raster_tab, self.tr("栅格图层"))
        
        # Assign UI references to self.layersTable for compatibility
        self.layersTable['vector']['tableWidget'] = self.vector_table
        self.layersTable['vector']['commitButton'] = self.btn_commit_vector
        self.layersTable['vector']['discardButton'] = self.btn_discard_vector
        
        self.layersTable['raster']['tableWidget'] = self.raster_table
        self.layersTable['raster']['commitButton'] = self.btn_commit_raster
        self.layersTable['raster']['discardButton'] = self.btn_discard_raster
        
        self.splitter.addWidget(self.left_container)
        
        # 4. Right Panel (Collapsible / Scrollable side actions panel)
        self.right_scroll = QScrollArea()
        self.right_scroll.setWidgetResizable(True)
        self.right_scroll.setStyleSheet("QScrollArea { border: 1px solid #dee2e6; background-color: #f8f9fa; }")
        
        self.right_container = QWidget()
        self.right_layout = QVBoxLayout(self.right_container)
        self.right_layout.setContentsMargins(10, 10, 10, 10)
        self.right_layout.setSpacing(12)
        
        # Initialize sections (stubs for task 1)
        self._init_right_panel_stubs()
        
        self.right_scroll.setWidget(self.right_container)
        self.splitter.addWidget(self.right_scroll)
        
        # Set stretch factor: left panel gets most space, right panel is fixed/smaller
        self.splitter.setStretchFactor(0, 3)
        self.splitter.setStretchFactor(1, 1)
        
        self._apply_qss_styles()

    def _init_right_panel_stubs(self):
        # Placeholder layout additions for now
        self.right_layout.addWidget(QLabel("Right Panel Controls"))
        
    def _apply_qss_styles(self):
        self.setStyleSheet("""
            QPushButton {
                background-color: #f1f3f5;
                color: #495057;
                border: 1px solid #ced4da;
                border-radius: 4px;
                padding: 6px 12px;
                font-family: "Microsoft YaHei", "Segoe UI", sans-serif;
                font-size: 12px;
                font-weight: 500;
            }
            QPushButton:hover {
                background-color: #e9ecef;
                color: #212529;
            }
            QPushButton:pressed {
                background-color: #dee2e6;
            }
            QPushButton:disabled {
                background-color: #e9ecef;
                color: #adb5bd;
            }
            QTableWidget {
                gridline-color: #dee2e6;
                border: 1px solid #dee2e6;
                font-size: 12px;
            }
            QTableWidget::item {
                padding: 5px;
            }
            QGroupBox {
                font-weight: bold;
                border: 1px solid #dee2e6;
                border-radius: 6px;
                margin-top: 10px;
                padding: 10px;
                background-color: #ffffff;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 0 5px;
                left: 10px;
            }
        """)
