import os
import sys


# Robust fallback imports for Qt
try:
    from qgis.PyQt.QtCore import Qt, QModelIndex, QPersistentModelIndex, QTimer
    from qgis.PyQt.QtWidgets import (QAction, QToolBar, QStackedWidget, QListView,
                                 QTreeView, QVBoxLayout, QHBoxLayout, QWidget, QLabel, QPushButton, QMenu, QFileDialog, QInputDialog,
                                 QAbstractItemView, QMessageBox, QActionGroup, QHeaderView, QSizePolicy, QDialog, QToolButton)
except ImportError:
    try:
        from qtpy.QtCore import Qt, QModelIndex, QPersistentModelIndex, QTimer
        from qtpy.QtWidgets import (QAction, QToolBar, QStackedWidget, QListView,
                                    QTreeView, QVBoxLayout, QHBoxLayout, QWidget, QLabel, QPushButton, QMenu, QFileDialog, QInputDialog,
                                    QAbstractItemView, QMessageBox, QActionGroup, QHeaderView, QSizePolicy, QDialog, QToolButton)
    except ImportError:
        try:
            from PySide2.QtCore import Qt, QModelIndex, QPersistentModelIndex, QTimer
            from PySide2.QtWidgets import (QAction, QToolBar, QStackedWidget, QListView,
                                           QTreeView, QVBoxLayout, QHBoxLayout, QWidget, QLabel, QPushButton, QMenu, QFileDialog, QInputDialog,
                                           QAbstractItemView, QMessageBox, QActionGroup, QHeaderView, QSizePolicy, QDialog, QToolButton)
        except ImportError:
            try:
                from PySide6.QtCore import Qt, QModelIndex, QPersistentModelIndex, QTimer
                from PySide6.QtWidgets import (QToolBar, QStackedWidget, QListView,
                                               QTreeView, QVBoxLayout, QHBoxLayout, QWidget, QLabel, QPushButton, QMenu, QFileDialog, QInputDialog,
                                               QAbstractItemView, QMessageBox, QHeaderView, QSizePolicy, QDialog, QToolButton)
                from PySide6.QtGui import QAction, QActionGroup
            except ImportError:
                # Basic mock classes for CLI tests without Qt installed
                class QTimer:
                    def __init__(self, parent=None):
                        self.timeout = self._Signal()
                    class _Signal:
                        def connect(self, slot): pass
                        def emit(self, *args): pass
                    def setSingleShot(self, val): pass
                    def setInterval(self, val): pass
                    def start(self): pass
                    @staticmethod
                    def singleShot(msecs, slot): pass
                class Qt:
                    LeftDockWidgetArea = 1
                    RightDockWidgetArea = 2
                    CustomContextMenu = 3
                    UserRole = 32
                    Horizontal = 1
                    AlignLeft = 1
                    ToolButtonTextBesideIcon = 2
                    class CheckState:
                        Unchecked = 0
                        PartiallyChecked = 1
                        Checked = 2
                    class AlignmentFlag:
                        AlignLeft = 1
                    class ToolButtonStyle:
                        ToolButtonTextBesideIcon = 2
                    class ContextMenuPolicy:
                        CustomContextMenu = 3
                    class ItemDataRole:
                        UserRole = 32
                    class WindowType:
                        WindowMinimizeButtonHint = 1
                        WindowMaximizeButtonHint = 2
                    class MouseButton:
                        LeftButton = 1
                        RightButton = 2
                        MiddleButton = 4
                    class DropAction:
                        MoveAction = 2
                class QHeaderView:
                    Interactive = 0
                    ResizeToContents = 1
                    class ResizeMode:
                        Interactive = 0
                        ResizeToContents = 1
                class QSizePolicy:
                    Fixed = 0
                    Preferred = 1
                    Expanding = 2
                    class Policy:
                        Fixed = 0
                        Preferred = 1
                        Expanding = 2
                class QModelIndex:
                    pass
                QPersistentModelIndex = QModelIndex
                class QAction:
                    def __init__(self, *args, **kwargs):
                        self._icon = kwargs.get('icon', None)
                        self._text = kwargs.get('text', "")
                        self.parent = kwargs.get('parent', None)

                        # Map remaining unassigned positional args to standard QAction signatures
                        if len(args) == 1:
                            if isinstance(args[0], str):
                                self._text = args[0]
                            else:
                                self.parent = args[0]
                        elif len(args) == 2:
                            self._text = args[0]
                            self.parent = args[1]
                        elif len(args) >= 3:
                            self._icon = args[0]
                            self._text = args[1]
                            self.parent = args[2]

                        self._checkable = False
                        self._checked = False
                        self.triggered = self._Signal()
                    class _Signal:
                        def connect(self, slot):
                            self._slot = slot
                        def emit(self, *args):
                            if hasattr(self, '_slot'):
                                self._slot(*args)
                    def setCheckable(self, val):
                        self._checkable = val
                    def isCheckable(self):
                        return self._checkable
                    def setChecked(self, val):
                        self._checked = val
                    def isChecked(self):
                        return self._checked
                    def setText(self, text):
                        self._text = text
                    def text(self):
                        return self._text
                    def setIcon(self, icon):
                        self._icon = icon
                    def setEnabled(self, val):
                        self._enabled = bool(val)
                    def isEnabled(self):
                        return getattr(self, '_enabled', True)
                    def setVisible(self, val):
                        self._visible = bool(val)
                class QActionGroup:
                    def __init__(self, parent=None):
                        self._actions = []
                        self._exclusive = True
                    def addAction(self, action):
                        self._actions.append(action)
                        return action
                    def setExclusive(self, val):
                        self._exclusive = val
                class QToolBar:
                    def __init__(self, parent=None):
                        self._actions = []
                        self._widgets = []
                    def addAction(self, action):
                        self._actions.append(action)
                        return action
                    def addWidget(self, widget):
                        self._widgets.append(widget)
                        return widget
                    def addSeparator(self):
                        pass
                    def setSizePolicy(self, h, v):
                        pass
                    def setToolButtonStyle(self, style):
                        pass
                    def setIconSize(self, size):
                        pass
                class QStackedWidget:
                    def __init__(self, parent=None):
                        self._widgets = []
                        self._current_index = 0
                    def addWidget(self, widget):
                        self._widgets.append(widget)
                    def setCurrentIndex(self, index):
                        self._current_index = index
                    def currentIndex(self):
                        return self._current_index
                class QListView:
                    def __init__(self, parent=None):
                        self._model = None
                        self._selection_model = self._SelectionModel()
                        self._selection_mode = None
                        self._alternating_row_colors = False
                    def setObjectName(self, name):
                        pass
                    def setModel(self, model):
                        self._model = model
                    def setContextMenuPolicy(self, policy):
                        pass
                    def setSelectionMode(self, mode):
                        self._selection_mode = mode
                    def setSelectionBehavior(self, behavior):
                        pass
                    def setAllColumnsShowFocus(self, val):
                        pass
                    def setAlternatingRowColors(self, val):
                        self._alternating_row_colors = val
                    def setEditTriggers(self, triggers):
                        pass
                    class _SelectionModel:
                        def selectedIndexes(self):
                            return []
                        def isSelected(self, index):
                            return False
                        def select(self, index, flags):
                            pass
                        def clearSelection(self):
                            pass
                    def selectionModel(self):
                        return self._selection_model
                    def mapToGlobal(self, pos):
                        return pos
                    class _Signal:
                        def connect(self, slot):
                            pass
                    customContextMenuRequested = _Signal()
                    doubleClicked = _Signal()
                class QTreeView(QListView):
                    def __init__(self, parent=None):
                        super().__init__(parent)
                        self._header = self._Header()
                    def setDragEnabled(self, val):
                        pass
                    def setAcceptDrops(self, val):
                        pass
                    def setDropIndicatorShown(self, val):
                        pass
                    def setColumnWidth(self, col, width):
                        pass
                    def header(self):
                        return self._header
                    def setRootIsDecorated(self, val):
                        pass
                    def setItemsExpandable(self, val):
                        pass
                    def setSortingEnabled(self, val):
                        pass
                    def expandAll(self):
                        pass
                    def collapseAll(self):
                        pass
                    def isExpanded(self, index):
                        return False
                    def setExpanded(self, index, val):
                        pass
                    def verticalScrollBar(self):
                        return None
                    def horizontalScrollBar(self):
                        return None
                    class _Header:
                        def setSectionResizeMode(self, col, mode):
                            pass
                        def setMinimumSectionSize(self, size):
                            pass
                        def count(self):
                            return 3
                class QVBoxLayout:
                    def __init__(self, parent=None):
                        self._widgets = []
                    def addWidget(self, widget, *args):
                        self._widgets.append(widget)
                    def setContentsMargins(self, *args):
                        pass
                    def setSpacing(self, spacing):
                        pass
                class QHBoxLayout:
                    def __init__(self, parent=None):
                        self._widgets = []
                    def addWidget(self, widget, *args):
                        self._widgets.append(widget)
                    def setContentsMargins(self, *args):
                        pass
                    def setSpacing(self, spacing):
                        pass
                    def setAlignment(self, align):
                        pass
                    def count(self):
                        return 1
                    def takeAt(self, index):
                        return None
                class QLabel:
                    def __init__(self, text=""):
                        self._text = text
                    def setStyleSheet(self, style):
                        pass
                    def setObjectName(self, name):
                        pass
                class QPushButton:
                    clicked = None
                    def __init__(self, text=""):
                        self._text = text
                        class MockSignal:
                            def connect(self, slot): pass
                        self.clicked = MockSignal()
                    def text(self):
                        return self._text
                    def setStyleSheet(self, style):
                        pass
                    def setObjectName(self, name):
                        pass
                class QWidget:
                    def __init__(self, parent=None):
                        self._parent = parent
                        self._layout = None
                    def setLayout(self, layout):
                        self._layout = layout
                    def setStyleSheet(self, style):
                        pass
                    def setObjectName(self, name):
                        pass
                    def setSizePolicy(self, h, v):
                        pass
                    def show(self): pass
                    def hide(self): pass
                class QDialog(QWidget):
                    def __init__(self, parent=None):
                        super().__init__(parent)
                    def setWindowTitle(self, title):
                        pass
                    def resize(self, w, h):
                        pass
                    def setWindowFlags(self, flags):
                        pass
                    def windowFlags(self):
                        return 0
                class QToolButton(QWidget):
                    def __init__(self, parent=None):
                        super().__init__(parent)
                        self.toggled = self._Signal()
                        self._checkable = False
                        self._checked = False
                        self._tooltip = ""
                        self._icon = None
                        self._icon_size = None
                    class _Signal:
                        def connect(self, slot):
                            self._slot = slot
                        def emit(self, *args):
                            if hasattr(self, '_slot'):
                                self._slot(*args)
                    def setCheckable(self, val):
                        self._checkable = val
                    def isCheckable(self):
                        return self._checkable
                    def setChecked(self, val):
                        self._checked = val
                        self.toggled.emit(val)
                    def isChecked(self):
                        return self._checked
                    def setToolTip(self, val):
                        self._tooltip = val
                    def setIcon(self, icon):
                        self._icon = icon
                    def setIconSize(self, size):
                        self._icon_size = size
                class QMenu:
                    def __init__(self, parent=None):
                        pass
                    def setStyleSheet(self, style):
                        pass
                    def setIconSize(self, size):
                        pass
                    def addAction(self, text):
                        return QAction(text, self)
                    def addMenu(self, text):
                        return QMenu(self)
                    def addSeparator(self):
                        pass
                    def exec(self, pos):
                        pass
                    def setIcon(self, icon):
                        self._icon = icon
                class QFileDialog:
                    @classmethod
                    def getOpenFileName(cls, *args, **kwargs):
                        return "", ""
                    @classmethod
                    def getSaveFileName(cls, *args, **kwargs):
                        return "", ""
                    @classmethod
                    def getExistingDirectory(cls, *args, **kwargs):
                        return ""
                class QInputDialog:
                    @classmethod
                    def getText(cls, *args, **kwargs):
                        return "", False
                class QAbstractItemView:
                    NoEditTriggers = 0
                    ExtendedSelection = 3
                    SelectRows = 1
                    class SelectionMode:
                        ExtendedSelection = 3
                    class SelectionBehavior:
                        SelectRows = 1
                class QMessageBox:
                    Yes = 16384
                    No = 65536
                    class StandardButton:
                        Yes = 16384
                        No = 65536
                    class ButtonRole:
                        ActionRole = 1
                        RejectRole = 2
                    def __init__(self, parent=None):
                        self._buttons = []
                        self._clicked = None
                    def setWindowTitle(self, title):
                        pass
                    def setText(self, text):
                        pass
                    def addButton(self, *args):
                        class DummyButton:
                            def setStyleSheet(self, style):
                                pass
                            def setIcon(self, icon):
                                pass
                        btn = DummyButton()
                        self._buttons.append(btn)
                        return btn
                    def exec(self):
                        if self._buttons:
                            self._clicked = self._buttons[0]
                        return 0
                    def clickedButton(self):
                        return self._clicked
                    @classmethod
                    def warning(cls, parent, title, text, buttons=None, default_button=None):
                        return 16384
                    @classmethod
                    def information(cls, parent, title, text):
                        pass
                    @classmethod
                    def critical(cls, parent, title, text):
                        pass
                    @classmethod
                    def question(cls, parent, title, text, buttons=None, default_button=None):
                        return 16384

# Robust fallback imports for QStandardItemModel & QStandardItem
try:
    from qgis.PyQt.QtGui import QStandardItemModel, QStandardItem, QIcon
except ImportError:
    try:
        from qtpy.QtGui import QStandardItemModel, QStandardItem, QIcon
    except ImportError:
        try:
            from PySide2.QtGui import QStandardItemModel, QStandardItem, QIcon
        except ImportError:
            try:
                from PySide6.QtGui import QStandardItemModel, QStandardItem, QIcon
            except ImportError:
                class QStandardItemModel:
                    def __init__(self, parent=None):
                        self.itemChanged = self._Signal()
                    class _Signal:
                        def connect(self, slot): pass
                        def emit(self, *args): pass
                    def clear(self): pass
                    def setHorizontalHeaderLabels(self, labels): pass
                    def appendRow(self, items): pass
                    def itemFromIndex(self, idx): return None
                    def setSortRole(self, role): pass
                class QStandardItem:
                    def __init__(self, text=""): self._text = text
                    def setData(self, val, role): pass
                    def flags(self): return 33
                    def setFlags(self, flags): pass
                class QIcon:
                    def __init__(self, path=""): pass

# Robust fallback imports for QGIS
try:
    from qgis.gui import QgsDockWidget
    from qgis.core import (
        QgsMapLayer,
        QgsMapLayerStyle,
        QgsLayerTreeModel,
        QgsProject,
        QgsRasterLayer,
        QgsVectorFileWriter,
        QgsVectorLayer,
    )
except ImportError:
    # Use our own mocked versions
    class QgsDockWidget(QWidget):
        def __init__(self, title, parent=None):
            super().__init__(parent)
            self._title = title
            self._widget = None
        def setAllowedAreas(self, areas):
            pass
        def setWidget(self, widget):
            self._widget = widget
        def show(self):
            pass

    class QgsProject:
        _instance = None
        @classmethod
        def instance(cls):
            if cls._instance is None:
                cls._instance = cls()
            return cls._instance
        def mapLayers(self):
            return {}
        def fileName(self):
            return ""
        def mapLayer(self, layer_id):
            return None
        def addMapLayer(self, layer):
            pass
        def addVectorLayer(self, path, name, provider):
            # For testing success
            return QgsVectorLayer(path, name, provider)
        def removeMapLayer(self, layer_id):
            pass
        def removeMapLayers(self, layer_ids):
            for layer_id in layer_ids:
                self.removeMapLayer(layer_id)
        def transformContext(self):
            return None

    class QgsLayerTreeModel:
        class Flag:
            AllowNodeReorder = 1
        def __init__(self, root):
            self.root = root
        def setFlag(self, flag, enabled=True):
            pass
        def node2index(self, node):
            return QModelIndex()
        def mimeData(self, indexes):
            return None
        def dropMimeData(self, data, action, row, column, parent):
            return False

    class QgsMapLayer:
        def __init__(self, layer_id="", name="", source_path="", provider=""):
            self._id = layer_id
            self._name = name
            self._source = source_path
            self._provider = self._DataProvider(provider)
        class _DataProvider:
            def __init__(self, name):
                self._name = name
            def name(self):
                return self._name
        def id(self): return self._id
        def name(self): return self._name
        def source(self): return self._source
        def isValid(self): return True
        def isEditable(self): return False
        def startEditing(self): return False
        def commitChanges(self): return False
        def setName(self, name): self._name = name
        def triggerRepaint(self): pass
        def dataProvider(self): return self._provider

    class QgsVectorLayer(QgsMapLayer):
        def __init__(self, path, name, provider):
            super().__init__(name, name, path, provider)
            self._subset_string = ""
        def subsetString(self):
            return self._subset_string
        def setSubsetString(self, expression):
            self._subset_string = expression
            return True

    class QgsMapLayerStyle:
        def __init__(self):
            self.source_layer = None
            self.target_layer = None
        def readFromLayer(self, layer):
            self.source_layer = layer
        def writeToLayer(self, layer):
            self.target_layer = layer

    class QgsRasterLayer(QgsMapLayer):
        def __init__(self, path, name, provider):
            super().__init__(name, name, path, provider)

    class QgsVectorFileWriter:
        NoError = 0
        CreateOrOverwriteFile = 0
        CreateOrOverwriteLayer = 1
        AppendToLayerNoNewFields = 2
        AppendToLayerAddFields = 3
        class ActionOnExistingFile:
            CreateOrOverwriteFile = 0
            CreateOrOverwriteLayer = 1
            AppendToLayerNoNewFields = 2
            AppendToLayerAddFields = 3
        class SaveVectorOptions:
            def __init__(self):
                self.driverName = ""
                self.fileEncoding = ""
                self.layerName = ""
                self.actionOnExistingFile = 0
        class WriterError:
            NoError = 0
        @staticmethod
        def writeAsVectorFormatV3(*args):
            return 0, "", "", ""

# Try importing our modules
try:
    from .layer_model import LayerTreeModel, LayerItem, FolderItem, split_qgis_source, get_layer_format
    from .treemap_widget import TreeMapWidget
    from .mindmap_view import MindMapView
    from .file_operations import safe_copy, safe_move, safe_rename, safe_rename_parent_dir, safe_rename_dir, safe_migrate_dir, update_layer_source, get_associated_files, format_size, resolve_physical_path, pending_rename_cleanup_files
except ImportError:
    try:
        from layer_model import LayerTreeModel, LayerItem, FolderItem, split_qgis_source, get_layer_format
        from treemap_widget import TreeMapWidget
        from mindmap_view import MindMapView
        from file_operations import safe_copy, safe_move, safe_rename, safe_rename_parent_dir, safe_rename_dir, safe_migrate_dir, update_layer_source, get_associated_files, format_size, resolve_physical_path, pending_rename_cleanup_files
    except ImportError:
        # Mock models and operations for standalone tests
        class LayerTreeModel:
            def __init__(self): pass
            def rebuild_model(self, group_by_physical): pass
        class LayerItem:
            pass
        class FolderItem:
            pass
        class TreeMapWidget(QWidget):
            class _Signal:
                def connect(self, slot): pass
                def emit(self, *args): pass
            layerSelected = _Signal()
            contextMenuTriggered = _Signal()
            def set_layers(self, layers): pass
        class MindMapView(QWidget):
            class _Signal:
                def connect(self, slot): pass
                def emit(self, *args): pass
            layerSelected = _Signal()
            layerDoubleClicked = _Signal()
            def set_layers(self, layers): pass
            def select_layer_node(self, layer_id): pass
            def zoom_to_fit(self): pass
        def safe_copy(*args): pass
        def safe_move(*args): pass
        def safe_rename(*args): pass
        def pending_rename_cleanup_files(): return []
        def safe_rename_parent_dir(*args): pass
        def update_layer_source(*args): pass
        def split_qgis_source(x): return x, ""
        def get_associated_files(x): return [x] if x else []
        def format_size(x): return "0 B"


