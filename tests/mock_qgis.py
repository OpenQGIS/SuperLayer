"""Unified mock implementation of QGIS and Qt modules for headless testing.

This module is used strictly by the test suite to allow test discovery and unit tests
to run in environments without QGIS or Qt installed (e.g. CI runners).
"""

import sys
import types
import os

# --- Core Mock Classes ---

class _MockSignal:
    def __init__(self, *args, **kwargs):
        self._slots = []

    def connect(self, slot):
        if slot not in self._slots:
            self._slots.append(slot)

    def disconnect(self, slot=None):
        if slot is None:
            self._slots = []
        elif slot in self._slots:
            self._slots.remove(slot)

    def emit(self, *args, **kwargs):
        for slot in list(self._slots):
            try:
                slot(*args, **kwargs)
            except TypeError:
                try:
                    slot(*args)
                except TypeError:
                    slot()


class Signal(_MockSignal):
    pass


pyqtSignal = Signal


class Qt:
    LeftDockWidgetArea = 1
    RightDockWidgetArea = 2
    CustomContextMenu = 3
    UserRole = 32
    Horizontal = 1
    Vertical = 2
    AlignLeft = 1
    AlignRight = 2
    AlignHCenter = 4
    AlignVCenter = 128
    AlignCenter = 132
    ToolButtonTextBesideIcon = 2
    ScrollBarAlwaysOff = 0
    ScrollBarAlwaysOn = 1
    KeepAspectRatio = 1
    NoPen = 0
    NoBrush = 0
    ItemIsSelectable = 1
    ItemIsEditable = 2
    ItemIsEnabled = 4
    ItemIsUserCheckable = 8
    ItemIsFocusable = 16
    ItemIsDragEnabled = 32
    ItemIsDropEnabled = 64
    EditRole = 2
    DisplayRole = 0
    ToolTipRole = 3
    DecorationRole = 1
    yellow = 12
    NoItemFlags = 0
    WaitCursor = 3
    SolidLine = 1
    LeftButton = 1
    RightButton = 2
    MiddleButton = 4
    ElideRight = 0
    ElideLeft = 1
    ElideMiddle = 2
    ElideNone = 3
    TextWordWrap = 64
    TopRightCorner = 1
    TopLeftCorner = 0

    class CheckState:
        Unchecked = 0
        PartiallyChecked = 1
        Checked = 2

    class AlignmentFlag:
        AlignLeft = 1
        AlignRight = 2
        AlignHCenter = 4
        AlignVCenter = 128
        AlignCenter = 132

    class ToolButtonStyle:
        ToolButtonTextBesideIcon = 2

    class ContextMenuPolicy:
        CustomContextMenu = 3

    class ItemDataRole:
        UserRole = 32
        DisplayRole = 0
        ToolTipRole = 3
        DecorationRole = 1
        EditRole = 2

    class ItemFlag:
        NoItemFlags = 0
        ItemIsSelectable = 1
        ItemIsEditable = 2
        ItemIsEnabled = 4
        ItemIsUserCheckable = 8
        ItemIsDragEnabled = 32
        ItemIsDropEnabled = 64

    class WindowType:
        WindowMinimizeButtonHint = 1
        WindowMaximizeButtonHint = 2

    class MouseButton:
        LeftButton = 1
        RightButton = 2
        MiddleButton = 4

    class DropAction:
        MoveAction = 2
        CopyAction = 1

    class KeyboardModifier:
        AltModifier = 1
        ControlModifier = 2
        ShiftModifier = 4

    class Orientation:
        Horizontal = 1
        Vertical = 2

    class CursorShape:
        ClosedHandCursor = 1
        OpenHandCursor = 2
        PointingHandCursor = 3
        WaitCursor = 4

    class GlobalColor:
        yellow = 12
        transparent = 0

    class Corner:
        TopRightCorner = 1
        TopLeftCorner = 0

    class ScrollBarPolicy:
        ScrollBarAlwaysOff = 0
        ScrollBarAlwaysOn = 1

    class AspectRatioMode:
        KeepAspectRatio = 1

    class PenStyle:
        NoPen = 0
        SolidLine = 1
        DashLine = 2

    class TextElideMode:
        ElideRight = 0
        ElideLeft = 1
        ElideMiddle = 2
        ElideNone = 3

    class ClipOperation:
        IntersectClip = 1

    class TextFlag:
        TextWordWrap = 1


class QSize:
    def __init__(self, w=0, h=0):
        self._w = w
        self._h = h

    def width(self):
        return self._w

    def height(self):
        return self._h


class QPoint:
    def __init__(self, x=0, y=0):
        self._x = x
        self._y = y

    def x(self):
        return self._x

    def y(self):
        return self._y

    def __sub__(self, other):
        if hasattr(other, 'x') and hasattr(other, 'y'):
            return QPoint(self._x - other.x(), self._y - other.y())
        return self

    def manhattanLength(self):
        return abs(self._x) + abs(self._y)


class QPointF:
    def __init__(self, x=0.0, y=0.0):
        self._x = float(x)
        self._y = float(y)

    def x(self):
        return self._x

    def y(self):
        return self._y

    def __sub__(self, other):
        if hasattr(other, 'x') and hasattr(other, 'y'):
            return QPointF(self._x - other.x(), self._y - other.y())
        return self

    def manhattanLength(self):
        return abs(self._x) + abs(self._y)


class QRect:
    def __init__(self, x=0, y=0, w=0, h=0):
        self._x = int(x)
        self._y = int(y)
        self._w = int(w)
        self._h = int(h)

    def x(self):
        return self._x

    def y(self):
        return self._y

    def width(self):
        return self._w

    def height(self):
        return self._h


class QRectF:
    def __init__(self, x=0.0, y=0.0, w=0.0, h=0.0):
        self._x = float(x)
        self._y = float(y)
        self._w = float(w)
        self._h = float(h)

    def x(self):
        return self._x

    def y(self):
        return self._y

    def width(self):
        return self._w

    def height(self):
        return self._h

    def topLeft(self):
        return QPoint(self._x, self._y)

    def bottomRight(self):
        return QPoint(self._x + self._w, self._y + self._h)

    def contains(self, *args):
        if len(args) == 1:
            pt = args[0]
            if hasattr(pt, 'x') and hasattr(pt, 'y'):
                return self._x <= pt.x() <= self._x + self._w and self._y <= pt.y() <= self._y + self._h
            return True
        elif len(args) == 2:
            x, y = args
            return self._x <= x <= self._x + self._w and self._y <= y <= self._y + self._h
        return True

    def united(self, other):
        return self

    def adjusted(self, dx1, dy1, dx2, dy2):
        return QRectF(self._x + dx1, self._y + dy1, self._w + dx2 - dx1, self._h + dy2 - dy1)

    def toRect(self):
        return QRect(self._x, self._y, self._w, self._h)


