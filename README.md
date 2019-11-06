# SPARQL Unicorn Plugin

**This plugin adds a GeoJSON layer from SPARQL enpoint queries.**

* qgisMinimumVersion=3.0
* version=0.7
* author=SPARQL Unicorn, Florian Thiery, Timo Homburg
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
* Nomisma.org: http://nomisma.org/query
* Kerameikos.org: http://kerameikos.org/query
* LinkedGeodata.org: http://linkedgeodata.org/sparql
* DBPedia: http://dbpedia.org/sparql
* GeoNames: http://factforge.net/repositories/ff-news

Prefixes are (mostly) included.

For Wikidata queries geometries as `?geo` --> `Point (x y)` is needed.

For OSUK queries the geom as `?easting` and `?northing` is needed.

For Nomisma/Kerameikos queries the geom as `?lat` and `?long` is needed.

For LinkedGeodata queries geometries as `?geo` --> `POINT (x y)` is needed.

For DBpedia/GeoNames queries the geom as `?lat` and `?lon` is needed.

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

#### Airports in European countries

```sql
SELECT ?label ?geo ?item ?country ?labelC WHERE {
  ?item wdt:P31 wd:Q1248784;
    ?range ?country;
    wdt:P625 ?geo;
    rdfs:label ?label.
  ?country rdfs:label ?labelC.
  FILTER((LANG(?label)) = "en")
  FILTER((LANG(?labelC)) = "en")
  FILTER(?country IN(wd:Q183, wd:Q142, wd:Q145, wd:Q27, wd:Q29, wd:Q38, wd:Q35, wd:Q34, wd:Q20, wd:Q33, wd:Q45, wd:Q189))
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

#### Ogam Stones

```sql
SELECT ?label ?geo ?item WHERE {
  ?item wdt:P31 wd:Q2016147; #Ogam Stone
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

### Nomisma.org

#### All Mints

```sql
SELECT ?mint ?label ?lat ?long WHERE {
   ?loc geo:lat ?lat ;
        geo:long ?long .
   ?mint geo:location ?loc ;
         skos:prefLabel ?label ;
         a nmo:Mint
  FILTER langMatches (lang(?label), 'en')
}
```

### Kerameikos.org

#### All Production Places

```sql
SELECT ?pp ?label ?lat ?long WHERE {
   ?loc geo:lat ?lat ;
        geo:long ?long .
   ?pp geo:location ?loc ;
         skos:prefLabel ?label ;
         a kon:ProductionPlace
  FILTER langMatches (lang(?label), 'en')
}
```

### LinkedGeodata.org

#### Restaurants in Mainz, 500m around of the Mainzer Dom

```sql
SELECT ?item ?label ?geo
FROM <http://linkedgeodata.org> {
  ?item
    a lgdo:Restaurant ;
    rdfs:label ?label ;
    geom:geometry [
      ogc:asWKT ?geo
    ] .

  Filter (
    bif:st_intersects (?geo, bif:st_point (8.274167,49.998889),0.5)
  ) .
}
```

#### Amenity in Cork, 1km around of the UCC

```sql
SELECT ?item ?label ?geo
FROM <http://linkedgeodata.org> {
  ?item
    a lgdo:Amenity ;
    rdfs:label ?label ;
    geom:geometry [
      ogc:asWKT ?geo
    ] .

  Filter (
    bif:st_intersects (?geo, bif:st_point (-8.491873,51.893497),1.0)
  ) .
}
```
### DBPedia

#### 10 Points from DBPedia

```sql
SELECT ?lat ?lon ?location WHERE {
  ?location geo:lat ?lat .
  ?location geo:long ?lon .
}
LIMIT 10
```

### Geonames

#### 10 Points from Geonames

```sql
SELECT ?lat ?lon ?location WHERE {
  ?location geo:lat ?lat .
  ?location geo:long ?lon .
}
LIMIT 10
```
