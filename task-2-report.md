# Task 2: Safe File Operations Module Fixes Report

## Summary of Changes

All issues identified in Task 2 have been successfully resolved and validated with unit tests.

### 1. Case-Sensitivity & QGIS Sidecars
- Modified `get_associated_files` to look up the physical file on disk to determine its exact casing.
- Sidecar detection matches extensions case-insensitively.
- Raster world file extension calculation now preserves the case pattern of the source extension (e.g. `.TIF` yields `.TFW`, while `.tif` yields `.tfw`).
- Added standard QGIS-specific sidecars to `get_associated_files`:
  - **Vector (Shapefile)**: Added `.qml`, `.qmd`, and `.qix` to the `shp_extensions` list.
  - **Raster**: Added `.qml`, `.qmd`, and `(main_ext + ".ovr").lower()` to the `target_exts` list.
- Filtered associated files in `get_associated_files` to only return files, not directories, by checking `os.path.isfile(full_path)` before adding to `seen`.
- Modified `safe_rename` to match complex extensions (`.shp.xml` and `.aux.xml`) case-insensitively and preserve the exact casing of the suffix on disk.

### 2. QGIS Layer Source Query Parameter Handling & Provider Safety
- Introduced `split_qgis_source` to split any incoming layer source paths into `phys_path` (physical path) and `query_params` (e.g., `|layername=table|subset=filter`).
- Allowed physical operations (existence checks, sidecar resolution, copying, moving, renaming) to run on the physical file path.
- Updated `safe_move` and `safe_rename` to reconstruct the final layer datasource with the query parameters re-appended, ensuring QGIS loads the correct layer and filters.
- Added a `dataProvider` safety check in `update_layer_source` to ensure `dataProvider()` is not `None` before calling `.name()`.

### 3. Silent Overwrite & Transaction Safety in `safe_rename`
- Implemented a pre-check in `safe_rename` that maps all files to their destination names before executing the renames.
- Performs a check: if any destination file already exists on disk (excluding files that are part of the rename set itself, to support case-only renames), it raises a `FileExistsError` and halts before writing.
- Sanitized `new_filename` in `safe_rename` by doing `new_filename = os.path.basename(new_filename)` first.
- **Transaction Safety**: Wrapped both the `os.rename` loop and `update_layer_source` inside the single `try-except` block. If `update_layer_source` (or any rename step) raises an exception, it performs the rollback of already renamed files on disk back to their original names.

### 4. Case-Insensitive Directory Comparison in `safe_move`
- Improved directory comparison in `safe_move` to use case-insensitive evaluation:
  `if os.path.normcase(os.path.abspath(source_dir)) == os.path.normcase(os.path.abspath(target_dir)):`

### 5. Unit Tests Added
Ten unit tests are now defined in `test_file_operations.py`:
1. `test_case_insensitive_sidecars`: Verifies shapefiles with mixed/uppercase extensions and raster `.TIF` / `.TFW` casing match correctly.
2. `test_query_parameters_safe_move`: Verifies `safe_move` correctly splits and reconstructs query parameters in the layer source.
3. `test_query_parameters_safe_rename`: Verifies `safe_rename` correctly splits and reconstructs query parameters in the layer source.
4. `test_safe_rename_file_exists_error`: Verifies that a `FileExistsError` is raised if a renamed destination file exists, and that no files are modified/deleted.
5. `test_safe_rename_rollback_on_failure`: Mocks `os.rename` failing to verify that already renamed files are rolled back to original names.
6. `test_safe_rename_rollback_on_update_source_failure`: Mocks `update_layer_source` raising an exception to verify that disk renames are rolled back to original names.
7. `test_new_sidecars_detection`: Verifies standard vector (`.qml`, `.qmd`, `.qix`) and raster (`.qml`, `.qmd`, `.ovr`) sidecars are correctly detected.
8. `test_associated_files_ignores_directories`: Verifies that directories with names matching expected sidecar extensions are ignored.
9. `test_safe_rename_sanitizes_filename`: Verifies path sanitization using `os.path.basename`.
10. `test_update_layer_source_none_provider`: Verifies safety check when `dataProvider()` is `None`.

## Test Execution Results
All 16 tests executed and passed:
```
................
----------------------------------------------------------------------
Ran 16 tests in 0.123s

OK
```

Status: **DONE**
