# SPARQL Unicorn Wikidata Plugin

**This plugin adds a GeoJSON layer from a Wikidata SPARQL query.**

* qgisMinimumVersion=3.0
* version=0.3
* author=SPARQL Unicorn, Florian Thiery
* email=rse@fthiery.de

* You have to install [`pip`](https://raw.githubusercontent.com/sparqlunicorn/sparqlunicornGoesGIS/master/sparql_unicorn/scripts/get-pip.py) first, save this file and run it on the console.

use the following commands in the `Administrator:OSGeo4W Shell` to install required libs for python 2.7 and python 3.x

* https://youtu.be/94W51WuDKzA
  * install in py2: python -m pip install `package`
  * switch from py2 to py3: py3_env
  * install in py3: python -m pip install `package`
* `geomet`, `geojson`, `SPARQLWrapper`, `convertbng`

## QGIS Plugin

This Plugin is listed under die experimentail QGIS Pluigins:

https://plugins.qgis.org/plugins/sparqlunicorn/

## Supported SPARQL endpoints

* Wikidata: https://query.wikidata.org/sparql
* Ordnance Survey UK: http://data.ordnancesurvey.co.uk/datasets/os-linked-data/apis/sparql

Prefixes are (mostly) included.

For Wikidata queries geometries as `?geo` --> `Point (x y)` is needed.

For OSUK queries the geom as `?easting` and `?northing` is needed.

## Sample queries

### Wikidata

#### Airports in Germany

```sql
SELECT ?label ?geo ?item WHERE {
  ?item wdt:P31 wd:Q1248784; #Airport
    ?range wd:Q183; #Germany
    wdt:P625 ?geo;
    rdfs:label ?label.
  FILTER((LANG(?label)) = "en")
}
```

#### Hospitals

```sql
SELECT ?label ?geo ?item WHERE {
  ?item ((wdt:P31*)/(wdt:P279*)) wd:Q16917; #Hospital
    wdt:P625 ?geo;
    rdfs:label ?label.
  FILTER((LANG(?label)) = "en")
}
```

#### Castles as archaeological sites

```sql
SELECT ?label ?geo ?item WHERE {
  ?item wdt:P31 wd:Q839954; #archaeologicalSite
    (wdt:P31/(wdt:P279*)) wd:Q23413; #Castle
    wdt:P625 ?geo;
    rdfs:label ?label.
  FILTER((LANG(?label)) = "en")
}
```

#### Ogham Stones

```sql
SELECT ?label ?geo ?item WHERE {
  ?item wdt:P31 wd:Q2016147; #Ogham Stone
    wdt:P361 wd:Q67978809;
    wdt:P195 ?collection.
  OPTIONAL { ?item wdt:P625 ?geo. }
  OPTIONAL {
    ?item rdfs:label ?label.
    FILTER((LANG(?label)) = "en")
  }
  OPTIONAL {
    ?collection rdfs:label ?collectionLabel.
    FILTER((LANG(?collectionLabel)) = "en")
  }
}
```

### Ordnance Survey UK

#### Roman Antiquity Sites in UK

```sql
SELECT ?uri ?label ?easting ?northing
WHERE {
  ?uri
    gaz:featureType gaz:RomanAntiquity;
    rdfs:label ?label;
    spatial:easting ?easting;
    spatial:northing ?northing;
}
```

#### Antiquity Sites in UK

```sql
SELECT ?uri ?label ?easting ?northing
WHERE {
  ?uri
    gaz:featureType gaz:Antiquity;
    rdfs:label ?label;
    spatial:easting ?easting;
    spatial:northing ?northing;
}
```
