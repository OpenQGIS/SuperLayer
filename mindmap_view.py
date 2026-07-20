import os

try:
    from PyQt5.QtCore import Qt, QPointF, QRectF, QLineF, QObject
    from PyQt5.QtCore import pyqtSignal as Signal
    from PyQt5.QtGui import QPainter, QPainterPath, QColor, QFont, QIcon, QPixmap, QPen, QBrush
    from PyQt5.QtWidgets import (QGraphicsView, QGraphicsScene, QGraphicsItem, QGraphicsLineItem,
                                 QGraphicsObject, QStyleOptionGraphicsItem)
except ImportError:
    try:
        from qtpy.QtCore import Qt, QPointF, QRectF, QLineF, QObject, Signal
        from qtpy.QtGui import QPainter, QPainterPath, QColor, QFont, QIcon, QPixmap, QPen, QBrush
        from qtpy.QtWidgets import (QGraphicsView, QGraphicsScene, QGraphicsItem, QGraphicsLineItem,
                                     QGraphicsObject, QStyleOptionGraphicsItem)
    except ImportError:
        try:
            from PySide2.QtCore import Qt, QPointF, QRectF, QLineF, QObject
            from PySide2.QtCore import Signal as Signal
            from PySide2.QtGui import QPainter, QPainterPath, QColor, QFont, QIcon, QPixmap, QPen, QBrush
            from PySide2.QtWidgets import (QGraphicsView, QGraphicsScene, QGraphicsItem, QGraphicsLineItem,
                                         QGraphicsObject, QStyleOptionGraphicsItem)
        except ImportError:
            try:
                from PySide6.QtCore import Qt, QPointF, QRectF, QLineF, QObject, Signal
                from PySide6.QtGui import QPainter, QPainterPath, QColor, QFont, QIcon, QPixmap, QPen, QBrush
                from PySide6.QtWidgets import (QGraphicsView, QGraphicsScene, QGraphicsItem, QGraphicsLineItem,
                                             QGraphicsObject, QStyleOptionGraphicsItem)
            except ImportError:
                # Basic mock for headless test runs
                class Qt:
                    ScrollBarAlwaysOff = 0
                    ScrollBarAlwaysOn = 1
                    UserRole = 32
                    KeepAspectRatio = 1
                    NoPen = 0
                    NoBrush = 0
                    ItemIsSelectable = 1
                    ItemIsFocusable = 2
                    AlignVCenter = 0
                    AlignLeft = 0
                    ElideRight = 0
                    SolidLine = 1
                    LeftButton = 1
                    RightButton = 2
                    MiddleButton = 4
                class QObject:
                    def __init__(self, *args, **kw): pass
                class Signal:
                    def __init__(self, *args): pass
                    def emit(self, *args): pass
                    def connect(self, slot): pass
                class QPointF:
                    def __init__(self, x=0.0, y=0.0):
                        self._x = x
                        self._y = y
                    def x(self): return self._x
                    def y(self): return self._y
                class QRectF:
                    def __init__(self, x=0.0, y=0.0, w=0.0, h=0.0):
                        self._x, self._y, self._w, self._h = x, y, w, h
                    def x(self): return self._x
                    def y(self): return self._y
                    def width(self): return self._w
                    def height(self): return self._h
                    def contains(self, pt): return True
                    def united(self, other): return self
                    def adjusted(self, *args): return self
                    def toRect(self): return self
                class QLineF: pass
                class QPainter:
                    Antialiasing = 1
                    SmoothPixmapTransform = 2
                class QPainterPath:
                    def moveTo(self, *args): pass
                    def cubicTo(self, *args): pass
                    def addRoundedRect(self, *args): pass
                class QColor:
                    def __init__(self, *args): pass
                class QFont:
                    def __init__(self, *args): pass
                    def setBold(self, *args): pass
                class QIcon:
                    def __init__(self, *args): pass
                    def pixmap(self, *args): return QPixmap()
                    def isNull(self): return True
                    def paint(self, *args): pass
                class QPixmap:
                    def __init__(self, *args): pass
                    def isNull(self): return True
                class QPen:
                    def __init__(self, *args): pass
                class QBrush:
                    def __init__(self, *args): pass
                class QGraphicsItem:
                    ItemSelectedHasChanged = 4
                    ItemIsSelectable = 1
                    ItemIsFocusable = 2
                    def __init__(self, *args, **kw): pass
                    def setFlags(self, *args): pass
                    def setAcceptHoverEvents(self, val): pass
                    def setToolTip(self, text): pass
                    def setSelected(self, val):
                        self._selected = val
                    def isSelected(self):
                        return getattr(self, '_selected', False)
                    def scene(self): return None
                    def setZValue(self, val): pass
                    def mapFromScene(self, pt): return pt
                    def sceneBoundingRect(self): return QRectF()
                class QGraphicsLineItem(QGraphicsItem):
                    def __init__(self, *args): super().__init__()
                    def setPen(self, *args): pass
                    def setLine(self, *args): pass
                    def show(self): pass
                    def hide(self): pass
                class QGraphicsObject(QGraphicsItem):
                    layerDoubleClicked = Signal()
                    layerClicked = Signal()
                    layoutChanged = Signal()
                    def __init__(self, *args, **kw):
                        super().__init__(*args, **kw)
                class QStyleOptionGraphicsItem: pass
                class QGraphicsView:
                    NoDrag = 0
                    ScrollHandDrag = 1
                    AnchorUnderMouse = 1
                    def __init__(self, *args, **kw): pass
                    def setScene(self, scene): pass
                    def setDragMode(self, mode): pass
                    def setRenderHints(self, hints): pass
                    def setTransformationAnchor(self, anchor): pass
                    def scale(self, sx, sy): pass
                    def fitInView(self, *args): pass
                    def viewport(self): return None
                    def setHorizontalScrollBarPolicy(self, p): pass
                    def setVerticalScrollBarPolicy(self, p): pass
                    def centerOn(self, item): pass
                class QGraphicsScene:
                    def __init__(self, *args, **kw): pass
                    def clear(self): pass
                    def addItem(self, item): pass
                    def setSceneRect(self, *args): pass
                    def items(self): return []
                    def itemsBoundingRect(self): return QRectF()

