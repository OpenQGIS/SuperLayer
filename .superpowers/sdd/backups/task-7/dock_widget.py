import os

# Robust fallback imports for Qt
try:
    from PyQt5.QtCore import Qt, QModelIndex
    from PyQt5.QtWidgets import (QAction, QToolBar, QStackedWidget, QListView, 
                                 QTreeView, QVBoxLayout, QHBoxLayout, QWidget, QLabel, QPushButton, QMenu, QFileDialog, QInputDialog,
                                 QAbstractItemView, QMessageBox, QActionGroup, QHeaderView, QSizePolicy, QDialog)
except ImportError:
    try:
        from qtpy.QtCore import Qt, QModelIndex
        from qtpy.QtWidgets import (QAction, QToolBar, QStackedWidget, QListView, 
                                    QTreeView, QVBoxLayout, QHBoxLayout, QWidget, QLabel, QPushButton, QMenu, QFileDialog, QInputDialog,
                                    QAbstractItemView, QMessageBox, QActionGroup, QHeaderView, QSizePolicy, QDialog)
    except ImportError:
        try:
            from PySide2.QtCore import Qt, QModelIndex
            from PySide2.QtWidgets import (QAction, QToolBar, QStackedWidget, QListView, 
                                           QTreeView, QVBoxLayout, QHBoxLayout, QWidget, QLabel, QPushButton, QMenu, QFileDialog, QInputDialog,
                                           QAbstractItemView, QMessageBox, QActionGroup, QHeaderView, QSizePolicy, QDialog)
        except ImportError:
            try:
                from PySide6.QtCore import Qt, QModelIndex
                from PySide6.QtWidgets import (QToolBar, QStackedWidget, QListView, 
                                               QTreeView, QVBoxLayout, QHBoxLayout, QWidget, QLabel, QPushButton, QMenu, QFileDialog, QInputDialog,
                                               QAbstractItemView, QMessageBox, QHeaderView, QSizePolicy, QDialog)
                from PySide6.QtGui import QAction, QActionGroup
            except ImportError:
                # Basic mock classes for CLI tests without Qt installed
                class Qt:
                    LeftDockWidgetArea = 1
                    RightDockWidgetArea = 2
                    CustomContextMenu = 3
                    UserRole = 32
                    Horizontal = 1
                    AlignLeft = 1
                class QHeaderView:
                    Interactive = 0
                    ResizeToContents = 1
                class QSizePolicy:
                    Fixed = 0
                    Preferred = 1
                class QModelIndex:
                    pass
                class QAction:
                    def __init__(self, text, parent=None):
                        self._text = text
                        self.parent = parent
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
                    def addAction(self, action):
                        self._actions.append(action)
                        return action
                    def addSeparator(self):
                        pass
                    def setSizePolicy(self, h, v):
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
                    def setModel(self, model):
                        self._model = model
                    def setContextMenuPolicy(self, policy):
                        pass
                    def setSelectionMode(self, mode):
                        self._selection_mode = mode
                    def setAlternatingRowColors(self, val):
                        self._alternating_row_colors = val
                    def setEditTriggers(self, triggers):
                        pass
                    class _SelectionModel:
                        def selectedIndexes(self):
                            return []
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
                class QMenu:
                    def __init__(self, parent=None):
                        pass
                    def addAction(self, text):
                        return QAction(text, self)
                    def addMenu(self, text):
                        return QMenu(self)
                    def addSeparator(self):
                        pass
                    def exec_(self, pos):
                        pass
                    def setIcon(self, icon):
                        self._icon = icon
                class QFileDialog:
                    @classmethod
                    def getOpenFileName(cls, *args, **kwargs):
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
                class QMessageBox:
                    Yes = 16384
                    No = 65536
                    @classmethod
                    def warning(cls, parent, title, text):
                        pass
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
    from PyQt5.QtGui import QStandardItemModel, QStandardItem, QIcon
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
    from qgis.core import QgsProject, QgsMapLayer, QgsVectorLayer, QgsRasterLayer
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
            
    class QgsRasterLayer(QgsMapLayer):
        def __init__(self, path, name, provider):
            super().__init__(name, name, path, provider)

