# SPARQLing Unicorn QGIS Plugin

This plugin adds a GeoJSON layer from SPARQL enpoint queries. The necessary python libs are bundled with the plugin.

qgisMinimumVersion = 3.0

Doxygen Documentation <https://sparqlunicorn.github.io/sparqlunicornGoesGIS/>

## SPARQL Unicorn

The SPARQL Unicorn idea was born at the Computer Applications and Quantitative Methods in Archaeology conference 2019 in Kraków, Poland. As an important part of a scientific conference, networking and knowledge exchange brought interesting topics to daylight: In archaeological and (Digital) Humanities related research documentation, creating and maintaining databases and data analyses play a central role. However, very few databases are made free and open available and accessible and even less are linked into the Linked Open Data Cloud. This fact challenges comparative analyses of records across multiple datasets. But we have a lack of user-friendly, easy to use, free and open tools, especially for Linked Open Data technologies and repositories as well as Wikidata itself. Wikidata also still lacks in recognition as a research tool, not just because of a general anonymousness, but also for the reasons mentioned above. To mitigate these problems, the SPARQL Unicorn was developed, which we would like to propose as a friendly tool series for researchers working with Wikidata and other related triple stores. The unicorn’s aim is to help researchers of ancient studies in using the community driven data from Wikidata and to make it accessible to those without expertise in LOD or SPARQL.

<center><img src="https://raw.githubusercontent.com/sparqlunicorn/sparqlunicorn-logo/master/fivrr/sparql-unicorn-Logo-A.png" width="400"></center>

Florian Thiery, Sophie Charlotte Schmidt, Timo Homburg, & Martina Trognitz. (2020). The SPARQL Unicorn: An introduction. In Research Squirrel Engineers - Squirrel Papers. Mainz, Germany: Florian Thiery. <http://doi.org/10.5281/zenodo.3742186>

## QGIS Plugin

<center><img src="https://raw.githubusercontent.com/sparqlunicorn/sparqlunicornGoesGIS/master/icon.png" width="400"></center>

The `SPARQLing Unicorn QGIS Plugin` is listed under the experimental QGIS plugins:

-   <https://plugins.qgis.org/plugins/sparqlunicorn/>