try:
    from qgis.core import QgsProject
except ImportError:
    class QgsProject:
        _instance = None
        @classmethod
        def instance(cls):
            if not cls._instance:
                cls._instance = QgsProject()
            return cls._instance
        def mapLayers(self):
            return {}
        def fileName(self):
            return ""

try:
    from .layer_model import _get_layer_icon, _get_folder_icon, split_qgis_source, _get_layer_icon_path, _get_folder_icon_path
except ImportError:
    from layer_model import _get_layer_icon, _get_folder_icon, split_qgis_source, _get_layer_icon_path, _get_folder_icon_path

try:
    from .file_operations import resolve_physical_path
except ImportError:
    try:
        from file_operations import resolve_physical_path
    except ImportError:
        def resolve_physical_path(path):
            return path

try:
    from PyQt5.QtSvg import QSvgRenderer
except ImportError:
    class QSvgRenderer:
        def __init__(self, path=None):
            self._path = path
        def isValid(self):
            return bool(self._path)
        def render(self, painter, rect):
            pass


def truncate_middle_path(path_str, max_len=30):
    if not path_str or len(path_str) <= max_len:
        return path_str
        
    import re
    temp = path_str.replace(" / ", "/").replace(" \\ ", "\\")
    parts = re.split(r'[\\/]', temp)
    parts = [p.strip() for p in parts if p.strip()]
    
    if len(parts) < 2:
        half = (max_len - 3) // 2
        if half < 1:
            return path_str[:max_len]
        return path_str[:half] + "……" + path_str[-half:]
        
    if " / " in path_str:
        separator = " / "
    elif " \\ " in path_str:
        separator = " \\ "
    elif "/" in path_str:
        separator = "/"
    else:
        separator = "\\"
        
    if len(parts) >= 3:
        opt1 = separator.join([parts[0], parts[1]]) + separator + "……" + separator + parts[-1]
        if len(opt1) <= max_len:
            return opt1
            
    opt2 = parts[0] + separator + "……" + separator + parts[-1]
    if len(opt2) <= max_len:
        return opt2
        
    reserved = len(separator) * 2 + 2
    available = max_len - reserved
    if available < 4:
        half = (max_len - 3) // 2
        return path_str[:half] + "……" + path_str[-half:]
        
    half = available // 2
    left = parts[0]
    if len(left) > half:
        left = left[:half-1] + "…"
    right = parts[-1]
    if len(right) > half:
        right = "…" + right[-(half-1):]
        
    return left + separator + "……" + separator + right


class MindMapNode:
    """Logical model representing a node in the file path hierarchy."""
    def __init__(self, name, is_physical_folder=False, layer=None, path=""):
        self.name = name
        self.is_physical_folder = is_physical_folder
        self.layer = layer
        self.path = path
        self.children = []
        self.parent = None
        self.collapsed = False
        
        # Position & Size
        self.x = 0.0
        self.y = 0.0
        self.width = 130.0
        self.height = 36.0
        self.subtree_span = 0.0
        
        self.item = None


