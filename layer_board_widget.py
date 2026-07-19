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
        QScrollArea, QMessageBox, QFileDialog, QApplication, QGroupBox, QAbstractItemView
    )
except ImportError:
    try:
        from qtpy.QtCore import Qt, QCoreApplication, QSettings, QTranslator, QSize
        from qtpy.QtGui import QIcon, QTextCursor, QBrush, QColor
        from qtpy.QtWidgets import (
            QWidget, QVBoxLayout, QHBoxLayout, QSplitter, QTabWidget, QTableWidget,
            QTableWidgetItem, QPushButton, QLineEdit, QComboBox, QLabel, QTextEdit,
            QScrollArea, QMessageBox, QFileDialog, QApplication, QGroupBox, QAbstractItemView
        )
    except ImportError:
        try:
            from PySide2.QtCore import Qt, QCoreApplication, QSettings, QTranslator, QSize
            from PySide2.QtGui import QIcon, QTextCursor, QBrush, QColor
            from PySide2.QtWidgets import (
                QWidget, QVBoxLayout, QHBoxLayout, QSplitter, QTabWidget, QTableWidget,
                QTableWidgetItem, QPushButton, QLineEdit, QComboBox, QLabel, QTextEdit,
                QScrollArea, QMessageBox, QFileDialog, QApplication, QGroupBox, QAbstractItemView
            )
        except ImportError:
            try:
                from PySide6.QtCore import Qt, QCoreApplication, QSize
                from PySide6.QtGui import QAction, QIcon, QTextCursor, QBrush, QColor
                from PySide6.QtWidgets import (
                    QWidget, QVBoxLayout, QHBoxLayout, QSplitter, QTabWidget, QTableWidget,
                    QTableWidgetItem, QPushButton, QLineEdit, QComboBox, QLabel, QTextEdit,
                    QScrollArea, QMessageBox, QFileDialog, QApplication, QGroupBox, QAbstractItemView
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
                    WaitCursor = 3
                class QSize:
                    def __init__(self, w, h): pass
                class QIcon:
                    def __init__(self, *args): pass
                class QTextCursor:
                    End = 1
                    MoveAnchor = 2
                class QBrush:
                    def __init__(self, color):
                        self._color = color
                    def color(self):
                        return self._color
                class QColor:
                    def __init__(self, *args):
                        if len(args) == 1:
                            self._color_val = args[0]
                        else:
                            self._color_val = args
                    def name(self):
                        return str(self._color_val)
                class QWidget:
                    def __init__(self, parent=None):
                        self.layout = None
                        self._enabled = True
                    def setLayout(self, layout):
                        self.layout = layout
                    def setStyleSheet(self, style): pass
                    def setMinimumHeight(self, h): pass
                    def setMaximumWidth(self, w): pass
                    def setEnabled(self, e):
                        self._enabled = e
                    def isEnabled(self):
                        return self._enabled
                class QVBoxLayout:
                    def __init__(self, parent=None):
                        self.widgets = []
                    def addWidget(self, widget, *args):
                        self.widgets.append(widget)
                    def addLayout(self, layout, *args): pass
                    def setContentsMargins(self, *args): pass
                    def setSpacing(self, s): pass
                    def addStretch(self, *args): pass
                class QHBoxLayout(QVBoxLayout): pass
                class QSplitter(QWidget):
                    def __init__(self, *args):
                        super().__init__()
                        self.widgets = []
                    def addWidget(self, w):
                        self.widgets.append(w)
                    def setStretchFactor(self, idx, f): pass
                class _Signal:
                    def __init__(self):
                        self._slots = []
                    def connect(self, slot):
                        if slot not in self._slots:
                            self._slots.append(slot)
                    def disconnect(self, slot=None):
                        if slot is None:
                            self._slots = []
                        elif slot in self._slots:
                            self._slots.remove(slot)
                    def emit(self, *args):
                        for slot in list(self._slots):
                            slot(*args)
                class QTabWidget(QWidget):
                    def __init__(self, parent=None):
                        super().__init__()
                        self.tabs = []
                        self.currentChanged = _Signal()
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
                        self._selected_rows = []
                        self.itemChanged = _Signal()
                    def setRowCount(self, r): self.rows = r
                    def rowCount(self): return self.rows
                    def setColumnCount(self, c): self.cols = c
                    def columnCount(self): return self.cols
                    def setHorizontalHeaderLabels(self, labels): self.horizontal_labels = labels
                    def setItem(self, r, c, item):
                        self.items[(r, c)] = item
                        if item is not None:
                            item._row = r
                            item._col = c
                            item._table = self
                    def item(self, r, c): return self.items.get((r, c), None)
                    def removeRow(self, r): self.rows = max(0, self.rows - 1)
                    def clearSelection(self): pass
                    def setAlternatingRowColors(self, val): pass
                    def setSelectionBehavior(self, behavior): pass
                    def setSelectionMode(self, mode): pass
                    def selectionModel(self):
                        class MockSM:
                            def __init__(self, table):
                                self._table = table
                                self.selectionChanged = _Signal()
                            def selectedRows(self):
                                return self._table._selected_rows
                        return MockSM(self)
                class QTableWidgetItem:
                    def __init__(self, text=""):
                        self._text = text
                        self._data = {}
                        self._flags = 0
                        self._row = -1
                        self._col = -1
                        self._background = None
                        self._table = None
                    def setFlags(self, f): self._flags = f
                    def setData(self, role, val):
                        self._data[role] = val
                        if role == 2:  # Qt.EditRole
                            self._text = str(val)
                        if self._table and hasattr(self._table, 'itemChanged'):
                            self._table.itemChanged.emit(self)
                    def data(self, role): return self._data.get(role, self._text)
                    def setBackground(self, brush): self._background = brush
                    def background(self): return self._background
                    def setIcon(self, icon): pass
                    def setToolTip(self, text): pass
                    def row(self): return self._row
                    def column(self): return self._col
                class QPushButton(QWidget):
                    def __init__(self, text=""):
                        super().__init__()
                        self.text = text
                        self.clicked = _Signal()
                class QLineEdit(QWidget):
                    def __init__(self, parent=None):
                        super().__init__()
                        self._text = ""
                    def text(self): return self._text
                    def clear(self): self._text = ""
                    def setText(self, text): self._text = text
                class QComboBox(QWidget):
                    def __init__(self, parent=None):
                        super().__init__()
                        self._items = []
                        self._current_text = ""
                    def clear(self):
                        self._items = []
                        self._current_text = ""
                    def addItem(self, text, val=None):
                        self._items.append(text)
                        if not self._current_text:
                            self._current_text = text
                    def currentText(self): return self._current_text
                    def setCurrentText(self, text): self._current_text = text
                    def findText(self, text):
                        try:
                            return self._items.index(text)
                        except ValueError:
                            return -1
                    def setCurrentIndex(self, index):
                        if 0 <= index < len(self._items):
                            self._current_text = self._items[index]
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
                    def setReadOnly(self, r): pass
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
                class QAbstractItemView:
                    SelectRows = 1
                    ExtendedSelection = 3
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
        def crs(self): return QgsCoordinateReferenceSystem()
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
        def isValid(self): return True
    class QgsVectorDataProvider:
        CreateSpatialIndex = 1
    class QgsVectorLayer(QgsMapLayer):
        def isEditable(self): return False
        def isValid(self): return True
        def geometryType(self): return 0
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
        self.vector_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.vector_table.setSelectionMode(QAbstractItemView.ExtendedSelection)
        vector_layout.addWidget(self.vector_table)
        
        self.vector_buttons_layout = QHBoxLayout()
        self.btn_commit_vector = QPushButton(self.tr("保存修改 (Commit)"))
        self.btn_discard_vector = QPushButton(self.tr("放弃修改 (Discard)"))
        self.btn_commit_vector.clicked.connect(lambda: self.commitLayersChanges('vector'))
        self.btn_discard_vector.clicked.connect(lambda: self.discardLayersChanges('vector'))
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
        self.raster_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.raster_table.setSelectionMode(QAbstractItemView.ExtendedSelection)
        raster_layout.addWidget(self.raster_table)
        
        self.raster_buttons_layout = QHBoxLayout()
        self.btn_commit_raster = QPushButton(self.tr("保存修改 (Commit)"))
        self.btn_discard_raster = QPushButton(self.tr("放弃修改 (Discard)"))
        self.btn_commit_raster.clicked.connect(lambda: self.commitLayersChanges('raster'))
        self.btn_discard_raster.clicked.connect(lambda: self.discardLayersChanges('raster'))
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
        
        # 4. Right Panel (Direct widget, not wrapped in QScrollArea to prevent child QTabWidget collapsing)
        self.right_container = QWidget()
        self.right_container.setMaximumWidth(360)
        self.right_layout = QVBoxLayout(self.right_container)
        self.right_layout.setContentsMargins(10, 10, 10, 10)
        self.right_layout.setSpacing(12)
        
        # Initialize sections (stubs for task 1)
        self._init_right_panel_stubs()
        
        self.splitter.addWidget(self.right_container)
        
        # Set stretch factor: left panel gets most space, right panel is fixed/smaller
        self.splitter.setStretchFactor(0, 3)
        self.splitter.setStretchFactor(1, 1)
        
        self._apply_qss_styles()

    def _init_right_panel_stubs(self):
        # Create QTabWidget for right panel controls
        self.right_tab_widget = QTabWidget()
        self.right_layout.addWidget(self.right_tab_widget)
        
        # --- TAB 1: Actions on Layers (图层操作) ---
        tab_actions = QWidget()
        actions_layout = QVBoxLayout(tab_actions)
        actions_layout.setContentsMargins(8, 8, 8, 8)
        actions_layout.setSpacing(10)
        
        # Batch updates (inside group box)
        group_batch = QGroupBox(self.tr("批量更新 (Batch Update)"))
        batch_layout = QVBoxLayout(group_batch)
        batch_layout.setSpacing(8)
        
        # Row 1: CRS and Encoding side-by-side
        row1_layout = QHBoxLayout()
        row1_layout.setSpacing(12)
        
        # CRS Left Column
        crs_widget = QWidget()
        crs_v_layout = QVBoxLayout(crs_widget)
        crs_v_layout.setContentsMargins(0, 0, 0, 0)
        crs_v_layout.setSpacing(4)
        crs_lbl = QLabel(self.tr("设置 CRS:"))
        crs_v_layout.addWidget(crs_lbl)
        crs_row = QHBoxLayout()
        self.inCrs = QLineEdit()
        self.btDefineProjection = QPushButton("...")
        self.btApplyCrs = QPushButton(self.tr("应用"))
        crs_row.addWidget(self.inCrs, 1)
        crs_row.addWidget(self.btDefineProjection)
        crs_row.addWidget(self.btApplyCrs)
        crs_v_layout.addLayout(crs_row)
        row1_layout.addWidget(crs_widget, 1)
        
        # Encoding Right Column
        enc_widget = QWidget()
        enc_v_layout = QVBoxLayout(enc_widget)
        enc_v_layout.setContentsMargins(0, 0, 0, 0)
        enc_v_layout.setSpacing(4)
        self.encodingLabel = QLabel(self.tr("设置编码 (仅矢量):"))
        enc_v_layout.addWidget(self.encodingLabel)
        enc_row = QHBoxLayout()
        self.inEncodingList = QComboBox()
        self.populateAvailableEncodingList()
        self.btApplyEncoding = QPushButton(self.tr("应用"))
        enc_row.addWidget(self.inEncodingList, 1)
        enc_row.addWidget(self.btApplyEncoding)
        enc_v_layout.addLayout(enc_row)
        row1_layout.addWidget(enc_widget, 1)
        
        batch_layout.addLayout(row1_layout)
        
        # Row 2: Max Scale and Min Scale side-by-side
        row2_layout = QHBoxLayout()
        row2_layout.setSpacing(12)
        
        # Max Scale Left Column
        max_scale_widget = QWidget()
        max_scale_v_layout = QVBoxLayout(max_scale_widget)
        max_scale_v_layout.setContentsMargins(0, 0, 0, 0)
        max_scale_v_layout.setSpacing(4)
        max_scale_lbl = QLabel(self.tr("设置最大比例尺:"))
        max_scale_v_layout.addWidget(max_scale_lbl)
        max_row = QHBoxLayout()
        self.inMaxScale = QLineEdit()
        self.btApplyMaxScale = QPushButton(self.tr("应用"))
        max_row.addWidget(self.inMaxScale, 1)
        max_row.addWidget(self.btApplyMaxScale)
        max_scale_v_layout.addLayout(max_row)
        row2_layout.addWidget(max_scale_widget, 1)
        
        # Min Scale Right Column
        min_scale_widget = QWidget()
        min_scale_v_layout = QVBoxLayout(min_scale_widget)
        min_scale_v_layout.setContentsMargins(0, 0, 0, 0)
        min_scale_v_layout.setSpacing(4)
        min_scale_lbl = QLabel(self.tr("设置最小比例尺:"))
        min_scale_v_layout.addWidget(min_scale_lbl)
        min_row = QHBoxLayout()
        self.inMinScale = QLineEdit()
        self.btApplyMinScale = QPushButton(self.tr("应用"))
        min_row.addWidget(self.inMinScale, 1)
        min_row.addWidget(self.btApplyMinScale)
        min_scale_v_layout.addLayout(min_row)
        row2_layout.addWidget(min_scale_widget, 1)
        
        batch_layout.addLayout(row2_layout)
        actions_layout.addWidget(group_batch)
        
        # 2. Actions Group Box
        group_actions = QGroupBox(self.tr("批量操作 (Actions)"))
        act_layout = QVBoxLayout(group_actions)
        act_layout.setSpacing(8)
        
        # Row 4: Save Default Style and Create Spatial Index
        row4_layout = QHBoxLayout()
        row4_layout.setSpacing(12)
        self.btSaveStyleAsDefault = QPushButton(self.tr("保存样式为默认"))
        self.btCreateSpatialIndex = QPushButton(self.tr("创建空间索引 (矢量)"))
        row4_layout.addWidget(self.btSaveStyleAsDefault, 1)
        row4_layout.addWidget(self.btCreateSpatialIndex, 1)
        act_layout.addLayout(row4_layout)
        
        # Row 5: Remove Layer and Clear Ghost Layers
        row5_layout = QHBoxLayout()
        row5_layout.setSpacing(12)
        self.btRemoveLayer = QPushButton(self.tr("从项目移除图层"))
        self.btRemoveGhostLayers = QPushButton(self.tr("清除幽灵图层"))
        row5_layout.addWidget(self.btRemoveLayer, 1)
        row5_layout.addWidget(self.btRemoveGhostLayers, 1)
        act_layout.addLayout(row5_layout)
        
        actions_layout.addWidget(group_actions)
        actions_layout.addStretch(1)
        
        self.right_tab_widget.addTab(tab_actions, self.tr("图层操作"))
        
        # --- TAB 2: Layer Style (图层样式) ---
        tab_style = QWidget()
        style_layout = QVBoxLayout(tab_style)
        style_layout.setContentsMargins(8, 8, 8, 8)
        style_layout.setSpacing(10)
        
        self.styleScrollArea = QScrollArea()
        self.styleScrollArea.setWidgetResizable(True)
        self.styleScrollArea.setMinimumHeight(150)
        self.btApplyStyle = QPushButton(self.tr("应用样式"))
        style_layout.addWidget(self.styleScrollArea, 1)
        style_layout.addWidget(self.btApplyStyle)
        
        self.right_tab_widget.addTab(tab_style, self.tr("图层样式"))
        
        # --- TAB 3: Export (数据导出) ---
        tab_export = QWidget()
        export_layout = QVBoxLayout(tab_export)
        export_layout.setContentsMargins(8, 8, 8, 8)
        export_layout.setSpacing(10)
        
        group_export = QGroupBox(self.tr("数据导出 (Export)"))
        exp_box_layout = QVBoxLayout(group_export)
        self.btExportCsv = QPushButton(self.tr("导出当前看板为 CSV"))
        exp_box_layout.addWidget(self.btExportCsv)
        export_layout.addWidget(group_export)
        export_layout.addStretch(1)
        
        self.right_tab_widget.addTab(tab_export, self.tr("数据导出"))
        
        # --- TAB 4: Log (操作日志) ---
        tab_log = QWidget()
        log_layout = QVBoxLayout(tab_log)
        log_layout.setContentsMargins(8, 8, 8, 8)
        log_layout.setSpacing(10)
        
        self.txtLog = QTextEdit()
        self.txtLog.setReadOnly(True)
        self.txtLog.setMinimumHeight(150)
        self.btClearLog = QPushButton(self.tr("清空日志"))
        log_layout.addWidget(self.txtLog, 1)
        log_layout.addWidget(self.btClearLog)
        
        self.right_tab_widget.addTab(tab_log, self.tr("操作日志"))
        
        self._setup_connections()

    def _setup_connections(self):
        # Selection signals for style
        self.vector_table.selectionModel().selectionChanged.connect(partial(self.setSelectedLayerStyleWidget, 'vector'))
        self.raster_table.selectionModel().selectionChanged.connect(partial(self.setSelectedLayerStyleWidget, 'raster'))
        self.tab_widget.currentChanged.connect(self.onTabChanged)
        
        self.btDefineProjection.clicked.connect(self.chooseProjection)
        self.btClearLog.clicked.connect(self.clearLog)
        self.btApplyStyle.clicked.connect(self.applyStyle)
        self.btExportCsv.clicked.connect(self.exportToCsv)
        
        # Bulk updates
        self.btApplyCrs.clicked.connect(lambda: self.applyPropertyOnSelectedLayers('crs'))
        self.btApplyMaxScale.clicked.connect(lambda: self.applyPropertyOnSelectedLayers('maxScale'))
        self.btApplyMinScale.clicked.connect(lambda: self.applyPropertyOnSelectedLayers('minScale'))
        self.btApplyEncoding.clicked.connect(lambda: self.applyPropertyOnSelectedLayers('encoding'))
        
        # Batch actions
        self.btSaveStyleAsDefault.clicked.connect(lambda: self.performActionOnSelectedLayers('saveStyleAsDefault'))
        self.btCreateSpatialIndex.clicked.connect(lambda: self.performActionOnSelectedLayers('createSpatialIndex'))
        self.btRemoveLayer.clicked.connect(lambda: self.performActionOnSelectedLayers('removeLayer'))
        self.btRemoveGhostLayers.clicked.connect(self.removeGhostLayers)
        
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

    def populateLayerTable(self, layerType):
        lt = self.layersTable[layerType]
        table = lt['tableWidget']
        
        self.layerBoardChangedData[layerType] = {}
        
        try:
            table.itemChanged.disconnect()
        except Exception:
            pass
            
        attributes = self.layersTable['generic']['attributes'] + lt['attributes']
        self.layersAttributes[layerType] = attributes
        
        self.layerBoardData[layerType] = []
        headerData = [a['key'] for a in attributes]
        self.layerBoardData[layerType].append(headerData)
        
        # Empty table
        table.setRowCount(0)
        
        # Set columns
        columnsLabels = [a['label'] for a in attributes]
        colCount = len(attributes)
        table.setColumnCount(colCount)
        table.setHorizontalHeaderLabels(columnsLabels)
        
        lr = QgsProject.instance()
        for lid, layer in lr.mapLayers().items():
            if layerType == 'vector' and layer.type() != QgsMapLayer.VectorLayer:
                continue
            if layerType == 'raster' and layer.type() != QgsMapLayer.RasterLayer:
                continue
                
            self.layerBoardChangedData[layerType][lid] = {}
            lineData = []
            
            twRowCount = table.rowCount()
            table.setRowCount(twRowCount + 1)
            
            i = 0
            for attr in attributes:
                newItem = QTableWidgetItem()
                newItem.setToolTip(layer.name())
                
                # Check spatial only for non-spatial layers
                if layerType == 'vector' and not layer.isSpatial() and attr.get('spatial_only'):
                    newItem.setFlags(Qt.NoItemFlags)
                elif attr.get('editable'):
                    newItem.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEditable | Qt.ItemIsEnabled)
                else:
                    newItem.setFlags(Qt.ItemIsSelectable)
                    
                if layerType == 'vector' and not layer.isSpatial() and attr.get('spatial_only'):
                    value = None
                else:
                    value = self.getLayerProperty(layer, attr['key'])
                newItem.setData(Qt.EditRole, value)
                lineData.append(value)
                
                if attr['key'] == 'name':
                    icon = QgsMapLayerModel.iconForLayer(layer)
                    newItem.setIcon(icon)
                    
                table.setItem(twRowCount, i, newItem)
                i += 1
                
            self.layerBoardData[layerType].append(lineData)
            
        # Hook change listener
        slot = partial(self.onItemChanged, layerType)
        table.itemChanged.connect(slot)

    def getLayerProperty(self, layer, prop):
        if prop == 'id':
            return layer.id()
        if prop == 'name':
            return layer.name()
        elif prop == 'title':
            return layer.title()
        elif prop == 'abstract':
            return layer.abstract()
        elif prop == 'shortname':
            return layer.shortName()
        elif prop == 'ghost':
            return str(self.is_ghost_layer(layer))
        elif prop == 'crs':
            return layer.crs().authid()
        elif prop == 'extent':
            return layer.extent().toString(2)
        elif prop == 'maxScale':
            try:
                return int(layer.maximumScale())
            except Exception:
                return 100000000
        elif prop == 'minScale':
            try:
                return int(layer.minimumScale())
            except Exception:
                return 0
        # vector
        elif prop == 'labelsEnabled':
            if hasattr(layer, 'labelsEnabled'):
                return layer.labelsEnabled()
            elif hasattr(layer, 'hasLabelsEnabled'):
                return layer.hasLabelsEnabled()
            return False
        elif prop == 'featureCount':
            return layer.featureCount()
        elif prop == 'source|uri':
            return layer.dataProvider().name() + "|" + layer.dataProvider().dataSourceUri().split('|')[0]
        elif prop == 'encoding':
            if hasattr(layer.dataProvider(), 'encoding'):
                return layer.dataProvider().encoding()
            return "UTF-8"
        elif prop == 'styles_in_db':
            if hasattr(layer, 'listStylesInDatabase'):
                nb, _, _, _, _ = layer.listStylesInDatabase()
                if nb < 0:
                    nb = 0
                return nb
            return 0
        # raster
        elif prop == 'width':
            return int(layer.width()) if hasattr(layer, 'width') else 0
        elif prop == 'height':
            return int(layer.height()) if hasattr(layer, 'height') else 0
        elif prop == 'rasterUnitsPerPixelX':
            return int(layer.rasterUnitsPerPixelX()) if hasattr(layer, 'rasterUnitsPerPixelX') else 0
        elif prop == 'rasterUnitsPerPixelY':
            return int(layer.rasterUnitsPerPixelY()) if hasattr(layer, 'rasterUnitsPerPixelY') else 0
        elif prop == 'uri':
            return layer.dataProvider().dataSourceUri().split('|')[0]
        return None

    def is_ghost_layer(self, layer):
        project = QgsProject.instance()
        # Mock layerTreeRoot if needed
        root = getattr(project, 'layerTreeRoot', lambda: None)()
        if root:
            count = QgsLayerTreeUtils.countMapLayerInTree(root, layer)
            return count == 0
        return False
        
    def onItemChanged(self, layerType, item):
        table = self.layersTable[layerType]['tableWidget']
        
        row = item.row()
        col = item.column()
        
        table.clearSelection()
        
        layerId = table.item(row, 0).data(Qt.EditRole)
        lr = QgsProject.instance()
        layer = lr.mapLayer(layerId)
        if not layer:
            return
            
        prop = self.layersAttributes[layerType][col]['key']
        data = table.item(row, col).data(Qt.EditRole)
        
        # Check URI validation
        if prop == 'source|uri' and not self.newDatasourceIsValid(layer, data):
            table.itemChanged.disconnect()
            item.setData(Qt.EditRole, self.getLayerProperty(layer, 'source|uri'))
            slot = partial(self.onItemChanged, layerType)
            table.itemChanged.connect(slot)
            return
            
        # Check encoding
        if prop == 'encoding' and data not in layer.dataProvider().availableEncodings():
            table.itemChanged.disconnect()
            item.setData(Qt.EditRole, self.getLayerProperty(layer, 'encoding'))
            slot = partial(self.onItemChanged, layerType)
            table.itemChanged.connect(slot)
            return
            
        # Check shortname
        if prop == 'shortname':
            table.itemChanged.disconnect()
            newshortname = re.sub('[^A-Za-z0-9\\.-]', '_', data)
            item.setData(Qt.EditRole, newshortname)
            slot = partial(self.onItemChanged, layerType)
            table.itemChanged.connect(slot)
            data = newshortname
            
        if layerId not in self.layerBoardChangedData[layerType]:
            self.layerBoardChangedData[layerType][layerId] = {}
        self.layerBoardChangedData[layerType][layerId][prop] = data
        
        # Change cell color
        try:
            item.setBackground(QBrush(QColor(Qt.yellow)))
        except Exception:
            pass

    def splitSource(self, source):
        if "|" in source:
            datasourceType = source.split("|")[0]
            uri = source.split("|")[1].replace('\\', '/')
        else:
            datasourceType = None
            uri = source.replace('\\', '/')
        return (datasourceType, uri)

    def newDatasourceIsValid(self, layer, newDS):
        # True for CLI mock environment testing
        if not hasattr(layer, 'geometryType'):
            return True
        ds, uri = self.splitSource(newDS)
        if not ds:
            ds = layer.dataProvider().name()
        nlayer = QgsVectorLayer(uri, "probe", ds)
        if not nlayer.isValid():
            if hasattr(self.iface, 'messageBar'):
                self.iface.messageBar().pushMessage("Error", "incorrect source|uri string: " + newDS, level=Qgis.Critical, duration=4)
            return False
        if nlayer.geometryType() != layer.geometryType():
            if hasattr(self.iface, 'messageBar'):
                self.iface.messageBar().pushMessage("Error", "geometry type mismatch: " + newDS, level=Qgis.Critical, duration=4)
            return False
        return True

    def commitLayersChanges(self, layerType='vector'):
        lr = QgsProject.instance()
        self.updateLog('')
        self.updateLog('###############')
        self.updateLog(datetime.datetime.now().strftime("%Y-%m-%d %H:%M"))
        self.updateLog(self.tr('Layer type: ') + layerType)
        self.updateLog('###############')
        
        for layerId, layerData in list(self.layerBoardChangedData[layerType].items()):
            if not layerData:
                continue
                
            layer = lr.mapLayer(layerId)
            if not layer:
                self.layerBoardChangedData[layerType][layerId] = {}
                continue
                
            self.updateLog('')
            self.updateLog('<b>%s</b> ( %s ):' % (layer.name(), layerId))
            
            for prop, data in list(layerData.items()):
                if data or data == '':
                    self.setLayerProperty(layerType, [layer], prop, data, repopulate=False)
                    self.updateLog('* %s -> %s' % (prop, data))
                    
        # Mark project dirty
        lr.setDirty(True)
        self.populateLayerTable(layerType)

    def discardLayersChanges(self, layerType='vector'):
        self.populateLayerTable(layerType)

    def setLayerProperty(self, layerType, layers, prop, data, repopulate=True):
        for layer in layers:
            if not layer:
                continue
            if prop == 'name':
                layer.setName(str(data))
            elif prop == 'title':
                if hasattr(layer, 'setTitle'): layer.setTitle(data)
            elif prop == 'abstract':
                if hasattr(layer, 'setAbstract'): layer.setAbstract(data)
            elif prop == 'shortname':
                newshortname = re.sub('[^A-Za-z0-9\\.-]', '_', data)
                if hasattr(layer, 'setShortName'): layer.setShortName(newshortname)
            elif prop == 'maxScale':
                try:
                    val = float(data)
                    layer.toggleScaleBasedVisibility(True)
                    layer.setMaximumScale(val)
                    layer.triggerRepaint()
                except ValueError:
                    pass
            elif prop == 'minScale':
                try:
                    val = float(data)
                    layer.toggleScaleBasedVisibility(True)
                    layer.setMinimumScale(val)
                    layer.triggerRepaint()
                except ValueError:
                    pass
            elif prop == 'crs':
                qcrs = QgsCoordinateReferenceSystem()
                qcrs.createFromOgcWmsCrs(data)
                if qcrs.isValid():
                    layer.setCrs(qcrs)
                    layer.triggerRepaint()
            elif prop == 'source|uri':
                self.setDataSource(layer, data)
            elif prop == 'encoding':
                if hasattr(layer, 'setProviderEncoding'):
                    layer.setProviderEncoding(data)
                    
        if repopulate:
            self.populateLayerTable(layerType)

    def setDataSource(self, layer, newSourceUri):
        # Verify write XML functionality (if present)
        if not hasattr(layer, 'writeLayerXML'):
            return
        try:
            from qgis.PyQt.QtXml import QDomDocument, QDomElement
        except ImportError:
            # Fallback mock for unit testing environment
            class QDomDocument:
                def __init__(self, name): pass
                def createElement(self, name):
                    class MockElement:
                        def __init__(self, name):
                            self._name = name
                            self._children = []
                            self._value = ""
                        def firstChildElement(self, name):
                            el = MockElement(name)
                            self._children.append(el)
                            return el
                        def firstChild(self):
                            class MockNode:
                                def __init__(self, parent):
                                    self._parent = parent
                                def setNodeValue(self, val):
                                    self._parent._value = val
                            return MockNode(self)
                        def appendChild(self, el):
                            self._children.append(el)
                    return MockElement(name)
                def appendChild(self, el): pass
            class QDomElement: pass

        newDS, newUri = self.splitSource(newSourceUri)
        newDatasourceType = newDS or layer.dataProvider().name()
        
        XMLDocument = QDomDocument("style")
        XMLMapLayers = XMLDocument.createElement("maplayers")
        XMLMapLayer = XMLDocument.createElement("maplayer")
        layer.writeLayerXML(XMLMapLayer, XMLDocument)
        
        XMLMapLayer.firstChildElement("datasource").firstChild().setNodeValue(newUri)
        XMLMapLayer.firstChildElement("provider").firstChild().setNodeValue(newDatasourceType)
        XMLMapLayers.appendChild(XMLMapLayer)
        XMLDocument.appendChild(XMLMapLayers)
        layer.readLayerXML(XMLMapLayer)
        if hasattr(layer, 'reload'): layer.reload()
        if hasattr(self.iface, 'actionDraw'): self.iface.actionDraw().trigger()
        if hasattr(self.iface, 'mapCanvas'): self.iface.mapCanvas().refresh()

    def getActiveLayerType(self):
        return 'vector' if self.tab_widget.currentIndex() == 0 else 'raster'

    def chooseProjection(self):
        try:
            from qgis.gui import QgsProjectionSelectionDialog
            
            # Anchor to QGIS main window
            projSelector = QgsProjectionSelectionDialog(self.iface.mainWindow())
            projSelector.setWindowTitle(self.tr("设置CRS"))
            
            init_crs = None
            current_crs_text = self.inCrs.text().strip()
            if current_crs_text:
                crs_candidate = QgsCoordinateReferenceSystem(current_crs_text)
                if crs_candidate.isValid():
                    init_crs = crs_candidate
            
            if not init_crs:
                # Fallback to project CRS so that the map preview is active immediately
                project_crs = QgsProject.instance().crs()
                if project_crs.isValid():
                    init_crs = project_crs
            
            if init_crs:
                projSelector.setCrs(init_crs)
                
            if projSelector.exec_():
                crs = projSelector.crs()
                self.inCrs.setText(crs.authid())
        except Exception:
            pass

    def applyPropertyOnSelectedLayers(self, key):
        layerType = self.getActiveLayerType()
        table = self.layersTable[layerType]['tableWidget']
        
        # Value
        value = None
        if key == 'crs': value = self.inCrs.text()
        elif key == 'maxScale': value = self.inMaxScale.text()
        elif key == 'minScale': value = self.inMinScale.text()
        elif key == 'encoding': value = self.inEncodingList.currentText()
        
        if not value:
            return
            
        sm = table.selectionModel()
        lines = sm.selectedRows()
        if not lines:
            return
            
        col = next(index for (index, d) in enumerate(self.layersAttributes[layerType]) if d['key'] == key)
        for index in lines:
            row = index.row()
            item = table.item(row, col)
            item.setData(Qt.EditRole, value)

    def performActionOnSelectedLayers(self, key):
        layerType = self.getActiveLayerType()
        table = self.layersTable[layerType]['tableWidget']
        
        sm = table.selectionModel()
        lines = sm.selectedRows()
        if not lines:
            return
            
        lines = sorted(lines, key=lambda idx: idx.row(), reverse=True)
        lr = QgsProject.instance()
        for index in lines:
            row = index.row()
            layerId = table.item(row, 0).data(Qt.EditRole)
            layer = lr.mapLayer(layerId)
            if not layer:
                continue
                
            if key == 'saveStyleAsDefault':
                if layer.providerType() == 'postgres':
                    if hasattr(layer, 'saveStyleToDatabase'):
                        layer.saveStyleToDatabase(layer.name(), '', True, None, '')
                else:
                    if hasattr(layer, 'saveDefaultStyle'):
                        layer.saveDefaultStyle()
                        
            elif key == 'createSpatialIndex' and layer.type() == QgsMapLayer.VectorLayer:
                provider = layer.dataProvider()
                if hasattr(provider, 'capabilities') and (provider.capabilities() & QgsVectorDataProvider.CreateSpatialIndex):
                    provider.createSpatialIndex()
                    
            elif key == 'removeLayer':
                lr.removeMapLayer(layer.id())
                table.removeRow(row)
                lr.setDirty(True)

    def removeGhostLayers(self):
        project = QgsProject.instance()
        for layer in list(project.mapLayers().values()):
            if self.is_ghost_layer(layer):
                project.removeMapLayer(layer.id())
        project.setDirty(True)
        self.populateLayerTable('vector')
        self.populateLayerTable('raster')

    def onTabChanged(self):
        layerType = self.getActiveLayerType()
        isEnabled = layerType == 'vector'
        self.encodingLabel.setEnabled(isEnabled)
        self.inEncodingList.setEnabled(isEnabled)
        self.btApplyEncoding.setEnabled(isEnabled)
        self.btCreateSpatialIndex.setEnabled(isEnabled)

    def setSelectedLayerStyleWidget(self, layerType, selected=None, unselected=None):
        table = self.layersTable[layerType]['tableWidget']
        sm = table.selectionModel()
        lines = sm.selectedRows()
        
        self.styleWidget = None
        self.styleLayer = None
        
        # Clear container
        self.styleScrollArea.setWidget(QWidget())
        
        if len(lines) != 1:
            self.inCrs.clear()
            self.inMaxScale.clear()
            self.inMinScale.clear()
            self.inEncodingList.setCurrentIndex(0)
            return
            
        row = lines[0].row()
        layerId = table.item(row, 0).data(Qt.EditRole)
        layer = QgsProject.instance().mapLayer(layerId)
        if not layer:
            return
            
        self.styleLayer = layer
        
        # Populate the batch update fields for single layer selection
        crs_val = self.getLayerProperty(layer, 'crs')
        max_scale_val = self.getLayerProperty(layer, 'maxScale')
        min_scale_val = self.getLayerProperty(layer, 'minScale')
        encoding_val = self.getLayerProperty(layer, 'encoding')
        
        self.inCrs.setText(str(crs_val) if crs_val is not None else "")
        self.inMaxScale.setText(str(max_scale_val) if max_scale_val is not None and max_scale_val != 100000000 else "")
        self.inMinScale.setText(str(min_scale_val) if min_scale_val is not None and min_scale_val != 0 else "")
        
        if encoding_val:
            idx = self.inEncodingList.findText(encoding_val)
            if idx >= 0:
                self.inEncodingList.setCurrentIndex(idx)
            else:
                self.inEncodingList.setCurrentText(encoding_val)
        else:
            self.inEncodingList.setCurrentIndex(0)
            
        # Dynamic style Dialog loading (only Vector layers supported by QGIS UI)
        if layer.type() == QgsMapLayer.VectorLayer:
            try:
                from qgis.gui import QgsRendererPropertiesDialog
                # Check for standard styling class properties
                w = QgsRendererPropertiesDialog(layer, QgsStyle.defaultStyle(), True)
                self.styleWidget = w
                self.styleScrollArea.setWidget(w)
            except Exception:
                # Basic Label fallback for mock environments
                lbl = QLabel("Symbology properties (Mocked)")
                self.styleWidget = lbl
                self.styleScrollArea.setWidget(lbl)

    def applyStyle(self):
        w = self.styleWidget
        layer = self.styleLayer
        if not w or not layer:
            return
            
        if hasattr(w, 'apply'):
            w.apply()
        if hasattr(layer, "setCacheImage"):
            layer.setCacheImage(None)
        layer.triggerRepaint()

    def clearLog(self):
        self.txtLog.clear()

    def updateLog(self, msg):
        prefix = '<span style="font-weight:normal;">'
        suffix = '</span>'
        self.txtLog.append('%s %s %s' % (prefix, msg, suffix))
        c = self.txtLog.textCursor()
        c.movePosition(QTextCursor.End, QTextCursor.MoveAnchor)
        self.txtLog.setTextCursor(c)

    def exportToCsv(self):
        path, _ = QFileDialog.getSaveFileName(self, self.tr("导出数据"), '', 'CSV (*.csv)')
        if not path:
            return
            
        layerType = self.getActiveLayerType()
        data = self.layerBoardData[layerType]
        
        try:
            QApplication.setOverrideCursor(Qt.WaitCursor)
            with open(path, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(
                    csvfile, delimiter=self.csvDelimiter, quotechar=self.csvQuotechar, quoting=self.csvQuoting
                )
                writer.writerows(data)
            self.updateLog(self.tr("数据已成功导出到 CSV！"))
        except Exception as e:
            self.updateLog(self.tr("导出错误: ") + str(e))
        finally:
            QApplication.restoreOverrideCursor()
            
    def populateAvailableEncodingList(self):
        cb = self.inEncodingList
        cb.clear()
        cb.addItem('---')
        try:
            vl = QgsVectorLayer("Point?crs=epsg:4326", "temp", "memory")
            enclist = vl.dataProvider().availableEncodings()
            for enc in enclist:
                cb.addItem(enc)
        except Exception:
            # Fallback mock encodings
            cb.addItem("UTF-8")
            cb.addItem("GBK")
            cb.addItem("ISO-8859-1")
