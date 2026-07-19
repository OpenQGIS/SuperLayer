# Layer Board Migration Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Integrate the LayerBoard plugin tabular editing and bulk actions features into TreeMap_Layer_Manager as a new page called "属性看板" with matching styling and full unit tests.

**Architecture:** A new python file `layer_board_widget.py` defines the `LayerBoardWidget` class containing the Splitter layout (left side tabs with tables, right side side-panel scroll area). `dock_widget.py` imports this and registers it as a page in `stacked_widget` toggled by toolbar.

**Tech Stack:** PyQGIS (QgsProject, QgsMapLayer, QgsCoordinateReferenceSystem, QgsStyle, QgsLayerTreeUtils, etc.), Qt (PyQt5, PySide2, PySide6 compatibility fallback).

## Global Constraints
- Naming rules: Follow PEP8. Keep methods in `LayerBoardWidget` matching the original where possible for easy diff comparison.
- Stylings: Layout borders, widgets background, buttons must match `TreeMapDockWidget` style formatting (flat, light-grey borders, alternate row colors).
- Robust imports: All Qt and QGIS imports must have standard try/except fallback blocks to support mocked environments.

---

### Task 1: Qt fallbacks and basic layout initialization of LayerBoardWidget

**Files:**
- Create: `layer_board_widget.py`
- Create: `test_layer_board.py`

**Interfaces:**
- Consumes: None
- Produces: Class `LayerBoardWidget(QWidget)` with layout containing `QSplitter`, `QTabWidget` (vector/raster tabs), and side-panel scroll area.

- [ ] **Step 1: Write the layer_board_widget.py with layout structure**

Write the basic widget class and UI structure in `layer_board_widget.py`:
```python
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
```

- [ ] **Step 2: Create unit test file test_layer_board.py**

Write initialization checks in `test_layer_board.py`:
```python
import unittest
from unittest.mock import MagicMock, patch
import sys
import os

# Include directory in sys.path
sys.path.insert(0, os.path.dirname(__file__))

import layer_board_widget
from layer_board_widget import LayerBoardWidget

class TestLayerBoardWidget(unittest.TestCase):
    def setUp(self):
        self.iface = MagicMock()
        
    def test_widget_init(self):
        widget = LayerBoardWidget(self.iface)
        self.assertEqual(widget.iface, self.iface)
        self.assertIsNotNone(widget.tab_widget)
        self.assertIsNotNone(widget.vector_table)
        self.assertIsNotNone(widget.raster_table)
        
if __name__ == '__main__':
    unittest.main()
```

- [ ] **Step 3: Run the unit test to verify it passes**

Run: `python -m unittest test_layer_board.py`
Expected output:
```text
.
----------------------------------------------------------------------
Ran 1 test in 0.002s

OK
```

- [ ] **Step 4: Commit**

```bash
git add layer_board_widget.py test_layer_board.py
git commit -m "feat: add basic LayerBoardWidget UI setup and tests"
```

---

### Task 2: Data Population & Read Properties

**Files:**
- Modify: `layer_board_widget.py`
- Modify: `test_layer_board.py`

**Interfaces:**
- Consumes: `LayerBoardWidget(QWidget)` from Task 1.
- Produces: `populateLayerTable(layerType)` populating the tables, and `getLayerProperty(layer, prop)` returns current value.

- [ ] **Step 1: Implement getLayerProperty and populateLayerTable**

Add the methods in `LayerBoardWidget` (replacing the stubs):
```python
    # Add these methods inside LayerBoardWidget class in layer_board_widget.py

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
        pass # Stub for Task 3
```

- [ ] **Step 2: Add tests for layer loading in test_layer_board.py**

