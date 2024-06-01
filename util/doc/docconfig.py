
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

    timeproperties = ["http://www.cidoc-crm.org/cidoc-crm/P79_beginning_is_qualified_by",
                      "http://www.cidoc-crm.org/cidoc-crm/P80_end_is_qualified_by",
                      "http://www.w3.org/2006/time#inXSDDateTime", "http://www.w3.org/2006/time#inXSDDate",
                      "http://www.w3.org/2006/time#inXSDDateTimeStamp", "http://www.w3.org/2006/time#inXSDgYear",
                      "http://www.w3.org/2006/time#inXSDgYearMonth"]

    timepointerproperties = ["http://www.cidoc-crm.org/cidoc-crm/P4_has_time-span",
                             "http://www.w3.org/2006/time#hasTime", "http://www.w3.org/2006/time#hasDuration",
                             "http://www.w3.org/2006/time#hasBeginning", "http://www.w3.org/2006/time#hasEnd",
                             "http://www.w3.org/ns/sosa/phenomenonTime", "http://www.w3.org/ns/sosa/resultTime"]

    timeliteraltypes = {
        "http://www.w3.org/2001/XMLSchema#gYear": "http://www.ontology-of-units-of-measure.org/resource/om-2/year",
        "http://www.w3.org/2006/time#generalYear": "http://www.w3.org/2006/time#unitYear",
        "http://www.w3.org/2001/XMLSchema#gMonth": "http://www.ontology-of-units-of-measure.org/resource/om-2/month",
        "http://www.w3.org/TR/owl-time#generalMonth": "http://www.w3.org/2006/time#unitMonth",
        "http://www.w3.org/2001/XMLSchema#gDay": "http://www.ontology-of-units-of-measure.org/resource/om-2/day",
        "http://www.w3.org/TR/owl-time#generalDay": "http://www.w3.org/2006/time#unitDay",
        "http://www.w3.org/2001/XMLSchema#date": "", "http://www.w3.org/2001/XMLSchema#dateTime": ""}

    classToCollectionClass={
        "http://www.opengis.net/ont/geosparql#SpatialObject": {"class": "http://www.opengis.net/ont/geosparql#SpatialObjectCollection","prop": "http://www.w3.org/2000/01/rdf-schema#member"},
        "http://www.geonames.org/ontology#GeonamesFeature":{"class":"http://www.opengis.net/ont/geosparql#FeatureCollection","super":"http://www.opengis.net/ont/geosparql#SpatialObjectCollection","prop":"http://www.w3.org/2000/01/rdf-schema#member"},
        "http://www.geonames.org/ontology#Feature": {
            "class": "http://www.opengis.net/ont/geosparql#FeatureCollection",
            "super": "http://www.opengis.net/ont/geosparql#SpatialObjectCollection",
            "prop": "http://www.w3.org/2000/01/rdf-schema#member"},
        "http://www.opengis.net/ont/geosparql#Feature": {
            "class": "http://www.opengis.net/ont/geosparql#FeatureCollection",
            "super": "http://www.opengis.net/ont/geosparql#SpatialObjectCollection",
            "prop": "http://www.w3.org/2000/01/rdf-schema#member"},
        "http://www.opengis.net/ont/geosparql#Geometry": {"class":"http://www.opengis.net/ont/geosparql#GeometryCollection", "super":"http://www.opengis.net/ont/geosparql#SpatialObjectCollection","prop":"http://www.w3.org/2000/01/rdf-schema#member"},
        "http://geovocab.org/geometry#Geometry": {"class": "http://www.opengis.net/ont/geosparql#GeometryCollection",
                                                   "super": "http://www.opengis.net/ont/geosparql#SpatialObjectCollection",
                                                   "prop": "http://www.w3.org/2000/01/rdf-schema#member"},
        "http://geovocab.org/geometry#BoundingBox": {"class": "http://www.opengis.net/ont/geosparql#GeometryCollection",
                                                  "super": "http://www.opengis.net/ont/geosparql#SpatialObjectCollection",
                                                  "prop": "http://www.w3.org/2000/01/rdf-schema#member"},
        "http://geovocab.org/geometry#LineString": {"class": "http://www.opengis.net/ont/geosparql#GeometryCollection",
                                                     "super": "http://www.opengis.net/ont/geosparql#SpatialObjectCollection",
                                                     "prop": "http://www.w3.org/2000/01/rdf-schema#member"},
        "http://geovocab.org/geometry#MultiLineString": {"class": "http://www.opengis.net/ont/geosparql#GeometryCollection",
                                                    "super": "http://www.opengis.net/ont/geosparql#SpatialObjectCollection",
                                                    "prop": "http://www.w3.org/2000/01/rdf-schema#member"},
        "http://geovocab.org/geometry#MultiPoint": {
            "class": "http://www.opengis.net/ont/geosparql#GeometryCollection",
            "super": "http://www.opengis.net/ont/geosparql#SpatialObjectCollection",
            "prop": "http://www.w3.org/2000/01/rdf-schema#member"},
        "http://geovocab.org/geometry#MultiPolygon": {
            "class": "http://www.opengis.net/ont/geosparql#GeometryCollection",
            "super": "http://www.opengis.net/ont/geosparql#SpatialObjectCollection",
            "prop": "http://www.w3.org/2000/01/rdf-schema#member"},
        "http://geovocab.org/geometry#Polygon": {
            "class": "http://www.opengis.net/ont/geosparql#GeometryCollection",
            "super": "http://www.opengis.net/ont/geosparql#SpatialObjectCollection",
            "prop": "http://www.w3.org/2000/01/rdf-schema#member"},
        "http://www.w3.org/2003/01/geo/wgs84_pos#Point": {
            "class": "http://www.opengis.net/ont/geosparql#GeometryCollection",
            "super": "http://www.opengis.net/ont/geosparql#SpatialObjectCollection",
            "prop": "http://www.w3.org/2000/01/rdf-schema#member"},
        "https://purl.org/geojson/vocab#Point": {
            "class": "http://www.opengis.net/ont/geosparql#GeometryCollection",
            "super": "http://www.opengis.net/ont/geosparql#SpatialObjectCollection",
            "prop": "http://www.w3.org/2000/01/rdf-schema#member"},
        "https://purl.org/geojson/vocab#LineString": {"class": "http://www.opengis.net/ont/geosparql#GeometryCollection",
                                                    "super": "http://www.opengis.net/ont/geosparql#SpatialObjectCollection",
                                                    "prop": "http://www.w3.org/2000/01/rdf-schema#member"},
        "https://purl.org/geojson/vocab#Polygon": {
            "class": "http://www.opengis.net/ont/geosparql#GeometryCollection",
            "super": "http://www.opengis.net/ont/geosparql#SpatialObjectCollection",
            "prop": "http://www.w3.org/2000/01/rdf-schema#member"},
        "https://purl.org/geojson/vocab#MultiPoint": {
            "class": "http://www.opengis.net/ont/geosparql#GeometryCollection",
            "super": "http://www.opengis.net/ont/geosparql#SpatialObjectCollection",
            "prop": "http://www.w3.org/2000/01/rdf-schema#member"},
        "https://purl.org/geojson/vocab#MultiLineString": {
            "class": "http://www.opengis.net/ont/geosparql#GeometryCollection",
            "super": "http://www.opengis.net/ont/geosparql#SpatialObjectCollection",
            "prop": "http://www.w3.org/2000/01/rdf-schema#member"},
        "https://purl.org/geojson/vocab#MultiPolygon": {
            "class": "http://www.opengis.net/ont/geosparql#GeometryCollection",
            "super": "http://www.opengis.net/ont/geosparql#SpatialObjectCollection",
            "prop": "http://www.w3.org/2000/01/rdf-schema#member"},
    "http://purl.org/net/cartCoord#Point": {"class": "http://www.opengis.net/ont/geosparql#GeometryCollection",
                                            "super": "http://www.opengis.net/ont/geosparql#SpatialObjectCollection",
                                            "prop": "http://www.w3.org/2000/01/rdf-schema#member"},
    "http://www.opengis.net/ont/sf#Point": {"class": "http://www.opengis.net/ont/geosparql#GeometryCollection", "super":"http://www.opengis.net/ont/geosparql#SpatialObjectCollection", "prop": "http://www.w3.org/2000/01/rdf-schema#member"},
        "http://www.opengis.net/ont/sf#Envelope": {"class": "http://www.opengis.net/ont/geosparql#GeometryCollection",
                                                "super":"http://www.opengis.net/ont/geosparql#SpatialObjectCollection","prop": "http://www.w3.org/2000/01/rdf-schema#member"},


        "http://www.opengis.net/ont/sf#Geometry": {"class": "http://www.opengis.net/ont/geosparql#GeometryCollection",
                                                "super":"http://www.opengis.net/ont/geosparql#SpatialObjectCollection","prop": "http://www.w3.org/2000/01/rdf-schema#member"},
        "http://www.opengis.net/ont/sf#Line": {"class": "http://www.opengis.net/ont/geosparql#GeometryCollection",
                                                "super":"http://www.opengis.net/ont/geosparql#SpatialObjectCollection","prop": "http://www.w3.org/2000/01/rdf-schema#member"},
        "http://www.opengis.net/ont/sf#LineString": {"class": "http://www.opengis.net/ont/geosparql#GeometryCollection",
                                                "super":"http://www.opengis.net/ont/geosparql#SpatialObjectCollection","prop": "http://www.w3.org/2000/01/rdf-schema#member"},
        "http://www.opengis.net/ont/sf#LinearRing": {"class": "http://www.opengis.net/ont/geosparql#GeometryCollection",
                                                "super":"http://www.opengis.net/ont/geosparql#SpatialObjectCollection","prop": "http://www.w3.org/2000/01/rdf-schema#member"},
        "http://www.opengis.net/ont/sf#MultiCurve": {"class": "http://www.opengis.net/ont/geosparql#GeometryCollection",
                                                "super":"http://www.opengis.net/ont/geosparql#SpatialObjectCollection","prop": "http://www.w3.org/2000/01/rdf-schema#member"},
        "http://www.opengis.net/ont/sf#MultiLineString": {"class": "http://www.opengis.net/ont/geosparql#GeometryCollection",
                                                "super":"http://www.opengis.net/ont/geosparql#SpatialObjectCollection","prop": "http://www.w3.org/2000/01/rdf-schema#member"},
        "http://www.opengis.net/ont/sf#MultiPoint": {"class": "http://www.opengis.net/ont/geosparql#GeometryCollection",
                                                "super":"http://www.opengis.net/ont/geosparql#SpatialObjectCollection","prop": "http://www.w3.org/2000/01/rdf-schema#member"},
        "http://www.opengis.net/ont/sf#MultiPolygon": {"class": "http://www.opengis.net/ont/geosparql#GeometryCollection",
                                                "super":"http://www.opengis.net/ont/geosparql#SpatialObjectCollection","prop": "http://www.w3.org/2000/01/rdf-schema#member"},
        "http://www.opengis.net/ont/sf#MultiSurface": {"class": "http://www.opengis.net/ont/geosparql#GeometryCollection",
                                                "super":"http://www.opengis.net/ont/geosparql#SpatialObjectCollection","prop": "http://www.w3.org/2000/01/rdf-schema#member"},
        "http://www.opengis.net/ont/sf#Polygon": {"class": "http://www.opengis.net/ont/geosparql#GeometryCollection",
                                                "super":"http://www.opengis.net/ont/geosparql#SpatialObjectCollection","prop": "http://www.w3.org/2000/01/rdf-schema#member"},
        "http://www.opengis.net/ont/sf#PolyhedralSurface": {"class": "http://www.opengis.net/ont/geosparql#GeometryCollection",
                                                "super":"http://www.opengis.net/ont/geosparql#SpatialObjectCollection","prop": "http://www.w3.org/2000/01/rdf-schema#member"},
        "http://www.opengis.net/ont/sf#Surface": {"class": "http://www.opengis.net/ont/geosparql#GeometryCollection",
                                                "super":"http://www.opengis.net/ont/geosparql#SpatialObjectCollection","prop": "http://www.w3.org/2000/01/rdf-schema#member"},
        "http://www.opengis.net/ont/sf#TIN": {"class": "http://www.opengis.net/ont/geosparql#GeometryCollection",
                                                "super":"http://www.opengis.net/ont/geosparql#SpatialObjectCollection","prop": "http://www.w3.org/2000/01/rdf-schema#member"},
        "http://www.opengis.net/ont/sf#Triangle": {"class": "http://www.opengis.net/ont/geosparql#GeometryCollection",
                                                "super":"http://www.opengis.net/ont/geosparql#SpatialObjectCollection","prop": "http://www.w3.org/2000/01/rdf-schema#member"},
        "http://www.w3.org/2006/vcard/ns#Individual": {"class":"http://www.w3.org/2006/vcard/ns#Group","prop":"http://www.w3.org/2006/vcard/ns#hasMember"},
        "http://xmlns.com/foaf/0.1/Person": {"class":"http://www.w3.org/2006/vcard/ns#Group","prop":"http://www.w3.org/2006/vcard/ns#hasMember"},
         "https://dblp.org/rdf/schema/Person": {"class": "http://www.w3.org/2006/vcard/ns#Group",
                                                                    "prop": "http://www.w3.org/2006/vcard/ns#hasMember"},

        "http://www.w3.org/ns/lemon/ontolex#LexicalEntry": {"class":"http://www.w3.org/ns/lemon/lime#Lexicon","prop":"http://www.w3.org/ns/lemon/lexicog#entry"},
        "http://www.w3.org/ns/dcat#Dataset": {"class":"http://www.w3.org/ns/dcat#Catalog","prop":"http://www.w3.org/ns/dcat#dataset"},
        "http://www.w3.org/ns/sosa/Observation":{"class":"http://www.w3.org/ns/sosa/ObservationCollection","prop":"http://www.w3.org/2000/01/rdf-schema#member"},
        "http://purl.org/ontology/bibo/Document": {"class": "http://purl.org/ontology/bibo/Collection",
                                                   "prop": "http://www.w3.org/2000/01/rdf-schema#member"},
        "http://xmlns.com/foaf/0.1/Document": {"class": "http://purl.org/ontology/bibo/Collection",
                                                   "prop": "http://www.w3.org/2000/01/rdf-schema#member"},
        "https://dblp.org/rdf/schema/Publication": {"class": "http://purl.org/ontology/bibo/Collection",
                                               "prop": "http://www.w3.org/2000/01/rdf-schema#member"},
        "https://dblp.org/rdf/schema/Article": {"class": "http://purl.org/ontology/bibo/Collection",
                                                  "prop": "http://www.w3.org/2000/01/rdf-schema#member"},
        "http://purl.org/net/nknouf/ns/bibtex#Article": {"class": "http://purl.org/ontology/bibo/Collection",
                                                "prop": "http://www.w3.org/2000/01/rdf-schema#member"},
        "http://purl.org/ontology/bibo/Article": {"class": "http://purl.org/ontology/bibo/Collection",
                                                  "prop": "http://www.w3.org/2000/01/rdf-schema#member"},
        "http://www.wikidata.org/entity/Q13442814": {"class": "http://purl.org/ontology/bibo/Collection",
                                                  "prop": "http://www.w3.org/2000/01/rdf-schema#member"},
        "http://purl.org/ontology/bibo/AcademicArticle": {"class": "http://purl.org/ontology/bibo/Collection",
                                                          "prop": "http://www.w3.org/2000/01/rdf-schema#member"},
        "https://dblp.org/rdf/schema/Inproceedings": {"class": "http://purl.org/ontology/bibo/Collection",
                                                          "prop": "http://www.w3.org/2000/01/rdf-schema#member"},
        "http://purl.org/net/nknouf/ns/bibtex#Inproceedings": {"class": "http://purl.org/ontology/bibo/Collection",
                                                      "prop": "http://www.w3.org/2000/01/rdf-schema#member"},
        "http://purl.org/net/nknouf/ns/bibtex#Inbook": {"class": "http://purl.org/ontology/bibo/Collection",
                                                               "prop": "http://www.w3.org/2000/01/rdf-schema#member"},
        "http://purl.org/net/nknouf/ns/bibtex#Booklet": {"class": "http://purl.org/ontology/bibo/Collection",
                                                        "prop": "http://www.w3.org/2000/01/rdf-schema#member"},
        "http://purl.org/net/nknouf/ns/bibtex#Manual": {"class": "http://purl.org/ontology/bibo/Collection",
                                                         "prop": "http://www.w3.org/2000/01/rdf-schema#member"},
        "http://purl.org/net/nknouf/ns/bibtex#Phdthesis": {"class": "http://purl.org/ontology/bibo/Collection",
                                                        "prop": "http://www.w3.org/2000/01/rdf-schema#member"},
        "http://purl.org/net/nknouf/ns/bibtex#Misc": {"class": "http://purl.org/ontology/bibo/Collection",
                                                           "prop": "http://www.w3.org/2000/01/rdf-schema#member"},
        "http://purl.org/net/nknouf/ns/bibtex#Proceedings": {"class": "http://purl.org/ontology/bibo/Collection",
                                                      "prop": "http://www.w3.org/2000/01/rdf-schema#member"},
        "http://purl.org/ontology/bibo/Thesis": {"class": "http://purl.org/ontology/bibo/Collection",
                                                 "prop": "http://www.w3.org/2000/01/rdf-schema#member"},
        "http://purl.org/ontology/bibo/BookSection": {"class": "http://purl.org/ontology/bibo/Collection",
                                                      "prop": "http://www.w3.org/2000/01/rdf-schema#member"},
        "http://purl.org/ontology/bibo/EditedBook": {"class": "http://purl.org/ontology/bibo/Collection",
                                                     "prop": "http://www.w3.org/2000/01/rdf-schema#member"},
        "http://purl.org/ontology/bibo/Report": {"class": "http://purl.org/ontology/bibo/Collection",
                                                 "prop": "http://www.w3.org/2000/01/rdf-schema#member"},
        "http://purl.org/net/nknouf/ns/bibtex#Techreport": {"class": "http://purl.org/ontology/bibo/Collection",
                                                 "prop": "http://www.w3.org/2000/01/rdf-schema#member"},
        "https://dblp.org/rdf/schema/Incollection": {"class": "http://purl.org/ontology/bibo/Collection",
                                             "prop": "http://www.w3.org/2000/01/rdf-schema#member"},
        "http://purl.org/net/nknouf/ns/bibtex#Incollection": {
                                   "class": "http://purl.org/ontology/bibo/Collection",
                                   "prop": "http://www.w3.org/2000/01/rdf-schema#member"},
        "https://dblp.org/rdf/schema/Book": {"class": "http://purl.org/ontology/bibo/Collection",
                                               "prop": "http://www.w3.org/2000/01/rdf-schema#member"},
        "http://purl.org/net/nknouf/ns/bibtex#Book": {"class": "http://purl.org/ontology/bibo/Collection",
                                             "prop": "http://www.w3.org/2000/01/rdf-schema#member"},
        "https://schema.org/Book": {"class": "http://purl.org/ontology/bibo/Collection",
                                     "prop": "http://www.w3.org/2000/01/rdf-schema#member"},
        "http://schema.org/Book": {"class": "http://purl.org/ontology/bibo/Collection",
                                    "prop": "http://www.w3.org/2000/01/rdf-schema#member"},
        "wd:Q571": {"class": "http://purl.org/ontology/bibo/Collection",
                                   "prop": "http://www.w3.org/2000/01/rdf-schema#member"},
        "http://purl.org/ontology/bibo/Book": {"class": "http://purl.org/ontology/bibo/Collection",
                                               "prop": "http://www.w3.org/2000/01/rdf-schema#member"},
        "http://purl.org/ontology/bibo/Proceedings": {"class": "http://purl.org/ontology/bibo/Collection",
                                                      "prop": "http://www.w3.org/2000/01/rdf-schema#member"}
    }

    namespaceToTopic={
        "http://www.opengis.net/ont/geosparql#":[{"uri":"http://www.wikidata.org/entity/Q121810372","label":"geospatial data"},{"uri":"http://dbpedia.org/resource/Location","label":"Location"},{"uri":"http://dbpedia.org/resource/OGC_GeoSPARQL","label":"OGC GeoSPARQL"}],
        "http://www.opengis.net/ont/sf#": [{"uri": "http://www.wikidata.org/entity/Q121810372", "label": "geospatial data"},{"uri": "http://dbpedia.org/resource/Location", "label": "Location"},{"uri": "http://dbpedia.org/resource/Simple_Features", "label": "Simple Features"}],
        "http://www.w3.org/2003/01/geo/wgs84_pos#": [{"uri":"http://www.wikidata.org/entity/Q121810372","label":"geospatial data"},{"uri":"http://dbpedia.org/resource/Location","label":"Location"}],
        "http://www.georss.org/georss/": [{"uri":"http://www.wikidata.org/entity/Q121810372","label":"geospatial data"},{"uri":"http://dbpedia.org/resource/Location","label":"Location"}],
        "http://www.w3.org/ns/locn#": [{"uri":"http://www.wikidata.org/entity/Q121810372","label":"geospatial data"},{"uri":"http://dbpedia.org/resource/Location","label":"Location"}],
        "http://rdfs.co/juso/": [{"uri":"http://www.wikidata.org/entity/Q121810372","label":"geospatial data"},{"uri":"http://dbpedia.org/resource/Location","label":"Location"}],
        "http://purl.org/dc/terms/spatial": [{"uri":"http://www.wikidata.org/entity/Q121810372","label":"geospatial data"},{"uri":"http://dbpedia.org/resource/Location","label":"Location"}],
        "http://www.w3.org/2006/vcard/ns#":[{"uri":"http://xmlns.com/foaf/0.1/Person","label":"Person"}],
        "http://xmlns.com/foaf/0.1/": [{"uri":"http://xmlns.com/foaf/0.1/Person","label":"Person"}],
        "http://rdfs.org/sioc/ns#": [{"uri":"http://xmlns.com/foaf/0.1/OnlineAccount","label":"Online Account"}],
        "http://www.cidoc-crm.org/cidoc-crm/":[{"uri":"http://dbpedia.org/resource/Cultural_heritage","label":"Cultural Heritage"}],
        "http://www.w3.org/2006/time#": [{"uri":"http://dbpedia.org/resource/Time","label":"Time Data"}],
        "http://www.w3.org/ns/lemon/ontolex#": [{"uri":"http://dbpedia.org/resource/Lexicography","label":"Lexicography data"}],
        "http://www.w3.org/ns/lemon/lime#": [{"uri":"http://dbpedia.org/resource/Lexicography","label":"Lexicography data"}],
        "http://www.w3.org/ns/oa#": [{"uri":"http://dbpedia.org/resource/Web_annotation","label":"Web Annotation"}],
        "http://purl.org/ontology/bibo/": [{"uri":"http://dbpedia.org/resource/Bibliography","label":"Bibliography Data"}]
    }

    baselayers={
        "OpenStreetMap (OSM)":{"url":"https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png","default":True,"type":"tile"}
    }

    classtreequery="""PREFIX owl: <http://www.w3.org/2002/07/owl#>\n
            PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>\n
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>\n
            SELECT DISTINCT ?subject ?label ?supertype\n
            WHERE {\n
               { ?individual %%typeproperty%% ?subject . } UNION { ?subject %%typeproperty%% owl:Class . } UNION { ?subject %%typeproperty%% rdfs:Class . } .\n
               OPTIONAL { ?subject %%subclassproperty%% ?supertype } .\n
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