# Layer Filtering and Physical Path Context Menu Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Exclude online layers globally from the SuperLayer plugin and support right-click copy folder link / open folder location on the physical path column (Column 2).

**Architecture:** Extend `get_layer_format` to properly categorize virtual, memory, and invalid layers while identifying true online layers. Filter out online layers at data collection points in all views. Adjust right-click event column checks in `QTreeView` to allow context menu trigger on Column 2 and map it to folder actions.

**Tech Stack:** QGIS Python API (PyQGIS), PyQt5 / PySide2 / PySide6.

## Global Constraints
- Target QGIS Python plugin environment.
- Do not import QGIS modules at the top level where it breaks CLI unit tests.
- Support both PyQt5 and QtPy/PySide fallback imports as defined in existing code.
- Ensure all automated tests run and pass using `python -m unittest discover -v`.

---

### Task 1: Layer Classification & Online Layer Filtering in Layer Model

**Files:**
- Modify: `c:/Users/tesla/AppData/Roaming/QGIS/QGIS3/profiles/ForTest/python/plugins/SuperLayer/layer_model.py`

**Interfaces:**
- Consumes: `layer.dataProvider()`, `layer.source()`, `layer.isValid()`
- Produces: Updated `get_layer_format(layer)` returning `"在线图层"`, `"虚拟图层"`, `"临时图层"`, `"不可用图层"`, `"shp"`, `"gpkg"`, etc.

- [ ] **Step 1: Inspect get_layer_format and rebuild_model in layer_model.py**
- [ ] **Step 2: Modify get_layer_format to classify virtual, memory, invalid layers and filter true online layers**
Show modified code for `get_layer_format` starting at line 387:
```python
def get_layer_format(layer):
    if not layer:
        return "其他"
    try:
        if hasattr(layer, 'isValid') and not layer.isValid():
            return "不可用图层"
    except Exception:
        pass
        
    try:
        provider_type = ""
        if hasattr(layer, 'providerType'):
            provider_type = layer.providerType().lower()
        if provider_type == 'virtual':
            return "虚拟图层"
        if provider_type == 'memory':
            return "临时图层"
            
        provider = layer.dataProvider()
        if provider:
            provider_name = provider.name().lower()
            if provider_name == 'virtual':
                return "虚拟图层"
            if provider_name == 'memory':
                return "临时图层"
            if provider_name in ['wms', 'wfs', 'wcs', 'arcgismapserver', 'arcgisfeatureserver', 'tilexyz', 'vectortile']:
                return "在线图层"
    except Exception:
        pass
        
    source = layer.source()
    if not source:
        return "其他"
        
    source_lower = source.lower()
    if source_lower.startswith('http://') or source_lower.startswith('https://') or 'url=' in source_lower:
        return "在线图层"
        
    phys_path, _ = split_qgis_source(source)
    if not phys_path:
        return "其他"
        
    if '.gdb' in source_lower or 'gdb:' in source_lower:
        return "gdb"
    elif '.gpkg' in source_lower or 'gpkg:' in source_lower:
        return "gpkg"
        
    _, ext = os.path.splitext(phys_path)
    if ext:
        ext_clean = ext.lower().lstrip('.')
        if ext_clean in ['shp', 'dbf']:
            return "shp"
        elif ext_clean in ['tif', 'tiff']:
            return "tif"
        return ext_clean
        
    return "其他"
```
- [ ] **Step 3: Modify rebuild_model and _traverse_qgis_tree in layer_model.py to filter out online layers**
Under `rebuild_model`:
```python
        layers = list(project.mapLayers().values())
        # Filter out online layers completely
        layers = [l for l in layers if get_layer_format(l) != "在线图层"]
        if filter_format:
            layers = [l for l in layers if get_layer_format(l) == filter_format]
```
Under `_traverse_qgis_tree`:
```python
            elif isinstance(child, QgsLayerTreeLayer):
                layer = child.layer()
                if layer:
                    # Filter out online layers completely
                    if get_layer_format(layer) == "在线图层":
                        continue
                    if filter_format and get_layer_format(layer) != filter_format:
                        continue
```
- [ ] **Step 4: Run unit tests for layer model**
Run: `python -m unittest test_layer_model.py -v`
Expected: PASS

---

### Task 2: Mindmap View Filtering & Test Correction

**Files:**
- Modify: `c:/Users/tesla/AppData/Roaming/QGIS/QGIS3/profiles/ForTest/python/plugins/SuperLayer/mindmap_view.py`
- Modify: `c:/Users/tesla/AppData/Roaming/QGIS/QGIS3/profiles/ForTest/python/plugins/SuperLayer/test_mindmap.py`

- [ ] **Step 1: Filter out online layers in mindmap_view.py**
Modify `set_layers` in `mindmap_view.py`:
```python
        for layer in layers:
            if not layer:
                continue
                
            # Filter out online layers from mindmap rendering
            source = layer.source()
            source_lower = source.lower()
            is_online = False
            if source_lower.startswith(('http://', 'https://')) or 'url=http' in source_lower or 'type=xyz' in source_lower:
                is_online = True
            else:
                try:
                    if hasattr(layer, 'dataProvider') and layer.dataProvider():
                        prov_name = layer.dataProvider().name().lower()
                        if prov_name in ['wms', 'wfs', 'wcs', 'vectortile', 'arcgisfeatureserver', 'arcgismapserver']:
                            is_online = True
                except Exception:
                    pass
            if is_online:
                continue
```
- [ ] **Step 2: Update test_mindmap.py to verify that online layers are filtered out**
Modify `test_memory_vs_missing_layer_separation` in `test_mindmap.py`:
Remove `"在线图层"` checks, and assert that it is NOT in `node_names`.
```python
            node_names = [n.name for n in all_nodes]
            self.assertIn("内存与临时图层", node_names)
            self.assertIn("虚拟图层", node_names)
            self.assertIn("无效图层", node_names)
            self.assertNotIn("在线图层", node_names)
```
- [ ] **Step 3: Run test_mindmap.py**
Run: `python -m unittest test_mindmap.py -v`
Expected: PASS

