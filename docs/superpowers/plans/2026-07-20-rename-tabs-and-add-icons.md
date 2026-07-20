# Rename Tabs and Add Icons Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Modify the tabs (toolbar buttons) in the QGIS SuperLayer plugin to use new labels and icons (folder: `icons_panel_toolbar/`), showing icon and text side-by-side.

**Architecture:** Update `_setup_toolbar` in `dock_widget.py` to load icons from `icons_panel_toolbar/`, set actions with new names and icons, set toolbar style to `Qt.ToolButtonTextBesideIcon` safely, and update the mocked classes for testing.

**Tech Stack:** Python, PyQt5 / PySide (Qt Framework).

## Global Constraints
- Target workspace: `C:\Users\tesla\AppData\Roaming\QGIS\QGIS3\profiles\ForTest\python\plugins\SuperLayer`
- Naming rules: Rename user-facing actions to "文件夹分类", "图层分类", "矩形树状图", "路径导图", "批量修改", "刷新".
- Internal python variable names (`act_physical_tree`, `act_group_tree`, etc.) must remain unchanged.

---

### Task 1: Update UI Dock Widget Implementation & Mock fallbacks

**Files:**
- Modify: `dock_widget.py` (lines 30-74, 81-90, 563-604)

**Interfaces:**
- Consumes: SVG files under `icons_panel_toolbar/`
- Produces: Updated `SuperLayerDockWidget._setup_toolbar` setting text and icons.

