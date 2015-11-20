####################################################################
# Accesses the sparql endpoint, runs the query required for dumping
# the links needed (2 queries are performed at the moment).

from SPARQLWrapper import SPARQLWrapper, JSON

# First query (sparql engine expects to be running) - results:all.links

sparql = SPARQLWrapper("http://mapping.semic.eu/sparql")
sparql.setQuery(
    """
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
    prefix vdm: <http://mapping.semic.eu/def#>
    prefix dcterms: <http://purl.org/dc/terms/>
    prefix coreclass: <http://mapping.semic.eu/vdm/id/cv/class/>
    prefix adms: <http://www.w3.org/ns/adms#>
    
    SELECT DISTINCT ?datamodel ?datamodellab 
       ?coreclass ?coreclasslabel 
       ?coreproperty ?corepropertylabel 
                ?matchingprop ?matchingprop as ?label
                ?targetdatamodel ?targetdatamodellabel
		            ?target ?targetLabel 
    WHERE {
    ?datamodel rdf:type vdm:DataModel .
    ?datamodel rdfs:label ?datamodellab .
    FILTER(STR(?datamodel)="http://mapping.semic.eu/vdm/id/cv/0b0cb2485cb9429c5df6ec01d10a3dae")

    ?coreclass dcterms:isPartOf ?datamodel .
    ?coreclass rdf:type vdm:ObjectClass .
    ?coreclass rdfs:label ?coreclasslabel .

    ?coreproperty a vdm:Property .
    ?coreclass adms:includedAsset ?coreproperty.
    ?coreproperty rdfs:label ?corepropertylabel .

    { { ?coreproperty skos:exactMatch ?target }
        union
      { ?coreproperty skos:closeMatch ?target }
        union
      { ?coreproperty skos:relatedMatch ?target }
        union
      { ?coreproperty skos:broadMatch ?target }
        union
      { ?coreproperty skos:narrowMatch ?target } 
        union
      { ?target skos:broadMatch ?coreproperty }
        union 
      { ?target skos:narrowMatch ?coreproperty } }
    { { ?coreproperty ?matchingprop ?target }
      union 
      { ?target ?matchingprop ?coreproperty } }
    ?target rdfs:label ?targetLabel .
    ?target dcterms:isPartOf ?targetdatamodel .
    ?targetdatamodel rdfs:label ?targetdatamodellabel .
    } 
    """)
sparql.setReturnFormat(JSON)
results = sparql.query().convert()

f=open("all.links","w+")
for result in results["results"]["bindings"]:
    print >> f, "%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s" % (
           result["datamodel"]["value"].encode('utf-8','replace'),
           result["datamodellab"]["value"].encode('utf-8','replace'),
           result["coreclass"]["value"].encode('utf-8','replace'),
           result["coreclasslabel"]["value"].encode('utf-8','replace'),
           result["coreproperty"]["value"].encode('utf-8','replace'),
           result["corepropertylabel"]["value"].encode('utf-8','replace'),
           result["matchingprop"]["value"].encode('utf-8','replace'),
           result["matchingprop"]["value"].encode('utf-8','replace'), # as ?label
           result["targetdatamodel"]["value"].encode('utf-8','replace'),
           result["targetdatamodellabel"]["value"].encode('utf-8','replace'),
           result["target"]["value"].encode('utf-8','replace'),
           result["targetLabel"]["value"].encode('utf-8','replace'))
f.close()

#################################################################################
# Second query - results:all-dcat.links (flare.json)

sparql2 = SPARQLWrapper("http://mapping.semic.eu/sparql")
sparql2.setQuery(
    """
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
    prefix vdm: <http://mapping.semic.eu/def#>
    prefix coreclass: <http://mapping.semic.eu/vdm/id/cv/class/>

    SELECT DISTINCT ?datamodel ?datamodellab 
       ?coreclass ?coreclasslabel 
       ?coreproperty ?corepropertylabel 
       ?matchingprop ?matchingprop as ?label
       ?targetdatamodel ?targetdatamodellabel
       ?target ?targetLabel 
    WHERE {
       ?datamodel rdf:type vdm:DataModel .
       ?datamodel rdfs:label ?datamodellab .
       FILTER(STR(?datamodel)="http://mapping.semic.eu/vdm/id/cv/34884a917711536741cf1da45b7f6b41")

       ?coreclass dcterms:isPartOf ?datamodel .
       ?coreclass rdf:type vdm:ObjectClass .
       ?coreclass rdfs:label ?coreclasslabel .
       ?coreclass adms:includedAsset ?coreproperty .

       ?coreproperty a vdm:Property .
       ?coreproperty rdfs:label ?corepropertylabel .

       { { ?coreproperty skos:exactMatch ?target}
       union
       { ?coreproperty skos:closeMatch ?target }
       union
       { ?coreproperty skos:relatedMatch ?target }
       union
       { ?coreproperty skos:broaderMatch ?target }
       union
       { ?coreproperty skos:narrowerMatch ?target } }
       ?coreproperty ?matchingprop ?target .
       ?target rdfs:label ?targetLabel .

       ?target dcterms:isPartOf ?targetdatamodel .
       ?targetdatamodel rdfs:label ?targetdatamodellabel .
       FILTER(STR(?targetdatamodel)!="http://mapping.semic.eu/vdm/id/cv/0a7380a6c87798dc2d0db45ef1814630")
    }
    """)
sparql2.setReturnFormat(JSON)
results2 = sparql2.query().convert()

f2=open("all-dcat.links","w+")
for result in results2["results"]["bindings"]:
    print >> f2, "%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s" % (
           result["datamodel"]["value"].encode('utf-8','replace'),
           result["datamodellab"]["value"].encode('utf-8','replace'),
           result["coreclass"]["value"].encode('utf-8','replace'),
           result["coreclasslabel"]["value"].encode('utf-8','replace'),
           result["coreproperty"]["value"].encode('utf-8','replace'),
           result["corepropertylabel"]["value"].encode('utf-8','replace'),
           result["matchingprop"]["value"].encode('utf-8','replace'),
           result["matchingprop"]["value"].encode('utf-8','replace'), # as ?label
           result["targetdatamodel"]["value"].encode('utf-8','replace'),
           result["targetdatamodellabel"]["value"].encode('utf-8','replace'),
           result["target"]["value"].encode('utf-8','replace'),
           result["targetLabel"]["value"].encode('utf-8','replace'))
f2.close()
