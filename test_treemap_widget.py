import unittest
import os
import tempfile
import shutil
from unittest.mock import MagicMock
import treemap_widget
from treemap_widget import TreeMapNode, TreeMapWidget, Signal, QPoint, QRectF

class TestTreeMapWidget(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.src_dir = os.path.join(self.temp_dir.name, 'src')
        os.makedirs(self.src_dir)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_tree_map_node(self):
        layer = MagicMock()
        node = TreeMapNode(layer, 100, "dummy_path")
        self.assertEqual(node.layer, layer)
        self.assertEqual(node.size, 100)
        self.assertEqual(node.path, "dummy_path")
        self.assertIsInstance(node.rect, QRectF)

    def test_worst_aspect_ratio(self):
        widget = TreeMapWidget()
        widget.resize(800, 600)
        
        # Test empty row returns infinity
        self.assertEqual(widget._worst_aspect_ratio([], QRectF(0, 0, 800, 600), 1000), float('inf'))
        
        # Test normal calculations
        node1 = TreeMapNode(MagicMock(), 4000, "path1")
        node2 = TreeMapNode(MagicMock(), 2000, "path2")
        
        rect = QRectF(0, 0, 800, 600)
        worst_ratio = widget._worst_aspect_ratio([node1, node2], rect, 6000)
        self.assertGreater(worst_ratio, 0)
        self.assertNotEqual(worst_ratio, float('inf'))

    def test_squarify_layout(self):
        # Create temp files representing layers
        file1 = os.path.join(self.src_dir, "file1.shp")
        file2 = os.path.join(self.src_dir, "file2.shp")
        file3 = os.path.join(self.src_dir, "file3.shp")
        
        with open(file1, 'wb') as f:
            f.write(b'a' * 1000000)
        with open(file2, 'wb') as f:
            f.write(b'b' * 500000)
        with open(file3, 'wb') as f:
            f.write(b'c' * 250000)
            
        layer1 = MagicMock()
        layer1.source.return_value = file1
        layer1.name.return_value = "Layer A"
        layer1.id.return_value = "id1"
        
        layer2 = MagicMock()
        layer2.source.return_value = file2
        layer2.name.return_value = "Layer B"
        layer2.id.return_value = "id2"
        
        layer3 = MagicMock()
        layer3.source.return_value = file3
        layer3.name.return_value = "Layer C"
        layer3.id.return_value = "id3"
        
        widget = TreeMapWidget()
        widget.resize(800, 600)
        widget.set_layers([layer1, layer2, layer3])
        
        self.assertEqual(len(widget.nodes), 3)
        self.assertEqual(widget.nodes[0].layer, layer1)
        self.assertEqual(widget.nodes[1].layer, layer2)
        self.assertEqual(widget.nodes[2].layer, layer3)
        
        # Verify node geometry coordinates
        # Sum of sizes is 1,750,000 bytes
        # Ratio is 4:2:1 (approx 1,000,000 : 500,000 : 250,000)
        # Check that rects have non-zero width and height and they fit within the widget size
        for node in widget.nodes:
            self.assertGreater(node.rect.width(), 0)
            self.assertGreater(node.rect.height(), 0)
            self.assertGreaterEqual(node.rect.x(), -1e-5)
            self.assertGreaterEqual(node.rect.y(), -1e-5)
            self.assertLessEqual(node.rect.x() + node.rect.width(), 800.001)
            self.assertLessEqual(node.rect.y() + node.rect.height(), 600.001)

    def test_duplicate_layer_sources_share_one_physical_size(self):
        shared_file = os.path.join(self.src_dir, "shared.shp")
        with open(shared_file, 'wb') as f:
            f.write(b'a' * 1200)

        layers = []
        for index in range(3):
            layer = MagicMock()
            layer.isValid.return_value = True
            layer.source.return_value = shared_file
            layer.name.return_value = f"Shared {index}"
            layer.id.return_value = f"shared-{index}"
            layers.append(layer)

        widget = TreeMapWidget()
        widget.resize(800, 600)
        widget.set_layers(layers)

        self.assertEqual(len(widget.nodes), 3)
        self.assertAlmostEqual(sum(node.size for node in widget.nodes), 1200)
        for node in widget.nodes:
            self.assertEqual(node.physical_size, 1200)
            self.assertEqual(node.reference_count, 3)
            self.assertAlmostEqual(node.size, 400)
            self.assertGreater(node.rect.width(), 0)
            self.assertGreater(node.rect.height(), 0)

    def test_leave_event(self):
        widget = TreeMapWidget()
        dummy_node = TreeMapNode(MagicMock(), 100, "dummy_path")
        widget.hovered_node = dummy_node
        
        # Mock QToolTip.hideText and widget.update
        import treemap_widget
        orig_hide_text = treemap_widget.QToolTip.hideText
        treemap_widget.QToolTip.hideText = MagicMock()
        widget.update = MagicMock()
        
        try:
            widget.leaveEvent(MagicMock())
            self.assertIsNone(widget.hovered_node)
            treemap_widget.QToolTip.hideText.assert_called_once()
            widget.update.assert_called_once()
        finally:
            treemap_widget.QToolTip.hideText = orig_hide_text

    def test_invalid_layers_filtered(self):
        # Setup files for layers
        file_valid = os.path.join(self.src_dir, "valid.shp")
        with open(file_valid, 'wb') as f:
            f.write(b'a' * 100)
            
        layer_valid = MagicMock()
        layer_valid.source.return_value = file_valid
        layer_valid.name.return_value = "Valid Layer"
        layer_valid.id.return_value = "valid_id"
        layer_valid.isValid.return_value = True

        layer_invalid = MagicMock()
        layer_invalid.source.return_value = file_valid
        layer_invalid.name.return_value = "Invalid Layer"
        layer_invalid.id.return_value = "invalid_id"
        layer_invalid.isValid.return_value = False

        widget = TreeMapWidget()
        widget.resize(800, 600)
        widget.set_layers([layer_valid, layer_invalid, None])

        self.assertEqual(len(widget.nodes), 1)
        self.assertEqual(widget.nodes[0].layer, layer_valid)

    def test_get_text_width(self):
        fm = MagicMock()
        # Test horizontalAdvance fallback to width
        del fm.horizontalAdvance
        fm.width.return_value = 50
        self.assertEqual(treemap_widget.get_text_width(fm, "hello"), 50)
        
        # Test fallback to len * 8
        del fm.width
        self.assertEqual(treemap_widget.get_text_width(fm, "hello"), 40)

    def test_elide_text(self):
        fm = MagicMock()
        del fm.elidedText
        # Test fallback logic in elide_text
        self.assertEqual(treemap_widget.elide_text(fm, "abcdefgh", 1, 80), "abcdefgh")
        self.assertEqual(treemap_widget.elide_text(fm, "abcdefgh", 1, 40), "ab...")

    def test_format_treemap_text(self):
        fm = MagicMock()
        fm.lineSpacing.return_value = 15
        fm.height.return_value = 15
        
        # Mock width calculation to return len(text) * 8
        del fm.horizontalAdvance
        del fm.width
        del fm.elidedText
        
        # Case 1: Short name, fits in 1 line of name, size on line 2
        # w = 80 (fits 10 chars), h = 35 (max_lines = 2)
        # max_name_lines = 1
        res = treemap_widget.format_treemap_text("short", "100 B", 80, 35, fm)
        self.assertEqual(res, ["short", "100 B"])
        
        # Case 2: Only 1 line available total, show elided name
        # w = 40 (fits 5 chars), h = 15 (max_lines = 1)
        res = treemap_widget.format_treemap_text("verylongname", "100 B", 40, 15, fm)
        self.assertEqual(res, ["ve..."])
        
        # Case 3: Wrapping name across multiple lines
        # w = 40 (fits 5 chars), h = 50 (max_lines = 3, max_name_lines = 2)
        # Name is "12345678" -> should wrap to ["12345", "678"] which is <= 2 lines.
        res = treemap_widget.format_treemap_text("12345678", "100 B", 40, 50, fm)
        self.assertEqual(res, ["12345", "678", "100 B"])
        
        # Case 4: Wrapping and elision
        # w = 40 (fits 5 chars), h = 50 (max_lines = 3, max_name_lines = 2)
        # Name is "123456789012" -> wrapped to ["12345", "67890", "12"] (3 lines).
        # Since max_name_lines = 2, first line is "12345", and second line is remaining "6789012" elided to fit 40px (5 chars max) -> "67..."
        res = treemap_widget.format_treemap_text("123456789012", "100 B", 40, 50, fm)
        self.assertEqual(res, ["12345", "67...", "100 B"])


if __name__ == '__main__':
    unittest.main()