try:
    from .layer_board_widget import LayerBoardWidget
except ImportError:
    try:
        from layer_board_widget import LayerBoardWidget
    except ImportError:
        # Mock class for offline tests
        class LayerBoardWidget(QWidget):
            def __init__(self, iface=None, parent=None):
                super().__init__(parent)
            def populateLayerTable(self, t): pass
            def populateAvailableEncodingList(self): pass


try:
    from qgis.PyQt.QtCore import QSize
except ImportError:
    try:
        from qtpy.QtCore import QSize
    except ImportError:
        try:
            from PySide2.QtCore import QSize
        except ImportError:
            try:
                from PySide6.QtCore import QSize
            except ImportError:
                class QSize:
                    def __init__(self, w, h):
                        self.w = w
                        self.h = h


try:
    from .translation import tr
except ImportError:
    try:
        from translation import tr
    except ImportError:
        def tr(text, disambiguation=None): return text

def _get_drag_distance():
    try:
        from qgis.PyQt.QtWidgets import QApplication
        return QApplication.startDragDistance()
    except Exception:
        try:
            from qtpy.QtWidgets import QApplication
            return QApplication.startDragDistance()
        except Exception:
            try:
                from PySide2.QtWidgets import QApplication
                return QApplication.startDragDistance()
            except Exception:
                try:
                    from PySide6.QtWidgets import QApplication
                    return QApplication.startDragDistance()
                except Exception:
                    return 8


