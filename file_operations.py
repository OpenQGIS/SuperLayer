import os
import shutil
import hashlib
import json
import logging

try:
    from qgis.core import QgsMapLayer, QgsVectorLayer, QgsRasterLayer, QgsSettings
except ImportError:
    # Fallback/Mock classes for environment without QGIS (like CLI test environment)
    class QgsMapLayer:
        pass
    class QgsVectorLayer(QgsMapLayer):
        pass
    class QgsRasterLayer(QgsMapLayer):
        pass
    QgsSettings = None

try:
    from qgis.PyQt.QtCore import QCoreApplication, QTimer
except ImportError:
    QCoreApplication = None
    QTimer = None


_CLEANUP_SETTINGS_KEY = "SuperLayer/pendingRenameCleanupV1"
_cleanup_jobs = []
_cleanup_timer = None
_cleanup_loaded = False


def _file_fingerprint(path):
    """Return a stable identity used to prevent deferred deletion of a new file."""
    stat = os.stat(path)
    digest = hashlib.sha256()
    with open(path, "rb") as stream:
        digest.update(stream.read(65536))
        if stat.st_size > 65536:
            stream.seek(max(0, stat.st_size - 65536))
            digest.update(stream.read(65536))
    return {"size": stat.st_size, "mtime_ns": stat.st_mtime_ns, "digest": digest.hexdigest()}


def _fingerprint_matches(path, expected):
    try:
        return _file_fingerprint(path) == expected
    except OSError:
        return False


def _load_cleanup_jobs():
    global _cleanup_loaded, _cleanup_jobs
    if _cleanup_loaded:
        return
    _cleanup_loaded = True
    if QgsSettings is None:
        return
    try:
        raw = QgsSettings().value(_CLEANUP_SETTINGS_KEY, "")
        loaded = json.loads(str(raw)) if raw else []
        if isinstance(loaded, list):
            _cleanup_jobs = [job for job in loaded if isinstance(job, dict)]
    except Exception as exc:
        logging.getLogger(__name__).warning("Unable to load pending rename cleanup: %s", exc)


def _persist_cleanup_jobs():
    if QgsSettings is None:
        return
    try:
        settings = QgsSettings()
        if _cleanup_jobs:
            settings.setValue(_CLEANUP_SETTINGS_KEY, json.dumps(_cleanup_jobs, ensure_ascii=False))
        else:
            settings.remove(_CLEANUP_SETTINGS_KEY)
    except Exception as exc:
        logging.getLogger(__name__).warning("Unable to persist pending rename cleanup: %s", exc)


def _process_cleanup_jobs():
    """Attempt one non-blocking cleanup pass and retain locked files for retry."""
    global _cleanup_jobs
    remaining_jobs = []
    for job in _cleanup_jobs:
        remaining_files = []
        for item in job.get("files", []):
            path = item.get("path", "")
            if not path or not os.path.exists(path):
                continue
            if not _fingerprint_matches(path, item.get("fingerprint", {})):
                logging.getLogger(__name__).warning(
                    "Skipped deferred deletion because the file changed: %s", path
                )
                continue
            try:
                os.remove(path)
            except OSError:
                remaining_files.append(item)
        if remaining_files:
            job["files"] = remaining_files
            job["attempts"] = int(job.get("attempts", 0)) + 1
            remaining_jobs.append(job)
    _cleanup_jobs = remaining_jobs
    _persist_cleanup_jobs()
    return bool(_cleanup_jobs)


def _on_cleanup_timeout():
    pending = _process_cleanup_jobs()
    if not pending or all(int(job.get("attempts", 0)) >= 60 for job in _cleanup_jobs):
        if _cleanup_timer is not None:
            _cleanup_timer.stop()
        if pending:
            logging.getLogger(__name__).warning(
                "Some renamed source files remain locked and will be retried next time SuperLayer starts"
            )


def _schedule_cleanup():
    global _cleanup_timer
    if not _cleanup_jobs or QTimer is None or QCoreApplication is None:
        return
    try:
        if QCoreApplication.instance() is None:
            return
        if _cleanup_timer is None:
            _cleanup_timer = QTimer()
            _cleanup_timer.setInterval(500)
            _cleanup_timer.timeout.connect(_on_cleanup_timeout)
        if not _cleanup_timer.isActive():
            _cleanup_timer.start()
    except Exception as exc:
        logging.getLogger(__name__).warning("Unable to start deferred rename cleanup: %s", exc)


