#!/usr/bin/env python3
# Convert a spreadsheet containing goals, transactions, high level
# requirements, information requirements, and business rules, according to
# the e-Document engineering methodology, to RDF satisfying the MDR vocabulary.
#
# Copyright 2014 European Union
# Author: Vianney le Clément de Saint-Marcq (PwC EU Services)
#
# Licensed under the EUPL, Version 1.1 or - as soon they
# will be approved by the European Commission - subsequent
# versions of the EUPL (the "Licence");
# You may not use this work except in compliance with the
# Licence.
# You may obtain a copy of the Licence at:
# http://ec.europa.eu/idabc/eupl
#
# Unless required by applicable law or agreed to in
# writing, software distributed under the Licence is
# distributed on an "AS IS" basis,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either
# express or implied.
# See the Licence for the specific language governing
# permissions and limitations under the Licence.

import argparse
import sys
import re
import xlrd
import rdflib
import hashlib

from rdflib import URIRef, Literal
from rdflib.namespace import RDF, RDFS, SKOS
MDR = rdflib.Namespace("http://mdr.semic.eu/def#")
DCATNS = rdflib.Namespace("http://vocabs.tenforce.com/mdr/id/")
UBLNS = rdflib.Namespace("http://ubl/terms#")

class CommonVocabularySpreadsheet:

    '''The CommonVocabularySpreadsheet class handles a spreadsheet following the
    e-Document engineering methodology.'''

    def __init__(self, filename, namespace):
        '''Initialize a CommonVocabularySpreadsheet.

        Arguments:
        filename -- the path to the xls/xlsx file
        namespace -- the namespace of the resulting graph
        '''
        self.workbook = xlrd.open_workbook(filename)
        self.ns = rdflib.Namespace(namespace)

    # Utility methods

    def column_name(self, name, prefix):
        '''Return the normalized column name name.'''
        name = re.sub("^"+prefix.lower()+r"\s+", "", name.strip().lower())
        name = re.sub(r"^reference\s+to\s+", "", name)
        name = re.sub(r"\s+", " ", name)
        return name

    def read_sheet(self, name, prefix):
        '''Read the sheet named name and yield the rows as dictionaries indexed
        by the column name.'''
        sheet = self.workbook.sheet_by_name(name)
        header = [self.column_name(sheet.cell(0, i).value, prefix)
                  for i in range(sheet.ncols)]
        for i in range(1, sheet.nrows):
            yield {name:sheet.cell(i, j).value
                   for j, name in enumerate(header)}

    def uri(self, concept, name):
        '''Return the URI of name.'''
        return self.ns.term(concept + "/" + name.replace(":","_").replace("/","-"))

    def text(self, text):
        '''Return an RDF Literal with the text.'''
        return Literal(text, lang="en")

    def split(self, values):
        '''Split a comma-separated list of values.'''
        return re.split(r"\s*,\s*", values)

    # Main methods

    def convert(self):
        '''Return the RDF Graph corresponding to the spreadsheet.'''
        g = rdflib.Graph()
        g.bind("skos", str(SKOS))
        g.bind("mdr", str(MDR))
        g.bind("dcat", str(DCATNS))
        g.bind("ubl", str(UBLNS))
        g.add((URIRef(self.ns), RDF.type, MDR.Context))
        self.convert_dcat_vocabularies(g)
        # self.convert_datatypes(g)
        self.convert_mapping_file(g)
        return g

    def convert_dcat_vocabularies(self, g):
        '''Add the contents of the 'Core Vocabularies' sheet to the graph g.'''
        for item in self.read_sheet("Dcat Vocabularies", ""):
            if item["type"] == "Class":
                self.cv_class(item,g)
            elif item["type"] == "Property":
                self.cv_property(item,g)
            elif item["type"] == "Association": 
                self.cv_association(item,g)
            else:
                exit;

    def cv_class(self,item,g):
        uri = self.uri("class", item["identifier"])
        g.add((uri, MDR.context, URIRef(self.ns)))
        # g.add((uri, MDR.hasURI, rdflib.term.URIRef(DCATNS+item["identifier"])))
        g.add((uri, RDF.type, MDR.ObjectClass))
        g.add((uri, MDR.objectClassName, self.text(item["term"])))
        g.add((uri, RDFS.label, self.text(item["identifier"])))
        # g.add((uri, MDR.propertyTerm, self.text(item["term"])))
        # g.add((uri, RDFS.comment, self.text(item["definition"].strip())))
        g.add((uri, SKOS.definition, self.text(item["definition"].strip())))
        g.add((uri, MDR.rationale, self.text(item["description"].strip())))

    def cv_property(self,item,g):
        uri = self.uri("property", item["identifier"])
        g.add((uri, MDR.context, URIRef(self.ns)))
        g.add((uri, RDF.type, MDR.Property))
        g.add((uri, RDFS.label, self.text(item["identifier"])))
        g.add((uri, MDR.objectClass, self.uri("class",item["class"].replace(" ",""))))
        g.add((uri, MDR.property, self.uri("class",item["data type"].replace(" ",""))))
        g.add((uri, MDR.representation, RDFS.Literal))
        g.add((uri, MDR.propertyTerm, self.text(item["term"])))
        g.add((uri, MDR.hasXMLNamespace, self.text(item["vocab"])))
        g.add((uri, MDR.minCardinality, self.text(item["cardinality"].split("..")[0])))
        g.add((uri, MDR.maxCardinality, self.text(item["cardinality"].split("..")[1])))
        # g.add((uri, RDFS.comment, self.text(item["definition"])))
        g.add((uri, SKOS.definition, self.text(item["definition"].strip())))
        g.add((uri, RDFS.comment, self.text(item["usage recommendation"].strip())))
        g.add((uri, MDR.rationale, self.text(item["description"].strip())))
        g.add((uri, MDR.example, self.text(item["examples"])))
        g.add((uri, SKOS.editorialNote, self.text(item["comments for next version"])))

    def cv_association(self,item,g):
        uri = self.uri("property", item["identifier"])
        g.add((uri, RDFS.label, self.text(item["identifier"])))
        g.add((uri, MDR.context, URIRef(self.ns)))
        g.add((uri, MDR.property, self.uri("class",item["data type"].replace(" ",""))))
        g.add((uri, RDF.type, MDR.Property))
        g.add((uri, MDR.objectClass, self.uri("class",item["class"].replace(" ",""))))
        g.add((uri, MDR.propertyTerm, self.text(item["term"])))
        g.add((uri, RDFS.comment, self.text(item["usage recommendation"].strip())))
        g.add((uri, RDFS.comment, self.text(item["definition"])))
        g.add((uri, MDR.rationale, self.text(item["description"].strip())))

    def cv_composite_type(self,item,g):
        uri = self.uri("datatype", item["identifier"])
        g.add((uri, MDR.context, URIRef(self.ns)))
        # g.add((uri, MDR.hasURI, rdflib.term.URIRef(DCATNS+item["identifier"])))
        g.add((uri, RDF.type, MDR.DataType))
        g.add((uri, MDR.representationTerm, self.text(item["primitive type"])))
        g.add((uri, MDR.propertyTerm, self.text(item["term"])))
        g.add((uri, RDFS.comment, self.text(item["definition"])))
        g.add((uri, MDR.rationale, self.text(item["description"].strip())))

    def cv_attribute(self,item,g):
        uri = self.uri("datatype", item["identifier"])
        g.add((uri, MDR.context, URIRef(self.ns)))
        # g.add((uri, MDR.hasURI, rdflib.term.URIRef(DCATNS+item["identifier"])))
        g.add((uri, RDF.type, MDR.DataType))
        g.add((uri, MDR.propertyTerm, self.text(item["term"])))
        g.add((uri, MDR.representation, self.uri("datatype",item["data type"].replace(" ",""))))
        g.add((uri, RDFS.comment, self.text(item["definition"])))
        g.add((uri, MDR.rationale, self.text(item["description"].strip())))

    def convert_datatypes(self, g):
        '''Add the contents of the 'Data Types' sheet to the graph g.'''
        for item in self.read_sheet("Data Types", ""):
            if item["type"] == "Composite Type":
                self.cv_composite_type(item,g)
            elif item["type"] == "Attribute":
                self.cv_attribute(item,g)
            else:
                exit;

    def cv_ref(self, part, label):
        if part.strip() == "":
           return list()
        else:
           return [URIRef(hashlib.md5(part.strip().encode()).hexdigest())]

    def cv_datamodelid(self, datamodel):
        if datamodel == "":
           return "non"
        else:
           return URIRef(hashlib.md5(datamodel.encode()).hexdigest())

