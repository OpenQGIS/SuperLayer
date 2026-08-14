import unittest
from unittest.mock import MagicMock, patch
import os
import tempfile
import shutil

# Make sure it can load in testing environment
import dock_widget
from dock_widget import SuperLayerDockWidget, QModelIndex, QMenu

class TestDockWidget(unittest.TestCase):
    def setUp(self):
        self.iface = MagicMock()
        self.parent = MagicMock()
        
        # Mock active canvas/layer methods
        self.canvas = MagicMock()
        self.iface.mapCanvas.return_value = self.canvas
        
    def test_dock_widget_init(self):
        with patch('dock_widget.LayerTreeModel') as mock_model_cls, \
             patch('dock_widget.LayerOrderTreeModel') as group_model_cls, \
             patch('dock_widget.TreeMapWidget') as mock_treemap_cls, \
             patch('dock_widget.MindMapView') as mock_mindmap_cls:
            
            mock_model = MagicMock()
            mock_model_cls.return_value = mock_model
            group_model = MagicMock()
            group_model_cls.return_value = group_model
            mock_treemap = MagicMock()
            mock_treemap_cls.return_value = mock_treemap
            mock_mindmap = MagicMock()
            mock_mindmap_cls.return_value = mock_mindmap
            
            dock = SuperLayerDockWidget(self.iface, self.parent)
            self.assertEqual(dock.iface, self.iface)
            self.assertTrue(dock.group_by_physical)
            
            # Verify views initialization
            self.assertIsNotNone(dock.physical_tree_view)
            self.assertIsNotNone(dock.group_tree_view)
            self.assertIsNotNone(dock.treemap_view)
            self.assertIsNotNone(dock.mindmap_view)
            self.assertEqual(dock.physical_model, mock_model)
            self.assertEqual(dock.group_model, group_model)

    def test_switch_view(self):
        with patch('dock_widget.LayerTreeModel'), \
             patch('dock_widget.TreeMapWidget'), \
             patch('dock_widget.MindMapView'):
            dock = SuperLayerDockWidget(self.iface, self.parent)
            
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
            dock = SuperLayerDockWidget(self.iface, self.parent)
            
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
                self.iface.zoomToActiveLayer.assert_not_called()

    def test_get_selected_layers(self):
        with patch('dock_widget.LayerTreeModel'), \
             patch('dock_widget.TreeMapWidget'):
            dock = SuperLayerDockWidget(self.iface, self.parent)
            
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
            dock = SuperLayerDockWidget(self.iface, self.parent)
            
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
            
            dock = SuperLayerDockWidget(self.iface, self.parent)
            
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

            # 3. Memory (Temporary) layer
            memory_layer = MagicMock(spec=QgsVectorLayer)
            memory_layer.isEditable.return_value = False
            memory_layer.name.return_value = "MemoryVector"
            mock_provider = MagicMock()
            mock_provider.name.return_value = "memory"
            memory_layer.dataProvider.return_value = mock_provider

            mock_menu_mem = MagicMock(spec=QMenu)
            mock_edit_menu_mem = MagicMock(spec=QMenu)
            mock_menu_mem.addMenu.return_value = mock_edit_menu_mem

            with patch('dock_widget.QMenu', return_value=mock_menu_mem):
                dock._create_layer_context_menu([memory_layer], None)

                # Check top-level menu items added for memory layer
                top_level_actions = [c[0][0] for c in mock_menu_mem.addAction.call_args_list]
                self.assertIn("缩放到图层", top_level_actions)
                self.assertIn("保存临时图层", top_level_actions)
                # Verify non-temporary actions like "更换数据源" are not in there
                self.assertNotIn("更换数据源", top_level_actions)
                self.assertNotIn("打开文件位置", top_level_actions)
                self.assertNotIn("删除图层", top_level_actions)

                # Check edit menu items for memory layer
                added_edit_actions_mem = [c[0][0] for c in mock_edit_menu_mem.addAction.call_args_list]
                self.assertIn("开始编辑", added_edit_actions_mem)
                self.assertIn("重命名图层", added_edit_actions_mem)
                self.assertIn("打开属性表", added_edit_actions_mem)
                self.assertIn("打开图层属性", added_edit_actions_mem)
                # Verify "重命名文件" is NOT in the memory layer's edit menu
                self.assertNotIn("重命名文件", added_edit_actions_mem)

            # 4. Multiple Memory (Temporary) layers
            mem_layer1 = MagicMock(spec=QgsVectorLayer)
            mock_prov1 = MagicMock()
            mock_prov1.name.return_value = "memory"
            mem_layer1.dataProvider.return_value = mock_prov1

            mem_layer2 = MagicMock(spec=QgsVectorLayer)
            mock_prov2 = MagicMock()
            mock_prov2.name.return_value = "memory"
            mem_layer2.dataProvider.return_value = mock_prov2

            mock_menu_multi_mem = MagicMock(spec=QMenu)
            with patch('dock_widget.QMenu', return_value=mock_menu_multi_mem):
                dock._create_layer_context_menu([mem_layer1, mem_layer2], None)

                # Check top-level menu items added for multiple memory layers
                actions = [c[0][0] for c in mock_menu_multi_mem.addAction.call_args_list]
                self.assertIn("缩放到…", actions)
                self.assertIn("保存临时图层到…", actions)
                self.assertIn("删除选中图层", actions)
                # Verify physical/regular multi-select options are not there
                self.assertNotIn("移动选中的 2 个文件到…", actions)
                self.assertNotIn("复制选中的 2 个文件到…", actions)

    def test_action_copy_with_style_success(self):
        with patch('dock_widget.LayerTreeModel'), \
             patch('dock_widget.TreeMapWidget'), \
             patch('dock_widget.QFileDialog.getExistingDirectory', return_value="/mock/target/dir"), \
             patch('dock_widget.safe_copy') as mock_safe_copy, \
             patch('dock_widget.QgsMapLayerStyle') as mock_style_class, \
             patch('dock_widget.QgsProject.instance') as mock_proj_inst:
            
            mock_proj = MagicMock()
            mock_proj_inst.return_value = mock_proj
            
            dock = SuperLayerDockWidget(self.iface, self.parent)
            
            # Setup layer
            from dock_widget import QgsVectorLayer
            mock_layer = MagicMock(spec=QgsVectorLayer)
            mock_layer.source.return_value = "/mock/source/file.shp"
            mock_layer.name.return_value = "MyLayer"
            mock_layer.dataProvider().name.return_value = "ogr"
            mock_layer.subsetString.return_value = '"status" = 1'
            
            # Trigger
            dock.action_copy_with_style(mock_layer)
            
            mock_safe_copy.assert_called_once_with("/mock/source/file.shp", "/mock/target/dir")
            mock_proj.addMapLayer.assert_called_once()
            added_layer = mock_proj.addMapLayer.call_args[0][0]
            self.assertTrue(isinstance(added_layer, QgsVectorLayer))
            self.assertEqual(added_layer.name(), "MyLayer (复制)")
            mock_style = mock_style_class.return_value
            mock_style.readFromLayer.assert_called_once_with(mock_layer)
            mock_style.writeToLayer.assert_called_once_with(added_layer)
            self.assertEqual(added_layer.subsetString(), '"status" = 1')

    def test_action_copy_with_style_exception(self):
        with patch('dock_widget.LayerTreeModel'), \
             patch('dock_widget.TreeMapWidget'), \
             patch('dock_widget.QFileDialog.getExistingDirectory', return_value="/mock/target/dir"), \
             patch('dock_widget.safe_copy', side_effect=Exception("Disk Full")), \
             patch('dock_widget.QMessageBox.warning') as mock_warning:
             
            dock = SuperLayerDockWidget(self.iface, self.parent)
            
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
             
            dock = SuperLayerDockWidget(self.iface, self.parent)
            
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
             
            dock = SuperLayerDockWidget(self.iface, self.parent)
            
            from dock_widget import QgsVectorLayer
            mock_layer = MagicMock(spec=QgsVectorLayer)
            mock_layer.source.return_value = "/mock/source/file.shp"
            
            dock.action_rename_file(mock_layer)
            
            mock_warning.assert_called_once_with(
                dock, "操作失败", "重命名文件失败: Permission Denied"
            )

    def test_action_rename_parent_dir_success(self):
        with patch('dock_widget.LayerTreeModel'), \
             patch('dock_widget.TreeMapWidget'), \
             patch('dock_widget.QInputDialog.getText', return_value=("new_parent", True)), \
             patch('dock_widget.safe_rename_parent_dir') as mock_safe_rename_parent_dir:
             
            dock = SuperLayerDockWidget(self.iface, self.parent)
            
            from dock_widget import QgsVectorLayer
            mock_layer = MagicMock(spec=QgsVectorLayer)
            mock_layer.source.return_value = "/mock/source/file.shp"
            
            dock.action_rename_parent_dir(mock_layer)
            
            mock_safe_rename_parent_dir.assert_called_once_with(mock_layer, "new_parent")

    def test_action_rename_parent_dir_exception(self):
        with patch('dock_widget.LayerTreeModel'), \
             patch('dock_widget.TreeMapWidget'), \
             patch('dock_widget.QInputDialog.getText', return_value=("new_parent", True)), \
             patch('dock_widget.safe_rename_parent_dir', side_effect=Exception("Locked")), \
             patch('dock_widget.QMessageBox.warning') as mock_warning:
             
            dock = SuperLayerDockWidget(self.iface, self.parent)
            
            from dock_widget import QgsVectorLayer
            mock_layer = MagicMock(spec=QgsVectorLayer)
            mock_layer.source.return_value = "/mock/source/file.shp"
            
            dock.action_rename_parent_dir(mock_layer)
            
            mock_warning.assert_called_once_with(
                dock, "操作失败", "重命名父文件夹名失败: Locked"
            )

    def test_action_move_files_success(self):
        with patch('dock_widget.LayerTreeModel'), \
             patch('dock_widget.TreeMapWidget'), \
             patch('dock_widget.QFileDialog.getExistingDirectory', return_value="/mock/target/dir"), \
             patch('dock_widget.safe_move') as mock_safe_move:
             
            dock = SuperLayerDockWidget(self.iface, self.parent)
            
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
             
            dock = SuperLayerDockWidget(self.iface, self.parent)
            
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
             
            dock = SuperLayerDockWidget(self.iface, self.parent)
            
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
             
            dock = SuperLayerDockWidget(self.iface, self.parent)
            
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
             
            dock = SuperLayerDockWidget(self.iface, self.parent)
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
            
            dock = SuperLayerDockWidget(self.iface, self.parent)
            
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
                
                dock = SuperLayerDockWidget(self.iface, self.parent)
                
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

    def test_handle_layer_relocation_copy(self):
        import tempfile
        import shutil
        temp_dir = tempfile.mkdtemp()
        shp_file = os.path.join(temp_dir, "reloc_copy.shp")
        open(shp_file, 'w').close()
        
        try:
            with patch('dock_widget.LayerTreeModel'), \
                 patch('dock_widget.TreeMapWidget'), \
                 patch('dock_widget.QMessageBox') as mock_qmsg_box_class, \
                 patch('dock_widget.safe_copy') as mock_safe_copy, \
                 patch('dock_widget.QgsProject.instance') as mock_proj_inst:
                 
                # Setup mock QMessageBox behavior
                mock_msgbox = MagicMock()
                mock_qmsg_box_class.return_value = mock_msgbox
                
                # Mock buttons
                btn_copy = MagicMock()
                from dock_widget import tr
                def add_button_mock(text, role):
                    if text == tr("复制"):
                        return btn_copy
                    return MagicMock()
                mock_msgbox.addButton.side_effect = add_button_mock
                mock_msgbox.clickedButton.return_value = btn_copy
                
                dock = SuperLayerDockWidget(self.iface, self.parent)
                
                mock_layer = MagicMock()
                mock_layer.__class__.__name__ = "QgsVectorLayer"
                mock_layer.name.return_value = "reloc_layer"
                mock_layer.isEditable.return_value = False
                mock_layer.source.return_value = shp_file
                mock_layer.dataProvider().name.return_value = "ogr"
                
                mock_proj = MagicMock()
                mock_proj.mapLayer.return_value = mock_layer
                mock_proj_inst.return_value = mock_proj
                
                with patch('dock_widget.get_associated_files', return_value=[shp_file]), \
                     patch.object(dock, 'refresh') as mock_refresh:
                     
                    dock.handle_layer_relocation("layer_123", temp_dir + "_target")
                    
                mock_safe_copy.assert_called_once_with(shp_file, temp_dir + "_target")
                mock_refresh.assert_called_once()
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)
            shutil.rmtree(temp_dir + "_target", ignore_errors=True)

    def test_handle_layer_relocation_backup(self):
        import tempfile
        import shutil
        temp_dir = tempfile.mkdtemp()
        shp_file = os.path.join(temp_dir, "reloc_backup.shp")
        open(shp_file, 'w').close()
        
        try:
            with patch('dock_widget.LayerTreeModel'), \
                 patch('dock_widget.TreeMapWidget'), \
                 patch('dock_widget.QMessageBox') as mock_qmsg_box_class, \
                 patch('dock_widget.safe_copy') as mock_safe_copy, \
                 patch('dock_widget.QgsProject.instance') as mock_proj_inst:
                 
                # Setup mock QMessageBox behavior
                mock_msgbox = MagicMock()
                mock_qmsg_box_class.return_value = mock_msgbox
                
                # Mock buttons
                btn_backup = MagicMock()
                from dock_widget import tr
                def add_button_mock(text, role):
                    if text == tr("备份"):
                        return btn_backup
                    return MagicMock()
                mock_msgbox.addButton.side_effect = add_button_mock
                mock_msgbox.clickedButton.return_value = btn_backup
                
                dock = SuperLayerDockWidget(self.iface, self.parent)
                
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
                    
                mock_safe_copy.assert_called_once_with(shp_file, temp_dir + "_target")
                mock_refresh.assert_called_once()
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)
            shutil.rmtree(temp_dir + "_target", ignore_errors=True)

    def test_handle_folder_relocation_success(self):
        from dock_widget import QMessageBox
        def exists_side_effect(path):
            norm_path = path.replace('\\', '/')
            if norm_path in ["/some/source/dir", "/some/target/dir"]:
                return True
            return False
        with patch('dock_widget.LayerTreeModel'), \
             patch('dock_widget.TreeMapWidget'), \
             patch('dock_widget.QMessageBox.question', return_value=QMessageBox.Yes), \
             patch('dock_widget.QMessageBox.information') as mock_info, \
             patch('dock_widget.safe_migrate_dir', return_value=True) as mock_migrate, \
             patch('os.path.exists', side_effect=exists_side_effect), \
             patch('os.path.isdir', return_value=True):
             
            dock = SuperLayerDockWidget(self.iface, self.parent)
            
            with patch.object(dock, 'refresh') as mock_refresh:
                dock.handle_folder_relocation("/some/source/dir", "/some/target/dir")
                
            mock_migrate.assert_called_once_with(os.path.normpath("/some/source/dir"), os.path.normpath("/some/target/dir"))
            mock_refresh.assert_called_once()
            mock_info.assert_called_once()

    def test_handle_folder_relocation_self_nested(self):
        def exists_side_effect(path):
            norm_path = path.replace('\\', '/')
            if norm_path in ["/some/source/dir", "/some/source/dir/sub"]:
                return True
            return False
        with patch('dock_widget.LayerTreeModel'), \
             patch('dock_widget.TreeMapWidget'), \
             patch('dock_widget.QMessageBox.warning') as mock_warning, \
             patch('os.path.exists', side_effect=exists_side_effect), \
             patch('os.path.isdir', return_value=True):
             
            dock = SuperLayerDockWidget(self.iface, self.parent)
            
            dock.handle_folder_relocation("/some/source/dir", "/some/source/dir/sub")
            mock_warning.assert_called_once()
            self.assertIn("不能将文件夹移动到自身", mock_warning.call_args[0][2])

    def test_refresh_expands_tree_views(self):
        with patch('dock_widget.LayerTreeModel'), \
             patch('dock_widget.TreeMapWidget'):
            dock = SuperLayerDockWidget(self.iface, self.parent)
            
            # Mock expand/collapse methods
            dock.physical_tree_view.expandAll = MagicMock()
            dock.group_tree_view.collapseAll = MagicMock()
            
            # Call refresh
            dock.refresh()
            
            # Verify correct states were applied
            dock.physical_tree_view.expandAll.assert_called_once()
            dock.group_tree_view.collapseAll.assert_not_called()

    def test_update_filter_tags_dynamic_rebuild(self):
        with patch('dock_widget.LayerTreeModel'), \
             patch('dock_widget.TreeMapWidget'), \
             patch('dock_widget.QgsProject.instance') as mock_proj_inst:
            
            dock = SuperLayerDockWidget(self.iface, self.parent)
            
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
            
            dock = SuperLayerDockWidget(self.iface, self.parent)
            
            with patch.object(dock, 'refresh') as mock_refresh:
                dock.set_filter_format("SHP")
                self.assertEqual(dock.current_filter_format, "SHP")
                mock_refresh.assert_called_once()

    def test_action_open_containing_folder(self):
        with patch('dock_widget.LayerTreeModel'), \
             patch('dock_widget.TreeMapWidget'):
            
            dock = SuperLayerDockWidget(self.iface, self.parent)
            
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
            dock = SuperLayerDockWidget(self.iface, self.parent)
            
            with patch('dock_widget.QMenu') as mock_menu_cls, \
                 patch('os.path.exists', return_value=True), \
                 patch('subprocess.Popen') as mock_popen, \
                 patch('dock_widget.QInputDialog.getText', return_value=("new_dir", True)), \
                 patch('dock_widget.safe_rename_dir') as mock_rename_dir, \
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
                    explorer_path = os.path.join(os.environ.get('SystemRoot', 'C:\\Windows'), 'explorer.exe')
                    mock_popen.assert_called_with([explorer_path, '\\some\\physical\\dir'])

    def test_switch_view_layer_board(self):
        with patch('dock_widget.LayerTreeModel'), \
             patch('dock_widget.TreeMapWidget'), \
             patch('dock_widget.MindMapView'), \
             patch('dock_widget.LayerBoardWidget') as mock_lb_cls:
            
            mock_lb = MagicMock()
            mock_lb_cls.return_value = mock_lb
            
            dock = SuperLayerDockWidget(self.iface, self.parent)
            
            # Reset mock to clear calls during initialization/refresh inside init
            mock_lb.reset_mock()
            
            # Switch to Attribute Board (index 4)
            dock.switch_view(4)
            self.assertTrue(dock.act_layer_board.isChecked())
            self.assertEqual(dock.stacked_widget.currentIndex(), 4)
            mock_lb.populateLayerTable.assert_any_call('vector')
            mock_lb.populateLayerTable.assert_any_call('raster')
            mock_lb.populateAvailableEncodingList.assert_called_once()
            
            # Reset mock and test running refresh when active
            mock_lb.reset_mock()
            dock.refresh()
            mock_lb.populateLayerTable.assert_any_call('vector')
            mock_lb.populateLayerTable.assert_any_call('raster')
            mock_lb.populateAvailableEncodingList.assert_called_once()

    def test_setup_toolbar_icons_and_labels(self):
        with patch('dock_widget.LayerTreeModel'), \
             patch('dock_widget.TreeMapWidget'), \
             patch('dock_widget.MindMapView'):
            dock = SuperLayerDockWidget(self.iface, self.parent)
            
            # Verify the updated text labels
            self.assertEqual(dock.act_physical_tree.text(), "文件夹分类")
            self.assertEqual(dock.act_group_tree.text(), "图层分类")
            self.assertEqual(dock.act_treemap.text(), "矩形树状图")
            self.assertEqual(dock.act_mindmap.text(), "路径导图")
            self.assertEqual(dock.act_layer_board.text(), "批量修改")
            self.assertEqual(dock.act_refresh.text(), "刷新")
            
            # Verify icons are loaded/created
            self.assertIsNotNone(dock.act_physical_tree._icon)
            self.assertIsNotNone(dock.act_group_tree._icon)
            self.assertIsNotNone(dock.act_treemap._icon)
            self.assertIsNotNone(dock.act_mindmap._icon)
            self.assertIsNotNone(dock.act_layer_board._icon)
            self.assertIsNotNone(dock.act_refresh._icon)

    def test_physical_tree_context_menu_column2(self):
        with patch('dock_widget.LayerTreeModel'), \
             patch('dock_widget.TreeMapWidget'):
            dock = SuperLayerDockWidget(self.iface, self.parent)
            
            # Setup mocks for physical tree view and model
            mock_view = MagicMock()
            dock.physical_tree_view = mock_view
            
            mock_index = MagicMock()
            mock_index.isValid.return_value = True
            mock_index.row.return_value = 0
            mock_index.column.return_value = 2 # Column 2
            mock_view.indexAt.return_value = mock_index
            
            mock_model = MagicMock()
            mock_view.model.return_value = mock_model
            
            # Layer item at col 0
            mock_layer = MagicMock()
            mock_layer.source.return_value = "/nonexistent/test.shp"
            mock_item = MagicMock(spec=dock_widget.LayerItem)
            mock_item.layer = mock_layer
            mock_model.itemFromIndex.return_value = mock_item
            
            with patch.object(dock, '_create_folder_context_menu') as mock_create:
                with patch('os.path.exists', return_value=True):
                    dock.show_physical_tree_context_menu(MagicMock())
                    mock_create.assert_called_once()

    def test_action_backup_files_success(self):
        with patch('dock_widget.LayerTreeModel'), \
             patch('dock_widget.TreeMapWidget'), \
             patch('dock_widget.QFileDialog.getExistingDirectory', return_value="/mock/backup/dir"), \
             patch('dock_widget.safe_copy') as mock_safe_copy, \
             patch('dock_widget.QMessageBox.information') as mock_info:
            
            dock = SuperLayerDockWidget(self.iface, self.parent)
            mock_layer = MagicMock()
            mock_layer.source.return_value = "/mock/source.shp"
            
            dock.action_backup_files([mock_layer])
            mock_safe_copy.assert_called_once_with("/mock/source.shp", "/mock/backup/dir")
            mock_info.assert_called_once()

    def test_action_clear_default_style_success(self):
        with patch('dock_widget.LayerTreeModel'), \
             patch('dock_widget.TreeMapWidget'), \
             patch('dock_widget.resolve_physical_path', return_value="/mock/source.shp"), \
             patch('os.path.exists', return_value=True), \
             patch('os.remove') as mock_remove, \
             patch('dock_widget.QMessageBox.information') as mock_info:
            
            dock = SuperLayerDockWidget(self.iface, self.parent)
            mock_layer = MagicMock()
            mock_layer.source.return_value = "/mock/source.shp"
            mock_style_manager = MagicMock()
            mock_layer.styleManager.return_value = mock_style_manager
            mock_layer.geometryType.return_value = 1
            
            dock.action_clear_default_style(mock_layer)
            mock_remove.assert_called_once_with("/mock/source.qml")
            mock_style_manager.reset.assert_called_once()
            mock_info.assert_called_once()

    def test_action_save_as_default_style_success(self):
        with patch('dock_widget.LayerTreeModel'), \
             patch('dock_widget.TreeMapWidget'), \
             patch('dock_widget.QMessageBox.information') as mock_info:
            
            dock = SuperLayerDockWidget(self.iface, self.parent)
            mock_layer = MagicMock()
            mock_layer.saveDefaultStyle.return_value = ("Success", True)
            
            dock.action_save_as_default_style(mock_layer)
            mock_layer.saveDefaultStyle.assert_called_once()
            mock_info.assert_called_once()

    def test_action_remove_layer_success(self):
        with patch('dock_widget.LayerTreeModel'), \
             patch('dock_widget.TreeMapWidget'), \
             patch('dock_widget.QgsProject') as mock_proj_cls:

            mock_project = MagicMock()
            mock_proj_cls.instance.return_value = mock_project

            dock = SuperLayerDockWidget(self.iface, self.parent)
            mock_layer = MagicMock()
            mock_layer.id.return_value = "layer-001"

            dock.action_remove_layer(mock_layer)
            mock_project.removeMapLayer.assert_called_once_with("layer-001")

    def test_action_delete_files_cancelled(self):
        """If the user presses No in the confirmation dialog, nothing is deleted."""
        with patch('dock_widget.LayerTreeModel'), \
             patch('dock_widget.TreeMapWidget'), \
             patch('dock_widget.resolve_physical_path', return_value="/mock/source.shp"), \
             patch('dock_widget.get_associated_files', return_value=["/mock/source.shp", "/mock/source.dbf"]), \
             patch('os.path.exists', return_value=True), \
             patch('dock_widget.QMessageBox.warning', return_value=0) as mock_warn:  # 0 != QMessageBox.Yes

            dock = SuperLayerDockWidget(self.iface, self.parent)
            mock_layer = MagicMock()
            mock_layer.source.return_value = "/mock/source.shp"

            with patch('os.remove') as mock_remove:
                dock.action_delete_files(mock_layer)
                mock_remove.assert_not_called()

    def test_action_delete_files_confirmed(self):
        """If the user presses Yes, all associated files are deleted and layer is removed."""
        with patch('dock_widget.LayerTreeModel'), \
             patch('dock_widget.TreeMapWidget'), \
             patch('dock_widget.resolve_physical_path', return_value="/mock/source.shp"), \
             patch('dock_widget.get_associated_files', return_value=["/mock/source.shp", "/mock/source.dbf"]), \
             patch('os.path.exists', return_value=True), \
             patch('dock_widget.QMessageBox.warning', return_value=16384) as mock_warn, \
             patch('os.remove') as mock_remove, \
             patch('dock_widget.QgsProject') as mock_proj_cls:

            mock_project = MagicMock()
            mock_proj_cls.instance.return_value = mock_project

            dock = SuperLayerDockWidget(self.iface, self.parent)
            mock_layer = MagicMock()
            mock_layer.source.return_value = "/mock/source.shp"
            mock_layer.id.return_value = "layer-001"

            dock.action_delete_files(mock_layer)
            self.assertEqual(mock_remove.call_count, 2)
            mock_project.removeMapLayer.assert_called_once_with("layer-001")

    def test_action_remove_layers_success(self):
        with patch('dock_widget.LayerTreeModel'), \
             patch('dock_widget.TreeMapWidget'), \
             patch('dock_widget.QgsProject') as mock_proj_cls:

            mock_project = MagicMock()
            mock_proj_cls.instance.return_value = mock_project

            dock = SuperLayerDockWidget(self.iface, self.parent)
            mock_layer1 = MagicMock()
            mock_layer1.id.return_value = "layer-001"
            mock_layer2 = MagicMock()
            mock_layer2.id.return_value = "layer-002"

            dock.action_remove_layers([mock_layer1, mock_layer2])
            self.assertEqual(mock_project.removeMapLayer.call_count, 2)

    def test_action_delete_files_multi_confirmed(self):
        with patch('dock_widget.LayerTreeModel'), \
             patch('dock_widget.TreeMapWidget'), \
             patch('dock_widget.resolve_physical_path', return_value="/mock/source.shp"), \
             patch('dock_widget.get_associated_files', return_value=["/mock/source.shp", "/mock/source.dbf"]), \
             patch('os.path.exists', return_value=True), \
             patch('dock_widget.QMessageBox.warning', return_value=16384), \
             patch('os.remove') as mock_remove, \
             patch('dock_widget.QgsProject') as mock_proj_cls:

            mock_project = MagicMock()
            mock_proj_cls.instance.return_value = mock_project

            dock = SuperLayerDockWidget(self.iface, self.parent)
            mock_layer1 = MagicMock()
            mock_layer1.source.return_value = "/mock/source.shp"
            mock_layer1.id.return_value = "layer-001"
            
            mock_layer2 = MagicMock()
            mock_layer2.source.return_value = "/mock/source.shp"
            mock_layer2.id.return_value = "layer-002"

            dock.action_delete_files_multi([mock_layer1, mock_layer2])
            self.assertEqual(mock_remove.call_count, 2)
            self.assertEqual(mock_project.removeMapLayer.call_count, 2)

    def test_action_export_temporary_layer_success(self):
        with patch('dock_widget.LayerTreeModel'), \
             patch('dock_widget.TreeMapWidget'), \
             patch('dock_widget.QFileDialog.getSaveFileName', return_value=("/mock/temp_saved.gpkg", "GeoPackage")), \
             patch('dock_widget.QMessageBox.information') as mock_info, \
             patch('dock_widget.QgsProject') as mock_proj_cls:

            mock_project = MagicMock()
            mock_proj_cls.instance.return_value = mock_project

            dock = SuperLayerDockWidget(self.iface, self.parent)
            
            from dock_widget import QgsVectorLayer
            mock_layer = MagicMock(spec=QgsVectorLayer)
            mock_layer.name.return_value = "temp_layer"
            mock_layer.id.return_value = "temp_layer_id"

            dock.action_export_temporary_layer(mock_layer)
            
        with patch('dock_widget.LayerTreeModel'), \
             patch('dock_widget.TreeMapWidget'), \
             patch('dock_widget.QFileDialog.getSaveFileName', return_value=("/mock/temp_saved.gpkg", "GeoPackage")), \
             patch('dock_widget.QMessageBox.information') as mock_info, \
             patch('dock_widget.QgsProject') as mock_proj_cls:

            mock_project = MagicMock()
            mock_proj_cls.instance.return_value = mock_project

            dock = SuperLayerDockWidget(self.iface, self.parent)
            
            from dock_widget import QgsVectorLayer
            mock_layer = MagicMock(spec=QgsVectorLayer)
            mock_layer.name.return_value = "temp_layer"
            mock_layer.id.return_value = "temp_layer_id"

            dock.action_export_temporary_layer(mock_layer)
            
            # Assert that addMapLayer was called with a QgsVectorLayer instance
            mock_project.addMapLayer.assert_called_once()
            added_layer = mock_project.addMapLayer.call_args[0][0]
            self.assertTrue(isinstance(added_layer, QgsVectorLayer))
            self.assertEqual(added_layer.source(), "/mock/temp_saved.gpkg")
            self.assertEqual(added_layer.name(), "temp_saved")
            
            mock_project.removeMapLayer.assert_called_once_with("temp_layer_id")
            mock_info.assert_called_once()

    def test_action_delete_gpkg_layer_success(self):
        with patch('dock_widget.LayerTreeModel'), \
             patch('dock_widget.TreeMapWidget'), \
             patch('dock_widget.QMessageBox.warning', return_value=16384), \
             patch('dock_widget.QMessageBox.information') as mock_info, \
             patch('dock_widget.QgsProject') as mock_proj_cls:

            mock_project = MagicMock()
            mock_proj_cls.instance.return_value = mock_project

            dock = SuperLayerDockWidget(self.iface, self.parent)
            
            from dock_widget import QgsVectorLayer
            mock_layer = MagicMock(spec=QgsVectorLayer)
            mock_layer.name.return_value = "table1"
            mock_layer.source.return_value = "/mock/db.gpkg|layername=table1"
            mock_layer.id.return_value = "layer-001"

            dock.action_delete_gpkg_layer(mock_layer)
            mock_project.removeMapLayer.assert_called_once_with("layer-001")
            mock_info.assert_called_once()

    def test_action_delete_gpkg_layers_success(self):
        with patch('dock_widget.LayerTreeModel'), \
             patch('dock_widget.TreeMapWidget'), \
             patch('dock_widget.QMessageBox.warning', return_value=16384), \
             patch('dock_widget.QMessageBox.information') as mock_info, \
             patch('dock_widget.QgsProject') as mock_proj_cls:

            mock_project = MagicMock()
            mock_proj_cls.instance.return_value = mock_project

            dock = SuperLayerDockWidget(self.iface, self.parent)
            
            from dock_widget import QgsVectorLayer
            mock_layer1 = MagicMock(spec=QgsVectorLayer)
            mock_layer1.name.return_value = "table1"
            mock_layer1.source.return_value = "/mock/db.gpkg|layername=table1"
            mock_layer1.id.return_value = "layer-001"

            mock_layer2 = MagicMock(spec=QgsVectorLayer)
            mock_layer2.name.return_value = "table2"
            mock_layer2.source.return_value = "/mock/db.gpkg|layername=table2"
            mock_layer2.id.return_value = "layer-002"

            dock.action_delete_gpkg_layers([mock_layer1, mock_layer2])
            self.assertEqual(mock_project.removeMapLayer.call_count, 2)
            mock_info.assert_called_once()

    def test_layer_context_menu_order_hidden(self):
        from dock_widget import QMenu
        from unittest.mock import MagicMock
        
        with patch('dock_widget.LayerTreeModel'), \
             patch('dock_widget.TreeMapWidget'), \
             patch('layer_model.is_layer_visible', return_value=False):
             
            dock = SuperLayerDockWidget(self.iface, self.parent)
            
            mock_layer = MagicMock()
            mock_layer.id.return_value = "layer-hidden"
            mock_layer.name.return_value = "Hidden Layer"
            
            mock_menu = MagicMock(spec=QMenu)
            with patch('dock_widget.QMenu', return_value=mock_menu), \
                 patch('os.path.exists', return_value=True):
                dock._create_layer_context_menu([mock_layer], None)
                
            added_actions = [c[0][0] for c in mock_menu.addAction.call_args_list]
            self.assertIn("隐藏图层", added_actions)
            self.assertIn("显示图层", added_actions)
            
            idx_hide = added_actions.index("隐藏图层")
            idx_show = added_actions.index("显示图层")
            self.assertTrue(idx_show < idx_hide)

    def test_safe_export_layer_name_removes_invalid_path_characters(self):
        self.assertEqual(
            SuperLayerDockWidget._safe_export_layer_name('roads:<2026>/main?'),
            "roads__2026__main_",
        )

    def test_resolve_export_name_auto_renames_duplicates(self):
        with patch('dock_widget.LayerTreeModel'), \
             patch('dock_widget.TreeMapWidget'):
            dock = SuperLayerDockWidget(self.iface, self.parent)
            used_names = {"roads"}

            resolved = dock._resolve_export_name(
                "/mock/output.gpkg", "GPKG", "roads", "rename", used_names
            )

            self.assertEqual(resolved, "roads_2")
            self.assertIn("roads_2", used_names)

    def test_resolve_export_name_skips_duplicates(self):
        with patch('dock_widget.LayerTreeModel'), \
             patch('dock_widget.TreeMapWidget'):
            dock = SuperLayerDockWidget(self.iface, self.parent)

            resolved = dock._resolve_export_name(
                "/mock/output.gpkg", "GPKG", "roads", "skip", {"roads"}
            )

            self.assertIsNone(resolved)

    def test_resolve_export_name_never_overwrites_an_earlier_batch_layer(self):
        with patch('dock_widget.LayerTreeModel'), \
             patch('dock_widget.TreeMapWidget'):
            dock = SuperLayerDockWidget(self.iface, self.parent)

            resolved = dock._resolve_export_name(
                "/mock/output.gpkg", "GPKG", "roads", "overwrite", {"roads"}
            )

            self.assertEqual(resolved, "roads_2")

    def test_batch_export_never_accesses_source_layer_after_removal(self):
        with patch('dock_widget.LayerTreeModel'), \
             patch('dock_widget.TreeMapWidget'), \
             patch('dock_widget.QMessageBox.information'), \
             patch('dock_widget.QgsProject') as project_class:
            dock = SuperLayerDockWidget(self.iface, self.parent)
            dock.refresh = MagicMock()
            dock._capture_layer_style = MagicMock(return_value="style-snapshot")
            dock._apply_layer_style = MagicMock()
            removed = {"value": False}

            layer = MagicMock(spec=dock_widget.QgsVectorLayer)
            layer.name.side_effect = lambda: (
                (_ for _ in ()).throw(RuntimeError("deleted"))
                if removed["value"] else "roads"
            )
            layer.id.return_value = "temporary-roads"

            project = MagicMock()
            project.transformContext.return_value = None
            project.removeMapLayers.side_effect = lambda ids: removed.update(value=True)
            project_class.instance.return_value = project

            with tempfile.TemporaryDirectory() as destination:
                dock._export_temporary_layers_batch(
                    [layer],
                    "GPKG",
                    os.path.join(destination, "batch.gpkg"),
                    replace=True,
                )

            project.removeMapLayers.assert_called_once_with(["temporary-roads"])
            self.assertEqual(layer.name.call_count, 1)
            dock._capture_layer_style.assert_called_once_with(layer)
            dock._apply_layer_style.assert_called_once()
            self.assertEqual(
                dock._apply_layer_style.call_args.args[0],
                "style-snapshot",
            )

    def test_batch_export_skips_a_wrapper_deleted_before_style_snapshot(self):
        with patch('dock_widget.LayerTreeModel'), \
             patch('dock_widget.TreeMapWidget'), \
             patch('dock_widget.QMessageBox.warning') as warning:
            dock = SuperLayerDockWidget(self.iface, self.parent)
            dock.refresh = MagicMock()
            deleted_layer = MagicMock(spec=dock_widget.QgsVectorLayer)
            deleted_layer.name.side_effect = RuntimeError("deleted")

            with tempfile.TemporaryDirectory() as destination:
                dock._export_temporary_layers_batch(
                    [deleted_layer],
                    "GPKG",
                    os.path.join(destination, "batch.gpkg"),
                )

            warning.assert_called_once()
            self.assertIn("失败：1 个", warning.call_args.args[2])

    def test_action_delete_gpkg_layer_success(self):
        with patch('dock_widget.LayerTreeModel'), \
             patch('dock_widget.TreeMapWidget'), \
             patch('dock_widget.QMessageBox.warning', return_value=16384), \
             patch('dock_widget.QMessageBox.information') as mock_info, \
             patch('dock_widget.QgsProject') as mock_proj_cls:

            mock_project = MagicMock()
            mock_proj_cls.instance.return_value = mock_project

            dock = SuperLayerDockWidget(self.iface, self.parent)
            
            from dock_widget import QgsVectorLayer
            mock_layer = MagicMock(spec=QgsVectorLayer)
            mock_layer.name.return_value = "table1"
            mock_layer.source.return_value = "/mock/db.gpkg|layername=table1"
            mock_layer.id.return_value = "layer-001"

            dock.action_delete_gpkg_layer(mock_layer)
            mock_project.removeMapLayer.assert_called_once_with("layer-001")
            mock_info.assert_called_once()

            mock_menu = MagicMock(spec=QMenu)
            with patch('dock_widget.QMenu', return_value=mock_menu), \
                 patch('os.path.exists', return_value=True):
                dock._create_layer_context_menu([mock_layer], None)
                
            added_actions = [c[0][0] for c in mock_menu.addAction.call_args_list]
            self.assertIn("隐藏图层", added_actions)
            self.assertIn("显示图层", added_actions)
            
            idx_hide = added_actions.index("隐藏图层")
            idx_show = added_actions.index("显示图层")
            self.assertTrue(idx_show < idx_hide)

    def test_draggable_tree_view_drop_event(self):
        from dock_widget import DraggableTreeView
        from layer_model import FolderItem
        from unittest.mock import MagicMock
        
        view = DraggableTreeView()
        
        mock_idx = MagicMock()
        mock_idx.isValid.return_value = True
        
        mock_item = FolderItem("/mock/target/dir", is_physical=True)
        
        mock_model = MagicMock()
        mock_model.itemFromIndex.return_value = mock_item
        
        view.indexAt = MagicMock(return_value=mock_idx)
        view.model = MagicMock(return_value=mock_model)
        
        mock_slot = MagicMock()
        view.layersDropped.connect(mock_slot)
        
        event_mock = MagicMock()
        event_mock.mimeData().hasFormat.return_value = True
        event_mock.mimeData().data.return_value.data.return_value.decode.return_value = '["layer-1", "layer-2"]'
        
        view.dropEvent(event_mock)
        
        mock_slot.assert_called_once_with(["layer-1", "layer-2"], "/mock/target/dir")
        event_mock.acceptProposedAction.assert_called_once()

    def test_toolbar_filter_visible_toggled(self):
        dock = SuperLayerDockWidget(self.iface, self.parent)
        self.assertIsNotNone(dock.btn_filter_visible)
        
        # Test toggling the checkable filter button on the toolbar
        dock.btn_filter_visible.toggled.emit(True)
        self.assertTrue(dock.layer_board_view.filter_visible_only)
        
        dock.btn_filter_visible.toggled.emit(False)
        self.assertFalse(dock.layer_board_view.filter_visible_only)

    def test_filter_visible_layers_in_treemap_and_mindmap(self):
        dock = SuperLayerDockWidget(self.iface, self.parent)

        # Setup mock layers
        layer_visible = MagicMock()
        layer_visible.id.return_value = "layer_vis"
        layer_visible.name.return_value = "Visible Layer"

        layer_hidden = MagicMock()
        layer_hidden.id.return_value = "layer_hid"

    def test_action_delete_gpkg_layer_success(self):
        with patch('dock_widget.LayerTreeModel'), \
             patch('dock_widget.TreeMapWidget'), \
             patch('dock_widget.QMessageBox.warning', return_value=16384), \
             patch('dock_widget.QMessageBox.information') as mock_info, \
             patch('dock_widget.QgsProject') as mock_proj_cls:

            mock_project = MagicMock()
            mock_proj_cls.instance.return_value = mock_project

            dock = SuperLayerDockWidget(self.iface, self.parent)
            
            from dock_widget import QgsVectorLayer
            mock_layer = MagicMock(spec=QgsVectorLayer)
            mock_layer.name.return_value = "table1"
            mock_layer.source.return_value = "/mock/db.gpkg|layername=table1"
            mock_layer.id.return_value = "layer-001"

            dock.action_delete_gpkg_layer(mock_layer)
            mock_project.removeMapLayer.assert_called_once_with("layer-001")
            mock_info.assert_called_once()

    def test_action_delete_gpkg_layers_success(self):
        with patch('dock_widget.LayerTreeModel'), \
             patch('dock_widget.TreeMapWidget'), \
             patch('dock_widget.QMessageBox.warning', return_value=16384), \
             patch('dock_widget.QMessageBox.information') as mock_info, \
             patch('dock_widget.QgsProject') as mock_proj_cls:

            mock_project = MagicMock()
            mock_proj_cls.instance.return_value = mock_project

            dock = SuperLayerDockWidget(self.iface, self.parent)
            
            from dock_widget import QgsVectorLayer
            mock_layer1 = MagicMock(spec=QgsVectorLayer)
            mock_layer1.name.return_value = "table1"
            mock_layer1.source.return_value = "/mock/db.gpkg|layername=table1"
            mock_layer1.id.return_value = "layer-001"

            mock_layer2 = MagicMock(spec=QgsVectorLayer)
            mock_layer2.name.return_value = "table2"
            mock_layer2.source.return_value = "/mock/db.gpkg|layername=table2"
            mock_layer2.id.return_value = "layer-002"

            dock.action_delete_gpkg_layers([mock_layer1, mock_layer2])
            self.assertEqual(mock_project.removeMapLayer.call_count, 2)
            mock_info.assert_called_once()

    def test_layer_context_menu_order_hidden(self):
        from dock_widget import QMenu
        from unittest.mock import MagicMock
        
        with patch('dock_widget.LayerTreeModel'), \
             patch('dock_widget.TreeMapWidget'), \
             patch('layer_model.is_layer_visible', return_value=False):
             
            dock = SuperLayerDockWidget(self.iface, self.parent)
            
            mock_layer = MagicMock()
            mock_layer.id.return_value = "layer-hidden"
            mock_layer.name.return_value = "Hidden Layer"
            
            mock_menu = MagicMock(spec=QMenu)
            with patch('dock_widget.QMenu', return_value=mock_menu), \
                 patch('os.path.exists', return_value=True):
                dock._create_layer_context_menu([mock_layer], None)
                
            added_actions = [c[0][0] for c in mock_menu.addAction.call_args_list]
            self.assertIn("隐藏图层", added_actions)
            self.assertIn("显示图层", added_actions)
            
            idx_hide = added_actions.index("隐藏图层")
            idx_show = added_actions.index("显示图层")
            self.assertTrue(idx_show < idx_hide)

    def test_draggable_tree_view_drop_event(self):
        from dock_widget import DraggableTreeView
        from layer_model import FolderItem
        from unittest.mock import MagicMock
        
        view = DraggableTreeView()
        
        mock_idx = MagicMock()
        mock_idx.isValid.return_value = True
        
        mock_item = FolderItem("/mock/target/dir", is_physical=True)
        
        mock_model = MagicMock()
        mock_model.itemFromIndex.return_value = mock_item
        
        view.indexAt = MagicMock(return_value=mock_idx)
        view.model = MagicMock(return_value=mock_model)
        
        mock_slot = MagicMock()
        view.layersDropped.connect(mock_slot)
        
        event_mock = MagicMock()
        event_mock.mimeData().hasFormat.return_value = True
        event_mock.mimeData().data.return_value.data.return_value.decode.return_value = '["layer-1", "layer-2"]'
        
        view.dropEvent(event_mock)
        
        mock_slot.assert_called_once_with(["layer-1", "layer-2"], "/mock/target/dir")
        event_mock.acceptProposedAction.assert_called_once()

    def test_toolbar_filter_visible_toggled(self):
        dock = SuperLayerDockWidget(self.iface, self.parent)
        self.assertIsNotNone(dock.btn_filter_visible)
        
        # Test toggling the checkable filter button on the toolbar
        dock.btn_filter_visible.toggled.emit(True)
        self.assertTrue(dock.layer_board_view.filter_visible_only)
        
        dock.btn_filter_visible.toggled.emit(False)
        self.assertFalse(dock.layer_board_view.filter_visible_only)

    def test_filter_visible_layers_in_treemap_and_mindmap(self):
        dock = SuperLayerDockWidget(self.iface, self.parent)

        # Setup mock layers
        layer_visible = MagicMock()
        layer_visible.id.return_value = "layer_vis"
        layer_visible.name.return_value = "Visible Layer"

        layer_hidden = MagicMock()
        layer_hidden.id.return_value = "layer_hid"
        layer_hidden.name.return_value = "Hidden Layer"

        # Mock QgsProject to return these layers
        mock_project = MagicMock()
        mock_project.mapLayers.return_value = {"l1": layer_visible, "l2": layer_hidden}
        mock_project.layerTreeRoot.return_value = MagicMock()

        # is_layer_effectively_visible determines the filter outcome
        def eff_visible(layer):
            return layer.id() == "layer_vis"

        with patch('layer_model.QgsProject.instance', return_value=mock_project), \
             patch('dock_widget.QgsProject.instance', return_value=mock_project), \
             patch('layer_model.is_layer_effectively_visible', side_effect=eff_visible):

            # 1. When filter is OFF (checked = False) – all layers returned
            dock.btn_filter_visible.setChecked(False)
            layers = dock._get_filtered_layers(None)
            self.assertEqual(len(layers), 2)
            self.assertIn(layer_visible, layers)
            self.assertIn(layer_hidden, layers)

            # 2. When filter is ON (checked = True) – only effectively-visible layer
            dock.btn_filter_visible.setChecked(True)
            layers = dock._get_filtered_layers(None)
            self.assertEqual(len(layers), 1)
            self.assertIn(layer_visible, layers)
            self.assertNotIn(layer_hidden, layers)

    def test_map_theme_filters_by_recorded_layer_ids(self):
        dock = SuperLayerDockWidget(self.iface, self.parent)
        dock.group_model = MagicMock()
        layer_in_theme = MagicMock()
        layer_in_theme.id.return_value = "theme-layer"
        layer_outside_theme = MagicMock()
        layer_outside_theme.id.return_value = "other-layer"

        collection = MagicMock()
        collection.mapThemeVisibleLayers.return_value = [layer_in_theme]
        project = MagicMock()
        project.mapLayers.return_value = {
            "theme-layer": layer_in_theme,
            "other-layer": layer_outside_theme,
        }
        project.mapThemeCollection.return_value = collection

        with patch('dock_widget.QgsProject.instance', return_value=project):
            dock.current_map_theme = "Planning"
            dock.btn_filter_visible.setChecked(True)
            layers = dock._get_filtered_layers(None)

        collection.mapThemeVisibleLayers.assert_called_with("Planning")
        self.assertEqual(layers, [layer_in_theme])
        dock.group_model.set_theme_layer_ids.assert_called_with({"theme-layer"})

    def test_draggable_group_tree_view_mouse_events_and_drag_selection_suppression(self):
        from dock_widget import DraggableGroupTreeView, Qt
        from unittest.mock import MagicMock

        view = DraggableGroupTreeView()
        self.assertIsNone(view._drop_target_index)
        self.assertIsNone(view._drop_position)

        idx_col_0 = MagicMock()
        idx_col_0.isValid.return_value = True
        idx_col_0.column.return_value = 0
        view.indexAt = MagicMock(return_value=idx_col_0)

        pos_val = MagicMock()
        pos_val.x.return_value = 10
        pos_val.y.return_value = 10
        pos_val.__sub__ = lambda self, other: MagicMock(manhattanLength=lambda: 2)

        event_press = MagicMock()
        event_press.button.return_value = Qt.MouseButton.LeftButton
        event_press.pos.return_value = pos_val

        view.mousePressEvent(event_press)
        self.assertEqual(view._drag_start_pos, pos_val)

        event_move = MagicMock()
        event_move.buttons.return_value = Qt.MouseButton.LeftButton
        event_move.pos.return_value = pos_val
        view.start_group_drag = MagicMock()

        view.mouseMoveEvent(event_move)
        view.start_group_drag.assert_not_called()

        view.mouseReleaseEvent(event_press)
        self.assertIsNone(view._drag_start_pos)

    def test_handle_group_reorder_moves_qgis_tree_nodes(self):
        from dock_widget import SuperLayerDockWidget
        from unittest.mock import MagicMock, patch

        mock_iface = MagicMock()
        with patch('dock_widget.QgsProject') as mock_qgsproject:
            mock_project = MagicMock()
            mock_root = MagicMock()
            mock_qgsproject.instance.return_value = mock_project
            mock_project.layerTreeRoot.return_value = mock_root

            target_node = MagicMock()
            target_parent = MagicMock()
            target_node.parent.return_value = target_parent
            target_parent.children.return_value = []
            
            source_node = MagicMock()
            source_node.parent.return_value = target_parent
            target_parent.children.return_value = [source_node, target_node]
            source_layer = MagicMock()
            target_layer = MagicMock()
            source_node.layer.return_value = source_layer
            target_node.layer.return_value = target_layer

            mock_root.findLayer.side_effect = lambda lid: target_node if lid == "target_lyr" else source_node

            dock = SuperLayerDockWidget(mock_iface)
            dock._refresh_timer = MagicMock()

            dragged_items = [{"type": "layer", "id": "src_lyr", "name": "Source Layer"}]
            target_info = {"type": "layer", "id": "target_lyr"}
            dock.handle_group_reorder(dragged_items, target_info, "below")

            target_parent.reorderGroupLayers.assert_called_once_with([target_layer, source_layer])
            dock._refresh_timer.start.assert_called_once()
            source_node.clone.assert_not_called()
            target_parent.removeChildNode.assert_not_called()

    def test_handle_group_reorder_rejects_cross_group_move(self):
        from dock_widget import SuperLayerDockWidget
        from unittest.mock import MagicMock, patch

        with patch('dock_widget.QgsProject') as mock_qgsproject:
            root = MagicMock()
            mock_qgsproject.instance.return_value.layerTreeRoot.return_value = root
            target_node = MagicMock()
            source_node = MagicMock()
            target_node.parent.return_value = MagicMock()
            source_node.parent.return_value = MagicMock()
            root.findLayer.side_effect = lambda lid: target_node if lid == "target" else source_node

            dock = SuperLayerDockWidget(MagicMock())
            dock.handle_group_reorder(
                [{"type": "layer", "id": "source"}],
                {"type": "layer", "id": "target"},
                "above",
            )

            target_node.parent.return_value.reorderGroupLayers.assert_not_called()

if __name__ == '__main__':
    unittest.main()
