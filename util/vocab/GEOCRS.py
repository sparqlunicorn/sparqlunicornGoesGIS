from rdflib.namespace import DefinedNamespace, Namespace
from rdflib.term import URIRef

class GEOCRS(DefinedNamespace):

    ProjectedCRS: URIRef
    GeographicCRS: URIRef
    BoundCRS: URIRef


    _NS = Namespace("http://www.opengis.net/ont/crs/")