#        match = re.search(r'http://*',part)
#        named = re.search(r'rdfs:*',part)
#        en = re.search(r'EN:*',label)
#        if match:
#           return [URIRef(part.strip())]
#        if named:
#           return [URIRef(hashlib.md5(part.encode()).hexdigest())]
#        elif en:
#            return [URIRef(hashlib.md5(part.encode()).hexdigest())]
#        elif part == "":
#           return list()
#        elif (label != "") & (len(part.strip().split(".")) != 0):
#           return [URIRef(label.replace(" ","").strip())]
#        else:
#            return [self.uri("class", name) for name in part.replace(" ","").split(".")]

    def cv_ubl(self, item, g):
        uri = self.uri("property", item["dcat vocabulary identifier"].replace(" ",""))
        if item["mapping relation"] != "Has no match":
            for ubluri in self.cv_ref(item["identifier"],item["label"]):
               datamodel= self.cv_datamodelid(item["data model"])
               g.add((datamodel, RDF.type, MDR.Context))
               g.add((datamodel, RDFS.label, self.text(item["data model"])))
               g.add((ubluri, MDR.context, datamodel))
               # g.add((ubluri, MDR.hasURI, rdflib.term.URIRef(UBLNS+item["identifier"])))
               g.add((ubluri, RDF.type, MDR.Property))
               g.add((ubluri, RDFS.label, self.text(item["identifier"])))
