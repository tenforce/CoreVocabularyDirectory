from SPARQLWrapper import SPARQLWrapper, JSON

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
