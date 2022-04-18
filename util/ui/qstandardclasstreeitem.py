from .uiutils import UIUtils
from qgis.PyQt.QtGui import QStandardItem


class QStandardClassTreeItem(QStandardItem):

    def from_json(self,jsonobj):
        if "text" in jsonobj:
            self.setText(jsonobj["text"])
        if "icon" in jsonobj:
            self.setIcon(jsonobj["icon"])
        if "data" in jsonobj:
            dataarray=jsonobj["data"]
            if "nodetype" in jsonobj["data"]:
                self.setData(UIUtils.dataslot_nodetype,jsonobj["data"]["nodetype"])
            if "conceptURI" in jsonobj["data"]:
                self.setData(UIUtils.dataslot_conceptURI, jsonobj["data"]["conceptURI"])
            if "instanceamount" in jsonobj["data"]:
                self.setData(UIUtils.dataslot_instanceamount, jsonobj["data"]["instanceamount"])
            if "instancesloaded" in jsonobj["data"]:
                self.setData(UIUtils.dataslot_instancesloaded, jsonobj["data"]["instancesloaded"])
            if "linkedconceptrel" in jsonobj["data"]:
                self.setData(UIUtils.dataslot_linkedconceptrel, jsonobj["data"]["linkedconceptrel"])

    def toJSON(self):
        dataarray={}
        dataarray["nodetype"]=self.data(UIUtils.dataslot_nodetype)
        dataarray["conceptURI"]=self.data(UIUtils.dataslot_conceptURI)
        dataarray["instanceamount"]=self.data(UIUtils.dataslot_instanceamount)
        dataarray["instancesloaded"]=self.data(UIUtils.dataslot_instancesloaded)
        dataarray["linkedconceptrel"]=self.data(UIUtils.dataslot_linkedconceptrel)
        return {"text":self.getText(),"data":dataarray,"icon":self.getIcon()}
