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
        self.assertIsNotNone(widget.right_tab_widget)
        self.assertEqual(len(widget.right_tab_widget.tabs), 4)
        self.assertEqual(widget.right_tab_widget.tabs[0][1], "图层操作")
        self.assertEqual(widget.right_tab_widget.tabs[1][1], "图层样式")
        self.assertEqual(widget.right_tab_widget.tabs[2][1], "数据导出")
        self.assertEqual(widget.right_tab_widget.tabs[3][1], "操作日志")

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

    @patch('layer_board_widget.QgsProject.instance')
    def test_remove_ghost_layers(self, mock_project_inst):
        mock_vlayer = MagicMock()
        mock_vlayer.id.return_value = "v1"
        mock_vlayer.type.return_value = 0
        mock_vlayer.name.return_value = "VectorLayer"
        mock_vlayer.isSpatial.return_value = True
        mock_vlayer.dataProvider().name.return_value = "ogr"
        mock_vlayer.dataProvider().dataSourceUri.return_value = "v_uri"
        mock_vlayer.listStylesInDatabase.return_value = (0, [], [], [], [])
        
        mock_proj = MagicMock()
        mock_proj.mapLayers.return_value = {"v1": mock_vlayer}
        mock_project_inst.return_value = mock_proj
        
        widget = LayerBoardWidget(self.iface)
        
        # Force it to be a ghost layer by patching is_ghost_layer
        widget.is_ghost_layer = MagicMock(return_value=True)
        widget.removeGhostLayers()
        
        # Verify it was removed
        mock_proj.removeMapLayer.assert_called_with("v1")

    @patch('layer_board_widget.QgsProject.instance')
    def test_apply_property_on_selected_layers(self, mock_project_inst):
        mock_vlayer = MagicMock()
        mock_vlayer.type.return_value = 0
        mock_vlayer.id.return_value = "v1"
        mock_vlayer.name.return_value = "VectorLayer"
        mock_vlayer.isSpatial.return_value = True
        mock_vlayer.dataProvider().name.return_value = "ogr"
        mock_vlayer.dataProvider().dataSourceUri.return_value = "v_uri"
        mock_vlayer.dataProvider().availableEncodings.return_value = ["UTF-8", "GBK"]
        mock_vlayer.listStylesInDatabase.return_value = (0, [], [], [], [])
        
        mock_proj = MagicMock()
        mock_proj.mapLayers.return_value = {"v1": mock_vlayer}
        mock_proj.mapLayer.return_value = mock_vlayer
        mock_project_inst.return_value = mock_proj
        
        widget = LayerBoardWidget(self.iface)
        widget.populateLayerTable('vector')
        
        # Mock row selection (row 0 is selected)
        class MockIndex:
            def __init__(self, r): self._row = r
            def row(self): return self._row
        widget.vector_table._selected_rows = [MockIndex(0)]
        
        # Test Case 1: CRS Apply
        widget.inCrs.setText("EPSG:3857")
        widget.applyPropertyOnSelectedLayers('crs')
        
        # Verify the CRS column in the table is updated
        crs_col = next(i for i, attr in enumerate(widget.layersAttributes['vector']) if attr['key'] == 'crs')
        self.assertEqual(widget.vector_table.item(0, crs_col).data(Qt.EditRole), "EPSG:3857")
        self.assertEqual(widget.layerBoardChangedData['vector']['v1']['crs'], "EPSG:3857")
        
        # Test Case 2: Max Scale Apply
        widget.inMaxScale.setText("1000")
        widget.applyPropertyOnSelectedLayers('maxScale')
        max_scale_col = next(i for i, attr in enumerate(widget.layersAttributes['vector']) if attr['key'] == 'maxScale')
        self.assertEqual(widget.vector_table.item(0, max_scale_col).data(Qt.EditRole), "1000")
        
        # Test Case 3: Encoding Apply
        widget.inEncodingList.setCurrentText("GBK")
        widget.applyPropertyOnSelectedLayers('encoding')
        enc_col = next(i for i, attr in enumerate(widget.layersAttributes['vector']) if attr['key'] == 'encoding')
        self.assertEqual(widget.vector_table.item(0, enc_col).data(Qt.EditRole), "GBK")
        
        # Test Case 4: Min Scale Apply
        widget.inMinScale.setText("200000")
        widget.applyPropertyOnSelectedLayers('minScale')
        min_scale_col = next(i for i, attr in enumerate(widget.layersAttributes['vector']) if attr['key'] == 'minScale')
        self.assertEqual(widget.vector_table.item(0, min_scale_col).data(Qt.EditRole), "200000")
        self.assertEqual(widget.layerBoardChangedData['vector']['v1']['minScale'], "200000")

    @patch('layer_board_widget.QgsProject.instance')
    def test_perform_action_on_selected_layers(self, mock_project_inst):
        mock_vlayer = MagicMock()
        mock_vlayer.type.return_value = 0 # Vector
        mock_vlayer.id.return_value = "v1"
        mock_vlayer.name.return_value = "VectorLayer"
        mock_vlayer.isSpatial.return_value = True
        mock_vlayer.providerType.return_value = "ogr"
        mock_vlayer.dataProvider().name.return_value = "ogr"
        mock_vlayer.dataProvider().dataSourceUri.return_value = "v_uri"
        mock_vlayer.listStylesInDatabase.return_value = (0, [], [], [], [])
        
        mock_proj = MagicMock()
        mock_proj.mapLayers.return_value = {"v1": mock_vlayer}
        mock_proj.mapLayer.return_value = mock_vlayer
        mock_project_inst.return_value = mock_proj
        
        widget = LayerBoardWidget(self.iface)
        widget.populateLayerTable('vector')
        
        # Select row 0
        class MockIndex:
            def __init__(self, r): self._row = r
            def row(self): return self._row
        widget.vector_table._selected_rows = [MockIndex(0)]
        
        # Test saveStyleAsDefault (ogr provider)
        widget.performActionOnSelectedLayers('saveStyleAsDefault')
        mock_vlayer.saveDefaultStyle.assert_called_once()
        
        # Test saveStyleAsDefault (postgres provider)
        mock_vlayer.providerType.return_value = 'postgres'
        widget.performActionOnSelectedLayers('saveStyleAsDefault')
        mock_vlayer.saveStyleToDatabase.assert_called_once()
        
        # Test createSpatialIndex
        # Mock provider capabilities to support CreateSpatialIndex
        mock_vlayer.dataProvider().capabilities.return_value = layer_board_widget.QgsVectorDataProvider.CreateSpatialIndex
        widget.performActionOnSelectedLayers('createSpatialIndex')
        mock_vlayer.dataProvider().createSpatialIndex.assert_called_once()
        
        # Test removeLayer
        widget.performActionOnSelectedLayers('removeLayer')
        mock_proj.removeMapLayer.assert_called_with("v1")
        mock_proj.setDirty.assert_called_with(True)

    @patch('layer_board_widget.QgsProject.instance')
    def test_perform_action_remove_multiple_layers(self, mock_project_inst):
        mock_vlayer1 = MagicMock()
        mock_vlayer1.type.return_value = 0
        mock_vlayer1.id.return_value = "v1"
        mock_vlayer1.name.return_value = "VL1"
        mock_vlayer1.isSpatial.return_value = True
        mock_vlayer1.dataProvider().name.return_value = "ogr"
        mock_vlayer1.dataProvider().dataSourceUri.return_value = "v_uri1"
        mock_vlayer1.listStylesInDatabase.return_value = (0, [], [], [], [])
        
        mock_vlayer2 = MagicMock()
        mock_vlayer2.type.return_value = 0
        mock_vlayer2.id.return_value = "v2"
        mock_vlayer2.name.return_value = "VL2"
        mock_vlayer2.isSpatial.return_value = True
        mock_vlayer2.dataProvider().name.return_value = "ogr"
        mock_vlayer2.dataProvider().dataSourceUri.return_value = "v_uri2"
        mock_vlayer2.listStylesInDatabase.return_value = (0, [], [], [], [])
        
        mock_proj = MagicMock()
        mock_proj.mapLayers.return_value = {"v1": mock_vlayer1, "v2": mock_vlayer2}
        mock_proj.mapLayer.side_effect = lambda lid: mock_vlayer1 if lid == "v1" else mock_vlayer2
        mock_project_inst.return_value = mock_proj
        
        widget = LayerBoardWidget(self.iface)
        widget.populateLayerTable('vector')
        
        removed_rows = []
        widget.vector_table.removeRow = lambda r: removed_rows.append(r)
        
        class MockIndex:
            def __init__(self, r): self._row = r
            def row(self): return self._row
            
        widget.vector_table._selected_rows = [MockIndex(0), MockIndex(1)]
        
        widget.performActionOnSelectedLayers('removeLayer')
        self.assertEqual(removed_rows, [1, 0])

    @patch('layer_board_widget.QgsProject.instance')
    def test_on_tab_changed(self, mock_project_inst):
        widget = LayerBoardWidget(self.iface)
        
        # Force tab index to 0 (vector)
        widget.tab_widget.currentIndex = MagicMock(return_value=0)
        widget.onTabChanged()
        self.assertTrue(widget.encodingLabel.isEnabled())
        
        # Force tab index to 1 (raster)
        widget.tab_widget.currentIndex = MagicMock(return_value=1)
        widget.onTabChanged()
        self.assertFalse(widget.encodingLabel.isEnabled())
        self.assertFalse(widget.inEncodingList.isEnabled())

    def test_choose_projection(self):
        import types
        mock_dialog_class = MagicMock()
        mock_dialog = MagicMock()
        mock_dialog_class.return_value = mock_dialog
        mock_dialog.exec_.return_value = True
        
        mock_crs = MagicMock()
        mock_crs.authid.return_value = "EPSG:3857"
        mock_dialog.crs.return_value = mock_crs
        
        mock_gui = types.ModuleType('qgis.gui')
        mock_gui.QgsProjectionSelectionDialog = mock_dialog_class
        
        mock_qgis = types.ModuleType('qgis')
        mock_qgis.gui = mock_gui
        
        with patch.dict('sys.modules', {'qgis': mock_qgis, 'qgis.gui': mock_gui}):
            widget = LayerBoardWidget(self.iface)
            widget.chooseProjection()
            self.assertEqual(widget.inCrs.text(), "EPSG:3857")

    @patch('layer_board_widget.QgsProject.instance')
    def test_set_selected_layer_style_widget(self, mock_project_inst):
        # 1. Mock vector layer and project
        mock_vlayer = MagicMock()
        mock_vlayer.type.return_value = 0 # VectorLayer
        mock_vlayer.id.return_value = "v1"
        mock_vlayer.name.return_value = "VectorLayer"
        mock_vlayer.isSpatial.return_value = True
        mock_vlayer.crs().authid.return_value = "EPSG:4326"
        mock_vlayer.maximumScale.return_value = 5000
        mock_vlayer.minimumScale.return_value = 100000
        mock_vlayer.dataProvider().name.return_value = "ogr"
        mock_vlayer.dataProvider().dataSourceUri.return_value = "v_uri"
        mock_vlayer.dataProvider().encoding.return_value = "UTF-8"
        mock_vlayer.listStylesInDatabase.return_value = (0, [], [], [], [])
        
        mock_proj = MagicMock()
        mock_proj.mapLayers.return_value = {"v1": mock_vlayer}
        mock_proj.mapLayer.return_value = mock_vlayer
        mock_project_inst.return_value = mock_proj
        
        widget = LayerBoardWidget(self.iface)
        widget.populateLayerTable('vector')
        
        # 2. Mock selection model and selectedRows to return single vector layer row
        class MockIndex:
            def __init__(self, r): self._row = r
            def row(self): return self._row
            
        mock_sm = MagicMock()
        mock_sm.selectedRows.return_value = [MockIndex(0)]
        widget.vector_table.selectionModel = MagicMock(return_value=mock_sm)
        
        # Call it
        widget.setSelectedLayerStyleWidget('vector')
        
        # Assertions
        self.assertEqual(widget.styleLayer, mock_vlayer)
        self.assertIsNotNone(widget.styleWidget)
        
        # Check that single selection populated the batch update fields
        self.assertEqual(widget.inCrs.text(), "EPSG:4326")
        self.assertEqual(widget.inMaxScale.text(), "5000")
        self.assertEqual(widget.inMinScale.text(), "100000")
        self.assertEqual(widget.inEncodingList.currentText(), "UTF-8")
        
        # 3. Test multiple rows selected clears styling and inputs
        mock_sm.selectedRows.return_value = [MockIndex(0), MockIndex(1)]
        widget.setSelectedLayerStyleWidget('vector')
        self.assertIsNone(widget.styleLayer)
        self.assertIsNone(widget.styleWidget)
        self.assertEqual(widget.inCrs.text(), "")
        self.assertEqual(widget.inMaxScale.text(), "")
        self.assertEqual(widget.inMinScale.text(), "")
        self.assertEqual(widget.inEncodingList.currentText(), "---")
        
        # 4. Test no rows selected clears styling and inputs
        widget.inCrs.setText("EPSG:3857")
        mock_sm.selectedRows.return_value = []
        widget.setSelectedLayerStyleWidget('vector')
        self.assertIsNone(widget.styleLayer)
        self.assertIsNone(widget.styleWidget)
        self.assertEqual(widget.inCrs.text(), "")
        
        # 5. Test raster layer selected does not set styleWidget (only VectorLayer supported)
        # Mock raster layer
        mock_rlayer = MagicMock()
        mock_rlayer.type.return_value = 1 # RasterLayer
        mock_rlayer.id.return_value = "r1"
        mock_rlayer.name.return_value = "RasterLayer"
        mock_rlayer.dataProvider().dataSourceUri.return_value = "r_uri"
        mock_rlayer.width.return_value = 100
        mock_rlayer.height.return_value = 100
        
        mock_proj.mapLayers.return_value = {"r1": mock_rlayer}
        mock_proj.mapLayer.return_value = mock_rlayer
        widget.populateLayerTable('raster')
        
        mock_sm_raster = MagicMock()
        mock_sm_raster.selectedRows.return_value = [MockIndex(0)]
        widget.raster_table.selectionModel = MagicMock(return_value=mock_sm_raster)
        
        widget.setSelectedLayerStyleWidget('raster')
        self.assertEqual(widget.styleLayer, mock_rlayer)
        self.assertIsNone(widget.styleWidget)

    def test_apply_style(self):
        widget = LayerBoardWidget(self.iface)
        
        # 1. No styleWidget / styleLayer
        widget.applyStyle() # Should return gracefully without error
        
        # 2. With styleWidget and styleLayer
        mock_style_widget = MagicMock()
        mock_layer = MagicMock()
        
        widget.styleWidget = mock_style_widget
        widget.styleLayer = mock_layer
        
        widget.applyStyle()
        
        # Check calls
        mock_style_widget.apply.assert_called_once()
        mock_layer.setCacheImage.assert_called_once_with(None)
        mock_layer.triggerRepaint.assert_called_once()

    @patch('layer_board_widget.QFileDialog.getSaveFileName')
    def test_export_to_csv(self, mock_save_file):
        import tempfile
        # Create a temporary file and get its path
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.csv')
        temp_path = temp_file.name
        temp_file.close() # Close it so we can write to it in exportToCsv
        
        try:
            mock_save_file.return_value = (temp_path, "CSV (*.csv)")
            widget = LayerBoardWidget(self.iface)
            widget.getActiveLayerType = MagicMock(return_value='vector')
            widget.layerBoardData['vector'] = [
                ['id', 'name', 'crs'],
                ['v1', 'Layer 1', 'EPSG:4326']
            ]
            
            widget.exportToCsv()
            
            # Read the file and assert content
            with open(temp_path, 'r', encoding='utf-8') as f:
                content = f.read()
            # Since quoting=csv.QUOTE_ALL, the output should be quoted
            self.assertIn('"id","name","crs"', content.replace('\r\n', '\n').replace('\r', '\n'))
            self.assertIn('"v1","Layer 1","EPSG:4326"', content.replace('\r\n', '\n').replace('\r', '\n'))
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)

    def test_log_functions(self):
        widget = LayerBoardWidget(self.iface)
        widget.clearLog()
        widget.updateLog("Test Message")
        # Since it's plain QWidget or mock QTextEdit on CLI, let's verify mock compatibility
        self.assertIsNotNone(widget.txtLog)

if __name__ == '__main__':
    unittest.main()
