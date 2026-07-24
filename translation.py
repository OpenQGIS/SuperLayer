from qgis.PyQt.QtCore import QCoreApplication

def tr(text, disambiguation=None):
    """Translate text using QCoreApplication with context 'SuperLayer'."""
    try:
        return QCoreApplication.translate("SuperLayer", text, disambiguation)
    except Exception:
        return text
