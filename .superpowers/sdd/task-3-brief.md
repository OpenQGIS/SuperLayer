# Task 3: Unit Test Updates

**Goal:** Update unit test files to import and test the renamed `SuperLayerPlugin` and `SuperLayerDockWidget` classes, and assert the correct window/action titles.

**Files:**
- Modify: `test_dock_widget.py`
- Modify: `test_main_plugin.py`

**Instructions:**
1. Update `test_dock_widget.py`:
   - Replace imports/references of `TreeMapDockWidget` with `SuperLayerDockWidget`.
2. Update `test_main_plugin.py`:
   - Replace imports/references of `TreeMapLayerManagerPlugin` with `SuperLayerPlugin`.
   - Replace references of `TreeMapDockWidget` with `SuperLayerDockWidget`.
   - Update assertions for the QAction text to expect `"SuperLayer"` instead of `"树状图层管理器"`.