Modify `test_layer_board.py` to mock layers and test population:
```python
    # Add inside TestLayerBoardWidget in test_layer_board.py

    @patch('layer_board_widget.QgsProject.instance')
    def test_populate_tables(self, mock_project_inst):
        # Mock vector layer
        mock_vlayer = MagicMock()
        mock_vlayer.type.return_value = 0 # Vector
        mock_vlayer.id.return_value = "v1"
        mock_vlayer.name.return_value = "VectorLayer"
        mock_vlayer.isSpatial.return_value = True
        mock_vlayer.dataProvider().name.return_value = "ogr"
        mock_vlayer.dataProvider().dataSourceUri.return_value = "v_uri"
        
        # Mock raster layer
        mock_rlayer = MagicMock()
        mock_rlayer.type.return_value = 1 # Raster
        mock_rlayer.id.return_value = "r1"
        mock_rlayer.name.return_value = "RasterLayer"
        mock_rlayer.dataProvider().dataSourceUri.return_value = "r_uri"
        
        mock_proj = MagicMock()
        mock_proj.mapLayers.return_value = {"v1": mock_vlayer, "r1": mock_rlayer}
        mock_proj.mapLayer.side_effect = lambda lid: mock_vlayer if lid == "v1" else mock_rlayer
        mock_project_inst.return_value = mock_proj
        
        widget = LayerBoardWidget(self.iface)
        widget.populateLayerTable('vector')
        widget.populateLayerTable('raster')
        
        self.assertEqual(widget.vector_table.rowCount(), 1)
        self.assertEqual(widget.raster_table.rowCount(), 1)
        
        # Check name column value (generic index 1 is name)
        self.assertEqual(widget.vector_table.item(0, 1).data(Qt.EditRole), "VectorLayer")
        self.assertEqual(widget.raster_table.item(0, 1).data(Qt.EditRole), "RasterLayer")
```

- [ ] **Step 3: Run test_layer_board.py**

Run: `python -m unittest test_layer_board.py`
Expected output: PASS

- [ ] **Step 4: Commit**

```bash
git add layer_board_widget.py test_layer_board.py
git commit -m "feat: implement getLayerProperty and populateLayerTable with tests"
```

---

### Task 3: Cell Editing, Validation, and Yellow Highlighting

**Files:**
- Modify: `layer_board_widget.py`
- Modify: `test_layer_board.py`

**Interfaces:**
- Consumes: `LayerBoardWidget` from Task 2.
- Produces: `onItemChanged(layerType, item)` checking validators (`newDatasourceIsValid`), highlighting changed item yellow.

- [ ] **Step 1: Implement onItemChanged and validators in LayerBoardWidget**

Implement the logic in `layer_board_widget.py`:
```python
    # Add or update inside LayerBoardWidget in layer_board_widget.py

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
```

- [ ] **Step 2: Add validation and change tests in test_layer_board.py**

Add unit tests:
```python
    # Add inside TestLayerBoardWidget in test_layer_board.py

    @patch('layer_board_widget.QgsProject.instance')
    def test_on_item_changed(self, mock_project_inst):
        mock_vlayer = MagicMock()
        mock_vlayer.type.return_value = 0
        mock_vlayer.id.return_value = "v1"
        mock_vlayer.name.return_value = "VectorLayer"
        mock_vlayer.isSpatial.return_value = True
        mock_vlayer.dataProvider().name.return_value = "ogr"
        mock_vlayer.dataProvider().dataSourceUri.return_value = "v_uri"
        mock_vlayer.dataProvider().availableEncodings.return_value = ["UTF-8", "GBK"]
        
        mock_proj = MagicMock()
        mock_proj.mapLayers.return_value = {"v1": mock_vlayer}
        mock_proj.mapLayer.return_value = mock_vlayer
        mock_project_inst.return_value = mock_proj
        
        widget = LayerBoardWidget(self.iface)
        widget.populateLayerTable('vector')
        
        # Find 'name' column (col 1)
        item = widget.vector_table.item(0, 1)
        item.setData(Qt.EditRole, "NewName")
        
        # Trigger manually
        widget.onItemChanged('vector', item)
        
        # Verify it was added to changed data cache
        self.assertEqual(widget.layerBoardChangedData['vector']['v1']['name'], "NewName")
```

- [ ] **Step 3: Run tests**

Run: `python -m unittest test_layer_board.py`
Expected output: PASS

- [ ] **Step 4: Commit**

```bash
git add layer_board_widget.py test_layer_board.py
git commit -m "feat: implement onItemChanged editing listeners and validators"
```

---

### Task 4: Saving & Discarding Changes

**Files:**
- Modify: `layer_board_widget.py`
- Modify: `test_layer_board.py`