Please cite the `SPARQLing Unicorn QGIS Plugin` software as shown in [CITATION.cff](https://github.com/sparqlunicorn/sparqlunicornGoesGIS/blob/master/CITATION.cff).

### Change Log

-   0.12 Plugin is now based on QgisTasks, BBOX dialog improved, quick add new triple stores, SPARQL interface improvements, improved list view of geo-classes, ability to add converted RDF sets to triple stores
-   0.11: Added interlinking and enrichment dialog (experimental), use dataset columns as query vars, search for concepts to include in your SPARQL query
-   0.10: Bundled dependent libraries, added new triple stores, added support for non-geo queries
-   0.9: Add triplestore functionallity, add more endpoints
-   0.8: Syntax Highlighting and query validation, support for bbox queries, import and export of rdf files, Preloading of geoconcepts from triple stores
-   0.7: add support for DBpedia and GeoNames
-   0.6: add support for linkedgeodata.org
-   0.5: add support for kerameikos.org
-   0.4: add support for nomisma.org
-   0.3: add support for more multiple vars and add Ordnance Survey UK SPARQL endpoint
-   0.2: bugfixes and more user comfort
-   0.1: initial commit

### Talks and Publications

-   Timo Homburg, & Florian Thiery. (2020, October). Little Minions and SPARQL Unicorns as tools for archaeology. Presented at the ARCHEO.FOSS XIV | 2020 Open software, hardware, processes, data and formats in archaeological research (ARCHEO.FOSS XIV | 2020), virtual: Zenodo. <http://doi.org/10.5281/zenodo.4091734>
-   Timo Homburg, & Florian Thiery. (2020, July). Linked Open Geodata in GIS? Ein Überblick über Linked Geodata Open Source Software. Presented at the AGIT 2020 connecting spatially – virtually (AGIT), Zenodo. <http://doi.org/10.5281/zenodo.3931262>
-   Florian Thiery, & Timo Homburg. (2020, March). QGIS - A SPARQLing Unicorn? Eine Einführung in Linked Open Geodata zur Integration von RDF in QGIS Plugins. Presented at the Anwenderkonferenz für Freie und Open Source Software für Geoinformationssysteme (FOSSGIS) (FOSSGIS2020), University of Freiburg, Germany: Zenodo. <http://doi.org/10.5281/zenodo.3706962>
-   Florian Thiery, & Timo Homburg. (2020). QGIS - A SPARQLing Unicorn? Eine Einführung in Linked Open Geodata zur Integration von RDF in QGIS Plugins. In FOSSGIS 2020: Anwenderkonferenz für Freie und Open Source Software für Geoinformationssysteme (pp. 68–72). University of Freiburg, Germany: FOSSGIS e.V. <http://doi.org/10.5281/zenodo.3719128>

## Credits

-   developers
    -   Research Squirrel Engineers SPARQL Unicorn Working Group
    -   Florian Thiery, M.Sc. in Geodesy and Geoinformatics [0000-0002-3246-3531](https://orcid.org/0000-0002-3246-3531)
    -   Timo Homburg, M.Sc. in Computer Science [0000-0002-9499-5840](https://orcid.org/0000-0002-9499-5840)
-   contact: qgisplugin@sparqlunicorn.link

# Documentation and Help

This short documentation should help users and developers to get a better understanding about the internals of the `SPARQLing Unicorn QGIS Plugin`.

## Querying geospatial data

The  `SPARQLing Unicorn QGIS Plugin` returns QGIS layers from specifically formatted SPARQL queries. In this section the kinds of queries which are supported are presented.

### SPARQL queries including a geometry literal

The SPARQL queries need to include the following components:

-   A query variable which is used to return the geometry literals (usually _?geo_)
-   A query variable indicating the URI of the owl:Individual which is queried (i.e. the feature id) (usually _?item_)

Example:

    SELECT ?item ?geo WHERE {
       ?item a ex:House .
       ?item geosparql:hasGeometry ?geom_obj .
       ?geom_obj geosparql:asWKT ?geo .
    } LIMIT 10

This query queries fictional houses from an unspecified SPARQL endpoint. Each house is associated with a URI which is captured in the _?item_ variable.
The geometry literal (here a WKTLiteral) is captured in the _?geo_ variable.
The results of any additional query variables become new columns of the result set, i.e. the QGIS vector layer.

The SPARQL Unicorn QGIS plugin currently supports the parsing of the following literal types:

-   OGC GeoSPARQL WKT Literals
-   GeoJSON Literals
-   GML Literals
-   WKB Well Known Binary Literals

In the case that the triple store does not include geometry literals but instead provides two properties with latitude and longitude, two variables _?lat_ _?lon_ have to be included in the query description.

Example using the [Kerameikos](http://kerameikos.org/) Triple Store:

    SELECT ?item ?lat ?lon WHERE {
         ?item a <http://www.cidoc-crm.org/cidoc-crm/E53_Place>.
         ?item wgs84_pos:lat ?lat .
         ?item wgs84_pos:long ?lon .
    } LIMIT 10

The triple store configuration should reflect if geometry literals are used or if lat/lon properties are provided.

### Querying all properties of a given semantic class

Very often, a SPARQL query is used to discover linked data, so that not all properties of a given class which should be returned are known.
Similarly, one typically does not want to specify a query variable for all columns of the QGIS vector layer if this can be avoided.

Example: Query 100 schools from Wikidata with all properties

    SELECT ?item ?itemLabel ?rel ?val ?geo WHERE {
        ?item wdt:P31 wd:Q3914 .
        ?item wdt:P625 ?geo .
        ?item ?rel ?val .
        SERVICE wikibase:label { bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en". }
    } LIMIT 100

This query uses the special variables _?rel_ and _?val_ to indicate that all relations and values of the school instances should be included in the result set.

### SPARQL queries without geometry literals

SPARQL queries without geometry literals may be issued to a triple store when the appropriate checkbox ("Allow non-geo queries") is selected in the user interface. This allows for the execution of arbitrary SPARQL queries and returns a QGIS layer without an attached geometry which might be used for merging with other QGIS layers.

Example:

    SELECT ?tower WHERE {
     ?tower a <http://onto.squirrel.link/ontology#Watchtower>.
    } LIMIT 100

### Querying instances with the help of data included in other QGIS layers

The columns of a loaded QGIS vector layer may be used as a query input in the  `SPARQLing Unicorn QGIS Plugin`.

To achieve this behavior QGIS columns are converted to a SPARQL values statement as illustrated in the following example.

Consider a QGIS vector layer of houses which is formatted as follows:

| Geometry  | Address          |
| --------- | ---------------- |
| POINT(..) | First Street  8  |
| POINT(..) | Second Street 32 |
| POINT(..) | Third Street 4   |

The task: Give me the height of all houses which is stored in a given triple store.

Assuming the addresses are unique identifiers in this example, the task could be solved as follows:

    SELECT ?item ?geo ?height WHERE {
        ?item ex:address "First Street 8" .
        ?item ex:height ?height .
        ?item geo:hasGeometry ?geom .
        ?item geo:asWKT ?geo .
    }

However, this approach requires one query per table row and is not user friendly.

A better approach would be to convert the column _Address_ to a query variable so that the following query could be stated:

    SELECT ?item ?geo ?height WHERE {
        ?item ex:address ?address .
        ?item ex:height ?height .
        ?item geo:hasGeometry ?geom .
        ?item geo:asWKT ?geo .
    }

SPARQL 1.1 allows this behaviour by defining a VALUES statement as follows:

    SELECT ?item ?geo ?height WHERE {
        VALUES ?address { "First Street 8" "Second Street 32" "Third Street 4" }
        ?item ex:address ?address .
        ?item ex:height ?height .
        ?item geo:hasGeometry ?geom .
        ?item geo:asWKT ?geo .
    }

The  `SPARQLing Unicorn QGIS Plugin` allows the user to define special query variables which are replaced by VALUES statements of connected columns of QGIS vector layers before sending the SPARQL query to the selected SPARQL endpoint.
A user defined query in this way would look like this:

    SELECT ?item ?geo ?height WHERE {
        ?item ex:address ?_address .
        ?item ex:height ?height .
        ?item geo:hasGeometry ?geom .
        ?item geo:asWKT ?geo .
    }

The underscore in the query variable _?\_address_ marks the variable visibly as to be supplemented by a VALUES statement as given above.

### Using GeoSPARQL or another customized SPARQL query syntax

The supported SPARQL syntax is a matter of the triple store which is queried. The SPARQL Unicorn QGIS plugin does not restrict the usage of SPARQL extensions as long as they are matching the SPARQL syntax.
If a triple store does not support e.g. a GeoSPARQL query then the SPARQL Unicorn QGIS plugin will return an error message.

## Dataset conversion to RDF

To convert a QGIS layer to RDF, each feature of the QGIS layer is converted to an instance of type owl:Indiviual.
Titles of columns become relations in the RDF graph, values of columns become either literals or URIs in the RDF representation.

### Generic conversion process

The generic conversion process does not need any further information to convert a QGIS vector layer to RDF. Geometries of the layer are converted to WKTLiterals in the graph and represented using the GeoSPARQL vocabulary.
The feature ID is used as the name of the instance using a customized namespace defined by the QGIS plugin.
Further information appended to features of the vector data layer is converted to relations associated with the instance defined by its feature id.
Literal types of XSD literals are determined automatically for the types of xsd:string, xsd:double, xsd:integer.

### Defining Interlinks

A better representation of the RDF graph is gained by defining the relations used in the RDF graph beforehand, e.g. by using relations of the Wikidata graph. This mapping from a column name to a relation URI can be given in the Interlinking dialog.

### Mapping Schema format

A mapping schema is defined in XML and saves mappings from QGIS vector layer columns to relation URIs in the to-be-build RDF graph and makes them reusable.

Consider the following example:

Example:

    <?xml version="1.0"?>
    <data>
    <file class="http://onto.squirrel.link/ontology#RomanRoad" indid="groupID" indidprefix="line_"
    namespace="http://lod.squirrel.link/data/intinerarium-antonini/"
    attnamespace="http://lod.squirrel.link/data/intinerarium-antonini/" epsg="4326" nometadata="true" attachepsg="true">

    <column name="groupID" prop="data" propiri="http://onto.squirrel.link/ontology#groupID" range="http://www.w3.org/2001/XMLSchema#string"/>

    <addcolumn prop="annotation" propiri="http://www.w3.org/2000/01/rdf-schema#label" value="Intinerarium Antonini Line"/>

    </file>
    </data>

This mapping schema defines a mapping for a RomanRoad dataset, a dataset of annotated LineStrings. The mapping schema defines a target namespace (namespace) for the instance, an attributenamespace (attnamespace) for relations and coordinate reference system (epsg) and possibly a column which may be used as the individual id (indid).

Then, each column is assigned a configuration with the following attributes:

-   _name_: the name of the column in the QGIS vector layer
-   _prop_: The property type to convert into (DataProperty (data), ObjectProperty (obj), AnnotationProperty (anno), SubClass (subclass))
-   _propiri_: The IRI used in the graph to represent the respective column
-   _range_: The range of the property

## Data Enrichment

The second function of the SPARQL Unicorn Plugin is data enrichment. Here, new columns may be added to an already existing QGIS Vector layer.

### What to enrich?

The first step of a data enrichment is to know what can be enriched.
For example:
Given a dataset of universities including their geolocation, address and name and a triple store only properties with specific attributes might be interesting for an enrichment.
In particular properties which occur sufficiently often should be of interest.
In order to find out which properties exist and how often they are represented in a SPARQL endpoint, a "whattoenrichquery" may be defined in the triple store configuration.
An example is given below:

    SELECT (COUNT(distinct ?con) AS ?countcon) (COUNT(?rel) AS ?countrel) ?rel WHERE {
        ?con wdt:P31 %%concept%% .
        ?con wdt:P625 ?coord .
        ?con ?rel ?val .
    }
    GROUP BY ?rel
    ORDER BY DESC(?countrel)

This query is a template query in which the variable %%concept%% may be replaced by a Wikidata concept.
The query returns every relation linked to instances of %%concept%% and its relative occurrences in relation to the individuals.
The result is interpreted by the  `SPARQLing Unicorn QGIS Plugin` as a list in which most occurring properties are shown first.

### Data enrichment process

To enrich data from a triple store to a QGIS Vector layer, each feature included in the vector layer needs to be at best uniquely identified in the respective triple store.
This has to be done by a matching relation e.g. the name of a university which is also present in Wikidata or by a URI which is already included in the QGIS vector layer.

## Adding new triple stores using configuration files

Apart from the graphical user interface new triple stores may be added to the plugin by modifying the JSON configuration files as follows:

_triplestoreconf.json_: This configuration file is delivered on installation of the SPARQL Unicorn QGIS plugin. It is not modified and serves as a backup for a possible reset option.

_triplestoreconf_personal.json_: This configuration file is created the first time the SPARQL Unicorn QGIS plugin is started. All added triple stores will be stored within there in the following format:

    {
    "name": "Research Squirrel Engineers Triplestore",
    "prefixes": {
      "geosparql": "http://www.opengis.net/ont/geosparql#",
      "owl": "http://www.w3.org/2002/07/owl#",
      "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
      "rdfs": "http://www.w3.org/2000/01/rdf-schema#",
      "spatial": "http://geovocab.org/spatial#",
      "hw": "http://hadrianswall.squirrel.link/ontology#"
    },
    "endpoint": "http://sandbox.mainzed.org/squirrels/sparql",
    "mandatoryvariables": [
      "item",
      "geo"
    ],
    "classfromlabelquery": "SELECT DISTINCT ?class { ?class rdf:type owl:Class . ?class rdfs:label ?label . FILTER(CONTAINS(?label,\"%%label%%\"))} LIMIT 100 ",
    "geoconceptquery": "",
    "whattoenrichquery": "SELECT (COUNT(distinct ?con) AS ?countcon) (COUNT(?rel) AS ?countrel) ?rel WHERE { ?con rdf:type %%concept%% . ?con geosparql:hasGeometry ?coord . ?con ?rel ?val . }  GROUP BY ?rel ORDER BY DESC(?countrel)",
    "geoconceptlimit": 500,
    "querytemplate": [
      {
        "label": "10 Random Geometries",
        "query": "SELECT ?item ?geo WHERE {\n ?item a <%%concept%%>.\n ?item geosparql:hasGeometry ?geom_obj .\n ?geom_obj geosparql:asWKT ?geo .\n } LIMIT 10"
      },
      {
        "label": "Hadrian's Wall Forts",
        "query": "SELECT ?a ?wkt_geom WHERE {\n ?item rdf:type hw:Fort .\n ?item geosparql:hasGeometry ?item_geom . ?item_geom geosparql:asWKT ?wkt_geom .\n }"
      }
    ],
    "crs": 4326,
    "staticconcepts": [
      "http://onto.squirrel.link/ontology#Watchtower",
      "http://hadrianswall.squirrel.link/ontology#Milefortlet",
    ],
    "active": true
    }

The following configuration options exist:

-   _active_: Indicates that the triple store is visible in the GUI
-   _classlabelquery_: A SPARQL query OR a URL which returns a set of labels for a given list of class URIs
-   _classfromlabelquery_: A query which retrieves a set of classes from a given label (useful for class searches)
-   _propertylabelquery_:  A SPARQL query OR a URL which returns labels for a given list of properties
-   _propertyfromlabelquery_:  A SPARQL query OR a URL which returns properties for a given list of labels
-   _crs_: The EPSG code of the CRS which should be used by QGIS to interpret the data received from the triple store
-   _endpoint_: The address of the SPARQL endpoint of the triple store
-   _geoconceptlimit_: A reasonable limit to query considering the performance of the triple store and the data included
-   _geoconceptquery_: A query to retrieve concepts associated to geometrical representations inside the triple store. The results of this query or the content of staticconcepts constitutes the list of concepts which is selectable in the graphical user interface
-   _name_: The name of the triple store which is display in the user interface
-   _mandatoryvariables_: A list of SPARQL query variables which have to be present in the SELECT statement (usually ?item for the URI and ?geo for the geometry but sometimes also ?lat ?lon instead of ?geo)
-   _querytemplate_: A list of JSON objects representing labeled queries which may be selectable in the user interface
-   _staticconcepts_: A list of concepts which are loaded to the dropdown menu of available concepts
-   _prefixes_: A list of prefixes which is used by the triple store. Each prefix in this list is recognized in the query interface automatically.
-   _whattoenrichquery_: A query which is sent to the triple store returning attributes and their occurance frequency for the whattoenrich dialog

The configuration file allows the definition of placeholder variables (currently only %%concept%%) in template queries.
These variables are prefixed and suffixed with %% statements.
Example:

    SELECT ?item ?label ?geo WHERE {
        ?place a <%%concept%%>.
        ?place pleiades:hasLocation ?item .
        ?item geosparql:asWKT ?geo .
        ?item dcterms:title ?label .
    } LIMIT 100

This query defines the placeholder variable %%concept%% which is replaced by the currently selected concept from the dropdown menu in the user interface when a concept is selected.
