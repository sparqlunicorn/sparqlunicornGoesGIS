import os
import json
from ..pages.personpage import PersonPage

class CardDAVExporter:

    def vcardJSONToFile(self,vcard,path):
        with open(path,"w",encoding="utf-8") as f:
            f.write("BEGIN:VCARD\nVERSION:4.0\n")
            f.write("PROFILE:VCARD\n")
            for key in vcard:
                f.write(f"{str(key).upper()}:{str(vcard[key])}\n")
            f.write("END:VCARD\n")


    def generateCardDAVCollection(self, outpath, deploypath, graph,subject,license="",version="3"):
        if not os.path.exists(outpath + "/addressbook/"):
            os.makedirs(outpath + "/addressbook/")
        vcards=PersonPage.generateCollectionWidget(graph,  subject,None, None)
        counter=1
        for vcard in vcards:
            if "fn" in vcard:
                self.vcardJSONToFile(vcard,f'{outpath}/addressbook/{str(vcard["fn"]).lower().replace(" ","_")}.vcf')
            else:
                self.vcardJSONToFile(vcard, f"{outpath}/addressbook/vcard{counter}.vcf")
            counter+=1