class QLineF:
    def __init__(self, *args):
        pass


class QObject:
    def __init__(self, parent=None):
        self._parent = parent


class QTimer(QObject):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.timeout = _MockSignal()

    def setSingleShot(self, val):
        pass

    def setInterval(self, val):
        pass

    def start(self, *args):
        pass

    def stop(self):
        pass

    def isActive(self):
        return False

    @staticmethod
    def singleShot(msecs, slot):
        pass


class QModelIndex:
    def __init__(self, ptr=None):
        self._ptr = ptr

    def isValid(self):
        return self._ptr is not None

    def row(self):
        return 0

    def column(self):
        return 0

    def internalPointer(self):
        return self._ptr


QPersistentModelIndex = QModelIndex


class QItemSelectionModel:
    def __init__(self, model=None):
        self._model = model
        self._selected = []
        self.selectionChanged = _MockSignal()

    def selectedIndexes(self):
        return self._selected

    def selectedRows(self):
        return self._selected

    def isSelected(self, index):
        return index in self._selected

    def select(self, index, flags=None):
        if index not in self._selected:
            self._selected.append(index)

    def clearSelection(self):
        self._selected = []


class QCoreApplication:
    @staticmethod
    def instance():
        class _App:
            def processEvents(self): pass
        return _App()

    @staticmethod
    def installTranslator(*args):
        pass

    @staticmethod
    def removeTranslator(*args):
        pass

    @staticmethod
    def translate(context, text, *args):
        return text

    @staticmethod
    def processEvents():
        pass


class QSettings:
    def __init__(self, *args):
        self._data = {}

    def value(self, key, default=None):
        return self._data.get(key, default)

    def setValue(self, key, value):
        self._data[key] = value

    def remove(self, key):
        self._data.pop(key, None)


class QTranslator:
    def __init__(self, *args):
        pass

    def load(self, *args, **kwargs):
        return False


class QLocale:
    class system:
        @staticmethod
        def name():
            return "en"


# --- GUI / Painting Mocks ---

class QColor:
    def __init__(self, *args):
        if len(args) == 1:
            self._color_val = args[0]
        else:
            self._color_val = args

    def name(self):
        return str(self._color_val) if isinstance(self._color_val, str) else "#ffffff"

    def lighter(self, *args):
        return self

    def darker(self, *args):
        return self


class QFont:
    def __init__(self, *args):
        pass

    def setBold(self, val):
        pass

    def setPointSize(self, size):
        pass


class QFontMetrics:
    def __init__(self, font=None):
        pass

    def width(self, text):
        return len(str(text)) * 7

    def horizontalAdvance(self, text):
        return len(str(text)) * 7

    def height(self):
        return 14

    def elidedText(self, text, mode, width):
        return str(text)


class QPen:
    def __init__(self, *args):
        pass

    def setColor(self, c):
        pass

    def setWidth(self, w):
        pass


class QBrush:
    def __init__(self, color=None):
        self._color = color

    def color(self):
        return self._color

    def setColor(self, c):
        self._color = c


class QLinearGradient:
    def __init__(self, *args):
        pass

    def setColorAt(self, pos, color):
        pass


class QCursor:
    @classmethod
    def pos(cls):
        return QPointF(0.0, 0.0)


class QTextCursor:
    class MoveOperation:
        End = 1

    class MoveMode:
        MoveAnchor = 0

    def movePosition(self, *args):
        pass


class QPainterPath:
    def moveTo(self, *args):
        pass

    def lineTo(self, *args):
        pass

    def cubicTo(self, *args):
        pass

    def addRoundedRect(self, *args):
        pass


class QPixmap:
    def __init__(self, *args):
        self._w = 16
        self._h = 16

    def isNull(self):
        return False

    def fill(self, color):
        pass

    def width(self):
        return self._w

    def height(self):
        return self._h


class QIcon:
    def __init__(self, *args):
        self._path = args[0] if args else ""

    def pixmap(self, *args):
        return QPixmap()

    def isNull(self):
        return False

    def paint(self, *args):
        pass


class QPainter:
    Antialiasing = 1
    SmoothPixmapTransform = 2

    class RenderHint:
        Antialiasing = 1
        SmoothPixmapTransform = 2

    def __init__(self, *args):
        pass

    def begin(self, *args):
        return True

    def end(self):
        return True

    def setPen(self, *args):
        pass

    def setBrush(self, *args):
        pass

    def setFont(self, *args):
        pass

    def setRenderHint(self, *args):
        pass

    def drawRect(self, *args):
        pass

    def drawRoundedRect(self, *args):
        pass

    def drawText(self, *args):
        pass

    def drawPath(self, *args):
        pass

    def drawPixmap(self, *args):
        pass

    def fillRect(self, *args):
        pass

    def save(self):
        pass

    def restore(self):
        pass


class QAction(QObject):
    def __init__(self, *args, **kwargs):
        super().__init__(kwargs.get("parent", None))
        self._icon = kwargs.get("icon", None)
        self._text = kwargs.get("text", "")
        self.parent = kwargs.get("parent", None)

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
        self._enabled = True
        self._visible = True
        self._tooltip = ""
        self.triggered = _MockSignal()

    def setCheckable(self, val):
        self._checkable = bool(val)

    def isCheckable(self):
        return self._checkable

    def setChecked(self, val):
        self._checked = bool(val)

    def isChecked(self):
        return self._checked

    def setText(self, text):
        self._text = text

    def text(self):
        return self._text

    def setIcon(self, icon):
        self._icon = icon

    def icon(self):
        return self._icon

    def setEnabled(self, val):
        self._enabled = bool(val)

    def isEnabled(self):
        return self._enabled

    def setVisible(self, val):
        self._visible = bool(val)

    def isVisible(self):
        return self._visible

    def setToolTip(self, text):
        self._tooltip = text


class QActionGroup(QObject):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._actions = []
        self._exclusive = True

    def addAction(self, action):
        self._actions.append(action)
        return action

    def setExclusive(self, val):
        self._exclusive = val