- [ ] **Step 1: Update mock fallback classes**
  Modify lines 30-74 and 81-90 in [dock_widget.py](file:///C:/Users/tesla/AppData/Roaming/QGIS/QGIS3/profiles/ForTest/python/plugins/SuperLayer/dock_widget.py) to support QAction icon constructor and QToolBar styling.

  Target content:
  ```python
                  class Qt:
                      LeftDockWidgetArea = 1
                      RightDockWidgetArea = 2
                      CustomContextMenu = 3
                      UserRole = 32
                      Horizontal = 1
                      AlignLeft = 1
  ```
  Replacement content:
  ```python
                  class Qt:
                      LeftDockWidgetArea = 1
                      RightDockWidgetArea = 2
                      CustomContextMenu = 3
                      UserRole = 32
                      Horizontal = 1
                      AlignLeft = 1
                      ToolButtonTextBesideIcon = 2
  ```

  Target content:
  ```python
                  class QAction:
                      def __init__(self, text, parent=None):
                          self._text = text
                          self.parent = parent
                          self._checkable = False
                          self._checked = False
                          self.triggered = self._Signal()
  ```
  Replacement content:
  ```python
                  class QAction:
                      def __init__(self, *args, **kwargs):
                          if len(args) >= 3:
                              self._icon = args[0]
                              self._text = args[1]
                              self.parent = args[2]
                          elif len(args) == 2:
                              self._text = args[0]
                              self.parent = args[1]
                              self._icon = None
                          elif len(args) == 1:
                              self._text = args[0]
                              self.parent = None
                              self._icon = None
                          else:
                              self._text = ""
                              self.parent = None
                              self._icon = None
                          self._checkable = False
                          self._checked = False
                          self.triggered = self._Signal()
  ```

  Target content:
  ```python
                  class QToolBar:
                      def __init__(self, parent=None):
                          self._actions = []
                      def addAction(self, action):
                          self._actions.append(action)
                          return action
                      def addSeparator(self):
                          pass
                      def setSizePolicy(self, h, v):
                          pass
  ```
  Replacement content:
  ```python
                  class QToolBar:
                      def __init__(self, parent=None):
                          self._actions = []
                      def addAction(self, action):
                          self._actions.append(action)
                          return action
                      def addSeparator(self):
                          pass
                      def setSizePolicy(self, h, v):
                          pass
                      def setToolButtonStyle(self, style):
                          pass
  ```

- [ ] **Step 2: Update toolbar creation logic**
  Modify `_setup_toolbar` in [dock_widget.py](file:///C:/Users/tesla/AppData/Roaming/QGIS/QGIS3/profiles/ForTest/python/plugins/SuperLayer/dock_widget.py) (lines 563-604) to load icons, update text labels, and set the toolbutton style.

  Target content:
  ```python
      def _setup_toolbar(self):
          self.view_group = QActionGroup(self)
          self.view_group.setExclusive(True)
          
          self.act_physical_tree = QAction("物理文件夹", self)
          self.act_physical_tree.setCheckable(True)
          self.act_physical_tree.setChecked(True)
          self.act_physical_tree.triggered.connect(lambda: self.switch_view(0))
          self.view_group.addAction(self.act_physical_tree)
          self.toolbar.addAction(self.act_physical_tree)
          
          self.act_group_tree = QAction("图层组", self)
          self.act_group_tree.setCheckable(True)
          self.act_group_tree.triggered.connect(lambda: self.switch_view(1))
          self.view_group.addAction(self.act_group_tree)
          self.toolbar.addAction(self.act_group_tree)
          
          self.act_treemap = QAction("矩形树状图", self)
          self.act_treemap.setCheckable(True)
          self.act_treemap.triggered.connect(lambda: self.switch_view(2))
          self.view_group.addAction(self.act_treemap)
          self.toolbar.addAction(self.act_treemap)
          
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
          
          self.toolbar.addSeparator()
          
          self.act_refresh = QAction("刷新", self)
          self.act_refresh.triggered.connect(self.refresh)
          self.toolbar.addAction(self.act_refresh)
  ```
  Replacement content:
  ```python
      def _setup_toolbar(self):
          if hasattr(self.toolbar, 'setToolButtonStyle') and hasattr(Qt, 'ToolButtonTextBesideIcon'):
              self.toolbar.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
              
          icon_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "icons_panel_toolbar")
          
          def get_toolbar_icon(name):
              icon_path = os.path.join(icon_dir, name)
              if os.path.exists(icon_path):
                  return QIcon(icon_path)
              return QIcon()
              
          self.view_group = QActionGroup(self)
          self.view_group.setExclusive(True)
          
          self.act_physical_tree = QAction(get_toolbar_icon("panel_toolbar_document.svg"), "文件夹分类", self)
          self.act_physical_tree.setCheckable(True)
          self.act_physical_tree.setChecked(True)
          self.act_physical_tree.triggered.connect(lambda: self.switch_view(0))
          self.view_group.addAction(self.act_physical_tree)
          self.toolbar.addAction(self.act_physical_tree)
          
          self.act_group_tree = QAction(get_toolbar_icon("panel_toolbar_group.svg"), "图层分类", self)
          self.act_group_tree.setCheckable(True)
          self.act_group_tree.triggered.connect(lambda: self.switch_view(1))
          self.view_group.addAction(self.act_group_tree)
          self.toolbar.addAction(self.act_group_tree)
          
          self.act_treemap = QAction(get_toolbar_icon("panel_toolbar_Rec-Tree_Chart.svg"), "矩形树状图", self)
          self.act_treemap.setCheckable(True)
          self.act_treemap.triggered.connect(lambda: self.switch_view(2))
          self.view_group.addAction(self.act_treemap)
          self.toolbar.addAction(self.act_treemap)
          
          self.act_mindmap = QAction(get_toolbar_icon("panel_toolbar_Mindmap.svg"), "路径导图", self)
          self.act_mindmap.setCheckable(True)
          self.act_mindmap.triggered.connect(lambda: self.switch_view(3))
          self.view_group.addAction(self.act_mindmap)
          self.toolbar.addAction(self.act_mindmap)
          
          # Add new Attribute Board Action
          self.act_layer_board = QAction(get_toolbar_icon("panel_toolbar_Property.svg"), "批量修改", self)
          self.act_layer_board.setCheckable(True)
          self.act_layer_board.triggered.connect(lambda: self.switch_view(4))
          self.view_group.addAction(self.act_layer_board)
          self.toolbar.addAction(self.act_layer_board)
          
          self.toolbar.addSeparator()
          
          self.act_refresh = QAction(get_toolbar_icon("panel_toolbar_refresh.svg"), "刷新", self)
          self.act_refresh.triggered.connect(self.refresh)
          self.toolbar.addAction(self.act_refresh)
  ```

- [ ] **Step 3: Run existing unit tests to verify they still compile and run**
  Run: `python -m unittest discover`
  Expected: PASS

---

### Task 2: Add UI verification tests & complete implementation

**Files:**
- Modify: `test_dock_widget.py`

**Interfaces:**
- Consumes: Updated `SuperLayerDockWidget` from Task 1.

- [ ] **Step 1: Add a test to verify names of toolbar actions**
  Add `test_toolbar_actions_labels_and_icons` to [test_dock_widget.py](file:///C:/Users/tesla/AppData/Roaming/QGIS/QGIS3/profiles/ForTest/python/plugins/SuperLayer/test_dock_widget.py).

  Target content:
  ```python
      def test_switch_view_layer_board(self):
  ```
  Replacement content:
  ```python
      def test_toolbar_actions_labels_and_icons(self):
          with patch('dock_widget.LayerTreeModel'), \
               patch('dock_widget.TreeMapWidget'), \
               patch('dock_widget.MindMapView'):
              dock = SuperLayerDockWidget(self.iface, self.parent)
              self.assertEqual(dock.act_physical_tree.text(), "文件夹分类")
              self.assertEqual(dock.act_group_tree.text(), "图层分类")
              self.assertEqual(dock.act_treemap.text(), "矩形树状图")
              self.assertEqual(dock.act_mindmap.text(), "路径导图")
              self.assertEqual(dock.act_layer_board.text(), "批量修改")
              self.assertEqual(dock.act_refresh.text(), "刷新")

      def test_switch_view_layer_board(self):
  ```

- [ ] **Step 2: Run all unit tests**
  Run: `python -m unittest discover`
  Expected: PASS (with 81 tests instead of 80)