#              g.add((ubluri, RDFS.comment, self.text(item["label"])))
               g.add((ubluri, RDFS.label, self.text(item["identifier"])))
               g.add((ubluri, RDFS.seeAlso, self.text(item["mapping code url"])))
               g.add((ubluri, SKOS.editorialNote, self.text(item["mapping comment"])))
               g.add((ubluri, MDR.propertyTerm, self.text(item["label"])))
               g.add((ubluri, SKOS.definition, self.text(item["definition"].strip())))
#              g.add((ubluri, RDFS.comment, self.text(item["definition"].strip())))
               g.add((ubluri, MDR.rationale, self.text(item["mapping comment"].strip())))
               if item["mapping relation"].strip() == "exactMatch":
                  g.add((uri,SKOS.exactMatch,ubluri))
               elif item["mapping relation"] == "Has close match":
                  g.add((uri,SKOS.closeMatch,ubluri))
               elif item["mapping relation"] == "Has broard match":
                  g.add((uri,SKOS.broadMatch,ubluri))
               elif item["mapping relation"] == "Has narrow match":
                  g.add((uri,SKOS.narrowMatch,ubluri))
               else:
                  exit;

    def convert_mapping_file(self, g):
        '''Add the contents of the 'Mappings' sheet to the graph g.'''
        for item in self.read_sheet("ODS Mappings", ""):
            self.cv_ubl(item,g);

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.description = "Convert a spreadsheet to MDR RDF."
    ap.add_argument("xlsfile", help="input XLS(X) file")
    ap.add_argument("-N", "--namespace",
                    default="http://vocabs.tenforce.com/mdr/id/dcat/",
                    help="output namespace (default: %(default)s)")
    ap.add_argument("-f", "--format", default="turtle",
                    help="serialization format (default: %(default)s)")
    args = ap.parse_args()
    edoc = CommonVocabularySpreadsheet(args.xlsfile, args.namespace)
    g = edoc.convert()
    print(g.serialize(format=args.format).decode())