---

### Task 3: QGIS Main Dock Integration (Filter Tags & Views Filtering)

**Files:**
- Modify: `c:/Users/tesla/AppData/Roaming/QGIS/QGIS3/profiles/ForTest/python/plugins/SuperLayer/dock_widget.py`

- [ ] **Step 1: Update update_filter_tags in dock_widget.py**
```python
        project = QgsProject.instance()
        formats = set()
        if project:
            for layer in project.mapLayers().values():
                fmt = get_layer_format(layer)
                if fmt and fmt != "在线图层":
                    formats.add(fmt.upper())
```
- [ ] **Step 2: Filter out online layers in switch_view and refresh in dock_widget.py**
Under `switch_view`:
```python
        if project:
            all_layers = list(project.mapLayers().values())
            all_layers = [l for l in all_layers if get_layer_format(l) != "在线图层"]
```
Under `refresh`:
```python
            if project:
                all_layers = list(project.mapLayers().values())
                all_layers = [l for l in all_layers if get_layer_format(l) != "在线图层"]
```
- [ ] **Step 3: Run test_dock_widget.py**
Run: `python -m unittest test_dock_widget.py -v`
Expected: PASS

---

### Task 4: Attribute Board (Layer Board) Filtering

**Files:**
- Modify: `c:/Users/tesla/AppData/Roaming/QGIS/QGIS3/profiles/ForTest/python/plugins/SuperLayer/layer_board_widget.py`

- [ ] **Step 1: Import get_layer_format in layer_board_widget.py**
Import `get_layer_format` inside `populateLayerTable`:
```python
        try:
            from .layer_model import get_layer_format
        except ImportError:
            try:
                from layer_model import get_layer_format
            except ImportError:
                def get_layer_format(l):
                    return "其他"
```
- [ ] **Step 2: Filter out online layers in populateLayerTable**
```python
        lr = QgsProject.instance()
        for lid, layer in lr.mapLayers().items():
            if get_layer_format(layer) == "在线图层":
                continue
            if layerType == 'vector' and layer.type() != QgsMapLayer.VectorLayer:
                continue
```
- [ ] **Step 3: Run test_layer_board.py**
Run: `python -m unittest test_layer_board.py -v`
Expected: PASS

---

### Task 5: Right-Click Context Menu Support for Physical Paths (Column 2)

**Files:**
- Modify: `c:/Users/tesla/AppData/Roaming/QGIS/QGIS3/profiles/ForTest/python/plugins/SuperLayer/dock_widget.py`

- [ ] **Step 1: Update show_physical_tree_context_menu and show_group_tree_context_menu**
Modify `show_physical_tree_context_menu` in `dock_widget.py`:
```python
    def show_physical_tree_context_menu(self, pos):
        idx = self.physical_tree_view.indexAt(pos)
        if idx.isValid():
            model = self.physical_tree_view.model()
            col0_idx = idx.sibling(idx.row(), 0)
            item = model.itemFromIndex(col0_idx)
            if item:
                # If clicking Column 2 or if the item is a physical folder
                if idx.column() == 2 or (isinstance(item, FolderItem) and item.is_physical):
                    folder_path = None
                    if isinstance(item, FolderItem):
                        folder_path = item.folder_path
                    elif isinstance(item, LayerItem) and item.layer:
                        source = item.layer.source()
                        phys_path, _ = split_qgis_source(source)
                        actual_path = resolve_physical_path(phys_path)
                        if actual_path:
                            folder_path = os.path.dirname(actual_path)
                    
                    if folder_path:
                        self._create_folder_context_menu(folder_path, self.physical_tree_view.mapToGlobal(pos))
                elif isinstance(item, LayerItem):
                    self._create_layer_context_menu([item.layer], self.physical_tree_view.mapToGlobal(pos))
```
Modify `show_group_tree_context_menu` in `dock_widget.py`:
```python
    def show_group_tree_context_menu(self, pos):
        idx = self.group_tree_view.indexAt(pos)
        if idx.isValid():
            model = self.group_tree_view.model()
            col0_idx = idx.sibling(idx.row(), 0)
            item = model.itemFromIndex(col0_idx)
            if item:
                # If clicking Column 2
                if idx.column() == 2:
                    folder_path = None
                    if isinstance(item, FolderItem):
                        folder_path = item.folder_path
                    elif isinstance(item, LayerItem) and item.layer:
                        source = item.layer.source()
                        phys_path, _ = split_qgis_source(source)
                        actual_path = resolve_physical_path(phys_path)
                        if actual_path:
                            folder_path = os.path.dirname(actual_path)
                    
                    if folder_path:
                        self._create_folder_context_menu(folder_path, self.group_tree_view.mapToGlobal(pos))
                elif isinstance(item, LayerItem):
                    self._create_layer_context_menu([item.layer], self.group_tree_view.mapToGlobal(pos))
```
- [ ] **Step 2: Run all unit tests**
Run: `python -m unittest discover -v`
Expected: PASS