def resume_pending_rename_cleanup():
    """Resume fingerprint-protected cleanup saved by an earlier QGIS session."""
    _load_cleanup_jobs()
    for job in _cleanup_jobs:
        job["attempts"] = 0
    _process_cleanup_jobs()
    _schedule_cleanup()


def pending_rename_cleanup_files():
    """Return old files still awaiting release by Windows/QGIS."""
    _load_cleanup_jobs()
    return [item.get("path") for job in _cleanup_jobs for item in job.get("files", [])]


def _enqueue_rename_cleanup(paths):
    _load_cleanup_jobs()
    items = []
    for path in paths:
        if os.path.exists(path):
            items.append({"path": os.path.abspath(path), "fingerprint": _file_fingerprint(path)})
    if not items:
        return
    _cleanup_jobs.append({"files": items, "attempts": 0})
    _persist_cleanup_jobs()
    _process_cleanup_jobs()
    _schedule_cleanup()

def split_qgis_source(source_path):
    if not source_path:
        return "", ""
    parts = source_path.split('|', 1)
    phys_path = parts[0]
    q_params = '|' + parts[1] if len(parts) == 2 else ""
    
    if '?' in phys_path:
        sub_parts = phys_path.split('?', 1)
        phys_path = sub_parts[0]
        q_params = '?' + sub_parts[1] + q_params
        
    return phys_path.replace('\\', '/'), q_params

def resolve_physical_path(path):
    if not path:
        return ""
    path = path.replace('\\', '/')
    for prefix in ['/vsizip/', '/vsitar/', '/vsigzip/', '/vsiz/', '/vsicurl/']:
        if path.startswith(prefix):
            path = path[len(prefix):]
            break
    for archive_ext in ['.zip/', '.tar/', '.tar.gz/', '.tgz/', '.gz/']:
        idx = path.lower().find(archive_ext)
        if idx != -1:
            path = path[:idx + len(archive_ext) - 1]
    return os.path.normpath(path)

def get_associated_files(file_path):
    phys_path, _ = split_qgis_source(file_path)
    actual_path = resolve_physical_path(phys_path)
    if not actual_path or not os.path.exists(actual_path):
        return []
    
    if actual_path.lower().endswith(('.zip', '.tar', '.gz', '.tgz', '.tar.gz')):
        return [actual_path]
        
    dir_name = os.path.dirname(actual_path)
    file_name = os.path.basename(actual_path)
    
    # Shapefile extensions
    shp_extensions = ['.shp.xml', '.shp', '.dbf', '.shx', '.prj', '.cpg', '.qpj', '.sbn', '.sbx', '.qml', '.qmd', '.qix']
    
    files_in_dir = os.listdir(dir_name or '.')
    
    # Find the actual case-preserved filename on disk
    actual_file_name = file_name
    for f in files_in_dir:
        if f.lower() == file_name.lower():
            actual_file_name = f
            break
            
    actual_file_name_lower = actual_file_name.lower()
    matched_ext = None
    for ext in shp_extensions:
        if actual_file_name_lower.endswith(ext):
            matched_ext = ext
            break
            
    is_shapefile = matched_ext is not None
    
    if is_shapefile:
        base_prefix = actual_file_name[:-len(matched_ext)]
        target_exts = shp_extensions
    else:
        # Raster
        if actual_file_name_lower.endswith('.aux.xml'):
            base_prefix = actual_file_name[:-8]
            _, main_ext = os.path.splitext(base_prefix)
        else:
            base_prefix, main_ext = os.path.splitext(actual_file_name)
            
        target_exts = [
            main_ext.lower(),
            (main_ext + '.aux.xml').lower(),
            (main_ext + '.ovr').lower(),
            '.tfw',
            '.wld',
            '.prj',
            '.xml',
            '.qml',
            '.qmd'
        ]
        if len(main_ext) >= 4:
            w_char = 'W' if main_ext[-1].isupper() else 'w'
            world_ext = main_ext[0] + main_ext[1] + main_ext[-1] + w_char
            if world_ext.lower() not in target_exts:
                target_exts.append(world_ext.lower())
                
    # Now we find matching files that start with base_prefix case-sensitively
    matching_files = [f for f in files_in_dir if f.startswith(base_prefix)]
    
    ext_to_file = {}
    for f in matching_files:
        ext_part = f[len(base_prefix):].lower()
        if ext_part not in ext_to_file:
            ext_to_file[ext_part] = []
        ext_to_file[ext_part].append(f)
        
    seen = set()
    associated = []
    for ext in target_exts:
        if ext in ext_to_file:
            for f in ext_to_file[ext]:
                full_path = os.path.join(dir_name, f)
                if os.path.isfile(full_path):
                    norm_path = os.path.normcase(os.path.abspath(full_path))
                    if norm_path not in seen:
                        seen.add(norm_path)
                        associated.append(full_path)
                    
    return associated