**Interfaces:**
- Consumes: `LayerBoardWidget` from Task 3.
- Produces: `commitLayersChanges(layerType)` saving edits to layer, `discardLayersChanges(layerType)` resetting table, and `setLayerProperty(layerType, layers, prop, data)` applying settings to layer.

- [ ] **Step 1: Implement Commit/Discard methods in LayerBoardWidget**

Implement the logic:
```python
    # Add inside LayerBoardWidget in layer_board_widget.py

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
                    self.setLayerProperty(layerType, [layer], prop, data)
                    self.updateLog('* %s -> %s' % (prop, data))
                    
        # Mark project dirty
        lr.setDirty(True)
        self.populateLayerTable(layerType)

    def discardLayersChanges(self, layerType='vector'):
        self.populateLayerTable(layerType)

    def setLayerProperty(self, layerType, layers, prop, data):
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
                layer.toggleScaleBasedVisibility(True)
                layer.setMaximumScale(float(data))
                layer.triggerRepaint()
            elif prop == 'minScale':
                layer.toggleScaleBasedVisibility(True)
                layer.setMinimumScale(float(data))
                layer.triggerRepaint()
            elif prop == 'crs':
                qcrs = QgsCoordinateReferenceSystem()
                qcrs.createFromOgcWmsCrs(data)
                if qcrs:
                    layer.setCrs(qcrs)
                    layer.triggerRepaint()
            elif prop == 'source|uri':
                self.setDataSource(layer, data)
            elif prop == 'encoding':
                if hasattr(layer, 'setProviderEncoding'):
                    layer.setProviderEncoding(data)
                    
        self.populateLayerTable(layerType)

    def setDataSource(self, layer, newSourceUri):
        # Verify write XML functionality (if present)
        if not hasattr(layer, 'writeLayerXML'):
            return
        from qgis.PyQt.QtXml import QDomDocument, QDomElement
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

    def updateLog(self, msg):
        pass # Stub for Task 6
```

- [ ] **Step 2: Add tests for commit and setLayerProperty in test_layer_board.py**

Update unit tests:
```python
    # Add inside TestLayerBoardWidget in test_layer_board.py

    @patch('layer_board_widget.QgsProject.instance')
    def test_commit_changes(self, mock_project_inst):
        mock_vlayer = MagicMock()
        mock_vlayer.type.return_value = 0
        mock_vlayer.id.return_value = "v1"
        mock_vlayer.name.return_value = "OldName"
        mock_vlayer.isSpatial.return_value = True
        mock_vlayer.dataProvider().name.return_value = "ogr"
        mock_vlayer.dataProvider().dataSourceUri.return_value = "v_uri"
        
        mock_proj = MagicMock()
        mock_proj.mapLayers.return_value = {"v1": mock_vlayer}
        mock_proj.mapLayer.return_value = mock_vlayer
        mock_project_inst.return_value = mock_proj
        
        widget = LayerBoardWidget(self.iface)
        widget.populateLayerTable('vector')
        
        # Populate changed data manually
        widget.layerBoardChangedData['vector']["v1"] = {"name": "CommittedName"}
        
        widget.commitLayersChanges('vector')
        
        # Verify setName was called on the PyQGIS map layer
        mock_vlayer.setName.assert_called_with("CommittedName")
```

- [ ] **Step 3: Run tests**

Run: `python -m unittest test_layer_board.py`
Expected output: PASS

- [ ] **Step 4: Commit**

```bash
git add layer_board_widget.py test_layer_board.py
git commit -m "feat: implement Commit/Discard buttons and setLayerProperty changes"
```

---

### Task 5: Batch operations and Ghost Layers

**Files:**
- Modify: `layer_board_widget.py`
- Modify: `test_layer_board.py`

**Interfaces:**
- Consumes: `LayerBoardWidget` from Task 4.
- Produces: Sidebar GUI panels for batch updating, methods `applyPropertyOnSelectedLayers`, `performActionOnSelectedLayers`, `removeGhostLayers`.

- [ ] **Step 1: Setup actual controls in side panel of LayerBoardWidget**

