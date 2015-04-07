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
from rdflib.namespace import RDF, RDFS, SKOS, DCTERMS
VDM = rdflib.Namespace("http://vocabs.tenforce.com/def#")
CVNS = rdflib.Namespace("http://vocabs.tenforce.com/vdm/id/")
UBLNS = rdflib.Namespace("http://ubl/terms#")
ADMS = rdflib.Namespace("http://www.w3.org/ns/adms#")

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

    def uri(self, name):
        '''Return the URI of name.'''
        # note: put a lower() before the encode() will mean a case will 
        # be ignored in the original data sheet (or correct the data sheet).
        return self.ns.term(URIRef(hashlib.md5(name.encode()).hexdigest()))

    def text(self, text):
        '''Return an RDF Literal with the text.'''
        return Literal(text, lang="en")

    def sanitise_label(self, text):
        '''Return a sanitised label - new newlines, tabs, '|' or ',' characters'''
        str0 = text.replace("\n"," ").replace("\r"," ").replace("\t"," ")
        str1 = str0.replace("|"," ").replace(","," ")
        return str1;
        
    def split(self, values):
        '''Split a comma-separated list of values.'''
        return re.split(r"\s*,\s*", values)

    # Main methods

    def convert(self):
        '''Return the RDF Graph corresponding to the spreadsheet.'''
        g = rdflib.Graph()
        g.bind("skos", str(SKOS))
        g.bind("vdm", str(VDM))
        g.bind("cv", str(CVNS))
        g.bind("ubl", str(UBLNS))
        g.bind("adms", str(ADMS))
        self.convert_core_vocabularies(g)
        self.convert_datatypes(g)
        self.convert_target_vocab(g)
        self.convert_mapping_file(g)
        return g

    def convert_core_vocabularies(self, g):
        '''Add the contents of the 'CoreVocabularies' sheet to the graph g.'''
        for item in self.read_sheet("CoreVocabularies", ""):
            if item["type"] == "Class":
                self.cv_class(item,g)
            elif item["type"] == "Property":
                self.cv_property(item,g)
            elif item["type"] == "Association": 
                self.cv_association(item,g)
            else:
                x=1

    def cv_class(self,item,g):
        identifier = item["identifier (internal)"]
        label = item["term / label"]
        uri = self.uri(identifier)
        pubid = item["public identifier (uri)"]
        if pubid != "":
            g.add((uri, DCTERMS.identifier, URIRef(pubid)))
        g.add((uri, RDF.type, VDM.ObjectClass))
        g.add((uri, SKOS.definition, self.text(item["definition"].strip())))
        g.add((uri, DCTERMS.description, self.text(item["description"].strip())))
        g.add((uri, DCTERMS.title, self.text(self.sanitise_label(label))))
        g.add((uri, VDM.has_internalidentifier, self.text(item["identifier (internal)"])))
        g.add((uri, RDFS.label, self.text(self.sanitise_label(label))))
        datamodel = self.uri(item["data model"])
        g.add((datamodel,RDF.type, VDM.DataModel))
        g.add((datamodel,RDFS.label,self.text(item["data model"])))
        g.add((uri, DCTERMS.isPartOf, datamodel))

    def cv_property(self,item,g):
        uri = self.uri(item["identifier (internal)"])
        label = item["term / label"]
        intid = item["identifier (internal)"]
        g.add((uri, RDF.type, VDM.Property))
        # Note: The excel names can contain spaces, etc. remove them all
        # before generating the ids, etc.
        cluri = self.uri(item["class"].replace(" ",""))
        g.add((uri, ADMS.includedAsset, cluri))
        pubid = item["public identifier (uri)"]
        if pubid != "":
            g.add((uri, DCTERMS.identifier, URIRef(pubid)))
        g.add((uri, SKOS.definition, self.text(item["definition"].strip())))
        g.add((uri, ADMS.sample, self.text(item["examples"])))
        g.add((uri, DCTERMS.description, self.text(item["description"].strip())))
        if label != intid:
            label = label + " (" + intid + ")"
        g.add((uri, RDFS.label, self.text(self.sanitise_label(label))))
        g.add((uri, DCTERMS.title, self.text(self.sanitise_label(label))))
        g.add((uri, VDM.has_internalidentifier, self.text(intid)))
        datamodel = self.uri(item["data model"])
        g.add((datamodel,RDF.type, VDM.DataModel))
        g.add((datamodel, VDM.has_internalidentifier, self.text("cv")))
        g.add((datamodel,RDFS.label,self.text(item["data model"])))
        g.add((uri, DCTERMS.isPartOf, datamodel))

    def cv_association(self,item,g):
        uri = self.uri(item["identifier (internal)"])
        label = item["term / label"]
        intid = item["identifier (internal)"]
        g.add((uri, RDF.type, VDM.Property))
        cluri = self.uri(item["class"].replace(" ","")) 
        g.add((uri, ADMS.includedAsset, cluri))
        if label != intid:
            label = label + " (" + intid + ")"
        g.add((uri, RDFS.label, self.text(self.sanitise_label(label))))
        g.add((uri, DCTERMS.title, self.text(self.sanitise_label(label))))
        g.add((uri, SKOS.definition, self.text(item["definition"])))
        g.add((uri, DCTERMS.description, self.text(item["description"])))
        g.add((uri, ADMS.versionNotes, self.text(item["comments for next version"])))
        g.add((uri, RDFS.range, self.uri(item["data type"].replace(" ",""))))
        g.add((uri, VDM.has_internalidentifier, self.text(intid)))
        datamodel = self.uri(item["data model"])
        g.add((datamodel,RDF.type, VDM.DataModel))
        g.add((datamodel,RDFS.label,self.text(item["data model"])))
        g.add((datamodel, VDM.has_internalidentifier, self.text("cv")))
        g.add((uri, DCTERMS.isPartOf, datamodel))

    def convert_datatypes(self, g):
        '''Add the contents of the 'Data Types' sheet to the graph g.'''
        for item in self.read_sheet("Data Types", ""):
            if item["type"] == "Composite Type":
                self.cv_composite_type(item,g)
            elif item["type"] == "Attribute":
                self.cv_attribute(item,g)
            else:
                x=1

    def cv_composite_type(self,item,g):
        uri = self.uri(item["identifier"])
        g.add((uri, RDFS.label, self.text(item["term"])))
        g.add((uri, RDF.type, VDM.DataType))
        g.add((uri, DCTERMS.type, VDM.DataType))
        g.add((uri, DCTERMS.title, self.text(item["term"])))
        g.add((uri, DCTERMS.description, self.text(item["description"].strip())))
        g.add((uri, SKOS.definition, self.text(item["definition"])))
        g.add((uri, VDM.dataType, self.text(item["data type"])))
        g.add((uri, ADMS.sample, self.text(item["examples"])))
        g.add((uri, ADMS.versionNotes, self.text(item["comments for next version"])))

    def cv_attribute(self,item,g):
        uri = self.uri(item["identifier"])
        g.add((uri, RDF.type, VDM.DataType))
        g.add((uri, DCTERMS.type, VDM.DataType))
        g.add((uri, DCTERMS.title, self.text(item["term"])))
        g.add((uri, VDM.primitiveType, self.text(item["primitive type"])))
        g.add((uri, RDFS.label, self.text(item["term"])))
        g.add((uri, SKOS.definition, self.text(item["definition"].strip())))
        g.add((uri, DCTERMS.description, self.text(item["description"].strip())))
        g.add((uri, ADMS.versionNotes, self.text(item["comments for next version"])))

    def cv_ref(self, part, label):
        if part == "":
           return list()
        else:
           return [URIRef(hashlib.md5(part.encode()).hexdigest())]

    def cv_datamodelid(self, datamodel):
        if datamodel == "":
           return "non"
        else:
           return URIRef(hashlib.md5(datamodel.encode()).hexdigest())

    ####################################################################
    # Convert the target vocab sheet.

    def convert_target_vocab(self,g):
        '''Add the contents of the 'TargetVocabulary' sheet to the graph g.'''
        for item in self.read_sheet("TargetVocabulary", ""):
            uri = self.uri(item["mapping tool internal identifier"])
            label = item["term/label"]
            intid = item["identifier (internal)"]
            if label == "":
                label = intid
            elif label != intid:
                label = label + " (" + intid + ")"
            g.add((uri, RDFS.label, self.text(self.sanitise_label(label))))
            g.add((uri, DCTERMS.title, self.text(self.sanitise_label(label))))
            pubid = item["public identifier (uri)"]
            if pubid != "":
               g.add((uri, DCTERMS.identifier, URIRef(pubid)))
            g.add((uri, VDM.has_internalidentifier, self.text(intid)))
            datamodel = self.uri(item["data model"])
            g.add((datamodel,RDF.type, VDM.DataModel))
            g.add((datamodel,RDFS.label,self.text(item["data model"])))
            g.add((uri, DCTERMS.isPartOf, datamodel))
            g.add((uri, SKOS.definition, self.text(item["definition"])))
            g.add((uri, DCTERMS.description, self.text(item["description"].strip())))
            g.add((uri, ADMS.sample, self.text(item["examples"])))
            if item["type"] == "Class":
                self.tv_class(uri,item,g)
            elif item["type"] == "Property":
                self.tv_property(uri,item,g)
            elif item["type"] == "Association": 
                self.tv_association(item,g)
            else:
                x=1
            
    def tv_class(self,uri,item,g):
        g.add((uri, RDF.type, VDM.ObjectClass))
        g.add((uri, DCTERMS.type, VDM.ObjectClass))

    def tv_property(self,uri,item,g):
        g.add((uri, RDF.type, VDM.Property))
        cluri = self.uri(item["class"],replace(" ",""))
        g.add((uri, ADMS.includedAsset, cluri))

    def convert_mapping_file(self, g):
        '''Add the contents of the 'Mappings' sheet to the graph g.'''
        for item in self.read_sheet("Mapping", ""):
            self.cv_ubl(item,g);

    def cv_ubl(self, item, g):
        uri = self.uri(item["core vocabularies internal identifier"])
        targeturi = self.uri(item["target vocabulary internal identifier"])
        if ( item["mapping relation"].strip() != "Has no match" 
             and len(item["mapping relation"].strip()) != 0 ) :
            if len(item["target identifier"].strip()) == 0:
                sys.exit("*** Error: mapping sheet/target identifier is empty, row starting : " + item["core vocabularies internal identifier"] + " " + item["mapping relation"])
            if item["mapping relation"] == "Has exact match":
                g.add((uri,SKOS.exactMatch,targeturi))
            elif item["mapping relation"] == "Has close match":
                g.add((uri,SKOS.closeMatch,targeturi))
            elif item["mapping relation"] == "Has broad match":
                g.add((uri,SKOS.broadMatch,targeturi))
            elif item["mapping relation"] == "Has narrow match":
                g.add((uri,SKOS.narrowMatch,targeturi))
            else:
                x=1

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.description = "Convert a spreadsheet to VDM RDF."
    ap.add_argument("xlsfile", help="input XLS(X) file")
    ap.add_argument("-N", "--namespace",
                    default="http://vocabs.tenforce.com/vdm/id/cv/",
                    help="output namespace (default: %(default)s)")
    ap.add_argument("-f", "--format", default="turtle",
                    help="serialization format (default: %(default)s)")
    args = ap.parse_args()
    edoc = CommonVocabularySpreadsheet(args.xlsfile, args.namespace)
    g = edoc.convert()
    print(g.serialize(format=args.format).decode())