class MindMapNodeItem(QGraphicsObject):
    """QGraphicsItem visually representing a folder or layer node."""
    # Signals for double clicks on layers, to focus and zoom in QGIS
    layerDoubleClicked = Signal(str)  # Emits layer ID
    layerClicked = Signal(str)        # Emits layer ID
    layoutChanged = Signal()          # Emits when node is collapsed/expanded

    def __init__(self, node):
        super().__init__()
        self.node = node
        node.item = self
        
        self.setFlags(QGraphicsItem.ItemIsSelectable | QGraphicsItem.ItemIsFocusable)
        self.setAcceptHoverEvents(True)
        self.hovered = False
        self.toggle_hovered = False
        self.drag_highlight = False
        # Tooltip for full folder path
        if node.is_physical_folder and node.path:
            self.setToolTip(node.path)
        
        # Pre-cache Icon
        self.node_icon = QIcon()
        self.svg_path = ""
        self.svg_renderer = None
        
        # 1. Resolve SVG Path
        if node.layer:
            self.svg_path = _get_layer_icon_path(node.layer)
        elif node.parent is None:
            plugin_dir = os.path.dirname(os.path.abspath(__file__))
            icons_dir = os.path.join(plugin_dir, "icons_panel")
            qgis_proj_path = os.path.join(icons_dir, "QGIS_Project.svg")
            if os.path.exists(qgis_proj_path):
                self.svg_path = qgis_proj_path
            else:
                self.svg_path = _get_folder_icon_path(is_physical=node.is_physical_folder, path=node.path)
        elif node.name == "内存与临时图层":
            plugin_dir = os.path.dirname(os.path.abspath(__file__))
            self.svg_path = os.path.join(plugin_dir, "icons_panel", "Memory.svg")
        elif node.name == "虚拟图层":
            plugin_dir = os.path.dirname(os.path.abspath(__file__))
            self.svg_path = os.path.join(plugin_dir, "icons_panel", "VirtualLayer.svg")
        elif node.name == "无效图层":
            plugin_dir = os.path.dirname(os.path.abspath(__file__))
            self.svg_path = os.path.join(plugin_dir, "icons_panel", "Document_Invalid.svg")
        elif node.name == "在线图层":
            plugin_dir = os.path.dirname(os.path.abspath(__file__))
            self.svg_path = os.path.join(plugin_dir, "icons_panel", "document_online.svg")
        else:
            self.svg_path = _get_folder_icon_path(is_physical=node.is_physical_folder, path=node.path)
            
        # 2. Check if it's a valid SVG path, and initialize renderer
        if self.svg_path and self.svg_path.lower().endswith('.svg') and os.path.exists(self.svg_path):
            self.svg_renderer = QSvgRenderer(self.svg_path)
            if not self.svg_renderer.isValid():
                self.svg_renderer = None
                
        # 3. Fallback to QIcon if no renderer is available
        if not self.svg_renderer:
            if node.layer:
                self.node_icon = _get_layer_icon(node.layer)
            else:
                self.node_icon = _get_folder_icon(is_physical=node.is_physical_folder, path=node.path)

    def set_drag_highlight(self, highlight):
        self.drag_highlight = highlight
        self.update()

    def boundingRect(self):
        # Expand bounding rect slightly to the right to cover the collapse indicator
        extra = 15.0 if (self.node.children and not self.node.layer) else 5.0
        return QRectF(-2.0, -2.0, self.node.width + extra, self.node.height + 4.0)

    def paint(self, painter, option, widget=None):
        painter.setRenderHint(QPainter.Antialiasing)
        
        # 1. Background round rect
        rect = QRectF(0.0, 0.0, self.node.width, self.node.height)
        path = QPainterPath()
        path.addRoundedRect(rect, 6.0, 6.0)
        
        # Select styles based on states
        is_selected = self.isSelected()
        if self.node.layer:
            # Layer node styling
            bg_color = QColor("#e7f1ff") if is_selected else QColor("#ffffff")
            border_color = QColor("#0d6efd") if (is_selected or self.hovered) else QColor("#dee2e6")
            border_width = 2.0 if is_selected else (1.5 if self.hovered else 1.0)
            text_color = QColor("#0d6efd") if is_selected else QColor("#212529")
        else:
            # Folder node styling
            is_drag_target = getattr(self, 'drag_highlight', False)
            bg_color = QColor("#e7f1ff") if is_drag_target else (QColor("#f1f3f5") if is_selected else QColor("#f8f9fa"))
            border_color = QColor("#0d6efd") if (is_selected or is_drag_target or self.hovered) else QColor("#ced4da")
            border_width = 2.0 if (is_selected or is_drag_target) else (1.5 if self.hovered else 1.0)
            text_color = QColor("#0d6efd") if is_drag_target else QColor("#495057")
            
        painter.fillPath(path, QBrush(bg_color))
        
        pen = QPen(border_color, border_width)
        painter.setPen(pen)
        painter.drawPath(path)
        
        # 2. Draw Icon
        icon_rect = QRectF(8.0, (self.node.height - 18.0) / 2.0, 18.0, 18.0)
        has_icon = False
        
        if self.svg_renderer:
            painter.save()
            painter.setClipRect(icon_rect, Qt.IntersectClip)
            self.svg_renderer.render(painter, icon_rect)
            painter.restore()
            has_icon = True
        elif self.node_icon and not self.node_icon.isNull():
            self.node_icon.paint(painter, icon_rect.toRect())
            has_icon = True
            
        if has_icon:
            text_start_x = 32
        else:
            text_start_x = 10
            
        # 3. Draw Text
        painter.setPen(QPen(text_color))
        font = QFont("Microsoft YaHei", 9)
        if is_selected:
            font.setBold(True)
        painter.setFont(font)
        
        # Elide text if too long for node
        font_metrics = painter.fontMetrics()
        available_width = self.node.width - text_start_x - 10
        elided_name = font_metrics.elidedText(self.node.name, Qt.ElideRight, int(available_width))
        
        # Vertically centered text
        text_rect = QRectF(text_start_x, 0.0, available_width, self.node.height)
        painter.drawText(text_rect, Qt.AlignVCenter | Qt.AlignLeft, elided_name)
        
        # 4. Draw Collapse/Expand indicator for folders with children
        if self.node.children and not self.node.layer:
            indicator_x = self.node.width
            indicator_y = self.node.height / 2.0
            radius = 7.0
            
            # Indicator background
            circle_color = QColor("#0d6efd") if self.toggle_hovered else QColor("#adb5bd")
            painter.setPen(Qt.NoPen)
            painter.setBrush(QBrush(circle_color))
            painter.drawEllipse(QPointF(indicator_x, indicator_y), radius, radius)
            
            # Plus/Minus sign
            painter.setPen(QPen(QColor("#ffffff"), 1.5))
            # Horizontal line (always drawn)
            painter.drawLine(QPointF(indicator_x - 4, indicator_y), QPointF(indicator_x + 4, indicator_y))
            # Vertical line (only if collapsed)
            if self.node.collapsed:
                painter.drawLine(QPointF(indicator_x, indicator_y - 4), QPointF(indicator_x, indicator_y + 4))

    def hoverMoveEvent(self, event):
        pos = event.pos()
        # Check if mouse is hovering over collapse/expand toggle circle
        indicator_x = self.node.width
        indicator_y = self.node.height / 2.0
        distance = ((pos.x() - indicator_x) ** 2 + (pos.y() - indicator_y) ** 2) ** 0.5
        
        old_toggle_hovered = self.toggle_hovered
        self.toggle_hovered = (distance <= 8.0)
        
        if old_toggle_hovered != self.toggle_hovered:
            self.update()
            
        super().hoverMoveEvent(event)

    def hoverEnterEvent(self, event):
        self.hovered = True
        self.update()
        super().hoverEnterEvent(event)

    def hoverLeaveEvent(self, event):
        self.hovered = False
        self.toggle_hovered = False
        self.update()
        super().hoverLeaveEvent(event)

    def mousePressEvent(self, event):
        if event.button() == Qt.RightButton:
            if self.node.layer or (self.node.is_physical_folder and self.node.path):
                self.setSelected(True)
            event.accept()
            return
            
        # Check click target: is it the collapse toggle?
        if self.toggle_hovered and self.node.children and not self.node.layer:
            self.node.collapsed = not self.node.collapsed
            self.update()
            self.layoutChanged.emit()
            event.accept()
        else:
            super().mousePressEvent(event)
            if event.button() == Qt.LeftButton and self.node.layer:
                self._drag_start_pos = event.screenPos()
                self._is_dragging = False
                event.accept()
            elif self.node.layer:
                self.layerClicked.emit(self.node.layer.id())

    def mouseMoveEvent(self, event):
        if event.buttons() & Qt.LeftButton and self.node.layer and hasattr(self, '_drag_start_pos'):
            delta = event.screenPos() - self._drag_start_pos
            dist = (delta.x()**2 + delta.y()**2)**0.5
            
            drag_threshold = 8.0
            try:
                from PyQt5.QtWidgets import QApplication
                drag_threshold = QApplication.startDragDistance()
            except Exception:
                pass
                
            if dist >= drag_threshold:
                if not getattr(self, '_is_dragging', False):
                    self._is_dragging = True
                    view = self.scene().views()[0] if (self.scene() and self.scene().views()) else None
                    if view and hasattr(view, 'start_dragging'):
                        start_pt = self.mapToScene(QPointF(self.node.width / 2.0, self.node.height / 2.0))
                        view.start_dragging(self, start_pt)
                
                if self._is_dragging:
                    view = self.scene().views()[0] if (self.scene() and self.scene().views()) else None
                    if view and hasattr(view, 'update_dragging'):
                        view.update_dragging(event.scenePos())
            event.accept()
        else:
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.RightButton:
            event.accept()
            return
        if event.button() == Qt.LeftButton and self.node.layer:
            if getattr(self, '_is_dragging', False):
                self._is_dragging = False
                view = self.scene().views()[0] if (self.scene() and self.scene().views()) else None
                if view and hasattr(view, 'end_dragging'):
                    view.end_dragging(event.scenePos())
            else:
                self.setSelected(True)
                self.layerClicked.emit(self.node.layer.id())
            event.accept()
        else:
            super().mouseReleaseEvent(event)

    def mouseDoubleClickEvent(self, event):
        if self.node.layer:
            self.layerDoubleClicked.emit(self.node.layer.id())
            event.accept()
        else:
            # Double-clicking a folder toggles expansion as well
            self.node.collapsed = not self.node.collapsed
            self.update()
            self.layoutChanged.emit()
            event.accept()

    def contextMenuEvent(self, event):
        if self.node.layer or (self.node.is_physical_folder and self.node.path):
            self.setSelected(True)
            try:
                from PyQt5.QtGui import QCursor
            except ImportError:
                try:
                    from qtpy.QtGui import QCursor
                except ImportError:
                    try:
                        from PySide2.QtGui import QCursor
                    except ImportError:
                        from PySide6.QtGui import QCursor
            global_pos = QCursor.pos()
            view = self.scene().views()[0] if (self.scene() and self.scene().views()) else None
            if view and hasattr(view, 'on_node_context_menu'):
                view.on_node_context_menu(self.node, global_pos)
            event.accept()
        else:
            super().contextMenuEvent(event)

    def itemChange(self, change, value):
        if change == QGraphicsItem.ItemSelectedHasChanged:
            if self.scene():
                self.scene().update()
        return super().itemChange(change, value)


