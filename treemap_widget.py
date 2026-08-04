import os

# Robust fallback imports for Qt
try:
    from qgis.PyQt.QtCore import Qt, QRectF, pyqtSignal as Signal, QPoint
    from qgis.PyQt.QtWidgets import QWidget, QToolTip
    from qgis.PyQt.QtGui import QPainter, QColor, QFont, QPen, QBrush, QLinearGradient
except ImportError:
    try:
        from qtpy.QtCore import Qt, QRectF, Signal, QPoint
        from qtpy.QtWidgets import QWidget, QToolTip
        from qtpy.QtGui import QPainter, QColor, QFont, QPen, QBrush, QLinearGradient
    except ImportError:
        try:
            from PySide2.QtCore import Qt, QRectF, Signal, QPoint
            from PySide2.QtWidgets import QWidget, QToolTip
            from PySide2.QtGui import QPainter, QColor, QFont, QPen, QBrush, QLinearGradient
        except ImportError:
            try:
                from PySide6.QtCore import Qt, QRectF, Signal, QPoint
                from PySide6.QtWidgets import QWidget, QToolTip
                from PySide6.QtGui import QPainter, QColor, QFont, QPen, QBrush, QLinearGradient
            except ImportError:
                # Basic mock for environment without PySide/PyQt (allows unit testing on CLI)
                class Qt:
                    AlignCenter = 132
                    TextWordWrap = 64
                    LeftButton = 1
                    RightButton = 2
                    ElideRight = 1
                    
                    class AlignmentFlag:
                        AlignCenter = 132
                        
                    class TextFlag:
                        TextWordWrap = 64
                        
                    class MouseButton:
                        LeftButton = 1
                        RightButton = 2
                        
                    class TextElideMode:
                        ElideRight = 1

                class QRectF:
                    def __init__(self, x=0.0, y=0.0, width=0.0, height=0.0):
                        self._x = float(x)
                        self._y = float(y)
                        self._w = float(width)
                        self._h = float(height)
                    def x(self): return self._x
                    def y(self): return self._y
                    def width(self): return self._w
                    def height(self): return self._h
                    def topLeft(self): return QPoint(self._x, self._y)
                    def bottomRight(self): return QPoint(self._x + self._w, self._y + self._h)
                    def contains(self, x, y):
                        return self._x <= x <= self._x + self._w and self._y <= y <= self._y + self._h
                    def adjusted(self, dx1, dy1, dx2, dy2):
                        return QRectF(self._x + dx1, self._y + dy1, self._w + dx2 - dx1, self._h + dy2 - dy1)
                        
                class Signal:
                    def __init__(self, *types):
                        self.types = types
                        self._listeners = []
                    def __get__(self, instance, owner):
                        return self
                    def connect(self, slot):
                        self._listeners.append(slot)
                    def emit(self, *args):
                        for listener in self._listeners:
                            listener(*args)
                            
                class QPoint:
                    def __init__(self, x=0, y=0):
                        self._x = x
                        self._y = y
                    def x(self): return self._x
                    def y(self): return self._y
                    
                class QWidget:
                    def __init__(self, parent=None):
                        self._parent = parent
                        self._width = 640
                        self._height = 480
                    def setMouseTracking(self, tracking):
                        pass
                    def width(self):
                        return self._width
                    def height(self):
                        return self._height
                    def rect(self):
                        return QRectF(0, 0, self._width, self._height)
                    def update(self):
                        pass
                    def resize(self, w, h):
                        self._width = w
                        self._height = h
                        
                class QToolTip:
                    @classmethod
                    def showText(cls, *args):
                        pass
                    @classmethod
                    def hideText(cls):
                        pass
                        
                class QPainter:
                    Antialiasing = 1
                    def __init__(self, *args):
                        pass
                    def setRenderHint(self, *args):
                        pass
                    def drawText(self, *args):
                        pass
                    def setPen(self, *args):
                        pass
                    def setBrush(self, *args):
                        pass
                    def drawRect(self, *args):
                        pass
                    def setFont(self, *args):
                        pass
                        
                class QColor:
                    def __init__(self, *args):
                        pass
                    def lighter(self, *args):
                        return self
                    def darker(self, *args):
                        return self
                        
                class QFont:
                    def __init__(self, *args):
                        pass
                        
                class QPen:
                    def __init__(self, *args):
                        pass
                        
                class QBrush:
                    def __init__(self, *args):
                        pass
                        
                class QLinearGradient:
                    def __init__(self, *args):
                        pass
                    def setColorAt(self, *args):
                        pass