Implement the sidebar UI structure and connections in `layer_board_widget.py`:
```python
    # Replace _init_right_panel_stubs in layer_board_widget.py

    def _init_right_panel_stubs(self):
        # 1. Batch Updates Group Box
        group_batch = QGroupBox(self.tr("批量更新 (Batch Update)"))
        batch_layout = QVBoxLayout(group_batch)
        batch_layout.setSpacing(8)
        
        # CRS
        crs_lbl = QLabel(self.tr("设置 CRS:"))
        batch_layout.addWidget(crs_lbl)
        crs_row = QHBoxLayout()
        self.inCrs = QLineEdit()
        self.btDefineProjection = QPushButton("...")
        self.btApplyCrs = QPushButton(self.tr("应用"))
        crs_row.addWidget(self.inCrs, 1)
        crs_row.addWidget(self.btDefineProjection)
        crs_row.addWidget(self.btApplyCrs)
        batch_layout.addLayout(crs_row)
        
        # Max Scale
        max_scale_lbl = QLabel(self.tr("设置最大比例尺:"))
        batch_layout.addWidget(max_scale_lbl)
        max_row = QHBoxLayout()
        self.inMaxScale = QLineEdit()
        self.btApplyMaxScale = QPushButton(self.tr("应用"))
        max_row.addWidget(self.inMaxScale, 1)
        max_row.addWidget(self.btApplyMaxScale)
        batch_layout.addLayout(max_row)
        
        # Min Scale
        min_scale_lbl = QLabel(self.tr("设置最小比例尺:"))
        batch_layout.addWidget(min_scale_lbl)
        min_row = QHBoxLayout()
        self.inMinScale = QLineEdit()
        self.btApplyMinScale = QPushButton(self.tr("应用"))
        min_row.addWidget(self.inMinScale, 1)
        min_row.addWidget(self.btApplyMinScale)
        batch_layout.addLayout(min_row)
        
        # Encoding
        self.encodingLabel = QLabel(self.tr("设置数据源编码 (仅矢量):"))
        batch_layout.addWidget(self.encodingLabel)
        enc_row = QHBoxLayout()
        self.inEncodingList = QComboBox()
        self.btApplyEncoding = QPushButton(self.tr("应用"))
        enc_row.addWidget(self.inEncodingList, 1)
        enc_row.addWidget(self.btApplyEncoding)
        batch_layout.addLayout(enc_row)
        
        self.right_layout.addWidget(group_batch)
        
        # 2. Actions Group Box
        group_actions = QGroupBox(self.tr("批量操作 (Actions)"))
        act_layout = QVBoxLayout(group_actions)
        act_layout.setSpacing(6)
        
        self.btSaveStyleAsDefault = QPushButton(self.tr("保存样式为默认"))
        self.btCreateSpatialIndex = QPushButton(self.tr("创建空间索引 (矢量)"))
        self.btRemoveLayer = QPushButton(self.tr("从项目移除图层"))
        self.btRemoveGhostLayers = QPushButton(self.tr("清除幽灵图层"))
        
        act_layout.addWidget(self.btSaveStyleAsDefault)
        act_layout.addWidget(self.btCreateSpatialIndex)
        act_layout.addWidget(self.btRemoveLayer)
        act_layout.addWidget(self.btRemoveGhostLayers)
        
        self.right_layout.addWidget(group_actions)
        
        # 3. Symbology Group Box
        self.group_style = QGroupBox(self.tr("图层样式直接修改"))
        style_layout = QVBoxLayout(self.group_style)
        self.styleScrollArea = QScrollArea()
        self.styleScrollArea.setWidgetResizable(True)
        self.styleScrollArea.setMinimumHeight(150)
        self.btApplyStyle = QPushButton(self.tr("应用样式"))
        style_layout.addWidget(self.styleScrollArea, 1)
        style_layout.addWidget(self.btApplyStyle)
        
        self.right_layout.addWidget(self.group_style)
        
        # 4. CSV Export Group Box
        group_export = QGroupBox(self.tr("数据导出 (Export)"))
        export_layout = QVBoxLayout(group_export)
        self.btExportCsv = QPushButton(self.tr("导出当前看板为 CSV"))
        export_layout.addWidget(self.btExportCsv)
        self.right_layout.addWidget(group_export)
        
        # 5. Log Group Box
        group_log = QGroupBox(self.tr("操作日志 (Log)"))
        log_layout = QVBoxLayout(group_log)
        self.txtLog = QTextEdit()
        self.txtLog.setReadOnly(True)
        self.txtLog.setMinimumHeight(100)
        self.btClearLog = QPushButton(self.tr("清空日志"))
        log_layout.addWidget(self.txtLog, 1)
        log_layout.addWidget(self.btClearLog)
        
        self.right_layout.addWidget(group_log)
        
        self._setup_connections()

    def _setup_connections(self):
        # Selection signals for style
        self.vector_table.selectionModel().selectionChanged.connect(partial(self.setSelectedLayerStyleWidget, 'vector'))
        self.raster_table.selectionModel().selectionChanged.connect(partial(self.setSelectedLayerStyleWidget, 'raster'))
        self.tab_widget.currentChanged.connect(self.onTabChanged)
        
        self.btDefineProjection.clicked.connect(self.chooseProjection)
        self.btClearLog.clicked.connect(self.clearLog)
        
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
```

