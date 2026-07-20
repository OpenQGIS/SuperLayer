# Design Document: Layer Categorization, Right-Click Actions on Physical Paths, and Online Layer Filtering

## Goal Description
This change introduces three key improvements to the QGIS SuperLayer plugin:
1. **Exclude Online Layers Globally**: Filter out remote online layers (such as WMS, WFS, WCS, VectorTile, XYZ, etc.) from all views (Physical Tree, Group Tree, Treemap, Mindmap, and Layer Board).
2. **Proper Categorization of Virtual/Temporary/Invalid Layers**: Ensure virtual, temporary (memory), and invalid (unavailable) layers are correctly identified and grouped under their respective virtual folders. Keep them visible while filtering out true online layers.
3. **Right-Click Context Menu on Physical Paths**: Expand the right-click menu functionality on QTreeView. If a user right-clicks on the "物理路径" (physical path) column (Column 2) of a layer or folder row, show the folder context menu containing "复制文件夹链接" (Copy Folder Link) and "打开文件夹位置" (Open Folder Location) for that physical path.

---

## Proposed Changes

### Component 1: Layer Classification & Filtering

#### [MODIFY] [layer_model.py](file:///c:/Users/tesla/AppData/Roaming/QGIS/QGIS3/profiles/ForTest/python/plugins/SuperLayer/layer_model.py)
* **Modify `get_layer_format`**:
  * Remove `virtual` from the online providers list.
  * Properly recognize `virtual` provider as `"虚拟图层"`.
  * Properly recognize `memory` provider as `"临时图层"`.
  * Check layer validity (`not layer.isValid()`) at the very top of `get_layer_format` and return `"不可用图层"`.
* **Modify `rebuild_model`**:
  * Exclude layers of format `"在线图层"` globally from the layers list in both physical tree (`_build_physical_tree`) and group tree (`_build_virtual_tree` / `_traverse_qgis_tree`) builders.

### Component 2: Global Filtering in Main Dock & Views

#### [MODIFY] [dock_widget.py](file:///c:/Users/tesla/AppData/Roaming/QGIS/QGIS3/profiles/ForTest/python/plugins/SuperLayer/dock_widget.py)
* **Modify `update_filter_tags`**: Skip online layers when generating format tags so "在线图层" tag doesn't show up.
* **Modify `switch_view` and `refresh`**: Filter out online layers before passing the layer list to Treemap and Mindmap views.
* **Modify `show_physical_tree_context_menu` & `show_group_tree_context_menu`**:
  * Remove the column-0 restriction (`idx.column() == 0`).
  * If the clicked column is Column 2 (`idx.column() == 2`) or the item is a physical `FolderItem`, retrieve the physical folder path (from the layer's source directory or folder item path).
  * If the path exists on disk, pop up the folder context menu ("打开文件夹位置" and "复制文件夹链接").

#### [MODIFY] [layer_board_widget.py](file:///c:/Users/tesla/AppData/Roaming/QGIS/QGIS3/profiles/ForTest/python/plugins/SuperLayer/layer_board_widget.py)
* **Modify `populateLayerTable`**: Filter out online layers when populating the tables.

#### [MODIFY] [mindmap_view.py](file:///c:/Users/tesla/AppData/Roaming/QGIS/QGIS3/profiles/ForTest/python/plugins/SuperLayer/mindmap_view.py)
* **Modify `set_layers`**: Filter out online layers.

---

## Verification Plan

### Automated Tests
* Run `python -m unittest discover -v` to ensure all existing and new tests pass.
* Update `test_mindmap.py` to reflect the removal of the `"在线图层"` node in the path tree.
* Add unit tests for right-clicking on Column 2 and verifying the menu options.

### Manual Verification
* Run QGIS, verify that online layers are not displayed in any view.
* Right-click on physical path (Column 2) of local layers and folders, and verify that "复制文件夹链接" and "打开文件夹位置" are displayed and function correctly.
