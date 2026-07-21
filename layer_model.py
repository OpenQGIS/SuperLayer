import os

try:
    from qgis.PyQt.QtCore import Qt, QSize
    from qgis.PyQt.QtGui import QStandardItemModel, QStandardItem, QIcon, QPixmap, QPainter
except ImportError:
    try:
        from qtpy.QtCore import Qt, QSize
        from qtpy.QtGui import QStandardItemModel, QStandardItem, QIcon, QPixmap, QPainter
    except ImportError:
        try:
            from PySide2.QtCore import Qt, QSize
            from PySide2.QtGui import QStandardItemModel, QStandardItem, QIcon, QPixmap, QPainter
        except ImportError:
            try:
                from PySide6.QtCore import Qt, QSize
                from PySide6.QtGui import QStandardItemModel, QStandardItem, QIcon, QPixmap, QPainter
            except ImportError:
                # Basic mock for environment without PySide/PyQt (allows unit testing on CLI)
                class Qt:
                    UserRole = 32
                    ItemIsEditable = 2
                    class ItemDataRole:
                        UserRole = 32
                    class ItemFlag:
                        NoItemFlags = 0
                        ItemIsEditable = 2
                class QSize:
                    def __init__(self, w, h):
                        pass
                class QIcon:
                    def __init__(self, *args):
                        pass
                class QPixmap:
                    def __init__(self, *args):
                        pass
                    def fill(self, color):
                        pass
                class QPainter:
                    def __init__(self, *args):
                        pass
                    def end(self):
                        pass
                class QStandardItem:
                    def __init__(self, text=""):
                        self._text = text
                        self._data = {}
                        self._children = []
                        self._icon = None
                        self._tooltip = ""
                    def flags(self):
                        return 33
                    def setFlags(self, flags):
                        pass
                    def setData(self, value, role):
                        self._data[role] = value
                    def data(self, role):
                        return self._data.get(role, None)
                    def text(self):
                        return self._text
                    def setText(self, text):
                        self._text = text
                    def setIcon(self, icon):
                        self._icon = icon
                    def icon(self):
                        return self._icon
                    def setToolTip(self, text):
                        self._tooltip = text
                    def toolTip(self):
                        return self._tooltip
                    def appendRow(self, items):
                        if isinstance(items, list):
                            self._children.append(items)
                        else:
                            self._children.append([items])
                    def rowCount(self):
                        return len(self._children)
                    def child(self, row, column=0):
                        if 0 <= row < len(self._children):
                            row_items = self._children[row]
                            if 0 <= column < len(row_items):
                                return row_items[column]
                        return None
                class _Signal:
                    def connect(self, slot): pass
                    def emit(self, *args): pass
                class QStandardItemModel(QStandardItem):
                    def __init__(self, parent=None):
                        super().__init__("")
                        self._headers = []
                        self._root_item = self
                        self.itemChanged = _Signal()
                        self._sort_role = 0
                    def setSortRole(self, role):
                        self._sort_role = role
                    def setHorizontalHeaderLabels(self, labels):
                        self._headers = labels
                    def clear(self):
                        self._children = []
                        self._headers = []
                    def invisibleRootItem(self):
                        return self._root_item
                    def item(self, row, column=0):
                        return self.child(row, column)

try:
    from qgis.core import QgsProject, QgsMapLayer, QgsLayerTreeGroup, QgsLayerTreeLayer
except ImportError:
    # Fallback/Mock classes for environments without QGIS
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
        def layerTreeRoot(self):
            return QgsLayerTreeGroup()

    class QgsMapLayer:
        def __init__(self, layer_id="", name="", source_path=""):
            self._id = layer_id
            self._name = name
            self._source = source_path
        def id(self):
            return self._id
        def name(self):
            return self._name
        def source(self):
            return self._source
        def isValid(self):
            return True

    class QgsLayerTreeGroup:
        def __init__(self, name=""):
            self._name = name
            self._children = []
        def children(self):
            return self._children
        def name(self):
            return self._name

    class QgsLayerTreeLayer:
        def __init__(self, layer):
            self._layer = layer
        def layer(self):
            return self._layer

