import os

from qgis.PyQt.QtCore import Qt, QSize
from qgis.PyQt.QtGui import QStandardItemModel, QStandardItem, QIcon, QPixmap, QPainter
from qgis.core import QgsProject, QgsLayerTreeGroup, QgsLayerTreeLayer

try:
    from .translation import tr
except ImportError:
    from translation import tr

try:
    from .file_operations import get_associated_files, split_qgis_source, format_size, resolve_physical_path
except ImportError:
    from file_operations import get_associated_files, split_qgis_source, format_size, resolve_physical_path


def is_layer_visible(layer):
    """Returns the layer's own checkbox state (itemVisibilityChecked).
    Used for UI display (checkbox, icon, context menu) – independent of parent groups."""
    if not layer:
        return True
    try:
        project = QgsProject.instance()
        if project and project.layerTreeRoot():
            node = project.layerTreeRoot().findLayer(layer.id())
            if node:
                return node.itemVisibilityChecked()
    except Exception as e:
        import logging
        logging.getLogger(__name__).debug("Failed to check if layer is visible: %s", e)
    return True


def is_layer_effectively_visible(layer):
    """Returns True only when the layer AND all ancestor groups are checked.
    Used exclusively for the 'only show visible layers' filter – matches what
    the map canvas actually renders."""
    if not layer:
        return True
    try:
        project = QgsProject.instance()
        if project and project.layerTreeRoot():
            node = project.layerTreeRoot().findLayer(layer.id())
            if node:
                return node.isVisible()
    except Exception as e:
        import logging
        logging.getLogger(__name__).debug("Failed to check effective layer visibility: %s", e)
    return True


def is_group_node_visible(qgis_group_node):
    """Returns True if the QGIS group node and all its ancestors are checked.
    Used to decide whether to overlay the hidden icon on a FolderItem."""
    if not qgis_group_node:
        return True
    try:
        if hasattr(qgis_group_node, 'isVisible'):
            return qgis_group_node.isVisible()
    except Exception as e:
        import logging
        logging.getLogger(__name__).debug("Failed to check group node visibility: %s", e)
    return True