class DraggableTreeView(QTreeView):
    try:
        from qgis.PyQt.QtCore import pyqtSignal as layersDroppedSignal
    except ImportError:
        try:
            from qtpy.QtCore import Signal as layersDroppedSignal
        except ImportError:
            try:
                from PySide2.QtCore import Signal as layersDroppedSignal
            except ImportError:
                try:
                    from PySide6.QtCore import Signal as layersDroppedSignal
                except ImportError:
                    class layersDroppedSignal:
                        def __init__(self, *args):
                            self._slots = []
                        def emit(self, *args):
                            for s in self._slots: s(*args)
                        def connect(self, s):
                            self._slots.append(s)

    layersDropped = layersDroppedSignal(list, str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setDragEnabled(False)
        self.setAcceptDrops(True)
        self.setDropIndicatorShown(True)
        self._drag_start_pos = None

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            idx = self.indexAt(event.pos())
            if idx.isValid():
                if idx.column() == 0:
                    self._drag_start_pos = event.pos()
                else:
                    self._drag_start_pos = None
            else:
                self._drag_start_pos = None
        else:
            self._drag_start_pos = None
        try:
            super().mousePressEvent(event)
        except AttributeError:
            pass

    def mouseMoveEvent(self, event):
        if event.buttons() & Qt.MouseButton.LeftButton and self._drag_start_pos is not None:
            delta = event.pos() - self._drag_start_pos
            if delta.manhattanLength() >= _get_drag_distance():
                self.start_custom_drag()
                self._drag_start_pos = None
                return
        try:
            super().mouseMoveEvent(event)
        except AttributeError:
            pass

    def dragEnterEvent(self, event):
        if event.mimeData().hasFormat("application/x-superlayer-layer-ids"):
            event.acceptProposedAction()
        else:
            try:
                super().dragEnterEvent(event)
            except AttributeError:
                pass

    def dragMoveEvent(self, event):
        if event.mimeData().hasFormat("application/x-superlayer-layer-ids"):
            idx = self.indexAt(event.pos())
            if idx.isValid():
                model = self.model()
                if model:
                    item = model.itemFromIndex(idx)
                    if isinstance(item, FolderItem) or isinstance(item, LayerItem):
                        event.acceptProposedAction()
                        return
            event.ignore()
        else:
            try:
                super().dragMoveEvent(event)
            except AttributeError:
                pass

    def dropEvent(self, event):
        if event.mimeData().hasFormat("application/x-superlayer-layer-ids"):
            idx = self.indexAt(event.pos())
            if idx.isValid():
                model = self.model()
                if model:
                    item = model.itemFromIndex(idx)
                    target_folder_path = None
                    if isinstance(item, FolderItem):
                        target_folder_path = item.folder_path
                    elif isinstance(item, LayerItem) and item.layer:
                        source_path = item.layer.source()
                        phys_source_path, _ = split_qgis_source(source_path)
                        actual_source_path = resolve_physical_path(phys_source_path)
                        if actual_source_path:
                            target_folder_path = os.path.dirname(actual_source_path)

                    if target_folder_path:
                        try:
                            import json
                            layer_ids = json.loads(event.mimeData().data("application/x-superlayer-layer-ids").data().decode('utf-8'))
                        except Exception:
                            layer_ids = []

                        if layer_ids:
                            self.layersDropped.emit(layer_ids, target_folder_path)
                            event.acceptProposedAction()
                            return
            event.ignore()
        else:
            try:
                super().dropEvent(event)
            except AttributeError:
                pass

    def start_custom_drag(self):
        model = self.model()
        if not model:
            return

        layer_ids = []
        for idx in self.selectionModel().selectedIndexes():
            if idx.column() == 0:
                item = model.itemFromIndex(idx)
                if isinstance(item, LayerItem) and item.layer:
                    layer_ids.append(item.layer.id())

        if not layer_ids:
            return

        try:
            from qgis.PyQt.QtGui import QDrag
            from qgis.PyQt.QtCore import QMimeData
        except ImportError:
            try:
                from qtpy.QtGui import QDrag
                from qtpy.QtCore import QMimeData
            except ImportError:
                try:
                    from PySide2.QtGui import QDrag
                    from PySide2.QtCore import QMimeData
                except ImportError:
                    try:
                        from PySide6.QtGui import QDrag
                        from PySide6.QtCore import QMimeData
                    except ImportError:
                        return

        mime_data = QMimeData()
        import json
        mime_data.setData("application/x-superlayer-layer-ids", json.dumps(layer_ids).encode('utf-8'))

        drag = QDrag(self)
        drag.setMimeData(mime_data)
        drag.exec(Qt.DropAction.MoveAction)


class LayerOrderTreeModel(QgsLayerTreeModel):
    """Native QGIS model restricted to sibling layer-node reordering."""

    def __init__(self, root):
        super().__init__(root)
        self._drag_parent_node = None
        self._theme_layer_ids = None
        flag_scope = getattr(QgsLayerTreeModel, "Flag", QgsLayerTreeModel)
        for flag_name in ("AllowNodeReorder", "AllowNodeRename", "AllowNodeChangeVisibility"):
            flag = getattr(flag_scope, flag_name, None)
            if flag is not None:
                self.setFlag(flag, True)

    def set_theme_layer_ids(self, layer_ids=None):
        """Show a read-only map-theme check state without changing the canvas."""
        self._theme_layer_ids = set(layer_ids) if layer_ids is not None else None
        if hasattr(self, 'beginResetModel') and hasattr(self, 'endResetModel'):
            self.beginResetModel()
            self.endResetModel()

    def _descendant_theme_states(self, node):
        states = []
        for child in node.children() if node and hasattr(node, 'children') else []:
            layer = self._node_layer(child)
            if layer:
                states.append(layer.id() in self._theme_layer_ids)
            else:
                states.extend(self._descendant_theme_states(child))
        return states

    def data(self, index, role):
        check_role = getattr(getattr(Qt, 'ItemDataRole', Qt), 'CheckStateRole', None)
        if self._theme_layer_ids is not None and role == check_role and index.isValid() and index.column() == 0:
            node = self.index2node(index)
            layer = self._node_layer(node)
            check_scope = getattr(Qt, 'CheckState', Qt)
            checked = getattr(check_scope, 'Checked', 2)
            unchecked = getattr(check_scope, 'Unchecked', 0)
            partial = getattr(check_scope, 'PartiallyChecked', 1)
            if layer:
                return checked if layer.id() in self._theme_layer_ids else unchecked
            states = self._descendant_theme_states(node)
            if states:
                if all(states):
                    return checked
                if any(states):
                    return partial
                return unchecked
        try:
            return super().data(index, role)
        except AttributeError:
            return None

    @staticmethod
    def _node_layer(node):
        try:
            return node.layer() if node and hasattr(node, "layer") else None
        except RuntimeError:
            return None

    def flags(self, index):
        base_flags = super().flags(index)
        if not index.isValid():
            return base_flags
        node = self.index2node(index)
        if self._node_layer(node):
            if self._theme_layer_ids is not None:
                checkable_flag = getattr(getattr(Qt, 'ItemFlag', Qt), 'ItemIsUserCheckable', None)
                if checkable_flag is not None:
                    return base_flags & ~checkable_flag
            return base_flags
        item_flag_scope = getattr(Qt, "ItemFlag", Qt)
        drag_flag = getattr(item_flag_scope, "ItemIsDragEnabled", None)
        return base_flags & ~drag_flag if drag_flag is not None else base_flags

    def mimeData(self, indexes):
        nodes = []
        for index in indexes:
            if not index.isValid() or index.column() != 0:
                continue
            node = self.index2node(index)
            if self._node_layer(node) and node not in nodes:
                nodes.append(node)
        if not nodes:
            self._drag_parent_node = None
            return None
        parent = nodes[0].parent()
        if not parent or any(node.parent() != parent for node in nodes):
            self._drag_parent_node = None
            return None
        self._drag_parent_node = parent
        return super().mimeData([self.node2index(node) for node in nodes])

    def dropMimeData(self, data, action, row, column, parent):
        source_parent = self._drag_parent_node
        try:
            target_parent = self.index2node(parent) if parent.isValid() else self.rootGroup()
            if not source_parent or target_parent != source_parent:
                return False
            return super().dropMimeData(data, action, row, column, parent)
        finally:
            self._drag_parent_node = None


class DraggableGroupTreeView(QTreeView):
    try:
        from qgis.PyQt.QtCore import pyqtSignal as groupReorderedSignal
    except ImportError:
        try:
            from qtpy.QtCore import Signal as groupReorderedSignal
        except ImportError:
            try:
                from PySide2.QtCore import Signal as groupReorderedSignal
            except ImportError:
                try:
                    from PySide6.QtCore import Signal as groupReorderedSignal
                except ImportError:
                    class groupReorderedSignal:
                        def __init__(self, *args):
                            self._slots = []
                        def emit(self, *args):
                            for s in self._slots: s(*args)
                        def connect(self, s):
                            self._slots.append(s)

    groupReordered = groupReorderedSignal(list, dict, str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setDragEnabled(False)
        self.setAcceptDrops(True)
        self.setDropIndicatorShown(True)
        self._drag_start_pos = None
        self._drop_target_index = None
        self._drop_position = None
        self._reorder_enabled = True

    def setReorderEnabled(self, enabled):
        """Enable ordering only when the view represents the complete tree."""
        self._reorder_enabled = bool(enabled)
        if not self._reorder_enabled:
            self._drag_start_pos = None
            self._drop_target_index = None
            self._drop_position = None
            viewport = self.viewport() if hasattr(self, "viewport") else None
            if viewport:
                viewport.update()

    def mousePressEvent(self, event):
        if self._reorder_enabled and event.button() == Qt.MouseButton.LeftButton:
            idx = self.indexAt(event.pos())
            if idx.isValid():
                model = self.model() if hasattr(self, "model") else None
                item = model.itemFromIndex(idx) if model and idx.column() == 0 else None
                can_drag = (isinstance(item, LayerItem) and item.layer) if model else idx.column() == 0
                if can_drag:
                    self._drag_start_pos = event.pos()
                else:
                    self._drag_start_pos = None
            else:
                self._drag_start_pos = None
        else:
            self._drag_start_pos = None
        try:
            super().mousePressEvent(event)
        except AttributeError:
            pass

    def mouseMoveEvent(self, event):
        if event.buttons() & Qt.MouseButton.LeftButton and self._drag_start_pos is not None:
            delta = event.pos() - self._drag_start_pos
            if delta.manhattanLength() >= _get_drag_distance():
                self.start_group_drag()
                self._drag_start_pos = None
                return
            # Suppress default Qt drag selection (rubberband/multi-row selection while dragging mouse)
            return
        try:
            super().mouseMoveEvent(event)
        except AttributeError:
            pass

    def mouseReleaseEvent(self, event):
        self._drag_start_pos = None
        try:
            super().mouseReleaseEvent(event)
        except AttributeError:
            pass

    def dragEnterEvent(self, event):
        if self._reorder_enabled and event.mimeData().hasFormat("application/x-superlayer-group-reorder"):
            event.acceptProposedAction()
        else:
            try:
                super().dragEnterEvent(event)
            except AttributeError:
                pass

    def dragMoveEvent(self, event):
        if self._reorder_enabled and event.mimeData().hasFormat("application/x-superlayer-group-reorder"):
            idx = self.indexAt(event.pos())
            if idx.isValid():
                if idx.column() != 0:
                    idx = idx.sibling(idx.row(), 0)
                model = self.model()
                target_item = model.itemFromIndex(idx) if model else None
                if not isinstance(target_item, LayerItem) or not target_item.layer:
                    self._drop_target_index = None
                    self._drop_position = None
                    if self.viewport():
                        self.viewport().update()
                    event.ignore()
                    return
                rect = self.visualRect(idx)
                pos_in_item = event.pos().y() - rect.top()
                position = "above" if pos_in_item < rect.height() * 0.5 else "below"

                try:
                    self._drop_target_index = QPersistentModelIndex(idx)
                except (TypeError, AttributeError):
                    self._drop_target_index = idx
                self._drop_position = position
                if self.viewport():
                    self.viewport().update()

                event.acceptProposedAction()
                return
            else:
                self._drop_target_index = None
                self._drop_position = None
                if self.viewport():
                    self.viewport().update()
            event.ignore()
        else:
            try:
                super().dragMoveEvent(event)
            except AttributeError:
                pass

    def dragLeaveEvent(self, event):
        self._drop_target_index = None
        self._drop_position = None
        if self.viewport():
            self.viewport().update()
        try:
            super().dragLeaveEvent(event)
        except AttributeError:
            pass

    def dropEvent(self, event):
        self._drop_target_index = None
        self._drop_position = None
        if self.viewport():
            self.viewport().update()

        if self._reorder_enabled and event.mimeData().hasFormat("application/x-superlayer-group-reorder"):
            idx = self.indexAt(event.pos())
            if idx.isValid():
                if idx.column() != 0:
                    idx = idx.sibling(idx.row(), 0)
                model = self.model()
                if model:
                    target_item = model.itemFromIndex(idx)
                    rect = self.visualRect(idx)
                    pos_in_item = event.pos().y() - rect.top()

                    if not isinstance(target_item, LayerItem) or not target_item.layer:
                        event.ignore()
                        return
                    position = "above" if pos_in_item < rect.height() * 0.5 else "below"

                    try:
                        import json
                        dragged_data = json.loads(event.mimeData().data("application/x-superlayer-group-reorder").data().decode('utf-8'))
                    except Exception:
                        dragged_data = []

                    target_info = {}
                    if isinstance(target_item, LayerItem) and target_item.layer:
                        target_info = {"type": "layer", "id": target_item.layer.id()}

                    if dragged_data and target_info:
                        # Never rebuild this view's model from inside QDropEvent.
                        # The event still owns QModelIndex/internal Qt pointers; a
                        # synchronous refresh invalidates them and can terminate
                        # QGIS in native code after the handler returns.
                        queued_dragged = [dict(item) for item in dragged_data]
                        queued_target = dict(target_info)
                        QTimer.singleShot(
                            0,
                            lambda items=queued_dragged, target=queued_target, pos=position:
                                self.groupReordered.emit(items, target, pos)
                        )
                        event.acceptProposedAction()
                        return
            event.ignore()
        else:
            try:
                super().dropEvent(event)
            except AttributeError:
                pass

    def paintEvent(self, event):
        try:
            super().paintEvent(event)
        except Exception:
            pass  # nosec B110

        drop_target = getattr(self, '_drop_target_index', None)
        drop_pos = getattr(self, '_drop_position', None)
        if drop_target and drop_target.isValid() and drop_pos:
            # PyQt5 does not implicitly convert QPersistentModelIndex for
            # QAbstractItemView.visualRect(), although PyQt6 often does.
            try:
                paint_index = QModelIndex(drop_target)
            except (TypeError, AttributeError):
                # Fallback for bindings without the conversion constructor.
                drop_model = drop_target.model()
                paint_index = drop_model.index(
                    drop_target.row(), drop_target.column(), drop_target.parent()
                )
            try:
                from qgis.PyQt.QtGui import QPainter, QPen, QColor, QBrush
                from qgis.PyQt.QtCore import QPoint
            except ImportError:
                try:
                    from qtpy.QtGui import QPainter, QPen, QColor, QBrush
                    from qtpy.QtCore import QPoint
                except ImportError:
                    try:
                        from PySide2.QtGui import QPainter, QPen, QColor, QBrush
                        from PySide2.QtCore import QPoint
                    except ImportError:
                        try:
                            from PySide6.QtGui import QPainter, QPen, QColor, QBrush
                            from PySide6.QtCore import QPoint
                        except ImportError:
                            return

            viewport = self.viewport()
            if not viewport:
                return

            rect = self.visualRect(paint_index)
            if not rect.isValid():
                return

            # Draw over the viewport after QTreeView has painted.  Qt's built-in
            # indicator is unavailable because this view uses a custom MIME type.
            painter = QPainter(viewport)
            try:
                painter.setRenderHint(QPainter.RenderHint.Antialiasing)
                right = max(rect.right(), viewport.width() - 2)

                if self._drop_position in ("above", "below"):
                    y = rect.top() if self._drop_position == "above" else rect.bottom()
                    painter.setPen(QPen(QColor(0, 120, 212), 3))
                    painter.drawLine(rect.left(), y, right, y)
                    painter.setBrush(QBrush(QColor(0, 120, 212)))
                    painter.drawEllipse(QPoint(rect.left() + 2, y), 3, 3)
                    painter.drawEllipse(QPoint(right - 2, y), 3, 3)
            finally:
                painter.end()

    def start_group_drag(self):
        if not self._reorder_enabled:
            return
        model = self.model()
        if not model:
            return

        dragged_items = []
        selected_parents = set()
        if self.selectionModel():
            for idx in self.selectionModel().selectedIndexes():
                if idx.column() == 0:
                    item = model.itemFromIndex(idx)
                    if isinstance(item, LayerItem) and item.layer:
                        layer_id = item.layer.id()
                        if not any(entry["id"] == layer_id for entry in dragged_items):
                            dragged_items.append({"type": "layer", "id": layer_id, "name": item.layer.name()})
                        if hasattr(item, "parent"):
                            selected_parents.add(item.parent())

        if not dragged_items or len(selected_parents) > 1:
            return

        try:
            from qgis.PyQt.QtGui import QDrag, QPixmap, QPainter, QPen, QColor
            from qgis.PyQt.QtCore import QMimeData, QPoint
        except ImportError:
            try:
                from qtpy.QtGui import QDrag, QPixmap, QPainter, QPen, QColor
                from qtpy.QtCore import QMimeData, QPoint
            except ImportError:
                try:
                    from PySide2.QtGui import QDrag, QPixmap, QPainter, QPen, QColor
                    from PySide2.QtCore import QMimeData, QPoint
                except ImportError:
                    try:
                        from PySide6.QtGui import QDrag, QPixmap, QPainter, QPen, QColor
                        from PySide6.QtCore import QMimeData, QPoint
                    except ImportError:
                        return

        mime_data = QMimeData()
        import json
        mime_data.setData("application/x-superlayer-group-reorder", json.dumps(dragged_items).encode('utf-8'))

        drag = QDrag(self)
        drag.setMimeData(mime_data)

        # Create drag preview pixmap
        try:
            count = len(dragged_items)
            if count == 1:
                display_txt = dragged_items[0].get("name", "图层")
            else:
                display_txt = f"移动 {count} 项"

            pixmap = QPixmap(180, 26)
            pixmap.fill(Qt.GlobalColor.transparent)
            p = QPainter(pixmap)
            p.setRenderHint(QPainter.RenderHint.Antialiasing)
            p.setBrush(QColor(0, 120, 212, 220))
            p.setPen(QPen(QColor(255, 255, 255), 1))
            p.drawRoundedRect(0, 0, 179, 25, 4, 4)
            p.setPen(QColor(255, 255, 255))
            font = p.font()
            font.setBold(True)
            p.setFont(font)
            p.drawText(10, 18, display_txt[:16])
            p.end()

            drag.setPixmap(pixmap)
            drag.setHotSpot(QPoint(10, 13))
        except Exception:
            pass  # nosec B110

        drag.exec(Qt.DropAction.MoveAction)


class SuperLayerDockWidget(QDialog):
    """The main QDialog container integrating flat list view, directory tree view,
    treemap view, toolbar controls, and context menu actions."""

    def __init__(self, iface, parent=None):
        super().__init__(parent)
        self.iface = iface
        self.setWindowTitle("SuperLayer")

        # Configure window properties
        self.resize(600, 450)
        try:
            self.setWindowFlags(self.windowFlags() | Qt.WindowType.WindowMinimizeButtonHint | Qt.WindowType.WindowMaximizeButtonHint)
        except Exception as e:  # noqa: BLE001
            import logging
            logging.getLogger(__name__).warning("Failed to set window flags: %s", e)

        # Setup UI components directly on dialog
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)

        # Toolbar
        self.toolbar = QToolBar()
        self.toolbar.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        self.layout.addWidget(self.toolbar)

        # Tag Filter Row container
        self.filter_container = QWidget()
        self.filter_container.setObjectName("filterContainer")
        self.filter_layout = QHBoxLayout(self.filter_container)
        self.filter_layout.setContentsMargins(10, 4, 10, 4)
        self.filter_layout.setSpacing(6)
        self.filter_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)

        # Tag Filter Label indicator
        self.filter_label = QLabel(tr("格式过滤:"))
        self.filter_label.setStyleSheet("color: #6c757d; font-size: 11px; font-weight: bold;")
        self.filter_layout.addWidget(self.filter_label)

        self.layout.addWidget(self.filter_container)

        # Selected filter state and cache
        self.current_filter_format = None
        # None means the live canvas visibility state. A string stores the
        # QGIS map theme used when the visibility filter button is enabled.
        self.current_map_theme = None
        self._current_avail_formats = []
        self.filter_buttons = {}

        # Stacked View
        self.stacked_widget = QStackedWidget()
        self.layout.addWidget(self.stacked_widget, 1)

        self.physical_tree_view = DraggableTreeView()
        self.physical_tree_view.setObjectName("physicalTreeView")
        self.physical_tree_view.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self.physical_tree_view.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.physical_tree_view.setAllColumnsShowFocus(True)
        self.physical_tree_view.setAlternatingRowColors(True)

        # The group panel uses QGIS' own model and Qt drag/drop implementation.
        self.group_tree_view = QTreeView()
        self.group_tree_view.setObjectName("groupTreeView")
        self.group_tree_view.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self.group_tree_view.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.group_tree_view.setAllColumnsShowFocus(True)
        self.group_tree_view.setAlternatingRowColors(True)

        self.treemap_view = TreeMapWidget()
        self.mindmap_view = MindMapView()
        self.layer_board_view = LayerBoardWidget(self.iface, self) # NEW PAGE

        self.stacked_widget.addWidget(self.physical_tree_view)
        self.stacked_widget.addWidget(self.group_tree_view)
        self.stacked_widget.addWidget(self.treemap_view)
        self.stacked_widget.addWidget(self.mindmap_view)
        self.stacked_widget.addWidget(self.layer_board_view) # NEW PAGE

        # Models
        self.physical_model = LayerTreeModel()
        project = QgsProject.instance()
        group_root = project.layerTreeRoot() if project and hasattr(project, "layerTreeRoot") else None
        self.group_model = LayerOrderTreeModel(group_root)


        self.physical_tree_view.setModel(self.physical_model)
        self.group_tree_view.setModel(self.group_model)
        self.group_tree_view.setDragEnabled(True)
        self.group_tree_view.setAcceptDrops(True)
        self.group_tree_view.setDropIndicatorShown(True)
        if hasattr(self.group_tree_view, "setDragDropMode"):
            drag_drop_scope = getattr(QAbstractItemView, "DragDropMode", QAbstractItemView)
            mode = getattr(drag_drop_scope, "InternalMove", None)
            if mode is not None:
                self.group_tree_view.setDragDropMode(mode)

        # Column widths are applied in refresh() after rebuild_model()

        # States
        self.group_by_physical = True

        self._setup_toolbar()
        self._setup_connections()
        self._apply_styles()
        self.refresh()

    def _apply_styles(self):
        """Applies a premium, modern design style to the panel."""
        self.setStyleSheet("""
            QToolBar {
                background: #f8f9fa;
                border-bottom: 1px solid #dee2e6;
                spacing: 2px;
                padding: 2px;
            }
            QToolBar QToolButton {
                background: transparent;
                border: 1px solid transparent;
                border-radius: 4px;
                padding: 2px 1px;
                font-family: "Microsoft YaHei", "Segoe UI", sans-serif;
                font-size: 13px;
                font-weight: 500;
                color: #495057;
            }
            QToolBar QToolButton:hover {
                background: #e9ecef;
                color: #212529;
            }
            QToolBar QToolButton:checked {
                background: #0d6efd;
                color: white;
            }
            QStackedWidget > QTreeView, QGraphicsView {
                background-color: #ffffff;
                border: none;
                alternate-background-color: #f8f9fa;
                selection-background-color: #1484dc;
                selection-color: #ffffff;
                font-family: "Microsoft YaHei", "Segoe UI", sans-serif;
                font-size: 12px;
                color: #212529;
            }
            QStackedWidget > QTreeView::item {
                height: 25px;
                border-bottom: 1px solid #f1f3f5;
            }
            QStackedWidget > QTreeView::item:hover:!selected {
                background-color: #f1f3f5;
            }
            QStackedWidget > QTreeView::item:selected {
                background-color: #1484dc;
                color: #ffffff;
            }
            QStackedWidget > QTreeView::item:selected:active {
                background-color: #1484dc;
                color: #ffffff;
            }
            QStackedWidget > QTreeView::item:selected:!active {
                background-color: #1484dc;
                color: #ffffff;
            }
            QHeaderView::section {
                background-color: #f8f9fa;
                color: #495057;
                padding: 6px;
                font-weight: bold;
                border: none;
                border-bottom: 2px solid #dee2e6;
            }
        """)

        # Keep visibility state visually independent from row selection. Native
        # Windows/Qt styles recolor check indicators with HighlightedText, making
        # a selected visible layer look faded or disabled.
        icon_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "icons_panel")
        checked_icon = os.path.join(icon_dir, "Visibility_Checked.svg").replace("\\", "/")
        unchecked_icon = os.path.join(icon_dir, "Visibility_Unchecked.svg").replace("\\", "/")
        partial_icon = os.path.join(icon_dir, "Visibility_Partial.svg").replace("\\", "/")
        if hasattr(self.group_tree_view, "setStyleSheet"):
            self.group_tree_view.setStyleSheet(f"""
                QTreeView::indicator {{
                    width: 16px;
                    height: 16px;
                }}
                QTreeView::indicator:checked {{ image: url(\"{checked_icon}\"); }}
                QTreeView::indicator:unchecked {{ image: url(\"{unchecked_icon}\"); }}
                QTreeView::indicator:indeterminate {{ image: url(\"{partial_icon}\"); }}
            """)

    def _setup_toolbar(self):
        if hasattr(self.toolbar, 'setToolButtonStyle') and hasattr(Qt, 'ToolButtonTextBesideIcon'):
            self.toolbar.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)

        if hasattr(self.toolbar, 'setIconSize'):
            self.toolbar.setIconSize(QSize(16, 16))

        icon_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "icons_panel_toolbar")

        def get_toolbar_icon(name):
            icon_path = os.path.join(icon_dir, name)
            if os.path.exists(icon_path):
                return QIcon(icon_path)
            return QIcon()

        self.view_group = QActionGroup(self)
        self.view_group.setExclusive(True)

        self.act_physical_tree = QAction(get_toolbar_icon("panel_toolbar_document.svg"), tr("文件夹分类"), self)
        self.act_physical_tree.setCheckable(True)
        self.act_physical_tree.setChecked(True)
        self.act_physical_tree.triggered.connect(lambda: self.switch_view(0))
        self.view_group.addAction(self.act_physical_tree)
        self.toolbar.addAction(self.act_physical_tree)

        self.act_group_tree = QAction(get_toolbar_icon("panel_toolbar_group.svg"), tr("图层分类"), self)
        self.act_group_tree.setCheckable(True)
        self.act_group_tree.triggered.connect(lambda: self.switch_view(1))
        self.view_group.addAction(self.act_group_tree)
        self.toolbar.addAction(self.act_group_tree)

        self.act_treemap = QAction(get_toolbar_icon("panel_toolbar_Rec-Tree_Chart.svg"), tr("矩形树状图"), self)
        self.act_treemap.setCheckable(True)
        self.act_treemap.triggered.connect(lambda: self.switch_view(2))
        self.view_group.addAction(self.act_treemap)
        self.toolbar.addAction(self.act_treemap)

        self.act_mindmap = QAction(get_toolbar_icon("panel_toolbar_Mindmap.svg"), tr("路径导图"), self)
        self.act_mindmap.setCheckable(True)
        self.act_mindmap.triggered.connect(lambda: self.switch_view(3))
        self.view_group.addAction(self.act_mindmap)
        self.toolbar.addAction(self.act_mindmap)

        # Add new Attribute Board Action
        self.act_layer_board = QAction(get_toolbar_icon("panel_toolbar_batch-modify.svg"), tr("批量修改"), self)
        self.act_layer_board.setCheckable(True)
        self.act_layer_board.triggered.connect(lambda: self.switch_view(4))
        self.view_group.addAction(self.act_layer_board)
        self.toolbar.addAction(self.act_layer_board)

        self.toolbar.addSeparator()

        self.act_refresh = QAction(get_toolbar_icon("panel_toolbar_refresh.svg"), tr("刷新"), self)
        self.act_refresh.triggered.connect(self.refresh)
        self.toolbar.addAction(self.act_refresh)

        # Add expanding spacer to push the filter button to the right end
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        self.toolbar.addWidget(spacer)

        # Add Filter Visible Only button to main toolbar
        self.btn_filter_visible = QToolButton()
        self.btn_filter_visible.setObjectName("btnFilterVisible")
        self.btn_filter_visible.setCheckable(True)
        self.btn_filter_visible.setToolTip(tr("只展示显示的图层"))
        self.btn_filter_visible.setIconSize(QSize(16, 16))

        # Load filter visible layers icon
        plugin_dir = os.path.dirname(os.path.abspath(__file__))
        icon_path = os.path.join(plugin_dir, "icons_panel", "Filter_visible_layers.svg")
        if os.path.exists(icon_path):
            self.btn_filter_visible.setIcon(QIcon(icon_path))

        self.btn_filter_visible.toggled.connect(self.on_filter_visible_toggled)
        if hasattr(self.btn_filter_visible, 'setContextMenuPolicy'):
            self.btn_filter_visible.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        if hasattr(self.btn_filter_visible, 'customContextMenuRequested'):
            self.btn_filter_visible.customContextMenuRequested.connect(self.show_filter_context_menu)

        # Styled beautifully matching application theme
        self.btn_filter_visible.setStyleSheet("""
            QToolButton#btnFilterVisible {
                border: none;
                border-radius: 4px;
                background-color: transparent;
                padding: 4px;
                margin-right: 8px;
                margin-top: 2px;
                margin-bottom: 2px;
            }
            QToolButton#btnFilterVisible:hover {
                background-color: rgba(0, 0, 0, 0.06);
            }
            QToolButton#btnFilterVisible:pressed {
                background-color: rgba(0, 0, 0, 0.12);
            }
            QToolButton#btnFilterVisible:checked {
                background-color: #80cc28;
                border: 1px solid #70b320;
                padding: 3px;
            }
            QToolButton#btnFilterVisible:checked:hover {
                background-color: #8ce62d;
            }
        """)
        self.toolbar.addWidget(self.btn_filter_visible)

    def _setup_connections(self):
        # Right click menu context
        self.physical_tree_view.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.physical_tree_view.customContextMenuRequested.connect(self.show_physical_tree_context_menu)
        self.physical_tree_view.layersDropped.connect(self.handle_multiple_layers_relocation)

        self.group_tree_view.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.group_tree_view.customContextMenuRequested.connect(self.show_group_tree_context_menu)

        self.treemap_view.contextMenuTriggered.connect(self.show_treemap_context_menu)

        # Focus on double click
        self.physical_tree_view.doubleClicked.connect(self.on_item_double_clicked)
        self.group_tree_view.doubleClicked.connect(self.on_item_double_clicked)
        self.treemap_view.layerSelected.connect(self.focus_layer_by_id)

        # Mind map connections
        self.mindmap_view.layerSelected.connect(self.focus_layer_by_id)
        self.mindmap_view.layerDoubleClicked.connect(self.focus_layer_by_id)
        self.mindmap_view.contextMenuTriggered.connect(self.show_treemap_context_menu)
        self.mindmap_view.layerRelocationRequested.connect(self.handle_layer_relocation)
        self.mindmap_view.folderRelocationRequested.connect(self.handle_folder_relocation)

        # Model item changed connections
        self.physical_model.itemChanged.connect(self.on_item_changed)

        # Debounced refresh timer for safe asynchronous tree updates
        self._refresh_timer = QTimer(self)
        self._refresh_timer.setSingleShot(True)
        self._refresh_timer.setInterval(50)  # 50ms debounce
        self._refresh_timer.timeout.connect(lambda: self.refresh())

        # Auto refresh on QGIS layer tree visibility changes
        try:
            from qgis.core import QgsProject
            project = QgsProject.instance()
            if project and project.layerTreeRoot() and hasattr(project.layerTreeRoot(), 'visibilityChanged'):
                project.layerTreeRoot().visibilityChanged.connect(self.on_visibility_changed)
        except (ImportError, AttributeError, RuntimeError) as e:
            import logging
            logging.getLogger(__name__).debug("Failed to connect visibilityChanged signal: %s", e)

    def set_tag_button_active(self, btn, active):
        try:
            from .layer_model import get_format_color_dict
        except ImportError:
            try:
                from layer_model import get_format_color_dict
            except ImportError:
                def get_format_color_dict(f):
                    return {"bg": "#f1f3f5", "border": "#ced4da", "text": "#495057", "treemap": "#0d6efd"}

        if hasattr(btn, 'text'):
            btn_text = btn.text()
        else:
            btn_text = getattr(btn, '_text', "")
        colors = get_format_color_dict(btn_text)

        if active:
            bg = colors["treemap"]
            text_color = "#ffffff"
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {bg};
                    color: {text_color};
                    border: 1px solid {bg};
                    border-radius: 12px;
                    padding: 3px 10px;
                    font-size: 11px;
                    font-weight: bold;
                }}
            """)
        else:
            bg = colors["bg"]
            text_color = colors["text"]
            border = colors["border"]
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {bg};
                    color: {text_color};
                    border: 1px solid {border};
                    border-radius: 12px;
                    padding: 3px 10px;
                    font-size: 11px;
                    font-weight: bold;
                }}
                QPushButton:hover {{
                    background-color: {border};
                    color: {text_color};
                }}
            """)

    def update_filter_tags(self):
        try:
            from .layer_model import get_layer_format
        except ImportError:
            def get_layer_format(layer):
                source = getattr(layer, 'source', lambda: '')()
                if source.endswith('.shp'): return 'shp'
                if source.endswith('.tif'): return 'tif'
                return 'other'

        project = QgsProject.instance()
        formats = set()
        has_invalid = False
        if project:
            for layer in project.mapLayers().values():
                if hasattr(layer, 'isValid') and not layer.isValid():
                    has_invalid = True
                fmt = get_layer_format(layer)
                if fmt:
                    formats.add(fmt.upper())
            if has_invalid:
                formats.add("不可用图层")

        priority = {"SHP": 1, "GPKG": 2, "GDB": 3, "TIF": 4, "TIFF": 5, "在线图层": 10, "不可用图层": 15, "其他": 20}
        sorted_formats = sorted(list(formats), key=lambda x: (priority.get(x, 5), x))

        if self.current_filter_format and self.current_filter_format not in sorted_formats:
            self.current_filter_format = None

        existing_formats = getattr(self, '_current_avail_formats', [])
        if sorted_formats != existing_formats:
            self._current_avail_formats = sorted_formats

            while self.filter_layout.count() > 1:
                item = self.filter_layout.takeAt(1)
                if item:
                    widget = item.widget()
                    if widget:
                        widget.deleteLater()

            btn_all = QPushButton(tr("全部"))
            self.filter_layout.addWidget(btn_all)
            btn_all.clicked.connect(lambda: self.set_filter_format(None))
            self.filter_buttons = {"全部": btn_all}

            for fmt in sorted_formats:
                btn = QPushButton(fmt)
                self.filter_layout.addWidget(btn)
                btn.clicked.connect(lambda checked, f=fmt: self.set_filter_format(f))
                self.filter_buttons[fmt] = btn

        active_key = self.current_filter_format if self.current_filter_format else "全部"
        for key, btn in self.filter_buttons.items():
            self.set_tag_button_active(btn, key == active_key)

    def set_filter_format(self, fmt):
        if self.current_filter_format == fmt:
            return
        self.current_filter_format = fmt

        active_key = fmt if fmt else "全部"
        for key, btn in self.filter_buttons.items():
            self.set_tag_button_active(btn, key == active_key)

        self.refresh()

    def _get_filtered_layers(self, filter_str):
        project = QgsProject.instance()
        layers = []
        if project:
            try:
                from .layer_model import get_layer_format, is_layer_effectively_visible
            except ImportError:
                try:
                    from layer_model import get_layer_format, is_layer_effectively_visible
                except ImportError:
                    def get_layer_format(layer):
                        source = getattr(layer, 'source', lambda: '')()
                        if source.endswith('.shp'): return 'shp'
                        if source.endswith('.tif'): return 'tif'
                        return 'other'
                    def is_layer_effectively_visible(layer):
                        return True

            all_layers = list(project.mapLayers().values())
            if filter_str:
                if filter_str == "不可用图层":
                    layers = [layer for layer in all_layers if hasattr(layer, 'isValid') and not layer.isValid()]
                else:
                    layers = [layer for layer in all_layers if get_layer_format(layer) == filter_str]
            else:
                layers = all_layers

            if hasattr(self, 'btn_filter_visible') and self.btn_filter_visible.isChecked():
                theme_name = getattr(self, 'current_map_theme', None)
                if theme_name:
                    theme_layer_ids = self._map_theme_layer_ids(theme_name)
                    layers = [layer for layer in layers if layer.id() in theme_layer_ids]
                else:
                    layers = [layer for layer in layers if is_layer_effectively_visible(layer)]
        return layers

    def _map_theme_layer_ids(self, theme_name):
        """Return layer IDs recorded as visible in a QGIS map theme."""
        project = QgsProject.instance()
        if not project or not theme_name or not hasattr(project, 'mapThemeCollection'):
            return set()
        collection = project.mapThemeCollection()
        if not collection:
            return set()
        try:
            visible_layers = collection.mapThemeVisibleLayers(theme_name)
        except Exception:
            return set()
        result = set()
        for layer in visible_layers or []:
            if hasattr(layer, 'id'):
                result.add(layer.id())
            elif isinstance(layer, str):
                result.add(layer)
        return result

    def set_visibility_filter_source(self, theme_name=None):
        """Select live canvas visibility or a map theme and enable filtering."""
        self.current_map_theme = theme_name
        if theme_name:
            tooltip = tr("按地图主题过滤：{}").format(theme_name)
        else:
            tooltip = tr("只展示当前地图中显示的图层")
        self.btn_filter_visible.setToolTip(tooltip)
        if not self.btn_filter_visible.isChecked():
            self.btn_filter_visible.setChecked(True)
        else:
            self.on_filter_visible_toggled(True)

    def show_filter_context_menu(self, pos):
        """Open the visibility-filter source menu without applying a map theme."""
        menu = QMenu(self)
        live_action = menu.addAction(tr("当前地图显示状态"))
        live_action.setCheckable(True)
        live_action.setChecked(getattr(self, 'current_map_theme', None) is None)
        live_action.triggered.connect(lambda checked=False: self.set_visibility_filter_source(None))

        theme_menu = menu.addMenu(tr("QGIS 地图主题"))
        project = QgsProject.instance()
        collection = project.mapThemeCollection() if project and hasattr(project, 'mapThemeCollection') else None
        try:
            theme_names = sorted(collection.mapThemes()) if collection else []
        except Exception:
            theme_names = []
        if not theme_names:
            empty_action = theme_menu.addAction(tr("没有可用的地图主题"))
            empty_action.setEnabled(False)
        else:
            for theme_name in theme_names:
                action = theme_menu.addAction(theme_name)
                action.setCheckable(True)
                action.setChecked(theme_name == getattr(self, 'current_map_theme', None))
                action.triggered.connect(
                    lambda checked=False, name=theme_name: self.set_visibility_filter_source(name)
                )

        global_pos = self.btn_filter_visible.mapToGlobal(pos) if hasattr(self.btn_filter_visible, 'mapToGlobal') else pos
        menu.exec(global_pos)

    def _set_group_reorder_actions_enabled(self, enabled):
        """Enable both order actions without coupling tests to a Qt binding."""
        for action_name in ("act_group_move_up", "act_group_move_down"):
            action = getattr(self, action_name, None)
            if action is not None and hasattr(action, "setEnabled"):
                action.setEnabled(bool(enabled))

    def _update_group_reorder_actions(self, filter_str=None, filter_visible=None):
        """Ordering is safe only in the complete, unfiltered group view."""
        if filter_str is None:
            filter_str = self.current_filter_format.lower() if self.current_filter_format else None
        if filter_visible is None:
            button = getattr(self, "btn_filter_visible", None)
            filter_visible = bool(button and button.isChecked())
        stacked = getattr(self, "stacked_widget", None)
        in_group_view = bool(stacked and stacked.currentIndex() == 1)
        for action_name in ("act_group_move_up", "act_group_move_down"):
            action = getattr(self, action_name, None)
            if action is not None and hasattr(action, "setVisible"):
                action.setVisible(in_group_view)
        self._set_group_reorder_actions_enabled(
            in_group_view and not filter_str and not filter_visible
        )

    def move_selected_group_layer(self, direction):
        """Move one selected layer one position within its current QGIS group."""
        if direction not in (-1, 1):
            return

        filter_str = self.current_filter_format.lower() if self.current_filter_format else None
        filter_visible = bool(self.btn_filter_visible.isChecked()) if hasattr(self, "btn_filter_visible") else False
        if self.stacked_widget.currentIndex() != 1 or filter_str or filter_visible:
            return

        selection_model = self.group_tree_view.selectionModel()
        if not selection_model:
            return
        selected_layers = []
        for index in selection_model.selectedIndexes():
            if index.column() != 0:
                continue
            item = self.group_model.itemFromIndex(index)
            if isinstance(item, LayerItem) and item.layer and item.layer.id() not in selected_layers:
                selected_layers.append(item.layer.id())
        if len(selected_layers) != 1:
            return

        root = QgsProject.instance().layerTreeRoot()
        source_node = root.findLayer(selected_layers[0]) if root else None
        parent = source_node.parent() if source_node else None
        if not parent:
            return
        children = parent.children()
        try:
            source_row = children.index(source_node)
        except ValueError:
            return

        target_row = source_row + direction
        if target_row < 0 or target_row >= len(children):
            return
        target_node = children[target_row]
        target_layer = target_node.layer() if hasattr(target_node, "layer") else None
        if not target_layer:
            return

        self.handle_group_reorder(
            [{"type": "layer", "id": selected_layers[0]}],
            {"type": "layer", "id": target_layer.id()},
            "above" if direction < 0 else "below",
        )

    def switch_view(self, index):
        self.act_physical_tree.setChecked(index == 0)
        self.act_group_tree.setChecked(index == 1)
        self.act_treemap.setChecked(index == 2)
        self.act_mindmap.setChecked(index == 3)
        self.act_layer_board.setChecked(index == 4) # NEW
        self.stacked_widget.setCurrentIndex(index)

        if index == 4:
            self.filter_container.hide()
        else:
            self.filter_container.show()

        filter_str = self.current_filter_format.lower() if self.current_filter_format else None
        layers = self._get_filtered_layers(filter_str)

        if index == 2:
            self.treemap_view.set_layers(layers)
        elif index == 3:
            self.mindmap_view.set_layers(layers)
        elif index == 4:
            # Refresh Attribute Board when switched to
            self.layer_board_view.populateLayerTable('vector')
            self.layer_board_view.populateLayerTable('raster')
            self.layer_board_view.populateAvailableEncodingList()

    def _apply_column_widths(self):
        """Apply fixed column widths after model rebuild."""
        for view in (self.physical_tree_view, self.group_tree_view):
            view.setColumnWidth(0, 300)
            view.setColumnWidth(1, 80)
            view.setColumnWidth(2, 250)
            hdr = view.header()
            if hdr and hdr.count() > 2:
                hdr.setSectionResizeMode(0, QHeaderView.ResizeMode.Interactive)
                hdr.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
                hdr.setSectionResizeMode(2, QHeaderView.ResizeMode.Interactive)

    def on_visibility_changed(self, *args, **kwargs):
        if hasattr(self, '_refresh_timer') and self._refresh_timer:
            self._refresh_timer.start()
        else:
            self.refresh()

    def on_filter_visible_toggled(self, checked):
        theme_layer_ids = None
        if checked and getattr(self, 'current_map_theme', None):
            theme_layer_ids = self._map_theme_layer_ids(self.current_map_theme)
        if hasattr(self, 'group_model') and hasattr(self.group_model, 'set_theme_layer_ids'):
            self.group_model.set_theme_layer_ids(theme_layer_ids)
        if hasattr(self, 'layer_board_view') and self.layer_board_view:
            if hasattr(self.layer_board_view, 'set_visibility_filter'):
                self.layer_board_view.set_visibility_filter(checked, theme_layer_ids)
            else:
                self.layer_board_view.on_filter_visible_toggled(checked)
        if checked:
            theme_name = getattr(self, 'current_map_theme', None)
            if theme_name:
                self.btn_filter_visible.setToolTip(tr("按地图主题过滤：{}").format(theme_name))
            else:
                self.btn_filter_visible.setToolTip(tr("只展示当前地图中显示的图层"))
        else:
            self.btn_filter_visible.setToolTip(tr("图层过滤已关闭；右键选择地图主题"))
        self.refresh()

    def refresh(self, *args, **kwargs):
        self._is_refreshing = True
        try:
            # Import QItemSelectionModel dynamically with fallback
            try:
                from qgis.PyQt.QtCore import QItemSelectionModel
            except ImportError:
                try:
                    from qtpy.QtCore import QItemSelectionModel
                except ImportError:
                    try:
                        from PySide2.QtCore import QItemSelectionModel
                    except ImportError:
                        try:
                            from PySide6.QtCore import QItemSelectionModel
                        except ImportError:
                            class QItemSelectionModel:
                                class SelectionFlag:
                                    ClearAndSelect = 1
                                    Rows = 2

            def get_tree_state(tree_view, model):
                expanded_keys = set()
                selected_keys = set()

                if not hasattr(model, 'index') or 'Mock' in type(model).__name__:
                    return expanded_keys, selected_keys, 0, 0

                # Check method availability to support mock testing objects safely
                has_is_expanded = hasattr(tree_view, 'isExpanded')
                has_selection_model = hasattr(tree_view, 'selectionModel') and tree_view.selectionModel() is not None and hasattr(tree_view.selectionModel(), 'isSelected')

                def traverse(index):
                    if not index.isValid() or 'Mock' in type(index).__name__:
                        return
                    item = model.itemFromIndex(index)
                    if item:
                        key = item.data(Qt.ItemDataRole.UserRole)
                        if not key:
                            key = item.text()
                        if key:
                            if has_is_expanded and tree_view.isExpanded(index):
                                expanded_keys.add(key)
                            if has_selection_model and tree_view.selectionModel().isSelected(index):
                                selected_keys.add(key)
                    for row in range(model.rowCount(index)):
                        traverse(model.index(row, 0, index))

                for row in range(model.rowCount()):
                    traverse(model.index(row, 0))

                v_val = 0
                h_val = 0
                if hasattr(tree_view, 'verticalScrollBar') and tree_view.verticalScrollBar():
                    v_val = tree_view.verticalScrollBar().value()
                if hasattr(tree_view, 'horizontalScrollBar') and tree_view.horizontalScrollBar():
                    h_val = tree_view.horizontalScrollBar().value()
                return expanded_keys, selected_keys, v_val, h_val

            def restore_tree_state(tree_view, model, state, default_expand_all=False):
                if not state:
                    if default_expand_all:
                        if hasattr(tree_view, 'expandAll'):
                            tree_view.expandAll()
                    else:
                        if hasattr(tree_view, 'collapseAll'):
                            tree_view.collapseAll()
                    return
                if not hasattr(model, 'index') or 'Mock' in type(model).__name__:
                    return

                expanded_keys, selected_keys, v_val, h_val = state
                selection_model = tree_view.selectionModel() if hasattr(tree_view, 'selectionModel') else None
                has_set_expanded = hasattr(tree_view, 'setExpanded')

                def traverse(index):
                    if not index.isValid() or 'Mock' in type(index).__name__:
                        return
                    item = model.itemFromIndex(index)
                    if item:
                        key = item.data(Qt.ItemDataRole.UserRole)
                        if not key:
                            key = item.text()
                        if key:
                            # Restore expanded state
                            if has_set_expanded:
                                if key in expanded_keys:
                                    tree_view.setExpanded(index, True)
                                else:
                                    if default_expand_all and not expanded_keys:
                                        tree_view.setExpanded(index, True)
                                    else:
                                        tree_view.setExpanded(index, False)

                            # Restore selection state
                            if selection_model and hasattr(selection_model, 'select') and key in selected_keys:
                                selection_model.select(index, QItemSelectionModel.SelectionFlag.ClearAndSelect | QItemSelectionModel.SelectionFlag.Rows)

                    for row in range(model.rowCount(index)):
                        traverse(model.index(row, 0, index))

                if selection_model and hasattr(selection_model, 'clearSelection'):
                    selection_model.clearSelection()
                for row in range(model.rowCount()):
                    traverse(model.index(row, 0))

                if hasattr(tree_view, 'verticalScrollBar') and tree_view.verticalScrollBar():
                    tree_view.verticalScrollBar().setValue(v_val)
                if hasattr(tree_view, 'horizontalScrollBar') and tree_view.horizontalScrollBar():
                    tree_view.horizontalScrollBar().setValue(h_val)

            # Check if this is the first load (when model is empty or mocked)
            is_first_load = True
            if 'Mock' not in type(self.physical_model).__name__:
                is_first_load = (self.physical_model.rowCount() == 0)
            phys_state = None
            if not is_first_load:
                phys_state = get_tree_state(self.physical_tree_view, self.physical_model)

            self.update_filter_tags()
            filter_str = self.current_filter_format.lower() if self.current_filter_format else None

            # Check if visibility filter is checked
            filter_visible = self.btn_filter_visible.isChecked() if hasattr(self, 'btn_filter_visible') else False

            # A filtered tree does not contain every sibling, so its visible row
            # positions cannot unambiguously represent the real QGIS layer order.
            # 1. Rebuild physical tree model
            theme_layer_ids = None
            if filter_visible and getattr(self, 'current_map_theme', None):
                theme_layer_ids = self._map_theme_layer_ids(self.current_map_theme)
            self.physical_model.rebuild_model(
                group_by_physical=True,
                filter_format=filter_str,
                filter_visible=filter_visible and theme_layer_ids is None,
                filter_layer_ids=theme_layer_ids,
            )

            # 3. Re-apply column widths (model rebuild resets them)
            self._apply_column_widths()

            # Make the separator row span across all columns to prevent text truncation
            model = self.physical_model
            for row in range(model.rowCount()):
                item = model.item(row, 0)
                if item and item.data(Qt.ItemDataRole.UserRole) == "separator":
                    self.physical_tree_view.setFirstColumnSpanned(row, QModelIndex(), True)
                    break

            # Restore tree view states
            restore_tree_state(self.physical_tree_view, self.physical_model, phys_state, default_expand_all=True)

            layers = self._get_filtered_layers(filter_str)

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

    def on_item_double_clicked(self, index):
        if index.column() > 0:
            index = index.sibling(index.row(), 0)

        model = self.physical_model
        if hasattr(index, 'model') and index.model():
            model = index.model()

        if isinstance(model, LayerOrderTreeModel):
            node = model.index2node(index)
            layer = node.layer() if node and hasattr(node, "layer") else None
            if layer:
                self.focus_layer_by_id(layer.id())
            return

        item = model.itemFromIndex(index)
        if isinstance(item, LayerItem):
            self.focus_layer_by_id(item.layer.id())

    def on_item_changed(self, item):
        # Prevent recursion during model building/refresh
        if hasattr(self, '_is_refreshing') and self._is_refreshing:
            return

        try:
            from .layer_model import LayerItem, FolderItem
        except ImportError:
            from layer_model import LayerItem, FolderItem

        new_name = item.text()

        if isinstance(item, LayerItem):
            layer = item.layer
            if layer:
                # 1. Handle Rename
                if new_name and layer.name() != new_name:
                    layer.setName(new_name)
                    self.refresh()
                    return

                # 2. Handle CheckState change (Visibility)
                try:
                    project = QgsProject.instance()
                    if project and project.layerTreeRoot():
                        node = project.layerTreeRoot().findLayer(layer.id())
                        if node:
                            is_checked = (item.checkState() == Qt.CheckState.Checked)
                            if node.itemVisibilityChecked() != is_checked:
                                node.setItemVisibilityChecked(is_checked)
                except Exception as e:
                    import logging
                    logging.getLogger(__name__).debug("Failed to set layer tree visibility: %s", e)

        elif isinstance(item, FolderItem):
            if not new_name:
                return
            # If it's a QGIS virtual group, rename the QGIS group node
            if not item.is_physical:
                old_name = item.data(Qt.ItemDataRole.UserRole)
                if old_name and old_name != new_name:
                    root = QgsProject.instance().layerTreeRoot()
                    if root:
                        group_node = root.findGroup(old_name)
                        if group_node:
                            group_node.setName(new_name)
                            item.setData(new_name, Qt.ItemDataRole.UserRole)
                            self.refresh()

    def focus_layer_by_id(self, layer_id):
        layer = QgsProject.instance().mapLayer(layer_id)
        if layer:
            self.iface.setActiveLayer(layer)

    def get_selected_layers(self, view):
        layers = []
        for idx in view.selectionModel().selectedIndexes():
            if idx.column() > 0:
                continue

            model = view.model()
            if isinstance(model, LayerOrderTreeModel):
                node = model.index2node(idx)
                layer = node.layer() if node and hasattr(node, "layer") else None
                if layer:
                    layers.append(layer)
                continue
            item = model.itemFromIndex(idx)
            if item and isinstance(item, LayerItem):
                layers.append(item.layer)
        return layers

    def show_physical_tree_context_menu(self, pos):
        idx = self.physical_tree_view.indexAt(pos)
        if idx.isValid():
            model = self.physical_tree_view.model()
            col0_idx = idx.sibling(idx.row(), 0)
            item = model.itemFromIndex(col0_idx)
            if item:
                if idx.column() == 2 or isinstance(item, FolderItem):
                    folder_path = None
                    if isinstance(item, FolderItem):
                        folder_path = item.folder_path
                    elif isinstance(item, LayerItem) and item.layer:
                        source = item.layer.source()
                        phys_path, _ = split_qgis_source(source)
                        actual_path = resolve_physical_path(phys_path)
                        if actual_path:
                            folder_path = os.path.dirname(actual_path)

                    if folder_path:
                        self._create_folder_context_menu(folder_path, self.physical_tree_view.mapToGlobal(pos), folder_item=item if isinstance(item, FolderItem) else None)
                elif isinstance(item, LayerItem):
                    # Multi-selection support: check if clicked item is selected
                    sm = self.physical_tree_view.selectionModel()
                    is_selected = sm.isSelected(idx) if sm else False
                    layers = []
                    if is_selected:
                        for index in sm.selectedIndexes():
                            if index.column() == 0:
                                sel_item = model.itemFromIndex(index)
                                if isinstance(sel_item, LayerItem) and sel_item.layer:
                                    layers.append(sel_item.layer)
                    if not layers and item.layer:
                        layers = [item.layer]
                    self._create_layer_context_menu(layers, self.physical_tree_view.mapToGlobal(pos))

    def show_group_tree_context_menu(self, pos):
        idx = self.group_tree_view.indexAt(pos)
        if idx.isValid():
            model = self.group_tree_view.model()
            col0_idx = idx.sibling(idx.row(), 0)
            if isinstance(model, LayerOrderTreeModel):
                node = model.index2node(col0_idx)
                layer = node.layer() if node and hasattr(node, "layer") else None
                if layer:
                    layers = []
                    selection_model = self.group_tree_view.selectionModel()
                    selected = selection_model.selectedIndexes() if selection_model else []
                    for selected_index in selected:
                        if selected_index.column() != 0:
                            continue
                        selected_node = model.index2node(selected_index)
                        selected_layer = (
                            selected_node.layer()
                            if selected_node and hasattr(selected_node, "layer") else None
                        )
                        if selected_layer and selected_layer not in layers:
                            layers.append(selected_layer)
                    if layer not in layers:
                        layers = [layer]
                    self._create_layer_context_menu(layers, self.group_tree_view.mapToGlobal(pos))
                elif node and hasattr(node, "children"):
                    folder_item = FolderItem(node.name(), is_physical=False, group_node=node)
                    self._create_folder_context_menu(
                        node.name(), self.group_tree_view.mapToGlobal(pos), folder_item=folder_item
                    )
                return
            item = model.itemFromIndex(col0_idx)
            if item:
                if idx.column() == 2 or isinstance(item, FolderItem):
                    folder_path = None
                    if isinstance(item, FolderItem):
                        folder_path = item.folder_path
                    elif isinstance(item, LayerItem) and item.layer:
                        source = item.layer.source()
                        phys_path, _ = split_qgis_source(source)
                        actual_path = resolve_physical_path(phys_path)
                        if actual_path:
                            folder_path = os.path.dirname(actual_path)

                    if folder_path:
                        self._create_folder_context_menu(folder_path, self.group_tree_view.mapToGlobal(pos), folder_item=item if isinstance(item, FolderItem) else None)
                elif isinstance(item, LayerItem):
                    # Multi-selection support: check if clicked item is selected
                    sm = self.group_tree_view.selectionModel()
                    is_selected = sm.isSelected(idx) if sm else False
                    layers = []
                    if is_selected:
                        for index in sm.selectedIndexes():
                            if index.column() == 0:
                                sel_item = model.itemFromIndex(index)
                                if isinstance(sel_item, LayerItem) and sel_item.layer:
                                    layers.append(sel_item.layer)
                    if not layers and item.layer:
                        layers = [item.layer]
                    self._create_layer_context_menu(layers, self.group_tree_view.mapToGlobal(pos))

    def show_treemap_context_menu(self, node, global_pos):
        layers = []
        if self.stacked_widget.currentWidget() == self.mindmap_view:
            selected_items = self.mindmap_view.scene().selectedItems() if hasattr(self.mindmap_view, 'scene') else []
            clicked_item_selected = False
            for item in selected_items:
                if hasattr(item, 'node') and item.node == node:
                    clicked_item_selected = True
                    break
            if clicked_item_selected:
                for item in selected_items:
                    if hasattr(item, 'node') and item.node and item.node.layer:
                        layers.append(item.node.layer)
        if not layers and node.layer:
            layers = [node.layer]

        if layers:
            self._create_layer_context_menu(layers, global_pos)
        elif node.is_physical_folder and node.path:
            self._create_folder_context_menu(node.path, global_pos)

    def _create_folder_context_menu(self, folder_path, global_pos, folder_item=None):
        is_logical = folder_item is not None and not getattr(folder_item, 'is_physical', True)

        actual_path = None
        if not is_logical:
            actual_path = resolve_physical_path(folder_path)
            if not actual_path or not os.path.exists(actual_path):
                return

        menu = QMenu(self)
        menu.setStyleSheet("""
            QMenu {
                background-color: #ffffff;
                border: 1px solid #dee2e6;
                padding: 4px 0px;
                icon-size: 16px;
            }
            QMenu::item {
                margin-left: 3px;
                padding: 5px 12px 5px 6px;
                font-family: "Microsoft YaHei", "Segoe UI", sans-serif;
                font-size: 12px;
                color: #212529;
            }
            QMenu::item:selected {
                background-color: #1484dc;
                color: #ffffff;
            }
        """)

        plugin_dir = os.path.dirname(os.path.abspath(__file__))
        zoom_icon_path = os.path.join(plugin_dir, "icons_component", "Zoom_to_Layer.svg")

        if is_logical:
            act_zoom = menu.addAction(tr("缩放到图层组"))
            if os.path.exists(zoom_icon_path):
                act_zoom.setIcon(QIcon(zoom_icon_path))
            act_zoom.triggered.connect(lambda: self.action_zoom_to_folder(folder_path, folder_item))
        else:
            act_zoom = menu.addAction(tr("缩放到文件夹"))
            if os.path.exists(zoom_icon_path):
                act_zoom.setIcon(QIcon(zoom_icon_path))
            act_zoom.triggered.connect(lambda: self.action_zoom_to_folder(folder_path, folder_item))

            menu.addSeparator()

            act_open_folder = menu.addAction(tr("打开文件夹位置"))
            open_icon_path = os.path.join(plugin_dir, "icons_component", "Open_File_Location.svg")
            if os.path.exists(open_icon_path):
                act_open_folder.setIcon(QIcon(open_icon_path))

            act_copy_link = menu.addAction(tr("复制文件夹链接"))
            copy_icon_path = os.path.join(plugin_dir, "icons_component", "Copy_Folder_Link.svg")
            if os.path.exists(copy_icon_path):
                act_copy_link.setIcon(QIcon(copy_icon_path))

            act_rename_folder = menu.addAction(tr("重命名文件夹"))
            rename_icon_path = os.path.join(plugin_dir, "icons_component", "Renamed_parent_folder.svg")
            if os.path.exists(rename_icon_path):
                act_rename_folder.setIcon(QIcon(rename_icon_path))

            act_migrate_folder = menu.addAction(tr("迁移文件夹"))
            migrate_icon_path = os.path.join(plugin_dir, "icons_component", "Move_Folder.svg")
            if os.path.exists(migrate_icon_path):
                act_migrate_folder.setIcon(QIcon(migrate_icon_path))

            def on_open():
                try:
                    import subprocess  # noqa: PLC0415  # nosec B404
                    norm_path = os.path.normpath(actual_path)
                    if os.name == 'nt':
                        explorer_path = os.path.join(os.environ.get('SystemRoot', 'C:\\Windows'), 'explorer.exe')
                        if os.path.isdir(norm_path):
                            subprocess.Popen([explorer_path, norm_path])  # nosec B603 B607
                        else:
                            subprocess.Popen([explorer_path, '/select,', norm_path])  # nosec B603 B607
                    else:
                        import shutil  # noqa: PLC0415
                        opener_cmd = 'open' if sys.platform == 'darwin' else 'xdg-open'
                        opener = shutil.which(opener_cmd) or ('/usr/bin/open' if sys.platform == 'darwin' else '/usr/bin/xdg-open')
                        if os.path.isdir(norm_path):
                            subprocess.Popen([opener, norm_path])  # nosec B603 B607
                        else:
                            subprocess.Popen([opener, os.path.dirname(norm_path)])  # nosec B603 B607
                except Exception as e:
                    QMessageBox.warning(self, tr("操作失败"), tr("打开文件夹失败: {}").format(str(e)))

            def on_copy():
                try:
                    from qgis.PyQt.QtWidgets import QApplication
                    norm_path = os.path.normpath(actual_path)
                    QApplication.clipboard().setText(norm_path)
                except Exception as e:
                    QMessageBox.warning(self, tr("操作失败"), tr("复制文件夹链接失败: {}").format(str(e)))

            def on_rename():
                old_name = os.path.basename(actual_path)
                new_name, ok = QInputDialog.getText(
                    self,
                    tr("重命名文件夹"),
                    tr("新文件夹名:"),
                    text=old_name
                )
                if ok and new_name and new_name != old_name:
                    try:
                        success = safe_rename_dir(actual_path, new_name)
                        if success:
                            self.refresh()
                    except Exception as e:
                        QMessageBox.warning(self, tr("操作失败"), tr("重命名文件夹失败: {}").format(str(e)))

            def on_migrate():
                initial_dir = os.path.dirname(actual_path) if actual_path else ""
                target_parent_dir = QFileDialog.getExistingDirectory(self, tr("选择迁移目标文件夹"), initial_dir)
                if target_parent_dir:
                    try:
                        success = safe_migrate_dir(actual_path, target_parent_dir)
                        if success:
                            self.refresh()
                    except Exception as e:
                        QMessageBox.warning(self, tr("操作失败"), tr("迁移文件夹失败: {}").format(str(e)))

            act_open_folder.triggered.connect(on_open)
            act_copy_link.triggered.connect(on_copy)
            act_rename_folder.triggered.connect(on_rename)
            act_migrate_folder.triggered.connect(on_migrate)

        menu.exec(global_pos)

    def handle_layer_relocation(self, layer_id, target_folder_path):
        try:
            project = QgsProject.instance()
            layer = project.mapLayer(layer_id)
        except Exception:
            layer = None

        if not layer:
            QMessageBox.warning(self, tr("移动失败"), tr("未找到指定的图层，无法进行文件移动。"))
            return

        layer_name = layer.name()

        if hasattr(layer, 'isEditable') and layer.isEditable():
            QMessageBox.warning(
                self,
                tr("操作被拦截"),
                tr("图层【{}】目前处于编辑状态。\n请先在 QGIS 中保存编辑并关闭编辑模式，然后再尝试操作。").format(layer_name)
            )
            return

        source_path = layer.source()
        phys_source_path, query_params = split_qgis_source(source_path)
        actual_source_path = resolve_physical_path(phys_source_path)
        if not actual_source_path or not os.path.exists(actual_source_path):
            QMessageBox.warning(self, tr("操作失败"), tr("未找到图层【{}】的源文件：\n{}").format(layer_name, phys_source_path))
            return

        # Pop up selection dialog with Move, Copy, Backup options
        files = get_associated_files(phys_source_path)
        file_list_str = "\n".join([f"  • {os.path.basename(f)}" for f in files if os.path.exists(f)])
        if not file_list_str:
            file_list_str = f"  • {os.path.basename(phys_source_path)}"

        msg_box = QMessageBox(self)
        msg_box.setWindowTitle(tr("选择操作"))
        msg_box.setText(tr("拖拽图层【{}】到该目录，请选择要执行的操作：\n\n涉及物理文件：\n{}").format(layer_name, file_list_str))

        plugin_dir = os.path.dirname(os.path.abspath(__file__))
        icons_dir = os.path.join(plugin_dir, "icons_component")
        icon_move = QIcon(os.path.join(icons_dir, "Move_File.svg"))
        icon_copy = QIcon(os.path.join(icons_dir, "Copy_to_new_folder.svg"))
        icon_backup = QIcon(os.path.join(icons_dir, "Backup_to_new_folder.svg"))

        btn_move = msg_box.addButton(tr("移动"), QMessageBox.ButtonRole.ActionRole)
        btn_move.setIcon(icon_move)
        btn_copy = msg_box.addButton(tr("复制"), QMessageBox.ButtonRole.ActionRole)
        btn_copy.setIcon(icon_copy)
        btn_backup = msg_box.addButton(tr("备份"), QMessageBox.ButtonRole.ActionRole)
        btn_backup.setIcon(icon_backup)
        btn_cancel = msg_box.addButton(tr("取消"), QMessageBox.ButtonRole.RejectRole)
        btn_cancel.setStyleSheet("background-color: #cccccc; min-width: 60px;")

        msg_box.exec()
        clicked = msg_box.clickedButton()

        if clicked == btn_cancel:
            return

        if clicked == btn_move:
            source_dir = os.path.dirname(actual_source_path)

            if os.path.normcase(os.path.abspath(source_dir)) == os.path.normcase(os.path.abspath(target_folder_path)):
                return

            files = get_associated_files(phys_source_path)
            conflict_files = []
            for src in files:
                dest = os.path.join(target_folder_path, os.path.basename(src))
                if os.path.exists(dest):
                    conflict_files.append(os.path.basename(src))

            if conflict_files:
                QMessageBox.warning(
                    self,
                    tr("移动冲突"),
                    tr("目标文件夹已存在以下同名文件：\n{} \n\n操作已被取消，请先清理或重命名冲突文件。").format("\n".join(conflict_files))
                )
                return

            file_size_text = ""
            try:
                total_size = sum(os.path.getsize(f) for f in files if os.path.exists(f))
                file_size_text = " " + tr("(总大小: {})").format(format_size(total_size))
            except Exception as e:  # noqa: BLE001
                import logging
                logging.getLogger(__name__).debug("Failed to calculate total size: %s", e)

            confirm_msg = (
                tr("确定要物理移动图层【{}】的文件吗？").format(layer_name) + "\n\n" +
                tr("源目录: {}").format(source_dir) + "\n" +
                tr("目标目录: {}").format(target_folder_path) + "\n" +
                tr("伴生文件数量: {} {}").format(len(files), file_size_text) + "\n\n" +
                tr("此操作将直接修改磁盘物理文件路径并更新 QGIS 数据源链接。")
            )

            reply = QMessageBox.question(
                self,
                tr("确认物理移动文件"),
                confirm_msg,
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )

            if reply == QMessageBox.StandardButton.Yes:
                try:
                    success = safe_move(layer, target_folder_path)
                    if success:
                        self.refresh()
                        QMessageBox.information(self, tr("移动成功"), tr("图层【{}】文件已成功移动至目标目录。").format(layer_name))
                    else:
                        QMessageBox.critical(self, tr("移动失败"), tr("在拷贝或移动图层【{}】文件时发生未知错误。").format(layer_name))
                except Exception as e:
                    QMessageBox.critical(self, tr("移动失败"), tr("移动文件异常：\n{}").format(str(e)))

        elif clicked == btn_copy:
            try:
                files = get_associated_files(phys_source_path)
                conflict_files = []
                for src in files:
                    dest = os.path.join(target_folder_path, os.path.basename(src))
                    if os.path.exists(dest):
                        conflict_files.append(os.path.basename(src))

                if conflict_files:
                    QMessageBox.warning(
                        self,
                        tr("复制冲突"),
                        tr("目标文件夹已存在以下同名文件：\n{} \n\n操作已被取消，请先清理或重命名冲突文件。").format("\n".join(conflict_files))
                    )
                    return

                # Copy files
                safe_copy(source_path, target_folder_path)

                # Load new layer in QGIS
                new_path = os.path.join(target_folder_path, os.path.basename(phys_source_path))
                new_layer = None

                if isinstance(layer, QgsVectorLayer):
                    new_layer = QgsVectorLayer(new_path, tr("{} (复制)").format(layer.name()), layer.dataProvider().name())
                elif isinstance(layer, QgsRasterLayer):
                    new_layer = QgsRasterLayer(new_path, tr("{} (复制)").format(layer.name()), layer.dataProvider().name())
                else:
                    ext = os.path.splitext(new_path)[1].lower()
                    vector_exts = ['.shp', '.geojson', '.gpkg', '.kml', '.tab']
                    if ext in vector_exts:
                        new_layer = QgsVectorLayer(new_path, tr("{} (复制)").format(layer.name()), "ogr")
                    else:
                        new_layer = QgsRasterLayer(new_path, tr("{} (复制)").format(layer.name()), "gdal")

                if new_layer and new_layer.isValid():
                    layer_style = self._capture_layer_style(layer)
                    self._apply_layer_style(layer_style, new_layer)
                    QgsProject.instance().addMapLayer(new_layer)

                self.refresh()
                QMessageBox.information(self, tr("复制成功"), tr("图层【{}】已成功复制并加载到当前工程。").format(layer_name))
            except Exception as e:
                QMessageBox.warning(self, tr("操作失败"), tr("复制图层失败: {}").format(str(e)))

        elif clicked == btn_backup:
            try:
                files = get_associated_files(phys_source_path)
                conflict_files = []
                for src in files:
                    dest = os.path.join(target_folder_path, os.path.basename(src))
                    if os.path.exists(dest):
                        conflict_files.append(os.path.basename(src))

                if conflict_files:
                    QMessageBox.warning(
                        self,
                        tr("备份冲突"),
                        tr("目标文件夹已存在以下同名文件：\n{} \n\n操作已被取消，请先清理或重命名冲突文件。").format("\n".join(conflict_files))
                    )
                    return

                # Copy files
                safe_copy(source_path, target_folder_path)

                self.refresh()
                QMessageBox.information(self, tr("备份成功"), tr("图层【{}】物理文件已成功备份至目标目录。").format(layer_name))
            except Exception as e:
                QMessageBox.warning(self, tr("操作失败"), tr("备份文件失败: {}").format(str(e)))

    def handle_group_reorder(self, dragged_items, target_info, position):
        """Submit a complete sibling-layer order through QGIS' group API."""
        if (not dragged_items or not target_info or
                target_info.get("type") != "layer" or
                position not in ("above", "below")):
            return

        try:
            project = QgsProject.instance()
            if not project or not project.layerTreeRoot():
                return
            root = project.layerTreeRoot()
        except Exception:
            return

        target_node = root.findLayer(target_info.get("id"))
        if not target_node:
            return

        target_parent = target_node.parent()
        if not target_parent:
            return

        # Resolve all sources before changing the order. Groups and cross-group
        # moves are deliberately unsupported.
        source_nodes = []
        for item_data in dragged_items:
            if item_data.get("type") != "layer":
                return
            source_node = root.findLayer(item_data.get("id"))
            if not source_node or source_node.parent() != target_parent:
                return
            if source_node not in source_nodes:
                source_nodes.append(source_node)

        if len(source_nodes) != 1 or target_node in source_nodes:
            return

        try:
            children = target_parent.children()
            # reorderGroupLayers() intentionally places non-layer children after
            # layers. Refuse mixed groups so subgroup positions never change.
            ordered_layers = []
            for child in children:
                layer = child.layer() if hasattr(child, "layer") else None
                if not layer:
                    return
                ordered_layers.append(layer)

            source_layer = source_nodes[0].layer()
            target_layer = target_node.layer()
            if not source_layer or not target_layer:
                return

            ordered_layers.remove(source_layer)
            target_index = ordered_layers.index(target_layer)
            if position == "below":
                target_index += 1
            ordered_layers.insert(target_index, source_layer)
            target_parent.reorderGroupLayers(ordered_layers)
            self._refresh_timer.start()
        except Exception as e:  # noqa: BLE001
            import logging
            logging.getLogger(__name__).warning("Failed to reorder sibling layers: %s", e)

    def handle_multiple_layers_relocation(self, layer_ids, target_folder_path):
        project = QgsProject.instance()
        if not project:
            return

        layers_to_move = []
        for lid in layer_ids:
            layer = project.mapLayer(lid)
            if layer:
                layers_to_move.append(layer)

        if not layers_to_move:
            return

        editing_names = [layer.name() for layer in layers_to_move if hasattr(layer, 'isEditable') and layer.isEditable()]
        if editing_names:
            QMessageBox.warning(
                self,
                tr("操作被拦截"),
                tr("以下图层处于编辑状态，请保存并关闭编辑模式后再尝试操作：\n{}").format("\n".join(editing_names))
            )
            return

        actual_target = resolve_physical_path(target_folder_path)
        if not actual_target or not os.path.exists(actual_target) or not os.path.isdir(actual_target):
            QMessageBox.warning(self, tr("操作失败"), tr("未找到合法的目标文件夹物理路径。"))
            return

        all_src_files = []
        layer_file_map = {}
        for layer in layers_to_move:
            source_path = layer.source()
            phys_source_path, query_params = split_qgis_source(source_path)
            actual_source_path = resolve_physical_path(phys_source_path)
            if not actual_source_path or not os.path.exists(actual_source_path):
                QMessageBox.warning(self, tr("操作失败"), tr("未找到图层【{}】的源文件。").format(layer.name()))
                return

            source_dir = os.path.dirname(actual_source_path)
            if os.path.normcase(os.path.abspath(source_dir)) == os.path.normcase(os.path.abspath(actual_target)):
                continue

            files = get_associated_files(phys_source_path)
            all_src_files.extend(files)
            layer_file_map[layer.id()] = (layer, files, phys_source_path, query_params)

        if not layer_file_map:
            return

        # Pop up selection dialog with Move, Copy, Backup options
        file_list_str = "\n".join([f"  • {os.path.basename(f)}" for f in all_src_files if os.path.exists(f)])
        if not file_list_str:
            file_list_str = tr("（未找到有效的物理文件）")

        msg_box = QMessageBox(self)
        msg_box.setWindowTitle(tr("选择操作"))
        msg_box.setText(tr("拖拽选中的 {} 个图层到该目录，请选择要执行的操作：\n\n涉及物理文件：\n{}").format(len(layer_file_map), file_list_str))

        plugin_dir = os.path.dirname(os.path.abspath(__file__))
        icons_dir = os.path.join(plugin_dir, "icons_component")
        icon_move = QIcon(os.path.join(icons_dir, "Move_File.svg"))
        icon_copy = QIcon(os.path.join(icons_dir, "Copy_to_new_folder.svg"))
        icon_backup = QIcon(os.path.join(icons_dir, "Backup_to_new_folder.svg"))

        btn_move = msg_box.addButton(tr("移动"), QMessageBox.ButtonRole.ActionRole)
        btn_move.setIcon(icon_move)
        btn_copy = msg_box.addButton(tr("复制"), QMessageBox.ButtonRole.ActionRole)
        btn_copy.setIcon(icon_copy)
        btn_backup = msg_box.addButton(tr("备份"), QMessageBox.ButtonRole.ActionRole)
        btn_backup.setIcon(icon_backup)
        btn_cancel = msg_box.addButton(tr("取消"), QMessageBox.ButtonRole.RejectRole)
        btn_cancel.setStyleSheet("background-color: #cccccc; min-width: 60px;")

        msg_box.exec()
        clicked = msg_box.clickedButton()

        if clicked == btn_cancel:
            return

        if clicked == btn_move:
            conflict_files = []
            for src in all_src_files:
                dest = os.path.join(actual_target, os.path.basename(src))
                if os.path.exists(dest):
                    conflict_files.append(os.path.basename(src))

            if conflict_files:
                QMessageBox.warning(
                    self,
                    tr("移动冲突"),
                    tr("目标文件夹已存在以下同名文件：\n{} \n\n操作已被取消。").format("\n".join(conflict_files))
                )
                return

            file_size_text = ""
            try:
                total_size = sum(os.path.getsize(f) for f in all_src_files if os.path.exists(f))
                file_size_text = " " + tr("(总大小: {})").format(format_size(total_size))
            except Exception as e:  # noqa: BLE001
                import logging
                logging.getLogger(__name__).debug("Failed to calculate total size: %s", e)

            confirm_msg = (
                tr("确定要物理移动选中的这 {} 个图层的文件吗？").format(len(layer_file_map)) + "\n\n" +
                tr("目标目录: {}").format(actual_target) + "\n" +
                tr("伴生文件数量: {} {}").format(len(all_src_files), file_size_text) + "\n\n" +
                tr("此操作将直接修改磁盘物理文件路径并更新 QGIS 数据源链接。")
            )

            reply = QMessageBox.question(
                self,
                tr("确认物理移动文件"),
                confirm_msg,
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )

            if reply == QMessageBox.StandardButton.Yes:
                success_count = 0
                failed_layers = []
                for lid, (layer, files, phys_source_path, query_params) in layer_file_map.items():
                    try:
                        success = safe_move(layer, actual_target)
                        if success:
                            success_count += 1
                        else:
                            failed_layers.append(layer.name())
                    except Exception as e:
                        failed_layers.append(f"{layer.name()} ({str(e)})")

                self.refresh()
                if not failed_layers:
                    QMessageBox.information(self, tr("移动成功"), tr("成功将 {} 个图层的文件移动到新目录。").format(success_count))
                else:
                    QMessageBox.critical(
                        self,
                        tr("部分移动失败"),
                        tr("成功移动了 {} 个图层，但以下图层移动失败：\n{}").format(success_count, "\n".join(failed_layers))
                    )

        elif clicked == btn_copy:
            try:
                conflict_files = []
                for src in all_src_files:
                    dest = os.path.join(actual_target, os.path.basename(src))
                    if os.path.exists(dest):
                        conflict_files.append(os.path.basename(src))

                if conflict_files:
                    QMessageBox.warning(
                        self,
                        tr("复制冲突"),
                        tr("目标文件夹已存在以下同名文件：\n{} \n\n操作已被取消。").format("\n".join(conflict_files))
                    )
                    return

                for lid, (layer, files, phys_source_path, query_params) in layer_file_map.items():
                    # Copy files
                    safe_copy(layer.source(), actual_target)
                    # Load new layer in QGIS
                    new_path = os.path.join(actual_target, os.path.basename(layer.source()))
                    new_layer = None

                    if isinstance(layer, QgsVectorLayer):
                        new_layer = QgsVectorLayer(new_path, tr("{} (复制)").format(layer.name()), layer.dataProvider().name())
                    elif isinstance(layer, QgsRasterLayer):
                        new_layer = QgsRasterLayer(new_path, tr("{} (复制)").format(layer.name()), layer.dataProvider().name())
                    else:
                        ext = os.path.splitext(new_path)[1].lower()
                        vector_exts = ['.shp', '.geojson', '.gpkg', '.kml', '.tab']
                        if ext in vector_exts:
                            new_layer = QgsVectorLayer(new_path, tr("{} (复制)").format(layer.name()), "ogr")
                        else:
                            new_layer = QgsRasterLayer(new_path, tr("{} (复制)").format(layer.name()), "gdal")

                    if new_layer and new_layer.isValid():
                        layer_style = self._capture_layer_style(layer)
                        self._apply_layer_style(layer_style, new_layer)
                        if isinstance(new_layer, QgsVectorLayer) and hasattr(layer, "subsetString"):
                            # Provider subset filters are datasource state, not part of
                            # QgsMapLayerStyle, so copy them explicitly.
                            new_layer.setSubsetString(layer.subsetString())
                        QgsProject.instance().addMapLayer(new_layer)
                self.refresh()
                QMessageBox.information(self, tr("复制成功"), tr("成功复制并加载了 {} 个图层。").format(len(layer_file_map)))
            except Exception as e:
                QMessageBox.warning(self, tr("操作失败"), tr("复制图层失败: {}").format(str(e)))

        elif clicked == btn_backup:
            try:
                conflict_files = []
                for src in all_src_files:
                    dest = os.path.join(actual_target, os.path.basename(src))
                    if os.path.exists(dest):
                        conflict_files.append(os.path.basename(src))

                if conflict_files:
                    QMessageBox.warning(
                        self,
                        tr("备份冲突"),
                        tr("目标文件夹已存在以下同名文件：\n{} \n\n操作已被取消。").format("\n".join(conflict_files))
                    )
                    return

                for lid, (layer, files, phys_source_path, query_params) in layer_file_map.items():
                    # Copy files
                    safe_copy(layer.source(), actual_target)
                self.refresh()
                QMessageBox.information(self, tr("备份成功"), tr("成功备份选中的 {} 个图层物理文件到目标目录。").format(len(layer_file_map)))
            except Exception as e:
                QMessageBox.warning(self, tr("操作失败"), tr("备份文件失败: {}").format(str(e)))

    def handle_folder_relocation(self, source_folder_path, target_folder_path):
        import shutil
        actual_source = resolve_physical_path(source_folder_path)
        actual_target = resolve_physical_path(target_folder_path)

        if not actual_source or not os.path.exists(actual_source):
            QMessageBox.warning(self, tr("操作失败"), tr("未找到源文件夹/容器物理路径。"))
            return

        if not actual_target or not os.path.exists(actual_target):
            QMessageBox.warning(self, tr("操作失败"), tr("未找到目标文件夹物理路径。"))
            return

        if not os.path.isdir(actual_target):
            QMessageBox.warning(self, tr("操作失败"), tr("目标路径必须是文件夹。"))
            return

        new_path = os.path.join(actual_target, os.path.basename(actual_source)).replace('\\', '/')

        if os.path.normcase(os.path.abspath(actual_source)) == os.path.normcase(os.path.abspath(new_path)):
            return

        if os.path.isdir(actual_source):
            norm_source = os.path.normcase(os.path.abspath(actual_source)).replace('\\', '/')
            norm_target = os.path.normcase(os.path.abspath(actual_target)).replace('\\', '/')
            if norm_target == norm_source or norm_target.startswith(norm_source + '/'):
                QMessageBox.warning(self, tr("移动失败"), tr("不能将文件夹移动到自身或其子文件夹下。"))
                return

        if os.path.exists(new_path):
            QMessageBox.warning(self, tr("移动冲突"), tr("目标文件夹中已存在同名文件夹或文件：\n{}").format(os.path.basename(actual_source)))
            return

        # Identify layers in the project under this directory
        project = QgsProject.instance()
        layers_under = []
        if project:
            def is_under_or_equal(path, parent):
                norm_p = os.path.normcase(os.path.abspath(path))
                norm_parent = os.path.normcase(os.path.abspath(parent))
                return norm_p == norm_parent or norm_p.startswith(norm_parent + os.sep) or norm_p.replace('\\', '/').startswith(norm_parent.replace('\\', '/') + '/')

            for layer_id, layer in project.mapLayers().items():
                if layer and layer.source():
                    p_path, q_params = split_qgis_source(layer.source())
                    actual_p_path = resolve_physical_path(p_path)
                    if is_under_or_equal(actual_p_path, actual_source):
                        layers_under.append(layer)

        # Pop up selection dialog with Move, Copy, Backup options
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle(tr("选择操作"))

        info_text = tr("拖拽文件夹【{}】到该目录，请选择要执行的操作：\n\n源路径：{}\n目标目录：{}").format(
            os.path.basename(actual_source), actual_source, actual_target
        )
        if layers_under:
            layers_str = "\n".join([f"  • {layer.name()}" for layer in layers_under])
            info_text += tr("\n\n关联的图层：\n{}").format(layers_str)

        msg_box.setText(info_text)

        plugin_dir = os.path.dirname(os.path.abspath(__file__))
        icons_dir = os.path.join(plugin_dir, "icons_component")
        icon_move = QIcon(os.path.join(icons_dir, "Move_File.svg"))
        icon_copy = QIcon(os.path.join(icons_dir, "Copy_to_new_folder.svg"))
        icon_backup = QIcon(os.path.join(icons_dir, "Backup_to_new_folder.svg"))

        btn_move = msg_box.addButton(tr("移动"), QMessageBox.ButtonRole.ActionRole)
        btn_move.setIcon(icon_move)
        btn_copy = msg_box.addButton(tr("复制"), QMessageBox.ButtonRole.ActionRole)
        btn_copy.setIcon(icon_copy)
        btn_backup = msg_box.addButton(tr("备份"), QMessageBox.ButtonRole.ActionRole)
        btn_backup.setIcon(icon_backup)
        btn_cancel = msg_box.addButton(tr("取消"), QMessageBox.ButtonRole.RejectRole)
        btn_cancel.setStyleSheet("background-color: #cccccc; min-width: 60px;")

        msg_box.exec()
        clicked = msg_box.clickedButton()

        if clicked == btn_cancel:
            return

        if clicked == btn_move:
            try:
                success = safe_migrate_dir(actual_source, actual_target)
                if success:
                    self.refresh()
                    QMessageBox.information(self, tr("移动成功"), tr("文件夹/容器移动成功。"))
                else:
                    QMessageBox.critical(self, tr("移动失败"), tr("在拷贝或移动文件夹/容器时发生未知错误。"))
            except Exception as e:
                QMessageBox.critical(self, tr("移动失败"), tr("移动发生异常错误：\n{}").format(str(e)))

        elif clicked == btn_copy:
            try:
                if os.path.isdir(actual_source):
                    shutil.copytree(actual_source, new_path)
                else:
                    parent_dir = os.path.dirname(new_path)
                    if not os.path.exists(parent_dir):
                        os.makedirs(parent_dir)
                    shutil.copy2(actual_source, new_path)
                    for log_ext in ['-wal', '-shm']:
                        log_src = actual_source + log_ext
                        log_dest = new_path + log_ext
                        if os.path.exists(log_src):
                            try:
                                shutil.copy2(log_src, log_dest)
                            except Exception as e:  # noqa: BLE001
                                import logging
                                logging.getLogger(__name__).debug("Failed to copy sidecar file: %s", e)

                # Load the copied layers
                for layer in layers_under:
                    source_path = layer.source()
                    phys_source_path, query_params = split_qgis_source(source_path)
                    actual_p_path = resolve_physical_path(phys_source_path)

                    if os.path.isdir(actual_source):
                        rel_path = os.path.relpath(phys_source_path, actual_source)
                        new_l_path = os.path.normpath(os.path.join(new_path, rel_path)).replace('\\', '/')
                    else:
                        new_l_path = new_path

                    new_layer = None
                    if isinstance(layer, QgsVectorLayer):
                        new_layer = QgsVectorLayer(new_l_path + query_params, tr("{} (复制)").format(layer.name()), layer.dataProvider().name())
                    elif isinstance(layer, QgsRasterLayer):
                        new_layer = QgsRasterLayer(new_l_path + query_params, tr("{} (复制)").format(layer.name()), layer.dataProvider().name())
                    else:
                        ext = os.path.splitext(new_l_path)[1].lower()
                        vector_exts = ['.shp', '.geojson', '.gpkg', '.kml', '.tab']
                        if ext in vector_exts:
                            new_layer = QgsVectorLayer(new_l_path + query_params, tr("{} (复制)").format(layer.name()), "ogr")
                        else:
                            new_layer = QgsRasterLayer(new_l_path + query_params, tr("{} (复制)").format(layer.name()), "gdal")

                    if new_layer and new_layer.isValid():
                        layer_style = self._capture_layer_style(layer)
                        self._apply_layer_style(layer_style, new_layer)
                        QgsProject.instance().addMapLayer(new_layer)

                self.refresh()
                QMessageBox.information(self, tr("复制成功"), tr("文件夹/容器复制成功，并已加载其下图层。"))
            except Exception as e:
                QMessageBox.critical(self, tr("复制失败"), tr("复制发生异常错误：\n{}").format(str(e)))

        elif clicked == btn_backup:
            try:
                if os.path.isdir(actual_source):
                    shutil.copytree(actual_source, new_path)
                else:
                    parent_dir = os.path.dirname(new_path)
                    if not os.path.exists(parent_dir):
                        os.makedirs(parent_dir)
                    shutil.copy2(actual_source, new_path)
                    for log_ext in ['-wal', '-shm']:
                        log_src = actual_source + log_ext
                        log_dest = new_path + log_ext
                        if os.path.exists(log_src):
                            try:
                                shutil.copy2(log_src, log_dest)
                            except Exception as e:  # noqa: BLE001
                                import logging
                                logging.getLogger(__name__).debug("Failed to copy sidecar file: %s", e)

                self.refresh()
                QMessageBox.information(self, tr("备份成功"), tr("文件夹/容器备份成功。"))
            except Exception as e:
                QMessageBox.critical(self, tr("备份失败"), tr("备份发生异常错误：\n{}").format(str(e)))

    def _create_layer_context_menu(self, layers, global_pos):
        menu = QMenu(self)
        menu.setStyleSheet("""
            QMenu {
                background-color: #ffffff;
                border: 1px solid #dee2e6;
                padding: 4px 0px;
                icon-size: 16px;
            }
            QMenu::item {
                margin-left: 3px;
                padding: 5px 12px 5px 6px;
                font-family: "Microsoft YaHei", "Segoe UI", sans-serif;
                font-size: 12px;
                color: #212529;
            }
            QMenu::item:selected {
                background-color: #1484dc;
                color: #ffffff;
            }
        """)

        plugin_dir = os.path.dirname(os.path.abspath(__file__))
        icons_dir = os.path.join(plugin_dir, "icons_component")

        def set_icon(item, svg_name):
            icon_path = os.path.join(icons_dir, svg_name)
            if os.path.exists(icon_path):
                item.setIcon(QIcon(icon_path))

        def set_panel_icon(item, svg_name):
            panel_icons_dir = os.path.join(plugin_dir, "icons_panel")
            icon_path = os.path.join(panel_icons_dir, svg_name)
            if os.path.exists(icon_path):
                item.setIcon(QIcon(icon_path))

        # Single layer actions
        if len(layers) == 1:
            layer = layers[0]
            try:
                from .layer_model import is_layer_visible
            except ImportError:
                from layer_model import is_layer_visible

            visible = is_layer_visible(layer)
            if visible:
                act_hide = menu.addAction(tr("隐藏图层"))
                act_hide.triggered.connect(lambda: self.action_set_layers_visibility([layer], False))
                set_icon(act_hide, "Component_layer_hide.svg")

                act_show = menu.addAction(tr("显示图层"))
                act_show.triggered.connect(lambda: self.action_set_layers_visibility([layer], True))
                set_icon(act_show, "Component_layer_show.svg")
            else:
                act_show = menu.addAction(tr("显示图层"))
                act_show.triggered.connect(lambda: self.action_set_layers_visibility([layer], True))
                set_icon(act_show, "Component_layer_show.svg")

                act_hide = menu.addAction(tr("隐藏图层"))
                act_hide.triggered.connect(lambda: self.action_set_layers_visibility([layer], False))
                set_icon(act_hide, "Component_layer_hide.svg")

            menu.addSeparator()

            is_memory = False
            if hasattr(layer, 'dataProvider') and layer.dataProvider() and hasattr(layer.dataProvider(), 'name'):
                is_memory = (layer.dataProvider().name() == "memory")

            if is_memory:
                act_zoom = menu.addAction(tr("缩放到图层"))
                act_zoom.triggered.connect(lambda: self.action_zoom_to_layers([layer]))
                set_icon(act_zoom, "Zoom_to_Layer.svg")

                act_export_temp = menu.addAction(tr("保存临时图层"))
                act_export_temp.triggered.connect(lambda: self.action_export_temporary_layer(layer))
                set_icon(act_export_temp, "Save_Temporary_Layer.svg")

                menu.addSeparator()

                edit_menu = menu.addMenu(tr("图层编辑"))
                set_icon(edit_menu, "Layer_Editing.svg")

                if isinstance(layer, QgsVectorLayer):
                    pencil_label = tr("停止编辑") if layer.isEditable() else tr("开始编辑")
                    act_toggle_edit = edit_menu.addAction(pencil_label)
                    act_toggle_edit.triggered.connect(lambda: self.action_toggle_edit(layer))
                    set_icon(act_toggle_edit, "Start_Editing.svg")

                act_rename_layer = edit_menu.addAction(tr("重命名图层"))
                act_rename_layer.triggered.connect(lambda: self.action_rename_layer(layer))
                set_icon(act_rename_layer, "Rename_Layer.svg")

                if isinstance(layer, QgsVectorLayer):
                    act_open_attrs = edit_menu.addAction(tr("打开属性表"))
                    act_open_attrs.triggered.connect(lambda: self.action_open_attribute_table(layer))
                    act_open_attrs.setToolTip(tr("重新加载到QGIS时候自动以新的文件名加载"))
                    set_icon(act_open_attrs, "Open_Property_Table.svg")

                act_properties = edit_menu.addAction(tr("打开图层属性"))
                act_properties.triggered.connect(lambda: self.action_open_properties(layer))
                set_icon(act_properties, "Open_Layer_Properties.svg")
            else:
                act_zoom = menu.addAction(tr("缩放到图层"))
                act_zoom.triggered.connect(lambda: self.action_zoom_to_layers([layer]))
                set_icon(act_zoom, "Zoom_to_Layer.svg")

                menu.addSeparator()

                act_datasource = menu.addAction(tr("更换数据源"))
                act_datasource.triggered.connect(lambda: self.action_change_datasource(layer))
                set_icon(act_datasource, "Change_Data_Source.svg")

                act_open_folder = menu.addAction(tr("打开文件位置"))
                act_open_folder.triggered.connect(lambda: self.action_open_containing_folder(layer))
                set_icon(act_open_folder, "Open_File_Location.svg")

                menu.addSeparator()

                act_move = menu.addAction(tr("移动选中的 1 个文件到…"))
                act_move.triggered.connect(lambda: self.action_move_files([layer]))
                act_move.setToolTip(tr("从新路径加载文件"))
                set_icon(act_move, "Move_File.svg")

                act_copy = menu.addAction(tr("复制选中的 1 个文件到…"))
                act_copy.triggered.connect(lambda: self.action_copy_files([layer]))
                act_copy.setToolTip(tr("从新路径加载文件"))
                set_icon(act_copy, "Copy_to_new_folder.svg")

                act_backup = menu.addAction(tr("备份选中的 1 个文件到…"))
                act_backup.triggered.connect(lambda: self.action_backup_files([layer]))
                act_backup.setToolTip(tr("从原始路径加载文件"))
                set_icon(act_backup, "Backup_to_new_folder.svg")

                menu.addSeparator()

                edit_menu = menu.addMenu(tr("图层编辑"))
                set_icon(edit_menu, "Layer_Editing.svg")

                if isinstance(layer, QgsVectorLayer):
                    pencil_label = tr("停止编辑") if layer.isEditable() else tr("开始编辑")
                    act_toggle_edit = edit_menu.addAction(pencil_label)
                    act_toggle_edit.triggered.connect(lambda: self.action_toggle_edit(layer))
                    set_icon(act_toggle_edit, "Start_Editing.svg")

                act_rename_layer = edit_menu.addAction(tr("重命名图层"))
                act_rename_layer.triggered.connect(lambda: self.action_rename_layer(layer))
                set_icon(act_rename_layer, "Rename_Layer.svg")

                act_rename_file = edit_menu.addAction(tr("重命名文件"))
                act_rename_file.triggered.connect(lambda: self.action_rename_file(layer))
                set_icon(act_rename_file, "Renamed_the_original_file.svg")

                if isinstance(layer, QgsVectorLayer):
                    act_open_attrs = edit_menu.addAction(tr("打开属性表"))
                    act_open_attrs.triggered.connect(lambda: self.action_open_attribute_table(layer))
                    set_icon(act_open_attrs, "Open_Property_Table.svg")

                act_properties = edit_menu.addAction(tr("打开图层属性"))
                act_properties.triggered.connect(lambda: self.action_open_properties(layer))
                set_icon(act_properties, "Open_Layer_Properties.svg")

                style_menu = menu.addMenu(tr("样式管理"))
                set_icon(style_menu, "Style_Manage.svg")

                act_clear_style = style_menu.addAction(tr("清除默认样式"))
                act_clear_style.triggered.connect(lambda: self.action_clear_default_style(layer))
                set_icon(act_clear_style, "delete_stlye.svg")

                act_save_style = style_menu.addAction(tr("保存为默认样式"))
                act_save_style.triggered.connect(lambda: self.action_save_as_default_style(layer))
                set_icon(act_save_style, "Save_stlye.svg")

                menu.addSeparator()

                act_remove_layer = menu.addAction(tr("删除图层"))
                act_remove_layer.triggered.connect(lambda: self.action_remove_layer(layer))
                set_icon(act_remove_layer, "Delete_Layer.svg")

                menu.addSeparator()

                is_gpkg = (get_layer_format(layer) == "gpkg")
                if is_gpkg:
                    act_delete_db_layer = menu.addAction(tr("删除数据库内图层"))
                    act_delete_db_layer.triggered.connect(lambda: self.action_delete_gpkg_layer(layer))
                    set_icon(act_delete_db_layer, "Delete_Files.svg")
                else:
                    act_delete_files = menu.addAction(tr("删除文件"))
                    act_delete_files.triggered.connect(lambda: self.action_delete_files(layer))
                    set_icon(act_delete_files, "Delete_Files.svg")

        else:
            # Multi-select actions
            try:
                from .layer_model import is_layer_visible
            except ImportError:
                from layer_model import is_layer_visible

            first_visible = is_layer_visible(layers[0])
            if first_visible:
                act_hide_multi = menu.addAction(tr("隐藏选中的 {} 个图层").format(len(layers)))
                act_hide_multi.triggered.connect(lambda: self.action_set_layers_visibility(layers, False))
                set_icon(act_hide_multi, "Component_layer_hide.svg")

                act_show_multi = menu.addAction(tr("显示选中的 {} 个图层").format(len(layers)))
                act_show_multi.triggered.connect(lambda: self.action_set_layers_visibility(layers, True))
                set_icon(act_show_multi, "Component_layer_show.svg")
            else:
                act_show_multi = menu.addAction(tr("显示选中的 {} 个图层").format(len(layers)))
                act_show_multi.triggered.connect(lambda: self.action_set_layers_visibility(layers, True))
                set_icon(act_show_multi, "Component_layer_show.svg")

                act_hide_multi = menu.addAction(tr("隐藏选中的 {} 个图层").format(len(layers)))
                act_hide_multi.triggered.connect(lambda: self.action_set_layers_visibility(layers, False))
                set_icon(act_hide_multi, "Component_layer_hide.svg")

            menu.addSeparator()

            is_all_memory = all(hasattr(layer, 'dataProvider') and layer.dataProvider() and hasattr(layer.dataProvider(), 'name') and layer.dataProvider().name() == "memory" for layer in layers)

            if is_all_memory:
                act_zoom = menu.addAction(tr("缩放到…"))
                act_zoom.triggered.connect(lambda: self.action_zoom_to_layers(layers))
                set_icon(act_zoom, "Zoom_to_Layer.svg")

                act_export_temp = menu.addAction(tr("保存临时图层到…"))
                act_export_temp.triggered.connect(lambda: self.action_export_temporary_layers(layers))
                set_icon(act_export_temp, "Save_Temporary_Layer.svg")

                menu.addSeparator()

                act_remove_layers = menu.addAction(tr("删除选中图层"))
                act_remove_layers.triggered.connect(lambda: self.action_remove_layers(layers))
                set_icon(act_remove_layers, "Delete_Layer.svg")
            else:
                act_zoom = menu.addAction(tr("缩放到选中的 {} 个图层").format(len(layers)))
                act_zoom.triggered.connect(lambda: self.action_zoom_to_layers(layers))
                set_icon(act_zoom, "Zoom_to_Layer.svg")

                menu.addSeparator()

                act_move = menu.addAction(tr("移动选中的 {} 个文件到…").format(len(layers)))
                act_move.triggered.connect(lambda: self.action_move_files(layers))
                act_move.setToolTip(tr("从新路径加载文件"))
                set_icon(act_move, "Move_File.svg")

                act_copy = menu.addAction(tr("复制选中的 {} 个文件到…").format(len(layers)))
                act_copy.triggered.connect(lambda: self.action_copy_files(layers))
                act_copy.setToolTip(tr("从新路径加载文件"))
                set_icon(act_copy, "Copy_to_new_folder.svg")

                act_backup = menu.addAction(tr("备份选中的 {} 个文件到…").format(len(layers)))
                act_backup.triggered.connect(lambda: self.action_backup_files(layers))
                act_backup.setToolTip(tr("从原始路径加载文件"))
                set_icon(act_backup, "Backup_to_new_folder.svg")

                menu.addSeparator()

                act_remove_layers = menu.addAction(tr("删除选中的 {} 个图层").format(len(layers)))
                act_remove_layers.triggered.connect(lambda: self.action_remove_layers(layers))
                set_icon(act_remove_layers, "Delete_Layer.svg")

                menu.addSeparator()

                is_all_gpkg = all(get_layer_format(layer) == "gpkg" for layer in layers)
                if is_all_gpkg:
                    act_delete_gpkg_layers = menu.addAction(tr("删除选中的 {} 个数据库内图层").format(len(layers)))
                    act_delete_gpkg_layers.triggered.connect(lambda: self.action_delete_gpkg_layers(layers))
                    set_icon(act_delete_gpkg_layers, "Delete_Files.svg")
                else:
                    act_delete_files_multi = menu.addAction(tr("删除选中的 {} 个文件").format(len(layers)))
                    act_delete_files_multi.triggered.connect(lambda: self.action_delete_files_multi(layers))
                    set_icon(act_delete_files_multi, "Delete_Files.svg")

        menu.exec(global_pos)

    # Context Actions implementation
    def action_change_datasource(self, layer):
        file_filter = tr("所有文件 (*)")
        initial_dir = os.path.dirname(layer.source()) if layer.source() else ""
        new_path, _ = QFileDialog.getOpenFileName(self, tr("更换数据源"), initial_dir, file_filter)
        if new_path:
            try:
                update_layer_source(layer, new_path)
                self.refresh()
            except Exception as e:
                QMessageBox.warning(self, tr("操作失败"), tr("更换数据源失败: {}").format(str(e)))

    def action_open_containing_folder(self, layer):
        source_path = layer.source()
        phys_path, _ = split_qgis_source(source_path)
        actual_path = resolve_physical_path(phys_path)
        if actual_path and os.path.exists(actual_path):
            try:
                norm_path = os.path.normpath(actual_path)
                if os.name == 'nt':
                    import subprocess  # noqa: PLC0415  # nosec B404
                    explorer_path = os.path.join(os.environ.get('SystemRoot', 'C:\\Windows'), 'explorer.exe')
                    subprocess.Popen([explorer_path, '/select,', norm_path])  # nosec B603 B607
                else:
                    dir_path = os.path.dirname(norm_path)
                    if os.path.isdir(dir_path):
                        import shutil  # noqa: PLC0415
                        import subprocess  # noqa: PLC0415  # nosec B404
                        opener_cmd = 'open' if sys.platform == 'darwin' else 'xdg-open'
                        opener = shutil.which(opener_cmd) or ('/usr/bin/open' if sys.platform == 'darwin' else '/usr/bin/xdg-open')
                        subprocess.Popen([opener, dir_path])  # nosec B603 B607
            except Exception as e:
                QMessageBox.warning(self, tr("操作失败"), tr("打开数据所在的文件夹失败: {}").format(str(e)))
        else:
            QMessageBox.warning(self, tr("操作失败"), tr("该图层没有有效的本地物理数据路径。"))

    def action_copy_with_style(self, layer):
        self.action_copy_files([layer])

    def action_copy_files(self, layers):
        if not layers:
            return
        initial_dir = os.path.dirname(layers[0].source()) if layers[0].source() else ""
        target_dir = QFileDialog.getExistingDirectory(self, tr("选择复制目标文件夹"), initial_dir)
        if target_dir:
            try:
                for layer in layers:
                    # Copy files
                    safe_copy(layer.source(), target_dir)
                    # Load new layer in QGIS
                    new_path = os.path.join(target_dir, os.path.basename(layer.source()))
                    new_layer = None

                    # Use dynamic checking of layer type
                    if isinstance(layer, QgsVectorLayer):
                        new_layer = QgsVectorLayer(new_path, tr("{} (复制)").format(layer.name()), layer.dataProvider().name())
                    elif isinstance(layer, QgsRasterLayer):
                        new_layer = QgsRasterLayer(new_path, tr("{} (复制)").format(layer.name()), layer.dataProvider().name())
                    else:
                        # General fallback if layer type cannot be determined
                        from qgis.core import QgsProviderRegistry
                        # Auto detect vector/raster using provider registry or extension
                        ext = os.path.splitext(new_path)[1].lower()
                        vector_exts = ['.shp', '.geojson', '.gpkg', '.kml', '.tab']
                        if ext in vector_exts:
                            new_layer = QgsVectorLayer(new_path, tr("{} (复制)").format(layer.name()), "ogr")
                        else:
                            new_layer = QgsRasterLayer(new_path, tr("{} (复制)").format(layer.name()), "gdal")

                    if new_layer and new_layer.isValid():
                        layer_style = self._capture_layer_style(layer)
                        self._apply_layer_style(layer_style, new_layer)
                        if isinstance(new_layer, QgsVectorLayer) and hasattr(layer, "subsetString"):
                            # Provider subset filters are datasource state, not part of
                            # QgsMapLayerStyle, so copy them explicitly.
                            new_layer.setSubsetString(layer.subsetString())
                        QgsProject.instance().addMapLayer(new_layer)
                self.refresh()
            except Exception as e:
                QMessageBox.warning(self, tr("操作失败"), tr("复制并应用样式失败: {}").format(str(e)))

    def action_backup_files(self, layers):
        if not layers:
            return
        initial_dir = os.path.dirname(layers[0].source()) if layers[0].source() else ""
        target_dir = QFileDialog.getExistingDirectory(self, tr("选择备份目标文件夹"), initial_dir)
        if target_dir:
            try:
                for layer in layers:
                    safe_copy(layer.source(), target_dir)
                QMessageBox.information(self, tr("备份成功"), tr("成功备份选中的 {} 个图层文件到目标目录。").format(len(layers)))
                self.refresh()
            except Exception as e:
                QMessageBox.warning(self, tr("操作失败"), tr("备份文件失败: {}").format(str(e)))

    def action_clear_default_style(self, layer):
        source_path = layer.source()
        if not source_path:
            QMessageBox.warning(self, tr("操作失败"), tr("该图层没有有效的数据源路径。"))
            return

        # 1. Resolve physical path
        phys_path, _ = split_qgis_source(source_path)
        actual_path = resolve_physical_path(phys_path)
        if not actual_path:
            QMessageBox.warning(self, tr("操作失败"), tr("该图层没有有效的数据源物理路径。"))
            return

        base_path, _ = os.path.splitext(actual_path)
        qml_path = base_path + ".qml"

        deleted_file = False
        if os.path.exists(qml_path):
            try:
                os.remove(qml_path)
                deleted_file = True
            except Exception as e:
                QMessageBox.warning(self, tr("操作失败"), tr("清除默认样式文件失败: {}").format(str(e)))
                return

        # 2. Reset style manager & renderer in memory
        try:
            layer.styleManager().reset()
            from qgis.core import QgsFeatureRenderer
            if hasattr(layer, 'geometryType'):
                default_renderer = QgsFeatureRenderer.defaultRenderer(layer.geometryType())
                layer.setRenderer(default_renderer)
            layer.triggerRepaint()
        except Exception as e:  # noqa: BLE001
            import logging
            logging.getLogger(__name__).warning("Failed to reset styleManager: %s", e)

        if deleted_file:
            QMessageBox.information(self, tr("操作成功"), tr("默认样式文件已成功清除并重置图层样式。"))
        else:
            QMessageBox.information(self, tr("操作成功"), tr("图层样式已成功重置为默认状态。"))
        self.refresh()

    def action_save_as_default_style(self, layer):
        try:
            res = layer.saveDefaultStyle()
            if isinstance(res, tuple) and len(res) == 2:
                msg, success = res
            else:
                msg, success = "", True

            if success:
                QMessageBox.information(self, tr("保存成功"), tr("当前样式已成功保存为默认样式。"))
            else:
                QMessageBox.warning(self, tr("操作失败"), tr("保存默认样式失败: {}").format(msg))
        except Exception as e:
            QMessageBox.warning(self, tr("操作失败"), tr("保存默认样式失败: {}").format(str(e)))

    def action_toggle_edit(self, layer):
        if layer.isEditable():
            layer.commitChanges()
        else:
            layer.startEditing()
        self.refresh()

    def action_rename_layer(self, layer):
        new_name, ok = QInputDialog.getText(self, tr("重命名图层"), tr("请输入新的图层名称:"), text=layer.name())
        if ok and new_name:
            layer.setName(new_name)
            self.refresh()

    def action_rename_file(self, layer):
        old_filename = os.path.basename(layer.source())
        new_name, ok = QInputDialog.getText(
            self,
            tr("重命名原始物理文件"),
            tr("请输入新的物理文件名 (包含后缀，重命名后图层将自动以新的文件名载入):"),
            text=old_filename
        )
        if ok and new_name and new_name != old_filename:
            try:
                old_files = {os.path.normcase(os.path.abspath(path)) for path in get_associated_files(layer.source())}
                safe_rename(layer, new_name)
                self.refresh()
                pending = [
                    path for path in pending_rename_cleanup_files()
                    if os.path.normcase(os.path.abspath(path)) in old_files
                ]
                if pending and hasattr(self.iface, 'messageBar'):
                    self.iface.messageBar().pushMessage(
                        tr("SuperLayer"),
                        tr("文件已重命名；{} 个被占用的旧文件将在后台安全清理。").format(len(pending)),
                        duration=6,
                    )
            except Exception as e:
                QMessageBox.warning(self, tr("操作失败"), tr("重命名文件失败: {}").format(str(e)))

    def action_rename_parent_dir(self, layer):
        phys_path, _ = split_qgis_source(layer.source())
        if not phys_path:
            return
        old_parent_dir = os.path.basename(os.path.dirname(phys_path))
        new_name, ok = QInputDialog.getText(
            self,
            tr("重命名父文件夹名"),
            tr("请输入新的父文件夹名称:"),
            text=old_parent_dir
        )
        if ok and new_name and new_name != old_parent_dir:
            try:
                safe_rename_parent_dir(layer, new_name)
                self.refresh()
            except Exception as e:
                QMessageBox.warning(self, tr("操作失败"), tr("重命名父文件夹名失败: {}").format(str(e)))

    def action_open_attribute_table(self, layer):
        if hasattr(self.iface, 'showAttributeTable'):
            self.iface.showAttributeTable(layer)

    def action_open_properties(self, layer):
        if hasattr(self.iface, 'showLayerProperties'):
            self.iface.showLayerProperties(layer)

    def action_move_files(self, layers):
        if not layers:
            return
        initial_dir = os.path.dirname(layers[0].source()) if layers[0].source() else ""
        target_dir = QFileDialog.getExistingDirectory(self, tr("选择移动目标文件夹"), initial_dir)
        if target_dir:
            try:
                for layer in layers:
                    safe_move(layer, target_dir)
                self.refresh()
            except Exception as e:
                QMessageBox.warning(self, tr("操作失败"), tr("移动文件失败: {}").format(str(e)))

    def action_remove_layer(self, layer):
        """从 QGIS 工程中移除图层（不删除物理文件）。"""
        try:
            QgsProject.instance().removeMapLayer(layer.id())
            self.refresh()
        except Exception as e:
            QMessageBox.warning(self, tr("操作失败"), tr("删除图层失败: {}").format(str(e)))

    def action_delete_files(self, layer):
        """删除图层对应的物理文件（含所有伴生文件），同时从工程中移除图层。需用户确认。"""
        source_path = layer.source()
        phys_path, _ = split_qgis_source(source_path)
        actual_path = resolve_physical_path(phys_path)

        if not actual_path or not os.path.exists(actual_path):
            QMessageBox.warning(self, tr("操作失败"), tr("该图层没有有效的本地物理文件路径，无法删除。"))
            return

        associated = get_associated_files(source_path)
        file_list = "\n".join(f"  • {os.path.basename(f)}" for f in associated) if associated else f"  • {os.path.basename(actual_path)}"

        reply = QMessageBox.warning(
            self,
            tr("确认删除文件"),
            tr("此操作将永久删除以下物理文件，且无法恢复：\n\n{}\n\n确定要继续吗？").format(file_list),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        if reply != QMessageBox.StandardButton.Yes:
            return

        errors = []
        files_to_delete = associated if associated else [actual_path]
        for f in files_to_delete:
            try:
                if os.path.exists(f):
                    os.remove(f)
            except Exception as e:
                errors.append(f"{os.path.basename(f)}: {e}")

        # 无论是否有错误，先从工程中移除图层
        try:
            QgsProject.instance().removeMapLayer(layer.id())
        except Exception as e:  # noqa: BLE001
            import logging
            logging.getLogger(__name__).warning("Failed to remove layer from project: %s", e)

        self.refresh()

        if errors:
            QMessageBox.warning(self, tr("部分文件删除失败"), tr("以下文件未能删除：\n") + "\n".join(errors))

    def action_remove_layers(self, layers):
        """从 QGIS 工程中移除多个图层（不删除物理文件）。"""
        try:
            project = QgsProject.instance()
            for layer in layers:
                project.removeMapLayer(layer.id())
            self.refresh()
        except Exception as e:
            QMessageBox.warning(self, tr("操作失败"), tr("删除多个图层失败: {}").format(str(e)))

    def action_delete_files_multi(self, layers):
        """删除多个图层对应的物理文件（含所有伴生文件），同时从工程中移除图层。需用户确认。"""
        if not layers:
            return

        all_files_to_delete = []
        for layer in layers:
            source_path = layer.source()
            phys_path, _ = split_qgis_source(source_path)
            actual_path = resolve_physical_path(phys_path)
            if actual_path and os.path.exists(actual_path):
                associated = get_associated_files(source_path)
                if associated:
                    all_files_to_delete.extend(associated)
                else:
                    all_files_to_delete.append(actual_path)

        # Remove duplicates
        all_files_to_delete = list(set(all_files_to_delete))
        if not all_files_to_delete:
            QMessageBox.warning(self, tr("操作失败"), tr("选中的图层没有有效的本地物理文件路径，无法删除。"))
            return

        file_list = "\n".join(f"  • {os.path.basename(f)}" for f in all_files_to_delete[:15])
        if len(all_files_to_delete) > 15:
            file_list += f"\n  ...等共 {len(all_files_to_delete)} 个文件"

        reply = QMessageBox.warning(
            self,
            tr("确认删除多个文件"),
            tr("此操作将永久删除以下物理文件（共 {} 个），且无法恢复：\n\n{}\n\n确定要继续吗？").format(len(all_files_to_delete), file_list),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        if reply != QMessageBox.StandardButton.Yes:
            return

        errors = []
        import gc
        # Release provider locks by removing layers first
        project = QgsProject.instance()
        for layer in layers:
            try:
                project.removeMapLayer(layer.id())
            except Exception as e:
                import logging
                logging.getLogger(__name__).warning("Failed to remove layer %s from project: %s", layer.id(), e)

        # Force garbage collection to release Windows file locks
        gc.collect()

        # Delete original files
        for f in all_files_to_delete:
            try:
                if os.path.exists(f):
                    os.remove(f)
            except Exception as e:
                errors.append(f"{os.path.basename(f)}: {e}")

        self.refresh()

        if errors:
            QMessageBox.warning(self, tr("部分文件删除失败"), tr("以下文件未能删除：\n") + "\n".join(errors))

    def action_export_temporary_layer(self, layer):
        """保存/导出临时图层为本地文件，并自动在 QGIS 中加载新生成的物理图层"""
        if not isinstance(layer, QgsVectorLayer):
            QMessageBox.warning(self, tr("操作失败"), tr("该功能仅支持矢量临时图层。"))
            return

        file_filter = "GeoPackage (*.gpkg);;ESRI Shapefile (*.shp)"
        default_name = layer.name()
        path, selected_filter = QFileDialog.getSaveFileName(self, tr("保存/导出临时图层"), default_name, file_filter)
        if not path:
            return

        driver_name = "GPKG"
        if path.endswith(".shp"):
            driver_name = "ESRI Shapefile"

        try:
            layer_style = self._capture_layer_style(layer)
            options = QgsVectorFileWriter.SaveVectorOptions()
            options.driverName = driver_name
            options.fileEncoding = "UTF-8"

            # Use writeAsVectorFormatV3 for QGIS 3
            context = QgsProject.instance().transformContext()
            err, err_msg, new_path, new_layer_id = QgsVectorFileWriter.writeAsVectorFormatV3(
                layer, path, context, options
            )

            # Since mock writes return 0 as QgsVectorFileWriter.WriterError.NoError
            # We check if write was successful
            if err == 0:  # NoError
                # Add the new layer to QGIS
                base_name = os.path.splitext(os.path.basename(path))[0]
                new_layer = QgsVectorLayer(path, base_name, "ogr")
                if new_layer and new_layer.isValid():
                    self._apply_layer_style(layer_style, new_layer)
                    QgsProject.instance().addMapLayer(new_layer)
                    # Remove the old temporary layer
                    QgsProject.instance().removeMapLayer(layer.id())
                    self.refresh()
                    QMessageBox.information(self, tr("保存成功"), tr("临时图层已成功保存为文件，并已加载到工程中。"))
                else:
                    QMessageBox.warning(self, tr("操作失败"), tr("文件已成功保存，但加载新图层失败。"))
            else:
                QMessageBox.warning(self, tr("保存失败"), tr("保存临时图层失败: {}").format(err_msg))
        except Exception as e:
            QMessageBox.warning(self, tr("操作失败"), tr("发生异常错误: {}").format(str(e)))

    @staticmethod
    def _capture_layer_style(layer):
        """Create an independent snapshot of all project-level layer styling."""
        style = QgsMapLayerStyle()
        style.readFromLayer(layer)
        return style

    @staticmethod
    def _apply_layer_style(style, layer):
        """Restore symbology, labeling, diagrams, forms, and custom properties."""
        style.writeToLayer(layer)
        layer.triggerRepaint()

    def action_export_temporary_layers(self, layers):
        """在一个批量对话框中保存选中的多个临时矢量图层。"""
        vector_layers = [layer for layer in layers if isinstance(layer, QgsVectorLayer)]
        if not vector_layers:
            QMessageBox.warning(self, tr("操作失败"), tr("没有可保存的临时矢量图层。"))
            return

        try:
            from .batch_export_dialog import BatchTemporaryLayerExportDialog
        except ImportError:
            from batch_export_dialog import BatchTemporaryLayerExportDialog

        project_path = QgsProject.instance().fileName()
        initial_dir = os.path.dirname(project_path) if project_path else ""
        dialog = BatchTemporaryLayerExportDialog(vector_layers, initial_dir, self)
        if not dialog.exec():
            return

        options = dialog.export_options()
        selected_layer_ids = options.pop("layer_ids")
        if not selected_layer_ids:
            QMessageBox.warning(self, tr("未选择图层"), tr("请至少勾选一个要保存的图层。"))
            return
        if not options["destination"]:
            QMessageBox.warning(self, tr("目标位置无效"), tr("请选择有效的保存位置。"))
            return

        # The dialog is modal and QGIS may refresh or remove layers while it is
        # open. Reacquire wrappers by ID instead of trusting stored references.
        project = QgsProject.instance()
        options["layers"] = []
        for layer_id in selected_layer_ids:
            current_layer = project.mapLayer(layer_id)
            if current_layer is not None:
                options["layers"].append(current_layer)
        if not options["layers"]:
            QMessageBox.warning(
                self,
                tr("图层已失效"),
                tr("所选临时图层已被移除或替换，请刷新后重新选择。"),
            )
            return

        self._export_temporary_layers_batch(**options)

    @staticmethod
    def _safe_export_layer_name(name):
        """Return a portable OGR layer/file name."""
        invalid = '<>:"/\\|?*'
        cleaned = "".join("_" if char in invalid or ord(char) < 32 else char for char in name)
        return cleaned.strip(" .") or "layer"

    @staticmethod
    def _container_layer_exists(path, layer_name):
        if not os.path.exists(path):
            return False
        probe = QgsVectorLayer("{}|layername={}".format(path, layer_name), layer_name, "ogr")
        return bool(probe and probe.isValid())

    def _resolve_export_name(self, destination, driver, requested, conflict, used_names):
        """Resolve duplicate names without overwriting unless explicitly requested."""
        candidate = self._safe_export_layer_name(requested)

        def exists_on_disk(name):
            if driver == "ESRI Shapefile":
                return os.path.exists(os.path.join(destination, name + ".shp"))
            return self._container_layer_exists(destination, name)

        duplicate_in_batch = candidate.casefold() in used_names
        duplicate_on_disk = exists_on_disk(candidate)
        if not duplicate_in_batch and (not duplicate_on_disk or conflict == "overwrite"):
            used_names.add(candidate.casefold())
            return candidate
        if conflict == "skip":
            return None

        base = candidate
        suffix = 2
        while (
            "{}_{}".format(base, suffix).casefold() in used_names
            or exists_on_disk("{}_{}".format(base, suffix))
        ):
            suffix += 1
        candidate = "{}_{}".format(base, suffix)
        used_names.add(candidate.casefold())
        return candidate

    def _export_temporary_layers_batch(
        self, layers, driver, destination, conflict="rename", replace=True
    ):
        """Write a batch and replace only layers whose outputs validate."""
        if driver == "ESRI Shapefile":
            if not os.path.isdir(destination):
                QMessageBox.warning(self, tr("目标位置无效"), tr("Shapefile 的目标位置必须是已有文件夹。"))
                return
        else:
            parent_dir = os.path.dirname(os.path.abspath(destination))
            if not os.path.isdir(parent_dir):
                QMessageBox.warning(self, tr("目标位置无效"), tr("目标文件的父文件夹不存在。"))
                return

        successes = []
        skipped = []
        failures = []
        replacement_layer_ids = []
        used_names = set()
        project = QgsProject.instance()
        context = project.transformContext()

        # Snapshot every source before writing or adding any destination layer.
        # Project signals fired later in the batch must not force us to query a
        # wrapper which QGIS may already have destroyed.
        source_records = []
        for layer in layers:
            try:
                source_records.append(
                    {
                        "layer": layer,
                        "name": layer.name(),
                        "id": layer.id(),
                        "style": self._capture_layer_style(layer),
                    }
                )
            except (RuntimeError, TypeError):
                failures.append(tr("已删除的临时图层：无法读取图层信息"))

        for record in source_records:
            layer = record["layer"]
            layer_name = record["name"]
            layer_id = record["id"]
            layer_style = record["style"]

            output_name = self._resolve_export_name(
                destination, driver, layer_name, conflict, used_names
            )
            if output_name is None:
                skipped.append(layer_name)
                continue

            output_path = (
                os.path.join(destination, output_name + ".shp")
                if driver == "ESRI Shapefile"
                else destination
            )
            writer_options = QgsVectorFileWriter.SaveVectorOptions()
            writer_options.driverName = driver
            writer_options.fileEncoding = "UTF-8"
            writer_options.layerName = output_name
            if os.path.exists(output_path):
                writer_options.actionOnExistingFile = QgsVectorFileWriter.ActionOnExistingFile.CreateOrOverwriteLayer

            try:
                err, err_msg, _, _ = QgsVectorFileWriter.writeAsVectorFormatV3(
                    layer, output_path, context, writer_options
                )
                if err != 0:
                    failures.append("{}: {}".format(layer_name, err_msg))
                    continue

                source = output_path
                if driver != "ESRI Shapefile":
                    source += "|layername={}".format(output_name)
                new_layer = QgsVectorLayer(source, output_name, "ogr")
                if not new_layer or not new_layer.isValid():
                    failures.append("{}: {}".format(layer_name, tr("写入后验证失败")))
                    continue

                self._apply_layer_style(layer_style, new_layer)
                project.addMapLayer(new_layer)
                if replace:
                    replacement_layer_ids.append(layer_id)
                successes.append(layer_name)
            except Exception as exc:
                failures.append("{}: {}".format(layer_name, str(exc)))

        # Removing a QGIS map layer immediately destroys its wrapped C++ object.
        # Defer all removals until no code below can access the source wrappers.
        if replacement_layer_ids:
            try:
                project.removeMapLayers(replacement_layer_ids)
            except AttributeError:
                for layer_id in replacement_layer_ids:
                    project.removeMapLayer(layer_id)

        self.refresh()
        summary = tr("成功：{} 个\n跳过：{} 个\n失败：{} 个").format(
            len(successes), len(skipped), len(failures)
        )
        if failures:
            details = "\n".join(failures[:10])
            QMessageBox.warning(self, tr("批量保存完成"), summary + "\n\n" + details)
        else:
            QMessageBox.information(self, tr("批量保存完成"), summary)

    def action_delete_gpkg_layer(self, layer):
        """从 GPKG 数据库中永久删除该图层（表），并从工程中移除该图层。"""
        source_path = layer.source()
        phys_path, query_params = split_qgis_source(source_path)

        # Parse table name from query params, e.g. |layername=my_table
        table_name = ""
        if "layername=" in query_params:
            for part in query_params.split('|'):
                if part.startswith("layername="):
                    table_name = part.split('=', 1)[1]
                    break
        if not table_name:
            table_name = layer.name()

        db_name = os.path.basename(phys_path)

        reply = QMessageBox.warning(
            self,
            tr("确认删除数据库内图层"),
            tr("此操作将从数据库【{}】中永久删除图层数据表【{}】，且无法恢复！\n\n确定要继续吗？").format(db_name, table_name),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        if reply != QMessageBox.StandardButton.Yes:
            return

        try:
            # 1. Remove from QGIS project first to release locks
            QgsProject.instance().removeMapLayer(layer.id())

            # 2. Force GC to make sure sqlite database connection is closed by this layer
            import gc
            gc.collect()

            # 3. Use OGR provider metadata to delete the layer table cleanly
            try:
                from qgis.core import QgsProviderRegistry
                metadata = QgsProviderRegistry.instance().providerMetadata("ogr")
            except ImportError:
                class MockMetadata:
                    def deleteLayer(self, src): return True
                class MockRegistry:
                    def providerMetadata(self, name): return MockMetadata()
                QgsProviderRegistry = MockRegistry()  # noqa: N806
                metadata = QgsProviderRegistry.providerMetadata("ogr")

            if metadata:
                success = metadata.deleteLayer(source_path)
                if success:
                    QMessageBox.information(self, tr("删除成功"), tr("已成功从数据库中删除图层表【{}】。").format(table_name))
                else:
                    QMessageBox.warning(self, tr("删除失败"), tr("无法从数据库中删除图层表【{}】。").format(table_name))
            else:
                QMessageBox.warning(self, tr("删除失败"), tr("未找到 OGR 数据源管理器，无法删除。"))
        except Exception as e:
            QMessageBox.warning(self, tr("操作失败"), tr("删除数据库内图层发生异常: {}").format(str(e)))

        self.refresh()

    def action_delete_gpkg_layers(self, layers):
        """批量从 GPKG 数据库中永久删除多个图层（表），并从工程中移除它们。"""
        if not layers:
            return

        gpkg_list = []
        for layer in layers:
            source_path = layer.source()
            phys_path, query_params = split_qgis_source(source_path)
            table_name = ""
            if "layername=" in query_params:
                for part in query_params.split('|'):
                    if part.startswith("layername="):
                        table_name = part.split('=', 1)[1]
                        break
            if not table_name:
                table_name = layer.name()
            gpkg_list.append((layer, phys_path, table_name))

        # Format list for prompt
        prompt_list = "\n".join(f"  • 数据库: {os.path.basename(p)}, 表名: {t}" for _, p, t in gpkg_list[:15])
        if len(gpkg_list) > 15:
            prompt_list += f"\n  ...等共 {len(gpkg_list)} 个图层表"

        reply = QMessageBox.warning(
            self,
            tr("确认删除数据库内图层"),
            tr("此操作将从各自的 GeoPackage 数据库中永久删除以下图层表（共 {} 个），且无法恢复！\n\n{}\n\n确定要继续吗？").format(len(gpkg_list), prompt_list),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        if reply != QMessageBox.StandardButton.Yes:
            return

        import gc
        project = QgsProject.instance()
        # Remove from project first to release locks
        for layer, _, _ in gpkg_list:
            try:
                project.removeMapLayer(layer.id())
            except Exception as e:
                import logging
                logging.getLogger(__name__).warning("Failed to remove layer %s: %s", layer.id(), e)

        # Force GC to release file lock handles
        gc.collect()

        # Now use OGR deleteLayer
        errors = []
        try:
            from qgis.core import QgsProviderRegistry
            metadata = QgsProviderRegistry.instance().providerMetadata("ogr")
        except ImportError:
            class MockMetadata:
                def deleteLayer(self, src): return True
            class MockRegistry:
                def providerMetadata(self, name): return MockMetadata()
            QgsProviderRegistry = MockRegistry()  # noqa: N806
            metadata = QgsProviderRegistry.providerMetadata("ogr")

        for layer, _, table_name in gpkg_list:
            if metadata:
                try:
                    success = metadata.deleteLayer(layer.source())
                    if not success:
                        errors.append(f"{table_name}: 删除失败")
                except Exception as e:
                    errors.append(f"{table_name}: {e}")
            else:
                errors.append(f"{table_name}: 未找到 OGR 数据源管理器")

        self.refresh()
        if errors:
            QMessageBox.warning(self, tr("部分图层删除失败"), tr("以下数据库内图层未能成功删除：\n") + "\n".join(errors))
        else:
            QMessageBox.information(self, tr("删除成功"), tr("选中的 {} 个数据库内图层已成功删除。").format(len(gpkg_list)))

    def action_set_layers_visibility(self, layers, visible):
        valid_layers = [layer for layer in layers if layer and layer.isValid()]
        if not valid_layers:
            return
        try:
            project = QgsProject.instance()
        except Exception:
            return

        if not project or not project.layerTreeRoot():
            return

        root = project.layerTreeRoot()
        for layer in valid_layers:
            node = root.findLayer(layer.id())
            if node:
                node.setItemVisibilityChecked(visible)
        self.refresh()

    def action_zoom_to_layers(self, layers):
        if not layers:
            return
        try:
            from qgis.core import QgsRectangle, QgsCoordinateTransform, QgsProject
        except ImportError:
            # Fallback mock for testing environment
            return

        # For a single valid layer, directly use QGIS's native zoom
        if len(layers) == 1:
            layer = layers[0]
            if layer and layer.isValid():
                self.iface.setActiveLayer(layer)
                if hasattr(self.iface, 'zoomToActiveLayer'):
                    self.iface.zoomToActiveLayer()
                    return

        combined_extent = QgsRectangle()
        canvas = self.iface.mapCanvas()
        project_crs = QgsProject.instance().crs()

        for layer in layers:
            if not layer or not layer.isValid():
                continue
            layer_extent = layer.extent()
            if layer_extent.isEmpty():
                continue

            try:
                transform = QgsCoordinateTransform(layer.crs(), project_crs, QgsProject.instance())
                transformed_extent = transform.transformBoundingBox(layer_extent)
                combined_extent.combineExtentWith(transformed_extent)
            except Exception:
                combined_extent.combineExtentWith(layer_extent)

        if not combined_extent.isEmpty():
            combined_extent.scale(1.05)
            canvas.setExtent(combined_extent)
            canvas.refresh()
        else:
            # Multi-layer fallback: zoom to the first valid layer natively
            for layer in layers:
                if layer and layer.isValid():
                    self.iface.setActiveLayer(layer)
                    if hasattr(self.iface, 'zoomToActiveLayer'):
                        self.iface.zoomToActiveLayer()
                        break

    def action_zoom_to_folder(self, folder_path, folder_item=None):
        layers = []
        if folder_item:
            def collect_layers_under_item(item):
                res = []
                if hasattr(item, 'layer') and item.layer:
                    res.append(item.layer)
                for row in range(item.rowCount()):
                    child = item.child(row, 0)
                    if child:
                        res.extend(collect_layers_under_item(child))
                return res
            layers = collect_layers_under_item(folder_item)

        if not layers and folder_path:
            actual_path = resolve_physical_path(folder_path)
            if actual_path:
                try:
                    from qgis.core import QgsProject
                    for layer in QgsProject.instance().mapLayers().values():
                        if layer and layer.source():
                            p_path, _ = split_qgis_source(layer.source())
                            layer_actual = resolve_physical_path(p_path)
                            if layer_actual and os.path.normcase(os.path.abspath(layer_actual)).startswith(os.path.normcase(os.path.abspath(actual_path))):
                                layers.append(layer)
                except ImportError:
                    pass

        self.action_zoom_to_layers(layers)