class MindMapConnectionItem(QGraphicsItem):
    """Draws a smooth cubic Bezier curve link between a parent and child node."""
    def __init__(self, parent_item, child_item):
        super().__init__()
        self.parent_item = parent_item
        self.child_item = child_item
        self.setZValue(-1)  # Draw below nodes

    def boundingRect(self):
        p_rect = self.parent_item.sceneBoundingRect()
        c_rect = self.child_item.sceneBoundingRect()
        # Unify them into a larger bounding rect
        return p_rect.united(c_rect)

    def paint(self, painter, option, widget=None):
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Calculate parent right-middle and child left-middle
        p_rect = self.parent_item.sceneBoundingRect()
        c_rect = self.child_item.sceneBoundingRect()
        
        # Map back to local coordinates
        start_pt = self.mapFromScene(QPointF(p_rect.x() + p_rect.width(), p_rect.y() + p_rect.height() / 2.0))
        end_pt = self.mapFromScene(QPointF(c_rect.x(), c_rect.y() + c_rect.height() / 2.0))
        
        # Create Bezier S-curve
        dx = end_pt.x() - start_pt.x()
        ctrl1 = QPointF(start_pt.x() + dx * 0.4, start_pt.y())
        ctrl2 = QPointF(end_pt.x() - dx * 0.4, end_pt.y())
        
        path = QPainterPath()
        path.moveTo(start_pt)
        path.cubicTo(ctrl1, ctrl2, end_pt)
        
        # Highlight connection line if either node is selected
        is_highlighted = self.parent_item.isSelected() or self.child_item.isSelected()
        
        pen_color = QColor("#0d6efd") if is_highlighted else QColor("#adb5bd")
        pen_width = 2.0 if is_highlighted else 1.25
        
        painter.setPen(QPen(pen_color, pen_width, Qt.SolidLine))
        painter.drawPath(path)