FORMAT_COLORS = {
    "sqlite": {
        "bg": "#e8eaf6",       # Indigo Light
        "border": "#c5cae9",   # Indigo Border
        "text": "#1a237e",     # Dark Indigo
        "treemap": "#3f51b5"   # Rich Indigo
    },
    "db": {
        "bg": "#e8eaf6",
        "border": "#c5cae9",
        "text": "#1a237e",
        "treemap": "#3f51b5"
    },
    "spatialite": {
        "bg": "#e8eaf6",
        "border": "#c5cae9",
        "text": "#1a237e",
        "treemap": "#3f51b5"
    },
    "shp": {
        "bg": "#e8f5e9",       # Mint Green Light
        "border": "#a5d6a7",   # Mint Green Border
        "text": "#1b5e20",     # Dark Green
        "treemap": "#50b86c"   # Rich Mint Green
    },
    "gpkg": {
        "bg": "#f3e5f5",       # Soft Lavender Light
        "border": "#e1bee7",   # Soft Lavender Border
        "text": "#4a148c",     # Dark Purple
        "treemap": "#9c27b0"   # Rich Lavender Purple
    },
    "gdb": {
        "bg": "#fff3e0",       # Warm Orange Light
        "border": "#ffcc80",   # Warm Orange Border
        "text": "#e65100",     # Dark Orange
        "treemap": "#ff9800"   # Rich Orange
    },
    "tif": {
        "bg": "#e0f7fa",       # Soft Cyan Light
        "border": "#b2ebf2",   # Soft Cyan Border
        "text": "#006064",     # Dark Cyan
        "treemap": "#00bcd4"   # Rich Cyan
    },
    "tiff": {
        "bg": "#e0f7fa",
        "border": "#b2ebf2",
        "text": "#006064",
        "treemap": "#00bcd4"
    },
    "geojson": {
        "bg": "#fce4ec",       # Soft Rose Light
        "border": "#f8bbd0",   # Soft Rose Border
        "text": "#880e4f",     # Dark Rose
        "treemap": "#e91e63"   # Rich Rose
    },
    "kml": {
        "bg": "#e0f2f1",       # Soft Teal Light
        "border": "#b2dfdb",   # Soft Teal Border
        "text": "#004d40",     # Dark Teal
        "treemap": "#009688"   # Rich Teal
    },
    "kmz": {
        "bg": "#e0f2f1",
        "border": "#b2dfdb",
        "text": "#004d40",
        "treemap": "#009688"
    },
    "csv": {
        "bg": "#efebe9",       # Sand Light
        "border": "#d7ccc8",   # Sand Border
        "text": "#4e342e",     # Dark Sand
        "treemap": "#8d6e63"   # Rich Sand Brown
    },
    "txt": {
        "bg": "#efebe9",
        "border": "#d7ccc8",
        "text": "#4e342e",
        "treemap": "#8d6e63"
    },
    "dxf": {
        "bg": "#ffebee",       # Soft Red Light
        "border": "#ffcdd2",   # Soft Red Border
        "text": "#b71c1c",     # Dark Red
        "treemap": "#f44336"   # Rich Red
    },
    "dwg": {
        "bg": "#ffebee",
        "border": "#ffcdd2",
        "text": "#b71c1c",
        "treemap": "#f44336"
    },
    "virtual": {
        "bg": "#f1f8e9",       # Lime Light
        "border": "#dcedc8",   # Lime Border
        "text": "#33691e",     # Dark Lime
        "treemap": "#8bc34a"   # Rich Lime Green
    },
    "虚拟图层": {
        "bg": "#f1f8e9",
        "border": "#dcedc8",
        "text": "#33691e",
        "treemap": "#8bc34a"
    },
    "memory": {
        "bg": "#eceff1",       # Blue Grey Light
        "border": "#cfd8dc",   # Blue Grey Border
        "text": "#37474f",     # Dark Blue Grey
        "treemap": "#78909c"   # Rich Blue Grey
    },
    "临时图层": {
        "bg": "#eceff1",
        "border": "#cfd8dc",
        "text": "#37474f",
        "treemap": "#78909c"
    },
    "online": {
        "bg": "#e3f2fd",       # Ocean Blue Light
        "border": "#bbdefb",   # Ocean Blue Border
        "text": "#0d47a1",     # Dark Ocean Blue
        "treemap": "#2196f3"   # Rich Ocean Blue
    },
    "在线图层": {
        "bg": "#e3f2fd",
        "border": "#bbdefb",
        "text": "#0d47a1",
        "treemap": "#2196f3"
    },
    "invalid": {
        "bg": "#ffebee",       # Crimson Light
        "border": "#ffcdd2",   # Crimson Border
        "text": "#c62828",     # Dark Crimson
        "treemap": "#e53935"   # Rich Crimson
    },
    "不可用图层": {
        "bg": "#ffebee",
        "border": "#ffcdd2",
        "text": "#c62828",
        "treemap": "#e53935"
    },
    "other": {
        "bg": "#fafafa",       # Neutral Grey Light
        "border": "#e0e0e0",   # Neutral Grey Border
        "text": "#424242",     # Dark Neutral Grey
        "treemap": "#9e9e9e"   # Rich Neutral Grey
    },
    "其他": {
        "bg": "#fafafa",
        "border": "#e0e0e0",
        "text": "#424242",
        "treemap": "#9e9e9e"
    },
    "全部": {
        "bg": "#e2e3e5",       # Neutral Dark Grey Light
        "border": "#d6d8db",   # Neutral Dark Grey Border
        "text": "#383d41",     # Dark Neutral
        "treemap": "#6c757d"   # Dark Grey
    }
}


def get_format_color_dict(fmt):
    if not fmt:
        return FORMAT_COLORS["other"]
    fmt_key = str(fmt).lower()
    if fmt_key in FORMAT_COLORS:
        return FORMAT_COLORS[fmt_key]
    return FORMAT_COLORS["other"]



