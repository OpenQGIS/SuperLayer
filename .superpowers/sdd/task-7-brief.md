### Task 7: Integrate into TreeMapDockWidget

**Files:**
- Modify: `dock_widget.py`
- Modify: `test_dock_widget.py`

**Interfaces:**
- Consumes: `LayerBoardWidget` from Task 6.
- Produces: Integrated menu option "属性看板" in QToolBar triggering view switcher to `self.layer_board_widget` on index 4 of `stacked_widget`.

- [ ] **Step 1: Modify dock_widget.py to load LayerBoardWidget**

Open `dock_widget.py` and modify the toolbar and stacked widget logic.

First, import the new widget:
```python
# In dock_widget.py, import section
try:
    from .layer_board_widget import LayerBoardWidget
except ImportError:
    try:
        from layer_board_widget import LayerBoardWidget
    except ImportError:
        # Mock class for offline tests
        class LayerBoardWidget(QWidget):
            def populateLayerTable(self, t): pass
            def populateAvailableEncodingList(self): pass
```

Add inside `__init__` of `TreeMapDockWidget`:
```python
        # Inside __init__ in dock_widget.py, around line 460
        self.treemap_view = TreeMapWidget()
        self.mindmap_view = MindMapView()
        self.layer_board_view = LayerBoardWidget(self.iface) # NEW PAGE
        
        self.stacked_widget.addWidget(self.physical_tree_view)
        self.stacked_widget.addWidget(self.group_tree_view)
        self.stacked_widget.addWidget(self.treemap_view)
        self.stacked_widget.addWidget(self.mindmap_view)
        self.stacked_widget.addWidget(self.layer_board_view) # NEW PAGE
```

Add in `_setup_toolbar`:
```python
        # Inside _setup_toolbar in dock_widget.py, around line 560
        self.act_mindmap = QAction("思维导图", self)
        self.act_mindmap.setCheckable(True)
        self.act_mindmap.triggered.connect(lambda: self.switch_view(3))
        self.view_group.addAction(self.act_mindmap)
        self.toolbar.addAction(self.act_mindmap)
        
        # Add new Attribute Board Action
        self.act_layer_board = QAction("属性看板", self)
        self.act_layer_board.setCheckable(True)
        self.act_layer_board.triggered.connect(lambda: self.switch_view(4))
        self.view_group.addAction(self.act_layer_board)
        self.toolbar.addAction(self.act_layer_board)
```

Update `switch_view`:
```python
    # Modify switch_view in dock_widget.py
    def switch_view(self, index):
        self.act_physical_tree.setChecked(index == 0)
        self.act_group_tree.setChecked(index == 1)
        self.act_treemap.setChecked(index == 2)
        self.act_mindmap.setChecked(index == 3)
        self.act_layer_board.setChecked(index == 4) # NEW
        self.stacked_widget.setCurrentIndex(index)
        
        filter_str = self.current_filter_format.lower() if self.current_filter_format else None
        project = QgsProject.instance()
        layers = []
        if project:
            all_layers = list(project.mapLayers().values())
            if filter_str:
                try:
                    from .layer_model import get_layer_format
                except ImportError:
                    def get_layer_format(l):
                        source = getattr(l, 'source', lambda: '')()
                        if source.endswith('.shp'): return 'shp'
                        if source.endswith('.tif'): return 'tif'
                        return 'other'
                layers = [l for l in all_layers if get_layer_format(l) == filter_str]
            else:
                layers = all_layers
                
        if index == 2:
            self.treemap_view.set_layers(layers)
        elif index == 3:
            self.mindmap_view.set_layers(layers)
        elif index == 4:
            # Refresh Attribute Board when switched to
            self.layer_board_view.populateLayerTable('vector')
            self.layer_board_view.populateLayerTable('raster')
            self.layer_board_view.populateAvailableEncodingList()
```

Update `refresh`:
```python
    # Update refresh in dock_widget.py
    def refresh(self):
        self._is_refreshing = True
        try:
            self.update_filter_tags()
            filter_str = self.current_filter_format.lower() if self.current_filter_format else None
            
            # 1. Rebuild physical tree model
            self.physical_model.rebuild_model(group_by_physical=True, filter_format=filter_str)
            
            # 2. Rebuild group tree model
            self.group_model.rebuild_model(group_by_physical=False, filter_format=filter_str)
            
            # 3. Re-apply column widths (model rebuild resets them)
            self._apply_column_widths()
            
            # Expand physical tree recursively, keep group tree collapsed
            self.physical_tree_view.expandAll()
            self.group_tree_view.collapseAll()
            
            project = QgsProject.instance()
            layers = []
            if project:
                all_layers = list(project.mapLayers().values())
                if filter_str:
                    try:
                        from .layer_model import get_layer_format
                    except ImportError:
                        def get_layer_format(l):
                            source = getattr(l, 'source', lambda: '')()
                            if source.endswith('.shp'): return 'shp'
                            if source.endswith('.tif'): return 'tif'
                            return 'other'
                        layers = [l for l in all_layers if get_layer_format(l) == filter_str]
                else:
                    layers = all_layers
            
            if self.stacked_widget.currentIndex() == 2:
                self.treemap_view.set_layers(layers)
            elif self.stacked_widget.currentIndex() == 3:
                self.mindmap_view.set_layers(layers)
            elif self.stacked_widget.currentIndex() == 4:
                self.layer_board_view.populateLayerTable('vector')
                self.layer_board_view.populateLayerTable('raster')
                self.layer_board_view.populateAvailableEncodingList()
        finally:
            self._is_refreshing = False
```

- [ ] **Step 2: Add integration checks in test_dock_widget.py**

Modify `test_dock_widget.py` to check page 4 (index 4) switches correctly:
```python
    # Add inside TestDockWidget in test_dock_widget.py

    def test_switch_view_layer_board(self):
        with patch('dock_widget.LayerTreeModel'), \
             patch('dock_widget.TreeMapWidget'), \
             patch('dock_widget.MindMapView'), \
             patch('dock_widget.LayerBoardWidget') as mock_lb_cls:
            
            mock_lb = MagicMock()
            mock_lb_cls.return_value = mock_lb
            
            dock = TreeMapDockWidget(self.iface, self.parent)
            
            # Switch to Attribute Board (index 4)
            dock.switch_view(4)
            self.assertTrue(dock.act_layer_board.isChecked())
            self.assertEqual(dock.stacked_widget.currentIndex(), 4)
            mock_lb.populateLayerTable.assert_any_call('vector')
            mock_lb.populateLayerTable.assert_any_call('raster')
            mock_lb.populateAvailableEncodingList.assert_called_once()
```

- [ ] **Step 3: Run the entire test suite**

Run: `python -m unittest discover -p "test_*.py"`
Expected output: Ran 63 tests. OK.

- [ ] **Step 4: Commit**

```bash
git add dock_widget.py test_dock_widget.py
git commit -m "feat: integrate LayerBoardWidget into TreeMapDockWidget view stack and toolbar"
```