def safe_copy(source_path, target_dir):
    phys_source_path, query_params = split_qgis_source(source_path)
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)
    files = get_associated_files(phys_source_path)
    copied = []
    for src in files:
        dest = os.path.join(target_dir, os.path.basename(src))
        shutil.copy2(src, dest)
        copied.append(dest)
    return copied

def update_layer_source(layer, new_source_path):
    """Safely updates the layer's source without breaking styling."""
    dp = layer.dataProvider()
    provider_name = dp.name() if dp is not None else ""
    if isinstance(layer, QgsVectorLayer):
        layer.setDataSource(new_source_path, layer.name(), provider_name)
    elif isinstance(layer, QgsRasterLayer):
        layer.setDataSource(new_source_path, layer.name(), provider_name)

def safe_move(layer, target_dir):
    source_path = layer.source()
    phys_source_path, query_params = split_qgis_source(source_path)
    actual_path = resolve_physical_path(phys_source_path)
    if not actual_path or not os.path.exists(actual_path):
        return False
    
    # Early exit if moving to same directory
    source_dir = os.path.dirname(phys_source_path)
    if os.path.normcase(os.path.abspath(source_dir)) == os.path.normcase(os.path.abspath(target_dir)):
        return True

    if not os.path.exists(target_dir):
        os.makedirs(target_dir)
    
    files = get_associated_files(phys_source_path)
    moved_files = []
    
    # Copy files first
    for src in files:
        dest = os.path.join(target_dir, os.path.basename(src))
        shutil.copy2(src, dest)
        moved_files.append((src, dest))
        
    # Verify copied files exist
    for _, dest in moved_files:
        if not os.path.exists(dest):
            return False
            
    # Update layer source path in QGIS
    new_phys_source_path = os.path.join(target_dir, os.path.basename(phys_source_path))
    new_source_path = new_phys_source_path + query_params
    update_layer_source(layer, new_source_path)
    
    # Delete original files after successful swap
    for src, _ in moved_files:
        try:
            os.remove(src)
        except Exception as e:  # noqa: BLE001
            import logging
            logging.getLogger(__name__).error("Failed to remove source file %s: %s", src, e)
    return True