class QStandardItem:
    def __init__(self, text=""):
        self._text = str(text)
        self._data = {
            0: str(text),
            2: str(text),
            Qt.ItemDataRole.DisplayRole: str(text),
            Qt.ItemDataRole.EditRole: str(text)
        }
        self._children = []
        self._parent = None
        self._icon = None
        self._checkable = False
        self._check_state = Qt.CheckState.Unchecked
        self._flags = 33
        self._tooltip = ""

    def setText(self, text):
        self._text = str(text)
        self._data[0] = str(text)
        self._data[2] = str(text)
        self._data[Qt.ItemDataRole.DisplayRole] = str(text)
        self._data[Qt.ItemDataRole.EditRole] = str(text)

    def text(self):
        return self._text

    def setData(self, val, role=Qt.ItemDataRole.UserRole):
        self._data[role] = val
        if role == Qt.ItemDataRole.EditRole or role == 2 or role == 0 or role == Qt.ItemDataRole.DisplayRole:
            self._text = str(val) if val is not None else ""

    def data(self, role=Qt.ItemDataRole.UserRole):
        if role in self._data:
            return self._data[role]
        if role == 0 or role == 2 or role == Qt.ItemDataRole.DisplayRole or role == Qt.ItemDataRole.EditRole:
            return self._text
        return None

    def setIcon(self, icon):
        self._icon = icon

    def icon(self):
        return self._icon

    def setToolTip(self, tip):
        self._tooltip = tip

    def toolTip(self):
        return self._tooltip

    def setFlags(self, flags):
        self._flags = flags

    def flags(self):
        return self._flags

    def setCheckable(self, checkable):
        self._checkable = bool(checkable)

    def isCheckable(self):
        return self._checkable

    def setCheckState(self, state):
        self._check_state = state

    def checkState(self):
        return self._check_state

    def appendRow(self, items):
        if isinstance(items, list):
            self._children.append(items)
        else:
            self._children.append([items])

    def rowCount(self):
        return len(self._children)

    def child(self, row, col=0):
        if 0 <= row < len(self._children):
            row_items = self._children[row]
            if 0 <= col < len(row_items):
                return row_items[col]
        return None

    def parent(self):
        return self._parent

    def row(self):
        if self._parent and hasattr(self._parent, '_children'):
            for idx, r in enumerate(self._parent._children):
                if self in r:
                    return idx
        return 0


class QStandardItemModel(QStandardItem):
    def __init__(self, parent=None):
        super().__init__("")
        self._headers = []
        self._root_item = self
        self.itemChanged = _MockSignal()
        self._sort_role = 0

    def clear(self):
        self._children = []
        self._headers = []

    def setHorizontalHeaderLabels(self, labels):
        self._headers = labels

    def setSortRole(self, role):
        self._sort_role = role

    def invisibleRootItem(self):
        return self._root_item

    def item(self, row, col=0):
        return self.child(row, col)

    def itemFromIndex(self, idx):
        if hasattr(idx, 'internalPointer') and idx.internalPointer():
            return idx.internalPointer()
        return None

    def indexFromItem(self, item):
        return QModelIndex(item)


# --- Widgets Mocks ---

class QWidget:
    def __init__(self, parent=None):
        self._parent = parent
        self._layout = None
        self._enabled = True
        self._visible = True
        self._style_sheet = ""
        self._object_name = ""
        self._tooltip = ""
        self._width = 640
        self._height = 480
        self._mouse_tracking = False

    def setLayout(self, layout):
        self._layout = layout

    def layout(self):
        return self._layout

    def setStyleSheet(self, style):
        self._style_sheet = style

    def styleSheet(self):
        return self._style_sheet

    def setObjectName(self, name):
        self._object_name = name

    def objectName(self):
        return self._object_name

    def setSizePolicy(self, *args):
        pass

    def setToolTip(self, tip):
        self._tooltip = tip

    def toolTip(self):
        return self._tooltip

    def setEnabled(self, val):
        self._enabled = bool(val)

    def isEnabled(self):
        return self._enabled

    def show(self):
        self._visible = True

    def hide(self):
        self._visible = False

    def isVisible(self):
        return self._visible

    def setVisible(self, val):
        self._visible = bool(val)

    def update(self):
        pass

    def repaint(self):
        pass

    def resize(self, w, h):
        self._width = w
        self._height = h

    def mapToGlobal(self, pos):
        return pos

    def width(self):
        return self._width

    def height(self):
        return self._height

    def rect(self):
        return QRectF(0, 0, self._width, self._height)

    def setMouseTracking(self, val):
        self._mouse_tracking = bool(val)

    def hasMouseTracking(self):
        return self._mouse_tracking

    def setMinimumWidth(self, w): pass
    def setMaximumWidth(self, w): pass
    def setMinimumHeight(self, h): pass
    def setMaximumHeight(self, h): pass
    def setFixedWidth(self, w): pass
    def setFixedHeight(self, h): pass
    def setFixedSize(self, *args): pass
    def setMinimumSize(self, *args): pass
    def setMaximumSize(self, *args): pass
    def close(self): return True
    def raise_(self): pass
    def activateWindow(self): pass
    def isMinimized(self): return False
    def showNormal(self): pass
    def deleteLater(self): pass


class QLabel(QWidget):
    def __init__(self, text="", parent=None):
        super().__init__(parent)
        self._text = str(text)

    def setText(self, text):
        self._text = str(text)

    def text(self):
        return self._text

    def setWordWrap(self, val):
        pass


class QPushButton(QWidget):
    def __init__(self, text="", parent=None):
        super().__init__(parent)
        self._text = str(text)
        self.clicked = _MockSignal()

    def setText(self, text):
        self._text = str(text)

    def text(self):
        return self._text

    def setIcon(self, icon): pass
    def setIconSize(self, size): pass


