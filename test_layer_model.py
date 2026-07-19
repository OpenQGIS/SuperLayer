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
        self.assertEqual(format_size(0), "N/A")
        self.assertEqual(format_size(-100), "N/A")
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

if __name__ == '__main__':
    unittest.main()
