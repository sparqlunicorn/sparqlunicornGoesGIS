import os
from qgis.PyQt import uic
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QStyle
from qgis.PyQt.QtWidgets import QDialog

from ...util.conf.cacheutils import CacheUtils

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), '../ui/settingsdialog.ui'))



# Class representing a search dialog which may be used to search for concepts or properties.
class SettingsDialog(QDialog, FORM_CLASS):

    def __init__(self,):
        super(QDialog, self).__init__()
        self.setupUi(self)
        self.setWindowTitle("Cache Settings")
        self.setWindowIcon(QIcon(self.style().standardIcon(getattr(QStyle, 'SP_ComputerIcon'))))
        self.closeButton.clicked.connect(self.close)
        self.clearGraphCacheButton.clicked.connect(CacheUtils.deleteGraphCache)
        self.clearClassTreeCacheButton.clicked.connect(CacheUtils.deleteClassTreeCache)
        self.clearGeoConceptsCacheButton.clicked.connect(CacheUtils.deleteGeoConceptsCache)
        self.graphCacheLabel.setText(self.graphCacheLabel.text()+" "+str(CacheUtils.graphCacheSize()))
        self.classTreeCacheLabel.setText(self.classTreeCacheLabel.text() + " " + str(CacheUtils.classTreeCacheSize()))
        self.geoConceptsCacheLabel.setText(self.geoConceptsCacheLabel.text() + " " + str(CacheUtils.geoconceptsCacheSize()))
        self.show()
