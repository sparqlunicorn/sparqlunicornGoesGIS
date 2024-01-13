import os
import json
from ..pages.personpage import PersonPage

class CardDAVExporter:

    def vcardJSONToFile(self,vcard,path):
        f=open(path,"w")
        f.write("BEGIN:VCARD\nVERSION:4.0\n")
        f.write("PROFILE:VCARD\n")
        for key in vcard:
            f.write(str(key).upper()+":"+str(vcard[key])+"\n")
        f.write("END:VCARD\n")
        f.close()



    def generateCardDAVCollection(self, outpath, deploypath, graph,subject,license="",version="3"):
        if not os.path.exists(outpath + "/addressbook/"):
            os.makedirs(outpath + "/addressbook/")
        vcards=PersonPage().generateCollectionWidget(graph, None, subject, None)
        counter=1
        for vcard in vcards:
            if "fn" in vcard:
                self.vcardJSONToFile(vcard,outpath+"/addressbook/"+str(vcard["fn"]).lower().replace(" ","_")+".vcf")
            else:
                self.vcardJSONToFile(vcard, outpath + "/addressbook/vcard" + str(counter) + ".vcf")
            counter+=1
