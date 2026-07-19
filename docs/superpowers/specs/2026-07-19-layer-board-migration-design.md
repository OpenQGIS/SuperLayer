# QGIS 图层属性看板（Layer Board）整合至树状图层管理器设计方案

将原独立的 `Layer Board` 插件迁移并集成进现有的 `TreeMap_Layer_Manager`（树状图层管理器）插件中，作为一个全新的独立视图页面展示。

---

## 1. 需求与设计规范

### 1.1 导航集成
* 在 `TreeMapDockWidget` 顶部的 QToolBar 中新增一个 `属性看板`（或 `图层看板`）按钮，设置为可 Checked 的互斥按钮，并关联到现有的 `self.view_group`。
* 在 `self.stacked_widget` 中添加一个新的页面，对应新编写的属性看板小部件。

### 1.2 界面结构（QSplitter 左右布局）
* **左侧区域：图层表格编辑器（QTabWidget）**
  * **矢量图层 Tab** 与 **栅格图层 Tab**。
  * 每个 Tab 包含一个 `QTableWidget` 用于以表格形式编辑和查看图层各项属性。
  * 具备行背景交替颜色风格（配合新插件风格）。
  * 双击单元格可修改。修改过的单元格背景标记为黄色。
  * 表格下方配置 `保存修改` 与 `放弃修改` 两个平面风格按钮。
* **右侧区域：控制面板侧边栏（QScrollArea 内嵌布局）**
  * **批量更新栏**：包含坐标系选择器（`QgsProjectionSelectionTreeWidget`）、最大/最小可见比例尺输入框、数据源编码选择下拉框，各自配有 `应用 (Set)` 按钮。
  * **批量操作栏**：包含 `保存样式为默认`、`创建空间索引`、`从项目移除图层`、`清除幽灵图层`（全局操作）四个功能按钮。
  * **样式编辑栏**：当且仅当选择单一矢量图层时，嵌入 `QgsRendererPropertiesDialog` 原生样式修改组件，并配有 `应用样式` 按钮。
  * **导出栏**：提供 `导出当前属性表格为 CSV` 按钮。
  * **操作日志栏**：文本日志显示框及 `清空日志` 按钮。

### 1.3 界面风格（CSS QSS）
* 继承并直接复用 `TreeMapDockWidget` 原有的 QSS 样式表，实现扁平化无边框设计、淡灰/白色背景（`#f8f9fa` / `#ffffff`）、圆角按钮与选中的 Bootstrap 蓝色风格（`#0d6efd`）。

---

## 2. 详细设计与核心组件

### 2.1 新增模块 `layer_board_widget.py`
创建全新的 `LayerBoardWidget` 类（继承自 `QWidget`），封装所有图层属性看板的 UI 绘制和业务逻辑。
* **数据流管理**：
  * 使用 `self.layersTable` 定义图层属性字段与其可编辑性映射。
  * 使用 `self.layerBoardChangedData` 字典缓存用户在表格中修改的内容（对应变黄的单元格）。
* **安全数据源校验**：
  * 在修改 `source|uri`（数据源 URI）和 `encoding` 时，必须通过创建临时的 `QgsVectorLayer` 进行校验，校验成功才允许高亮并暂存，否则提示报错并回滚输入。
* **图层样式加载**：
  * 当表格行选择改变时，更新右侧的样式控制面板。如果是单个矢量图层，则加载并展示 `QgsRendererPropertiesDialog`，否则清空该区域。

### 2.2 改造模块 `dock_widget.py`
* 导入 `LayerBoardWidget` 类。
* 在 `__init__` 中实例化 `LayerBoardWidget`，并作为第 5 个页面（index 4）添加到 `self.stacked_widget` 中。
* 在 `_setup_toolbar` 中添加 `act_layer_board` 的 Action，并将其加入到 `self.view_group` 中，保证互斥切换。
* 在 `switch_view` 函数中，增加对于 `index == 4` 的处理，触发 `LayerBoardWidget` 的初始化和图层加载。
* 在 `refresh` 函数中，触发 `LayerBoardWidget` 表格的重新加载，保证数据时刻与当前项目图层同步。

### 2.3 幽灵图层清理逻辑
* 遍历 `QgsProject.instance().mapLayers()`，使用 `QgsLayerTreeUtils.countMapLayerInTree(project.layerTreeRoot(), layer) == 0` 判断图层是否为幽灵图层。
* 执行 `Remove` 时直接从项目里调用 `removeMapLayer()` 移除，并调用 `project.setDirty(True)` 标记项目需要保存。

---

## 3. 测试与验证计划

### 3.1 自动化测试
* 运行现有的测试集以确保未引入任何破坏性更改。
* 编写针对 `layer_board_widget.py` 的测试用例（或直接在 `test_dock_widget.py` 中测试），验证：
  1. 属性看板页面正常添加与切换。
  2. 幽灵图层的识别和清理逻辑。
  3. 修改图层名称、比例尺、编码等属性时是否正确触发黄底暂存以及 Commit 物理保存。

### 3.2 手动功能测试
1. 在 QGIS 中加载具有矢量图层和栅格图层的项目，打开“树状图层管理器”，切换到“属性看板”。
2. 双击图层名称、可见比例尺进行编辑，验证单元格是否变黄。
3. 点击“应用修改”，验证图层名称是否在 QGIS 图层面板中同步更新。
4. 选择多个矢量图层，在右侧控制面板选择新编码或 CRS，点击 Set 批量更新，检查效果。
5. 验证选中单图层时，右侧是否能成功加载样式编辑器，并能够正常应用样式。
6. 点击 CSV 导出并保存到本地，验证 CSV 内容完整度。
