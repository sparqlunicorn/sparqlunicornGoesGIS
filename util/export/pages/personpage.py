from ...doc.docutils import DocUtils
from ...doc.docconfig import DocConfig

class PersonPage:

    vcardTohCard={
        "http://xmlns.com/foaf/0.1/birthday":"dt-bday",
        "http://xmlns.com/foaf/0.1/familyName":"p-family-name",
        "http://xmlns.com/foaf/0.1/family_name": "p-family-name",
        "http://xmlns.com/foaf/0.1/firstName": "p-given-name",
        "http://xmlns.com/foaf/0.1/lastName": "p-family-name",
        "http://xmlns.com/foaf/0.1/fullName":"FN",
        "http://xmlns.com/foaf/0.1/givenname": "p-given-name",
        "http://xmlns.com/foaf/0.1/givenName":"p-given-name",
        "http://xmlns.com/foaf/0.1/homePage":"u-url",
        "http://xmlns.com/foaf/0.1/gender": "p-sex",
        "http://xmlns.com/foaf/0.1/img":"u-photo",
        "http://xmlns.com/foaf/0.1/logo":"u-logo",
        "http://xmlns.com/foaf/0.1/mbox":"u-email",
        "http://xmlns.com/foaf/0.1/name":"N",
        "http://xmlns.com/foaf/0.1/nick":"p-nickname",
        "http://xmlns.com/foaf/0.1/phone":"p-tel",
        "http://xmlns.com/foaf/0.1/surname":"p-family-name",
        "http://xmlns.com/foaf/0.1/title":"p-job-title",
        "http://www.w3.org/2000/10/swap/pim/contact#address": "p-street-address",
        "http://www.w3.org/2000/10/swap/pim/contact#birthday": "dt-bday",
        "http://www.w3.org/2000/10/swap/pim/contact#emailAddress": "u-email",
        "http://www.w3.org/2000/10/swap/pim/contact#fax":"p-fax",
        "http://www.w3.org/2000/10/swap/pim/contact#firstName": "p-given-name",
        "http://www.w3.org/2000/10/swap/pim/contact#homepage": "u-url",
        "http://www.w3.org/2000/10/swap/pim/contact#knownAs": "p-nickname",
        "http://www.w3.org/2000/10/swap/pim/contact#lastName": "p-family-name",
        "http://www.w3.org/2000/10/swap/pim/contact#personalTitle": "p-job-title",
        "http://www.w3.org/2000/10/swap/pim/contact#phone":"p-tel",
        "http://www.w3.org/2006/vcard/ns#additional-name":"p-additional-name",
        "http://www.w3.org/2006/vcard/ns#anniversary":"dt-anniversary",
        "http://www.w3.org/2006/vcard/ns#bday":"dt-bday",
        "http://www.w3.org/2006/vcard/ns#email":"u-email",
        "http://www.w3.org/2006/vcard/ns#family-name":"p-family-name",
        "http://www.w3.org/2006/vcard/ns#fax":"p-fax",
        "http://www.w3.org/2006/vcard/ns#geo":"p-geo",
        "http://www.w3.org/2006/vcard/ns#given-name":"p-given-name",
        "http://www.w3.org/2006/vcard/ns#hasAddress":"p-street-address",
        "http://www.w3.org/2006/vcard/ns#hasEmail":"u-email",
        "http://www.w3.org/2006/vcard/ns#hasGeo":"p-geo",
        "http://www.w3.org/2006/vcard/ns#hasGender":"p-sex",
        "http://www.w3.org/2006/vcard/ns#hasLogo":"u-logo",
        "http://www.w3.org/2006/vcard/ns#hasName":"N",
        "http://www.w3.org/2006/vcard/ns#hasPhoto":"u-photo",
        "http://www.w3.org/2006/vcard/ns#hasSound":"u-sound",
        "http://www.w3.org/2006/vcard/ns#hasTelephone":"p-tel",
        "http://www.w3.org/2006/vcard/ns#hasURL":"u-url",
        "http://www.w3.org/2006/vcard/ns#homeTel":"p-tel",
        "http://www.w3.org/2006/vcard/ns#honorific-prefix":"p-honorific-prefix",
        "http://www.w3.org/2006/vcard/ns#honorific-suffix":"p-honorific-suffix",
        "http://www.w3.org/2006/vcard/ns#latitude":"p-latitude",
        "http://www.w3.org/2006/vcard/ns#longitude":"p-longitude",
        "http://www.w3.org/2006/vcard/ns#logo":"u-logo",
        "http://www.w3.org/2006/vcard/ns#mobileEmail":"u-email",
        "http://www.w3.org/2006/vcard/ns#mobileTel":"p-tel",
        "http://www.w3.org/2006/vcard/ns#role":"p-role",
        "http://www.w3.org/2006/vcard/ns#street-address": "p-street-address",
        "http://www.w3.org/2006/vcard/ns#sound":"u-sound",
        "http://www.w3.org/2006/vcard/ns#tel":"p-tel",
        "http://www.w3.org/2006/vcard/ns#title":"p-job-title",
        "http://www.w3.org/2006/vcard/ns#url":"u-url",
        "http://www.w3.org/2006/vcard/ns#workEmail":"u-email",
        "http://www.w3.org/2006/vcard/ns#workTel":"p-tel"
    }

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
        "http://www.w3.org/2006/vcard/ns#honorific-suffix":"",
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


    @staticmethod
    def extractPersonMetadata(subject,graph):
        thevcard={}
        thehcard={}
        for pprop in graph.predicate_objects(subject, True):
            if str(pprop[0]) in PersonPage.vcardTohCard:
                thehcard[str(PersonPage.vcardTohCard[str(pprop[0])])]={"value":str(pprop[1]),"prop":str(pprop[0])}
            if str(pprop[0]) in PersonPage.vcardprops:
                if PersonPage.vcardprops[str(pprop[0])] in thevcard:
                    thevcard[PersonPage.vcardprops[str(pprop[0])]]["value"]+=" "+str(pprop[1])
                else:
                    thevcard[PersonPage.vcardprops[str(pprop[0])]]={"value":str(pprop[1]),"prop":str(pprop[0])}
        return {"vcard":thevcard,"hcard":thehcard}

    @staticmethod
    def hcardToHTMLTable(vcard,hcard):
        result="<table id=\"person\" class=\"h-card\" border=\"1\"><thead><tr><th>Property</th><th>Value</th></tr></thead><tbody>"
        for prop in hcard:
            result+=f"<tr><td><a href=\"{hcard[prop]['prop']}\">{DocUtils.shortenURI(hcard[prop]['prop'])}</a></td>"
            if "http" in hcard[prop]:
                result+=f"<td><a href=\"{hcard[prop]['value']}\" class=\"{prop}\">{DocUtils.shortenURI(hcard[prop]['value'])}</a></td></tr>"
            else:
                if hcard[prop]["prop"] in PersonPage.vcardTohCard:
                    result += f"<td class=\"{PersonPage.vcardTohCard[hcard[prop]['prop']]}\">{hcard[prop]['value']}</td></tr>"
                else:
                    result += f"<td class=\"{prop}\">{hcard[prop]['value']}</td></tr>"
        result += "</tbody></table><script>$('#person').DataTable();</script><button id=\"vcard\" onclick=\"saveTextAsFile(`" + str(PersonPage.vcardJSONToString(vcard)) + "`,'vcard')\">Download VCard</button>"
        return result

    @staticmethod
    def hcardToHTMLTableRow(subject,graph,vcard,hcard,counter):
        label=DocUtils.getLabelForObject(subject,graph)
        result=f"<tr><td><a href=\"{subject}\" target=\"_blank\">{label}</a></td><td><ul>"
        for prop in hcard:
            result+=f"<li><a href=\"{hcard[prop]['prop']}\">{DocUtils.shortenURI(hcard[prop]['prop'])}</a> - "
            if "http" in hcard[prop]:
                result+=f"<a href=\"{hcard[prop]['value']}\" class=\"{prop}\">{DocUtils.shortenURI(hcard[prop]['value'])}</a></li>"
            else:
                if hcard[prop]["prop"] in PersonPage.vcardTohCard:
                    result += f"<span class=\"{PersonPage.vcardTohCard[hcard[prop]['prop']]}\">{hcard[prop]['value']}</span></li>"
                else:
                    result += f"<span class=\"{prop}\">{hcard[prop]['value']}</span></li>"
        return result+"</ul></td></tr>"

    @staticmethod
    def vcardJSONToString(vcard):
        res="BEGIN:VCARD\nVERSION:4.0\nPROFILE:VCARD\n"
        for key in vcard:
            res+=str(key).upper()+":"+str(vcard[key]["value"])+"\n"
        return res+"END:VCARD\n"

    @staticmethod
    def collectionConstraint():
        return DocConfig.collectionclasses

    @staticmethod
    def pageWidgetConstraint():
        return ["http://xmlns.com/foaf/0.1/Person","http://www.w3.org/2006/vcard/ns#Individual","http://schema.org/Person","http://dbpedia.org/ontology/Person","http://www.wikidata.org/entity/Q5"]

    @staticmethod
    def generatePageWidget(graph, subject, templates, f=None, pageWidget=False,counter=0):
        vcardres=PersonPage.extractPersonMetadata(subject,graph)
        if pageWidget and f is not None:
            f.write(PersonPage.hcardToHTMLTable(vcardres["vcard"],vcardres["hcard"]))
        elif not pageWidget and f is not None:
            f.write(PersonPage.hcardToHTMLTableRow(subject,graph,vcardres["vcard"],vcardres["hcard"],counter))
        return vcardres["vcard"]

    @staticmethod
    def generateCollectionWidget(graph, subject,templates, f=None):
        vcards=""
        counter=0
        f.write("<table id=\"person\" class=\"h-card\" border=\"1\"><thead><tr><th>Property</th><th>Value</th></tr></thead><tbody>")
        for person in graph.predicate_objects(subject):
            if str(person[0]) in  DocConfig.collectionrelationproperties:
                vcards+=PersonPage.vcardJSONToString(PersonPage.generatePageWidget(graph,person[1],templates,f,False,counter))
                counter+=1
        f.write("</tbody></table><script>$('#person').DataTable();</script><button id=\"vcard\" onclick=\"saveTextAsFile(`" + str(vcards) + "`,'vcard')\">Download VCards</button>")
        return vcards