# Try importing our modules
try:
    from .layer_model import LayerTreeModel, LayerItem, FolderItem, split_qgis_source
    from .treemap_widget import TreeMapWidget
    from .mindmap_view import MindMapView
    from .file_operations import safe_copy, safe_move, safe_rename, update_layer_source, get_associated_files, format_size, resolve_physical_path
except ImportError:
    try:
        from layer_model import LayerTreeModel, LayerItem, FolderItem, split_qgis_source
        from treemap_widget import TreeMapWidget
        from mindmap_view import MindMapView
        from file_operations import safe_copy, safe_move, safe_rename, update_layer_source, get_associated_files, format_size, resolve_physical_path
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
        def update_layer_source(*args): pass
        def split_qgis_source(x): return x, ""
        def get_associated_files(x): return [x] if x else []
        def format_size(x): return "0 B"


class TreeMapDockWidget(QDialog):
    """The main QDialog container integrating flat list view, directory tree view,
    treemap view, toolbar controls, and context menu actions."""

    def __init__(self, iface, parent=None):
        super().__init__(parent)
        self.iface = iface
        self.setWindowTitle("树状图层管理器")
        
        # Configure window properties
        self.resize(600, 450)
        try:
            self.setWindowFlags(self.windowFlags() | Qt.WindowMinimizeButtonHint | Qt.WindowMaximizeButtonHint)
        except Exception:
            pass
        
        # Setup UI components directly on dialog
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        
        # Toolbar
        self.toolbar = QToolBar()
        self.toolbar.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        self.layout.addWidget(self.toolbar)
        
        # Tag Filter Row container
        self.filter_container = QWidget()
        self.filter_container.setObjectName("filterContainer")
        self.filter_layout = QHBoxLayout(self.filter_container)
        self.filter_layout.setContentsMargins(10, 4, 10, 4)
        self.filter_layout.setSpacing(6)
        self.filter_layout.setAlignment(Qt.AlignLeft)
        
        # Tag Filter Label indicator
        self.filter_label = QLabel("格式过滤:")
        self.filter_label.setStyleSheet("color: #6c757d; font-size: 11px; font-weight: bold;")
        self.filter_layout.addWidget(self.filter_label)
        
        self.layout.addWidget(self.filter_container)
        
        # Selected filter state and cache
        self.current_filter_format = None
        self._current_avail_formats = []
        self.filter_buttons = {}
        
        # Stacked View
        self.stacked_widget = QStackedWidget()
        self.layout.addWidget(self.stacked_widget, 1)
        
        self.physical_tree_view = QTreeView()
        self.physical_tree_view.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.physical_tree_view.setAlternatingRowColors(True)
        
        self.group_tree_view = QTreeView()
        self.group_tree_view.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.group_tree_view.setAlternatingRowColors(True)
        
        self.treemap_view = TreeMapWidget()
        self.mindmap_view = MindMapView()
        
        self.stacked_widget.addWidget(self.physical_tree_view)
        self.stacked_widget.addWidget(self.group_tree_view)
        self.stacked_widget.addWidget(self.treemap_view)
        self.stacked_widget.addWidget(self.mindmap_view)
        
        # Models
        self.physical_model = LayerTreeModel()
        self.group_model = LayerTreeModel()
        

        self.physical_tree_view.setModel(self.physical_model)
        self.group_tree_view.setModel(self.group_model)
        
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
                spacing: 4px;
                padding: 4px;
            }
            QToolBar QToolButton {
                background: transparent;
                border: 1px solid transparent;
                border-radius: 4px;
                padding: 4px 8px;
                font-family: "Microsoft YaHei", "Segoe UI", sans-serif;
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
            QListView, QTreeView, QGraphicsView {
                background-color: #ffffff;
                border: none;
                alternate-background-color: #f8f9fa;
                selection-background-color: #e7f1ff;
                selection-color: #0c63e4;
                font-family: "Microsoft YaHei", "Segoe UI", sans-serif;
                font-size: 12px;
                color: #212529;
            }
            QTreeView::item, QListView::item {
                padding: 6px;
                border-bottom: 1px solid #f1f3f5;
            }
            QTreeView::item:hover, QListView::item:hover {
                background-color: #f1f3f5;
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

    def _setup_toolbar(self):
        self.view_group = QActionGroup(self)
        self.view_group.setExclusive(True)
        
        self.act_physical_tree = QAction("物理文件夹", self)
        self.act_physical_tree.setCheckable(True)
        self.act_physical_tree.setChecked(True)
        self.act_physical_tree.triggered.connect(lambda: self.switch_view(0))
        self.view_group.addAction(self.act_physical_tree)
        self.toolbar.addAction(self.act_physical_tree)
        
        self.act_group_tree = QAction("图层组", self)
        self.act_group_tree.setCheckable(True)
        self.act_group_tree.triggered.connect(lambda: self.switch_view(1))
        self.view_group.addAction(self.act_group_tree)
        self.toolbar.addAction(self.act_group_tree)
        
        self.act_treemap = QAction("矩形树状图", self)
        self.act_treemap.setCheckable(True)
        self.act_treemap.triggered.connect(lambda: self.switch_view(2))
        self.view_group.addAction(self.act_treemap)
        self.toolbar.addAction(self.act_treemap)
        
        self.act_mindmap = QAction("思维导图", self)
        self.act_mindmap.setCheckable(True)
        self.act_mindmap.triggered.connect(lambda: self.switch_view(3))
        self.view_group.addAction(self.act_mindmap)
        self.toolbar.addAction(self.act_mindmap)
        
        self.toolbar.addSeparator()
        
        self.act_refresh = QAction("刷新", self)
        self.act_refresh.triggered.connect(self.refresh)
        self.toolbar.addAction(self.act_refresh)

    def _setup_connections(self):
        # Right click menu context
        self.physical_tree_view.setContextMenuPolicy(Qt.CustomContextMenu)
        self.physical_tree_view.customContextMenuRequested.connect(self.show_physical_tree_context_menu)
        
        self.group_tree_view.setContextMenuPolicy(Qt.CustomContextMenu)
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
        
        # Model item changed connections
        self.physical_model.itemChanged.connect(self.on_item_changed)
        self.group_model.itemChanged.connect(self.on_item_changed)

    def set_tag_button_active(self, btn, active):
        if active:
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #0d6efd;
                    color: #ffffff;
                    border: 1px solid #0d6efd;
                    border-radius: 12px;
                    padding: 3px 10px;
                    font-size: 11px;
                    font-weight: bold;
                }
            """)
        else:
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #f1f3f5;
                    color: #495057;
                    border: 1px solid #ced4da;
                    border-radius: 12px;
                    padding: 3px 10px;
                    font-size: 11px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #e9ecef;
                    color: #212529;
                }
            """)

    def update_filter_tags(self):
        try:
            from .layer_model import get_layer_format
        except ImportError:
            def get_layer_format(l):
                source = getattr(l, 'source', lambda: '')()
                if source.endswith('.shp'): return 'shp'
                if source.endswith('.tif'): return 'tif'
                return 'other'
                
        project = QgsProject.instance()
        formats = set()
        if project:
            for layer in project.mapLayers().values():
                fmt = get_layer_format(layer)
                if fmt:
                    formats.add(fmt.upper())
                    
        priority = {"SHP": 1, "GPKG": 2, "GDB": 3, "TIF": 4, "TIFF": 5, "在线图层": 10, "其他": 20}
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
                        
            btn_all = QPushButton("全部")
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

    def switch_view(self, index):
        self.act_physical_tree.setChecked(index == 0)
        self.act_group_tree.setChecked(index == 1)
        self.act_treemap.setChecked(index == 2)
        self.act_mindmap.setChecked(index == 3)
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

    def _apply_column_widths(self):
        """Apply fixed column widths after model rebuild."""
        for view in (self.physical_tree_view, self.group_tree_view):
            view.setColumnWidth(0, 300)
            view.setColumnWidth(1, 80)
            view.setColumnWidth(2, 250)
            hdr = view.header()
            if hdr and hdr.count() > 2:
                hdr.setSectionResizeMode(0, QHeaderView.Interactive)
                hdr.setSectionResizeMode(1, QHeaderView.ResizeToContents)
                hdr.setSectionResizeMode(2, QHeaderView.Interactive)

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
        finally:
            self._is_refreshing = False

    def on_item_double_clicked(self, index):
        if index.column() > 0:
            index = index.sibling(index.row(), 0)
        
        model = self.physical_model
        if hasattr(index, 'model') and index.model():
            model = index.model()
            
        item = model.itemFromIndex(index)
        if isinstance(item, LayerItem):
            self.focus_layer_by_id(item.layer.id())

    def on_item_changed(self, item):
        # Prevent recursion during model building/refresh
        if hasattr(self, '_is_refreshing') and self._is_refreshing:
            return
            
        new_name = item.text()
        if not new_name:
            return
            
        if isinstance(item, LayerItem):
            layer = item.layer
            if layer and layer.name() != new_name:
                layer.setName(new_name)
                # Refresh to keep other models/views in sync
                self.refresh()
                
        elif isinstance(item, FolderItem):
            # If it's a QGIS virtual group, rename the QGIS group node
            if not item.is_physical:
                old_name = item.data(Qt.UserRole)
                if old_name and old_name != new_name:
                    root = QgsProject.instance().layerTreeRoot()
                    if root:
                        group_node = root.findGroup(old_name)
                        if group_node:
                            group_node.setName(new_name)
                            item.setData(new_name, Qt.UserRole)
                            self.refresh()

    def focus_layer_by_id(self, layer_id):
        layer = QgsProject.instance().mapLayer(layer_id)
        if layer:
            self.iface.setActiveLayer(layer)
            # Zoom to layer
            if hasattr(self.iface, 'zoomToActiveLayer'):
                self.iface.zoomToActiveLayer()

    def get_selected_layers(self, view):
        layers = []
        for idx in view.selectionModel().selectedIndexes():
            if idx.column() > 0:
                continue
            
            model = view.model()
            item = model.itemFromIndex(idx)
            if item and isinstance(item, LayerItem):
                layers.append(item.layer)
        return layers

    def show_physical_tree_context_menu(self, pos):
        idx = self.physical_tree_view.indexAt(pos)
        if idx.isValid() and idx.column() == 0:
            model = self.physical_tree_view.model()
            item = model.itemFromIndex(idx)
            if item:
                if isinstance(item, FolderItem) and item.is_physical and item.folder_path:
                    self._create_folder_context_menu(item.folder_path, self.physical_tree_view.mapToGlobal(pos))
                elif isinstance(item, LayerItem):
                    self._create_layer_context_menu([item.layer], self.physical_tree_view.mapToGlobal(pos))

    def show_group_tree_context_menu(self, pos):
        idx = self.group_tree_view.indexAt(pos)
        if idx.isValid() and idx.column() == 0:
            model = self.group_tree_view.model()
            item = model.itemFromIndex(idx)
            if item and isinstance(item, LayerItem):
                self._create_layer_context_menu([item.layer], self.group_tree_view.mapToGlobal(pos))

    def show_treemap_context_menu(self, node, global_pos):
        if node.layer:
            self._create_layer_context_menu([node.layer], global_pos)
        elif node.is_physical_folder and node.path:
            self._create_folder_context_menu(node.path, global_pos)

    def _create_folder_context_menu(self, folder_path, global_pos):
        actual_path = resolve_physical_path(folder_path)
        if not actual_path or not os.path.exists(actual_path):
            return
            
        menu = QMenu(self)
        menu.setStyleSheet("""
            QMenu {
                background-color: #ffffff;
                border: 1px solid #dee2e6;
                padding: 4px;
            }
            QMenu::item {
                padding: 6px 20px;
                color: #212529;
            }
            QMenu::item:selected {
                background-color: #e7f1ff;
                color: #0c63e4;
            }
        """)
        
        act_open_folder = menu.addAction("打开文件夹位置")
        
        plugin_dir = os.path.dirname(os.path.abspath(__file__))
        icon_path = os.path.join(plugin_dir, "icons_component", "Open_File_Location.svg")
        if os.path.exists(icon_path):
            act_open_folder.setIcon(QIcon(icon_path))
            
        def on_open():
            try:
                norm_path = os.path.normpath(actual_path)
                if os.name == 'nt':
                    import subprocess
                    if os.path.isdir(norm_path):
                        subprocess.Popen(f'explorer.exe "{norm_path}"')
                    else:
                        subprocess.Popen(f'explorer /select,"{norm_path}"')
                else:
                    if os.path.isdir(norm_path):
                        os.startfile(norm_path)
                    else:
                        os.startfile(os.path.dirname(norm_path))
            except Exception as e:
                QMessageBox.warning(self, "操作失败", f"打开文件夹失败: {str(e)}")
                
        act_open_folder.triggered.connect(on_open)
        menu.exec_(global_pos)

    def handle_layer_relocation(self, layer_id, target_folder_path):
        try:
            project = QgsProject.instance()
            layer = project.mapLayer(layer_id)
        except Exception:
            layer = None
            
        if not layer:
            QMessageBox.warning(self, "移动失败", "未找到指定的图层，无法进行文件移动。")
            return
            
        layer_name = layer.name()
        
        if hasattr(layer, 'isEditable') and layer.isEditable():
            QMessageBox.warning(
                self, 
                "移动被拦截", 
                f"图层【{layer_name}】目前处于编辑状态。\n请先在 QGIS 中保存编辑并关闭编辑模式，然后再尝试移动文件。"
            )
            return
            
        source_path = layer.source()
        phys_source_path, query_params = split_qgis_source(source_path)
        actual_source_path = resolve_physical_path(phys_source_path)
        if not actual_source_path or not os.path.exists(actual_source_path):
            QMessageBox.warning(self, "移动失败", f"未找到图层【{layer_name}】的源文件：\n{phys_source_path}")
            return
            
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
                "移动冲突", 
                f"目标文件夹已存在以下同名文件：\n" + "\n".join(conflict_files) + "\n\n操作已被取消，请先清理或重命名冲突文件。"
            )
            return
            
        file_size_text = ""
        try:
            total_size = sum(os.path.getsize(f) for f in files if os.path.exists(f))
            file_size_text = f" (总大小: {format_size(total_size)})"
        except Exception:
            pass
            
        confirm_msg = (
            f"确定要物理移动图层【{layer_name}】的文件吗？\n\n"
            f"源目录: {source_dir}\n"
            f"目标目录: {target_folder_path}\n"
            f"伴生文件数量: {len(files)}{file_size_text}\n\n"
            "此操作将直接修改磁盘物理文件路径并更新 QGIS 数据源链接。"
        )
        
        reply = QMessageBox.question(
            self, 
            "确认物理移动文件", 
            confirm_msg, 
            QMessageBox.Yes | QMessageBox.No, 
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                success = safe_move(layer, target_folder_path)
                if success:
                    self.refresh()
                    QMessageBox.information(self, "移动成功", f"图层【{layer_name}】的文件已成功移动到新目录。")
                else:
                    QMessageBox.critical(self, "移动失败", f"在拷贝或移动图层【{layer_name}】文件时发生未知错误。")
            except Exception as e:
                QMessageBox.critical(self, "移动失败", f"物理移动文件发生异常错误：\n{str(e)}")

    def _create_layer_context_menu(self, layers, global_pos):
        menu = QMenu(self)
        
        plugin_dir = os.path.dirname(os.path.abspath(__file__))
        icons_dir = os.path.join(plugin_dir, "icons_component")
        
        def set_icon(item, svg_name):
            icon_path = os.path.join(icons_dir, svg_name)
            if os.path.exists(icon_path):
                item.setIcon(QIcon(icon_path))
        
        # Single layer actions
        if len(layers) == 1:
            layer = layers[0]
            
            act_datasource = menu.addAction("更换数据源...")
            act_datasource.triggered.connect(lambda: self.action_change_datasource(layer))
            set_icon(act_datasource, "Change_Data_Source.svg")
            
            act_copy_style = menu.addAction("复制并保留样式到新文件夹...")
            act_copy_style.triggered.connect(lambda: self.action_copy_with_style(layer))
            set_icon(act_copy_style, "Copy_to_new_folder.svg")
            
            act_open_folder = menu.addAction("打开文件位置")
            act_open_folder.triggered.connect(lambda: self.action_open_containing_folder(layer))
            set_icon(act_open_folder, "Open_File_Location.svg")
            
            menu.addSeparator()
            
            edit_menu = menu.addMenu("图层编辑")
            set_icon(edit_menu, "Layer_Editing.svg")
            
            # Toggle edit
            if isinstance(layer, QgsVectorLayer):
                pencil_label = "停止编辑" if layer.isEditable() else "开始编辑"
                act_toggle_edit = edit_menu.addAction(pencil_label)
                act_toggle_edit.triggered.connect(lambda: self.action_toggle_edit(layer))
                set_icon(act_toggle_edit, "Start_Editing.svg")
            
            act_rename_layer = edit_menu.addAction("重命名图层...")
            act_rename_layer.triggered.connect(lambda: self.action_rename_layer(layer))
            set_icon(act_rename_layer, "Rename_Layer.svg")
            
            act_rename_file = edit_menu.addAction("重命名物理文件...")
            act_rename_file.triggered.connect(lambda: self.action_rename_file(layer))
            set_icon(act_rename_file, "Renamed_the_original_file.svg")
            
            if isinstance(layer, QgsVectorLayer):
                act_open_attrs = edit_menu.addAction("打开属性表")
                act_open_attrs.triggered.connect(lambda: self.action_open_attribute_table(layer))
                set_icon(act_open_attrs, "Open_Property_Table.svg")
            
            act_properties = edit_menu.addAction("打开图层属性")
            act_properties.triggered.connect(lambda: self.action_open_properties(layer))
            set_icon(act_properties, "Open_Layer_Properties.svg")
        
        # Multi-select actions
        if len(layers) >= 1:
            act_move = menu.addAction(f"移动选中的 {len(layers)} 个文件...")
            act_move.triggered.connect(lambda: self.action_move_files(layers))
            set_icon(act_move, "Move_File.svg")

        menu.exec_(global_pos)

    # Context Actions implementation
    def action_change_datasource(self, layer):
        file_filter = "所有文件 (*)"
        initial_dir = os.path.dirname(layer.source()) if layer.source() else ""
        new_path, _ = QFileDialog.getOpenFileName(self, "更换数据源", initial_dir, file_filter)
        if new_path:
            try:
                update_layer_source(layer, new_path)
                self.refresh()
            except Exception as e:
                QMessageBox.warning(self, "操作失败", f"更换数据源失败: {str(e)}")

    def action_open_containing_folder(self, layer):
        source_path = layer.source()
        phys_path, _ = split_qgis_source(source_path)
        actual_path = resolve_physical_path(phys_path)
        if actual_path and os.path.exists(actual_path):
            try:
                norm_path = os.path.normpath(actual_path)
                if os.name == 'nt':
                    import subprocess
                    subprocess.Popen(f'explorer /select,"{norm_path}"')
                else:
                    dir_path = os.path.dirname(norm_path)
                    if os.path.isdir(dir_path):
                        os.startfile(dir_path)
            except Exception as e:
                QMessageBox.warning(self, "操作失败", f"打开数据所在的文件夹失败: {str(e)}")
        else:
            QMessageBox.warning(self, "操作失败", "该图层没有有效的本地物理数据路径。")

    def action_copy_with_style(self, layer):
        initial_dir = os.path.dirname(layer.source()) if layer.source() else ""
        target_dir = QFileDialog.getExistingDirectory(self, "选择复制目标文件夹", initial_dir)
        if target_dir:
            try:
                # Copy files
                safe_copy(layer.source(), target_dir)
                # Load new layer in QGIS
                new_path = os.path.join(target_dir, os.path.basename(layer.source()))
                new_layer = None
                
                # Use dynamic checking of layer type
                if isinstance(layer, QgsVectorLayer):
                    new_layer = QgsVectorLayer(new_path, f"{layer.name()} (复制)", layer.dataProvider().name())
                elif isinstance(layer, QgsRasterLayer):
                    new_layer = QgsRasterLayer(new_path, f"{layer.name()} (复制)", layer.dataProvider().name())
                else:
                    # General fallback if layer type cannot be determined
                    from qgis.core import QgsProviderRegistry
                    # Auto detect vector/raster using provider registry or extension
                    ext = os.path.splitext(new_path)[1].lower()
                    vector_exts = ['.shp', '.geojson', '.gpkg', '.kml', '.tab']
                    if ext in vector_exts:
                        new_layer = QgsVectorLayer(new_path, f"{layer.name()} (复制)", "ogr")
                    else:
                        new_layer = QgsRasterLayer(new_path, f"{layer.name()} (复制)", "gdal")

                if new_layer and new_layer.isValid():
                    QgsProject.instance().addMapLayer(new_layer)
                    # Apply original symbology
                    if hasattr(layer, 'renderer') and layer.renderer():
                        new_layer.setRenderer(layer.renderer().clone())
                    if hasattr(layer, 'labeling') and layer.labeling():
                        new_layer.setLabeling(layer.labeling().clone())
                    new_layer.triggerRepaint()
                    self.refresh()
            except Exception as e:
                QMessageBox.warning(self, "操作失败", f"复制并应用样式失败: {str(e)}")

    def action_toggle_edit(self, layer):
        if layer.isEditable():
            layer.commitChanges()
        else:
            layer.startEditing()
        self.refresh()

    def action_rename_layer(self, layer):
        new_name, ok = QInputDialog.getText(self, "重命名图层", "请输入新的图层名称:", text=layer.name())
        if ok and new_name:
            layer.setName(new_name)
            self.refresh()

    def action_rename_file(self, layer):
        old_filename = os.path.basename(layer.source())
        new_name, ok = QInputDialog.getText(self, "重命名物理文件", "请输入新的物理文件名 (包含后缀):", text=old_filename)
        if ok and new_name and new_name != old_filename:
            try:
                safe_rename(layer, new_name)
                self.refresh()
            except Exception as e:
                QMessageBox.warning(self, "操作失败", f"重命名文件失败: {str(e)}")

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
        target_dir = QFileDialog.getExistingDirectory(self, "选择移动目标文件夹", initial_dir)
        if target_dir:
            try:
                for layer in layers:
                    safe_move(layer, target_dir)
                self.refresh()
            except Exception as e:
                QMessageBox.warning(self, "操作失败", f"移动文件失败: {str(e)}")
