from pyproj import CRS
from qgis.core import Qgis
from qgis.core import QgsMessageLog

MESSAGE_CATEGORY = 'ExportCRSTools'

units = {}
units["m"] = "om:meter"
units["metre"] = "om:metre"
units["grad"] = "om:degree"
units["degree"] = "om:degree"
units["ft"] = "om:foot"
units["us-ft"] = "om:usfoot"
scope = {}
scope["geodesy"] = "geocrs:Geodesy"
scope["topographic mapping"] = "geocrs:TopographicMap"
scope["spatial referencing"] = "geocrs:SpatialReferencing"
scope["engineering survey"] = "geocrs:EngineeringSurvey"
scope["satellite survey"] = "geocrs:SatelliteSurvey"
scope["satellite navigation"] = "geocrs:SatelliteNvaigation"
scope["coastal hydrography"] = "geocrs:CoastalHydrography"
scope["offshore engineering"] = "geocrs:OffshoreEngineering"
scope["hydrography"] = "geocrs:Hydrography"
scope["drilling"] = "geocrs:Drilling"
scope["nautical charting"] = "geocrs:NauticalChart"
scope["oil and gas exploration"] = "geocrs:OilAndGasExploration"
scope["cadastre"] = "geocrs:CadastreMap"
coordinatesystem = {}
coordinatesystem["ellipsoidal"] = "geocrs:EllipsoidalCoordinateSystem"
coordinatesystem["cartesian"] = "geocrs:CartesianCoordinateSystem"
coordinatesystem["vertical"] = "geocrs:VerticalCoordinateSystem"
coordinatesystem["ft"] = "om:foot"
coordinatesystem["us-ft"] = "om:usfoot"
spheroids = {}
spheroids["GRS80"] = "geocrsgeod:GRS1980"
spheroids["GRS 80"] = "geocrsgeod:GRS1980"
spheroids["GRS67"] = "geocrsgeod:GRS67"
spheroids["GRS 1967"] = "geocrsgeod:GRS67"
spheroids["GRS 1967 Modified"] = "geocrsgeod:GRS67Modified"
spheroids["GRS 67"] = "geocrsgeod:GRS67"
spheroids["GRS1980"] = "geocrsgeod:GRS1980"
spheroids["GRS 1980"] = "geocrsgeod:GRS1980"
spheroids["NWL 9D"] = "geocrsgeod:NWL9D"
spheroids["PZ-90"] = "geocrsgeod:PZ90"
spheroids["Airy 1830"] = "geocrsgeod:Airy1830"
spheroids["Airy Modified 1849"] = "geocrsgeod:AiryModified1849"
spheroids["intl"] = "geocrsgeod:International1924"
spheroids["aust_SA"] = "geocrsgeod:AustralianNationalSpheroid"
spheroids["Australian National Spheroid"] = "geocrsgeod:AustralianNationalSpheroid"
spheroids["International 1924"] = "geocrsgeod:International1924"
spheroids["clrk"] = "geocrsgeod:Clarke1866"
spheroids["War Office"] = "geocrsgeod:WarOffice"
spheroids["evrst30"] = "geocrsgeod:Everest1930"
spheroids["clrk66"] = "geocrsgeod:Clarke1866"
spheroids["Plessis 1817"] = "geocrsgeod:Plessis1817"
spheroids["Danish 1876"] = "geocrsgeod:Danish1876"
spheroids["Struve 1860"] = "geocrsgeod:Struve1860"
spheroids["IAG 1975"] = "geocrsgeod:IAG1975"
spheroids["Clarke 1866"] = "geocrsgeod:Clarke1866"
spheroids["Clarke 1858"] = "geocrsgeod:Clarke1858"
spheroids["Clarke 1880"] = "geocrsgeod:Clarke1880"
spheroids["Helmert 1906"] = "geocrsgeod:Helmert1906"
spheroids["Moon_2000_IAU_IAG"] = "geocrsgeod:Moon2000_IAU_IAG"
spheroids["CGCS2000"] = "geocrsgeod:CGCS2000"
spheroids["GSK-2011"] = "geocrsgeod:GSK2011"
spheroids["Zach 1812"] = "geocrsgeod:Zach1812"
spheroids["Hough 1960"] = "geocrsgeod:Hough1960"
spheroids["Hughes 1980"] = "geocrsgeod:Hughes1980"
spheroids["Indonesian National Spheroid"] = "geocrsgeod:IndonesianNationalSpheroid"
spheroids["clrk80"] = "geocrsgeod:Clarke1880RGS"
spheroids["Clarke 1880 (Arc)"] = "geocrsgeod:Clarke1880ARC"
spheroids["Clarke 1880 (RGS)"] = "geocrsgeod:Clarke1880RGS"
spheroids["Clarke 1880 (IGN)"] = "geocrsgeod:Clarke1880IGN"
spheroids["clrk80ign"] = "geocrsgeod:Clarke1880IGN"
spheroids["WGS66"] = "geocrsgeod:WGS66"
spheroids["WGS 66"] = "geocrsgeod:WGS66"
spheroids["WGS72"] = "geocrsgeod:WGS72"
spheroids["WGS 72"] = "geocrsgeod:WGS72"
spheroids["WGS84"] = "geocrsgeod:WGS84"
spheroids["WGS 84"] = "geocrsgeod:WGS84"
spheroids["Krassowsky 1940"] = "geocrsgeod:Krassowsky1940"
spheroids["krass"] = "geocrsgeod:Krassowsky1940"
spheroids["Bessel 1841"] = "geocrsgeod:Bessel1841"
spheroids["bessel"] = "geocrsgeod:Bessel1841"
spheroids["Bessel Modified"] = "geocrsgeod:BesselModified"
projections = {}
projections["tmerc"] = "geocrs:TransverseMercatorProjection"
projections["omerc"] = "geocrs:ObliqueMercatorProjection"
projections["merc"] = "geocrs:MercatorProjection"
projections["sinu"] = "geocrs:SinusoidalProjection"
projections["rpoly"] = "geocrs:RectangularPolyconicProjection"
projections["poly"] = "geocrs:AmericanPolyconicProjection"
projections["eqdc"] = "geocrs:EquidistantConicProjection"
projections["sterea"] = "geocrs:ObliqueStereographicProjection"
projections["cea"] = "geocrs:CylindricalEqualArea"
projections["aea"] = "geocrs:AlbersEqualAreaProjection"
projections["eqearth"] = "geocrs:EqualEarthProjection"
projections["natearth"] = "geocrs:NaturalEarthProjection"
projections["stere"] = "geocrs:StereographicProjection"
projections["cass"] = "geocrs:CassiniProjection"
projections["nell"] = "geocrs:PseudoCylindricalProjection"
projections["eck1"] = "geocrs:PseudoCylindricalProjection"
projections["eck2"] = "geocrs:PseudoCylindricalProjection"
projections["eck3"] = "geocrs:PseudoCylindricalProjection"
projections["eck4"] = "geocrs:PseudoCylindricalProjection"
projections["eck5"] = "geocrs:PseudoCylindricalProjection"
projections["eck6"] = "geocrs:PseudoCylindricalProjection"
projections["eqc"] = "geocrs:EquidistantCylindricalProjection"
projections["col_urban"] = "geocrs:ColombiaUrbanProjection"
projections["laea"] = "geocrs:LambertAzimuthalEqualArea"
projections["leac"] = "geocrs:LambertEqualAreaConic"
projections["labrd"] = "geocrs:LabordeProjection"
projections["lcc"] = "geocrs:LambertConformalConicProjection"
projections["gnom"] = "geocrs:GnomonicProjection"
projections["bonne"] = "geocrs:BonneProjection"
projections["moll"] = "geocrs:MollweideProjection"
projections["mill"] = "geocrs:MillerProjection"
projections["nicol"] = "geocrs:NicolosiGlobularProjection"
projections["collg"] = "geocrs:CollignonProjection"
projections["robin"] = "geocrs:RobinsonProjection"
projections["loxim"] = "geocrs:LoximuthalProjection"
projections["aitoff"] = "geocrs:AitoffProjection"
projections["ortho"] = "geocrs:OrthographicProjection"
projections["kav5"] = "geocrs:PseudoCylindricalProjection"
projections["tcea"] = "geocrs:CylindricalProjection"
projections["utm"] = "geocrs:UniversalTransverseMercatorProjection"
projections["krovak"] = "geocrs:Krovak"
projections["geocent"] = "geocrs:Geocentric"
projections["latlong"] = "geocrs:LatLonProjection"
projections["longlat"] = "geocrs:LonLatProjection"

