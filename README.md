# SPARQL Unicorn Wikidata Plugin

**This plugin adds a GeoJSON layer from a Wikidata SPARQL query.**

* qgisMinimumVersion=3.0
* version=0.1
* author=SPARQL Unicorn
* email=rse@fthiery.de

use the following commands in the `Administrator:OSGeo4W Shell` to install required libs:

* python-gqis.bat -m pip install geomet
* python-gqis.bat -m pip install sparqlwrapper
* python-gqis.bat -m pip install geojson

## Sample query

*What is needed?*

* ?label
* ?geo
* ?item

### Ogham Stones

```sql
SELECT ?label ?geo ?item WHERE {
  ?item wdt:P31 wd:Q2016147;
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
ORDER BY (?label)
```

### Hospitals

```sql
SELECT * WHERE {
  ?item ((wdt:P31*)/(wdt:P279*)) wd:Q16917;
    wdt:P625 ?geo;
    rdfs:label ?label.
  FILTER((LANG(?label)) = "en")
}
LIMIT 5000
```