Now, implement the execution functions:
```python
    # Add inside LayerBoardWidget in layer_board_widget.py

    def getActiveLayerType(self):
        return 'vector' if self.tab_widget.currentIndex() == 0 else 'raster'

    def chooseProjection(self):
        try:
            from qgis.gui import QgsProjectionSelectionTreeWidget
            projSelector = QgsProjectionSelectionTreeWidget(self)
            if projSelector.exec_():
                crs = QgsCoordinateReferenceSystem(projSelector.selectedCrsId(), QgsCoordinateReferenceSystem.InternalCrsId)
                if len(projSelector.selectedAuthId()) > 0:
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
            self.onItemChanged(layerType, item)

    def performActionOnSelectedLayers(self, key):
        layerType = self.getActiveLayerType()
        table = self.layersTable[layerType]['tableWidget']
        
        sm = table.selectionModel()
        lines = sm.selectedRows()
        if not lines:
            return
            
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
```

- [ ] **Step 2: Add test cases in test_layer_board.py for batch actions**

Add tests:
```python
    # Add inside TestLayerBoardWidget in test_layer_board.py

    @patch('layer_board_widget.QgsProject.instance')
    def test_remove_ghost_layers(self, mock_project_inst):
        mock_vlayer = MagicMock()
        mock_vlayer.id.return_value = "v1"
        mock_vlayer.type.return_value = 0
        mock_vlayer.isSpatial.return_value = True
        
        mock_proj = MagicMock()
        mock_proj.mapLayers.return_value = {"v1": mock_vlayer}
        mock_project_inst.return_value = mock_proj
        
        widget = LayerBoardWidget(self.iface)
        
        # Force it to be a ghost layer by patching is_ghost_layer
        widget.is_ghost_layer = MagicMock(return_value=True)
        widget.removeGhostLayers()
        
        # Verify it was removed
        mock_proj.removeMapLayer.assert_called_with("v1")
```

- [ ] **Step 3: Run tests**

Run: `python -m unittest test_layer_board.py`
Expected output: PASS

- [ ] **Step 4: Commit**

```bash
git add layer_board_widget.py test_layer_board.py
git commit -m "feat: implement right side-panel controls and batch actions with tests"
```

---

### Task 6: Style editor integration & CSV Export/Log

**Files:**
- Modify: `layer_board_widget.py`
- Modify: `test_layer_board.py`

**Interfaces:**
- Consumes: `LayerBoardWidget` from Task 5.
- Produces: Layer styling integration (`setSelectedLayerStyleWidget`, `applyStyle`), export functionality (`exportToCsv`), log functions (`updateLog`, `clearLog`).

- [ ] **Step 1: Implement style editor, log, and export methods in LayerBoardWidget**

