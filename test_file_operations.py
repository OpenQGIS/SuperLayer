import unittest
import tempfile
import os
import shutil
from unittest.mock import MagicMock

# Import the code to test
import file_operations
from file_operations import get_associated_files, safe_copy, safe_move, safe_rename, update_layer_source

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

    def dataProvider(self):
        return self._provider

    def setDataSource(self, source, name, provider_name):
        self._source = source
        self.datasource_updated = (source, name, provider_name)

class TestFileOperations(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.src_dir = os.path.join(self.temp_dir.name, 'src')
        self.dest_dir = os.path.join(self.temp_dir.name, 'dest')
        os.makedirs(self.src_dir)
        os.makedirs(self.dest_dir)
        
    def tearDown(self):
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
        
        # Layer source should be updated
        self.assertEqual(layer.source(), renamed_shp)

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

        # Verify layer source updated with query param
        self.assertEqual(layer.source(), new_shp + "|layername=table")

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
        self.assertEqual(layer.source(), sanitized_shp)

    def test_update_layer_source_none_provider(self):
        shp = os.path.join(self.src_dir, "test.shp")
        layer = TestVectorLayer(shp, "my_layer")
        layer.dataProvider = lambda: None # return None
        new_path = os.path.join(self.dest_dir, "test.shp")
        
        update_layer_source(layer, new_path)
        self.assertEqual(layer.source(), new_path)
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

if __name__ == '__main__':
    unittest.main()