def safe_rename(layer, new_filename):
    new_filename = os.path.basename(new_filename)
    source_path = layer.source()
    phys_source_path, query_params = split_qgis_source(source_path)
    actual_path = resolve_physical_path(phys_source_path)
    if not actual_path or not os.path.exists(actual_path):
        return False
    if hasattr(layer, 'isEditable') and layer.isEditable():
        raise RuntimeError("Cannot rename a layer while it is being edited")
    dir_path = os.path.dirname(phys_source_path)
    _, old_ext = os.path.splitext(phys_source_path)
    new_base_name, _ = os.path.splitext(new_filename)
    new_phys_source_path = os.path.join(dir_path, new_base_name + old_ext)
    
    # Early exit if rename resolves to same file path (case-insensitive comparison)
    if os.path.normcase(os.path.abspath(phys_source_path)) == os.path.normcase(os.path.abspath(new_phys_source_path)):
        if hasattr(layer, 'setName'):
            layer.setName(new_base_name)
        return True

    files = get_associated_files(phys_source_path)
    
    # Pre-calculate destinations and handle complex extensions case-insensitively
    rename_mapping = []
    for src in files:
        if src.lower().endswith('.shp.xml'):
            dest_ext = src[-8:]
        elif src.lower().endswith('.aux.xml'):
            dest_ext = src[-8:]
        else:
            _, src_ext = os.path.splitext(src)
            dest_ext = src_ext
        dest = os.path.join(dir_path, new_base_name + dest_ext)
        rename_mapping.append((src, dest))
        
    # Check for silent overwrite before renaming
    source_set = {os.path.normcase(os.path.abspath(f)) for f in files}
    for _, dest in rename_mapping:
        normalized_dest = os.path.normcase(os.path.abspath(dest))
        if os.path.exists(dest) and normalized_dest not in source_set:
            raise FileExistsError(f"Destination file already exists: {dest}")
            
    copied_files = []
    source_updated = False
    # Copy files first to avoid Windows file lock WinError 32
    try:
        for src, dest in rename_mapping:
            shutil.copy2(src, dest)
            copied_files.append((src, dest))
        
        # Verify copied files exist
        for _, dest in copied_files:
            if not os.path.exists(dest):
                raise FileNotFoundError(f"Failed to copy file: {dest}")
        for src, dest in copied_files:
            if _file_fingerprint(src) != _file_fingerprint(dest):
                raise IOError(f"Copied file verification failed: {dest}")

        # Update layer source path in QGIS
        new_source_path = new_phys_source_path + query_params
        update_layer_source(layer, new_source_path)
        source_updated = True
        
        # Update layer name to match the new file name (without extension)
        if hasattr(layer, 'setName'):
            layer.setName(new_base_name)
        
        # Give Qt a chance to retire the old provider, without blocking its event loop.
        try:
            from qgis.PyQt.QtCore import QCoreApplication
            QCoreApplication.processEvents()
        except ImportError:
            try:
                from qtpy.QtCore import QCoreApplication
                QCoreApplication.processEvents()
            except ImportError:
                try:
                    from PySide2.QtCore import QCoreApplication
                    QCoreApplication.processEvents()
                except ImportError:
                    try:
                        from PySide6.QtCore import QCoreApplication
                        QCoreApplication.processEvents()
                    except ImportError:
                        pass

        # Force garbage collection to release any Python-side wrappers.
        import gc
        gc.collect()

        # Delete unlocked files now; retry locked files asynchronously and across restarts.
        _enqueue_rename_cleanup([src for src, _ in copied_files])
    except Exception as e:
        # Never remove the active destination after the layer has switched to it.
        if not source_updated:
            for _, dest in copied_files:
                try:
                    if os.path.exists(dest):
                        os.remove(dest)
                except Exception as rollback_error:
                    logging.getLogger(__name__).error(
                        "Failed to rollback copied destination file %s: %s", dest, rollback_error
                    )
        raise e
        
    return True