Implement the code:
```python
    # Add inside LayerBoardWidget in layer_board_widget.py

    def setSelectedLayerStyleWidget(self, layerType, selected, unselected):
        table = self.layersTable[layerType]['tableWidget']
        sm = table.selectionModel()
        lines = sm.selectedRows()
        
        self.styleWidget = None
        self.styleLayer = None
        
        # Clear container
        self.styleScrollArea.setWidget(QWidget())
        
        if len(lines) != 1:
            return
            
        row = lines[0].row()
        layerId = table.item(row, 0).data(Qt.EditRole)
        layer = QgsProject.instance().mapLayer(layerId)
        if not layer:
            return
            
        self.styleLayer = layer
        
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
```

Hook the exports in `_setup_connections()`:
```python
        # Add to _setup_connections in layer_board_widget.py
        self.btApplyStyle.clicked.connect(self.applyStyle)
        self.btExportCsv.clicked.connect(self.exportToCsv)
```

- [ ] **Step 2: Add tests in test_layer_board.py**

```python
    # Add inside TestLayerBoardWidget in test_layer_board.py

    def test_log_functions(self):
        widget = LayerBoardWidget(self.iface)
        widget.clearLog()
        widget.updateLog("Test Message")
        # Since it's plain QWidget or mock QTextEdit on CLI, let's verify mock compatibility
        self.assertIsNotNone(widget.txtLog)
```

- [ ] **Step 3: Run tests**

Run: `python -m unittest test_layer_board.py`
Expected output: PASS

- [ ] **Step 4: Commit**

```bash
git add layer_board_widget.py test_layer_board.py
git commit -m "feat: implement Symbology Styling, CSV export and logging with tests"
```

---

### Task 7: Integrate into TreeMapDockWidget

**Files:**
- Modify: `dock_widget.py`
- Modify: `test_dock_widget.py`

**Interfaces:**
- Consumes: `LayerBoardWidget` from Task 6.
- Produces: Integrated menu option "属性看板" in QToolBar triggering view switcher to `self.layer_board_widget` on index 4 of `stacked_widget`.

- [ ] **Step 1: Modify dock_widget.py to load LayerBoardWidget**

Open `dock_widget.py` and modify the toolbar and stacked widget logic.

First, import the new widget:
```python
# In dock_widget.py, import section
try:
    from .layer_board_widget import LayerBoardWidget
except ImportError:
    try:
        from layer_board_widget import LayerBoardWidget
    except ImportError:
        # Mock class for offline tests
        class LayerBoardWidget(QWidget):
            def populateLayerTable(self, t): pass
            def populateAvailableEncodingList(self): pass
```

Add inside `__init__` of `TreeMapDockWidget`:
```python
        # Inside __init__ in dock_widget.py, around line 460
        self.treemap_view = TreeMapWidget()
        self.mindmap_view = MindMapView()
        self.layer_board_view = LayerBoardWidget(self.iface) # NEW PAGE
        
        self.stacked_widget.addWidget(self.physical_tree_view)
        self.stacked_widget.addWidget(self.group_tree_view)
        self.stacked_widget.addWidget(self.treemap_view)
        self.stacked_widget.addWidget(self.mindmap_view)
        self.stacked_widget.addWidget(self.layer_board_view) # NEW PAGE
```

Add in `_setup_toolbar`:
```python
        # Inside _setup_toolbar in dock_widget.py, around line 560
        self.act_mindmap = QAction("思维导图", self)
        self.act_mindmap.setCheckable(True)
        self.act_mindmap.triggered.connect(lambda: self.switch_view(3))
        self.view_group.addAction(self.act_mindmap)
        self.toolbar.addAction(self.act_mindmap)
        
        # Add new Attribute Board Action
        self.act_layer_board = QAction("属性看板", self)
        self.act_layer_board.setCheckable(True)
        self.act_layer_board.triggered.connect(lambda: self.switch_view(4))
        self.view_group.addAction(self.act_layer_board)
        self.toolbar.addAction(self.act_layer_board)
```