# Robust fallback imports for QGIS
try:
    from qgis.core import QgsMapLayer
except ImportError:
    class QgsMapLayer:
        def __init__(self, layer_id="", name="", source_path=""):
            self._id = layer_id
            self._name = name
            self._source = source_path
        def id(self): return self._id
        def name(self): return self._name
        def source(self): return self._source
        def isValid(self): return True

# Robust imports for file_operations helper functions
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
            phys_path = parts[0]
            q_params = '|' + parts[1] if len(parts) == 2 else ""
            if '?' in phys_path:
                sub_parts = phys_path.split('?', 1)
                phys_path = sub_parts[0]
                q_params = '?' + sub_parts[1] + q_params
            return phys_path.replace('\\', '/'), q_params
        
        def get_associated_files(file_path):
            phys_path, _ = split_qgis_source(file_path)
            return [phys_path] if (phys_path and os.path.exists(phys_path)) else []

        def format_size(size_in_bytes):
            """Formats the size in bytes to a human-readable string."""
            if size_in_bytes <= 0:
                return "-"
            val = float(size_in_bytes)
            for unit in ['B', 'KB', 'MB', 'GB']:
                if val < 1024.0:
                    return f"{val:.2f} {unit}"
                val /= 1024.0
            return f"{val:.2f} TB"
try:
    from .translation import tr
except ImportError:
    try:
        from translation import tr
    except ImportError:
        def tr(text, disambiguation=None): return text


class TreeMapNode:
    """Class representing a node in the treemap, binding a QGIS layer and its physical layout rectangle."""
    def __init__(self, layer, size, path):
        self.layer = layer
        self.size = size  # File size in bytes
        self.path = path
        self.rect = QRectF()  # Assigned coordinate box during layout


def get_text_width(font_metrics, text):
    try:
        return font_metrics.horizontalAdvance(text)
    except AttributeError:
        try:
            return font_metrics.width(text)
        except AttributeError:
            return len(text) * 8


def elide_text(font_metrics, text, mode, width):
    try:
        return font_metrics.elidedText(text, mode, int(width))
    except AttributeError:
        char_w = 8
        max_chars = max(0, int(width / char_w))
        if len(text) <= max_chars:
            return text
        if max_chars <= 3:
            return "..."[:max_chars]
        return text[:max_chars - 3] + "..."