class ConvertCRS:

	def __init__(self):
		self.ttlhead = "@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .\n"
		self.ttlhead += "@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .\n"
		self.ttlhead += "@prefix owl: <http://www.w3.org/2002/07/owl#> .\n"
		self.ttlhead += "@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .\n"
		self.ttlhead += "@prefix skos: <http://www.w3.org/2004/02/skos/core#> .\n"
		self.ttlhead += "@prefix prov: <http://www.w3.org/ns/prov-o/> .\n"
		self.ttlhead += "@prefix geoepsg: <http://www.opengis.net/def/crs/EPSG/0/> .\n"
		self.ttlhead += "@prefix geo: <http://www.opengis.net/ont/geosparql#> .\n"
		self.ttlhead += "@prefix geocrs: <http://www.opengis.net/ont/crs/> .\n"
		self.ttlhead += "@prefix geocrsdatum: <http://www.opengis.net/ont/crs/datum/> .\n"
		self.ttlhead += "@prefix geocrsisbody: <http://www.opengis.net/ont/crs/isbody/> .\n"
		self.ttlhead += "@prefix geocrsgrid: <http://www.opengis.net/ont/crs/grid/> .\n"
		self.ttlhead += "@prefix geocrsproj: <http://www.opengis.net/ont/crs/proj/> .\n"
		self.ttlhead += "@prefix geocrsaxis: <http://www.opengis.net/ont/crs/cs/axis/> .\n"
		self.ttlhead += "@prefix geocrsgeod: <http://www.opengis.net/ont/crs/geod/> .\n"
		self.ttlhead += "@prefix geocrsaou: <http://www.opengis.net/ont/crs/areaofuse/> .\n"
		self.ttlhead += "@prefix geocrsmeridian: <http://www.opengis.net/ont/crs/primeMeridian/> .\n"
		self.ttlhead += "@prefix geocrsoperation: <http://www.opengis.net/ont/crs/operation/> .\n"
		self.ttlhead += "@prefix geocs: <http://www.opengis.net/ont/crs/cs/> .\n"
		self.ttlhead += "@prefix dc: <http://purl.org/dc/elements/1.1/> .\n"
		self.ttlhead += "@prefix wd: <http://www.wikidata.org/entity/> .\n"
		self.ttlhead += "@prefix om: <http://www.ontology-of-units-of-measure.org/resource/om-2/> .\n"

	@staticmethod
	def convertCRSFromEPSG(epsgcode,ttl):
		if "EPSG:" in epsgcode:
			epsgcode=epsgcode.replace("EPSG:","")
		try:
			curcrs=CRS.from_epsg(int(epsgcode))
			print("EPSG: "+str(epsgcode))
			ttl+=ConvertCRS.crsToTTL(ttl, curcrs, epsgcode, 1, None)
		except:
			QgsMessageLog.logMessage("Could not parse EPSG code "+str(epsgcode), MESSAGE_CATEGORY, Qgis.Info)
		return ttl

	@staticmethod
	def convertCRSFromWKTStringSet(wkt,ttl, authcode=None):
		if authcode!=None and "EPSG:" in authcode:
			authcode=authcode.replace("EPSG:","")
		try:
			curcrs=CRS.from_wkt(wkt)
			QgsMessageLog.logMessage("Parsed WKT " + str(curcrs), MESSAGE_CATEGORY, Qgis.Info)
			if authcode!=None and authcode!="":
				res=ConvertCRS.crsToTTL(ttl, curcrs, authcode, 1, None)
			else:
				res=ConvertCRS.crsToTTL(ttl, curcrs, "WKT", 1, None)
			QgsMessageLog.logMessage("Parsed WKT Res " + str(res), MESSAGE_CATEGORY, Qgis.Info)
			ttl=res
		except:
			QgsMessageLog.logMessage("Could not parse WKT "+str(wkt), MESSAGE_CATEGORY, Qgis.Info)
		return ttl

	@staticmethod
	def convertCRSFromWKTString(wkt,ttl, authcode=None):
		set=ConvertCRS.convertCRSFromWKTStringSet(wkt,ttl, authcode)
		return "".join(set)

	@staticmethod
	def crsToTTL(ttl,curcrs,x,geodcounter,crsclass):
		epsgcode=str(x)
		wkt=curcrs.to_wkt().replace("\"","'").strip()
		if crsclass is not None:
			ttl.add("geoepsg:"+epsgcode+" rdf:type "+crsclass+" .\n")
		elif "Projected CRS" in curcrs.type_name:
			ttl.add("geoepsg:"+epsgcode+" rdf:type geocrs:ProjectedCRS .\n")
		elif "Geographic 2D CRS" in curcrs.type_name:
			ttl.add("geoepsg:"+epsgcode+" rdf:type geocrs:GeographicCRS .\n")
		elif "Geographic 3D CRS" in curcrs.type_name:
			ttl.add("geoepsg:"+epsgcode+" rdf:type geocrs:GeographicCRS .\n")
		elif "Bound CRS" in curcrs.type_name:
			ttl.add("geoepsg:"+epsgcode+" rdf:type geocrs:BoundCRS .\n")
		elif "Vertical CRS" in curcrs.type_name:
			ttl.add("geoepsg:"+epsgcode+" rdf:type geocrs:VerticalCRS .\n")
		elif "Geocentric CRS" in curcrs.type_name:
			ttl.add("geoepsg:"+epsgcode+" rdf:type geocrs:GeocentricCRS .\n")
		elif "Geographic 3D CRS" in curcrs.type_name:
			ttl.add("geoepsg:"+epsgcode+" rdf:type geocrs:GeographicCRS .\n")
		elif "Compound CRS" in curcrs.type_name:
			ttl.add("geoepsg:"+epsgcode+" rdf:type geocrs:CompoundCRS .\n")
			for subcrs in curcrs.sub_crs_list:
				ttl.add("geoepsg:"+epsgcode+" geocrs:includesSRS geoepsg:"+str(subcrs.to_epsg())+" .\n")
		else:
			ttl.add("geoepsg:"+epsgcode+" rdf:type geocrs:CRS .\n")
		ttl.add("geoepsg:"+epsgcode+" rdf:type prov:Entity. \n")
		ttl.add("geoepsg:"+epsgcode+" geocrs:isApplicableTo geocrsisbody:Earth .\n")
		ttl.add("geoepsg:"+epsgcode+" rdf:type owl:NamedIndividual .\n")
		ttl.add("geoepsg:"+epsgcode+" rdfs:label \""+curcrs.name.strip()+"\"@en .\n")
		ttl.add("geoepsg:"+epsgcode+" geocrs:isBound \""+str(curcrs.is_bound).lower()+"\"^^xsd:boolean . \n")
		if curcrs.coordinate_system is not None and curcrs.coordinate_system.name in coordinatesystem:
			ttl.add("geoepsg:"+epsgcode+"_cs rdf:type "+coordinatesystem[curcrs.coordinate_system.name]+" . \n")
			if len(curcrs.coordinate_system.axis_list)==2:
				ttl.add("geoepsg:"+epsgcode+"_cs rdf:type geocrs:PlanarCoordinateSystem . \n")
			elif len(curcrs.coordinate_system.axis_list)==3:
				ttl.add("geoepsg:"+epsgcode+"_cs rdf:type geocrs:3DCoordinateSystem . \n")
			ttl.add("geoepsg:"+epsgcode+"_cs rdfs:label \"EPSG:"+epsgcode+" CS: "+curcrs.coordinate_system.name+"\" . \n")
			if curcrs.coordinate_system.remarks is not None:
				ttl.add("geoepsg:"+epsgcode+"_cs rdfs:comment \""+str(curcrs.coordinate_system.remarks)+"\"@en . \n")
			if curcrs.coordinate_system.scope is not None:
				ttl.add("geoepsg:"+epsgcode+"_cs geocrs:scope \""+str(curcrs.coordinate_system.scope)+"\" . \n")
			for axis in curcrs.coordinate_system.axis_list:
				axisid=axis.name.replace(" ","_").replace("(","_").replace(")","_").replace("/","_").replace("'","_")+"_"+axis.unit_name.replace(" ","_").replace("(","_").replace(")","_").replace("/","_").replace("'","_")+"_"+axis.direction.replace(" ","_").replace("(","_").replace(")","_").replace("/","_").replace("'","_")
				ttl.add("geoepsg:"+epsgcode+"_cs geocrs:axis geocrsaxis:"+axisid+" . \n")
				ttl.add("geocrsaxis:"+axisid+" rdf:type geocrs:CoordinateSystemAxis . \n")
				ttl.add("geocrsaxis:"+axisid+" geocrs:direction geocrs:"+axis.direction+" . \n")
				ttl.add("geocrsaxis:"+axisid+" geocrs:abbreviation \""+str(axis.abbrev).replace("\"","'")+"\"^^xsd:string . \n")
				ttl.add("geocrsaxis:"+axisid+" geocrs:unit_conversion_factor \""+str(axis.unit_conversion_factor)+"\"^^xsd:double . \n")
				ttl.add("geocrsaxis:"+axisid+" geocrs:unit_auth_code \""+str(axis.unit_auth_code)+"\"^^xsd:string . \n")
				ttl.add("geocrsaxis:"+axisid+" geocrs:unit_code \""+str(axis.unit_code)+"\"^^xsd:string . \n")
				ttl.add("geocrsaxis:"+axis.direction+" rdf:type geocrs:AxisDirection . \n")
				if axis.unit_name in units:
					ttl.add("geocrsaxis:"+axisid+" geocrs:unit "+units[axis.unit_name]+" . \n")
					ttl.add("geocrsaxis:"+axisid+" rdfs:label \""+axis.name+" ("+str(units[axis.unit_name])+")\"@en . \n")
				else:
					ttl.add("geocrsaxis:"+axisid+" geocrs:unit \""+axis.unit_name+"\" . \n")
					ttl.add("geocrsaxis:"+axisid+" rdfs:label \""+axis.name+" ("+str(axis.unit_name)+")\"@en . \n")
			ttl.add("geoepsg:"+epsgcode+"_cs geocrs:asWKT \""+str(curcrs.coordinate_system.to_wkt()).replace("\"","'").replace("\n","")+"\" . \n")
			ttl.add("geoepsg:"+epsgcode+"_cs geocrs:asProjJSON \""+str(curcrs.coordinate_system.to_json()).replace("\"","'").replace("\n","")+"\" . \n")
			ttl.add("geoepsg:"+epsgcode+" geocrs:coordinateSystem geoepsg:"+epsgcode+"_cs . \n")
		elif curcrs.coordinate_system is not None:
			ttl.add("geoepsg:"+epsgcode+" geocrs:coordinateSystem \""+str(curcrs.coordinate_system)+"\"^^xsd:string . \n")
		if curcrs.source_crs is not None:
			ttl.add("geoepsg:"+epsgcode+" geocrs:sourceCRS geoepsg:"+str(curcrs.source_crs.to_epsg())+" . \n")
		if curcrs.target_crs is not None:
			ttl.add("geoepsg:"+epsgcode+" geocrs:targetCRS geoepsg:"+str(curcrs.target_crs.to_epsg())+" . \n")
		if curcrs.scope is not None:
			if "," in curcrs.scope:
				for scp in curcrs.scope.split(","):
					#print("Scope: "+scp)
					if scp.lower().strip().replace(".","") in scope:
						ttl.add("geoepsg:"+epsgcode+" geocrs:usage "+scope[scp.lower().strip().replace(".","")]+" . \n")
						ttl.add(scope[scp.lower().strip().replace(".","")]+" rdfs:subClassOf geocrs:SRSApplication . \n")
					else:
						ttl.add("geoepsg:"+epsgcode+" geocrs:usage \""+str(curcrs.datum.scope)+"\"^^xsd:string . \n")
			ttl.add("geoepsg:"+epsgcode+" geocrs:scope \""+str(curcrs.scope).replace("\"","'")+"\"^^xsd:string . \n")
		if curcrs.area_of_use is not None:
			ttl.add("geoepsg:"+epsgcode+" geocrs:area_of_use geoepsg:"+epsgcode+"_area_of_use . \n")
			ttl.add("geoepsg:"+epsgcode+"_area_of_use"+" rdf:type geocrs:AreaOfUse .\n")
			ttl.add("geoepsg:"+epsgcode+"_area_of_use"+" rdfs:label \""+str(curcrs.area_of_use.name).replace("\"","'")+"\"@en .\n")
			#b = box(curcrs.area_of_use.west, curcrs.area_of_use.south, curcrs.area_of_use.east, curcrs.area_of_use.north)
			#ttl.add("geoepsg:"+epsgcode+"_area_of_use"+" geocrs:extent   \"<http://www.opengis.net/def/crs/OGC/1.3/CRS84> "+str(b.wkt)+"\"^^geo:wktLiteral . \n")
			#\"ENVELOPE("+str(curcrs.area_of_use.west)+" "+str(curcrs.area_of_use.south)+","+str(curcrs.area_of_use.east)+" "+str(curcrs.area_of_use.north)+")\"^^geo:wktLiteral . \n")
		if curcrs.get_geod() is not None:
			geoid="geocrsgeod:"+str(geodcounter)
			if curcrs.datum.ellipsoid is not None:
				if curcrs.datum.ellipsoid.name in spheroids:
					geoid=spheroids[curcrs.datum.ellipsoid.name]
					ttl.add(geoid+" rdf:type geocrs:Ellipsoid . \n")
					ttl.add(geoid+" rdfs:label \""+curcrs.datum.ellipsoid.name+"\"@en . \n")
					ttl.add(geoid+" geocrs:approximates geocrsisbody:Earth . \n")
				elif curcrs.get_geod().sphere:
					geoid="geocrsgeod:"+str(curcrs.datum.ellipsoid.name).replace(" ","_").replace("(","_").replace(")","_")
					ttl.add(geoid+" rdf:type geocrs:Sphere . \n")
					ttl.add(geoid+" rdfs:label \""+curcrs.datum.ellipsoid.name+"\"@en . \n")
					ttl.add(geoid+" geocrs:approximates geocrsisbody:Earth . \n")
				else:
					geoid="geocrsgeod:"+str(curcrs.datum.ellipsoid.name).replace(" ","_").replace("(","_").replace(")","_")
					ttl.add(geoid+" rdf:type geocrs:Geoid . \n")
					ttl.add(geoid+" rdfs:label \""+curcrs.datum.ellipsoid.name+"\"@en . \n")
					ttl.add(geoid+" geocrs:approximates geocrsisbody:Earth . \n")
			else:
				ttl.add("geoepsg:"+epsgcode+" geocrs:ellipsoid geocrsgeod:"+str(geodcounter)+" . \n")
				ttl.add("geocrsgeod:geod"+str(geodcounter)+" rdf:type geocrs:Geoid . \n")
				ttl.add(geoid+" rdfs:label \"Geoid "+str(geodcounter)+"\"@en . \n")
				ttl.add(geoid+" geocrs:approximates geocrsisbody:Earth . \n")
			ttl.add(geoid+" skos:definition \""+str(curcrs.get_geod().initstring)+"\"^^xsd:string . \n")
			ttl.add(geoid+" geocrs:eccentricity \""+str(curcrs.get_geod().es)+"\"^^xsd:double . \n")
			ttl.add(geoid+" geocrs:isSphere \""+str(curcrs.get_geod().sphere)+"\"^^xsd:boolean . \n")
			ttl.add(geoid+" geocrs:semiMajorAxis \""+str(curcrs.get_geod().a)+"\"^^xsd:string . \n")
			ttl.add(geoid+" geocrs:semiMinorAxis \""+str(curcrs.get_geod().b)+"\"^^xsd:string . \n")
			ttl.add(geoid+" geocrs:flatteningParameter \""+str(curcrs.get_geod().f)+"\"^^xsd:double . \n")
			geodcounter+=1
		if curcrs.coordinate_operation is not None:
			coordoperationid=curcrs.coordinate_operation.name.replace(" ","_").replace("(","_").replace(")","_").replace("/","_").replace("'","_").replace(",","_").replace("&","and").strip()
			ttl.add("geoepsg:"+epsgcode+" geocrs:coordinateOperation geocrsoperation:"+str(coordoperationid)+" . \n")
			ttl.add("geocrsoperation:"+str(coordoperationid)+" geocrs:accuracy \""+str(curcrs.coordinate_operation.accuracy)+"\"^^xsd:double . \n")
			ttl.add("geocrsoperation:"+str(coordoperationid)+" geocrs:method_name \""+str(curcrs.coordinate_operation.method_name)+"\" . \n")
			ttl.add("geocrsoperation:"+str(coordoperationid)+" geocrs:asProj4 \""+str(curcrs.coordinate_operation.to_proj4()).strip().replace("\"","'").replace("\n","")+"\" . \n")
			ttl.add("geocrsoperation:"+str(coordoperationid)+" geocrs:asProjJSON \""+str(curcrs.coordinate_operation.to_json()).strip().replace("\"","'").replace("\n","")+"\" . \n")
			ttl.add("geocrsoperation:"+str(coordoperationid)+" geocrs:asWKT \""+str(curcrs.coordinate_operation.to_wkt()).replace("\"","'").replace("\n","")+"\"^^geo:wktLiteral . \n")
			if curcrs.coordinate_operation.scope is not None:
				ttl.add("geocrsoperation:"+str(coordoperationid)+" geocrs:scope \""+str(curcrs.coordinate_operation.scope).replace("\"","'")+"\"^^xsd:string . \n")
			if curcrs.coordinate_operation.remarks is not None:
				ttl.add("geocrsoperation:"+str(coordoperationid)+" rdfs:comment \""+str(curcrs.coordinate_operation.remarks).replace("\"","'").replace("\n","")+"\"^^xsd:string . \n")
			ttl.add("geocrsoperation:"+str(coordoperationid)+" geocrs:has_ballpark_transformation \""+str(curcrs.coordinate_operation.has_ballpark_transformation)+"\"^^xsd:boolean . \n")
			if curcrs.coordinate_operation.area_of_use is not None:
				ttl.add("geocrsoperation:"+str(coordoperationid)+" geocrs:area_of_use geocrsaou:"+str(coordoperationid)+"_area_of_use . \n")
				ttl.add("geocrsaou:"+str(coordoperationid)+"_area_of_use"+" rdf:type geocrs:AreaOfUse .\n")
				ttl.add("geocrsaou:"+str(coordoperationid)+"_area_of_use"+" rdfs:label \""+str(curcrs.coordinate_operation.area_of_use.name).replace("\"","'")+"\"@en .\n")
				#b = box(curcrs.coordinate_operation.area_of_use.west, curcrs.coordinate_operation.area_of_use.south, curcrs.coordinate_operation.area_of_use.east, curcrs.coordinate_operation.area_of_use.north)
				#ttl.add("geocrsaou:"+str(coordoperationid)+"_area_of_use geocrs:extent \"<http://www.opengis.net/def/crs/OGC/1.3/CRS84> "+str(b.wkt)+"\"^^geo:wktLiteral . \n")
				#ENVELOPE("+str(curcrs.coordinate_operation.area_of_use.west)+" "+str(curcrs.coordinate_operation.area_of_use.south)+","+str(curcrs.coordinate_operation.area_of_use.east)+" "+str(curcrs.coordinate_operation.area_of_use.north)+")\"^^geocrs:wktLiteral . \n")
			if curcrs.coordinate_operation.towgs84 is not None:
				print(curcrs.coordinate_operation.towgs84)
			for par in curcrs.coordinate_operation.params:
				ttl.add(" geocrs:"+str(par.name)[0].lower()+str(par.name).title().replace(" ","")[1:]+" rdf:type owl:DatatypeProperty . \n")
				ttl.add(" geocrs:"+str(par.name)[0].lower()+str(par.name).title().replace(" ","")[1:]+" rdfs:range xsd:double . \n")
				ttl.add(" geocrs:"+str(par.name)[0].lower()+str(par.name).title().replace(" ","")[1:]+" rdfs:domain geocrs:CoordinateOperation . \n")
				ttl.add(" geocrs:"+str(par.name)[0].lower()+str(par.name).title().replace(" ","")[1:]+" rdfs:label \""+str(par.name)+"\"@en . \n")
				ttl.add("geocrsoperation:"+str(coordoperationid)+" geocrs:"+str(par.name)[0].lower()+str(par.name).title().replace(" ","")[1:]+" \""+str(par.value)+"\"^^xsd:double . \n")
			for grid in curcrs.coordinate_operation.grids:
				ttl.add("geocrsoperation:"+str(coordoperationid)+" geocrs:grid geocrsgrid:"+str(grid.name).replace(" ","_")+" . \n")
				ttl.add("geocrsgrid:"+str(grid.name).replace(" ","_")+" rdf:type geocrs:Grid . \n")
				ttl.add("geocrsgrid:"+str(grid.name).replace(" ","_")+" rdfs:label \""+str(grid.full_name)+"\"@en . \n")
				ttl.add("geocrsgrid:"+str(grid.name).replace(" ","_")+" rdfs:label \""+str(grid.short_name)+"\"@en . \n")
				ttl.add("geocrsgrid:"+str(grid.name).replace(" ","_")+" geocrs:open_license \""+str(grid.open_license)+"\"^^xsd:boolean . \n")
				ttl.add("geocrsgrid:"+str(grid.name).replace(" ","_")+" rdfs:comment \""+str(grid.url)+"\"@en . \n")
			if curcrs.coordinate_operation.operations is not None:
				for operation in curcrs.coordinate_operation.operations:
					ttl.add("geocrsoperation:"+str(coordoperationid)+" geocrs:operation \""+str(operation).replace("\n","").replace("\"","'")+"\"^^xsd:string . \n")
			if curcrs.coordinate_operation.type_name==None:
				ttl.add("geocrsoperation:"+str(coordoperationid)+" rdf:type geocrs:CoordinateOperation . \n")
			elif curcrs.coordinate_operation.type_name=="Conversion":
				found=False
				if curcrs.coordinate_operation.to_proj4() is not None:
					proj4string=curcrs.coordinate_operation.to_proj4().strip().replace("\"","'").replace("\n","")
					for prj in projections:
						if prj in proj4string:
							ttl.add("geocrsoperation:"+str(coordoperationid)+" rdf:type "+projections[prj]+" . \n")
							found=True
							break
				if not found:
					ttl.add("geocrsoperation:"+str(coordoperationid)+" rdf:type geocrs:CoordinateConversionOperation . \n")
			elif curcrs.coordinate_operation.type_name=="Transformation":
				ttl.add("geocrsoperation:"+str(coordoperationid)+" rdf:type geocrs:CoordinateTransformationOperation . \n")
			elif curcrs.coordinate_operation.type_name=="Concatenated Operation":
				ttl.add("geocrsoperation:"+str(coordoperationid)+" rdf:type geocrs:CoordinateConcatenatedOperation . \n")
			elif curcrs.coordinate_operation.type_name=="Other Coordinate Operation":
				ttl.add("geocrsoperation:"+str(coordoperationid)+" rdf:type geocrs:OtherCoordinateOperation . \n")
			ttl.add("geocrsoperation:"+str(coordoperationid)+" rdfs:label \""+curcrs.coordinate_operation.name+": "+curcrs.coordinate_operation.method_name+"\"@en . \n")
		if curcrs.datum is not None:
			datumid=str(curcrs.datum.name.replace(" ","_").replace("(","_").replace(")","_").replace("/","_").replace("'","_").replace("+","_plus").replace("[","_").replace("]","_"))
			ttl.add("geoepsg:"+epsgcode+" geocrs:datum geocrsdatum:"+str(datumid)+" . \n")
			if "Geodetic Reference Frame" in curcrs.datum.type_name:
				ttl.add("geocrsdatum:"+str(datumid)+" rdf:type geocrs:GeodeticReferenceFrame . \n")
			elif "Dynamic Vertical Reference Frame" in curcrs.datum.type_name:
				ttl.add("geocrsdatum:"+str(datumid)+" rdf:type geocrs:DynamicVerticalReferenceFrame . \n")
			elif "Vertical Reference Frame" in curcrs.datum.type_name:
				ttl.add("geocrsdatum:"+str(datumid)+" rdf:type geocrs:VerticalReferenceFrame . \n")
			else:
				print(curcrs.datum.type_name)
				ttl.add("geocrsdatum:"+str(datumid)+" rdf:type geocrs:Datum . \n")
			ttl.add("geocrsdatum:"+str(datumid)+" rdfs:label \"Datum: "+curcrs.datum.name+"\"@en . \n")
			if curcrs.datum.remarks is not None:
				ttl.add("geocrsdatum:"+str(datumid)+" rdfs:comment \""+str(curcrs.datum.remarks)+"\"@en . \n")
			if curcrs.datum.scope is not None:
				ttl.add("geocrsdatum:"+str(datumid)+" geocrs:scope \""+str(curcrs.datum.scope)+"\"^^xsd:string . \n")
				if "," in curcrs.datum.scope:
					for scp in curcrs.datum.scope.split(","):
						#print("Scope: "+scp)
						if scp.lower().strip().replace(".","") in scope:
							ttl.add("geocrsdatum:"+str(datumid)+" geocrs:usage "+scope[scp.lower().strip().replace(".","")]+" . \n")
							ttl.add(scope[scp.lower().strip().replace(".","")]+" rdfs:subClassOf geocrs:SRSApplication . \n")
						else:
							ttl.add("geocrsdatum:"+str(datumid)+" geocrs:usage \""+str(curcrs.datum.scope)+"\"^^xsd:string . \n")
				print(str(curcrs.datum.scope))
			if curcrs.datum.ellipsoid is not None and curcrs.datum.ellipsoid.name in spheroids:
				ttl.add("geocrsdatum:"+str(datumid)+" geocrs:ellipse "+spheroids[curcrs.datum.ellipsoid.name]+" . \n")
				ttl.add(spheroids[curcrs.datum.ellipsoid.name]+" rdfs:label \""+str(curcrs.datum.ellipsoid.name)+"\"@en . \n")
				ttl.add(spheroids[curcrs.datum.ellipsoid.name]+" rdf:type geocrs:Ellipsoid .\n")
				ttl.add(spheroids[curcrs.datum.ellipsoid.name]+" geocrs:inverse_flattening \""+str(curcrs.datum.ellipsoid.inverse_flattening)+"\"^^xsd:double .\n")
				if curcrs.datum.ellipsoid.remarks is not None:
					ttl.add(spheroids[curcrs.datum.ellipsoid.name]+" rdfs:comment \""+str(curcrs.datum.ellipsoid.remarks)+"\"^^xsd:string .\n")
				ttl.add(spheroids[curcrs.datum.ellipsoid.name]+" geocrs:is_semi_minor_computed \""+str(curcrs.datum.ellipsoid.is_semi_minor_computed).lower()+"\"^^xsd:boolean .\n")
			elif curcrs.datum.ellipsoid is not None:
				ttl.add("geocrsdatum:"+str(datumid)+" geocrs:ellipse \""+curcrs.datum.ellipsoid.name+"\" . \n")
			if curcrs.prime_meridian is not None:
				ttl.add("geocrsdatum:"+str(datumid)+" geocrs:primeMeridian geocrsmeridian:"+curcrs.prime_meridian.name.replace(" ","")+" . \n")
				ttl.add("geocrsmeridian:"+curcrs.prime_meridian.name.replace(" ","")+" rdf:type geocrs:PrimeMeridian . \n")
				ttl.add("geocrsmeridian:"+curcrs.prime_meridian.name.replace(" ","")+" rdfs:label \""+curcrs.prime_meridian.name+"\"@en . \n")
				ttl.add("geocrsmeridian:"+curcrs.prime_meridian.name.replace(" ","")+" geocrs:longitude \""+str(curcrs.prime_meridian.longitude)+"\"^^xsd:double . \n")
				if curcrs.prime_meridian.unit_name in units:
					ttl.add("geocrsmeridian:"+curcrs.prime_meridian.name.replace(" ","")+" geocrs:unit om:"+units[curcrs.prime_meridian.unit_name]+" . \n")
					ttl.add(units[curcrs.prime_meridian.unit_name]+" rdf:type om:Unit .\n")
				else:
					ttl.add("geocrsmeridian:"+curcrs.prime_meridian.name.replace(" ","")+" geocrs:unit \""+str(curcrs.prime_meridian.unit_name)+"\" . \n")
				ttl.add("geocrsmeridian:"+curcrs.prime_meridian.name.replace(" ","")+" geocrs:asWKT \""+str(curcrs.prime_meridian.to_wkt()).replace("\"","'").replace("\n","")+"\" . \n")
				ttl.add("geocrsmeridian:"+curcrs.prime_meridian.name.replace(" ","")+" geocrs:asProjJSON \""+str(curcrs.prime_meridian.to_json()).replace("\"","'").replace("\n","")+"\" . \n")
				if curcrs.prime_meridian.remarks is not None:
					ttl.add("geocrsmeridian:"+curcrs.prime_meridian.name.replace(" ","")+" rdfs:comment \""+str(curcrs.prime_meridian.remarks)+"\"@en . \n")
				if curcrs.prime_meridian.scope is not None:
					ttl.add("geocrsmeridian:"+curcrs.prime_meridian.name.replace(" ","")+" geocrs:scope \""+str(curcrs.prime_meridian.scope)+"\"^^xsd:string . \n")
		ttl.add("geoepsg:"+epsgcode+" geocrs:isVertical \""+str(curcrs.is_vertical).lower()+"\"^^xsd:boolean . \n")
		ttl.add("geoepsg:"+epsgcode+" geocrs:isProjected \""+str(curcrs.is_projected).lower()+"\"^^xsd:boolean . \n")
		ttl.add("geoepsg:"+epsgcode+" geocrs:isGeocentric \""+str(curcrs.is_geocentric).lower()+"\"^^xsd:boolean . \n")
		ttl.add("geoepsg:"+epsgcode+" geocrs:isGeographic \""+str(curcrs.is_geographic).lower()+"\"^^xsd:boolean . \n")
		if curcrs.utm_zone is not None:
			ttl.add("geoepsg:"+epsgcode+" geocrs:utm_zone \""+str(curcrs.utm_zone)+"\"^^xsd:string . \n")
		if curcrs.to_proj4() is not None:
			ttl.add("geoepsg:"+epsgcode+" geocrs:asProj4 \""+curcrs.to_proj4().strip().replace("\"","'")+"\"^^xsd:string . \n")
		if curcrs.to_json() is not None:
			ttl.add("geoepsg:"+epsgcode+" geocrs:asProjJSON \""+curcrs.to_json().strip().replace("\"","'")+"\"^^xsd:string . \n")
		if wkt!="":
			ttl.add("geoepsg:"+epsgcode+" geocrs:asWKT \""+wkt+"\"^^geocrs:wktLiteral . \n")
		ttl.add("geoepsg:"+epsgcode+" geocrs:epsgCode \"EPSG:"+epsgcode+"\"^^xsd:string . \n")
		return ttl
