import os
import sys

# Ensure repository root is on sys.path
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

# Initialize QGIS / Qt mocks for headless testing environments
from .mock_qgis import setup_qgis_mocks
setup_qgis_mocks()
