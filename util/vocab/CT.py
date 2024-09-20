from rdflib.namespace import DefinedNamespace, Namespace
from rdflib.term import URIRef

class CT(DefinedNamespace):


    CollectionClass: URIRef
    FeatureCollectionClass: URIRef
    GeoClass: URIRef
    GeoNamedIndividual: URIRef
    HalfGeoClass: URIRef
    Icontype: URIRef
    TreeConfig: URIRef
    TreeItem: URIRef

    icontype: URIRef
    icontypes: URIRef
    treeitem: URIRef




    _NS = Namespace("http://purl.org/vocab/classtree#")