try:
    from .file_operations import get_associated_files, split_qgis_source, format_size, resolve_physical_path
except ImportError:
    try:
        from file_operations import get_associated_files, split_qgis_source, format_size, resolve_physical_path
    except ImportError:
        def resolve_physical_path(path):
            return path
            
        def split_qgis_source(source_path):
            if not source_path:
                return "", ""
            parts = source_path.split('|', 1)
            if len(parts) == 2:
                return parts[0], '|' + parts[1]
            return source_path, ""
        
        def get_associated_files(file_path):
            phys_path, _ = split_qgis_source(file_path)
            return [phys_path] if (phys_path and os.path.exists(phys_path)) else []

        def format_size(size_in_bytes):
            """Formats the size in bytes to a human-readable string."""
            if size_in_bytes <= 0:
                return "N/A"
            val = float(size_in_bytes)
            for unit in ['B', 'KB', 'MB', 'GB']:
                if val < 1024.0:
                    return f"{val:.2f} {unit}"
                val /= 1024.0
            return f"{val:.2f} TB"


def _get_layer_icon_path(layer):
    if not layer:
        return ""
    
    plugin_dir = os.path.dirname(os.path.abspath(__file__))
    icons_dir = os.path.join(plugin_dir, "icons_panel")
    icon_name = "0_TreeMap_panel.svg"
    
    try:
        if hasattr(layer, 'isValid') and not layer.isValid():
            return os.path.join(icons_dir, "Invalid_Layer.svg")
            
        provider_type = ""
        if hasattr(layer, 'providerType'):
            provider_type = layer.providerType()
            
        if provider_type == 'memory':
            return os.path.join(icons_dir, "Memory.svg")
        elif provider_type == 'virtual':
            return os.path.join(icons_dir, "VirtualLayer.svg")
            
        layer_type = layer.type() if hasattr(layer, 'type') else None
    except Exception:
        layer_type = None
        
    class_name = layer.__class__.__name__
    
    # 1. 3D & Mesh & Point Cloud Layer Types
    if layer_type == 3 or class_name == 'QgsMeshLayer':
        icon_name = "MeshLayer.svg"
    elif layer_type == 5 or class_name == 'QgsPointCloudLayer':
        icon_name = "PointCloudLayer.svg"
    elif layer_type == 6 or class_name == 'QgsTiledSceneLayer':
        icon_name = "TiledScene.svg"
    elif class_name in ['QgsCesium3DTilesLayer', 'Qgs3DTilesLayer']:
        icon_name = "Cesium3dTiles.svg"
    elif layer_type == 4 or class_name == 'QgsVectorTileLayer':
        icon_name = "VectorTiles.svg"
        
    # 2. Raster Layer Types
    elif layer_type == 1 or class_name == 'QgsRasterLayer' or hasattr(layer, 'rasterType'):
        is_xyz = False
        is_wcs = False
        if hasattr(layer, 'dataProvider') and layer.dataProvider():
            provider_name = layer.dataProvider().name().lower()
            if provider_name == 'wms':
                is_xyz = True
            elif provider_name == 'wcs':
                is_wcs = True
        if not is_xyz and 'type=xyz' in getattr(layer, 'source', lambda: '')().lower():
            is_xyz = True
            
        if is_xyz:
            icon_name = "XYZ_Layer.svg"
        elif is_wcs:
            icon_name = "WCS.svg"
        else:
            icon_name = "Raster_Layer.svg"
            
    # 3. Vector Layer Types
    elif layer_type == 0 or class_name == 'QgsVectorLayer' or hasattr(layer, 'geometryType'):
        geom_type = layer.geometryType()
        # Check for NullGeometry (Table layers)
        if geom_type == 3:  # QgsWkbTypes.NullGeometry
            icon_name = "TableLayer.svg"
        else:
            # Check data provider specific vector formats
            provider_name = ""
            if hasattr(layer, 'dataProvider') and layer.dataProvider():
                provider_name = layer.dataProvider().name().lower()
                
            if provider_name == 'mssql':
                icon_name = "Mssql.svg"
            elif provider_name in ['postgres', 'postgis']:
                icon_name = "Postgis.svg"
            elif provider_name == 'oracle':
                icon_name = "Oracle.svg"
            elif provider_name == 'gpx':
                icon_name = "GPX_GPS.svg"
            elif provider_name == 'wfs':
                icon_name = "WFS.svg"
            elif provider_name == 'memory':
                icon_name = "Memory.svg"
            elif provider_name == 'virtual':
                icon_name = "VirtualLayer.svg"
            else:
                # Fallback to geometry type shapes
                if geom_type == 0:  # Point
                    icon_name = "Points_Layer.svg"
                elif geom_type == 1:  # Line
                    icon_name = "Line_Layer.svg"
                elif geom_type == 2:  # Polygon
                    icon_name = "Polygon_layer.svg"
            
    return os.path.join(icons_dir, icon_name)

