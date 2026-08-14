import unittest
from unittest.mock import MagicMock, patch
import os

import main_plugin
from main_plugin import SuperLayerPlugin

class TestMainPlugin(unittest.TestCase):
    def setUp(self):
        self.iface = MagicMock()
        self.main_window = MagicMock()
        self.iface.mainWindow.return_value = self.main_window
        self.plugin = SuperLayerPlugin(self.iface)

    def test_init_gui(self):
        # Case 1: Icon file exists
        with patch('main_plugin.QAction') as mock_action_cls, \
             patch('main_plugin.QIcon') as mock_icon_cls, \
             patch('os.path.exists', return_value=True):
            
            mock_action = MagicMock()
            mock_action_cls.return_value = mock_action
            mock_icon = MagicMock()
            mock_icon_cls.return_value = mock_icon
            
            self.plugin.initGui()
            
            mock_action_cls.assert_called_once_with(mock_icon, "SuperLayer", self.main_window)
            mock_action.triggered.connect.assert_called_once_with(self.plugin.run)
            self.iface.addPluginToMenu.assert_called_once_with("&Plugins", mock_action)
            self.iface.addToolBar.assert_called_once_with("SuperLayer")
            self.assertEqual(self.plugin.action, mock_action)
            
        # Reset mocks on self.iface
        self.iface.addPluginToMenu.reset_mock()
        self.iface.addToolBar.reset_mock()
        
        # Case 2: Icon file does not exist
        with patch('main_plugin.QAction') as mock_action_cls, \
             patch('os.path.exists', return_value=False):
            
            mock_action = MagicMock()
            mock_action_cls.return_value = mock_action
            
            self.plugin.initGui()
            
            mock_action_cls.assert_called_once_with("SuperLayer", self.main_window)
            mock_action.triggered.connect.assert_called_once_with(self.plugin.run)
            self.iface.addPluginToMenu.assert_called_once_with("&Plugins", mock_action)
            self.iface.addToolBar.assert_called_once_with("SuperLayer")
            self.assertEqual(self.plugin.action, mock_action)

    def test_unload(self):
        mock_action = MagicMock()
        self.plugin.action = mock_action
        mock_toolbar = MagicMock()
        self.plugin.toolbar = mock_toolbar
        
        mock_dock = MagicMock()
        self.plugin.dock = mock_dock
        
        self.plugin.unload()
        
        self.iface.removePluginMenu.assert_called_once_with("&Plugins", mock_action)
        mock_toolbar.clear.assert_called_once()
        self.main_window.removeToolBar.assert_called_once_with(mock_toolbar)
        mock_toolbar.deleteLater.assert_called_once()
        self.assertIsNone(self.plugin.toolbar)
        mock_dock.close.assert_called_once()
        mock_dock.deleteLater.assert_called_once()
        self.assertIsNone(self.plugin.dock)

    def test_run_lazy_initialization(self):
        with patch('main_plugin.SuperLayerDockWidget') as mock_dock_cls:
            mock_dock = MagicMock()
            mock_dock_cls.return_value = mock_dock
            
            # First call: dock is None, should instantiate
            self.plugin.run()
            
            mock_dock_cls.assert_called_once_with(self.iface, self.main_window)
            self.iface.addDockWidget.assert_not_called()
            mock_dock.show.assert_called_once()
            mock_dock.raise_.assert_called_once()
            mock_dock.activateWindow.assert_called_once()
            mock_dock.refresh.assert_called_once()
            self.assertEqual(self.plugin.dock, mock_dock)
            
            # Reset mocks
            mock_dock_cls.reset_mock()
            self.iface.addDockWidget.reset_mock()
            mock_dock.show.reset_mock()
            mock_dock.raise_.reset_mock()
            mock_dock.activateWindow.reset_mock()
            mock_dock.refresh.reset_mock()
            
            # Second call: dock is already instantiated, should not create it again
            self.plugin.run()
            
            mock_dock_cls.assert_not_called()
            self.iface.addDockWidget.assert_not_called()
            mock_dock.show.assert_called_once()
            mock_dock.raise_.assert_called_once()
            mock_dock.activateWindow.assert_called_once()
            mock_dock.refresh.assert_called_once()

if __name__ == '__main__':
    unittest.main()
