# Design Spec: Rename Tabs and Add Icons to Toolbar

This design document outlines the changes needed to rename the navigation tabs (toolbar actions) of the SuperLayer QGIS plugin and equip them with both icons and text.

## User Review Required

> [!NOTE]
> The internal python variable names (such as `act_physical_tree`, `act_group_tree`) will remain unchanged to minimize code churn and maintain safety with the existing test assertions. Only the user-facing text and icons will be modified.

## Proposed Changes

### Tab Name & Icon Mapping

| Original Tab | New Tab Name | SVG Icon File |
| :--- | :--- | :--- |
| 物理文件夹 | 文件夹分类 | `panel_toolbar_document.svg` |
| 图层组 | 图层分类 | `panel_toolbar_group.svg` |
| 矩形树状图 | 矩形树状图 | `panel_toolbar_Rec-Tree_Chart.svg` |
| 思维导图 | 路径导图 | `panel_toolbar_Mindmap.svg` |
| 属性看板 | 批量修改 | `panel_toolbar_Property.svg` |
| 刷新 | 刷新 | `panel_toolbar_refresh.svg` |

All icons are located under: `icons_panel_toolbar/`

### Component: SuperLayer UI Dock Widget

#### [MODIFY] [dock_widget.py](file:///C:/Users/tesla/AppData/Roaming/QGIS/QGIS3/profiles/ForTest/python/plugins/SuperLayer/dock_widget.py)

- **Icon Resolution**: Add a helper function or logic to resolve paths dynamically within `SuperLayerDockWidget` to point to the `icons_panel_toolbar` folder.
- **Toolbar Configuration**:
  - Set the toolbar style to `Qt.ToolButtonTextBesideIcon` to ensure both text and icon are displayed together. Use safe `hasattr` checks to avoid breaking the PyQt mock environments.
  - Update `QAction` creation to use the new names and load/set their corresponding icons.
- **Mock Safety**: Add mock values for `Qt.ToolButtonTextBesideIcon` and mock `setToolButtonStyle` / `setIconSize` on the mock `QToolBar` to prevent tests from failing in PyQt-less CLI runs.

## Verification Plan

### Automated Tests
- Run `python -m unittest discover` to ensure all tests pass.
- Update tests in `test_dock_widget.py` if any assert specific labels or icons on actions.

### Manual Verification
- Verify that icons are correctly loaded and shown next to the text on QGIS reload.
