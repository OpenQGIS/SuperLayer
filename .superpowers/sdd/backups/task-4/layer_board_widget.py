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
                    def setItem(self, r, c, item):
                        self.items[(r, c)] = item
                        if item is not None:
                            item._row = r
                            item._col = c
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
                        self._row = -1
                        self._col = -1
                        self._background = None
                    def setFlags(self, f): self._flags = f
                    def setData(self, role, val): self._data[role] = val
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