class QToolButton(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.toggled = _MockSignal()
        self.clicked = _MockSignal()
        self._checkable = False
        self._checked = False
        self._icon = None
        self._icon_size = None
        self._text = ""

    def setCheckable(self, val):
        self._checkable = bool(val)

    def isCheckable(self):
        return self._checkable

    def setChecked(self, val):
        self._checked = bool(val)
        self.toggled.emit(val)

    def isChecked(self):
        return self._checked

    def setIcon(self, icon):
        self._icon = icon

    def icon(self):
        return self._icon

    def setIconSize(self, size):
        self._icon_size = size

    def setText(self, text):
        self._text = text

    def text(self):
        return self._text

    def setMenu(self, menu): pass
    def setPopupMode(self, mode): pass


class QLineEdit(QWidget):
    def __init__(self, text="", parent=None):
        super().__init__(parent)
        self._text = str(text)
        self.textChanged = _MockSignal()

    def setText(self, text):
        self._text = str(text)
        self.textChanged.emit(self._text)

    def text(self):
        return self._text

    def clear(self):
        self.setText("")

    def setPlaceholderText(self, text):
        pass


class QTextEdit(QWidget):
    def __init__(self, text="", parent=None):
        super().__init__(parent)
        self._text = str(text)

    def setPlainText(self, text):
        self._text = str(text)

    def toPlainText(self):
        return self._text

    def textCursor(self):
        return QTextCursor()

    def setTextCursor(self, cursor):
        pass

    def clear(self):
        self._text = ""

    def append(self, text):
        self._text += str(text) + "\n"

    def setReadOnly(self, r):
        pass

    def ensureCursorVisible(self):
        pass


class QComboBox(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._items = []
        self._current_index = 0
        self.currentIndexChanged = _MockSignal()

    def addItem(self, text, data=None):
        self._items.append((str(text), data))

    def addItems(self, items):
        for item in items:
            self.addItem(item)

    def count(self):
        return len(self._items)

    def currentText(self):
        if 0 <= self._current_index < len(self._items):
            return self._items[self._current_index][0]
        return ""

    def currentData(self):
        if 0 <= self._current_index < len(self._items):
            return self._items[self._current_index][1]
        return None

    def currentIndex(self):
        return self._current_index

    def setCurrentIndex(self, idx):
        self._current_index = idx
        self.currentIndexChanged.emit(idx)

    def setCurrentText(self, text):
        idx = self.findText(text)
        if idx >= 0:
            self.setCurrentIndex(idx)

    def findText(self, text):
        for idx, item in enumerate(self._items):
            if item[0] == text:
                return idx
        return -1

    def clear(self):
        self._items = []
        self._current_index = 0


class QCheckBox(QWidget):
    def __init__(self, text="", parent=None):
        super().__init__(parent)
        self._text = str(text)
        self._checked = False
        self.stateChanged = _MockSignal()

    def setChecked(self, val):
        self._checked = bool(val)
        self.stateChanged.emit(val)

    def isChecked(self):
        return self._checked

    def setText(self, text):
        self._text = str(text)

    def text(self):
        return self._text


class QListWidgetItem:
    def __init__(self, text=""):
        self._text = str(text)
        self._data = {}
        self._flags = 33
        self._check_state = Qt.CheckState.Unchecked

    def text(self):
        return self._text

    def setText(self, t):
        self._text = str(t)

    def setData(self, role, val):
        self._data[role] = val

    def data(self, role):
        return self._data.get(role, None)

    def setFlags(self, flags):
        self._flags = flags

    def flags(self):
        return self._flags

    def setCheckState(self, state):
        self._check_state = state

    def checkState(self):
        return self._check_state


class QListWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._items = []

    def addItem(self, item):
        if isinstance(item, str):
            item = QListWidgetItem(item)
        self._items.append(item)

    def count(self):
        return len(self._items)

    def item(self, row):
        if 0 <= row < len(self._items):
            return self._items[row]
        return None

    def clear(self):
        self._items = []


class QTableWidgetItem:
    def __init__(self, text=""):
        self._text = str(text)
        self._data = {
            0: str(text),
            2: str(text),
            Qt.ItemDataRole.DisplayRole: str(text),
            Qt.ItemDataRole.EditRole: str(text)
        }
        self._flags = 33
        self._tooltip = ""
        self._icon = None
        self._background = None
        self._row = -1
        self._col = -1
        self._table = None

    def setText(self, text):
        self._text = str(text)
        self._data[0] = str(text)
        self._data[2] = str(text)
        self._data[Qt.ItemDataRole.DisplayRole] = str(text)
        self._data[Qt.ItemDataRole.EditRole] = str(text)

    def text(self):
        return self._text

    def setToolTip(self, tip):
        self._tooltip = tip

    def toolTip(self):
        return self._tooltip

    def setIcon(self, icon):
        self._icon = icon

    def icon(self):
        return self._icon

    def setFlags(self, flags):
        self._flags = flags

    def flags(self):
        return self._flags

    def setData(self, role, val):
        self._data[role] = val
        if role == Qt.ItemDataRole.EditRole or role == 2 or role == 0 or role == Qt.ItemDataRole.DisplayRole:
            self._text = str(val) if val is not None else ""
        if self._table and hasattr(self._table, 'itemChanged'):
            self._table.itemChanged.emit(self)

    def data(self, role=Qt.ItemDataRole.DisplayRole):
        return self._data.get(role, None)

    def setBackground(self, brush):
        self._background = brush

    def background(self):
        return self._background

    def setForeground(self, brush):
        pass

    def row(self):
        return self._row

    def column(self):
        return self._col


class QTableWidget(QWidget):
    def __init__(self, rows=0, cols=0, parent=None):
        super().__init__(parent)
        self.rows = rows
        self._rows = rows
        self.cols = cols
        self._cols = cols
        self._items = {}
        self.horizontal_labels = []
        self._headers = []
        self._selected_rows = []
        self.cellChanged = _MockSignal()
        self.itemChanged = _MockSignal()
        self.itemDoubleClicked = _MockSignal()

    def setRowCount(self, count):
        self.rows = count
        self._rows = count

    def rowCount(self):
        return self._rows

    def setColumnCount(self, count):
        self.cols = count
        self._cols = count

    def columnCount(self):
        return self._cols

    def setHorizontalHeaderLabels(self, labels):
        self._headers = labels
        self.horizontal_labels = labels

    def setItem(self, row, col, item):
        self._items[(row, col)] = item
        if item is not None:
            item._row = row
            item._col = col
            item._table = self

    def item(self, row, col):
        return self._items.get((row, col), None)

    def removeRow(self, r):
        self.rows = max(0, self.rows - 1)
        self._rows = self.rows

    def clear(self):
        self._items = {}

    def clearSelection(self):
        pass

    def horizontalHeader(self):
        return QHeaderView()

    def verticalHeader(self):
        return QHeaderView()

    def selectionModel(self):
        class _SM:
            def __init__(sm_self):
                sm_self.selectionChanged = _MockSignal()
            def selectedRows(sm_self):
                return self._selected_rows
            def selectedIndexes(sm_self):
                return []
            def isSelected(sm_self, idx):
                return False
            def select(sm_self, idx, flags=None):
                pass
            def clearSelection(sm_self):
                pass
        return _SM()

    def setSelectionBehavior(self, behavior):
        pass

    def setSelectionMode(self, mode):
        pass

    def setAlternatingRowColors(self, val):
        pass

    def setHorizontalScrollMode(self, mode):
        pass

    def setVerticalScrollMode(self, mode):
        pass

    def horizontalScrollBar(self):
        class _Bar:
            def value(self): return 0
            def setValue(self, v): pass
        return _Bar()

    def verticalScrollBar(self):
        class _Bar:
            def value(self): return 0
            def setValue(self, v): pass
        return _Bar()


class QListView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._model = None
        self._selection_model = QItemSelectionModel()
        self._selection_mode = 0
        self._selection_behavior = 0
        self._alternating_row_colors = False
        self.customContextMenuRequested = _MockSignal()
        self.doubleClicked = _MockSignal()

    def setModel(self, model):
        self._model = model

    def model(self):
        return self._model

    def selectionModel(self):
        return self._selection_model

    def setContextMenuPolicy(self, policy):
        pass

    def setSelectionMode(self, mode):
        self._selection_mode = mode

    def setSelectionBehavior(self, behavior):
        self._selection_behavior = behavior

    def setAlternatingRowColors(self, val):
        self._alternating_row_colors = bool(val)

    def alternatingRowColors(self):
        return self._alternating_row_colors

    def setEditTriggers(self, triggers):
        pass

    def setAllColumnsShowFocus(self, val):
        pass


class QTreeView(QListView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._header = QHeaderView()

    def header(self):
        return self._header

    def setDragEnabled(self, val):
        pass

    def setAcceptDrops(self, val):
        pass

    def setDropIndicatorShown(self, val):
        pass

    def setColumnWidth(self, col, width):
        pass

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

    def isExpanded(self, idx):
        return False

    def setExpanded(self, idx, val):
        pass

    def verticalScrollBar(self):
        return None

    def horizontalScrollBar(self):
        return None

    def indexAt(self, pos):
        return QModelIndex()

    def viewport(self):
        return self


class QStackedWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._widgets = []
        self._current_index = 0

    def addWidget(self, widget):
        self._widgets.append(widget)

    def setCurrentIndex(self, index):
        self._current_index = index

    def currentIndex(self):
        return self._current_index


class QScrollArea(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._widget = None

    def setWidget(self, widget):
        self._widget = widget

    def setWidgetResizable(self, val):
        pass


class QGroupBox(QWidget):
    def __init__(self, title="", parent=None):
        super().__init__(parent)
        self._title = title

    def setTitle(self, title):
        self._title = title


class QSplitter(QWidget):
    def __init__(self, orientation=1, parent=None):
        super().__init__(parent)
        self._widgets = []

    def addWidget(self, widget):
        self._widgets.append(widget)

    def setSizes(self, sizes):
        pass

    def setStretchFactor(self, idx, f):
        pass


class QTabWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._tabs = []
        self.tabs = self._tabs
        self._current_index = 0
        self._corner_widget = None
        self.currentChanged = _MockSignal()

    def addTab(self, widget, label):
        self._tabs.append((widget, label))

    def setCurrentIndex(self, index):
        self._current_index = index
        self.currentChanged.emit(index)

    def currentIndex(self):
        return self._current_index

    def setCornerWidget(self, widget, corner=None):
        self._corner_widget = widget


class QVBoxLayout:
    def __init__(self, parent=None):
        self._items = []

    def addWidget(self, widget, *args):
        self._items.append(widget)

    def addLayout(self, layout, *args):
        self._items.append(layout)

    def setContentsMargins(self, *args):
        pass

    def setSpacing(self, s):
        pass

    def addStretch(self, *args):
        pass


class QHBoxLayout(QVBoxLayout):
    def setAlignment(self, align):
        pass

    def count(self):
        return len(self._items)

    def takeAt(self, idx):
        if 0 <= idx < len(self._items):
            return self._items.pop(idx)
        return None


class QGridLayout(QVBoxLayout):
    def addWidget(self, widget, row=0, col=0, *args):
        self._items.append(widget)

    def setHorizontalSpacing(self, s): pass
    def setVerticalSpacing(self, s): pass
    def setColumnStretch(self, col, stretch): pass


class QFormLayout(QVBoxLayout):
    def addRow(self, label, widget):
        self._items.append((label, widget))


class QDialogButtonBox(QWidget):
    class StandardButton:
        Save = 1
        Cancel = 2
        Ok = 4

    def __init__(self, buttons=None, parent=None):
        super().__init__(parent)
        self.accepted = _MockSignal()
        self.rejected = _MockSignal()


class QToolBar(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
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

    def setToolButtonStyle(self, style):
        pass

    def setIconSize(self, size):
        pass

    def clear(self):
        self._actions = []
        self._widgets = []


class QMenu(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._actions = []

    def addAction(self, *args):
        if len(args) == 1 and isinstance(args[0], QAction):
            act = args[0]
        elif len(args) >= 1 and isinstance(args[0], str):
            act = QAction(args[0], self)
        else:
            act = QAction("", self)
        self._actions.append(act)
        return act

    def addMenu(self, title):
        m = QMenu(self)
        return m

    def addSeparator(self):
        pass

    def exec(self, pos=None):
        pass

    def setIcon(self, icon):
        pass


class QHeaderView(QWidget):
    Interactive = 0
    ResizeToContents = 1
    Stretch = 2

    class ResizeMode:
        Interactive = 0
        ResizeToContents = 1
        Stretch = 2

    def setSectionResizeMode(self, col, mode):
        pass

    def setMinimumSectionSize(self, size):
        pass

    def setDefaultSectionSize(self, size):
        pass

    def count(self):
        return 3


class QSizePolicy:
    Fixed = 0
    Minimum = 1
    Maximum = 4
    Preferred = 5
    Expanding = 7
    Ignored = 13

    class Policy:
        Fixed = 0
        Minimum = 1
        Maximum = 4
        Preferred = 5
        Expanding = 7
        Ignored = 13

    def __init__(self, h=1, v=1):
        pass


class QAbstractItemView:
    NoEditTriggers = 0
    ExtendedSelection = 3
    SelectRows = 1
    SingleSelection = 1
    MultiSelection = 2
    ScrollPerPixel = 1
    ScrollPerItem = 0

    class SelectionMode:
        ExtendedSelection = 3
        SingleSelection = 1
        MultiSelection = 2

    class SelectionBehavior:
        SelectRows = 1
        SelectColumns = 2
        SelectItems = 0

    class ScrollMode:
        ScrollPerPixel = 1
        ScrollPerItem = 0


class QDialog(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._result = 0

    def setWindowTitle(self, title):
        self._title = title

    def setWindowFlags(self, flags):
        pass

    def windowFlags(self):
        return 0

    def accept(self):
        self._result = 1

    def reject(self):
        self._result = 0

    def exec(self):
        return self._result


class QMessageBox(QDialog):
    Yes = 16384
    No = 65536
    Ok = 1024
    Cancel = 4194304

    class StandardButton:
        Yes = 16384
        No = 65536
        Ok = 1024
        Cancel = 4194304

    class ButtonRole:
        ActionRole = 1
        RejectRole = 2
        AcceptRole = 0

    def __init__(self, parent=None):
        super().__init__(parent)
        self._buttons = []
        self._clicked = None
        self._text = ""
        self._icon = None

    def setText(self, text):
        self._text = text

    def setIcon(self, icon):
        self._icon = icon

    def addButton(self, *args):
        class _DummyButton:
            def setStyleSheet(self, style): pass
            def setIcon(self, icon): pass
        btn = _DummyButton()
        self._buttons.append(btn)
        return btn

    def clickedButton(self):
        return self._clicked

    def exec(self):
        if self._buttons:
            self._clicked = self._buttons[0]
        return 0

    @classmethod
    def warning(cls, parent, title, text, buttons=None, default_button=None):
        return cls.Yes

    @classmethod
    def information(cls, parent, title, text):
        pass

    @classmethod
    def critical(cls, parent, title, text):
        pass

    @classmethod
    def question(cls, parent, title, text, buttons=None, default_button=None):
        return cls.Yes


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


class QApplication:
    @classmethod
    def clipboard(cls):
        class _Clip:
            def setText(self, t): pass
        return _Clip()

    @classmethod
    def setOverrideCursor(cls, c): pass

    @classmethod
    def restoreOverrideCursor(cls): pass

    @staticmethod
    def startDragDistance():
        return 8


class QToolTip:
    @classmethod
    def showText(cls, *args): pass

    @classmethod
    def hideText(cls): pass


# --- Graphics Scene & View Mocks ---

class QGraphicsItem:
    ItemSelectedHasChanged = 4
    ItemIsSelectable = 1
    ItemIsFocusable = 2

    class GraphicsItemChange:
        ItemSelectedHasChanged = 4

    class GraphicsItemFlag:
        ItemIsSelectable = 1
        ItemIsFocusable = 2

    def __init__(self, parent=None):
        self._selected = False

    def setFlags(self, *args): pass
    def setAcceptHoverEvents(self, val): pass
    def setToolTip(self, text): pass
    def setSelected(self, val): self._selected = bool(val)
    def isSelected(self): return self._selected
    def scene(self): return None
    def setZValue(self, val): pass
    def mapFromScene(self, pt): return pt
    def sceneBoundingRect(self): return QRectF()


class QGraphicsLineItem(QGraphicsItem):
    def __init__(self, *args):
        super().__init__()

    def setPen(self, *args): pass
    def setLine(self, *args): pass
    def show(self): pass
    def hide(self): pass


class QGraphicsObject(QGraphicsItem):
    layerDoubleClicked = _MockSignal()
    layerClicked = _MockSignal()
    layoutChanged = _MockSignal()


class QStyleOptionGraphicsItem:
    pass


class QGraphicsScene(QObject):
    def __init__(self, parent=None):
        super().__init__(parent)

    def clear(self): pass
    def addItem(self, item): pass
    def setSceneRect(self, *args): pass
    def items(self): return []
    def itemsBoundingRect(self): return QRectF()


class QGraphicsView(QWidget):
    NoDrag = 0
    ScrollHandDrag = 1
    RubberBandDrag = 2
    AnchorUnderMouse = 1

    class DragMode:
        NoDrag = 0
        ScrollHandDrag = 1
        RubberBandDrag = 2

    class ViewportAnchor:
        AnchorUnderMouse = 1

    def __init__(self, parent=None):
        super().__init__(parent)
        self._drag_mode = 0

    def setScene(self, scene): pass
    def setDragMode(self, mode): self._drag_mode = mode
    def dragMode(self): return self._drag_mode
    def setRenderHints(self, hints): pass
    def setTransformationAnchor(self, anchor): pass
    def scale(self, sx, sy): pass
    def fitInView(self, *args): pass
    def viewport(self): return self
    def setHorizontalScrollBarPolicy(self, p): pass
    def setVerticalScrollBarPolicy(self, p): pass
    def centerOn(self, item): pass


class QSvgRenderer:
    def __init__(self, path=None):
        self._path = path

    def isValid(self):
        return bool(self._path)

    def render(self, painter, rect):
        pass


# --- QGIS Core & GUI Mocks ---

class Qgis:
    class MessageLevel:
        Info = 0
        Warning = 1
        Critical = 2
        Success = 3


class QgsSettings:
    def __init__(self, *args):
        self._data = {}

    def value(self, key, default=None):
        return self._data.get(key, default)

    def setValue(self, key, value):
        self._data[key] = value

    def remove(self, key):
        self._data.pop(key, None)


class QgsCoordinateReferenceSystem:
    def __init__(self, authid="EPSG:4326"):
        self._authid = authid

    def authid(self):
        return self._authid

    def isValid(self):
        return True

    def createFromOgcWmsCrs(self, text):
        return True


class QgsRectangle:
    def __init__(self, xmin=0, ymin=0, xmax=0, ymax=0):
        self._xmin, self._ymin, self._xmax, self._ymax = xmin, ymin, xmax, ymax

    def xMinimum(self): return self._xmin
    def yMinimum(self): return self._ymin
    def xMaximum(self): return self._xmax
    def yMaximum(self): return self._ymax
    def isNull(self): return False
    def combineExtentWith(self, *args): pass
    def toString(self, dec=0): return f"{self._xmin},{self._ymin},{self._xmax},{self._ymax}"


class QgsVectorDataProvider:
    CreateSpatialIndex = 1

    class Capability:
        FastFilters = 1
        CreateSpatialIndex = 1

    def __init__(self, name="ogr"):
        self._name = name

    def name(self):
        return self._name

    def capabilities(self):
        return 1

    def storageType(self):
        return "GPKG"

    def encoding(self):
        return "UTF-8"

    def capabilitiesString(self):
        return ""

    def dataSourceUri(self):
        return "test_path"

    def availableEncodings(self):
        return ["UTF-8", "GBK", "CP936"]


class QgsMapLayer:
    class LayerType:
        VectorLayer = 0
        RasterLayer = 1
        PluginLayer = 2
        MeshLayer = 3
        VectorTileLayer = 4
        PointCloudLayer = 5
        AnnotationLayer = 6
        TiledSceneLayer = 7

    def __init__(self, layer_id="", name="", source_path="", provider="ogr"):
        self._id = layer_id or name
        self._name = name
        self._source = source_path
        self._provider = QgsVectorDataProvider(provider)
        self._crs = QgsCoordinateReferenceSystem("EPSG:4326")
        self._custom_properties = {}

    def id(self): return self._id
    def name(self): return self._name
    def setName(self, name): self._name = name
    def source(self): return self._source
    def setDataSource(self, source, name, provider, options=None):
        self._source = source
        self._name = name
    def isValid(self): return True
    def isEditable(self): return False
    def startEditing(self): return False
    def commitChanges(self): return False
    def triggerRepaint(self): pass
    def dataProvider(self): return self._provider
    def crs(self): return self._crs
    def setCrs(self, crs): self._crs = crs
    def extent(self): return QgsRectangle()
    def type(self): return self.LayerType.VectorLayer
    def geometryType(self): return 0
    def customProperty(self, key, default=None): return self._custom_properties.get(key, default)
    def setCustomProperty(self, key, val): self._custom_properties[key] = val
    def title(self): return ""
    def abstract(self): return ""
    def shortName(self): return ""
    def isSpatial(self): return True
    def maximumScale(self): return 0.0
    def minimumScale(self): return 0.0
    def toggleScaleBasedVisibility(self, b): pass
    def setMaximumScale(self, s): pass
    def setMinimumScale(self, s): pass
    def providerType(self): return "ogr"


class QgsVectorLayer(QgsMapLayer):
    def __init__(self, path="", name="", provider="ogr"):
        super().__init__(name, name, path, provider)
        self._subset_string = ""
        self._fields = []

    def subsetString(self):
        return self._subset_string

    def setSubsetString(self, expr):
        self._subset_string = expr
        return True

    def type(self):
        return self.LayerType.VectorLayer

    def fields(self):
        return self._fields


class QgsRasterLayer(QgsMapLayer):
    def __init__(self, path="", name="", provider="gdal"):
        super().__init__(name, name, path, provider)

    def type(self):
        return self.LayerType.RasterLayer


class QgsMapLayerStyle:
    def __init__(self):
        self.source_layer = None
        self.target_layer = None

    def readFromLayer(self, layer):
        self.source_layer = layer

    def writeToLayer(self, layer):
        self.target_layer = layer


class QgsLayerTreeLayer:
    def __init__(self, layer):
        self._layer = layer
        self._parent = None
        self._visible = True

    def layer(self):
        return self._layer

    def layerId(self):
        return self._layer.id() if self._layer else ""

    def name(self):
        return self._layer.name() if self._layer else ""

    def isItemVisibilityChecked(self):
        return bool(self._visible)

    def itemVisibilityChecked(self):
        return bool(self._visible)

    def isVisible(self):
        if not self._visible:
            return False
        if hasattr(self, '_parent') and self._parent:
            return self._parent.isVisible()
        return True

    def setItemVisibilityChecked(self, checked):
        self._visible = bool(checked)

    def parent(self):
        return self._parent


class QgsLayerTreeGroup:
    def __init__(self, name=""):
        self._name = name
        self._children = []
        self._parent = None
        self._visible = True

    def name(self):
        return self._name

    def setName(self, name):
        self._name = name

    def children(self):
        return self._children

    def addGroup(self, name):
        grp = QgsLayerTreeGroup(name)
        grp._parent = self
        self._children.append(grp)
        return grp

    def addLayer(self, layer):
        node = QgsLayerTreeLayer(layer)
        node._parent = self
        self._children.append(node)
        return node

    def findLayer(self, layer_id):
        for ch in self._children:
            if isinstance(ch, QgsLayerTreeLayer) and ch.layer() and ch.layer().id() == layer_id:
                return ch
            if isinstance(ch, QgsLayerTreeGroup):
                res = ch.findLayer(layer_id)
                if res:
                    return res
        return None

    def findGroup(self, name):
        for ch in self._children:
            if isinstance(ch, QgsLayerTreeGroup):
                if ch.name() == name:
                    return ch
                res = ch.findGroup(name)
                if res:
                    return res
        return None

    def isItemVisibilityChecked(self):
        return bool(self._visible)

    def itemVisibilityChecked(self):
        return bool(self._visible)

    def isVisible(self):
        if not self._visible:
            return False
        if hasattr(self, '_parent') and self._parent:
            return self._parent.isVisible()
        return True

    def setItemVisibilityChecked(self, checked):
        self._visible = bool(checked)

    def parent(self):
        return self._parent


class QgsLayerTreeModel:
    class Flag:
        AllowNodeReorder = 1

    def __init__(self, root=None):
        self.root = root

    def setFlag(self, flag, enabled=True):
        pass

    def node2index(self, node):
        return QModelIndex(node)

    def mimeData(self, indexes):
        return None

    def dropMimeData(self, data, action, row, column, parent):
        return False


class QgsLayerTreeUtils:
    @classmethod
    def countMapLayers(cls, root):
        return 0

    @classmethod
    def countMapLayerInTree(cls, root, layer):
        return 1


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


class QgsMapThemeCollection:
    def __init__(self):
        self._themes = {}

    def mapThemes(self):
        return list(self._themes.keys())

    def mapThemeVisibleLayerIds(self, theme):
        return self._themes.get(theme, [])


class QgsProject:
    _instance = None

    def __init__(self):
        self._layers = {}
        self._root = QgsLayerTreeGroup("root")
        self._theme_collection = QgsMapThemeCollection()
        self._file_name = ""
        self.layerRemoved = _MockSignal()
        self.layerWasAdded = _MockSignal()
        self.layersAdded = _MockSignal()
        self.layersRemoved = _MockSignal()

    @classmethod
    def instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def mapLayers(self):
        return self._layers

    def mapLayer(self, layer_id):
        return self._layers.get(layer_id, None)

    def addMapLayer(self, layer):
        self._layers[layer.id()] = layer
        self._root.addLayer(layer)
        return layer

    def addVectorLayer(self, path, name, provider="ogr"):
        layer = QgsVectorLayer(path, name, provider)
        self.addMapLayer(layer)
        return layer

    def removeMapLayer(self, layer_id):
        if layer_id in self._layers:
            del self._layers[layer_id]

    def removeMapLayers(self, layer_ids):
        for lid in list(layer_ids):
            self.removeMapLayer(lid)

    def fileName(self):
        return self._file_name

    def setFileName(self, name):
        self._file_name = name

    def layerTreeRoot(self):
        return self._root

    def mapThemeCollection(self):
        return self._theme_collection

    def transformContext(self):
        return None

    def setDirty(self, d):
        pass

    def crs(self):
        return QgsCoordinateReferenceSystem()

    def clear(self):
        self._layers = {}
        self._root = QgsLayerTreeGroup("root")
        self._file_name = ""


class QgsDockWidget(QWidget):
    def __init__(self, title="", parent=None):
        super().__init__(parent)
        self._title = title
        self._widget = None

    def setAllowedAreas(self, areas):
        pass

    def setWidget(self, widget):
        self._widget = widget


class QgsMapCanvas(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

    def setExtent(self, rect):
        pass

    def refresh(self):
        pass

    def currentLayer(self):
        return None

    def setCurrentLayer(self, layer):
        pass


class QgsMessageBar(QWidget):
    def pushMessage(self, *args, **kwargs):
        pass


class QgsStyle:
    @classmethod
    def defaultStyle(cls):
        return None


class QgsMapLayerModel:
    @classmethod
    def iconForLayer(cls, layer):
        return QIcon()


# --- Module Registration System ---

def setup_qgis_mocks():
    """Inject mock modules into sys.modules if qgis is not installed."""
    if "qgis" in sys.modules and hasattr(sys.modules["qgis"], "core"):
        return

    # Root packages
    qgis_mod = types.ModuleType("qgis")
    pyqt_mod = types.ModuleType("qgis.PyQt")
    core_mod = types.ModuleType("qgis.core")
    gui_mod = types.ModuleType("qgis.gui")
    utils_mod = types.ModuleType("qgis.utils")

    # QtCore
    qtcore_mod = types.ModuleType("qgis.PyQt.QtCore")
    qtcore_symbols = {
        "Qt": Qt,
        "QTimer": QTimer,
        "QModelIndex": QModelIndex,
        "QPersistentModelIndex": QPersistentModelIndex,
        "QSize": QSize,
        "QPoint": QPoint,
        "QPointF": QPointF,
        "QRect": QRect,
        "QRectF": QRectF,
        "QLineF": QLineF,
        "QObject": QObject,
        "Signal": Signal,
        "pyqtSignal": pyqtSignal,
        "QCoreApplication": QCoreApplication,
        "QSettings": QSettings,
        "QTranslator": QTranslator,
        "QLocale": QLocale,
        "QItemSelectionModel": QItemSelectionModel,
    }
    for k, v in qtcore_symbols.items():
        setattr(qtcore_mod, k, v)

    # QtGui
    qtgui_mod = types.ModuleType("qgis.PyQt.QtGui")
    qtgui_symbols = {
        "QIcon": QIcon,
        "QPixmap": QPixmap,
        "QPainter": QPainter,
        "QPainterPath": QPainterPath,
        "QColor": QColor,
        "QFont": QFont,
        "QFontMetrics": QFontMetrics,
        "QPen": QPen,
        "QBrush": QBrush,
        "QLinearGradient": QLinearGradient,
        "QCursor": QCursor,
        "QTextCursor": QTextCursor,
        "QAction": QAction,
        "QActionGroup": QActionGroup,
        "QStandardItemModel": QStandardItemModel,
        "QStandardItem": QStandardItem,
    }
    for k, v in qtgui_symbols.items():
        setattr(qtgui_mod, k, v)

    # QtWidgets
    qtwidgets_mod = types.ModuleType("qgis.PyQt.QtWidgets")
    qtwidgets_symbols = {
        "QWidget": QWidget,
        "QDialog": QDialog,
        "QMessageBox": QMessageBox,
        "QFileDialog": QFileDialog,
        "QInputDialog": QInputDialog,
        "QLabel": QLabel,
        "QPushButton": QPushButton,
        "QToolButton": QToolButton,
        "QLineEdit": QLineEdit,
        "QTextEdit": QTextEdit,
        "QComboBox": QComboBox,
        "QCheckBox": QCheckBox,
        "QListWidget": QListWidget,
        "QListWidgetItem": QListWidgetItem,
        "QTableWidget": QTableWidget,
        "QTableWidgetItem": QTableWidgetItem,
        "QTreeView": QTreeView,
        "QListView": QListView,
        "QStackedWidget": QStackedWidget,
        "QScrollArea": QScrollArea,
        "QGroupBox": QGroupBox,
        "QSplitter": QSplitter,
        "QTabWidget": QTabWidget,
        "QVBoxLayout": QVBoxLayout,
        "QHBoxLayout": QHBoxLayout,
        "QGridLayout": QGridLayout,
        "QFormLayout": QFormLayout,
        "QDialogButtonBox": QDialogButtonBox,
        "QToolBar": QToolBar,
        "QMenu": QMenu,
        "QAction": QAction,
        "QActionGroup": QActionGroup,
        "QHeaderView": QHeaderView,
        "QSizePolicy": QSizePolicy,
        "QAbstractItemView": QAbstractItemView,
        "QApplication": QApplication,
        "QToolTip": QToolTip,
        "QGraphicsView": QGraphicsView,
        "QGraphicsScene": QGraphicsScene,
        "QGraphicsItem": QGraphicsItem,
        "QGraphicsLineItem": QGraphicsLineItem,
        "QGraphicsObject": QGraphicsObject,
        "QStyleOptionGraphicsItem": QStyleOptionGraphicsItem,
    }
    for k, v in qtwidgets_symbols.items():
        setattr(qtwidgets_mod, k, v)

    # QtSvg
    qtsvg_mod = types.ModuleType("qgis.PyQt.QtSvg")
    setattr(qtsvg_mod, "QSvgRenderer", QSvgRenderer)

    # qgis.core
    core_symbols = {
        "Qgis": Qgis,
        "QgsProject": QgsProject,
        "QgsMapLayer": QgsMapLayer,
        "QgsVectorLayer": QgsVectorLayer,
        "QgsRasterLayer": QgsRasterLayer,
        "QgsLayerTreeGroup": QgsLayerTreeGroup,
        "QgsLayerTreeLayer": QgsLayerTreeLayer,
        "QgsLayerTreeModel": QgsLayerTreeModel,
        "QgsLayerTreeUtils": QgsLayerTreeUtils,
        "QgsVectorFileWriter": QgsVectorFileWriter,
        "QgsMapLayerStyle": QgsMapLayerStyle,
        "QgsMapThemeCollection": QgsMapThemeCollection,
        "QgsCoordinateReferenceSystem": QgsCoordinateReferenceSystem,
        "QgsVectorDataProvider": QgsVectorDataProvider,
        "QgsStyle": QgsStyle,
        "QgsSettings": QgsSettings,
        "QgsRectangle": QgsRectangle,
        "QgsMapLayerModel": QgsMapLayerModel,
    }
    for k, v in core_symbols.items():
        setattr(core_mod, k, v)

    # qgis.gui
    gui_symbols = {
        "QgsDockWidget": QgsDockWidget,
        "QgsMapCanvas": QgsMapCanvas,
        "QgsMessageBar": QgsMessageBar,
    }
    for k, v in gui_symbols.items():
        setattr(gui_mod, k, v)

    # qgis.utils
    class _MockIface:
        def __init__(self):
            self.mapCanvas_inst = QgsMapCanvas()
            self.messageBar_inst = QgsMessageBar()
            class _MW:
                def removeToolBar(self, tb): pass
            self._mw = _MW()
        def mapCanvas(self): return self.mapCanvas_inst
        def messageBar(self): return self.messageBar_inst
        def mainWindow(self): return self._mw
        def addDockWidget(self, *args): pass
        def removeDockWidget(self, *args): pass
        def addToolBar(self, *args): return QToolBar()
        def addPluginToMenu(self, *args): pass
        def removePluginMenu(self, *args): pass
        def addVectorLayer(self, *args): return QgsVectorLayer()
        def addRasterLayer(self, *args): return QgsRasterLayer()

    setattr(utils_mod, "iface", _MockIface())
    setattr(utils_mod, "plugins", {})

    # Link nested modules
    pyqt_mod.QtCore = qtcore_mod
    pyqt_mod.QtGui = qtgui_mod
    pyqt_mod.QtWidgets = qtwidgets_mod
    pyqt_mod.QtSvg = qtsvg_mod
    qgis_mod.PyQt = pyqt_mod
    qgis_mod.core = core_mod
    qgis_mod.gui = gui_mod
    qgis_mod.utils = utils_mod

    # Register in sys.modules
    sys.modules["qgis"] = qgis_mod
    sys.modules["qgis.PyQt"] = pyqt_mod
    sys.modules["qgis.PyQt.QtCore"] = qtcore_mod
    sys.modules["qgis.PyQt.QtGui"] = qtgui_mod
    sys.modules["qgis.PyQt.QtWidgets"] = qtwidgets_mod
    sys.modules["qgis.PyQt.QtSvg"] = qtsvg_mod
    sys.modules["qgis.core"] = core_mod
    sys.modules["qgis.gui"] = gui_mod
    sys.modules["qgis.utils"] = utils_mod
