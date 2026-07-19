# SuperLayer - QGIS 核心图层与物理文件管理器

`SuperLayer` 是一个用于 QGIS 的多维图层与文件管理器插件，通过列表、物理树、矩形树图、思维导图和属性属性看板五个维度，帮助您直观地组织工程图层，并安全地在磁盘层面操作物理数据文件。

---

## 🌟 核心功能

1.  **多视角视图切换**
    *   **物理树视图**：直接将磁盘上的物理文件关系映射为树状结构，展示各个文件夹及下属图层的存储层次。
    *   **组树视图**：完整映射 QGIS 图层面板的图层组逻辑结构。
    *   **矩形树图**：按图层文件在磁盘上的实际占用空间生成大小比例矩形，大图层和无效冗余数据一目了然。
    *   **思维导图**：自动将目录与图层生成高清矢量思维脑图，并将在线图层、临时内存图层及失效无效图层精准分流展示。
    *   **属性看板**：提供全功能的表格格网，用以批量且就地编辑图层基本元数据，带有就地校验和脏数据高亮提示。
2.  **物理存储层级的安全重构**
    *   **安全移动与重命名**：提供在操作系统文件层面移动、重命名及复制矢量/栅格图层的功能。移动时会自动携带所有伴生文件（如 `.shp` 伴生的 `.shx`、`.dbf`、`.prj` 等），并在完成后自动更新 QGIS 中的图层数据源路径，防止数据源丢失或损坏。
    *   **磁盘文件物理追踪**：图层和文件夹均支持右键“打开文件夹位置”，一键唤起文件资源管理器并定位。
3.  **原生样式编辑器整合**
    *   在插件右侧区域，深度嵌入了 QGIS 原生的图层符号化样式设置面板，支持就地配置样式并触发地图画布重新渲染。

---

## 📖 用法教程

### 1. 启动插件
在 QGIS 菜单栏中点击 `插件` -> `SuperLayer`，或直接在 QGIS 工具栏中点击 **SuperLayer 的专属图标**，即可在侧边栏或浮动窗口中唤起主控制台。

### 2. 切换管理维度
控制台顶部提供了五个视图切换按钮，点击可在不同管理维度间切换：
*   **列表模式 / 树形模式**：查看图层的物理组织结构。
*   **矩形树图**：矩形面积代表磁盘空间占比。
*   **思维导图**：以可视化网状脑图形式交互。
*   **属性看板**：批量修改和配置属性元数据。

### 3. 使用物理树重构磁盘图层
*   **移动物理文件**：在物理树视图下，右键点击某个图层，选择 `移动物理文件` 并选择目标文件夹。插件会自动解析该图层的所有伴生文件一并移过去，并热更新 QGIS 中的数据源链接，图层无需重新载入。
*   **文件重命名**：在图层上右键选择 `重命名图层物理文件`，插件将重命名磁盘文件并同步更新 QGIS 图层名与关联路径。
*   **快速查找**：右键点击图层或文件夹，选择 `打开文件夹位置` 即可直接定位到 Windows 文件资源管理器中的该文件。

### 4. 使用思维导图交互
*   **物理迁移（拖拽）**：在脑图视图中，可以直接用鼠标将一个图层节点拖拽到任意文件夹节点上，松开鼠标即可在后台自动执行物理文件搬迁及数据源重定向。
*   **缩放定位**：双击任意图层节点，QGIS 地图画布会自动缩放到该图层的边界范围；双击文件夹节点可展开或收起其子级。

### 5. 使用属性看板批量操作
*   **就地双击编辑**：切换到 `属性看板` 页面，直接双击表格中的任意单元格，即可就地修改 `图层名称`、`数据源路径`、`CRS (坐标系)`、`可见比例尺范围` 和 `编码`。
*   **高亮与统一提交**：被修改的单元格会高亮标记为黄色（脏数据状态）。确认修改无误后，点击下方的 **Commit（提交）** 按钮即可一并写入并刷新工程；若想撤销，点击 **Discard（放弃）** 即可恢复原状态。
*   **数据导出与日志**：在看板底部，可以一键将所有属性数据 `导出为 CSV`；或者在 `操作日志` 标签页中实时查看所有的重定向和文件改动日志。