def _get_layer_icon(layer):
    path = _get_layer_icon_path(layer)
    if path and os.path.exists(path):
        return QIcon(path)
    return QIcon()


class LayerItem(QStandardItem):
    """QStandardItem subclass representing a QGIS map layer."""
    def __init__(self, layer, display_name):
        super().__init__(display_name)
        self.layer = layer
        if layer:
            self.setData(layer.id(), Qt.ItemDataRole.UserRole)
        else:
            self.setData("", Qt.ItemDataRole.UserRole)
            
        # Load and set custom icon
        self.setIcon(_get_layer_icon(layer))

    def is_layer(self):
        return True


def _get_folder_icon_path(is_physical, path=""):
    plugin_dir = os.path.dirname(os.path.abspath(__file__))
    icons_dir = os.path.join(plugin_dir, "icons_panel")
    
    if path:
        if path == "虚拟图层" or path == "临时图层":
            p = os.path.join(icons_dir, "Document_Temporary.svg")
            if os.path.exists(p):
                return p
        elif path == "不可用图层":
            p = os.path.join(icons_dir, "Document_Invalid.svg")
            if os.path.exists(p):
                return p
                
        lower_path = path.lower()
        if lower_path.endswith('.zip'):
            zip_path = os.path.join(icons_dir, "ZIP.svg")
            if os.path.exists(zip_path):
                return zip_path
        elif lower_path.endswith('.gpkg'):
            gpkg_path = os.path.join(icons_dir, "GPKG.svg")
            if os.path.exists(gpkg_path):
                return gpkg_path
        elif lower_path.endswith('.gdb'):
            gdb_path = os.path.join(icons_dir, "GDB.svg")
            if os.path.exists(gdb_path):
                return gdb_path
                
    if is_physical:
        # Physical Folder: try Folder or Document SVG/PNG
        candidates = [
            "Folder.svg",
            "Folder.png",
            "Document.svg",
            "Document.png",
            "0_TreeMap_panel.svg"
        ]
    else:
        # Layer Group: try Group SVG/PNG
        candidates = [
            "Group.svg",
            "Group.png",
            "0_TreeMap_panel.svg"
        ]
        
    for cand in candidates:
        p = os.path.join(icons_dir, cand)
        if os.path.exists(p):
            return p
    return ""

