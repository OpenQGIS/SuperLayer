import os
import re

# Robust fallback imports for Qt
try:
    from qgis.PyQt.QtCore import Qt, QTranslator, QLocale, QCoreApplication
    from qgis.PyQt.QtWidgets import QAction
    from qgis.PyQt.QtGui import QIcon
    from qgis.core import QgsSettings
except ImportError:
    try:
        from qtpy.QtCore import Qt, QTranslator, QLocale, QCoreApplication
        from qtpy.QtWidgets import QAction
        from qtpy.QtGui import QIcon
        class QgsSettings:
            def value(self, key, default=None): return default
    except ImportError:
        try:
            from PySide2.QtCore import Qt, QTranslator, QLocale, QCoreApplication
            from PySide2.QtWidgets import QAction
            from PySide2.QtGui import QIcon
            class QgsSettings:
                def value(self, key, default=None): return default
        except ImportError:
            try:
                from PySide6.QtCore import Qt, QTranslator, QLocale, QCoreApplication
                from PySide6.QtGui import QAction, QIcon
                class QgsSettings:
                    def value(self, key, default=None): return default
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
                class QTranslator:
                    def load(self, *args, **kwargs): return False
                class QLocale:
                    class system:
                        @staticmethod
                        def name(): return "en"
                class QCoreApplication:
                    @staticmethod
                    def installTranslator(*args): pass
                    @staticmethod
                    def removeTranslator(*args): pass
                class QgsSettings:
                    def value(self, key, default=None): return default

def _qt_immediate_delete(obj):
    """Immediately destroy a Qt C++ object across all Qt bindings.

    Using deleteLater() inside plugin unload() is problematic: it schedules
    deletion asynchronously, so when QGIS reloads the plugin and calls
    initGui() right away, the old widget with the same objectName still
    exists, causing QGIS to emit a "duplicated widget" warning.

    Priority order:
      1. qgis.PyQt.sip   – QGIS 3 (PyQt5) and QGIS 4 (PyQt6) via the
                           qgis.PyQt compatibility shim
      2. PyQt6.sip       – standalone PyQt6
      3. sip             – standalone PyQt5 (installed as a top-level module)
      4. PyQt5.sip       – alternative PyQt5 layout
      5. shiboken6       – PySide6
      6. shiboken2       – PySide2
      7. deleteLater()   – last resort fallback (async, may leave warning)
    """
    # --- sip-based bindings (PyQt5 / PyQt6) ---
    for _loader in (
        lambda: __import__('qgis.PyQt', fromlist=['sip']).sip,
        lambda: __import__('PyQt6.sip', fromlist=['sip']),
        lambda: __import__('sip'),
        lambda: __import__('PyQt5.sip', fromlist=['sip']),
    ):
        try:
            _mod = _loader()
        except ImportError:
            continue
        try:
            if not _mod.isdeleted(obj):
                _mod.delete(obj)
            return
        except (AttributeError, RuntimeError):
            continue
    # --- shiboken-based bindings (PySide6 / PySide2) ---
    for _loader in (
        lambda: __import__('shiboken6'),
        lambda: __import__('shiboken2'),
    ):
        try:
            _mod = _loader()
        except ImportError:
            continue
        try:
            if _mod.isValid(obj):
                _mod.delete(obj)
            return
        except (AttributeError, RuntimeError):
            continue
    # --- async fallback ---
    try:
        obj.deleteLater()
    except RuntimeError:
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
        self.toolbar = None

        # Fetch locale and sanitize to prevent path traversal
        locale_name = QgsSettings().value("locale/userLocale", QLocale.system().name())
        if locale_name is not None:
            locale_name = str(locale_name)
        else:
            locale_name = "en"
        if not re.match(r"^[a-zA-Z0-9_\-]+$", locale_name):
            locale_name = "en"

        # Normalize QGIS locale format (e.g. zh-Hans → zh_CN, zh-Hant → zh_TW)
        _locale_map = {
            "zh-hans": "zh_CN",
            "zh-hant": "zh_TW",
            "zh-cn":   "zh_CN",
            "zh-tw":   "zh_TW",
        }
        locale_candidates = []
        _key = locale_name.lower()
        if _key in _locale_map:
            locale_candidates.append(_locale_map[_key])
        locale_candidates.append(locale_name.replace("-", "_"))
        locale_candidates.append(locale_name.split("_")[0].split("-")[0])

        self.translator = QTranslator()
        i18n_dir = os.path.join(os.path.dirname(__file__), "i18n")
        for candidate in locale_candidates:
            if self.translator.load(f"SuperLayer_{candidate}", i18n_dir):
                QCoreApplication.installTranslator(self.translator)
                break

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
        
        # Create a dedicated draggable/movable QToolBar in the QGIS window
        if hasattr(self.iface, 'addToolBar'):
            self.toolbar = self.iface.addToolBar("SuperLayer")
            if self.toolbar:
                if hasattr(self.toolbar, 'setObjectName'):
                    self.toolbar.setObjectName("SuperLayer")
                if hasattr(self.toolbar, 'addAction'):
                    self.toolbar.addAction(self.action)
        else:
            self.iface.addToolBarIcon(self.action)

    def unload(self):
        if hasattr(self, 'translator'):
            QCoreApplication.removeTranslator(self.translator)
        if self.action:
            self.iface.removePluginMenu("&Plugins", self.action)
            if hasattr(self, 'toolbar') and self.toolbar:
                try:
                    if hasattr(self.toolbar, 'clear'):
                        self.toolbar.clear()
                    if hasattr(self.iface, 'mainWindow') and self.iface.mainWindow() and hasattr(self.iface.mainWindow(), 'removeToolBar'):
                        self.iface.mainWindow().removeToolBar(self.toolbar)
                    elif hasattr(self.iface, 'removeToolBar'):
                        self.iface.removeToolBar(self.toolbar)
                    # Immediately destroy the C++ Qt object so that QGIS reload
                    # does not detect a stale widget with the same objectName
                    # "SuperLayer" before initGui() creates the new one.
                    _qt_immediate_delete(self.toolbar)
                except (RuntimeError, AttributeError):
                    pass
                self.toolbar = None
            else:
                self.iface.removeToolBarIcon(self.action)
        if self.dock:
            try:
                self.dock.close()
                _qt_immediate_delete(self.dock)
            except (RuntimeError, AttributeError):
                pass
            self.dock = None

    def run(self):
        if not self.dock:
            self.dock = SuperLayerDockWidget(self.iface, self.iface.mainWindow())
        
        if self.dock.isMinimized():
            self.dock.showNormal()
        self.dock.show()
        self.dock.raise_()
        self.dock.activateWindow()
        self.dock.refresh()
