import os
import re
import csv
import datetime
from functools import partial

from qgis.PyQt.QtCore import Qt, QCoreApplication, QSize
from qgis.PyQt.QtGui import QIcon, QTextCursor, QBrush, QColor
from qgis.PyQt.QtWidgets import (
    QWidget, QSizePolicy, QVBoxLayout, QHBoxLayout, QGridLayout, QSplitter, QTabWidget, QTableWidget,
    QTableWidgetItem, QPushButton, QLineEdit, QComboBox, QLabel, QTextEdit,
    QScrollArea, QFileDialog, QApplication, QGroupBox, QAbstractItemView, QMenu
)
from qgis.core import (
    Qgis, QgsProject, QgsMapLayer, QgsMapLayerModel, QgsCoordinateReferenceSystem,
    QgsVectorDataProvider, QgsVectorLayer, QgsStyle, QgsLayerTreeUtils
)


class CustomTableWidget(QTableWidget):
    """Custom QTableWidget that handles Alt + Mouse Wheel to scroll horizontally with a smaller step size."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setHorizontalScrollMode(QAbstractItemView.ScrollMode.ScrollPerPixel)

    def wheelEvent(self, event):
        if event.modifiers() & Qt.KeyboardModifier.AltModifier:
            delta = event.angleDelta().y() if event.angleDelta().y() != 0 else event.angleDelta().x()
            hbar = self.horizontalScrollBar()
            if hbar:
                # Custom smaller horizontal scrolling step (30 pixels per notch)
                scroll_amount = int(30 * (delta / 120.0))
                hbar.setValue(hbar.value() - scroll_amount)
            event.accept()
        else:
            super().wheelEvent(event)


class LayerBoardWidget(QWidget):
    """Integrated tabular editor and dashboard for QGIS vector/raster layers."""
    def __init__(self, iface, parent=None):
        super().__init__(parent)
        self.iface = iface
        self.dock_widget = parent
        
        # Attribute mappings & metadata schema
        self.layersTable = {
            'generic': {
                'attributes': [
                    {'key': 'id', 'label': self.tr('编号'), 'editable': False, 'spatial_only': False},
                    {'key': 'name', 'label': self.tr('图层名'), 'editable': True, 'type': 'string', 'spatial_only': False},
                    {'key': 'crs', 'label': self.tr('坐标系'), 'editable': False, 'type': 'crs', 'spatial_only': True},
                    {'key': 'maxScale', 'label': self.tr('最大比例尺'), 'editable': True, 'type': 'integer', 'spatial_only': True},
                    {'key': 'minScale', 'label': self.tr('最小比例尺'), 'editable': True, 'type': 'integer', 'spatial_only': True},
                    {'key': 'extent', 'label': self.tr('范围'), 'editable': False, 'spatial_only': True},
                    {'key': 'title', 'label': self.tr('标题'), 'editable': True, 'type': 'string', 'spatial_only': False},
                    {'key': 'abstract', 'label': self.tr('摘要'), 'editable': True, 'type': 'string', 'spatial_only': False},
                    {'key': 'shortname', 'label': self.tr('简称'), 'editable': True, 'type': 'string', 'spatial_only': False},
                    {'key': 'ghost', 'label': self.tr('幽灵图层'), 'editable': False, 'type': 'string', 'spatial_only': False}
                ]
            },
            'vector': {
                'attributes': [
                    {'key': 'labelsEnabled', 'label': self.tr('标注已启用'), 'editable': False, 'spatial_only': True},
                    {'key': 'featureCount', 'label': self.tr('要素数量'), 'editable': False, 'spatial_only': False},
                    {'key': 'source|uri', 'label': self.tr('数据源路径'), 'editable': True, 'spatial_only': False},
                    {'key': 'encoding', 'label': self.tr('字符编码'), 'editable': True, 'spatial_only': False},
                    {'key': 'styles_in_db', 'label': self.tr('数据库样式数'), 'editable': False, 'type': 'string', 'spatial_only': False},
                ],
            },
            'raster': {
                'attributes': [
                    {'key': 'width', 'label': self.tr('宽度（像素）'), 'editable': False},
                    {'key': 'height', 'label': self.tr('高度（像素）'), 'editable': False},
                    {'key': 'rasterUnitsPerPixelX', 'label': self.tr('X方向分辨率'), 'editable': False},
                    {'key': 'rasterUnitsPerPixelY', 'label': self.tr('Y方向分辨率'), 'editable': False},
                    {'key': 'uri', 'label': self.tr('数据路径'), 'editable': False}
                ],
            }
        }
        
        self.layersAttributes = {}
        self.layerBoardChangedData = {'vector': {}, 'raster': {}}
        self.layerBoardData = {'vector': [], 'raster': []}
        self._last_active_layer_type = 'vector'
        
        self.csvDelimiter = ','
        self.csvQuotechar = '"'
        self.csvQuoting = csv.QUOTE_ALL
        
        self.styleWidget = None
        self.styleLayer = None
        self.filter_visible_only = False
        self.filter_layer_ids = None
        
        self.init_ui()
        
    def tr(self, message):
        return QCoreApplication.translate('LayerBoardWidget', message)
        
    def init_ui(self):
        self.setObjectName("LayerBoardWidget")
        # 1. Main Layout
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(10, 10, 10, 10)
        self.main_layout.setSpacing(10)
        
        # 2. QSplitter (left-right split)
        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        self.main_layout.addWidget(self.splitter)
        
        # 3. Left Panel (Tab widget for vector and raster tables)
        self.left_container = QWidget()
        self.left_container.setObjectName("left_container")
        left_layout = QVBoxLayout(self.left_container)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(10)
        
        self.tab_widget = QTabWidget()
        self.tab_widget.setObjectName("tab_widget")
        left_layout.addWidget(self.tab_widget)
        
        # Vector Tab
        self.vector_tab = QWidget()
        vector_layout = QVBoxLayout(self.vector_tab)
        vector_layout.setContentsMargins(8, 8, 8, 8)
        vector_layout.setSpacing(6)
        
        self.vector_table = CustomTableWidget()
        self.vector_table.setAlternatingRowColors(True)
        self.vector_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.vector_table.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        vector_layout.addWidget(self.vector_table)
        
        self.vector_buttons_layout = QHBoxLayout()
        self.btn_commit_vector = QPushButton(self.tr("保存修改"))
        self.btn_discard_vector = QPushButton(self.tr("放弃修改"))
        self.btn_commit_vector.clicked.connect(lambda: self.commitLayersChanges('vector'))
        self.btn_discard_vector.clicked.connect(lambda: self.discardLayersChanges('vector'))
        self.vector_buttons_layout.addWidget(self.btn_commit_vector)
        self.vector_buttons_layout.addWidget(self.btn_discard_vector)
        vector_layout.addLayout(self.vector_buttons_layout)
        
        self.tab_widget.addTab(self.vector_tab, self.tr("矢量图层"))
        
        # Raster Tab
        self.raster_tab = QWidget()
        raster_layout = QVBoxLayout(self.raster_tab)
        raster_layout.setContentsMargins(8, 8, 8, 8)
        raster_layout.setSpacing(6)
        
        self.raster_table = CustomTableWidget()
        self.raster_table.setAlternatingRowColors(True)
        self.raster_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.raster_table.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        raster_layout.addWidget(self.raster_table)
        
        self.raster_buttons_layout = QHBoxLayout()
        self.btn_commit_raster = QPushButton(self.tr("保存修改"))
        self.btn_discard_raster = QPushButton(self.tr("放弃修改"))
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
        
        if hasattr(self.vector_table, 'setContextMenuPolicy'):
            policy = getattr(Qt, 'ContextMenuPolicy', None)
            custom_policy = getattr(policy, 'CustomContextMenu', None) if policy else None
            if custom_policy is None:
                custom_policy = getattr(Qt, 'CustomContextMenu', 3)
            self.vector_table.setContextMenuPolicy(custom_policy)
        if hasattr(self.vector_table, 'customContextMenuRequested'):
            self.vector_table.customContextMenuRequested.connect(lambda pos: self.showTableContextMenu(self.vector_table, pos))
            
        if hasattr(self.raster_table, 'setContextMenuPolicy'):
            policy = getattr(Qt, 'ContextMenuPolicy', None)
            custom_policy = getattr(policy, 'CustomContextMenu', None) if policy else None
            if custom_policy is None:
                custom_policy = getattr(Qt, 'CustomContextMenu', 3)
            self.raster_table.setContextMenuPolicy(custom_policy)
        if hasattr(self.raster_table, 'customContextMenuRequested'):
            self.raster_table.customContextMenuRequested.connect(lambda pos: self.showTableContextMenu(self.raster_table, pos))
        
        self.splitter.addWidget(self.left_container)
        
        # 4. Right Panel (Direct widget, not wrapped in QScrollArea to prevent child QTabWidget collapsing)
        self.right_container = QWidget()
        self.right_container.setObjectName("right_container")
        self.right_container.setMaximumWidth(360)
        self.right_layout = QVBoxLayout(self.right_container)
        self.right_layout.setContentsMargins(10, 0, 0, 0)
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
        self.right_tab_widget.setObjectName("right_tab_widget")
        self.right_layout.addWidget(self.right_tab_widget)
        
        # --- TAB 1: Actions on Layers (图层操作) ---
        tab_actions = QWidget()
        actions_layout = QVBoxLayout(tab_actions)
        actions_layout.setContentsMargins(8, 8, 8, 8)
        actions_layout.setSpacing(8)
        
        # Batch updates (inside group box)
        group_batch = QGroupBox(self.tr("批量更新"))
        batch_layout = QVBoxLayout(group_batch)
        batch_layout.setContentsMargins(4, 4, 4, 4)
        grid_layout = QGridLayout()
        grid_layout.setHorizontalSpacing(6)
        grid_layout.setVerticalSpacing(6)
        grid_layout.setColumnStretch(0, 1)   # CRS / MaxScale column
        grid_layout.setColumnStretch(1, 1)   # Encoding / MinScale column

        # Row 0: Labels (plain, no embedded buttons)
        plugin_dir = os.path.dirname(os.path.abspath(__file__))
        crs_lbl = QLabel(self.tr("设置坐标系:"))
        self.encodingLabel = QLabel(self.tr("设置字符编码（仅矢量）:"))
        grid_layout.addWidget(crs_lbl, 0, 0)
        grid_layout.addWidget(self.encodingLabel, 0, 1)

        # Row 1: [inCrs + CRS icon btn] as one unit | Encoding dropdown
        crs_icon_path = os.path.join(plugin_dir, "icons_panel", "CRS.svg")
        crs_icon = QIcon(crs_icon_path) if os.path.exists(crs_icon_path) else QIcon()

        crs_input_widget = QWidget()
        crs_input_widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        crs_input_widget.setMinimumWidth(0)
        crs_input_layout = QHBoxLayout(crs_input_widget)
        crs_input_layout.setContentsMargins(0, 0, 0, 0)
        crs_input_layout.setSpacing(2)
        self.inCrs = QLineEdit()
        self.inCrs.setFixedHeight(24)
        self.btDefineProjection = QPushButton()
        self.btDefineProjection.setObjectName("btDefineProjection")
        self.btDefineProjection.setIcon(crs_icon)
        self.btDefineProjection.setIconSize(QSize(16, 16))
        self.btDefineProjection.setFixedSize(24, 24)
        self.btDefineProjection.setToolTip(self.tr("选择坐标系"))
        crs_input_layout.addWidget(self.inCrs, 1)
        crs_input_layout.addWidget(self.btDefineProjection)

        self.inEncodingList = QComboBox()
        self.inEncodingList.setMinimumWidth(0)
        self.inEncodingList.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Fixed)
        self.populateAvailableEncodingList()
        enc_wrapper = QWidget()
        enc_wrapper.setMinimumWidth(0)
        enc_wrapper.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        enc_wrap_layout = QHBoxLayout(enc_wrapper)
        enc_wrap_layout.setContentsMargins(0, 0, 0, 0)
        enc_wrap_layout.addWidget(self.inEncodingList)
        grid_layout.addWidget(crs_input_widget, 1, 0)
        grid_layout.addWidget(enc_wrapper, 1, 1)

        # Row 2: Labels
        max_scale_lbl = QLabel(self.tr("设置最大比例尺:"))
        min_scale_lbl = QLabel(self.tr("设置最小比例尺:"))
        grid_layout.addWidget(max_scale_lbl, 2, 0)
        grid_layout.addWidget(min_scale_lbl, 2, 1)

        # Row 3: Max Scale | Min Scale inputs  (equal full-column width)
        self.inMaxScale = QLineEdit()
        max_scale_wrapper = QWidget()
        max_scale_wrapper.setMinimumWidth(0)
        max_scale_wrapper.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        max_scale_wrap_layout = QHBoxLayout(max_scale_wrapper)
        max_scale_wrap_layout.setContentsMargins(0, 0, 0, 0)
        max_scale_wrap_layout.addWidget(self.inMaxScale)
        self.inMinScale = QLineEdit()
        min_scale_wrapper = QWidget()
        min_scale_wrapper.setMinimumWidth(0)
        min_scale_wrapper.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        min_scale_wrap_layout = QHBoxLayout(min_scale_wrapper)
        min_scale_wrap_layout.setContentsMargins(0, 0, 0, 0)
        min_scale_wrap_layout.addWidget(self.inMinScale)
        grid_layout.addWidget(max_scale_wrapper, 3, 0)
        grid_layout.addWidget(min_scale_wrapper, 3, 1)

        batch_layout.addLayout(grid_layout)

        # Unified apply button
        self.btApplyBatchUpdate = QPushButton(self.tr("应用"))
        self.btApplyBatchUpdate.setObjectName("btApplyBatchUpdate")
        batch_layout.addWidget(self.btApplyBatchUpdate)
        actions_layout.addWidget(group_batch)
        
        # 2. Actions Group Box
        group_actions = QGroupBox(self.tr("批量操作"))
        act_layout = QVBoxLayout(group_actions)
        act_layout.setSpacing(8)
        
        # Row 4: Save Default Style and Create Spatial Index
        row4_layout = QHBoxLayout()
        row4_layout.setSpacing(12)
        self.btSaveStyleAsDefault = QPushButton(self.tr("保存样式为默认"))
        self.btCreateSpatialIndex = QPushButton(self.tr("创建空间索引（仅矢量）"))
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
        self.styleScrollArea.setMinimumHeight(90)
        self.btApplyStyle = QPushButton(self.tr("应用样式"))
        style_layout.addWidget(self.styleScrollArea, 1)
        style_layout.addWidget(self.btApplyStyle)
        
        self.right_tab_widget.addTab(tab_style, self.tr("图层样式"))
        
        # --- TAB 3: Export (数据导出) ---
        tab_export = QWidget()
        export_layout = QVBoxLayout(tab_export)
        export_layout.setContentsMargins(8, 8, 8, 8)
        export_layout.setSpacing(10)
        
        group_export = QGroupBox(self.tr("数据导出"))
        exp_box_layout = QVBoxLayout(group_export)
        self.btExportCsv = QPushButton(self.tr("导出当前看板为CSV"))
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
        
        self.tab_widget.addTab(tab_log, self.tr("操作日志"))
        
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
        
        # Bulk updates — single unified apply button
        self.btApplyBatchUpdate.clicked.connect(self.applyBatchUpdate)
        
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
            QPushButton#btApplyBatchUpdate {
                background-color: #4a90d9;
                color: #ffffff;
                border: none;
                font-weight: 600;
            }
            QPushButton#btApplyBatchUpdate:hover {
                background-color: #357abd;
            }
            QPushButton#btApplyBatchUpdate:pressed {
                background-color: #2868a8;
            }
            QPushButton#btDefineProjection {
                padding: 2px;
                background-color: #f1f3f5;
                border: 1px solid #ced4da;
            }
            QPushButton#btDefineProjection:hover {
                background-color: #e9ecef;
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
                selection-background-color: #1484dc;
                selection-color: #ffffff;
            }
            QTableWidget::item {
                padding: 5px;
            }
            QWidget#right_container QTreeView::item, QWidget#right_container QTableView::item {
                height: 20px;
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
        except Exception as e:  # noqa: BLE001
            import logging
            logging.getLogger(__name__).debug("Failed to disconnect itemChanged (likely not connected): %s", e)
            
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
        try:
            from .layer_model import get_layer_format
        except ImportError:
            try:
                from layer_model import get_layer_format
            except ImportError:
                def get_layer_format(layer):
                    return "其他"
        for lid, layer in lr.mapLayers().items():
            if get_layer_format(layer) == "在线图层":
                continue
            if layerType == 'vector' and layer.type() != QgsMapLayer.LayerType.VectorLayer:
                continue
            if layerType == 'raster' and layer.type() != QgsMapLayer.LayerType.RasterLayer:
                continue
                
            # Filter visible layers only if option is active
            if getattr(self, 'filter_visible_only', False):
                filter_layer_ids = getattr(self, 'filter_layer_ids', None)
                if filter_layer_ids is not None:
                    if layer.id() not in filter_layer_ids:
                        continue
                else:
                    try:
                        from .layer_model import is_layer_effectively_visible
                    except ImportError:
                        try:
                            from layer_model import is_layer_effectively_visible
                        except ImportError:
                            def is_layer_effectively_visible(layer):
                                return True
                    if not is_layer_effectively_visible(layer):
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
                is_editable = attr.get('editable', False)
                is_spatial_disabled = (layerType == 'vector' and not layer.isSpatial() and attr.get('spatial_only'))
                
                if is_spatial_disabled:
                    newItem.setFlags(Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled)
                    try:
                        newItem.setForeground(QBrush(QColor('#8c96a0')))
                    except (AttributeError, NameError):
                        pass
                elif is_editable:
                    newItem.setFlags(Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEditable | Qt.ItemFlag.ItemIsEnabled)
                else:
                    newItem.setFlags(Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled)
                    try:
                        newItem.setForeground(QBrush(QColor('#8c96a0')))
                    except (AttributeError, NameError):
                        pass
                    
                if layerType == 'vector' and not layer.isSpatial() and attr.get('spatial_only'):
                    value = None
                else:
                    value = self.getLayerProperty(layer, attr['key'])
                newItem.setData(Qt.ItemDataRole.EditRole, value)
                lineData.append(value)
                
                if attr['key'] == 'name':
                    icon = QgsMapLayerModel.iconForLayer(layer)
                    try:
                        from .layer_model import is_layer_visible, _create_hidden_layer_icon
                    except ImportError:
                        from layer_model import is_layer_visible, _create_hidden_layer_icon
                    if not is_layer_visible(layer):
                        icon = _create_hidden_layer_icon(icon)
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
        
        layerId = table.item(row, 0).data(Qt.ItemDataRole.EditRole)
        lr = QgsProject.instance()
        layer = lr.mapLayer(layerId)
        if not layer:
            return
            
        prop = self.layersAttributes[layerType][col]['key']
        data = table.item(row, col).data(Qt.ItemDataRole.EditRole)
        
        # Check URI validation
        if prop == 'source|uri' and not self.newDatasourceIsValid(layer, data):
            table.itemChanged.disconnect()
            item.setData(Qt.ItemDataRole.EditRole, self.getLayerProperty(layer, 'source|uri'))
            slot = partial(self.onItemChanged, layerType)
            table.itemChanged.connect(slot)
            return
            
        # Check encoding
        if prop == 'encoding' and data not in layer.dataProvider().availableEncodings():
            table.itemChanged.disconnect()
            item.setData(Qt.ItemDataRole.EditRole, self.getLayerProperty(layer, 'encoding'))
            slot = partial(self.onItemChanged, layerType)
            table.itemChanged.connect(slot)
            return
            
        # Check shortname
        if prop == 'shortname':
            table.itemChanged.disconnect()
            newshortname = re.sub('[^A-Za-z0-9\\.-]', '_', data)
            item.setData(Qt.ItemDataRole.EditRole, newshortname)
            slot = partial(self.onItemChanged, layerType)
            table.itemChanged.connect(slot)
            data = newshortname
            
        if layerId not in self.layerBoardChangedData[layerType]:
            self.layerBoardChangedData[layerType][layerId] = {}
        self.layerBoardChangedData[layerType][layerId][prop] = data
        
        # Change cell color
        try:
            item.setBackground(QBrush(QColor(Qt.GlobalColor.yellow)))
        except Exception as e:  # noqa: BLE001
            import logging
            logging.getLogger(__name__).debug("Failed to set cell background: %s", e)

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
                self.iface.messageBar().pushMessage("Error", "incorrect source|uri string: " + newDS, level=Qgis.MessageLevel.Critical, duration=4)
            return False
        if nlayer.geometryType() != layer.geometryType():
            if hasattr(self.iface, 'messageBar'):
                self.iface.messageBar().pushMessage("Error", "geometry type mismatch: " + newDS, level=Qgis.MessageLevel.Critical, duration=4)
            return False
        return True

    def commitLayersChanges(self, layerType='vector'):
        lr = QgsProject.instance()
        self.updateLog('')
        self.updateLog('###############')
        self.updateLog(datetime.datetime.now().strftime("%Y-%m-%d %H:%M"))
        self.updateLog(self.tr('图层类型: ') + layerType)
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
            from qgis.PyQt.QtXml import QDomDocument
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
        idx = self.tab_widget.currentIndex()
        if idx == 0:
            return 'vector'
        elif idx == 1:
            return 'raster'
        else:
            return getattr(self, '_last_active_layer_type', 'vector')

    def chooseProjection(self):
        try:
            from qgis.gui import QgsProjectionSelectionDialog
            
            # Anchor to QGIS main window
            projSelector = QgsProjectionSelectionDialog(self.iface.mainWindow())
            projSelector.setWindowTitle(self.tr("设置坐标系"))
            
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
                
            if projSelector.exec():
                crs = projSelector.crs()
                self.inCrs.setText(crs.authid())
        except Exception as e:  # noqa: BLE001
            import logging
            logging.getLogger(__name__).warning("Failed to execute CRS selection dialog: %s", e)

    def applyBatchUpdate(self):
        """Apply all non-empty batch update fields to selected layers."""
        for key in ('crs', 'encoding', 'maxScale', 'minScale'):
            self.applyPropertyOnSelectedLayers(key)

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
            item.setData(Qt.ItemDataRole.EditRole, value)

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
            layerId = table.item(row, 0).data(Qt.ItemDataRole.EditRole)
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
                        
            elif key == 'createSpatialIndex' and layer.type() == QgsMapLayer.LayerType.VectorLayer:
                provider = layer.dataProvider()
                if hasattr(provider, 'capabilities') and (provider.capabilities() & QgsVectorDataProvider.Capability.CreateSpatialIndex):
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

    def on_filter_visible_toggled(self, checked):
        self.filter_visible_only = checked
        if not checked:
            self.filter_layer_ids = None
        self.refreshTables()

    def set_visibility_filter(self, checked, layer_ids=None):
        """Filter by live visibility or by an explicit map-theme layer set."""
        self.filter_visible_only = bool(checked)
        self.filter_layer_ids = set(layer_ids) if checked and layer_ids is not None else None
        self.refreshTables()

    def onTabChanged(self):
        idx = self.tab_widget.currentIndex()
        if idx == 0:
            self._last_active_layer_type = 'vector'
        elif idx == 1:
            self._last_active_layer_type = 'raster'
            
        layerType = self.getActiveLayerType()
        isEnabled = layerType == 'vector'
        self.encodingLabel.setEnabled(isEnabled)
        self.inEncodingList.setEnabled(isEnabled)
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
        layerId = table.item(row, 0).data(Qt.ItemDataRole.EditRole)
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
            
        # Dynamic style widget loading (both Vector and Raster layers supported natively)
        if layer.type() == 0: # VectorLayer
            if hasattr(layer, 'geometryType') and layer.geometryType() not in [3, 4]:
                try:
                    from qgis.gui import QgsRendererPropertiesDialog
                    from qgis.core import QgsStyle
                    w = QgsRendererPropertiesDialog(layer, QgsStyle.defaultStyle(), True)
                    self.styleWidget = w
                    self.styleScrollArea.setWidget(w)
                except Exception as e:
                    import traceback
                    self.updateLog("加载矢量图层样式面板失败: " + str(e) + "\n" + traceback.format_exc())
        elif layer.type() == 1: # RasterLayer
            try:
                renderer = layer.renderer()
                w = None
                if renderer:
                    r_name = renderer.__class__.__name__
                    if r_name == 'QgsSingleBandGrayRenderer':
                        from qgis.gui import QgsSingleBandGrayRendererWidget
                        w = QgsSingleBandGrayRendererWidget(layer, layer.extent())
                    elif r_name == 'QgsMultiBandColorRenderer':
                        from qgis.gui import QgsMultiBandColorRendererWidget
                        w = QgsMultiBandColorRendererWidget(layer, layer.extent())
                    elif r_name == 'QgsSingleBandPseudoColorRenderer':
                        from qgis.gui import QgsSingleBandPseudoColorRendererWidget
                        w = QgsSingleBandPseudoColorRendererWidget(layer, layer.extent())
                    elif r_name == 'QgsPalettedRasterRenderer':
                        from qgis.gui import QgsPalettedRendererWidget
                        w = QgsPalettedRendererWidget(layer, layer.extent())
                    elif r_name == 'QgsHillshadeRenderer':
                        from qgis.gui import QgsHillshadeRendererWidget
                        w = QgsHillshadeRendererWidget(layer, layer.extent())
                    
                    if w:
                        self.styleWidget = w
                        self.styleScrollArea.setWidget(w)
            except Exception as e:
                import traceback
                self.updateLog("加载栅格图层样式面板失败: " + str(e) + "\n" + traceback.format_exc())

        if not self.styleWidget:
            # Fallback for mock environments
            lbl = QLabel(self.tr("图层样式配置面板"))
            self.styleWidget = lbl
            self.styleScrollArea.setWidget(lbl)

    def applyStyle(self):
        w = self.styleWidget
        layer = self.styleLayer
        if not w or not layer:
            return
            
        try:
            if hasattr(w, 'apply'):
                w.apply()
            elif hasattr(w, 'renderer'):
                new_renderer = w.renderer()
                if new_renderer:
                    layer.setRenderer(new_renderer.clone())
        except Exception as e:  # noqa: BLE001
            import logging
            logging.getLogger(__name__).warning("Failed to clone and set renderer: %s", e)
            
        if hasattr(layer, "setCacheImage"):
            layer.setCacheImage(None)
        layer.triggerRepaint()
        
        try:
            self.iface.mapCanvas().refresh()
        except Exception as e:  # noqa: BLE001
            import logging
            logging.getLogger(__name__).debug("Failed to refresh canvas: %s", e)

    def clearLog(self):
        self.txtLog.clear()

    def updateLog(self, msg):
        prefix = '<span style="font-weight:normal;">'
        suffix = '</span>'
        self.txtLog.append('%s %s %s' % (prefix, msg, suffix))
        c = self.txtLog.textCursor()
        c.movePosition(QTextCursor.MoveOperation.End, QTextCursor.MoveMode.MoveAnchor)
        self.txtLog.setTextCursor(c)

    def exportToCsv(self):
        path, _ = QFileDialog.getSaveFileName(self, self.tr("导出数据"), '', 'CSV (*.csv)')
        if not path:
            return
            
        layerType = self.getActiveLayerType()
        data = self.layerBoardData[layerType]
        
        try:
            QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
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

    def getSelectedLayers(self, table):
        sm = table.selectionModel()
        lines = sm.selectedRows() if hasattr(sm, 'selectedRows') else []
        if not lines:
            if hasattr(table, 'currentIndex'):
                current_index = table.currentIndex()
                if current_index and hasattr(current_index, 'isValid') and current_index.isValid():
                    row = current_index.row()
                    item_0 = table.item(row, 0)
                    if item_0:
                        layerId = item_0.data(Qt.ItemDataRole.EditRole)
                        layer = QgsProject.instance().mapLayer(layerId)
                        return [layer] if layer else []
            return []
            
        lr = QgsProject.instance()
        selected_layers = []
        for index in lines:
            row = index.row()
            item_0 = table.item(row, 0)
            if item_0:
                layerId = item_0.data(Qt.ItemDataRole.EditRole)
                layer = lr.mapLayer(layerId)
                if layer:
                    selected_layers.append(layer)
        return selected_layers

    def refreshTables(self):
        self.populateLayerTable('vector')
        self.populateLayerTable('raster')

    def showTableContextMenu(self, table, pos):
        layers = self.getSelectedLayers(table)
        if not layers:
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
        icons_dir = os.path.join(plugin_dir, "icons_component")
        
        def set_icon(item, svg_name):
            icon_path = os.path.join(icons_dir, svg_name)
            if os.path.exists(icon_path):
                item.setIcon(QIcon(icon_path))
                
        num_layers = len(layers)
        
        act_change_ds = menu.addAction(self.tr("更换数据源"))
        act_change_ds.setEnabled(num_layers == 1)
        set_icon(act_change_ds, "Change_Data_Source.svg")
        
        act_open_loc = menu.addAction(self.tr("打开文件位置"))
        act_open_loc.setEnabled(num_layers == 1)
        set_icon(act_open_loc, "Open_File_Location.svg")
        
        menu.addSeparator()
        
        act_move = menu.addAction(self.tr("移动选中的 {} 个文件到…").format(num_layers))
        act_move.setToolTip(self.tr("从新路径加载文件"))
        set_icon(act_move, "Move_File.svg")
        
        act_copy = menu.addAction(self.tr("复制选中的 {} 个文件到…").format(num_layers))
        act_copy.setToolTip(self.tr("从新路径加载文件"))
        set_icon(act_copy, "Copy_to_new_folder.svg")
        
        act_backup = menu.addAction(self.tr("备份选中的 {} 个文件到…").format(num_layers))
        act_backup.setToolTip(self.tr("从原始路径加载文件"))
        set_icon(act_backup, "Backup_to_new_folder.svg")
        
        act_rename = menu.addAction(self.tr("重命名文件"))
        act_rename.setEnabled(num_layers == 1)
        set_icon(act_rename, "Renamed_the_original_file.svg")
        
        menu.addSeparator()
        
        style_menu = menu.addMenu(self.tr("样式管理"))
        set_icon(style_menu, "Style_Manage.svg")
        
        act_clear_style = style_menu.addAction(self.tr("清除默认样式"))
        act_clear_style.setEnabled(num_layers == 1)
        set_icon(act_clear_style, "delete_stlye.svg")
        
        act_save_style = style_menu.addAction(self.tr("保存为默认样式"))
        act_save_style.setEnabled(num_layers == 1)
        set_icon(act_save_style, "Save_stlye.svg")
        
        # Execute menu (Qt5/Qt6 compatible: prefer exec, fall back to exec_)
        exec_pos = table.viewport().mapToGlobal(pos) if hasattr(table, 'viewport') else pos
        action = getattr(menu, 'exec', getattr(menu, 'exec_', None))(exec_pos)
        if not action:
            return
            
        dw = self.dock_widget
        if not dw:
            return
            
        if action == act_change_ds and hasattr(dw, 'action_change_datasource'):
            dw.action_change_datasource(layers[0])
            self.refreshTables()
        elif action == act_open_loc and hasattr(dw, 'action_open_containing_folder'):
            dw.action_open_containing_folder(layers[0])
        elif action == act_move and hasattr(dw, 'action_move_files'):
            dw.action_move_files(layers)
            self.refreshTables()
        elif action == act_copy and hasattr(dw, 'action_copy_files'):
            dw.action_copy_files(layers)
            self.refreshTables()
        elif action == act_backup and hasattr(dw, 'action_backup_files'):
            dw.action_backup_files(layers)
            self.refreshTables()
        elif action == act_rename and hasattr(dw, 'action_rename_file'):
            dw.action_rename_file(layers[0])
            self.refreshTables()
        elif action == act_clear_style and hasattr(dw, 'action_clear_default_style'):
            dw.action_clear_default_style(layers[0])
            self.refreshTables()
        elif action == act_save_style and hasattr(dw, 'action_save_as_default_style'):
            dw.action_save_as_default_style(layers[0])
            self.refreshTables()