def _get_folder_icon(is_physical, path=""):
    p = _get_folder_icon_path(is_physical, path)
    if p and os.path.exists(p):
        return QIcon(p)
        
    # Fallback to system standard folder icon
    try:
        try:
            from qgis.PyQt.QtWidgets import QApplication, QStyle
        except ImportError:
            try:
                from qtpy.QtWidgets import QApplication, QStyle
            except ImportError:
                try:
                    from PySide2.QtWidgets import QApplication, QStyle
                except ImportError:
                    try:
                        from PySide6.QtWidgets import QApplication, QStyle
                    except ImportError:
                        from PyQt6.QtWidgets import QApplication, QStyle
        
        style = QApplication.style()
        if style:
            return style.standardIcon(QStyle.StandardPixmap.SP_DirIcon)
    except Exception as e:  # noqa: BLE001
        import logging
        logging.getLogger(__name__).debug("Failed to retrieve system standard folder icon: %s", e)
        
    return QIcon()


class FolderItem(QStandardItem):
    """QStandardItem subclass representing a folder path or QGIS layer group."""
    def __init__(self, folder_path, is_physical=True):
        super().__init__(os.path.basename(folder_path) if folder_path else "根目录")
        self.folder_path = folder_path
        self.is_physical = is_physical
        self.setData(folder_path, Qt.ItemDataRole.UserRole)
        
        # Load custom/system icon
        self.setIcon(_get_folder_icon(is_physical, folder_path))

    def is_layer(self):
        return False

def get_layer_format(layer):
    if not layer:
        return "其他"

    try:
        provider_type = ""
        if hasattr(layer, 'providerType'):
            pt = layer.providerType()
            if isinstance(pt, str):
                provider_type = pt.lower()
        if provider_type == 'virtual':
            return "虚拟图层"
        if provider_type == 'memory':
            return "临时图层"
            
        provider = layer.dataProvider()
        if provider:
            pn = provider.name()
            if isinstance(pn, str):
                provider_name = pn.lower()
                if provider_name == 'virtual':
                    return "虚拟图层"
                if provider_name == 'memory':
                    return "临时图层"
                if provider_name in ['wms', 'wfs', 'wcs', 'arcgismapserver', 'arcgisfeatureserver', 'tilexyz', 'vectortile']:
                    return "在线图层"
    except Exception as e:  # noqa: BLE001
        import logging
        logging.getLogger(__name__).debug("Failed to read layer provider name: %s", e)
        
    source = layer.source()
    if not isinstance(source, str) or not source:
        return "其他"
        
    source_lower = source.lower()
    if source_lower.startswith('http://') or source_lower.startswith('https://') or 'url=' in source_lower:
        return "在线图层"
        
    phys_path, _ = split_qgis_source(source)
    if not phys_path:
        return "其他"
        
    if '.gdb' in source_lower or 'gdb:' in source_lower:
        return "gdb"
    elif '.gpkg' in source_lower or 'gpkg:' in source_lower:
        return "gpkg"
        
    _, ext = os.path.splitext(phys_path)
    if ext:
        ext_clean = ext.lower().lstrip('.')
        if ext_clean in ['shp', 'dbf']:
            return "shp"
        elif ext_clean in ['tif', 'tiff']:
            return "tif"
        return ext_clean
        
    return "其他"


