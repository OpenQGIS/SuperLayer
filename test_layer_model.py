import unittest
import os
import tempfile
import shutil
from unittest.mock import MagicMock, patch

# Import qt components
import layer_model
from layer_model import LayerTreeModel, FolderItem, LayerItem, Qt

class TestLayerModel(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.src_dir = os.path.join(self.temp_dir.name, 'src')
        os.makedirs(self.src_dir)
        
        # Backup the original QgsProject instance
        self.orig_project_instance = layer_model.QgsProject._instance

    def tearDown(self):
        self.temp_dir.cleanup()
        layer_model.QgsProject._instance = self.orig_project_instance

    def test_format_size(self):
        from layer_model import format_size
        self.assertEqual(format_size(0), "-")
        self.assertEqual(format_size(-100), "-")
        self.assertEqual(format_size(500), "500.00 B")
        self.assertEqual(format_size(1024), "1.00 KB")
        self.assertEqual(format_size(1024 * 1024 * 2.5), "2.50 MB")
        self.assertEqual(format_size(1024 * 1024 * 1024 * 1.5), "1.50 GB")

    def test_get_file_size(self):
        # Create a temp file and some sidecars
        shp_file = os.path.join(self.src_dir, "test.shp")
        dbf_file = os.path.join(self.src_dir, "test.dbf")
        shx_file = os.path.join(self.src_dir, "test.shx")
        
        with open(shp_file, 'wb') as f:
            f.write(b'a' * 100) # 100 bytes
        with open(dbf_file, 'wb') as f:
            f.write(b'b' * 200) # 200 bytes
        with open(shx_file, 'wb') as f:
            f.write(b'c' * 50) # 50 bytes
            
        model = LayerTreeModel()
        # Test basic size accumulation (100 + 200 + 50 = 350 bytes)
        size = model._get_file_size(shp_file)
        self.assertEqual(size, 350)
        
        # Test non-existing file returns 0
        self.assertEqual(model._get_file_size("non_existent_file.shp"), 0)

    def test_build_physical_tree(self):
        # Setup layers
        shp_file1 = os.path.join(self.src_dir, "test1.shp")
        shp_file2 = os.path.join(self.src_dir, "test2.shp")
        
        with open(shp_file1, 'wb') as f:
            f.write(b'a' * 100)
        with open(shp_file2, 'wb') as f:
            f.write(b'b' * 300)
            
        # Create mock layer objects
        layer1 = MagicMock()
        layer1.id.return_value = "layer_1"
        layer1.name.return_value = "Layer One"
        layer1.source.return_value = shp_file1
        
        layer2 = MagicMock()
        layer2.id.return_value = "layer_2"
        layer2.name.return_value = "Layer Two"
        layer2.source.return_value = shp_file2
        
        # Mock QgsProject instance
        mock_project = MagicMock()
        mock_project.mapLayers.return_value = {
            "layer_1": layer1,
            "layer_2": layer2
        }
        layer_model.QgsProject._instance = mock_project
        
        model = LayerTreeModel()
        model.rebuild_model(group_by_physical=True)
        
        # The model should have folder node (row 0)
        self.assertEqual(model.rowCount(), 1)
        folder_item = model.item(0, 0)
        self.assertIsInstance(folder_item, FolderItem)
        self.assertTrue(folder_item.is_physical)
        self.assertEqual(folder_item.folder_path, os.path.normpath(os.path.abspath(self.src_dir)))
        
        # Folder item size in column 1 should be the sum (100 + 300 = 400 bytes)
        folder_size_item = model.item(0, 1)
        self.assertEqual(folder_size_item.text(), "400.00 B")
        self.assertEqual(folder_size_item.data(Qt.UserRole), 400)
        
        # Folder item should have two child layers
        self.assertEqual(folder_item.rowCount(), 2)
        
        layer1_item = folder_item.child(0, 0)
        layer1_size = folder_item.child(0, 1)
        self.assertIsInstance(layer1_item, LayerItem)
        self.assertEqual(layer1_item.text(), "Layer One")
        self.assertEqual(layer1_size.text(), "100.00 B")
        
        layer2_item = folder_item.child(1, 0)
        layer2_size = folder_item.child(1, 1)
        self.assertIsInstance(layer2_item, LayerItem)
        self.assertEqual(layer2_item.text(), "Layer Two")
        self.assertEqual(layer2_size.text(), "300.00 B")

    def test_build_physical_tree_duplicate_folders(self):
        # Create directories with same name 'data' in ProjectA and ProjectB
        dir_a = os.path.join(self.src_dir, 'ProjectA', 'data')
        dir_b = os.path.join(self.src_dir, 'ProjectB', 'data')
        os.makedirs(dir_a)
        os.makedirs(dir_b)
        
        shp_a = os.path.join(dir_a, "testA.shp")
        shp_b = os.path.join(dir_b, "testB.shp")
        with open(shp_a, 'wb') as f: f.write(b'a' * 50)
        with open(shp_b, 'wb') as f: f.write(b'b' * 150)
        
        # Create mocks
        layer_a = MagicMock()
        layer_a.id.return_value = "layer_a"
        layer_a.name.return_value = "Layer A"
        layer_a.source.return_value = shp_a
        
        layer_b = MagicMock()
        layer_b.id.return_value = "layer_b"
        layer_b.name.return_value = "Layer B"
        layer_b.source.return_value = shp_b
        
        mock_project = MagicMock()
        mock_project.mapLayers.return_value = {
            "layer_a": layer_a,
            "layer_b": layer_b
        }
        layer_model.QgsProject._instance = mock_project
        
        model = LayerTreeModel()
        model.rebuild_model(group_by_physical=True)
        
        # We should have 2 folders at the top level
        self.assertEqual(model.rowCount(), 2)
        
        # Get folder display names and paths
        f1 = model.item(0, 0)
        f2 = model.item(1, 0)
        
        display_names = {f1.text(), f2.text()}
        tooltips = {f1.toolTip(), f2.toolTip()}
        
        # Verify that display names include parent info to resolve collision
        self.assertEqual(display_names, {"data (ProjectA)", "data (ProjectB)"})
        # Verify tooltips contain full path
        self.assertEqual(tooltips, {
            os.path.normpath(os.path.abspath(dir_a)),
            os.path.normpath(os.path.abspath(dir_b))
        })

    def test_build_virtual_tree(self):
        # Setup mock QgsLayerTreeGroup and nodes
        mock_root = MagicMock()
        
        # Mock group node
        group1 = MagicMock(spec=layer_model.QgsLayerTreeGroup)
        group1.name.return_value = "Group A"
        
        # Mock layer node
        shp_file = os.path.join(self.src_dir, "test.shp")
        with open(shp_file, 'wb') as f:
            f.write(b'a' * 150)
            
        mock_layer_obj = MagicMock()
        mock_layer_obj.id.return_value = "layer_v"
        mock_layer_obj.name.return_value = "Layer Virtual"
        mock_layer_obj.source.return_value = shp_file
        mock_layer_obj.isValid.return_value = True
        
        layer_node = MagicMock(spec=layer_model.QgsLayerTreeLayer)
        layer_node.layer.return_value = mock_layer_obj
        
        group1.children.return_value = [layer_node]
        mock_root.children.return_value = [group1]
        
        mock_project = MagicMock()
        mock_project.layerTreeRoot.return_value = mock_root
        layer_model.QgsProject._instance = mock_project
        
        model = LayerTreeModel()
        model.rebuild_model(group_by_physical=False)
        
        # Model root has "Group A" group item in row 0
        self.assertEqual(model.rowCount(), 1)
        group_item = model.item(0, 0)
        self.assertIsInstance(group_item, FolderItem)
        self.assertFalse(group_item.is_physical)
        self.assertEqual(group_item.text(), "Group A")
        
        # Group size item in column 1 should be "150.00 B"
        group_size_item = model.item(0, 1)
        self.assertEqual(group_size_item.text(), "150.00 B")
        self.assertEqual(group_size_item.data(Qt.UserRole), 150)
        
        # Group A should have one child layer
        self.assertEqual(group_item.rowCount(), 1)
        child_item = group_item.child(0, 0)
        self.assertIsInstance(child_item, LayerItem)
        self.assertEqual(child_item.text(), "Layer Virtual")
        self.assertEqual(group_item.child(0, 1).text(), "150.00 B")


    def test_layer_and_folder_icons(self):
        from layer_model import FolderItem, LayerItem
        
        # Test folder item icon creation under mocked environment (should not raise)
        folder_item = FolderItem("/mock/path", is_physical=True)
        self.assertTrue(hasattr(folder_item, 'icon'))
            
        # Test layer item icon creation with geometry type Point (0)
        mock_layer = MagicMock()
        mock_layer.__class__.__name__ = "QgsVectorLayer"
        mock_layer.geometryType.return_value = 0
        mock_layer.id.return_value = "layer1"
        mock_layer.name.return_value = "Point Layer"
        
        with patch('os.path.exists', return_value=True):
            layer_item = LayerItem(mock_layer, "Point Layer")
            self.assertIsNotNone(layer_item)

    @patch('layer_model.QIcon')
    def test_get_layer_icon_mesh_and_database(self, mock_qicon):
        from layer_model import _get_layer_icon
        
        # Mock mesh layer
        mock_mesh = MagicMock()
        mock_mesh.type.return_value = 3
        mock_mesh.__class__.__name__ = "QgsMeshLayer"
        
        # Mock point cloud layer
        mock_pc = MagicMock()
        mock_pc.type.return_value = 5
        mock_pc.__class__.__name__ = "QgsPointCloudLayer"
        
        # Mock table layer (NullGeometry vector layer)
        mock_table = MagicMock()
        mock_table.type.return_value = 0
        mock_table.geometryType.return_value = 3 # NullGeometry
        mock_table.__class__.__name__ = "QgsVectorLayer"
        del mock_table.rasterType
        
        # Mock mssql layer
        mock_mssql_prov = MagicMock()
        mock_mssql_prov.name.return_value = "mssql"
        mock_mssql = MagicMock()
        mock_mssql.type.return_value = 0
        mock_mssql.geometryType.return_value = 0 # Point
        mock_mssql.dataProvider.return_value = mock_mssql_prov
        mock_mssql.__class__.__name__ = "QgsVectorLayer"
        del mock_mssql.rasterType
        
        # Patch os.path.exists to always return True for the tests
        with patch('os.path.exists', return_value=True):
            # Mesh
            _get_layer_icon(mock_mesh)
            called_args = mock_qicon.call_args[0][0]
            self.assertTrue(called_args.endswith("MeshLayer.svg"), f"Expected MeshLayer.svg but got {called_args}")
            
            # Point Cloud
            _get_layer_icon(mock_pc)
            called_args = mock_qicon.call_args[0][0]
            self.assertTrue(called_args.endswith("PointCloudLayer.svg"), f"Expected PointCloudLayer.svg but got {called_args}")
            
            # Table
            _get_layer_icon(mock_table)
            called_args = mock_qicon.call_args[0][0]
            self.assertTrue(called_args.endswith("TableLayer.svg"), f"Expected TableLayer.svg but got {called_args}")
            
            # MSSQL
            _get_layer_icon(mock_mssql)
            called_args = mock_qicon.call_args[0][0]
            self.assertTrue(called_args.endswith("Mssql.svg"), f"Expected Mssql.svg but got {called_args}")

    def test_build_physical_tree_container_split(self):
        zip_file = os.path.join(self.src_dir, "archive.zip")
        with open(zip_file, 'wb') as f:
            f.write(b'z' * 500)
            
        layer_zip = MagicMock()
        layer_zip.id.return_value = "layer_zip"
        layer_zip.name.return_value = "Zip Inner Layer"
        layer_zip.source.return_value = f"/vsizip/{zip_file}/internal_layer.shp"
        
        mock_project = MagicMock()
        mock_project.mapLayers.return_value = {"layer_zip": layer_zip}
        layer_model.QgsProject._instance = mock_project
        
        model = LayerTreeModel()
        model.rebuild_model(group_by_physical=True)
        
        self.assertEqual(model.rowCount(), 1)
        parent_folder = model.item(0, 0)
        self.assertEqual(parent_folder.folder_path, os.path.normpath(os.path.abspath(self.src_dir)))
        
        self.assertEqual(parent_folder.rowCount(), 1)
        container_folder = parent_folder.child(0, 0)
        self.assertEqual(container_folder.text(), "archive.zip")
        self.assertEqual(container_folder.folder_path, os.path.normpath(os.path.abspath(zip_file)))
        
        self.assertEqual(container_folder.rowCount(), 1)
        layer_item = container_folder.child(0, 0)
        self.assertEqual(layer_item.text(), "Zip Inner Layer")

    @patch('layer_model.QIcon')
    def test_layer_visibility_icons_and_actions(self, mock_qicon):
        from layer_model import _get_layer_icon, QgsProject, QgsLayerTreeLayer
        
        # Setup mock layers and tree root
        mock_layer = MagicMock()
        mock_layer.id.return_value = "layer_vis_test"
        mock_layer.isValid.return_value = True
        mock_layer.type.return_value = 0
        mock_layer.geometryType.return_value = 0 # Point
        mock_layer.__class__.__name__ = "QgsVectorLayer"
        del mock_layer.rasterType
        
        # Instantiate real mock project and tree root
        project = QgsProject.instance()
        root = project.layerTreeRoot()
        
        # Create mock layer node and add it to root
        layer_node = QgsLayerTreeLayer(mock_layer)
        root._children.append(layer_node)
        
        # Patch os.path.exists to return True
        with patch('os.path.exists', return_value=True):
            # Test default visibility (visible -> should not use Layer_Hide.svg)
            _get_layer_icon(mock_layer)
            called_args = mock_qicon.call_args[0][0]
            self.assertFalse(called_args.endswith("Layer_Hide.svg"))
            
            # Test invisible (unchecked -> should still not use Layer_Hide.svg, but retain type icon)
            layer_node.setItemVisibilityChecked(False)
            _get_layer_icon(mock_layer)
            called_args_inv = mock_qicon.call_args[0][0]
            self.assertFalse(called_args_inv.endswith("Layer_Hide.svg"))
            self.assertEqual(called_args, called_args_inv)
            
            # Test toggle back to visible
            layer_node.setItemVisibilityChecked(True)
            _get_layer_icon(mock_layer)
            called_args_vis = mock_qicon.call_args[0][0]
            self.assertFalse(called_args_vis.endswith("Layer_Hide.svg"))
            self.assertEqual(called_args, called_args_vis)

    def test_get_format_color_dict(self):
        from layer_model import get_format_color_dict
        
        # Test exact match
        self.assertEqual(get_format_color_dict("shp")["treemap"], "#50b86c")
        
        # Test case-insensitive match
        self.assertEqual(get_format_color_dict("SHP")["treemap"], "#50b86c")
        
        # Test sqlite match
        self.assertEqual(get_format_color_dict("sqlite")["treemap"], "#3f51b5")
        self.assertEqual(get_format_color_dict("db")["treemap"], "#3f51b5")
        self.assertEqual(get_format_color_dict("spatialite")["treemap"], "#3f51b5")
        
        # Test fallback to other
        self.assertEqual(get_format_color_dict("unknown_format")["treemap"], "#9e9e9e")
        
        # Test None fallback
        self.assertEqual(get_format_color_dict(None)["treemap"], "#9e9e9e")

    def test_create_hidden_layer_icon_mock_calls(self):
        from layer_model import _create_hidden_layer_icon, QSize
        from unittest.mock import MagicMock, patch
        
        class DummyIcon:
            def __init__(self):
                self._added = []
            def availableSizes(self):
                return [QSize(16, 16)]
            def pixmap(self, size):
                mock_pixmap = MagicMock()
                mock_pixmap.isNull.return_value = False
                return mock_pixmap
            def addPixmap(self, pm):
                self._added.append(pm)
                
        base_icon = DummyIcon()
        
        mock_painter = MagicMock()
        mock_overlay_icon = MagicMock()
        mock_overlay_pixmap = MagicMock()
        mock_overlay_pixmap.isNull.return_value = False
        mock_overlay_icon.pixmap.return_value = mock_overlay_pixmap
        
        with patch('layer_model.QPainter', return_value=mock_painter), \
             patch('layer_model.QIcon', return_value=mock_overlay_icon), \
             patch('os.path.exists', return_value=True):
             
            result = _create_hidden_layer_icon(base_icon)
            
            mock_painter.setOpacity.assert_any_call(0.3)
            mock_painter.setOpacity.assert_any_call(0.9)
            self.assertEqual(mock_painter.drawPixmap.call_count, 2)
            mock_painter.end.assert_called_once()

    def test_rebuild_model_with_visibility_filter(self):
        # Setup mock layers and tree structure
        mock_root = MagicMock()
        
        # Mock group node
        group1 = MagicMock(spec=layer_model.QgsLayerTreeGroup)
        group1.name.return_value = "Group A"
        
        # Mock visible layer
        layer_vis = MagicMock()
        layer_vis.id.return_value = "layer_vis"
        layer_vis.name.return_value = "Visible Layer"
        layer_vis.source.return_value = "visible.shp"
        layer_vis.isValid.return_value = True
        
        node_vis = MagicMock(spec=layer_model.QgsLayerTreeLayer)
        node_vis.layer.return_value = layer_vis
        
        # Mock hidden layer
        layer_hid = MagicMock()
        layer_hid.id.return_value = "layer_hid"
        layer_hid.name.return_value = "Hidden Layer"
        layer_hid.source.return_value = "hidden.shp"
        layer_hid.isValid.return_value = True
        
        node_hid = MagicMock(spec=layer_model.QgsLayerTreeLayer)
        node_hid.layer.return_value = layer_hid
        
        group1.children.return_value = [node_vis, node_hid]
        mock_root.children.return_value = [group1]
        mock_root.isVisible.return_value = True
        group1.isVisible.return_value = True

        # Mock findLayer to return appropriate visibility node
        mock_node_vis = MagicMock()
        mock_node_vis.itemVisibilityChecked.return_value = True
        mock_node_vis.isVisible.return_value = True

        mock_node_hid = MagicMock()
        mock_node_hid.itemVisibilityChecked.return_value = False
        mock_node_hid.isVisible.return_value = False

        def find_layer_mock(layer_id):
            if layer_id == "layer_vis":
                return mock_node_vis
            return mock_node_hid

        mock_root.findLayer.side_effect = find_layer_mock

        mock_project = MagicMock()
        mock_project.layerTreeRoot.return_value = mock_root
        mock_project.mapLayers.return_value = {"l1": layer_vis, "l2": layer_hid}

        layer_model.QgsProject._instance = mock_project

        # Patch is_layer_effectively_visible (used by rebuild_model filter)
        with patch('layer_model.is_layer_effectively_visible', side_effect=lambda layer: layer.id() == "layer_vis"):
            model = LayerTreeModel()

            # 1. With filter_visible = False (virtual tree)
            model.rebuild_model(group_by_physical=False, filter_visible=False)
            self.assertEqual(model.rowCount(), 1)
            group_item = model.item(0, 0)
            self.assertEqual(group_item.rowCount(), 2)  # Both layers are shown

            # 2. With filter_visible = True (virtual tree)
            model.rebuild_model(group_by_physical=False, filter_visible=True)
            self.assertEqual(model.rowCount(), 1)
            group_item = model.item(0, 0)
            self.assertEqual(group_item.rowCount(), 1)  # Only effectively-visible layer shown
            self.assertEqual(group_item.child(0, 0).text(), "Visible Layer")

            # 3. With filter_visible = True (physical tree) – just smoke-test
            model.rebuild_model(group_by_physical=True, filter_visible=True)

    # ------------------------------------------------------------------
    # is_layer_visible (own checkbox state, independent of parent groups)
    # ------------------------------------------------------------------
    def test_is_layer_visible_own_checkbox(self):
        from layer_model import is_layer_visible, QgsProject, QgsLayerTreeGroup, QgsLayerTreeLayer

        QgsProject._instance = None
        project = QgsProject.instance()
        root = project.layerTreeRoot()

        group = QgsLayerTreeGroup("Group")
        root._children.append(group)
        group._parent = root

        layer = MagicMock()
        layer.id.return_value = "layer_own"

        node = QgsLayerTreeLayer(layer)
        group._children.append(node)
        node._parent = group

        # Layer checked, group checked → visible
        group.setItemVisibilityChecked(True)
        node.setItemVisibilityChecked(True)
        self.assertTrue(is_layer_visible(layer))

        # Layer unchecked → own state is False
        node.setItemVisibilityChecked(False)
        self.assertFalse(is_layer_visible(layer))

        # KEY: group unchecked but layer still checked → is_layer_visible is True
        # (only own checkbox; group state ignored here)
        group.setItemVisibilityChecked(False)
        node.setItemVisibilityChecked(True)
        self.assertTrue(is_layer_visible(layer))  # own state unaffected by group

    # ------------------------------------------------------------------
    # is_layer_effectively_visible (cascades through ancestor groups)
    # ------------------------------------------------------------------
    def test_is_layer_effectively_visible_with_group(self):
        from layer_model import is_layer_effectively_visible, QgsProject, QgsLayerTreeGroup, QgsLayerTreeLayer

        QgsProject._instance = None
        project = QgsProject.instance()
        root = project.layerTreeRoot()

        group = QgsLayerTreeGroup("Group")
        root._children.append(group)
        group._parent = root

        layer = MagicMock()
        layer.id.return_value = "layer_eff"

        node = QgsLayerTreeLayer(layer)
        group._children.append(node)
        node._parent = group

        # Case 1: Everything visible
        group.setItemVisibilityChecked(True)
        node.setItemVisibilityChecked(True)
        self.assertTrue(is_layer_effectively_visible(layer))

        # Case 2: Layer's own checkbox unchecked
        group.setItemVisibilityChecked(True)
        node.setItemVisibilityChecked(False)
        self.assertFalse(is_layer_effectively_visible(layer))

        # Case 3: Group invisible, layer checkbox checked → effectively invisible
        group.setItemVisibilityChecked(False)
        node.setItemVisibilityChecked(True)
        self.assertFalse(is_layer_effectively_visible(layer))

    # ------------------------------------------------------------------
    # is_group_node_visible helper
    # ------------------------------------------------------------------
    def test_is_group_node_visible(self):
        from layer_model import is_group_node_visible, QgsLayerTreeGroup

        root_grp = QgsLayerTreeGroup("root")
        child_grp = QgsLayerTreeGroup("child")
        root_grp._children.append(child_grp)
        child_grp._parent = root_grp

        # Both visible
        root_grp.setItemVisibilityChecked(True)
        child_grp.setItemVisibilityChecked(True)
        self.assertTrue(is_group_node_visible(child_grp))

        # Child itself invisible
        child_grp.setItemVisibilityChecked(False)
        self.assertFalse(is_group_node_visible(child_grp))

        # Child visible but parent invisible → effectively invisible
        child_grp.setItemVisibilityChecked(True)
        root_grp.setItemVisibilityChecked(False)
        self.assertFalse(is_group_node_visible(child_grp))

        # None input → True (safe default)
        self.assertTrue(is_group_node_visible(None))

    # ------------------------------------------------------------------
    # FolderItem hidden icon overlay
    # ------------------------------------------------------------------
    def test_folder_item_hidden_icon_overlay(self):
        from layer_model import FolderItem, QgsLayerTreeGroup, _create_hidden_folder_icon, _get_folder_icon

        # A visible group node → no overlay
        vis_group = QgsLayerTreeGroup("VisGroup")
        vis_group.setItemVisibilityChecked(True)
        item_vis = FolderItem("VisGroup", is_physical=False, group_node=vis_group)
        # Icon should equal _get_folder_icon without overlay
        expected_vis_icon = _get_folder_icon(False, "VisGroup")
        self.assertIsNotNone(item_vis)
        self.assertEqual(item_vis.group_node, vis_group)

        # An invisible group node → hidden overlay applied (just smoke-test, no crash)
        hid_group = QgsLayerTreeGroup("HidGroup")
        hid_group.setItemVisibilityChecked(False)
        item_hid = FolderItem("HidGroup", is_physical=False, group_node=hid_group)
        self.assertIsNotNone(item_hid)
        self.assertEqual(item_hid.group_node, hid_group)

        # Physical folder → no group_node → no overlay
        item_phys = FolderItem("/some/path", is_physical=True, group_node=None)
        self.assertIsNotNone(item_phys)
        self.assertIsNone(item_phys.group_node)

if __name__ == '__main__':
    unittest.main()