class MindMapView(QGraphicsView):
    """Interactive canvas rendering the path-based mind map of layers."""
    layerSelected = Signal(str)
    layerDoubleClicked = Signal(str)
    contextMenuTriggered = Signal(object, object) # node, global_pos
    layerRelocationRequested = Signal(str, str) # layer_id, target_folder_path

    def __init__(self, parent=None):
        super().__init__(parent)
        self.scene_obj = QGraphicsScene(self)
        self.setScene(self.scene_obj)
        
        # Antialiasing & View Settings
        self.setRenderHints(QPainter.Antialiasing | QPainter.SmoothPixmapTransform)
        self.setDragMode(QGraphicsView.NoDrag) # Dragging nodes with left click, panning with middle click
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        
        # Hide scrollbars for cleaner canvas look
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        self.root_node = None
        self.selected_layer_id = ""
        self._drag_line_item = None
        self._drag_source_item = None
        self._drag_target_item = None
        self._drag_start_pos = None
        self._panning = False
        self._pan_start = None

    def on_node_context_menu(self, node, global_pos):
        self.contextMenuTriggered.emit(node, global_pos)

    def set_layers(self, layers):
        """Loads and visualizes QGIS layers as a physical path mind map."""
        # Save collapse states of current nodes to keep them consistent after refresh
        collapse_states = self._get_current_collapse_states()
        
        self.scene_obj.clear()
        self._drag_line_item = None  # scene.clear() destroys all C++ items; reset the reference
        
        # 1. Build Physical Directory Tree
        self.root_node = self._build_path_tree(layers, collapse_states)
        if not self.root_node:
            return
            
        # 2. Compute Layout & Draw Tree
        self.rebuild_and_draw()
        
        # 3. Fit initial view beautifully
        self.zoom_to_fit()

    def rebuild_and_draw(self):
        """Re-calculates the tree layout structure and draws items."""
        self.scene_obj.clear()
        self._drag_line_item = None  # scene.clear() destroys all C++ items; reset the reference
        if not self.root_node:
            return
            
        # 1. Determine Node dimensions based on label sizes at each depth
        try:
            from PyQt5.QtGui import QFont, QFontMetrics
            font = QFont("Microsoft YaHei", 9)
            font.setBold(True)
            fm = QFontMetrics(font)
            def get_text_width(text):
                return fm.width(text)
        except Exception:
            def get_text_width(text):
                w = 0.0
                for char in text:
                    if ord(char) > 127:
                        w += 14.0
                    else:
                        w += 7.5
                return w

        max_width_by_depth = {}
        def compute_widths(node, depth=0):
            # Dynamic node width to prevent text overflow (icon = 32px + 20px padding)
            node.width = max(130.0, get_text_width(node.name) + 52.0)
            max_width_by_depth[depth] = max(max_width_by_depth.get(depth, 0.0), node.width)
            if not node.collapsed:
                for child in node.children:
                    compute_widths(child, depth + 1)
        compute_widths(self.root_node)
        
        # 2. X coordinates for each depth column
        x_by_depth = {}
        curr_x = 20.0
        for depth in sorted(max_width_by_depth.keys()):
            x_by_depth[depth] = curr_x
            curr_x += max_width_by_depth[depth] + 75.0  # Column width + Horizontal spacing
            
        # 3. Calculate Vertical Subtree Spans (Bottom-Up)
        dy = 24.0 # vertical gap
        def calc_spans(node):
            if node.collapsed or not node.children:
                node.subtree_span = node.height
                return node.subtree_span
                
            total = 0.0
            for child in node.children:
                total += calc_spans(child)
            total += (len(node.children) - 1) * dy
            node.subtree_span = max(node.height, total)
            return node.subtree_span
        calc_spans(self.root_node)
        
        # 4. Assign Coordinates (Top-Down)
        def assign_coords(node, depth=0, center_y=0.0):
            node.x = x_by_depth[depth]
            node.y = center_y
            
            if node.collapsed or not node.children:
                return
                
            child_start_y = center_y - node.subtree_span / 2.0
            curr_y = child_start_y
            for child in node.children:
                span = child.subtree_span
                child_y = curr_y + span / 2.0
                assign_coords(child, depth + 1, child_y)
                curr_y += span + dy
        assign_coords(self.root_node, depth=0, center_y=0.0)
        
        # 5. Add Items & Connections to Scene
        def add_to_scene(node):
            # Create graphic node item
            item = MindMapNodeItem(node)
            item.setPos(node.x, node.y - node.height / 2.0) # GraphicsItem y is top-left
            self.scene_obj.addItem(item)
            
            # Hook up signals
            item.layerClicked.connect(self.layerSelected.emit)
            item.layerDoubleClicked.connect(self.layerDoubleClicked.emit)
            item.layoutChanged.connect(self.rebuild_and_draw)
            
            # Highlight selected node if it matches last selection
            if node.layer and node.layer.id() == self.selected_layer_id:
                item.setSelected(True)
                
            if not node.collapsed:
                for child in node.children:
                    child_item = add_to_scene(child)
                    # Draw linking curve
                    connection = MindMapConnectionItem(item, child_item)
                    self.scene_obj.addItem(connection)
            return item
            
        add_to_scene(self.root_node)
        
        # Adjust scene rect bounding area
        self.scene_obj.setSceneRect(self.scene_obj.itemsBoundingRect().adjusted(-50, -50, 50, 50))

    def _build_path_tree(self, layers, collapse_states):
        """Builds a neat path tree of layers, compressing linear subpaths."""
        project_path = QgsProject.instance().fileName()
        if project_path:
            project_name = os.path.basename(project_path)
        else:
            project_name = "未命名工程"
        root = MindMapNode(project_name)
        
        # Build raw hierarchy
        for layer in layers:
            if not layer:
                continue
            source = layer.source()
            phys_path, _ = split_qgis_source(source)
            actual_path = resolve_physical_path(phys_path)
            
            # Check if it is an online layer
            is_online = False
            source_lower = source.lower()
            if source_lower.startswith(('http://', 'https://')) or 'url=http' in source_lower or 'type=xyz' in source_lower:
                is_online = True
            else:
                try:
                    if hasattr(layer, 'dataProvider') and layer.dataProvider():
                        prov_name = layer.dataProvider().name().lower()
                        if prov_name in ['wms', 'wfs', 'wcs', 'vectortile', 'arcgisfeatureserver', 'arcgismapserver']:
                            is_online = True
                except Exception:
                    pass
            
            if is_online:
                continue
            
            # Check if it is a virtual layer
            is_virtual = False
            try:
                if hasattr(layer, 'dataProvider') and layer.dataProvider():
                    prov_name = layer.dataProvider().name().lower()
                    if prov_name == 'virtual':
                        is_virtual = True
            except Exception:
                pass
            
            # Check if it is a memory or temporary layer
            is_memory = False
            if not is_virtual:
                if not phys_path:
                    is_memory = True
                else:
                    try:
                        if hasattr(layer, 'dataProvider') and layer.dataProvider():
                            prov_name = layer.dataProvider().name().lower()
                            if prov_name == 'memory':
                                is_memory = True
                    except Exception:
                        pass
                    
            if is_virtual:
                # Put virtual layers under a Virtual folder
                self._insert_layer_to_tree(root, ["虚拟图层"], layer, "")
            elif is_memory:
                # Put memory/virtual layers under a Memory folder
                self._insert_layer_to_tree(root, ["内存与临时图层"], layer, "")
            elif not actual_path or not os.path.exists(actual_path):
                # This is a missing/invalid layer
                self._insert_layer_to_tree(root, ["无效图层"], layer, "")
            else:
                norm_path = os.path.normpath(os.path.abspath(actual_path))
                lower_path = norm_path.lower()
                is_container = False
                for ext in ['.zip', '.gpkg', '.gdb', '.tar', '.gz']:
                    if lower_path.endswith(ext):
                        is_container = True
                        break
                
                if is_container:
                    dir_path = norm_path
                else:
                    dir_path = os.path.dirname(norm_path)
                
                # Split path parts
                parts = []
                drive, tail = os.path.splitdrive(dir_path)
                if drive:
                    parts.append(drive + os.sep)
                
                for p in tail.split(os.sep):
                    if p:
                        parts.append(p)
                        
                self._insert_layer_to_tree(root, parts, layer, norm_path)
                
        # If root has only 1 child folder, make that child folder the root for a cleaner diagram!
        # (Avoids showing a single root node connected to a single drive node)
        while len(root.children) == 1 and root.children[0].is_physical_folder:
            root = root.children[0]
            
        # Clean up double nodes by compressing linear directory chains (e.g. data/vector)
        self._compress_tree_paths(root)
        
        # Truncate long folder paths to keep them compact (max 30 chars)
        def apply_truncation(n):
            if n.is_physical_folder:
                n.name = truncate_middle_path(n.name, max_len=30)
            for c in n.children:
                apply_truncation(c)
        apply_truncation(root)
        
        # Re-apply collapse states saved before refresh
        self._restore_collapse_states(root, collapse_states)
        
        return root

    def _insert_layer_to_tree(self, root_node, path_parts, layer, full_path):
        curr = root_node
        accumulated_path = ""
        for part in path_parts:
            # Construct folder path string for tracking collapse states
            accumulated_path = os.path.join(accumulated_path, part) if accumulated_path else part
            
            found = None
            for child in curr.children:
                if child.name == part and child.is_physical_folder:
                    found = child
                    break
            if not found:
                found = MindMapNode(part, is_physical_folder=True, path=accumulated_path)
                found.parent = curr
                curr.children.append(found)
            curr = found
            
        # Append layer leaf node
        leaf = MindMapNode(layer.name(), is_physical_folder=False, layer=layer, path=full_path)
        leaf.parent = curr
        curr.children.append(leaf)

    def _compress_tree_paths(self, node):
        """Recursively merges single-child directories for visual elegance."""
        for child in list(node.children):
            self._compress_tree_paths(child)
            
        # Merge if node has exactly one child directory and no layers (len == 1)
        if len(node.children) == 1 and node.children[0].is_physical_folder:
            child = node.children[0]
            
            is_container = False
            for n in [node, child]:
                name_lower = n.name.lower()
                if any(name_lower.endswith(ext) for ext in ['.zip', '.gpkg', '.gdb', '.tar', '.gz']):
                    is_container = True
                    break
            
            if not is_container:
                node.name = f"{node.name} / {child.name}"
                node.path = child.path
                node.children = child.children
                for gchild in node.children:
                    gchild.parent = node

    def _get_current_collapse_states(self):
        states = {}
        if not self.root_node:
            return states
        def collect(node):
            if node.is_physical_folder and node.path:
                states[node.path] = node.collapsed
            for child in node.children:
                collect(child)
        collect(self.root_node)
        return states

    def _restore_collapse_states(self, node, states):
        if node.is_physical_folder and node.path in states:
            node.collapsed = states[node.path]
        for child in node.children:
            self._restore_collapse_states(child, states)

    def zoom_to_fit(self):
        """Fits the entire mind map hierarchy inside the view viewport."""
        rect = self.scene_obj.itemsBoundingRect()
        if not rect.isEmpty():
            self.fitInView(rect.adjusted(-20, -20, 20, 20), Qt.KeepAspectRatio)

    def select_layer_node(self, layer_id):
        """Selects and focuses a layer item visually in the map view."""
        self.selected_layer_id = layer_id
        for item in self.scene_obj.items():
            if isinstance(item, MindMapNodeItem) and item.node.layer:
                if item.node.layer.id() == layer_id:
                    item.setSelected(True)
                    self.centerOn(item)
                else:
                    item.setSelected(False)

    def mousePressEvent(self, event):
        if event.button() == Qt.MiddleButton:
            self._pan_start = event.pos()
            self._panning = True
            self.setCursor(Qt.ClosedHandCursor)
            event.accept()
        else:
            super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if getattr(self, '_panning', False):
            delta = event.pos() - self._pan_start
            self.horizontalScrollBar().setValue(self.horizontalScrollBar().value() - delta.x())
            self.verticalScrollBar().setValue(self.verticalScrollBar().value() - delta.y())
            self._pan_start = event.pos()
            event.accept()
        else:
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MiddleButton and getattr(self, '_panning', False):
            self._panning = False
            self.unsetCursor()
            event.accept()
        else:
            super().mouseReleaseEvent(event)

    def start_dragging(self, item, start_scene_pos):
        self._drag_source_item = item
        self._drag_start_pos = start_scene_pos
        
        # Guard: also treat a sip-deleted C++ object as absent
        try:
            import sip
            if self._drag_line_item is not None and sip.isdeleted(self._drag_line_item):
                self._drag_line_item = None
        except Exception:
            pass

        if not self._drag_line_item:
            try:
                from PyQt5.QtWidgets import QGraphicsLineItem
                from PyQt5.QtGui import QPen, QColor
            except ImportError:
                class QGraphicsLineItem:
                    def __init__(self, *args): pass
                    def setPen(self, *args): pass
                    def setLine(self, *args): pass
                    def setZValue(self, val): pass
                    def show(self): pass
                    def hide(self): pass
                class QPen:
                    def __init__(self, *args): pass
                class QColor:
                    def __init__(self, *args): pass

            self._drag_line_item = QGraphicsLineItem()
            pen = QPen(QColor("#0d6efd"), 2.0, Qt.DashLine)
            self._drag_line_item.setPen(pen)
            self._drag_line_item.setZValue(100) # Draw on top
            self.scene_obj.addItem(self._drag_line_item)
            
        self._drag_line_item.setLine(start_scene_pos.x(), start_scene_pos.y(), start_scene_pos.x(), start_scene_pos.y())
        self._drag_line_item.show()

    def update_dragging(self, current_scene_pos):
        if self._drag_line_item and self._drag_start_pos:
            self._drag_line_item.setLine(
                self._drag_start_pos.x(), self._drag_start_pos.y(),
                current_scene_pos.x(), current_scene_pos.y()
            )
            
            target_item = self._find_folder_at(current_scene_pos)
            if hasattr(self, '_drag_target_item') and self._drag_target_item != target_item:
                if self._drag_target_item:
                    try:
                        self._drag_target_item.set_drag_highlight(False)
                    except Exception:
                        pass
            
            self._drag_target_item = target_item
            if target_item:
                try:
                    target_item.set_drag_highlight(True)
                except Exception:
                    pass

    def end_dragging(self, current_scene_pos):
        if self._drag_line_item:
            self._drag_line_item.hide()
            
        if hasattr(self, '_drag_target_item') and self._drag_target_item:
            try:
                self._drag_target_item.set_drag_highlight(False)
            except Exception:
                pass
            
        source_item = getattr(self, '_drag_source_item', None)
        target_item = getattr(self, '_drag_target_item', None)
        
        self._drag_source_item = None
        self._drag_target_item = None
        self._drag_start_pos = None
        
        if source_item and target_item and source_item.node.layer and not target_item.node.layer:
            layer_id = source_item.node.layer.id()
            target_folder_path = target_item.node.path
            self.layerRelocationRequested.emit(layer_id, target_folder_path)

    def _find_folder_at(self, scene_pos):
        items = self.scene_obj.items(scene_pos)
        for item in items:
            if isinstance(item, MindMapNodeItem) and not item.node.layer:
                return item
        return None

    def wheelEvent(self, event):
        # Dynamic zoom calculation based on angle delta
        zoom_factor = 1.15
        if event.angleDelta().y() < 0:
            zoom_factor = 1.0 / zoom_factor
        self.scale(zoom_factor, zoom_factor)
        event.accept()
