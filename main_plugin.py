import os

# Robust fallback imports for Qt
try:
    from PyQt5.QtCore import Qt
    from PyQt5.QtWidgets import QAction
    from PyQt5.QtGui import QIcon
except ImportError:
    try:
        from qtpy.QtCore import Qt
        from qtpy.QtWidgets import QAction
        from qtpy.QtGui import QIcon
    except ImportError:
        try:
            from PySide2.QtCore import Qt
            from PySide2.QtWidgets import QAction
            from PySide2.QtGui import QIcon
        except ImportError:
            try:
                from PySide6.QtCore import Qt
                from PySide6.QtGui import QAction, QIcon
            except ImportError:
                # Basic mock classes for CLI tests without Qt installed
                class Qt:
                    RightDockWidgetArea = 2
                class QAction:
                    def __init__(self, text, parent=None):
                        self._text = text
                        self.parent = parent
                        self.triggered = self._Signal()
                    class _Signal:
                        def connect(self, slot):
                            self._slot = slot
                        def emit(self, *args):
                            if hasattr(self, '_slot'):
                                self._slot(*args)
                class QIcon:
                    def __init__(self, *args):
                        pass

try:
    from .dock_widget import SuperLayerDockWidget
except ImportError:
    from dock_widget import SuperLayerDockWidget

class SuperLayerPlugin:
    """SuperLayer QGIS Plugin integration class."""
    def __init__(self, iface):
        self.iface = iface
        self.dock = None
        self.action = None

    def initGui(self):
        # Create action
        icon_path = os.path.join(os.path.dirname(__file__), 'icons', 'SuperLayer.svg')
        if os.path.exists(icon_path):
            icon = QIcon(icon_path)
            self.action = QAction(icon, "SuperLayer", self.iface.mainWindow())
        else:
            self.action = QAction("SuperLayer", self.iface.mainWindow())
        self.action.triggered.connect(self.run)
        
        # Add to Plugins menu and toolbar
        self.iface.addPluginToMenu("&Plugins", self.action)
        self.iface.addToolBarIcon(self.action)

    def unload(self):
        if self.action:
            self.iface.removePluginMenu("&Plugins", self.action)
            self.iface.removeToolBarIcon(self.action)
        if self.dock:
            self.dock.close()

    def run(self):
        if not self.dock:
            self.dock = SuperLayerDockWidget(self.iface, self.iface.mainWindow())
        
        if self.dock.isMinimized():
            self.dock.showNormal()
        self.dock.show()
        self.dock.raise_()
        self.dock.activateWindow()
        self.dock.refresh()
