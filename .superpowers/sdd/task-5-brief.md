### Task 5: Batch operations and Ghost Layers

**Files:**
- Modify: `layer_board_widget.py`
- Modify: `test_layer_board.py`

**Interfaces:**
- Consumes: `LayerBoardWidget` from Task 4.
- Produces: Sidebar GUI panels for batch updating, methods `applyPropertyOnSelectedLayers`, `performActionOnSelectedLayers`, `removeGhostLayers`.

- [ ] **Step 1: Setup actual controls in side panel of LayerBoardWidget**

Implement the sidebar UI structure and connections in `layer_board_widget.py`:
```python
    # Replace _init_right_panel_stubs in layer_board_widget.py

    def _init_right_panel_stubs(self):
        # 1. Batch Updates Group Box
        group_batch = QGroupBox(self.tr("批量更新 (Batch Update)"))
        batch_layout = QVBoxLayout(group_batch)
        batch_layout.setSpacing(8)
        
        # CRS
        crs_lbl = QLabel(self.tr("设置 CRS:"))
        batch_layout.addWidget(crs_lbl)
        crs_row = QHBoxLayout()
        self.inCrs = QLineEdit()
        self.btDefineProjection = QPushButton("...")
        self.btApplyCrs = QPushButton(self.tr("应用"))
        crs_row.addWidget(self.inCrs, 1)
        crs_row.addWidget(self.btDefineProjection)
        crs_row.addWidget(self.btApplyCrs)
        batch_layout.addLayout(crs_row)
        
        # Max Scale
        max_scale_lbl = QLabel(self.tr("设置最大比例尺:"))
        batch_layout.addWidget(max_scale_lbl)
        max_row = QHBoxLayout()
        self.inMaxScale = QLineEdit()
        self.btApplyMaxScale = QPushButton(self.tr("应用"))
        max_row.addWidget(self.inMaxScale, 1)
        max_row.addWidget(self.btApplyMaxScale)
        batch_layout.addLayout(max_row)
        
        # Min Scale
        min_scale_lbl = QLabel(self.tr("设置最小比例尺:"))
        batch_layout.addWidget(min_scale_lbl)
        min_row = QHBoxLayout()
        self.inMinScale = QLineEdit()
        self.btApplyMinScale = QPushButton(self.tr("应用"))
        min_row.addWidget(self.inMinScale, 1)
        min_row.addWidget(self.btApplyMinScale)
        batch_layout.addLayout(min_row)
        
        # Encoding
        self.encodingLabel = QLabel(self.tr("设置数据源编码 (仅矢量):"))
        batch_layout.addWidget(self.encodingLabel)
        enc_row = QHBoxLayout()
        self.inEncodingList = QComboBox()
        self.btApplyEncoding = QPushButton(self.tr("应用"))
        enc_row.addWidget(self.inEncodingList, 1)
        enc_row.addWidget(self.btApplyEncoding)
        batch_layout.addLayout(enc_row)
        
        self.right_layout.addWidget(group_batch)
        
        # 2. Actions Group Box
        group_actions = QGroupBox(self.tr("批量操作 (Actions)"))
        act_layout = QVBoxLayout(group_actions)
        act_layout.setSpacing(6)
        
        self.btSaveStyleAsDefault = QPushButton(self.tr("保存样式为默认"))
        self.btCreateSpatialIndex = QPushButton(self.tr("创建空间索引 (矢量)"))
        self.btRemoveLayer = QPushButton(self.tr("从项目移除图层"))
        self.btRemoveGhostLayers = QPushButton(self.tr("清除幽灵图层"))
        
        act_layout.addWidget(self.btSaveStyleAsDefault)
        act_layout.addWidget(self.btCreateSpatialIndex)
        act_layout.addWidget(self.btRemoveLayer)
        act_layout.addWidget(self.btRemoveGhostLayers)
        
        self.right_layout.addWidget(group_actions)
        
        # 3. Symbology Group Box
        self.group_style = QGroupBox(self.tr("图层样式直接修改"))
        style_layout = QVBoxLayout(self.group_style)
        self.styleScrollArea = QScrollArea()
        self.styleScrollArea.setWidgetResizable(True)
        self.styleScrollArea.setMinimumHeight(150)
        self.btApplyStyle = QPushButton(self.tr("应用样式"))
        style_layout.addWidget(self.styleScrollArea, 1)
        style_layout.addWidget(self.btApplyStyle)
        
        self.right_layout.addWidget(self.group_style)
        
        # 4. CSV Export Group Box
        group_export = QGroupBox(self.tr("数据导出 (Export)"))
        export_layout = QVBoxLayout(group_export)
        self.btExportCsv = QPushButton(self.tr("导出当前看板为 CSV"))
        export_layout.addWidget(self.btExportCsv)
        self.right_layout.addWidget(group_export)
        
        # 5. Log Group Box
        group_log = QGroupBox(self.tr("操作日志 (Log)"))
        log_layout = QVBoxLayout(group_log)
        self.txtLog = QTextEdit()
        self.txtLog.setReadOnly(True)
        self.txtLog.setMinimumHeight(100)
        self.btClearLog = QPushButton(self.tr("清空日志"))
        log_layout.addWidget(self.txtLog, 1)
        log_layout.addWidget(self.btClearLog)
        
        self.right_layout.addWidget(group_log)
        
        self._setup_connections()

    def _setup_connections(self):
        # Selection signals for style
        self.vector_table.selectionModel().selectionChanged.connect(partial(self.setSelectedLayerStyleWidget, 'vector'))
        self.raster_table.selectionModel().selectionChanged.connect(partial(self.setSelectedLayerStyleWidget, 'raster'))
        self.tab_widget.currentChanged.connect(self.onTabChanged)
        
        self.btDefineProjection.clicked.connect(self.chooseProjection)
        self.btClearLog.clicked.connect(self.clearLog)
        
        # Bulk updates
        self.btApplyCrs.clicked.connect(lambda: self.applyPropertyOnSelectedLayers('crs'))
        self.btApplyMaxScale.clicked.connect(lambda: self.applyPropertyOnSelectedLayers('maxScale'))
        self.btApplyMinScale.clicked.connect(lambda: self.applyPropertyOnSelectedLayers('minScale'))
        self.btApplyEncoding.clicked.connect(lambda: self.applyPropertyOnSelectedLayers('encoding'))
        
        # Batch actions
        self.btSaveStyleAsDefault.clicked.connect(lambda: self.performActionOnSelectedLayers('saveStyleAsDefault'))
        self.btCreateSpatialIndex.clicked.connect(lambda: self.performActionOnSelectedLayers('createSpatialIndex'))
        self.btRemoveLayer.clicked.connect(lambda: self.performActionOnSelectedLayers('removeLayer'))
        self.btRemoveGhostLayers.clicked.connect(self.removeGhostLayers)
```

