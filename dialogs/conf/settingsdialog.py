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
        self.setWindowIcon(QIcon(self.style().standardIcon(getattr(QStyle.StandardPixmap, 'SP_ComputerIcon'))))
        self.closeButton.clicked.connect(self.close)
        self.clearGraphCacheButton.clicked.connect(self.delGraphCache)
        self.clearClassTreeCacheButton.clicked.connect(self.delClassTreeCache)
        self.clearGeoConceptsCacheButton.clicked.connect(self.delGeoConceptsCache)
        self.classTreeCacheExpiryLineEdit.setText(str(CacheUtils.CLASSTREECACHE_EXPIRY))
        self.geoConceptsCacheExpiryLineEdit.setText(str(CacheUtils.GEOCONCEPTS_EXPIRY))
        self.graphCacheExpiryLineEdit.setText(str(CacheUtils.GRAPHCACHE_EXPIRY))
        self.graphCacheLabel.setText(self.graphCacheLabel.text()+" "+str(CacheUtils.graphCacheSize()))
        self.classTreeCacheLabel.setText(self.classTreeCacheLabel.text() + " " + str(CacheUtils.classTreeCacheSize()))
        self.geoConceptsCacheLabel.setText(self.geoConceptsCacheLabel.text() + " " + str(CacheUtils.geoconceptsCacheSize()))
        self.show()

    def delGeoConceptsCache(self):
        CacheUtils.deleteGeoConceptsCache()
        self.geoConceptsCacheLabel.setText(self.geoConceptsCacheLabel.text()[0:self.geoConceptsCacheLabel.text().rfind(" ")+1]+" 0")

    def delClassTreeCache(self):
        CacheUtils.deleteClassTreeCache()
        self.classTreeCacheLabel.setText(self.classTreeCacheLabel.text()[0:self.classTreeCacheLabel.text().rfind(" ")+1]+" 0")

    def delGraphCache(self):
        CacheUtils.deleteGraphCache()
        self.graphCacheLabel.setText(
            self.graphCacheLabel.text()[0:self.graphCacheLabel.text().rfind(" ") + 1] + " 0")