Update `switch_view`:
```python
    # Modify switch_view in dock_widget.py
    def switch_view(self, index):
        self.act_physical_tree.setChecked(index == 0)
        self.act_group_tree.setChecked(index == 1)
        self.act_treemap.setChecked(index == 2)
        self.act_mindmap.setChecked(index == 3)
        self.act_layer_board.setChecked(index == 4) # NEW
        self.stacked_widget.setCurrentIndex(index)
        
        filter_str = self.current_filter_format.lower() if self.current_filter_format else None
        project = QgsProject.instance()
        layers = []
        if project:
            all_layers = list(project.mapLayers().values())
            if filter_str:
                try:
                    from .layer_model import get_layer_format
                except ImportError:
                    def get_layer_format(l):
                        source = getattr(l, 'source', lambda: '')()
                        if source.endswith('.shp'): return 'shp'
                        if source.endswith('.tif'): return 'tif'
                        return 'other'
                layers = [l for l in all_layers if get_layer_format(l) == filter_str]
            else:
                layers = all_layers
                
        if index == 2:
            self.treemap_view.set_layers(layers)
        elif index == 3:
            self.mindmap_view.set_layers(layers)
        elif index == 4:
            # Refresh Attribute Board when switched to
            self.layer_board_view.populateLayerTable('vector')
            self.layer_board_view.populateLayerTable('raster')
            self.layer_board_view.populateAvailableEncodingList()
```

Update `refresh`:
```python
    # Update refresh in dock_widget.py
    def refresh(self):
        self._is_refreshing = True
        try:
            self.update_filter_tags()
            filter_str = self.current_filter_format.lower() if self.current_filter_format else None
            
            # 1. Rebuild physical tree model
            self.physical_model.rebuild_model(group_by_physical=True, filter_format=filter_str)
            
            # 2. Rebuild group tree model
            self.group_model.rebuild_model(group_by_physical=False, filter_format=filter_str)
            
            # 3. Re-apply column widths (model rebuild resets them)
            self._apply_column_widths()
            
            # Expand physical tree recursively, keep group tree collapsed
            self.physical_tree_view.expandAll()
            self.group_tree_view.collapseAll()
            
            project = QgsProject.instance()
            layers = []
            if project:
                all_layers = list(project.mapLayers().values())
                if filter_str:
                    try:
                        from .layer_model import get_layer_format
                    except ImportError:
                        def get_layer_format(l):
                            source = getattr(l, 'source', lambda: '')()
                            if source.endswith('.shp'): return 'shp'
                            if source.endswith('.tif'): return 'tif'
                            return 'other'
                        layers = [l for l in all_layers if get_layer_format(l) == filter_str]
                else:
                    layers = all_layers
            
            if self.stacked_widget.currentIndex() == 2:
                self.treemap_view.set_layers(layers)
            elif self.stacked_widget.currentIndex() == 3:
                self.mindmap_view.set_layers(layers)
            elif self.stacked_widget.currentIndex() == 4:
                self.layer_board_view.populateLayerTable('vector')
                self.layer_board_view.populateLayerTable('raster')
                self.layer_board_view.populateAvailableEncodingList()
        finally:
            self._is_refreshing = False
```

- [ ] **Step 2: Add integration checks in test_dock_widget.py**

Modify `test_dock_widget.py` to check page 4 (index 4) switches correctly:
```python
    # Add inside TestDockWidget in test_dock_widget.py

    def test_switch_view_layer_board(self):
        with patch('dock_widget.LayerTreeModel'), \
             patch('dock_widget.TreeMapWidget'), \
             patch('dock_widget.MindMapView'), \
             patch('dock_widget.LayerBoardWidget') as mock_lb_cls:
            
            mock_lb = MagicMock()
            mock_lb_cls.return_value = mock_lb
            
            dock = TreeMapDockWidget(self.iface, self.parent)
            
            # Switch to Attribute Board (index 4)
            dock.switch_view(4)
            self.assertTrue(dock.act_layer_board.isChecked())
            self.assertEqual(dock.stacked_widget.currentIndex(), 4)
            mock_lb.populateLayerTable.assert_any_call('vector')
            mock_lb.populateLayerTable.assert_any_call('raster')
            mock_lb.populateAvailableEncodingList.assert_called_once()
```

- [ ] **Step 3: Run the entire test suite**

Run: `python -m unittest discover -p "test_*.py"`
Expected output: Ran 63 tests. OK.

- [ ] **Step 4: Commit**

```bash
git add dock_widget.py test_dock_widget.py
git commit -m "feat: integrate LayerBoardWidget into TreeMapDockWidget view stack and toolbar"
```
