import unittest
from unittest.mock import MagicMock, patch
import os
import tempfile
import shutil

# Make sure it can load in testing environment
import dock_widget
from dock_widget import TreeMapDockWidget, QModelIndex

class TestDockWidget(unittest.TestCase):
    def setUp(self):
        self.iface = MagicMock()
        self.parent = MagicMock()
        
        # Mock active canvas/layer methods
        self.canvas = MagicMock()
        self.iface.mapCanvas.return_value = self.canvas
        
    def test_dock_widget_init(self):
        with patch('dock_widget.LayerTreeModel') as mock_model_cls, \
             patch('dock_widget.TreeMapWidget') as mock_treemap_cls, \
             patch('dock_widget.MindMapView') as mock_mindmap_cls:
            
            mock_model = MagicMock()
            mock_model_cls.return_value = mock_model
            mock_treemap = MagicMock()
            mock_treemap_cls.return_value = mock_treemap
            mock_mindmap = MagicMock()
            mock_mindmap_cls.return_value = mock_mindmap
            
            dock = TreeMapDockWidget(self.iface, self.parent)
            self.assertEqual(dock.iface, self.iface)
            self.assertTrue(dock.group_by_physical)
            
            # Verify views initialization
            self.assertIsNotNone(dock.physical_tree_view)
            self.assertIsNotNone(dock.group_tree_view)
            self.assertIsNotNone(dock.treemap_view)
            self.assertIsNotNone(dock.mindmap_view)
            self.assertEqual(dock.physical_model, mock_model)
            self.assertEqual(dock.group_model, mock_model)

    def test_switch_view(self):
        with patch('dock_widget.LayerTreeModel'), \
             patch('dock_widget.TreeMapWidget'), \
             patch('dock_widget.MindMapView'):
            dock = TreeMapDockWidget(self.iface, self.parent)
            
            # Switch to Physical Tree
            dock.switch_view(0)
            self.assertTrue(dock.act_physical_tree.isChecked())
            self.assertFalse(dock.act_group_tree.isChecked())
            self.assertFalse(dock.act_treemap.isChecked())
            self.assertFalse(dock.act_mindmap.isChecked())
            self.assertEqual(dock.stacked_widget.currentIndex(), 0)
            
            # Switch to Group Tree
            dock.switch_view(1)
            self.assertFalse(dock.act_physical_tree.isChecked())
            self.assertTrue(dock.act_group_tree.isChecked())
            self.assertFalse(dock.act_treemap.isChecked())
            self.assertFalse(dock.act_mindmap.isChecked())
            self.assertEqual(dock.stacked_widget.currentIndex(), 1)
            
            # Switch to Treemap
            with patch('dock_widget.QgsProject.instance') as mock_project_inst:
                mock_proj = MagicMock()
                mock_proj.mapLayers.return_value = {}
                mock_project_inst.return_value = mock_proj
                
                dock.switch_view(2)
                self.assertFalse(dock.act_physical_tree.isChecked())
                self.assertFalse(dock.act_group_tree.isChecked())
                self.assertTrue(dock.act_treemap.isChecked())
                self.assertFalse(dock.act_mindmap.isChecked())
                self.assertEqual(dock.stacked_widget.currentIndex(), 2)
                
            # Switch to Mindmap
            with patch('dock_widget.QgsProject.instance') as mock_project_inst:
                mock_proj = MagicMock()
                mock_proj.mapLayers.return_value = {}
                mock_project_inst.return_value = mock_proj
                
                dock.switch_view(3)
                self.assertFalse(dock.act_physical_tree.isChecked())
                self.assertFalse(dock.act_group_tree.isChecked())
                self.assertFalse(dock.act_treemap.isChecked())
                self.assertTrue(dock.act_mindmap.isChecked())
                self.assertEqual(dock.stacked_widget.currentIndex(), 3)

    def test_on_item_double_clicked(self):
        with patch('dock_widget.LayerTreeModel'), \
             patch('dock_widget.TreeMapWidget'):
            dock = TreeMapDockWidget(self.iface, self.parent)
            
            # Create a mock LayerItem
            mock_layer = MagicMock()
            mock_layer.id.return_value = "layer_id_123"
            
            from dock_widget import LayerItem
            mock_item = MagicMock(spec=LayerItem)
            mock_item.layer = mock_layer
            
            dock.physical_model.itemFromIndex = MagicMock(return_value=mock_item)
            
            with patch('dock_widget.QgsProject.instance') as mock_project_inst:
                mock_proj = MagicMock()
                mock_proj.mapLayer.return_value = mock_layer
                mock_project_inst.return_value = mock_proj
                
                index = QModelIndex()
                # Test column 0
                index.column = MagicMock(return_value=0)
                dock.on_item_double_clicked(index)
                
                self.iface.setActiveLayer.assert_called_with(mock_layer)
                self.iface.zoomToActiveLayer.assert_called_once()

    def test_get_selected_layers(self):
        with patch('dock_widget.LayerTreeModel'), \
             patch('dock_widget.TreeMapWidget'):
            dock = TreeMapDockWidget(self.iface, self.parent)
            
            # Setup selection
            mock_view = MagicMock()
            idx1 = MagicMock()
            idx1.column.return_value = 0
            idx2 = MagicMock()
            idx2.column.return_value = 1 # Should be filtered out
            
            mock_view.selectionModel().selectedIndexes.return_value = [idx1, idx2]
            mock_view.model.return_value = dock.physical_model
            
            mock_layer = MagicMock()
            from dock_widget import LayerItem
            mock_item = MagicMock(spec=LayerItem)
            mock_item.layer = mock_layer
            dock.physical_model.itemFromIndex = MagicMock(side_effect=lambda idx: mock_item if idx == idx1 else None)
            
            layers = dock.get_selected_layers(mock_view)
            self.assertEqual(layers, [mock_layer])

    def test_view_configurations(self):
        with patch('dock_widget.LayerTreeModel'), \
             patch('dock_widget.TreeMapWidget'), \
             patch('dock_widget.MindMapView'):
            
            from dock_widget import QAbstractItemView
            dock = TreeMapDockWidget(self.iface, self.parent)
            
            # Check ExtendedSelection selection mode
            self.assertEqual(dock.physical_tree_view._selection_mode, QAbstractItemView.ExtendedSelection)
            self.assertEqual(dock.group_tree_view._selection_mode, QAbstractItemView.ExtendedSelection)
            
            # Check alternatingRowColors
            self.assertTrue(dock.physical_tree_view._alternating_row_colors)
            self.assertTrue(dock.group_tree_view._alternating_row_colors)
            
            # Check QActionGroup
            self.assertIsNotNone(dock.view_group)
            self.assertTrue(dock.view_group._exclusive)
            self.assertIn(dock.act_physical_tree, dock.view_group._actions)
            self.assertIn(dock.act_group_tree, dock.view_group._actions)
            self.assertIn(dock.act_treemap, dock.view_group._actions)
            self.assertIn(dock.act_mindmap, dock.view_group._actions)

    def test_context_menu_actions_for_raster_vs_vector(self):
        with patch('dock_widget.LayerTreeModel'), \
             patch('dock_widget.TreeMapWidget'):
            
            dock = TreeMapDockWidget(self.iface, self.parent)
            
            from dock_widget import QgsVectorLayer, QgsRasterLayer, QMenu
            
            # 1. Vector layer
            vector_layer = MagicMock(spec=QgsVectorLayer)
            vector_layer.isEditable.return_value = False
            vector_layer.name.return_value = "Vector"
            
            # We can mock QMenu and see what's added to edit_menu
            mock_menu = MagicMock(spec=QMenu)
            mock_edit_menu = MagicMock(spec=QMenu)
            mock_menu.addMenu.return_value = mock_edit_menu
            
            with patch('dock_widget.QMenu', return_value=mock_menu):
                dock._create_layer_context_menu([vector_layer], None)
                
                # Check that edit submenu had Toggle Editing and Open Attribute Table added
                added_edit_actions = [c[0][0] for c in mock_edit_menu.addAction.call_args_list]
                self.assertIn("开始编辑", added_edit_actions)
                self.assertIn("打开属性表", added_edit_actions)
                
            # 2. Raster layer
            raster_layer = MagicMock(spec=QgsRasterLayer)
            raster_layer.name.return_value = "Raster"
            
            mock_menu_raster = MagicMock(spec=QMenu)
            mock_edit_menu_raster = MagicMock(spec=QMenu)
            mock_menu_raster.addMenu.return_value = mock_edit_menu_raster
            
            with patch('dock_widget.QMenu', return_value=mock_menu_raster):
                dock._create_layer_context_menu([raster_layer], None)
                
                # Check that edit submenu did NOT have Toggle Editing and Open Attribute Table added
                added_edit_actions_raster = [c[0][0] for c in mock_edit_menu_raster.addAction.call_args_list]
                self.assertNotIn("开始编辑", added_edit_actions_raster)
                self.assertNotIn("停止编辑", added_edit_actions_raster)
                self.assertNotIn("打开属性表", added_edit_actions_raster)

    def test_action_copy_with_style_success(self):
        with patch('dock_widget.LayerTreeModel'), \
             patch('dock_widget.TreeMapWidget'), \
             patch('dock_widget.QFileDialog.getExistingDirectory', return_value="/mock/target/dir"), \
             patch('dock_widget.safe_copy') as mock_safe_copy, \
             patch('dock_widget.QgsProject.instance') as mock_proj_inst:
            
            mock_proj = MagicMock()
            mock_proj_inst.return_value = mock_proj
            
            dock = TreeMapDockWidget(self.iface, self.parent)
            
            # Setup layer
            from dock_widget import QgsVectorLayer
            mock_layer = MagicMock(spec=QgsVectorLayer)
            mock_layer.source.return_value = "/mock/source/file.shp"
            mock_layer.name.return_value = "MyLayer"
            mock_layer.dataProvider().name.return_value = "ogr"
            
            # Trigger
            dock.action_copy_with_style(mock_layer)
            
            mock_safe_copy.assert_called_once_with("/mock/source/file.shp", "/mock/target/dir")
            mock_proj.addMapLayer.assert_called_once()
            added_layer = mock_proj.addMapLayer.call_args[0][0]
            self.assertTrue(isinstance(added_layer, QgsVectorLayer))
            self.assertEqual(added_layer.name(), "MyLayer (复制)")

    def test_action_copy_with_style_exception(self):
        with patch('dock_widget.LayerTreeModel'), \
             patch('dock_widget.TreeMapWidget'), \
             patch('dock_widget.QFileDialog.getExistingDirectory', return_value="/mock/target/dir"), \
             patch('dock_widget.safe_copy', side_effect=Exception("Disk Full")), \
             patch('dock_widget.QMessageBox.warning') as mock_warning:
             
            dock = TreeMapDockWidget(self.iface, self.parent)
            
            from dock_widget import QgsVectorLayer
            mock_layer = MagicMock(spec=QgsVectorLayer)
            mock_layer.source.return_value = "/mock/source/file.shp"
            
            dock.action_copy_with_style(mock_layer)
            
            mock_warning.assert_called_once_with(
                dock, "操作失败", "复制并应用样式失败: Disk Full"
            )

    def test_action_rename_file_success(self):
        with patch('dock_widget.LayerTreeModel'), \
             patch('dock_widget.TreeMapWidget'), \
             patch('dock_widget.QInputDialog.getText', return_value=("new_name.shp", True)), \
             patch('dock_widget.safe_rename') as mock_safe_rename:
             
            dock = TreeMapDockWidget(self.iface, self.parent)
            
            from dock_widget import QgsVectorLayer
            mock_layer = MagicMock(spec=QgsVectorLayer)
            mock_layer.source.return_value = "/mock/source/file.shp"
            
            dock.action_rename_file(mock_layer)
            
            mock_safe_rename.assert_called_once_with(mock_layer, "new_name.shp")

    def test_action_rename_file_exception(self):
        with patch('dock_widget.LayerTreeModel'), \
             patch('dock_widget.TreeMapWidget'), \
             patch('dock_widget.QInputDialog.getText', return_value=("new_name.shp", True)), \
             patch('dock_widget.safe_rename', side_effect=Exception("Permission Denied")), \
             patch('dock_widget.QMessageBox.warning') as mock_warning:
             
            dock = TreeMapDockWidget(self.iface, self.parent)
            
            from dock_widget import QgsVectorLayer
            mock_layer = MagicMock(spec=QgsVectorLayer)
            mock_layer.source.return_value = "/mock/source/file.shp"
            
            dock.action_rename_file(mock_layer)
            
            mock_warning.assert_called_once_with(
                dock, "操作失败", "重命名文件失败: Permission Denied"
            )

    def test_action_move_files_success(self):
        with patch('dock_widget.LayerTreeModel'), \
             patch('dock_widget.TreeMapWidget'), \
             patch('dock_widget.QFileDialog.getExistingDirectory', return_value="/mock/target/dir"), \
             patch('dock_widget.safe_move') as mock_safe_move:
             
            dock = TreeMapDockWidget(self.iface, self.parent)
            
            from dock_widget import QgsVectorLayer
            mock_layer1 = MagicMock(spec=QgsVectorLayer)
            mock_layer1.source.return_value = "/mock/source/file1.shp"
            mock_layer2 = MagicMock(spec=QgsVectorLayer)
            mock_layer2.source.return_value = "/mock/source/file2.shp"
            
            dock.action_move_files([mock_layer1, mock_layer2])
            
            self.assertEqual(mock_safe_move.call_count, 2)
            mock_safe_move.assert_any_call(mock_layer1, "/mock/target/dir")
            mock_safe_move.assert_any_call(mock_layer2, "/mock/target/dir")

    def test_action_move_files_exception(self):
        with patch('dock_widget.LayerTreeModel'), \
             patch('dock_widget.TreeMapWidget'), \
             patch('dock_widget.QFileDialog.getExistingDirectory', return_value="/mock/target/dir"), \
             patch('dock_widget.safe_move', side_effect=Exception("Access Denied")), \
             patch('dock_widget.QMessageBox.warning') as mock_warning:
             
            dock = TreeMapDockWidget(self.iface, self.parent)
            
            from dock_widget import QgsVectorLayer
            mock_layer = MagicMock(spec=QgsVectorLayer)
            mock_layer.source.return_value = "/mock/source/file.shp"
            
            dock.action_move_files([mock_layer])
            
            mock_warning.assert_called_once_with(
                dock, "操作失败", "移动文件失败: Access Denied"
            )

    def test_action_change_datasource_success(self):
        with patch('dock_widget.LayerTreeModel'), \
             patch('dock_widget.TreeMapWidget'), \
             patch('dock_widget.QFileDialog.getOpenFileName', return_value=("/new/source/path.shp", "shp")), \
             patch('dock_widget.update_layer_source') as mock_update:
             
            dock = TreeMapDockWidget(self.iface, self.parent)
            
            from dock_widget import QgsVectorLayer
            mock_layer = MagicMock(spec=QgsVectorLayer)
            mock_layer.source.return_value = "/mock/source/file.shp"
            
            dock.action_change_datasource(mock_layer)
            
            mock_update.assert_called_once_with(mock_layer, "/new/source/path.shp")

    def test_action_change_datasource_exception(self):
        with patch('dock_widget.LayerTreeModel'), \
             patch('dock_widget.TreeMapWidget'), \
             patch('dock_widget.QFileDialog.getOpenFileName', return_value=("/new/source/path.shp", "shp")), \
             patch('dock_widget.update_layer_source', side_effect=Exception("Invalid file")), \
             patch('dock_widget.QMessageBox.warning') as mock_warning:
             
            dock = TreeMapDockWidget(self.iface, self.parent)
            
            from dock_widget import QgsVectorLayer
            mock_layer = MagicMock(spec=QgsVectorLayer)
            mock_layer.source.return_value = "/mock/source/file.shp"
            
            dock.action_change_datasource(mock_layer)
            
            mock_warning.assert_called_once_with(
                dock, "操作失败", "更换数据源失败: Invalid file"
            )

    def test_on_item_changed(self):
        with patch('dock_widget.LayerTreeModel'), \
             patch('dock_widget.TreeMapWidget'), \
             patch('dock_widget.QgsProject.instance') as mock_proj_inst:
             
            dock = TreeMapDockWidget(self.iface, self.parent)
            dock._is_refreshing = False
            
            from dock_widget import LayerItem, Qt
            mock_layer = MagicMock()
            mock_layer.name.return_value = "Old Name"
            
            # Since isinstance check relies on the actual class, we instantiate a real LayerItem
            real_layer_item = LayerItem(mock_layer, "New Name")
            
            with patch.object(dock, 'refresh') as mock_refresh:
                dock.on_item_changed(real_layer_item)
                mock_layer.setName.assert_called_once_with("New Name")
                mock_refresh.assert_called_once()
                
            # Test FolderItem (virtual group) rename
            from dock_widget import FolderItem
            real_group_item = FolderItem("Old Group Name", is_physical=False)
            real_group_item.setText("New Group Name")
            real_group_item.setData("Old Group Name", Qt.UserRole)
            
            mock_proj = MagicMock()
            mock_root = MagicMock()
            mock_group_node = MagicMock()
            mock_root.findGroup.return_value = mock_group_node
            mock_proj.layerTreeRoot.return_value = mock_root
            mock_proj_inst.return_value = mock_proj
            
            with patch.object(dock, 'refresh') as mock_refresh:
                dock.on_item_changed(real_group_item)
                mock_root.findGroup.assert_called_once_with("Old Group Name")
                mock_group_node.setName.assert_called_once_with("New Group Name")
                mock_refresh.assert_called_once()
                self.assertEqual(real_group_item.data(Qt.UserRole), "New Group Name")

    def test_handle_layer_relocation_editable_blocked(self):
        with patch('dock_widget.LayerTreeModel'), \
             patch('dock_widget.TreeMapWidget'), \
             patch('dock_widget.QMessageBox.warning') as mock_warning:
            
            dock = TreeMapDockWidget(self.iface, self.parent)
            
            mock_layer = MagicMock()
            mock_layer.name.return_value = "editable_layer"
            mock_layer.isEditable.return_value = True
            
            mock_proj = MagicMock()
            mock_proj.mapLayer.return_value = mock_layer
            
            with patch('dock_widget.QgsProject.instance', return_value=mock_proj):
                dock.handle_layer_relocation("layer_123", "/target/path")
                
            mock_warning.assert_called_once()
            self.assertIn("处于编辑状态", mock_warning.call_args[0][2])

    def test_handle_layer_relocation_success(self):
        import tempfile
        import shutil
        temp_dir = tempfile.mkdtemp()
        shp_file = os.path.join(temp_dir, "reloc.shp")
        open(shp_file, 'w').close()
        
        try:
            from dock_widget import QMessageBox
            with patch('dock_widget.LayerTreeModel'), \
                 patch('dock_widget.TreeMapWidget'), \
                 patch('dock_widget.QMessageBox.question', return_value=QMessageBox.Yes), \
                 patch('dock_widget.QMessageBox.information') as mock_info, \
                 patch('dock_widget.safe_move', return_value=True) as mock_safe_move, \
                 patch('dock_widget.QgsProject.instance') as mock_proj_inst:
                
                dock = TreeMapDockWidget(self.iface, self.parent)
                
                mock_layer = MagicMock()
                mock_layer.name.return_value = "reloc_layer"
                mock_layer.isEditable.return_value = False
                mock_layer.source.return_value = shp_file
                
                mock_proj = MagicMock()
                mock_proj.mapLayer.return_value = mock_layer
                mock_proj_inst.return_value = mock_proj
                
                with patch('dock_widget.get_associated_files', return_value=[shp_file]), \
                     patch.object(dock, 'refresh') as mock_refresh:
                     
                    dock.handle_layer_relocation("layer_123", temp_dir + "_target")
                    
                mock_safe_move.assert_called_once_with(mock_layer, temp_dir + "_target")
                mock_refresh.assert_called_once()
                mock_info.assert_called_once()
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)
            shutil.rmtree(temp_dir + "_target", ignore_errors=True)

    def test_refresh_expands_tree_views(self):
        with patch('dock_widget.LayerTreeModel'), \
             patch('dock_widget.TreeMapWidget'):
            dock = TreeMapDockWidget(self.iface, self.parent)
            
            # Mock expand/collapse methods
            dock.physical_tree_view.expandAll = MagicMock()
            dock.group_tree_view.collapseAll = MagicMock()
            
            # Call refresh
            dock.refresh()
            
            # Verify correct states were applied
            dock.physical_tree_view.expandAll.assert_called_once()
            dock.group_tree_view.collapseAll.assert_called_once()

    def test_update_filter_tags_dynamic_rebuild(self):
        with patch('dock_widget.LayerTreeModel'), \
             patch('dock_widget.TreeMapWidget'), \
             patch('dock_widget.QgsProject.instance') as mock_proj_inst:
            
            dock = TreeMapDockWidget(self.iface, self.parent)
            
            mock_layer1 = MagicMock()
            mock_layer1.source.return_value = "/path/to/layer1.shp"
            mock_layer2 = MagicMock()
            mock_layer2.source.return_value = "/path/to/layer2.tif"
            
            mock_proj = MagicMock()
            mock_proj.mapLayers.return_value = {"l1": mock_layer1, "l2": mock_layer2}
            mock_proj_inst.return_value = mock_proj
            
            dock.update_filter_tags()
            
            self.assertIn("SHP", dock.filter_buttons)
            self.assertIn("TIF", dock.filter_buttons)
            self.assertIn("全部", dock.filter_buttons)

    def test_set_filter_format_refresh(self):
        with patch('dock_widget.LayerTreeModel'), \
             patch('dock_widget.TreeMapWidget'):
            
            dock = TreeMapDockWidget(self.iface, self.parent)
            
            with patch.object(dock, 'refresh') as mock_refresh:
                dock.set_filter_format("SHP")
                self.assertEqual(dock.current_filter_format, "SHP")
                mock_refresh.assert_called_once()

    def test_action_open_containing_folder(self):
        with patch('dock_widget.LayerTreeModel'), \
             patch('dock_widget.TreeMapWidget'):
            
            dock = TreeMapDockWidget(self.iface, self.parent)
            
            mock_layer = MagicMock()
            mock_layer.source.return_value = "/nonexistent/test.shp"
            
            with patch('dock_widget.QMessageBox.warning') as mock_warn:
                dock.action_open_containing_folder(mock_layer)
                mock_warn.assert_called_once()
                
            with patch('os.path.exists', return_value=True), \
                 patch('subprocess.Popen') as mock_popen, \
                 patch('os.name', 'nt'):
                dock.action_open_containing_folder(mock_layer)
                mock_popen.assert_called_once()

    def test_create_folder_context_menu(self):
        with patch('dock_widget.LayerTreeModel'), \
             patch('dock_widget.TreeMapWidget'):
            dock = TreeMapDockWidget(self.iface, self.parent)
            
            with patch('dock_widget.QMenu') as mock_menu_cls, \
                 patch('os.path.exists', return_value=True), \
                 patch('subprocess.Popen') as mock_popen, \
                 patch('os.name', 'nt'):
                 
                mock_menu = MagicMock()
                mock_menu_cls.return_value = mock_menu
                
                mock_action = MagicMock()
                mock_menu.addAction.return_value = mock_action
                
                def mock_triggered_connect(callback):
                    callback()
                mock_action.triggered.connect = mock_triggered_connect
                
                with patch('os.path.isdir', return_value=True):
                    dock._create_folder_context_menu("/some/physical/dir", MagicMock())
                    mock_popen.assert_called_with('explorer.exe "\\some\\physical\\dir"')

if __name__ == '__main__':
    unittest.main()
