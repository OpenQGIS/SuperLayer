import unittest
import tempfile
import os
import shutil
from unittest.mock import MagicMock, patch

# Import the code to test
import file_operations
from file_operations import get_associated_files, safe_copy, safe_move, safe_rename, safe_rename_parent_dir, safe_rename_dir, safe_migrate_dir, update_layer_source

# Define test double classes for QGIS layer types
# Since QGIS is not available in standard Python CLI runs, we subclass the fallback classes.
class TestVectorLayer(file_operations.QgsVectorLayer):
    def __init__(self, source_path, name="vector_layer"):
        self._source = source_path
        self._name = name
        self.datasource_updated = None
        self._provider = MagicMock()
        self._provider.name.return_value = "ogr"

    def source(self):
        return self._source

    def name(self):
        return self._name

    def setName(self, name):
        self._name = name

    def dataProvider(self):
        return self._provider

    def setDataSource(self, source, name, provider_name):
        self._source = source
        self.datasource_updated = (source, name, provider_name)

class TestRasterLayer(file_operations.QgsRasterLayer):
    def __init__(self, source_path, name="raster_layer"):
        self._source = source_path
        self._name = name
        self.datasource_updated = None
        self._provider = MagicMock()
        self._provider.name.return_value = "gdal"

    def source(self):
        return self._source

    def name(self):
        return self._name

    def setName(self, name):
        self._name = name

    def dataProvider(self):
        return self._provider

    def setDataSource(self, source, name, provider_name):
        self._source = source
        self.datasource_updated = (source, name, provider_name)