def safe_rename_dir(source_dir, new_dir_name, additional_layers=None):
    if not source_dir or not os.path.exists(source_dir):
        return False
    source_dir = os.path.abspath(source_dir).replace('\\', '/')
    
    parent_dir_parent = os.path.dirname(source_dir)
    new_source_dir = os.path.join(parent_dir_parent, new_dir_name).replace('\\', '/')
    
    # Early exit if rename resolves to same directory path
    if os.path.normcase(os.path.abspath(source_dir)) == os.path.normcase(os.path.abspath(new_source_dir)):
        return True
        
    # Check for overwrite
    if os.path.exists(new_source_dir):
        raise FileExistsError(f"Destination folder already exists: {new_source_dir}")
        
    # Find all layers in QGIS project that point to files inside source_dir
    try:
        from qgis.core import QgsProject
        project = QgsProject.instance()
    except ImportError:
        class MockProject:
            def mapLayers(self):
                return {}
        project = MockProject()
        
    layers_to_update = []
    seen_layers = set()
    
    if additional_layers:
        for layer in additional_layers:
            if layer and layer.source():
                p_path, q_params = split_qgis_source(layer.source())
                layers_to_update.append((layer, p_path, q_params))
                seen_layers.add(layer)
                
    for layer_id, layer in project.mapLayers().items():
        if layer and layer not in seen_layers and layer.source():
            p_path, q_params = split_qgis_source(layer.source())
            l_dir = os.path.dirname(p_path)
            if os.path.normcase(os.path.abspath(l_dir)) == os.path.normcase(os.path.abspath(source_dir)):
                layers_to_update.append((layer, p_path, q_params))
                seen_layers.add(layer)
                
    # Copy directory contents recursively to avoid Windows file locks on move
    shutil.copytree(source_dir, new_source_dir)
    
    try:
        # Update QGIS layer sources to point to new directory
        for layer, p_path, q_params in layers_to_update:
            filename = os.path.basename(p_path)
            new_l_path = os.path.join(new_source_dir, filename).replace('\\', '/') + q_params
            update_layer_source(layer, new_l_path)
            
        # Process pending Qt events to force destruction of old providers
        try:
            from qgis.PyQt.QtCore import QCoreApplication
            QCoreApplication.processEvents()
        except ImportError:
            try:
                from qtpy.QtCore import QCoreApplication
                QCoreApplication.processEvents()
            except ImportError:
                pass
                
        # Force garbage collection to release any Python-side wrappers
        import gc
        gc.collect()
        
        # Delete original directory with a retry loop for Windows locks
        import time
        deleted = False
        for attempt in range(20):
            try:
                shutil.rmtree(source_dir)
                deleted = True
                break
            except Exception:
                try:
                    from qgis.PyQt.QtCore import QCoreApplication
                    QCoreApplication.processEvents()
                except ImportError:
                    pass
                gc.collect()
                time.sleep(0.05)
                
        if not deleted:
            import logging
            logging.getLogger(__name__).warning("Failed to remove old parent directory %s after multiple attempts due to locks", source_dir)
            
    except Exception as e:
        # Rollback copied new directory if anything failed before we updated all layers
        try:
            if os.path.exists(new_source_dir):
                shutil.rmtree(new_source_dir)
        except Exception as rollback_err:
            import logging
            logging.getLogger(__name__).error("Failed to rollback copied destination directory %s: %s", new_source_dir, rollback_err)
        raise e
        
    return True

def safe_rename_parent_dir(layer, new_dir_name):
    phys_source_path, query_params = split_qgis_source(layer.source())
    if not phys_source_path:
        return False
    source_dir = os.path.dirname(phys_source_path)
    return safe_rename_dir(source_dir, new_dir_name, additional_layers=[layer])