def format_treemap_text(name, size_str, w, h, fm):
    try:
        lh = fm.lineSpacing()
    except AttributeError:
        try:
            lh = fm.height()
        except AttributeError:
            lh = 15
        
    max_lines = int(h // lh)
    if max_lines <= 0:
        return []
        
    elide_mode = getattr(Qt.TextElideMode, 'ElideRight', getattr(Qt, 'ElideRight', 1))
    
    if max_lines == 1:
        return [elide_text(fm, name, elide_mode, w)]
        
    max_name_lines = max_lines - 1
    
    wrapped_lines = []
    current_line = ""
    for char in name:
        test_line = current_line + char
        if get_text_width(fm, test_line) <= w:
            current_line = test_line
        else:
            if current_line:
                wrapped_lines.append(current_line)
                current_line = char
            else:
                wrapped_lines.append(char)
                current_line = ""
    if current_line:
        wrapped_lines.append(current_line)
        
    if len(wrapped_lines) <= max_name_lines:
        name_lines = wrapped_lines
    else:
        name_lines = wrapped_lines[:max_name_lines - 1]
        remaining_text = "".join(wrapped_lines[max_name_lines - 1:])
        name_lines.append(elide_text(fm, remaining_text, elide_mode, w))
        
    return name_lines + [size_str]

class TreeMapWidget(QWidget):
    layerSelected = Signal(str)  # Emits layer ID
    contextMenuTriggered = Signal(object, QPoint)  # Emits (TreeMapNode, global_pos)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMouseTracking(True)
        self.nodes = []
        self.hovered_node = None

        # Performance cache to avoid allocations inside paintEvent
        self.font = QFont("Outfit", 9)
        self.colors = [
            QColor(74, 144, 226),  # Soft Slate Blue
            QColor(80, 200, 120),  # Emerald Green
            QColor(245, 166, 35),  # Soft Gold
            QColor(208, 2, 27),    # Rich Crimson
            QColor(144, 19, 254),  # Deep Violet
            QColor(77, 208, 225),  # Soft Teal
            QColor(240, 98, 146),  # Soft Pink
        ]
        self.text_color = QColor(255, 255, 255)
        self.hover_border_color = QColor(255, 255, 255, 220)
        self.normal_border_color = QColor(255, 255, 255, 90)
        self.hover_pen = QPen(self.hover_border_color, 2)
        self.normal_pen = QPen(self.normal_border_color, 1)

    def set_layers(self, layers):
        """Calculates size, filters invalid layers, sorts descending, and updates treemap layout."""
        self.nodes = []
        for layer in layers:
            if not layer or not layer.isValid():
                continue
            src = layer.source()
            phys_path, _ = split_qgis_source(src)
            actual_path = resolve_physical_path(phys_path)
            if actual_path and os.path.exists(actual_path):
                try:
                    size = sum(os.path.getsize(f) for f in get_associated_files(phys_path) if os.path.exists(f))
                except Exception:
                    size = 0
                if size > 0:
                    self.nodes.append(TreeMapNode(layer, size, phys_path))
        # Sort nodes descending by size
        self.nodes.sort(key=lambda x: x.size, reverse=True)
        self.update_layout()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.update_layout()

    def update_layout(self):
        """Initiates layout calculation inside the current widget geometry."""
        if not self.nodes:
            self.update()
            return
        
        total_size = sum(n.size for n in self.nodes)
        if total_size == 0 or self.width() <= 0 or self.height() <= 0:
            return

        rect = QRectF(0.0, 0.0, float(self.width()), float(self.height()))
        self._squarify(self.nodes, [], rect, total_size)
        self.update()

    def _squarify(self, children, row, rect, total_size):
        """Recursive implementation of the Squarified Treemap layout algorithm."""
        if not children:
            if row:
                self._layout_row(row, rect, total_size)
            return
        
        c = children[0]
        row_with_c = row + [c]
        
        worst_row = self._worst_aspect_ratio(row, rect, total_size)
        worst_row_with_c = self._worst_aspect_ratio(row_with_c, rect, total_size)
        
        if worst_row >= worst_row_with_c:
            self._squarify(children[1:], row_with_c, rect, total_size)
        else:
            new_rect = self._layout_row(row, rect, total_size)
            self._squarify(children, [], new_rect, total_size)

    def _worst_aspect_ratio(self, row, rect, total_size):
        """Calculates worst aspect ratio score of layout rectangles in a row."""
        if not row:
            return float('inf')
        row_size = sum(n.size for n in row)
        if row_size == 0:
            return float('inf')
        
        side = min(rect.width(), rect.height())
        if side == 0:
            return float('inf')
            
        scale = (self.width() * self.height()) / total_size if total_size > 0 else 0
        
        row_area = row_size * scale
        min_area = min(n.size for n in row) * scale
        max_area = max(n.size for n in row) * scale
        
        if row_area == 0 or min_area == 0:
            return float('inf')
            
        r1 = (side ** 2 * max_area) / (row_area ** 2)
        r2 = (row_area ** 2) / (side ** 2 * min_area)
        return max(r1, r2)

    def _layout_row(self, row, rect, total_size):
        """Positions layout rectangles in row along the shorter edge of the remaining rect."""
        row_size = sum(n.size for n in row)
        scale = (self.width() * self.height()) / total_size if total_size > 0 else 0
        
        side = min(rect.width(), rect.height())
        thickness = (row_size * scale) / side if side > 0 else 0
        
        horizontal = rect.width() >= rect.height()
        x = rect.x()
        y = rect.y()
        
        for node in row:
            area = node.size * scale
            sub_thickness = area / thickness if thickness > 0 else 0
            if horizontal:
                node.rect = QRectF(x, y, thickness, sub_thickness)
                y += sub_thickness
            else:
                node.rect = QRectF(x, y, sub_thickness, thickness)
                x += sub_thickness
                
        if horizontal:
            return QRectF(rect.x() + thickness, rect.y(), max(0.0, rect.width() - thickness), rect.height())
        else:
            return QRectF(rect.x(), rect.y() + thickness, rect.width(), max(0.0, rect.height() - thickness))

    def paintEvent(self, event):
        """Draws the treemap nodes using QPainter."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        if not self.nodes:
            painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, tr("当前工程未加载包含有效物理文件的图层。"))
            return
        
        painter.setFont(self.font)
        
        for idx, node in enumerate(self.nodes):
            r = node.rect
            if r.width() < 5 or r.height() < 5:
                continue
            
            try:
                from .layer_model import get_layer_format, get_format_color_dict, is_layer_effectively_visible
            except ImportError:
                try:
                    from layer_model import get_layer_format, get_format_color_dict, is_layer_effectively_visible
                except ImportError:
                    def get_layer_format(l): return "other"
                    def get_format_color_dict(f): return {"treemap": "#9e9e9e"}
                    def is_layer_effectively_visible(l): return True
                    
            fmt = get_layer_format(node.layer)
            colors_dict = get_format_color_dict(fmt)
            base_color = QColor(colors_dict["treemap"])
            is_vis = is_layer_effectively_visible(node.layer)
            if not is_vis:
                base_color = base_color.darker(140)
            if node == self.hovered_node:
                base_color = base_color.lighter(120)
                pen = self.hover_pen
            else:
                pen = self.normal_pen
                
            grad = QLinearGradient(r.topLeft(), r.bottomRight())
            grad.setColorAt(0.0, base_color)
            grad.setColorAt(1.0, base_color.darker(115))
            
            painter.setPen(pen)
            painter.setBrush(QBrush(grad))
            painter.drawRect(r)
            
            # Top-left invisible icon overlay if layer is not effectively visible
            if not is_vis and r.width() >= 18 and r.height() >= 18:
                plugin_dir = os.path.dirname(os.path.abspath(__file__))
                hide_icon_path = os.path.join(plugin_dir, "icons_component", "Component_layer_hide.svg")
                if os.path.exists(hide_icon_path):
                    try:
                        from qgis.PyQt.QtGui import QIcon
                    except ImportError:
                        try:
                            from qtpy.QtGui import QIcon
                        except ImportError:
                            QIcon = None
                    if QIcon and hasattr(QIcon, 'pixmap'):
                        icon = QIcon(hide_icon_path)
                        px = icon.pixmap(18, 18)
                        if px and hasattr(px, 'isNull') and not px.isNull() and hasattr(painter, 'drawPixmap'):
                            painter.drawPixmap(int(r.x() + 6), int(r.y() + 6), px)
            
            pad_x = 4.0 if r.width() > 40 else 2.0
            pad_y = 4.0 if r.height() > 30 else 2.0
            w = int(r.width() - 2 * pad_x)
            h = int(r.height() - 2 * pad_y)
            
            fm = painter.fontMetrics()
            try:
                lh = fm.lineSpacing()
            except AttributeError:
                try:
                    lh = fm.height()
                except AttributeError:
                    lh = 15
                
            if w > 15 and h >= lh:
                painter.setPen(self.text_color)
                size_str = format_size(node.size)
                lines = format_treemap_text(node.layer.name(), size_str, w, h, fm)
                if lines:
                    text = "\n".join(lines)
                    painter.drawText(r.adjusted(pad_x, pad_y, -pad_x, -pad_y), Qt.AlignmentFlag.AlignCenter, text)

    def leaveEvent(self, event):
        if self.hovered_node:
            self.hovered_node = None
            QToolTip.hideText()
            self.update()

    def mouseMoveEvent(self, event):
        """Tracks cursor position to update hovered node and show tooltips."""
        pos = event.pos()
        found = None
        for node in self.nodes:
            if node.rect.contains(pos.x(), pos.y()):
                found = node
                break
                
        if found != self.hovered_node:
            self.hovered_node = found
            self.update()
            if found:
                try:
                    global_pos = event.globalPos()
                except AttributeError:
                    try:
                        global_pos = event.globalPosition().toPoint()
                    except AttributeError:
                        global_pos = QPoint(0, 0)
                size_str = format_size(found.size)
                QToolTip.showText(global_pos, f"{found.layer.name()}\n" + tr("大小: {}").format(size_str) + "\n" + tr("路径: {}").format(found.path), self)
            else:
                QToolTip.hideText()

    def mouseDoubleClickEvent(self, event):
        """Emits layerSelected signal on double-click with left button."""
        if self.hovered_node and event.button() == Qt.MouseButton.LeftButton:
            self.layerSelected.emit(self.hovered_node.layer.id())

    def mouseReleaseEvent(self, event):
        """Emits contextMenuTriggered signal on right-click."""
        if event.button() == Qt.MouseButton.RightButton and self.hovered_node:
            try:
                global_pos = event.globalPos()
            except AttributeError:
                try:
                    global_pos = event.globalPosition().toPoint()
                except AttributeError:
                    global_pos = QPoint(0, 0)
            self.contextMenuTriggered.emit(self.hovered_node, global_pos)
