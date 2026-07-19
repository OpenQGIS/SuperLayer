import unittest
from unittest.mock import MagicMock, patch
import sys
import os

# Include directory in sys.path
sys.path.insert(0, os.path.dirname(__file__))

import layer_board_widget
from layer_board_widget import LayerBoardWidget, Qt

class TestLayerBoardWidget(unittest.TestCase):
    def setUp(self):
        self.iface = MagicMock()
        
    def test_widget_init(self):
        widget = LayerBoardWidget(self.iface)
        self.assertEqual(widget.iface, self.iface)
        self.assertIsNotNone(widget.tab_widget)
        self.assertIsNotNone(widget.vector_table)
        self.assertIsNotNone(widget.raster_table)

    @patch('layer_board_widget.QgsProject.instance')
    def test_populate_tables(self, mock_project_inst):
        # Mock vector layer
        mock_vlayer = MagicMock()
        mock_vlayer.type.return_value = 0 # Vector
        mock_vlayer.id.return_value = "v1"
        mock_vlayer.name.return_value = "VectorLayer"
        mock_vlayer.isSpatial.return_value = True
        mock_vlayer.dataProvider().name.return_value = "ogr"
        mock_vlayer.dataProvider().dataSourceUri.return_value = "v_uri"
        mock_vlayer.listStylesInDatabase.return_value = (0, [], [], [], [])
        
        # Mock non-spatial vector layer
        mock_ns_vlayer = MagicMock()
        mock_ns_vlayer.type.return_value = 0 # Vector
        mock_ns_vlayer.id.return_value = "v2"
        mock_ns_vlayer.name.return_value = "NonSpatialVectorLayer"
        mock_ns_vlayer.isSpatial.return_value = False
        mock_ns_vlayer.dataProvider().name.return_value = "ogr"
        mock_ns_vlayer.dataProvider().dataSourceUri.return_value = "ns_v_uri"
        mock_ns_vlayer.listStylesInDatabase.return_value = (0, [], [], [], [])

        # Mock raster layer
        mock_rlayer = MagicMock()
        mock_rlayer.type.return_value = 1 # Raster
        mock_rlayer.id.return_value = "r1"
        mock_rlayer.name.return_value = "RasterLayer"
        mock_rlayer.dataProvider().dataSourceUri.return_value = "r_uri"
        mock_rlayer.width.return_value = 100
        mock_rlayer.height.return_value = 100
        mock_rlayer.rasterUnitsPerPixelX.return_value = 1
        mock_rlayer.rasterUnitsPerPixelY.return_value = 1
        
        mock_proj = MagicMock()
        mock_proj.mapLayers.return_value = {"v1": mock_vlayer, "v2": mock_ns_vlayer, "r1": mock_rlayer}
        def get_layer(lid):
            if lid == "v1": return mock_vlayer
            if lid == "v2": return mock_ns_vlayer
            return mock_rlayer
        mock_proj.mapLayer.side_effect = get_layer
        mock_project_inst.return_value = mock_proj
        
        widget = LayerBoardWidget(self.iface)
        widget.populateLayerTable('vector')
        widget.populateLayerTable('raster')
        
        # We have 2 vector layers, 1 raster layer
        self.assertEqual(widget.vector_table.rowCount(), 2)
        self.assertEqual(widget.raster_table.rowCount(), 1)
        
        # Check name column value (generic index 1 is name)
        self.assertEqual(widget.vector_table.item(0, 1).data(Qt.EditRole), "VectorLayer")
        self.assertEqual(widget.vector_table.item(1, 1).data(Qt.EditRole), "NonSpatialVectorLayer")
        self.assertEqual(widget.raster_table.item(0, 1).data(Qt.EditRole), "RasterLayer")
        
        # Check spatial-only columns on spatial vs non-spatial layer
        # Index 2 is CRS (spatial_only=True)
        # Spatial layer should have CRS value
        self.assertIsNotNone(widget.vector_table.item(0, 2).data(Qt.EditRole))
        # Non-spatial layer should have None and flags set to Qt.NoItemFlags (0)
        self.assertIsNone(widget.vector_table.item(1, 2).data(Qt.EditRole))
        self.assertEqual(widget.vector_table.item(1, 2)._flags, Qt.NoItemFlags)

    @patch('layer_board_widget.QgsProject.instance')
    def test_on_item_changed(self, mock_project_inst):
        mock_vlayer = MagicMock()
        mock_vlayer.type.return_value = 0
        mock_vlayer.id.return_value = "v1"
        mock_vlayer.name.return_value = "VectorLayer"
        mock_vlayer.isSpatial.return_value = True
        mock_vlayer.dataProvider().name.return_value = "ogr"
        mock_vlayer.dataProvider().dataSourceUri.return_value = "v_uri"
        mock_vlayer.dataProvider().availableEncodings.return_value = ["UTF-8", "GBK"]
        mock_vlayer.dataProvider().encoding.return_value = "UTF-8"
        mock_vlayer.listStylesInDatabase.return_value = (0, [], [], [], [])
        
        mock_proj = MagicMock()
        mock_proj.mapLayers.return_value = {"v1": mock_vlayer}
        mock_proj.mapLayer.return_value = mock_vlayer
        mock_project_inst.return_value = mock_proj
        
        widget = LayerBoardWidget(self.iface)
        widget.populateLayerTable('vector')
        
        # Find 'name' column (col 1)
        item = widget.vector_table.item(0, 1)
        item.setData(Qt.EditRole, "NewName")
        
        # Trigger manually
        widget.onItemChanged('vector', item)
        
        # Verify it was added to changed data cache
        self.assertEqual(widget.layerBoardChangedData['vector']['v1']['name'], "NewName")
        # Verify highlighting is yellow
        self.assertIsNotNone(item.background())
        self.assertEqual(item.background().color()._color_val, Qt.yellow)

    @patch('layer_board_widget.QgsProject.instance')
    @patch('layer_board_widget.QgsVectorLayer')
    def test_on_item_changed_validation(self, mock_qgs_vector_layer, mock_project_inst):
        mock_vlayer = MagicMock()
        mock_vlayer.type.return_value = 0
        mock_vlayer.id.return_value = "v1"
        mock_vlayer.name.return_value = "VectorLayer"
        mock_vlayer.isSpatial.return_value = True
        mock_vlayer.geometryType.return_value = 1
        mock_vlayer.dataProvider().name.return_value = "ogr"
        mock_vlayer.dataProvider().dataSourceUri.return_value = "v_uri"
        mock_vlayer.dataProvider().availableEncodings.return_value = ["UTF-8", "GBK"]
        mock_vlayer.dataProvider().encoding.return_value = "UTF-8"
        mock_vlayer.listStylesInDatabase.return_value = (0, [], [], [], [])
        
        mock_proj = MagicMock()
        mock_proj.mapLayers.return_value = {"v1": mock_vlayer}
        mock_proj.mapLayer.return_value = mock_vlayer
        mock_project_inst.return_value = mock_proj
        
        widget = LayerBoardWidget(self.iface)
        widget.populateLayerTable('vector')
        
        # Mock vector layer probed during URI validation
        mock_nlayer = MagicMock()
        mock_nlayer.isValid.return_value = True
        mock_nlayer.geometryType.return_value = 1
        mock_qgs_vector_layer.return_value = mock_nlayer
        
        # Col 12 is 'source|uri'
        uri_item = widget.vector_table.item(0, 12)
        
        # Test Case 1: Valid source URI changes
        uri_item.setData(Qt.EditRole, "ogr|new_path")
        widget.onItemChanged('vector', uri_item)
        self.assertEqual(widget.layerBoardChangedData['vector']['v1']['source|uri'], "ogr|new_path")
        self.assertEqual(uri_item.background().color()._color_val, Qt.yellow)
        
        # Test Case 2: Invalid source URI (isValid returns False)
        mock_nlayer.isValid.return_value = False
        uri_item.setData(Qt.EditRole, "ogr|bad_path")
        widget.onItemChanged('vector', uri_item)
        # Should restore original
        self.assertEqual(uri_item.data(Qt.EditRole), "ogr|v_uri")
        
        # Test Case 3: Mismatched geometry type (isValid is True but geometryType mismatch)
        mock_nlayer.isValid.return_value = True
        mock_nlayer.geometryType.return_value = 2  # Different from 1
        uri_item.setData(Qt.EditRole, "ogr|geom_mismatch")
        widget.onItemChanged('vector', uri_item)
        # Should restore original
        self.assertEqual(uri_item.data(Qt.EditRole), "ogr|v_uri")
        
        # Col 13 is 'encoding'
        encoding_item = widget.vector_table.item(0, 13)
        
        # Test Case 4: Valid encoding change
        encoding_item.setData(Qt.EditRole, "GBK")
        widget.onItemChanged('vector', encoding_item)
        self.assertEqual(widget.layerBoardChangedData['vector']['v1']['encoding'], "GBK")
        
        # Test Case 5: Invalid encoding (not in available encodings)
        encoding_item.setData(Qt.EditRole, "ISO-8859-1")
        widget.onItemChanged('vector', encoding_item)
        # Should restore original
        self.assertEqual(encoding_item.data(Qt.EditRole), "UTF-8")
        
        # Col 8 is 'shortname'
        shortname_item = widget.vector_table.item(0, 8)
        
        # Test Case 6: Shortname replacement validation (cleaning invalid characters)
        shortname_item.setData(Qt.EditRole, "My-Layer/Short@Name")
        widget.onItemChanged('vector', shortname_item)
        # Expect characters replacing invalid with '_'
        self.assertEqual(shortname_item.data(Qt.EditRole), "My-Layer_Short_Name")
        self.assertEqual(widget.layerBoardChangedData['vector']['v1']['shortname'], "My-Layer_Short_Name")

    @patch('layer_board_widget.QgsProject.instance')
    @patch('layer_board_widget.QgsCoordinateReferenceSystem')
    def test_commit_changes(self, mock_crs_class, mock_project_inst):
        mock_vlayer = MagicMock()
        mock_vlayer.type.return_value = 0
        mock_vlayer.id.return_value = "v1"
        mock_vlayer.name.return_value = "OldName"
        mock_vlayer.isSpatial.return_value = True
        mock_vlayer.dataProvider().name.return_value = "ogr"
        mock_vlayer.dataProvider().dataSourceUri.return_value = "v_uri"
        mock_vlayer.listStylesInDatabase.return_value = (0, [], [], [], [])
        
        mock_crs = MagicMock()
        mock_crs_class.return_value = mock_crs
        
        mock_proj = MagicMock()
        mock_proj.mapLayers.return_value = {"v1": mock_vlayer}
        mock_proj.mapLayer.return_value = mock_vlayer
        mock_project_inst.return_value = mock_proj
        
        widget = LayerBoardWidget(self.iface)
        widget.populateLayerTable('vector')
        
        # Populate changed data manually with various properties
        widget.layerBoardChangedData['vector']["v1"] = {
            "name": "CommittedName",
            "crs": "EPSG:3857",
            "maxScale": "5000",
            "minScale": "100000",
            "source|uri": "ogr|new_uri"
        }
        
        widget.commitLayersChanges('vector')
        
        # Verify changes were applied to the layer
        mock_vlayer.setName.assert_called_with("CommittedName")
        mock_crs_class.assert_called_once()
        mock_crs.createFromOgcWmsCrs.assert_called_with("EPSG:3857")
        mock_vlayer.setCrs.assert_called_with(mock_crs)
        mock_vlayer.toggleScaleBasedVisibility.assert_called_with(True)
        mock_vlayer.setMaximumScale.assert_called_with(5000.0)
        mock_vlayer.setMinimumScale.assert_called_with(100000.0)
        mock_vlayer.writeLayerXML.assert_called_once()
        mock_vlayer.readLayerXML.assert_called_once()
        mock_vlayer.reload.assert_called_once()
        
        # Verify project dirty flag set
        mock_proj.setDirty.assert_called_with(True)

    @patch('layer_board_widget.QgsProject.instance')
    def test_discard_changes(self, mock_project_inst):
        mock_vlayer = MagicMock()
        mock_vlayer.type.return_value = 0
        mock_vlayer.id.return_value = "v1"
        mock_vlayer.name.return_value = "OldName"
        mock_vlayer.isSpatial.return_value = True
        mock_vlayer.dataProvider().name.return_value = "ogr"
        mock_vlayer.dataProvider().dataSourceUri.return_value = "v_uri"
        mock_vlayer.listStylesInDatabase.return_value = (0, [], [], [], [])
        
        mock_proj = MagicMock()
        mock_proj.mapLayers.return_value = {"v1": mock_vlayer}
        mock_proj.mapLayer.return_value = mock_vlayer
        mock_project_inst.return_value = mock_proj
        
        widget = LayerBoardWidget(self.iface)
        widget.populateLayerTable('vector')
        
        # Populate changed data manually
        widget.layerBoardChangedData['vector']["v1"] = {"name": "CommittedName"}
        
        widget.discardLayersChanges('vector')
        
        # Verify setName was NOT called (changes discarded)
        mock_vlayer.setName.assert_not_called()

    @patch('layer_board_widget.QgsProject.instance')
    @patch('layer_board_widget.QgsCoordinateReferenceSystem')
    def test_set_layer_property_fixes(self, mock_crs_class, mock_project_inst):
        mock_vlayer = MagicMock()
        mock_vlayer.type.return_value = 0
        mock_vlayer.id.return_value = "v1"
        mock_vlayer.name.return_value = "OldName"
        mock_vlayer.isSpatial.return_value = True
        mock_vlayer.dataProvider().name.return_value = "ogr"
        mock_vlayer.dataProvider().dataSourceUri.return_value = "v_uri"
        mock_vlayer.listStylesInDatabase.return_value = (0, [], [], [], [])
        
        mock_proj = MagicMock()
        mock_proj.mapLayers.return_value = {"v1": mock_vlayer}
        mock_proj.mapLayer.return_value = mock_vlayer
        mock_project_inst.return_value = mock_proj
        
        widget = LayerBoardWidget(self.iface)
        widget.populateLayerTable = MagicMock()
        
        # Test case 1: repopulate=False does not trigger populateLayerTable
        widget.setLayerProperty('vector', [mock_vlayer], 'name', 'NewName', repopulate=False)
        widget.populateLayerTable.assert_not_called()
        mock_vlayer.setName.assert_called_with('NewName')
        
        # Test case 2: repopulate=True (default) triggers populateLayerTable
        widget.setLayerProperty('vector', [mock_vlayer], 'name', 'NewName2')
        widget.populateLayerTable.assert_called_once_with('vector')
        
        # Reset mocks
        mock_vlayer.reset_mock()
        widget.populateLayerTable.reset_mock()
        
        # Test case 3: Invalid float values for maxScale / minScale do not raise ValueError
        widget.setLayerProperty('vector', [mock_vlayer], 'maxScale', 'invalid_scale')
        mock_vlayer.setMaximumScale.assert_not_called()
        
        widget.setLayerProperty('vector', [mock_vlayer], 'minScale', 'another_invalid_scale')
        mock_vlayer.setMinimumScale.assert_not_called()
        
        # Test case 4: isValid() check on QgsCoordinateReferenceSystem
        mock_crs = MagicMock()
        mock_crs.isValid.return_value = False
        mock_crs_class.return_value = mock_crs
        
        widget.setLayerProperty('vector', [mock_vlayer], 'crs', 'EPSG:INVALID')
        mock_vlayer.setCrs.assert_not_called()
        
        # Test case 5: valid crs sets it
        mock_crs.isValid.return_value = True
        widget.setLayerProperty('vector', [mock_vlayer], 'crs', 'EPSG:4326')
        mock_vlayer.setCrs.assert_called_with(mock_crs)
        
if __name__ == '__main__':
    unittest.main()
