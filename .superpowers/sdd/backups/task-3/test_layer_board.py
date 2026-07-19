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
        
if __name__ == '__main__':
    unittest.main()