### 6. 编辑图层样式
点击任意图层后，展开插件右侧的样式编辑器折叠区。您可以在其中直接使用 QGIS 官方的原生样式编辑组件更改符号、颜色或渲染器，点击保存即可实时应用到地图上。

---

# SuperLayer - QGIS TreeMap Layer Manager

`SuperLayer` is a multi-dimensional layer and file manager plugin for QGIS. It enables you to organize map layers, inspect storage allocations, and safely modify underlying spatial datasets on disk.

---

## 🌟 Key Features

1.  **Multiple Visual Perspectives**
    *   **Physical Tree**: Displays layers in hierarchical directories on disk, allowing direct relocations.
    *   **Group Tree**: Matches the logical group structure of the native QGIS Layers Panel.
    *   **Treemap**: Renders responsive proportional rectangles by file size to spot massive or obsolete files easily.
    *   **Mindmap**: Compiles hierarchical directories into vector SVG mindmaps, filtering invalid, temporary, and online layers cleanly.
    *   **Layer Board**: Features a spreadsheets-like grid for batch properties tuning with live validation and rollback capabilities.
2.  **Safe Directory Restructuring**
    *   **Physical Move & Rename**: Moves, copies, or renames vector and raster files on disk. Handles all sidecar files (e.g. `.shp` auxiliary files `.shx`, `.dbf`, `.prj`) and auto-updates layer data sources inside QGIS.
    *   **Open Directory**: Right-click menus on folder and layer nodes to reveal files in Windows Explorer / OS Finder.
3.  **Embedded Styling**
    *   Embeds the official QGIS Renderer Properties configuration layout on the right sidebar for real-time map styling and redraws.

---

## 📖 Usage Tutorial

### 1. Launching the Plugin
Click `Plugins` -> `SuperLayer` in QGIS Menu, or click the **SuperLayer icon** in QGIS Toolbar to open the control dock.

### 2. View Switching
Click the view toggle buttons at the top of the dock to switch views:
*   **List / Tree View**: Inspect physical folders on disk.
*   **Treemap**: Analyze size percentages.
*   **Mindmap**: Interact with SVG nodes.
*   **Layer Board**: Batch update metadata fields.

### 3. Restructuring Files in Physical Tree
*   **Move Physical Files**: Right-click a layer and choose `Move Physical Files`. The plugin relocates the main file and its sidecars, then updates the layer source paths in your project immediately.
*   **Rename Storage**: Right-click a layer and choose `Rename Storage File` to change both filenames on disk and the layer name inside QGIS.
*   **Open Folder**: Right-click any node and choose `Open Folder Location` to locate it in system explorer.

### 4. Interactive Mindmap
*   **Drag & Drop Relocation**: Drag any layer node and drop it onto a folder node in the mindmap. The plugin performs physical file relocation and resets data sources automatically.
*   **Zoom to Layer**: Double-click any layer node to fit the QGIS map viewport to the layer's boundaries. Double-click folders to toggle collapse/expand.

### 5. Spreadsheet-like Layer Board
*   **Double-Click Inline Edit**: Double-click any grid cell to change `Name`, `Source Path`, `CRS`, `Visibility Scale`, or `Encoding` directly.
*   **Commit & Discard**: Modified cells highlight in yellow (unsaved state). Click **Commit** to apply all updates to layers, or **Discard** to revert modifications.
*   **CSV Export & Logs**: Click `Export to CSV` to save the properties grid, or check history details in the operations `Logs` tab.

### 6. Changing Styles
Select a layer, unfold the style panel on the right sidebar, edit symbols or colors using native QGIS tools, and see the rendering results on map canvas instantly.