def _get_layer_icon_path(layer):
    if not layer:
        return ""
    
    plugin_dir = os.path.dirname(os.path.abspath(__file__))
    icons_dir = os.path.join(plugin_dir, "icons_panel")
    
    try:
        if hasattr(layer, 'isValid') and not layer.isValid():
            return os.path.join(icons_dir, "Invalid_Layer.svg")
    except Exception as e:
        import logging
        logging.getLogger(__name__).debug("Failed to check if layer is valid: %s", e)
        
    icon_name = "0_TreeMap_panel.svg"
    
    try:
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

def _create_hidden_layer_icon(base_icon):
    plugin_dir = os.path.dirname(os.path.abspath(__file__))
    hide_svg_path = os.path.join(plugin_dir, "icons_component", "Component_layer_hide.svg")
    if not os.path.exists(hide_svg_path):
        return base_icon
        
    try:
        from unittest.mock import Mock, MagicMock
        if isinstance(base_icon, (Mock, MagicMock)):
            return base_icon
    except ImportError:
        pass
        
    if not hasattr(base_icon, 'availableSizes'):
        return base_icon
        
    sizes = base_icon.availableSizes()
    if not sizes:
        sizes = [QSize(16, 16), QSize(24, 24)]
        
    new_icon = QIcon()
    for size in sizes:
        # Create a completely transparent target pixmap of the correct size
        target_pixmap = QPixmap(size)
        if hasattr(Qt, 'GlobalColor') and hasattr(Qt.GlobalColor, 'transparent'):
            target_pixmap.fill(Qt.GlobalColor.transparent)
        elif hasattr(target_pixmap, 'fill'):
            target_pixmap.fill(0)
            
        # Draw on target_pixmap
        try:
            painter = QPainter(target_pixmap)
            if hasattr(painter, 'setRenderHint') and hasattr(QPainter, 'RenderHint'):
                painter.setRenderHint(QPainter.RenderHint.Antialiasing)
                
            w = size.width() if hasattr(size, 'width') else 16
            h = size.height() if hasattr(size, 'height') else 16
            
            # 1. Draw the base type icon with 30% opacity
            if hasattr(base_icon, 'pixmap'):
                base_pixmap = base_icon.pixmap(size)
                if hasattr(base_pixmap, 'isNull') and not base_pixmap.isNull():
                    if hasattr(painter, 'setOpacity'):
                        painter.setOpacity(0.3)
                    if hasattr(painter, 'drawPixmap'):
                        painter.drawPixmap(0, 0, base_pixmap)
            
            # 2. Draw the hide overlay icon centered, 55% size, 90% opacity
            overlay_w = int(w * 0.55)
            overlay_h = int(h * 0.55)
            overlay_x = (w - overlay_w) // 2
            overlay_y = (h - overlay_h) // 2
            
            overlay_icon = QIcon(hide_svg_path)
            if hasattr(overlay_icon, 'pixmap'):
                overlay_pixmap = overlay_icon.pixmap(QSize(overlay_w, overlay_h))
                if hasattr(overlay_pixmap, 'isNull') and not overlay_pixmap.isNull():
                    if hasattr(painter, 'setOpacity'):
                        painter.setOpacity(0.9)
                    if hasattr(painter, 'drawPixmap'):
                        painter.drawPixmap(overlay_x, overlay_y, overlay_pixmap)
                        
            if hasattr(painter, 'setOpacity'):
                painter.setOpacity(1.0)
            if hasattr(painter, 'end'):
                painter.end()
        except Exception as e:
            import logging
            logging.getLogger(__name__).debug("Failed to draw overlay icon: %s", e)
            
        if hasattr(new_icon, 'addPixmap'):
            new_icon.addPixmap(target_pixmap)
            
    return new_icon


def _create_hidden_folder_icon(base_icon):
    """Returns a dimmed version of *base_icon* with the hide-overlay centred on top.
    Identical visual treatment as _create_hidden_layer_icon but for folder/group items."""
    return _create_hidden_layer_icon(base_icon)