Now, implement the execution functions:
```python
    # Add inside LayerBoardWidget in layer_board_widget.py

    def getActiveLayerType(self):
        return 'vector' if self.tab_widget.currentIndex() == 0 else 'raster'

    def chooseProjection(self):
        try:
            from qgis.gui import QgsProjectionSelectionTreeWidget
            projSelector = QgsProjectionSelectionTreeWidget(self)
            if projSelector.exec_():
                crs = QgsCoordinateReferenceSystem(projSelector.selectedCrsId(), QgsCoordinateReferenceSystem.InternalCrsId)
                if len(projSelector.selectedAuthId()) > 0:
                    self.inCrs.setText(crs.authid())
        except Exception:
            pass

    def applyPropertyOnSelectedLayers(self, key):
        layerType = self.getActiveLayerType()
        table = self.layersTable[layerType]['tableWidget']
        
        # Value
        value = None
        if key == 'crs': value = self.inCrs.text()
        elif key == 'maxScale': value = self.inMaxScale.text()
        elif key == 'minScale': value = self.inMinScale.text()
        elif key == 'encoding': value = self.inEncodingList.currentText()
        
        if not value:
            return
            
        sm = table.selectionModel()
        lines = sm.selectedRows()
        if not lines:
            return
            
        col = next(index for (index, d) in enumerate(self.layersAttributes[layerType]) if d['key'] == key)
        for index in lines:
            row = index.row()
            item = table.item(row, col)
            item.setData(Qt.EditRole, value)
            self.onItemChanged(layerType, item)

    def performActionOnSelectedLayers(self, key):
        layerType = self.getActiveLayerType()
        table = self.layersTable[layerType]['tableWidget']
        
        sm = table.selectionModel()
        lines = sm.selectedRows()
        if not lines:
            return
            
        lr = QgsProject.instance()
        for index in lines:
            row = index.row()
            layerId = table.item(row, 0).data(Qt.EditRole)
            layer = lr.mapLayer(layerId)
            if not layer:
                continue
                
            if key == 'saveStyleAsDefault':
                if layer.providerType() == 'postgres':
                    if hasattr(layer, 'saveStyleToDatabase'):
                        layer.saveStyleToDatabase(layer.name(), '', True, None, '')
                else:
                    if hasattr(layer, 'saveDefaultStyle'):
                        layer.saveDefaultStyle()
                        
            elif key == 'createSpatialIndex' and layer.type() == QgsMapLayer.VectorLayer:
                provider = layer.dataProvider()
                if hasattr(provider, 'capabilities') and (provider.capabilities() & QgsVectorDataProvider.CreateSpatialIndex):
                    provider.createSpatialIndex()
                    
            elif key == 'removeLayer':
                lr.removeMapLayer(layer.id())
                table.removeRow(row)
                lr.setDirty(True)

    def removeGhostLayers(self):
        project = QgsProject.instance()
        for layer in list(project.mapLayers().values()):
            if self.is_ghost_layer(layer):
                project.removeMapLayer(layer.id())
        project.setDirty(True)
        self.populateLayerTable('vector')
        self.populateLayerTable('raster')

    def onTabChanged(self):
        layerType = self.getActiveLayerType()
        isEnabled = layerType == 'vector'
        self.encodingLabel.setEnabled(isEnabled)
        self.inEncodingList.setEnabled(isEnabled)
        self.btApplyEncoding.setEnabled(isEnabled)
        self.btCreateSpatialIndex.setEnabled(isEnabled)
```

- [ ] **Step 2: Add test cases in test_layer_board.py for batch actions**

Add tests:
```python
    # Add inside TestLayerBoardWidget in test_layer_board.py

    @patch('layer_board_widget.QgsProject.instance')
    def test_remove_ghost_layers(self, mock_project_inst):
        mock_vlayer = MagicMock()
        mock_vlayer.id.return_value = "v1"
        mock_vlayer.type.return_value = 0
        mock_vlayer.isSpatial.return_value = True
        
        mock_proj = MagicMock()
        mock_proj.mapLayers.return_value = {"v1": mock_vlayer}
        mock_project_inst.return_value = mock_proj
        
        widget = LayerBoardWidget(self.iface)
        
        # Force it to be a ghost layer by patching is_ghost_layer
        widget.is_ghost_layer = MagicMock(return_value=True)
        widget.removeGhostLayers()
        
        # Verify it was removed
        mock_proj.removeMapLayer.assert_called_with("v1")
```

- [ ] **Step 3: Run tests**

Run: `python -m unittest test_layer_board.py`
Expected output: PASS

- [ ] **Step 4: Commit**

```bash
git add layer_board_widget.py test_layer_board.py
git commit -m "feat: implement right side-panel controls and batch actions with tests"
```

---

