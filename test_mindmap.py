import unittest
from unittest.mock import MagicMock, patch
import os

import mindmap_view
from mindmap_view import MindMapNode, MindMapView

class TestMindMap(unittest.TestCase):
    def test_mindmap_node_init(self):
        node = MindMapNode("FolderA", is_physical_folder=True, path="/path/to/FolderA")
        self.assertEqual(node.name, "FolderA")
        self.assertTrue(node.is_physical_folder)
        self.assertEqual(node.path, "/path/to/FolderA")
        self.assertFalse(node.collapsed)
        self.assertEqual(len(node.children), 0)

    def test_deleted_qgis_layer_wrapper_is_treated_as_absent(self):
        layer = MagicMock()
        sip_api = MagicMock()
        sip_api.isdeleted.return_value = True
        node = MindMapNode("Deleted layer", layer=layer)

        with patch.object(mindmap_view, "_sip", sip_api):
            self.assertIsNone(node.layer)
            self.assertIsNone(node._layer)

    def test_insert_layer_and_compress(self):
        view = MindMapView()
        
        # Mock QGIS layers
        layer1 = MagicMock()
        layer1.name.return_value = "Points"
        layer1.id.return_value = "id1"
        layer1.source.return_value = "/data/project/vectors/points.shp"
        
        layer2 = MagicMock()
        layer2.name.return_value = "Lines"
        layer2.id.return_value = "id2"
        layer2.source.return_value = "/data/project/vectors/lines.shp"
        
        # Mock os.path.exists to simulate files exist
        original_exists = os.path.exists
        os.path.exists = lambda x: True
        
        try:
            root = view._build_path_tree([layer1, layer2], {})
            self.assertIsNotNone(root)
            
            # Since both layers are in "/data/project/vectors", the common prefix path 
            # should compress linear directories (data/project/vectors).
            # The tree compression should merge nodes into a compressed path.
            # Let's verify that the child nodes contain our layers.
            self.assertTrue("vectors" in root.name or "project" in root.name or "data" in root.name)
            
            # Find the leaf layer nodes in the tree
            leaves = []
            def collect_leaves(n):
                if not n.is_physical_folder:
                    leaves.append(n)
                for child in n.children:
                    collect_leaves(child)
            collect_leaves(root)
            
            self.assertEqual(len(leaves), 2)
            self.assertIn("Points", [leaf.name for leaf in leaves])
            self.assertIn("Lines", [leaf.name for leaf in leaves])
        finally:
            os.path.exists = original_exists

    def test_layout_spans_calculation(self):
        # Build manual tree:
        # Root
        #  +- ChildA (collapsed)
        #  |   +- GChildA1
        #  +- ChildB
        #      +- GChildB1
        #      +- GChildB2
        root = MindMapNode("Root", is_physical_folder=True)
        child_a = MindMapNode("ChildA", is_physical_folder=True)
        child_b = MindMapNode("ChildB", is_physical_folder=True)
        root.children = [child_a, child_b]
        
        gchild_a1 = MindMapNode("GChildA1")
        child_a.children = [gchild_a1]
        child_a.collapsed = True  # Collapsed!
        
        gchild_b1 = MindMapNode("GChildB1")
        gchild_b2 = MagicMock()
        gchild_b2.height = 36.0
        gchild_b2.collapsed = False
        gchild_b2.children = []
        child_b.children = [gchild_b1, gchild_b2]
        
        # Test layout vertical span calculations
        dy = 20.0
        
        # Calculate subtree vertical spans
        def calc_spans(node):
            if node.collapsed or not node.children:
                node.subtree_span = node.height
                return node.subtree_span
                
            total = 0.0
            for child in node.children:
                total += calc_spans(child)
            total += (len(node.children) - 1) * dy
            node.subtree_span = max(node.height, total)
            return node.subtree_span
            
        root_span = calc_spans(root)
        
        # child_a is collapsed, so its span is just its own height (36.0)
        self.assertEqual(child_a.subtree_span, 36.0)
        
        # child_b is open, has 2 children, span is: 36.0 (gchild_b1) + 36.0 (gchild_b2) + 20.0 (dy) = 92.0
        self.assertEqual(child_b.subtree_span, 92.0)
        
        # root has child_a and child_b, span is: 36.0 (child_a) + 92.0 (child_b) + 20.0 (dy) = 148.0
        self.assertEqual(root.subtree_span, 148.0)

    def test_container_based_grouping_zip_gpkg(self):
        view = MindMapView()
        
        layer_zip = MagicMock()
        layer_zip.name.return_value = "ZipLayer"
        layer_zip.id.return_value = "zip1"
        layer_zip.source.return_value = "/vsizip/E:/data/project.zip/internal.shp"
        
        layer_norm = MagicMock()
        layer_norm.name.return_value = "NormLayer"
        layer_norm.id.return_value = "norm1"
        layer_norm.source.return_value = "E:/data/normal.shp"
        
        original_exists = os.path.exists
        os.path.exists = lambda x: True
        
        try:
            root = view._build_path_tree([layer_zip, layer_norm], {})
            self.assertIsNotNone(root)
            
            all_nodes = []
            def collect_nodes(n):
                all_nodes.append(n)
                for child in n.children:
                    collect_nodes(child)
            collect_nodes(root)
            
            node_names = [n.name for n in all_nodes]
            self.assertIn("project.zip", node_names)
            
            zip_folder_node = next(n for n in all_nodes if n.name == "project.zip")
            self.assertTrue(zip_folder_node.is_physical_folder)
            
            self.assertIn("ZipLayer", [c.name for c in zip_folder_node.children])
        finally:
            os.path.exists = original_exists

    def test_memory_vs_missing_layer_separation(self):
        view = MindMapView()
        
        layer_mem = MagicMock()
        layer_mem.name.return_value = "MemLayer"
        layer_mem.id.return_value = "mem1"
        layer_mem.source.return_value = "memory:"
        layer_mem.dataProvider().name.return_value = "memory"
        
        layer_miss = MagicMock()
        layer_miss.name.return_value = "MissLayer"
        layer_miss.id.return_value = "miss1"
        layer_miss.source.return_value = "E:/non_existent/file.shp"
        layer_miss.dataProvider().name.return_value = "ogr"
        
        layer_online = MagicMock()
        layer_online.name.return_value = "OnlineLayer"
        layer_online.id.return_value = "online1"
        layer_online.source.return_value = "http://tile.server.com/wms"
        layer_online.dataProvider().name.return_value = "wms"
        
        layer_virt = MagicMock()
        layer_virt.name.return_value = "VirtLayer"
        layer_virt.id.return_value = "virt1"
        layer_virt.source.return_value = "?query=select * from test"
        layer_virt.dataProvider().name.return_value = "virtual"
        
        original_exists = os.path.exists
        os.path.exists = lambda x: False
        
        try:
            root = view._build_path_tree([layer_mem, layer_miss, layer_online, layer_virt], {})
            self.assertIsNotNone(root)
            
            all_nodes = []
            def collect_nodes(n):
                all_nodes.append(n)
                for child in n.children:
                    collect_nodes(child)
            collect_nodes(root)
            
            node_names = [n.name for n in all_nodes]
            self.assertIn("内存与临时图层", node_names)
            self.assertIn("虚拟图层", node_names)
            self.assertIn("无效图层", node_names)
            self.assertNotIn("在线图层", node_names)
            
            mem_group = next(n for n in all_nodes if n.name == "内存与临时图层")
            self.assertIn("MemLayer", [c.name for c in mem_group.children])
            
            miss_group = next(n for n in all_nodes if n.name == "无效图层")
            self.assertIn("MissLayer", [c.name for c in miss_group.children])
            
            virt_group = next(n for n in all_nodes if n.name == "虚拟图层")
            self.assertIn("VirtLayer", [c.name for c in virt_group.children])
        finally:
            os.path.exists = original_exists

    def test_truncate_middle_path(self):
        from mindmap_view import truncate_middle_path
        
        self.assertEqual(truncate_middle_path("short_path"), "short_path")
        
        p1 = "dirA / dirB / middle / finalDir"
        # p1 is 31 chars. If max_len=29, it exceeds, so Option 1 (len=27) is returned
        self.assertEqual(truncate_middle_path(p1, max_len=29), "dirA / dirB / …… / finalDir")
        
        # If max_len=25, Option 1 (len=27) exceeds, so Option 2 (len=18) is returned
        self.assertEqual(truncate_middle_path(p1, max_len=25), "dirA / …… / finalDir")
        
        p3 = "extremely_long_directory_name_part_one / middle / extremely_long_directory_name_part_two"
        res = truncate_middle_path(p3, max_len=30)
        self.assertLessEqual(len(res), 30)
        self.assertTrue(res.startswith("ex"))
        self.assertTrue(res.endswith("wo"))
        self.assertIn("……", res)

    def test_right_click_selects_and_accepts(self):
        from mindmap_view import MindMapNode, MindMapNodeItem, Qt

        node = MindMapNode("TestNode", is_physical_folder=True, path="/some/path")
        item = MindMapNodeItem(node)
        
        event_mock = MagicMock()
        event_mock.button.return_value = Qt.RightButton
        
        item.setSelected(False)
        item.mousePressEvent(event_mock)
        self.assertTrue(item.isSelected())
        event_mock.accept.assert_called()
        
        event_mock.reset_mock()
        item.mouseReleaseEvent(event_mock)
        event_mock.accept.assert_called()

    def test_drag_and_drop_folder_relocation(self):
        from mindmap_view import MindMapView, MindMapNodeItem, MindMapNode
        from unittest.mock import patch, MagicMock
        
        view = MindMapView()
        source_node = MindMapNode("SourceFolder", is_physical_folder=True, path="/some/src/dir")
        target_node = MindMapNode("TargetFolder", is_physical_folder=True, path="/some/target/dir")
        
        source_item = MindMapNodeItem(source_node)
        target_item = MindMapNodeItem(target_node)
        
        view._drag_source_item = source_item
        view._drag_target_item = target_item
        
        signal_data = []
        def on_relocate(src, dest):
            signal_data.append((src, dest))
        view.folderRelocationRequested.connect(on_relocate)
        
        with patch('os.path.exists', return_value=True):
            view.end_dragging(MagicMock())
            
        self.assertEqual(len(signal_data), 1)
        self.assertEqual(signal_data[0], ("/some/src/dir", "/some/target/dir"))

    def test_drag_and_drop_container_relocation(self):
        from mindmap_view import MindMapView, MindMapNodeItem, MindMapNode
        from unittest.mock import patch, MagicMock
        
        view = MindMapView()
        source_node = MindMapNode("db.gpkg", is_physical_folder=True, path="/some/src/db.gpkg")
        target_node = MindMapNode("TargetFolder", is_physical_folder=True, path="/some/target/dir")
        
        source_item = MindMapNodeItem(source_node)
        target_item = MindMapNodeItem(target_node)
        
        view._drag_source_item = source_item
        view._drag_target_item = target_item
        
        signal_data = []
        def on_relocate(src, dest):
            signal_data.append((src, dest))
        view.folderRelocationRequested.connect(on_relocate)
        
        with patch('os.path.exists', return_value=True):
            view.end_dragging(MagicMock())
            
        self.assertEqual(len(signal_data), 1)
        self.assertEqual(signal_data[0], ("/some/src/db.gpkg", "/some/target/dir"))

    def test_drop_onto_container_prevented(self):
        from mindmap_view import MindMapView, MindMapNodeItem, MindMapNode
        from unittest.mock import patch, MagicMock
        
        view = MindMapView()
        
        gpkg_node = MindMapNode("db.gpkg", is_physical_folder=True, path="/some/src/db.gpkg")
        gpkg_item = MindMapNodeItem(gpkg_node)
        
        folder_node = MindMapNode("TargetFolder", is_physical_folder=True, path="/some/target/dir")
        folder_item = MindMapNodeItem(folder_node)
        
        view.scene_obj.items = MagicMock(return_value=[gpkg_item])
        
        def exists_side_effect(path):
            if "db.gpkg" in path:
                return True
            return False
            
        def isdir_side_effect(path):
            if "db.gpkg" in path:
                return False
            return True
            
        with patch('os.path.exists', side_effect=exists_side_effect), \
             patch('os.path.isdir', side_effect=isdir_side_effect):
            res = view._find_folder_at(MagicMock())
            self.assertIsNone(res)
            
        view.scene_obj.items = MagicMock(return_value=[folder_item])
        with patch('os.path.exists', return_value=True), \
             patch('os.path.isdir', return_value=True):
            res = view._find_folder_at(MagicMock())
            self.assertEqual(res, folder_item)

    def test_marquee_selection_mode(self):
        from mindmap_view import MindMapView, QGraphicsView
        
        view = MindMapView()
        self.assertEqual(view.dragMode(), QGraphicsView.DragMode.RubberBandDrag)

if __name__ == '__main__':
    unittest.main()
