import os
import shutil

try:
    from qgis.core import QgsMapLayer, QgsVectorLayer, QgsRasterLayer
except ImportError:
    # Fallback/Mock classes for environment without QGIS (like CLI test environment)
    class QgsMapLayer:
        pass
    class QgsVectorLayer(QgsMapLayer):
        pass
    class QgsRasterLayer(QgsMapLayer):
        pass

def split_qgis_source(source_path):
    if not source_path:
        return "", ""
    parts = source_path.split('|', 1)
    if len(parts) == 2:
        return parts[0], '|' + parts[1]
    return source_path, ""

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
        except Exception:
            pass # Non-critical if OS locks file temporarily
    return True

def safe_rename(layer, new_filename):
    new_filename = os.path.basename(new_filename)
    source_path = layer.source()
    phys_source_path, query_params = split_qgis_source(source_path)
    actual_path = resolve_physical_path(phys_source_path)
    if not actual_path or not os.path.exists(actual_path):
        return False
    dir_path = os.path.dirname(phys_source_path)
    _, old_ext = os.path.splitext(phys_source_path)
    new_base_name, _ = os.path.splitext(new_filename)
    new_phys_source_path = os.path.join(dir_path, new_base_name + old_ext)
    
    # Early exit if rename resolves to same file path (case-insensitive comparison)
    if os.path.normcase(os.path.abspath(phys_source_path)) == os.path.normcase(os.path.abspath(new_phys_source_path)):
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
    # Copy files first to avoid Windows file lock WinError 32
    try:
        for src, dest in rename_mapping:
            shutil.copy2(src, dest)
            copied_files.append((src, dest))
        
        # Verify copied files exist
        for _, dest in copied_files:
            if not os.path.exists(dest):
                raise FileNotFoundError(f"Failed to copy file: {dest}")

        # Update layer source path in QGIS
        new_source_path = new_phys_source_path + query_params
        update_layer_source(layer, new_source_path)
        
        # Now that datasource is swapped, delete original files
        for src, _ in copied_files:
            try:
                os.remove(src)
            except Exception:
                pass # Ignore if OS holds file lock briefly
    except Exception as e:
        # Rollback copied files if error occurs before datasource update
        for _, dest in copied_files:
            try:
                if os.path.exists(dest):
                    os.remove(dest)
            except Exception:
                pass
        raise e
        
    return True

def format_size(size_in_bytes):
    """Formats the size in bytes to a human-readable string."""
    if size_in_bytes <= 0:
        return "N/A"
    val = float(size_in_bytes)
    for unit in ['B', 'KB', 'MB', 'GB']:
        if val < 1024.0:
            return f"{val:.2f} {unit}"
        val /= 1024.0
    return f"{val:.2f} TB"