def safe_migrate_dir(source_path, target_parent_dir, additional_layers=None):
    if not source_path or not os.path.exists(source_path):
        return False
    source_path = os.path.abspath(source_path).replace('\\', '/')
    target_parent_dir = os.path.abspath(target_parent_dir).replace('\\', '/')
    
    basename = os.path.basename(source_path)
    new_path = os.path.join(target_parent_dir, basename).replace('\\', '/')
    
    # Early exit if same path
    if os.path.normcase(os.path.abspath(source_path)) == os.path.normcase(os.path.abspath(new_path)):
        return True
        
    # Check if target is inside source (only if source is a directory)
    if os.path.isdir(source_path):
        norm_source = os.path.normcase(os.path.abspath(source_path))
        norm_new = os.path.normcase(os.path.abspath(new_path))
        if norm_new == norm_source or norm_new.startswith(norm_source + os.sep) or norm_new.replace('\\', '/').startswith(norm_source.replace('\\', '/') + '/'):
            raise ValueError("Cannot move a directory inside itself.")
            
    # Check for overwrite
    if os.path.exists(new_path):
        raise FileExistsError(f"Destination path already exists: {new_path}")
        
    # Find all layers in QGIS project that point to files inside/at source_path
    try:
        from qgis.core import QgsProject
        project = QgsProject.instance()
    except ImportError:
        class MockProject:
            def mapLayers(self):
                return {}
        project = MockProject()
        
    layers_to_update = []
    seen_layers = set()
    
    if additional_layers:
        for layer in additional_layers:
            if layer and layer.source():
                p_path, q_params = split_qgis_source(layer.source())
                layers_to_update.append((layer, p_path, q_params))
                seen_layers.add(layer)
                
    # Helper to check if a path is under source_path (or is source_path itself)
    def is_under_or_equal(path, parent):
        norm_p = os.path.normcase(os.path.abspath(path))
        norm_parent = os.path.normcase(os.path.abspath(parent))
        return norm_p == norm_parent or norm_p.startswith(norm_parent + os.sep) or norm_p.replace('\\', '/').startswith(norm_parent.replace('\\', '/') + '/')

    for layer_id, layer in project.mapLayers().items():
        if layer and layer not in seen_layers and layer.source():
            p_path, q_params = split_qgis_source(layer.source())
            actual_p_path = resolve_physical_path(p_path)
            if is_under_or_equal(actual_p_path, source_path):
                layers_to_update.append((layer, p_path, q_params))
                seen_layers.add(layer)
                
    # Copy the directory or file
    if os.path.isdir(source_path):
        shutil.copytree(source_path, new_path)
    else:
        # It's a file (like GPKG). Make sure the parent dir exists.
        parent_dir = os.path.dirname(new_path)
        if not os.path.exists(parent_dir):
            os.makedirs(parent_dir)
        shutil.copy2(source_path, new_path)
        # Copy GPKG sidecar WAL/SHM if they exist
        for log_ext in ['-wal', '-shm']:
            log_src = source_path + log_ext
            log_dest = new_path + log_ext
            if os.path.exists(log_src):
                try:
                    shutil.copy2(log_src, log_dest)
                except Exception as e:
                    import logging
                    logging.getLogger(__name__).debug("Failed to copy sidecar file %s: %s", log_src, e)
        
    try:
        # Update QGIS layer sources
        for layer, p_path, q_params in layers_to_update:
            if os.path.isdir(source_path):
                rel_path = os.path.relpath(p_path, source_path)
                new_l_path = os.path.normpath(os.path.join(new_path, rel_path)).replace('\\', '/') + q_params
            else:
                new_l_path = new_path + q_params
            update_layer_source(layer, new_l_path)
            
        # Process pending Qt events to force destruction of old providers
        try:
            from qgis.PyQt.QtCore import QCoreApplication
            QCoreApplication.processEvents()
        except ImportError:
            try:
                from qtpy.QtCore import QCoreApplication
                QCoreApplication.processEvents()
            except ImportError:
                pass
                
        # Force garbage collection to release any Python-side wrappers
        import gc
        gc.collect()
        
        # Delete original directory/file with retry loop
        import time
        deleted = False
        for attempt in range(20):
            try:
                if os.path.isdir(source_path):
                    shutil.rmtree(source_path)
                else:
                    os.remove(source_path)
                    for log_ext in ['-wal', '-shm']:
                        log_src = source_path + log_ext
                        if os.path.exists(log_src):
                            try:
                                os.remove(log_src)
                            except Exception as e:
                                import logging
                                logging.getLogger(__name__).debug("Failed to remove sidecar file %s: %s", log_src, e)
                deleted = True
                break
            except Exception:
                try:
                    from qgis.PyQt.QtCore import QCoreApplication
                    QCoreApplication.processEvents()
                except ImportError:
                    pass
                gc.collect()
                time.sleep(0.05)
                
        if not deleted:
            import logging
            logging.getLogger(__name__).warning("Failed to remove old path %s after multiple attempts due to locks", source_path)
            
    except Exception as e:
        # Rollback
        try:
            if os.path.exists(new_path):
                if os.path.isdir(new_path):
                    shutil.rmtree(new_path)
                else:
                    os.remove(new_path)
                    for log_ext in ['-wal', '-shm']:
                        log_dest = new_path + log_ext
                        if os.path.exists(log_dest):
                            try:
                                os.remove(log_dest)
                            except Exception as e:
                                import logging
                                logging.getLogger(__name__).debug("Failed to remove sidecar file %s during rollback: %s", log_dest, e)
        except Exception as rollback_err:
            import logging
            logging.getLogger(__name__).error("Failed to rollback copied path %s: %s", new_path, rollback_err)
        raise e
        
    return True

def format_size(size_in_bytes):
    """Formats the size in bytes to a human-readable string."""
    if size_in_bytes <= 0:
        return "-"
    val = float(size_in_bytes)
    for unit in ['B', 'KB', 'MB', 'GB']:
        if val < 1024.0:
            return f"{val:.2f} {unit}"
        val /= 1024.0
    return f"{val:.2f} TB"