def _get_layer_icon(layer):
    path = _get_layer_icon_path(layer)
    if path and os.path.exists(path):
        base_icon = QIcon(path)
        if layer and not is_layer_visible(layer):
            return _create_hidden_layer_icon(base_icon)
        return base_icon
    return QIcon()


class LayerItem(QStandardItem):
    """QStandardItem subclass representing a QGIS map layer."""
    def __init__(self, layer, display_name):
        super().__init__(display_name)
        self.layer = layer
        if layer:
            self.setData(layer.id(), Qt.ItemDataRole.UserRole)
            self.setCheckable(True)
            self.setCheckState(Qt.CheckState.Checked if is_layer_visible(layer) else Qt.CheckState.Unchecked)
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
        elif path == "在线图层":
            p = os.path.join(icons_dir, "Document_online.svg")
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
    """QStandardItem subclass representing a folder path or QGIS layer group.

    Parameters
    ----------
    group_node : QgsLayerTreeGroup or None
        When provided (virtual groups only) the item overlays the hidden-folder
        icon if the group is not effectively visible on the map canvas.
    """
    def __init__(self, folder_path, is_physical=True, group_node=None):
        special_names = {
            "在线图层": tr("在线图层"),
            "虚拟图层": tr("虚拟图层"),
            "临时图层": tr("临时图层"),
            "不可用图层": tr("不可用图层"),
            "内存与临时图层": tr("内存与临时图层"),
            "无效图层": tr("无效图层"),
        }
        if not folder_path:
            display_name = tr("根目录")
        elif folder_path in special_names:
            display_name = special_names[folder_path]
        else:
            display_name = os.path.basename(folder_path)
        super().__init__(display_name)
        self.folder_path = folder_path
        self.is_physical = is_physical
        self.group_node = group_node
        self.setData(folder_path, Qt.ItemDataRole.UserRole)

        # Load base icon, then optionally overlay the hidden-folder icon
        base_icon = _get_folder_icon(is_physical, folder_path)
        if group_node is not None and not is_group_node_visible(group_node):
            self.setIcon(_create_hidden_folder_icon(base_icon))
        else:
            self.setIcon(base_icon)

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
        elif ext_clean in ['tif', 'tiff', 'jpg', 'jpeg', 'png', 'bmp', 'img', 'asc']:
            return "tif"
        elif ext_clean in ['sqlite', 'db', 'spatialite']:
            return "sqlite"
        return ext_clean
        
    return "其他"


