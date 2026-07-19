import unittest
from unittest.mock import MagicMock, patch
import sys
import os

# Include directory in sys.path
sys.path.insert(0, os.path.dirname(__file__))

import layer_board_widget
from layer_board_widget import LayerBoardWidget

class TestLayerBoardWidget(unittest.TestCase):
    def setUp(self):
        self.iface = MagicMock()
        
    def test_widget_init(self):
        widget = LayerBoardWidget(self.iface)
        self.assertEqual(widget.iface, self.iface)
        self.assertIsNotNone(widget.tab_widget)
        self.assertIsNotNone(widget.vector_table)
        self.assertIsNotNone(widget.raster_table)
        
if __name__ == '__main__':
    unittest.main()