class TestFileOperations(unittest.TestCase):
    def setUp(self):
        file_operations._cleanup_jobs = []
        file_operations._cleanup_loaded = True
        self.temp_dir = tempfile.TemporaryDirectory()
        self.src_dir = os.path.join(self.temp_dir.name, 'src')
        self.dest_dir = os.path.join(self.temp_dir.name, 'dest')
        os.makedirs(self.src_dir)
        os.makedirs(self.dest_dir)
        
    def tearDown(self):
        file_operations._cleanup_jobs = []
        self.temp_dir.cleanup()
        
    def test_shp_sidecar_detection(self):
        shp = os.path.join(self.src_dir, "test.shp")
        dbf = os.path.join(self.src_dir, "test.dbf")
        shx = os.path.join(self.src_dir, "test.shx")
        
        open(shp, 'w').close()
        open(dbf, 'w').close()
        open(shx, 'w').close()
        
        files = get_associated_files(shp)
        self.assertEqual(len(files), 3)
        self.assertIn(shp, files)
        self.assertIn(dbf, files)
        self.assertIn(shx, files)

    def test_raster_sidecar_detection(self):
        tif = os.path.join(self.src_dir, "raster.tif")
        tfw = os.path.join(self.src_dir, "raster.tfw")
        prj = os.path.join(self.src_dir, "raster.prj")
        aux = os.path.join(self.src_dir, "raster.tif.aux.xml")
        
        open(tif, 'w').close()
        open(tfw, 'w').close()
        open(prj, 'w').close()
        open(aux, 'w').close()
        
        files = get_associated_files(tif)
        self.assertEqual(len(files), 4)
        self.assertIn(tif, files)
        self.assertIn(tfw, files)
        self.assertIn(prj, files)
        self.assertIn(aux, files)

    def test_safe_copy(self):
        shp = os.path.join(self.src_dir, "test.shp")
        dbf = os.path.join(self.src_dir, "test.dbf")
        open(shp, 'w').close()
        open(dbf, 'w').close()
        
        copied = safe_copy(shp, self.dest_dir)
        self.assertEqual(len(copied), 2)
        
        dest_shp = os.path.join(self.dest_dir, "test.shp")
        dest_dbf = os.path.join(self.dest_dir, "test.dbf")
        self.assertTrue(os.path.exists(dest_shp))
        self.assertTrue(os.path.exists(dest_dbf))

    def test_update_layer_source(self):
        shp = os.path.join(self.src_dir, "test.shp")
        layer = TestVectorLayer(shp, "my_layer")
        new_path = os.path.join(self.dest_dir, "test.shp")
        
        update_layer_source(layer, new_path)
        self.assertEqual(layer.source(), new_path)
        self.assertEqual(layer.datasource_updated, (new_path, "my_layer", "ogr"))

    def test_safe_move(self):
        shp = os.path.join(self.src_dir, "test.shp")
        dbf = os.path.join(self.src_dir, "test.dbf")
        open(shp, 'w').close()
        open(dbf, 'w').close()
        
        layer = TestVectorLayer(shp, "move_layer")
        result = safe_move(layer, self.dest_dir)
        
        self.assertTrue(result)
        # Original files should be removed
        self.assertFalse(os.path.exists(shp))
        self.assertFalse(os.path.exists(dbf))
        
        # New files should exist
        dest_shp = os.path.join(self.dest_dir, "test.shp")
        dest_dbf = os.path.join(self.dest_dir, "test.dbf")
        self.assertTrue(os.path.exists(dest_shp))
        self.assertTrue(os.path.exists(dest_dbf))
        
        # Layer source should be updated
        self.assertEqual(layer.source(), dest_shp)

    def test_safe_rename(self):
        shp = os.path.join(self.src_dir, "test.shp")
        dbf = os.path.join(self.src_dir, "test.dbf")
        shp_xml = os.path.join(self.src_dir, "test.shp.xml")
        open(shp, 'w').close()
        open(dbf, 'w').close()
        open(shp_xml, 'w').close()
        
        layer = TestVectorLayer(shp, "rename_layer")
        result = safe_rename(layer, "renamed.shp")
        
        self.assertTrue(result)
        # Original files should not exist
        self.assertFalse(os.path.exists(shp))
        self.assertFalse(os.path.exists(dbf))
        self.assertFalse(os.path.exists(shp_xml))
        
        # Renamed files should exist
        renamed_shp = os.path.join(self.src_dir, "renamed.shp")
        renamed_dbf = os.path.join(self.src_dir, "renamed.dbf")
        renamed_xml = os.path.join(self.src_dir, "renamed.shp.xml")
        self.assertTrue(os.path.exists(renamed_shp))
        self.assertTrue(os.path.exists(renamed_dbf))
        self.assertTrue(os.path.exists(renamed_xml))
        
        # Layer source and name should be updated
        self.assertEqual(layer.source().replace('\\', '/'), renamed_shp.replace('\\', '/'))
        self.assertEqual(layer.name(), "renamed")

    def test_safe_rename_defers_locked_source_without_blocking(self):
        shp = os.path.join(self.src_dir, "locked.shp")
        dbf = os.path.join(self.src_dir, "locked.dbf")
        with open(shp, "wb") as stream:
            stream.write(b"geometry")
        with open(dbf, "wb") as stream:
            stream.write(b"attributes")
        layer = TestVectorLayer(shp, "locked")
        real_remove = os.remove

        def locked_remove(path):
            if path in (shp, dbf):
                raise PermissionError("simulated Windows provider lock")
            return real_remove(path)

        with patch("file_operations.os.remove", side_effect=locked_remove):
            self.assertTrue(safe_rename(layer, "renamed.shp"))

        self.assertTrue(os.path.exists(shp))
        self.assertTrue(os.path.exists(dbf))
        self.assertCountEqual(file_operations.pending_rename_cleanup_files(), [shp, dbf])

        file_operations._process_cleanup_jobs()
        self.assertFalse(os.path.exists(shp))
        self.assertFalse(os.path.exists(dbf))
        self.assertEqual(file_operations.pending_rename_cleanup_files(), [])

    def test_deferred_cleanup_never_deletes_changed_file(self):
        shp = os.path.join(self.src_dir, "changed.shp")
        with open(shp, "wb") as stream:
            stream.write(b"old contents")

        with patch("file_operations.os.remove", side_effect=PermissionError("locked")):
            file_operations._enqueue_rename_cleanup([shp])

        with open(shp, "wb") as stream:
            stream.write(b"a different file now uses the old name")
        file_operations._process_cleanup_jobs()

        self.assertTrue(os.path.exists(shp))
        self.assertEqual(file_operations.pending_rename_cleanup_files(), [])

    def test_safe_rename_rejects_editable_layer(self):
        shp = os.path.join(self.src_dir, "editing.shp")
        open(shp, "w").close()
        layer = TestVectorLayer(shp, "editing")
        layer.isEditable = lambda: True

        with self.assertRaises(RuntimeError):
            safe_rename(layer, "renamed.shp")
        self.assertTrue(os.path.exists(shp))
        self.assertFalse(os.path.exists(os.path.join(self.src_dir, "renamed.shp")))

    def test_case_insensitive_sidecars(self):
        # Test shapefile with uppercase/mixed extensions
        shp = os.path.join(self.src_dir, "test.SHP")
        dbf = os.path.join(self.src_dir, "test.dbf")
        shp_xml = os.path.join(self.src_dir, "test.SHP.XML")
        
        open(shp, 'w').close()
        open(dbf, 'w').close()
        open(shp_xml, 'w').close()
        
        files = get_associated_files(shp)
        self.assertEqual(len(files), 3)
        self.assertIn(shp, files)
        self.assertIn(dbf, files)
        self.assertIn(shp_xml, files)

        # Test raster world file casing (.TIF -> .TFW)
        tif = os.path.join(self.src_dir, "raster.TIF")
        tfw = os.path.join(self.src_dir, "raster.TFW")
        open(tif, 'w').close()
        open(tfw, 'w').close()

        files_raster = get_associated_files(tif)
        self.assertEqual(len(files_raster), 2)
        self.assertIn(tif, files_raster)
        self.assertIn(tfw, files_raster)

    def test_query_parameters_safe_move(self):
        shp = os.path.join(self.src_dir, "test.shp")
        dbf = os.path.join(self.src_dir, "test.dbf")
        open(shp, 'w').close()
        open(dbf, 'w').close()

        # Query param in source path
        source_path = shp + "|layername=table|subset=filter"
        layer = TestVectorLayer(source_path, "query_layer")
        
        result = safe_move(layer, self.dest_dir)
        self.assertTrue(result)

        # Verify physical files are in destination
        dest_shp = os.path.join(self.dest_dir, "test.shp")
        dest_dbf = os.path.join(self.dest_dir, "test.dbf")
        self.assertTrue(os.path.exists(dest_shp))
        self.assertTrue(os.path.exists(dest_dbf))

        # Verify original files are gone
        self.assertFalse(os.path.exists(shp))
        self.assertFalse(os.path.exists(dbf))

        # Verify query parameters are reconstructed in datasource
        self.assertEqual(layer.source(), dest_shp + "|layername=table|subset=filter")

    def test_query_parameters_safe_rename(self):
        shp = os.path.join(self.src_dir, "test.shp")
        dbf = os.path.join(self.src_dir, "test.dbf")
        open(shp, 'w').close()
        open(dbf, 'w').close()

        # Query param in source path
        source_path = shp + "|layername=table"
        layer = TestVectorLayer(source_path, "query_layer")

        result = safe_rename(layer, "new_name.shp")
        self.assertTrue(result)

        # Verify physical files
        new_shp = os.path.join(self.src_dir, "new_name.shp")
        new_dbf = os.path.join(self.src_dir, "new_name.dbf")
        self.assertTrue(os.path.exists(new_shp))
        self.assertTrue(os.path.exists(new_dbf))

        # Verify old are gone
        self.assertFalse(os.path.exists(shp))
        self.assertFalse(os.path.exists(dbf))

        # Verify layer source updated with query param and name updated
        self.assertEqual(layer.source().replace('\\', '/'), (new_shp + "|layername=table").replace('\\', '/'))
        self.assertEqual(layer.name(), "new_name")

    def test_safe_rename_file_exists_error(self):
        shp = os.path.join(self.src_dir, "test.shp")
        dbf = os.path.join(self.src_dir, "test.dbf")
        open(shp, 'w').close()
        open(dbf, 'w').close()

        # Target renamed file already exists
        target_dbf = os.path.join(self.src_dir, "collision.dbf")
        open(target_dbf, 'w').close()

        layer = TestVectorLayer(shp, "collision_layer")
        
        # Should raise FileExistsError
        with self.assertRaises(FileExistsError):
            safe_rename(layer, "collision.shp")

        # Verify source files are NOT renamed or removed
        self.assertTrue(os.path.exists(shp))
        self.assertTrue(os.path.exists(dbf))

    def test_safe_rename_rollback_on_failure(self):
        import unittest.mock as mock
        shp = os.path.join(self.src_dir, "test.shp")
        dbf = os.path.join(self.src_dir, "test.dbf")
        shx = os.path.join(self.src_dir, "test.shx")
        open(shp, 'w').close()
        open(dbf, 'w').close()
        open(shx, 'w').close()

        layer = TestVectorLayer(shp, "rollback_layer")

        original_copy = shutil.copy2
        call_count = 0

        # We mock shutil.copy2 to fail on the second call
        def mock_copy(src, dest):
            nonlocal call_count
            call_count += 1
            if call_count == 2:
                raise OSError("Simulated copy failure")
            return original_copy(src, dest)

        with mock.patch('shutil.copy2', side_effect=mock_copy):
            with self.assertRaises(OSError):
                safe_rename(layer, "failed_rename.shp")

        # Verify that all original files still exist on disk (rolled back)
        self.assertTrue(os.path.exists(shp))
        self.assertTrue(os.path.exists(dbf))
        self.assertTrue(os.path.exists(shx))
        # Verify that any partially renamed file does NOT exist
        self.assertFalse(os.path.exists(os.path.join(self.src_dir, "failed_rename.shp")))
        self.assertFalse(os.path.exists(os.path.join(self.src_dir, "failed_rename.dbf")))
        self.assertFalse(os.path.exists(os.path.join(self.src_dir, "failed_rename.shx")))

    def test_safe_rename_rollback_on_update_source_failure(self):
        import unittest.mock as mock
        shp = os.path.join(self.src_dir, "test.shp")
        dbf = os.path.join(self.src_dir, "test.dbf")
        open(shp, 'w').close()
        open(dbf, 'w').close()

        layer = TestVectorLayer(shp, "rollback_layer2")

        # We mock update_layer_source to raise an exception
        with mock.patch('file_operations.update_layer_source', side_effect=ValueError("Simulated update source failure")):
            with self.assertRaises(ValueError):
                safe_rename(layer, "failed_update.shp")

        # Verify that all original files still exist on disk (rolled back)
        self.assertTrue(os.path.exists(shp))
        self.assertTrue(os.path.exists(dbf))
        # Verify that renamed files do not exist
        self.assertFalse(os.path.exists(os.path.join(self.src_dir, "failed_update.shp")))
        self.assertFalse(os.path.exists(os.path.join(self.src_dir, "failed_update.dbf")))

    def test_new_sidecars_detection(self):
        # Vector sidecars
        shp = os.path.join(self.src_dir, "vector.shp")
        qml = os.path.join(self.src_dir, "vector.qml")
        qmd = os.path.join(self.src_dir, "vector.qmd")
        qix = os.path.join(self.src_dir, "vector.qix")
        
        open(shp, 'w').close()
        open(qml, 'w').close()
        open(qmd, 'w').close()
        open(qix, 'w').close()
        
        files = get_associated_files(shp)
        self.assertIn(qml, files)
        self.assertIn(qmd, files)
        self.assertIn(qix, files)

        # Raster sidecars
        tif = os.path.join(self.src_dir, "raster.tif")
        rqml = os.path.join(self.src_dir, "raster.qml")
        rqmd = os.path.join(self.src_dir, "raster.qmd")
        ovr = os.path.join(self.src_dir, "raster.tif.ovr")
        
        open(tif, 'w').close()
        open(rqml, 'w').close()
        open(rqmd, 'w').close()
        open(ovr, 'w').close()
        
        files_raster = get_associated_files(tif)
        self.assertIn(rqml, files_raster)
        self.assertIn(rqmd, files_raster)
        self.assertIn(ovr, files_raster)

    def test_associated_files_ignores_directories(self):
        shp = os.path.join(self.src_dir, "test.shp")
        open(shp, 'w').close()
        
        # Create a directory with name test.dbf to see if it gets ignored
        dbf_dir = os.path.join(self.src_dir, "test.dbf")
        os.makedirs(dbf_dir)
        
        files = get_associated_files(shp)
        self.assertIn(shp, files)
        self.assertNotIn(dbf_dir, files)

    def test_safe_rename_sanitizes_filename(self):
        shp = os.path.join(self.src_dir, "test.shp")
        dbf = os.path.join(self.src_dir, "test.dbf")
        open(shp, 'w').close()
        open(dbf, 'w').close()
        
        layer = TestVectorLayer(shp, "sanitize_layer")
        # Rename using a relative path with subdirectories, which should be sanitized to just basename
        result = safe_rename(layer, "subdir/path/sanitized.shp")
        self.assertTrue(result)
        
        sanitized_shp = os.path.join(self.src_dir, "sanitized.shp")
        self.assertTrue(os.path.exists(sanitized_shp))
        self.assertEqual(layer.source().replace('\\', '/'), sanitized_shp.replace('\\', '/'))

    def test_update_layer_source_none_provider(self):
        shp = os.path.join(self.src_dir, "test.shp")
        layer = TestVectorLayer(shp, "my_layer")
        layer.dataProvider = lambda: None # return None
        new_path = os.path.join(self.dest_dir, "test.shp")
        
        update_layer_source(layer, new_path)
        self.assertEqual(layer.source().replace('\\', '/'), new_path.replace('\\', '/'))
        self.assertEqual(layer.datasource_updated, (new_path, "my_layer", ""))

    def test_resolve_physical_path(self):
        from file_operations import resolve_physical_path
        
        path1 = "/vsizip/E:/QGIS/Admin/china.zip/china.geojson"
        res1 = resolve_physical_path(path1)
        self.assertEqual(res1, os.path.normpath("E:/QGIS/Admin/china.zip"))
        
        path2 = "C:\\Data\\test.shp"
        res2 = resolve_physical_path(path2)
        self.assertEqual(res2, os.path.normpath("C:/Data/test.shp"))
        
        path3 = "/vsicurl/https://domain.com/file.tif"
        res3 = resolve_physical_path(path3)
        # normpath on URL keeps domain forward slashes on Windows because it starts with https:/
        # but let's test it properly:
        res3_clean = res3.replace('\\', '/')
        self.assertEqual(res3_clean, "https:/domain.com/file.tif")

    def test_safe_rename_parent_dir(self):
        # Create a layer pointing to a file in a sub-subdirectory of self.src_dir
        sub_dir = os.path.join(self.src_dir, "old_parent")
        os.makedirs(sub_dir)
        shp = os.path.join(sub_dir, "test.shp")
        dbf = os.path.join(sub_dir, "test.dbf")
        open(shp, 'w').close()
        open(dbf, 'w').close()
        
        layer = TestVectorLayer(shp, "test_layer")
        
        # Rename parent dir "old_parent" to "new_parent"
        result = safe_rename_parent_dir(layer, "new_parent")
        self.assertTrue(result)
        
        new_parent_dir = os.path.join(self.src_dir, "new_parent")
        self.assertTrue(os.path.exists(new_parent_dir))
        self.assertFalse(os.path.exists(sub_dir))
        
        new_shp_path = os.path.join(new_parent_dir, "test.shp")
        self.assertEqual(layer.source().replace('\\', '/'), new_shp_path.replace('\\', '/'))
        self.assertTrue(os.path.exists(new_shp_path))
        self.assertTrue(os.path.exists(os.path.join(new_parent_dir, "test.dbf")))

    def test_safe_rename_dir(self):
        from file_operations import safe_rename_dir
        # Create a directory to rename
        sub_dir = os.path.join(self.src_dir, "old_dir")
        os.makedirs(sub_dir)
        file_path = os.path.join(sub_dir, "file.txt")
        with open(file_path, 'w') as f:
            f.write("test")
            
        result = safe_rename_dir(sub_dir, "new_dir")
        self.assertTrue(result)
        
        new_dir = os.path.join(self.src_dir, "new_dir")
        self.assertTrue(os.path.exists(new_dir))
        self.assertFalse(os.path.exists(sub_dir))
        self.assertTrue(os.path.exists(os.path.join(new_dir, "file.txt")))

    def test_split_qgis_source(self):
        from file_operations import split_qgis_source
        
        # Test basic split
        path1 = "C:\\data\\file.shp|layername=test"
        phys1, q1 = split_qgis_source(path1)
        self.assertEqual(phys1, "C:/data/file.shp")
        self.assertEqual(q1, "|layername=test")
        
        # Test delimited text path with ? query string
        path2 = "file:///C:/Users/tesla/Downloads/test.txt?type=csv&delimiter=%20%5Ct&xField=X&yField=Y"
        phys2, q2 = split_qgis_source(path2)
        self.assertEqual(phys2, "file:///C:/Users/tesla/Downloads/test.txt")
        self.assertEqual(q2, "?type=csv&delimiter=%20%5Ct&xField=X&yField=Y")
        
        # Test combined ? and |
        path3 = "file:///C:/Users/tesla/Downloads/test.txt?type=csv|layername=test"
        phys3, q3 = split_qgis_source(path3)
        self.assertEqual(phys3, "file:///C:/Users/tesla/Downloads/test.txt")
        self.assertEqual(q3, "?type=csv|layername=test")

    def test_safe_migrate_dir_success(self):
        import sys
        orig_qgis = sys.modules.get('qgis')
        orig_core = sys.modules.get('qgis.core')
        
        mock_qgis = MagicMock()
        mock_core = MagicMock()
        mock_qgis.core = mock_core
        sys.modules['qgis'] = mock_qgis
        sys.modules['qgis.core'] = mock_core
        
        try:
            sub_dir = os.path.join(self.src_dir, "to_migrate")
            os.makedirs(sub_dir)
            file_path = os.path.join(sub_dir, "test.shp")
            with open(file_path, 'w') as f:
                f.write("test")
                
            mock_layer = TestVectorLayer(file_path, "layer1")
            mock_project = MagicMock()
            mock_project.mapLayers.return_value = {"layer1_id": mock_layer}
            mock_core.QgsProject.instance.return_value = mock_project
            
            result = safe_migrate_dir(sub_dir, self.dest_dir)
            self.assertTrue(result)
            
            new_dir = os.path.join(self.dest_dir, "to_migrate")
            self.assertTrue(os.path.exists(new_dir))
            self.assertFalse(os.path.exists(sub_dir))
            self.assertTrue(os.path.exists(os.path.join(new_dir, "test.shp")))
            
            expected_new_source = os.path.join(new_dir, "test.shp").replace('\\', '/')
            self.assertEqual(mock_layer.source(), expected_new_source)
        finally:
            if orig_qgis is not None:
                sys.modules['qgis'] = orig_qgis
            elif 'qgis' in sys.modules:
                del sys.modules['qgis']
            if orig_core is not None:
                sys.modules['qgis.core'] = orig_core
            elif 'qgis.core' in sys.modules:
                del sys.modules['qgis.core']

    def test_safe_migrate_dir_file_container(self):
        import sys
        orig_qgis = sys.modules.get('qgis')
        orig_core = sys.modules.get('qgis.core')
        
        mock_qgis = MagicMock()
        mock_core = MagicMock()
        mock_qgis.core = mock_core
        sys.modules['qgis'] = mock_qgis
        sys.modules['qgis.core'] = mock_core
        
        try:
            gpkg_file = os.path.join(self.src_dir, "db.gpkg")
            with open(gpkg_file, 'w') as f:
                f.write("gpkg content")
                
            mock_layer = TestVectorLayer(gpkg_file + "|layername=table1", "layer1")
            mock_project = MagicMock()
            mock_project.mapLayers.return_value = {"layer1_id": mock_layer}
            mock_core.QgsProject.instance.return_value = mock_project
            
            result = safe_migrate_dir(gpkg_file, self.dest_dir)
            self.assertTrue(result)
            
            new_gpkg = os.path.join(self.dest_dir, "db.gpkg")
            self.assertTrue(os.path.exists(new_gpkg))
            self.assertFalse(os.path.exists(gpkg_file))
            
            expected_new_source = new_gpkg.replace('\\', '/') + "|layername=table1"
            self.assertEqual(mock_layer.source(), expected_new_source)
        finally:
            if orig_qgis is not None:
                sys.modules['qgis'] = orig_qgis
            elif 'qgis' in sys.modules:
                del sys.modules['qgis']
            if orig_core is not None:
                sys.modules['qgis.core'] = orig_core
            elif 'qgis.core' in sys.modules:
                del sys.modules['qgis.core']

    def test_safe_migrate_dir_self_nesting(self):
        sub_dir = os.path.join(self.src_dir, "to_migrate")
        os.makedirs(sub_dir)
        
        with self.assertRaises(ValueError):
            safe_migrate_dir(sub_dir, sub_dir)
            
        sub_sub_dir = os.path.join(sub_dir, "inside")
        os.makedirs(sub_sub_dir)
        with self.assertRaises(ValueError):
            safe_migrate_dir(sub_dir, sub_sub_dir)

    def test_safe_migrate_dir_overwrite(self):
        sub_dir = os.path.join(self.src_dir, "to_migrate")
        os.makedirs(sub_dir)
        
        conflict_dir = os.path.join(self.dest_dir, "to_migrate")
        os.makedirs(conflict_dir)
        
        with self.assertRaises(FileExistsError):
            safe_migrate_dir(sub_dir, self.dest_dir)

if __name__ == '__main__':
    unittest.main()
