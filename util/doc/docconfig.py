
class DocConfig:

    version="SPARQLing Unicorn QGIS Plugin OntDoc Script 0.17"

    versionurl="https://github.com/sparqlunicorn/sparqlunicornGoesGIS-ontdoc"

    bibtextypemappings = {"http://purl.org/ontology/bibo/Document": "@misc",
                          "http://purl.org/ontology/bibo/Article": "@article",
                          "http://purl.org/ontology/bibo/AcademicArticle": "@article",
                          "http://purl.org/ontology/bibo/Thesis": "@phdthesis",
                          "http://purl.org/ontology/bibo/BookSection": "@inbook",
                          "http://purl.org/ontology/bibo/EditedBook": "@book",
                          "http://purl.org/ontology/bibo/Report": "@report",
                          "http://purl.org/ontology/bibo/Book": "@book",
                          "http://purl.org/ontology/bibo/Proceedings": "@inproceedings"}

    classToCollectionClass={
        "http://www.opengis.net/ont/geosparql#SpatialObject": {"class": "http://www.opengis.net/ont/geosparql#SpatialObjectCollection","prop": "http://www.w3.org/2000/01/rdf-schema#member"},
        "http://www.opengis.net/ont/geosparql#Feature":{"class":"http://www.opengis.net/ont/geosparql#FeatureCollection","prop":"http://www.w3.org/2000/01/rdf-schema#member"},
        "http://www.opengis.net/ont/geosparql#Geometry": {"class":"http://www.opengis.net/ont/geosparql#GeometryCollection","prop":"http://www.w3.org/2000/01/rdf-schema#member"},
        "http://www.w3.org/2006/vcard/ns#Individual": {"class":"http://www.w3.org/2006/vcard/ns#Group","prop":"http://www.w3.org/2006/vcard/ns#hasMember"},
        "http://xmlns.com/foaf/0.1/Person": {"class":"http://www.w3.org/2006/vcard/ns#Group","prop":"http://www.w3.org/2006/vcard/ns#hasMember"},
        "http://www.w3.org/ns/lemon/ontolex#LexicalEntry": {"class":"http://www.w3.org/ns/lemon/lime#Lexicon","prop":"http://www.w3.org/ns/lemon/lexicog#entry"},
        "http://www.w3.org/ns/dcat#Dataset": {"class":"http://www.w3.org/ns/lemon/lime#Catalog","prop":"http://www.w3.org/ns/dcat#dataset"},
        "http://www.w3.org/ns/sosa/Observation":{"class":"http://www.w3.org/ns/sosa/ObservationCollection","prop":"http://www.w3.org/2000/01/rdf-schema#member"},
        "http://purl.org/ontology/bibo/Document": {"class":"http://purl.org/ontology/bibo/Collection","prop":"http://www.w3.org/2000/01/rdf-schema#member"},
        "http://purl.org/ontology/bibo/Article": {"class":"http://purl.org/ontology/bibo/Collection","prop":"http://www.w3.org/2000/01/rdf-schema#member"},
        "http://purl.org/ontology/bibo/AcademicArticle": {"class":"http://purl.org/ontology/bibo/Collection","prop":"http://www.w3.org/2000/01/rdf-schema#member"},
        "http://purl.org/ontology/bibo/Thesis": {"class":"http://purl.org/ontology/bibo/Collection","prop":"http://www.w3.org/2000/01/rdf-schema#member"},
        "http://purl.org/ontology/bibo/BookSection": {"class":"http://purl.org/ontology/bibo/Collection","prop":"http://www.w3.org/2000/01/rdf-schema#member"},
        "http://purl.org/ontology/bibo/EditedBook": {"class":"http://purl.org/ontology/bibo/Collection","prop":"http://www.w3.org/2000/01/rdf-schema#member"},
        "http://purl.org/ontology/bibo/Report": {"class":"http://purl.org/ontology/bibo/Collection","prop":"http://www.w3.org/2000/01/rdf-schema#member"},
        "http://purl.org/ontology/bibo/Book": {"class":"http://purl.org/ontology/bibo/Collection","prop":"http://www.w3.org/2000/01/rdf-schema#member"},
        "http://purl.org/ontology/bibo/Proceedings": {"class":"http://purl.org/ontology/bibo/Collection","prop":"http://www.w3.org/2000/01/rdf-schema#member"}
    }

    baselayers={
        "OpenStreetMap (OSM)":{"url":"https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png","default":True,"type":"tile"}
    }

    classtreequery="""PREFIX owl: <http://www.w3.org/2002/07/owl#>\n
            PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>\n
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>\n
            SELECT DISTINCT ?subject ?label ?supertype\n
            WHERE {\n
               { ?individual rdf:type ?subject . } UNION { ?subject rdf:type owl:Class . } UNION { ?subject rdf:type rdfs:Class . } .\n
               OPTIONAL { ?subject rdfs:subClassOf ?supertype } .\n
               OPTIONAL { ?subject rdfs:label ?label. filter(langMatches(lang(?label),\"en\")) }
               OPTIONAL { ?subject rdfs:label ?label }.\n
                FILTER (\n
                    (\n
                    ?subject != owl:Class &&\n
                    ?subject != rdf:List &&\n
                    ?subject != rdf:Property &&\n
                    ?subject != rdfs:Class &&\n
                    ?subject != rdfs:Datatype &&\n
                    ?subject != rdfs:ContainerMembershipProperty &&\n
                    ?subject != owl:DatatypeProperty &&\n
                    ?subject != owl:AnnotationProperty &&\n
                    ?subject != owl:Restriction &&\n
                    ?subject != owl:ObjectProperty &&\n
                    ?subject != owl:NamedIndividual &&\n
                    ?subject != owl:Ontology) )\n
            }"""