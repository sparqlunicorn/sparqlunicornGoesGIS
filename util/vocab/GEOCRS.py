from rdflib.namespace import DefinedNamespace, Namespace
from rdflib.term import URIRef

class GEOCRS(DefinedNamespace):

    #3DCoordinateSystem: URIRef
    AreaOfUse: URIRef
    AxisDirection: URIRef
    BoundCRS: URIRef
    CRS: URIRef
    CompoundCRS: URIRef
    CoordinateConcatenatedOperation: URIRef
    CoordinateConversionOperation: URIRef
    CoordinateOperation: URIRef
    CoordinateTransformationOperation: URIRef
    CoordinateSystemAxis: URIRef
    Datum: URIRef
    DynamicVerticalReferenceFrame: URIRef
    Ellipsoid: URIRef
    GeocentricCRS: URIRef
    GeodeticReferenceFrame: URIRef
    GeographicCRS: URIRef
    Geoid: URIRef
    Grid: URIRef
    OtherCoordinateOperation: URIRef
    PrimeMeridian: URIRef
    ProjectedCRS: URIRef
    PlanarCoordinateSystem: URIRef
    Sphere: URIRef
    SRSApplication: URIRef
    VerticalCRS: URIRef
    VerticalReferenceFrame: URIRef

    abbreviation: URIRef
    accuracy: URIRef
    approximates: URIRef
    area_of_use: URIRef
    asWKT: URIRef
    asProj4: URIRef
    asProjJSON: URIRef
    axis: URIRef
    coordinateOperation: URIRef
    coordinateSystem: URIRef
    datum: URIRef
    direction: URIRef
    ellipsoid: URIRef
    ellipse: URIRef
    epsgCode: URIRef
    eccentricity: URIRef
    flatteningParameter: URIRef
    has_ballpark_transformation: URIRef
    includesSRS: URIRef
    inverse_flattening: URIRef
    isApplicableTo: URIRef
    isBound: URIRef
    isGeocentric: URIRef
    isGeographic: URIRef
    isProjected: URIRef
    isSphere: URIRef
    is_semi_minor_computed: URIRef
    isVertical: URIRef
    longitude: URIRef
    method_name: URIRef
    open_license: URIRef
    operation: URIRef
    primeMeridian: URIRef
    scope: URIRef
    semiMajorAxis: URIRef
    semiMinorAxis: URIRef
    sourceCRS: URIRef
    targetCRS: URIRef
    wktLiteral: URIRef
    unit: URIRef
    unit_auth_code: URIRef
    unit_code: URIRef
    unit_conversion_factor: URIRef
    usage: URIRef
    utm_zone: URIRef


    _NS = Namespace("http://www.opengis.net/ont/crs/")