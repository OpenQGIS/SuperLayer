# Task 2: Codebase & Metadata Renames

**Goal:** Update all Python class names, metadata descriptors, display names, and icon paths in the main codebase files to use the name `SuperLayer` or `SuperLayerPlugin` / `SuperLayerDockWidget`.

**Files:**
- Modify: `__init__.py`
- Modify: `metadata.txt`
- Modify: `main_plugin.py`
- Modify: `dock_widget.py`

**Instructions:**
1. Update `__init__.py`:
   - Replace import of `TreeMapLayerManagerPlugin` with `SuperLayerPlugin`.
   - Update `classFactory` to instantiate and return `SuperLayerPlugin`.
2. Update `metadata.txt`:
   - Change `name=树状图层管理器` to `name=SuperLayer`.
   - Change `icon=icons/TreeMap_Layer_Manager.svg` to `icon=icons/SuperLayer.svg`.
   - In descriptions or version logs inside `metadata.txt`, rename `树状图层管理器` to `SuperLayer` and `TreeMap Layer Manager` to `SuperLayer`.
3. Update `main_plugin.py`:
   - Rename class `TreeMapLayerManagerPlugin` to `SuperLayerPlugin`.
   - Update docstring to `SuperLayer QGIS Plugin integration class.`.
   - Update imported `TreeMapDockWidget` class name to `SuperLayerDockWidget`.
   - Change icon path from `TreeMap_Layer_Manager.svg` to `SuperLayer.svg`.
   - Change action display title from `"树状图层管理器"` to `"SuperLayer"`.
4. Update `dock_widget.py`:
   - Rename class `TreeMapDockWidget` to `SuperLayerDockWidget`.
   - Update `self.setWindowTitle("树状图层管理器")` to `self.setWindowTitle("SuperLayer")`.