class LayerTreeModel(QStandardItemModel):
    """Model that reads QGIS layers and exposes them grouped by physical folders or virtual groups."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setHorizontalHeaderLabels(["图层", "文件大小", "物理路径"])

    def rebuild_model(self, group_by_physical=True, filter_format=None):
        """Clears and rebuilds the model hierarchy from the current QgsProject."""
        self.clear()
        self.setHorizontalHeaderLabels(["图层", "文件大小", "物理路径"])

        project = QgsProject.instance()
        if not project:
            return

        layers = list(project.mapLayers().values())
        if filter_format:
            if filter_format == "不可用图层":
                layers = [l for l in layers if hasattr(l, 'isValid') and not l.isValid()]
            else:
                layers = [l for l in layers if get_layer_format(l) == filter_format]

        if group_by_physical:
            self._build_physical_tree(layers)
        else:
            self._build_virtual_tree(filter_format)

    def _get_file_size(self, file_path):
        """Calculates file size of a layer including all associated sidecar files."""
        if not file_path:
            return 0
        phys_path, _ = split_qgis_source(file_path)
        actual_path = resolve_physical_path(phys_path)
        if not actual_path or not os.path.exists(actual_path):
            return 0
        try:
            associated = get_associated_files(phys_path)
            return sum(os.path.getsize(f) for f in associated if os.path.exists(f))
        except Exception:
            return 0

    def _build_physical_tree(self, layers):
        """Builds a flat list of physical folders containing their respective layer files and sub-containers."""
        processed_items = []
        parent_dir_paths = set()
        
        for layer in layers:
            if not layer:
                continue
                
            provider_type = ""
            try:
                provider_type = layer.providerType()
            except Exception as e:  # noqa: BLE001
                import logging
                logging.getLogger(__name__).debug("Failed to read layer providerType: %s", e)
                
            is_online = False
            format_name = get_layer_format(layer)
            if format_name == "在线图层":
                is_online = True

            if is_online:
                phys_path = "在线图层"
                actual_path = ""
                parent_dir = "在线图层"
                container_path = None
            elif provider_type == 'virtual':
                phys_path = "虚拟图层"
                actual_path = ""
                parent_dir = "虚拟图层"
                container_path = None
            elif provider_type == 'memory':
                phys_path = "临时图层"
                actual_path = ""
                parent_dir = "临时图层"
                container_path = None
            else:
                source = layer.source()
                phys_path, _ = split_qgis_source(source)
                actual_path = resolve_physical_path(phys_path)
                
                path_to_resolve = actual_path if actual_path else phys_path
                if path_to_resolve:
                    norm_actual = os.path.normpath(os.path.abspath(path_to_resolve))
                    lower_path = norm_actual.lower()
                    
                    is_container = False
                    for ext in ['.zip', '.gpkg', '.gdb', '.tar', '.gz']:
                        if lower_path.endswith(ext):
                            is_container = True
                            break
                            
                    if is_container:
                        container_path = norm_actual
                        parent_dir = os.path.dirname(norm_actual)
                    else:
                        container_path = None
                        parent_dir = os.path.dirname(norm_actual)
                else:
                    phys_path = "不可用图层"
                    actual_path = ""
                    parent_dir = "不可用图层"
                    container_path = None
                    
            parent_dir_paths.add(parent_dir)
            processed_items.append((layer, phys_path, parent_dir, container_path))
            
        # 2. Count frequency of parent folder base names to decide formatting
        base_name_counts = {}
        for path in parent_dir_paths:
            base = os.path.basename(path) if path else "根目录"
            base_name_counts[base] = base_name_counts.get(base, 0) + 1
            
        # 3. Create tree hierarchy
        parent_dir_items = {} # parent_dir -> [FolderItem, SizeItem, PathItem, total_size]
        container_items = {}  # container_path -> [FolderItem, SizeItem, total_size]
        
        for layer, phys_path, parent_dir, container_path in processed_items:
            size = self._get_file_size(phys_path)
            
            # a. Ensure parent_dir node exists at the root of the tree
            if parent_dir not in parent_dir_items:
                base = os.path.basename(parent_dir) if parent_dir else "根目录"
                display_name = base
                if base_name_counts.get(base, 0) > 1 and parent_dir and parent_dir not in ["虚拟图层", "临时图层", "不可用图层", "在线图层"]:
                    parent_dir_parent = os.path.dirname(parent_dir)
                    parent_base = os.path.basename(parent_dir_parent) if parent_dir_parent else ""
                    if parent_base:
                        display_name = f"{base} ({parent_base})"
                    else:
                        display_name = f"{base} (.../{base})"
                        
                is_phys = parent_dir not in ["虚拟图层", "临时图层", "不可用图层", "在线图层"]
                parent_folder_item = FolderItem(parent_dir, is_physical=is_phys)
                parent_folder_item.setText(display_name)
                parent_folder_item.setToolTip(parent_dir if parent_dir else "根目录")
                parent_folder_item.setFlags(parent_folder_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                
                size_item_parent = QStandardItem("")
                size_item_parent.setFlags(size_item_parent.flags() & ~Qt.ItemFlag.ItemIsEditable)
                
                path_item_parent = QStandardItem("")
                path_item_parent.setFlags(path_item_parent.flags() & ~Qt.ItemFlag.ItemIsEditable)
                
                parent_dir_items[parent_dir] = [parent_folder_item, size_item_parent, path_item_parent, 0]
                
            parent_folder_item, size_item_parent, path_item_parent, _ = parent_dir_items[parent_dir]
            parent_dir_items[parent_dir][3] += size
            
            # b. Determine target node to append the layer node to
            if container_path:
                if container_path not in container_items:
                    container_folder_item = FolderItem(container_path, is_physical=True)
                    container_folder_item.setText(os.path.basename(container_path))
                    container_folder_item.setToolTip(container_path)
                    container_folder_item.setFlags(container_folder_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                    
                    size_item_container = QStandardItem("")
                    size_item_container.setFlags(size_item_container.flags() & ~Qt.ItemFlag.ItemIsEditable)
                    
                    path_item_container = QStandardItem("")
                    path_item_container.setFlags(path_item_container.flags() & ~Qt.ItemFlag.ItemIsEditable)
                    
                    parent_folder_item.appendRow([container_folder_item, size_item_container, path_item_container])
                    container_items[container_path] = [container_folder_item, size_item_container, 0]
                    
                target_folder_item, size_item_container, _ = container_items[container_path]
                container_items[container_path][2] += size
            else:
                target_folder_item = parent_folder_item
                
            # c. Create and append the LayerItem
            name_item = LayerItem(layer, layer.name())
            size_item = QStandardItem(format_size(size))
            size_item.setData(size, Qt.ItemDataRole.UserRole)
            size_item.setFlags(size_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            
            path_item = QStandardItem(phys_path if phys_path else "")
            path_item.setFlags(path_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            
            target_folder_item.appendRow([name_item, size_item, path_item])
            
        # Update folder total size labels
        for parent_dir, (parent_folder_item, size_item_parent, path_item_parent, total_size) in parent_dir_items.items():
            if parent_dir in ["虚拟图层", "临时图层", "不可用图层", "在线图层"]:
                size_item_parent.setText("")
                size_item_parent.setData(0, Qt.ItemDataRole.UserRole)
            else:
                size_item_parent.setText(format_size(total_size))
                size_item_parent.setData(total_size, Qt.ItemDataRole.UserRole)
            
        # Update container total size labels
        for container_path, (container_folder_item, size_item_container, total_size) in container_items.items():
            size_item_container.setText(format_size(total_size))
            size_item_container.setData(total_size, Qt.ItemDataRole.UserRole)

        # Sort and append folders to the model root
        normal_dirs = []
        special_dirs = {} # name -> [folder_item, size_item, path_item]
        special_names = ["虚拟图层", "临时图层", "不可用图层", "在线图层"]
        
        for parent_dir, (folder_item, size_item, path_item, total_size) in parent_dir_items.items():
            if parent_dir in special_names:
                special_dirs[parent_dir] = [folder_item, size_item, path_item]
            else:
                normal_dirs.append((parent_dir, folder_item, size_item, path_item))
                
        # Sort normal directories alphabetically by display name (case-insensitive)
        normal_dirs.sort(key=lambda x: x[1].text().lower())
        
        # 1. Append normal directories
        for parent_dir, folder_item, size_item, path_item in normal_dirs:
            self.appendRow([folder_item, size_item, path_item])
            
        # 2. Append separator if we have both normal directories and special directories
        has_specials = any(name in special_dirs for name in special_names)
        if normal_dirs and has_specials:
            sep_item = QStandardItem("────────────────────────────────────────────────────────────────────────────────────────────────────")
            sep_item.setFlags(Qt.ItemFlag.NoItemFlags)
            sep_item.setData("separator", Qt.ItemDataRole.UserRole)
            sep_size = QStandardItem("")
            sep_size.setFlags(Qt.ItemFlag.NoItemFlags)
            sep_path = QStandardItem("")
            sep_path.setFlags(Qt.ItemFlag.NoItemFlags)
            self.appendRow([sep_item, sep_size, sep_path])
            
        # 3. Append special directories in exact order: 虚拟图层, 临时图层, 不可用图层, 在线图层
        for name in special_names:
            if name in special_dirs:
                folder_item, size_item, path_item = special_dirs[name]
                self.appendRow([folder_item, size_item, path_item])

    def _build_virtual_tree(self, filter_format=None):
        """Builds tree mirroring the native QGIS group/layer structure."""
        root_node = QgsProject.instance().layerTreeRoot()
        if root_node:
            self._traverse_qgis_tree(root_node, self.invisibleRootItem(), filter_format)

    def _traverse_qgis_tree(self, qgis_node, qt_parent_item, filter_format=None):
        """Recursively traverses QGIS layer tree nodes and maps them to standard items."""
        for child in qgis_node.children():
            if not child:
                continue
            if isinstance(child, QgsLayerTreeGroup):
                group_item = FolderItem(child.name(), is_physical=False)
                size_item_group = QStandardItem("")
                size_item_group.setFlags(size_item_group.flags() & ~Qt.ItemFlag.ItemIsEditable)
                path_item_group = QStandardItem("")
                path_item_group.setFlags(path_item_group.flags() & ~Qt.ItemFlag.ItemIsEditable)

                # Traverse recursively first
                self._traverse_qgis_tree(child, group_item, filter_format)

                # If the group has matching layers, append it to the parent
                if group_item.rowCount() > 0:
                    qt_parent_item.appendRow([group_item, size_item_group, path_item_group])

                    # Aggregate child sizes for the group size label
                    total_group_size = 0
                    for row_idx in range(group_item.rowCount()):
                        child_size_item = group_item.child(row_idx, 1)
                        if child_size_item:
                            val = child_size_item.data(Qt.ItemDataRole.UserRole)
                            if isinstance(val, (int, float)):
                                total_group_size += val

                    if total_group_size > 0:
                        size_item_group.setText(format_size(total_group_size))
                        size_item_group.setData(total_group_size, Qt.ItemDataRole.UserRole)
                    else:
                        size_item_group.setText("N/A")
                        size_item_group.setData(0, Qt.ItemDataRole.UserRole)

            elif isinstance(child, QgsLayerTreeLayer):
                layer = child.layer()
                if layer:
                    if filter_format:
                        if filter_format == "不可用图层":
                            if hasattr(layer, 'isValid') and layer.isValid():
                                continue
                        elif get_layer_format(layer) != filter_format:
                            continue
                    source = layer.source()
                    phys_path, _ = split_qgis_source(source)
                    actual_path = resolve_physical_path(phys_path)
                    size = 0
                    if actual_path and os.path.exists(actual_path):
                        size = self._get_file_size(phys_path)
                        
                    name_item = LayerItem(layer, layer.name())
                    
                    size_item = QStandardItem(format_size(size))
                    size_item.setData(size, Qt.ItemDataRole.UserRole)
                    size_item.setFlags(size_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                    
                    path_item = QStandardItem(phys_path if phys_path else "")
                    path_item.setFlags(path_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                    
                    qt_parent_item.appendRow([name_item, size_item, path_item])
                else:
                    layer_id = child.layerId()
                    name_item = LayerItem(None, child.name())
                    name_item.setData(layer_id, Qt.ItemDataRole.UserRole)
                    
                    size_item = QStandardItem("N/A")
                    size_item.setData(0, Qt.ItemDataRole.UserRole)
                    size_item.setFlags(size_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                    
                    path_item = QStandardItem("不可用")
                    path_item.setFlags(path_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                    
                    qt_parent_item.appendRow([name_item, size_item, path_item])