class LayerTreeModel(QStandardItemModel):
    """Model that reads QGIS layers and exposes them grouped by physical folders or virtual groups."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setHorizontalHeaderLabels([tr("图层"), tr("文件大小"), tr("物理路径")])

    def canDropMimeData(self, data, action, row, column, parent):
        if data and hasattr(data, 'hasFormat') and data.hasFormat("application/x-superlayer-group-reorder"):
            return True
        try:
            return super().canDropMimeData(data, action, row, column, parent)
        except AttributeError:
            return False

    def rebuild_model(self, group_by_physical=True, filter_format=None, filter_visible=False,
                      filter_layer_ids=None):
        """Clears and rebuilds the model hierarchy from the current QgsProject."""
        self.clear()
        self.setHorizontalHeaderLabels([tr("图层"), tr("文件大小"), tr("物理路径")])

        project = QgsProject.instance()
        if not project:
            return

        layers = list(project.mapLayers().values())
        if filter_layer_ids is not None:
            layers = [layer for layer in layers if layer.id() in filter_layer_ids]
        if filter_format:
            if filter_format == "不可用图层":
                layers = [layer for layer in layers if hasattr(layer, 'isValid') and not layer.isValid()]
            else:
                layers = [layer for layer in layers if get_layer_format(layer) == filter_format]

        if filter_visible:
            layers = [layer for layer in layers if is_layer_effectively_visible(layer)]

        if group_by_physical:
            self._build_physical_tree(layers)
        else:
            self._build_virtual_tree(filter_format, filter_visible)

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
        parent_dir_items = {} # parent_dir -> [FolderItem, SizeItem, PathItem, total_size, has_visible_layer]
        container_items = {}  # container_path -> [FolderItem, SizeItem, total_size, has_visible_layer]
        
        for layer, phys_path, parent_dir, container_path in processed_items:
            size = self._get_file_size(phys_path)
            is_vis = is_layer_effectively_visible(layer)
            
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
                
                parent_dir_items[parent_dir] = [parent_folder_item, size_item_parent, path_item_parent, 0, False]
                
            parent_folder_item, size_item_parent, path_item_parent, _, _ = parent_dir_items[parent_dir]
            parent_dir_items[parent_dir][3] += size
            if is_vis:
                parent_dir_items[parent_dir][4] = True
            
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
                    container_items[container_path] = [container_folder_item, size_item_container, 0, False]
                    
                target_folder_item, size_item_container, _, _ = container_items[container_path]
                container_items[container_path][2] += size
                if is_vis:
                    container_items[container_path][3] = True
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
            
        # Update folder total size labels and invisible overlay
        for parent_dir, (parent_folder_item, size_item_parent, path_item_parent, total_size, has_vis) in parent_dir_items.items():
            if parent_dir in ["虚拟图层", "临时图层", "不可用图层", "在线图层"]:
                size_item_parent.setText("")
                size_item_parent.setData(0, Qt.ItemDataRole.UserRole)
            else:
                size_item_parent.setText(format_size(total_size))
                size_item_parent.setData(total_size, Qt.ItemDataRole.UserRole)
                
            if not has_vis:
                is_phys = parent_dir not in ["虚拟图层", "临时图层", "不可用图层", "在线图层"]
                base_icon = _get_folder_icon(is_phys, parent_dir)
                parent_folder_item.setIcon(_create_hidden_folder_icon(base_icon))
            
        # Update container total size labels and invisible overlay
        for container_path, (container_folder_item, size_item_container, total_size, has_vis) in container_items.items():
            size_item_container.setText(format_size(total_size))
            size_item_container.setData(total_size, Qt.ItemDataRole.UserRole)
            if not has_vis:
                base_icon = _get_folder_icon(True, container_path)
                container_folder_item.setIcon(_create_hidden_folder_icon(base_icon))

        # Sort and append folders to the model root
        normal_dirs = []
        special_dirs = {} # name -> [folder_item, size_item, path_item]
        special_names = ["虚拟图层", "临时图层", "不可用图层", "在线图层"]
        
        for parent_dir, (folder_item, size_item, path_item, total_size, _) in parent_dir_items.items():
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

    def _build_virtual_tree(self, filter_format=None, filter_visible=False):
        """Builds tree mirroring the native QGIS group/layer structure."""
        root_node = QgsProject.instance().layerTreeRoot()
        if root_node:
            self._traverse_qgis_tree(root_node, self.invisibleRootItem(), filter_format, filter_visible)

    def _traverse_qgis_tree(self, qgis_node, qt_parent_item, filter_format=None, filter_visible=False):
        """Recursively traverses QGIS layer tree nodes and maps them to standard items."""
        for child in qgis_node.children():
            if not child:
                continue
            if isinstance(child, QgsLayerTreeGroup):
                group_item = FolderItem(child.name(), is_physical=False, group_node=child)
                size_item_group = QStandardItem("")
                size_item_group.setFlags(size_item_group.flags() & ~Qt.ItemFlag.ItemIsEditable)
                path_item_group = QStandardItem("")
                path_item_group.setFlags(path_item_group.flags() & ~Qt.ItemFlag.ItemIsEditable)

                # Traverse recursively first
                self._traverse_qgis_tree(child, group_item, filter_format, filter_visible)

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
                        size_item_group.setText("-")
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
                    if filter_visible and not is_layer_effectively_visible(layer):
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
                    
                    size_item = QStandardItem("-")
                    size_item.setData(0, Qt.ItemDataRole.UserRole)
                    size_item.setFlags(size_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                    
                    path_item = QStandardItem("不可用")
                    path_item.setFlags(path_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                    
                    qt_parent_item.appendRow([name_item, size_item, path_item])
