from ...doc.docutils import DocUtils
from ...sparqlutils import SPARQLUtils


class PersonPage:

    vcardprops={
        "http://xmlns.com/foaf/0.1/birthday":"BDAY",
        "http://xmlns.com/foaf/0.1/familyName":"N",
        "http://xmlns.com/foaf/0.1/family_name": "N",
        "http://xmlns.com/foaf/0.1/firstName": "N",
        "http://xmlns.com/foaf/0.1/lastName": "N",
        "http://xmlns.com/foaf/0.1/fullName":"FN",
        "http://xmlns.com/foaf/0.1/givenname": "N",
        "http://xmlns.com/foaf/0.1/givenName":"N",
        "http://xmlns.com/foaf/0.1/homePage":"URL",
        "http://xmlns.com/foaf/0.1/gender": "GENDER",
        "http://xmlns.com/foaf/0.1/img":"PHOTO",
        "http://xmlns.com/foaf/0.1/logo":"LOGO",
        "http://xmlns.com/foaf/0.1/mbox":"EMAIL",
        "http://xmlns.com/foaf/0.1/name":"N",
        "http://xmlns.com/foaf/0.1/nick":"NICKNAME",
        "http://xmlns.com/foaf/0.1/phone":"TEL",
        "http://xmlns.com/foaf/0.1/surname":"N",
        "http://xmlns.com/foaf/0.1/title":"TITLE",
        "http://www.w3.org/2000/10/swap/pim/contact#address": "ADR",
        "http://www.w3.org/2000/10/swap/pim/contact#birthday": "BDAY",
        "http://www.w3.org/2000/10/swap/pim/contact#emailAddress": "EMAIL",
        "http://www.w3.org/2000/10/swap/pim/contact#fax":"FAX",
        "http://www.w3.org/2000/10/swap/pim/contact#firstName": "N",
        "http://www.w3.org/2000/10/swap/pim/contact#homepage": "URL",
        "http://www.w3.org/2000/10/swap/pim/contact#knownAs": "NICK",
        "http://www.w3.org/2000/10/swap/pim/contact#lastName": "N",
        "http://www.w3.org/2000/10/swap/pim/contact#personalTitle": "TITLE",
        "http://www.w3.org/2000/10/swap/pim/contact#phone":"TEL",
        "http://www.w3.org/2006/vcard/ns#additional-name":"N",
        "http://www.w3.org/2006/vcard/ns#anniversary":"ANNIVERSARY",
        "http://www.w3.org/2006/vcard/ns#bday":"BDAY",
        "http://www.w3.org/2006/vcard/ns#email":"EMAIL",
        "http://www.w3.org/2006/vcard/ns#family-name":"N",
        "http://www.w3.org/2006/vcard/ns#fax":"FAX",
        "http://www.w3.org/2006/vcard/ns#geo":"GEO",
        "http://www.w3.org/2006/vcard/ns#given-name":"N",
        "http://www.w3.org/2006/vcard/ns#hasAddress":"ADR",
        "http://www.w3.org/2006/vcard/ns#hasEmail":"EMAIL",
        "http://www.w3.org/2006/vcard/ns#hasGeo":"GEO",
        "http://www.w3.org/2006/vcard/ns#hasGender":"GENDER",
        "http://www.w3.org/2006/vcard/ns#hasLogo":"LOGO",
        "http://www.w3.org/2006/vcard/ns#hasName":"N",
        "http://www.w3.org/2006/vcard/ns#hasPhoto":"PHOTO",
        "http://www.w3.org/2006/vcard/ns#hasSound":"SOUND",
        "http://www.w3.org/2006/vcard/ns#hasTelephone":"TEL",
        "http://www.w3.org/2006/vcard/ns#hasURL":"URL",
        "http://www.w3.org/2006/vcard/ns#homeTel":"TEL",
        "http://www.w3.org/2006/vcard/ns#honorific-prefix":"TITLE",
        "http://www.w3.org/2006/vcard/ns#honorific-suffix"
        "http://www.w3.org/2006/vcard/ns#latitude":"LATITUDE",
        "http://www.w3.org/2006/vcard/ns#longitude":"LONGITUDE",
        "http://www.w3.org/2006/vcard/ns#logo":"LOGO",
        "http://www.w3.org/2006/vcard/ns#mobileEmail":"EMAIL",
        "http://www.w3.org/2006/vcard/ns#mobileTel":"TEL",
        "http://www.w3.org/2006/vcard/ns#role":"ROLE",
        "http://www.w3.org/2006/vcard/ns#street-address": "ADR",
        "http://www.w3.org/2006/vcard/ns#sound":"SOUND",
        "http://www.w3.org/2006/vcard/ns#tel":"TEL",
        "http://www.w3.org/2006/vcard/ns#title":"TITLE",
        "http://www.w3.org/2006/vcard/ns#url":"URL",
        "http://www.w3.org/2006/vcard/ns#workEmail":"EMAIL",
        "http://www.w3.org/2006/vcard/ns#workTel":"TEL"
    }

    def createNameProperty(self,vcard):
        print("create the name from differently mapped N values")


    def extractPersonMetadata(self,subject,graph):
        thevcard={}
        for pprop in graph.predicate_objects(subject, True):
            if str(pprop[0]) in self.vcardprops:
                if self.vcardprops[str(pprop[0])] in thevcard:
                    thevcard[self.vcardprops[str(pprop[0])]]["value"]+=" "+str(pprop[1])
                else:
                    thevcard[self.vcardprops[str(pprop[0])]]={"value":str(pprop[1]),"prop":str(pprop[0])}
        return thevcard

    def vcardToHTML(self,vcard):
        result="<table id=\"person\" class=\"vcard\" border=\"1\"><thead><tr><th>Property</th><th>Value</th></tr></thead><tbody>"
        for prop in vcard:
            result+="<tr><td><a href=\""+str(vcard[prop]["prop"])+"\">"+str(DocUtils.shortenURI(prop))+"</a></td>"
            if "http" in vcard[prop]:
                result+="<td><a href=\""+str(vcard[prop]["value"])+"\" class=\""+str(prop)+"\">"+str(DocUtils.shortenURI(vcard[prop]["value"]))+"</a></td></tr>"
            else:
                result += "<td class=\""+str(prop)+"\">" + str(vcard[prop]["value"]) + "</td></tr>"
        result+="</tbody></table><script>$('#person').DataTable();</script><button id=\"vcard\">Download VCard</button>"
        return result


    @staticmethod
    def collectionConstraint():
        return SPARQLUtils.collectionclasses

    @staticmethod
    def pageWidgetConstraint():
        return ["http://xmlns.com/foaf/0.1/Person","http://www.w3.org/2006/vcard/ns#Individual","http://schema.org/Person","http://dbpedia.org/ontology/Person","http://www.wikidata.org/entity/Q5"]

    def generatePageWidget(self, graph, subject, templates, f=None, pageWidget=False):
        print("PageWidget")
        vcard=self.extractPersonMetadata(subject,graph)
        if pageWidget and f!=None:
            f.write(self.vcardToHTML(vcard))
        return vcard

    def generateCollectionWidget(self, graph, templates, subject, f=None):
        print("CollectionWidget")
        vcards=[]
        for person in graph.predicate_objects(subject):
            if str(person[0]) in SPARQLUtils.collectionrelationproperties:
                vcards.append(self.generatePageWidget(graph,person[1],templates,f,True))
        return vcards