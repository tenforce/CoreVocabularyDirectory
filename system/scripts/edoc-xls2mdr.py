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

from rdflib import URIRef, Literal
from rdflib.namespace import RDF, RDFS, SKOS
MDR = rdflib.Namespace("http://mdr.semic.eu/def#")


class EDocumentSpreadsheet:

    '''The EDocumentSpreadsheet class handles a spreadsheet following the
    e-Document engineering methodology.'''

    def __init__(self, filename, namespace):
        '''Initialize a EDocumentSpreadsheet.

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
        return self.ns.term(concept + "/" + name)

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
        g.add((URIRef(self.ns), RDF.type, MDR.Context))
        self.convert_goals(g)
        self.convert_transactions(g)
        self.convert_requirements(g)
        self.convert_information(g)
        self.convert_rules(g)
        return g

    def convert_goals(self, g):
        '''Add the contents of the 'Goals' sheet to the graph g.'''
        for item in self.read_sheet("Goals", "Goal"):
            uri = self.uri("goal", item["identifier"])
            g.add((uri, RDF.type, MDR.Goal))
            g.add((uri, MDR.context, URIRef(self.ns)))
            g.add((uri, RDFS.label, self.text(item["name"])))
            g.add((uri, RDFS.comment, self.text(item["description"])))

    def convert_transactions(self, g):
        '''Add the contents of the 'Transactions' sheet to the graph g.'''
        for item in self.read_sheet("Transactions", "Transaction"):
            uri = self.uri("transaction", item["identifier"])
            g.add((uri, RDF.type, MDR.Transaction))
            g.add((uri, MDR.context, URIRef(self.ns)))
            g.add((uri, RDFS.label, self.text(item["name"])))
            g.add((uri, RDFS.comment, self.text(item["description"])))
            for goal in self.split(item["goals"]):
                g.add((uri, MDR.implements, self.uri("goal", goal)))

    def convert_requirements(self, g):
        '''Add the contents of the 'High Level Requirements' sheet to the
        graph g.'''
        for item in self.read_sheet("High Level Requirements", "Requirement"):
            uri = self.uri("requirement", item["identifier"])
            g.add((uri, RDF.type, MDR.HighLevelRequirement))
            g.add((uri, MDR.context, URIRef(self.ns)))
            g.add((uri, RDFS.label, self.text(item["name"])))
            g.add((uri, SKOS.definition, self.text(item["statement"])))
            g.add((uri, MDR.rationale, self.text(item["rationale"])))
            for goal in self.split(item["goals"]):
                g.add((uri, MDR.implements, self.uri("goal", goal)))
            g.add((uri, MDR.transaction, self.uri("transaction", item["transaction"])))

    def convert_information(self, g):
        '''Add the contents of the 'Information Requirements' sheet to the
        graph g.'''
        for item in self.read_sheet("Information Requirements", "Information Requirement"):
            uri = self.uri("ir", item["identifier"])
            g.add((uri, RDF.type, MDR.InformationRequirement))
            g.add((uri, MDR.context, URIRef(self.ns)))
            g.add((uri, RDFS.label, self.text(item["business term name"])))
            g.add((uri, SKOS.definition, self.text(item["usage"])))
            for req in self.split(item["high level requirements"]):
                g.add((uri, MDR.implements, self.uri("requirement", req)))
            g.add((uri, MDR.transaction, self.uri("transaction", item["transaction"])))

    def convert_rules(self, g):
        '''Add the contents of the 'Business Rules' sheet to the graph g.'''
        for item in self.read_sheet("Business Rules", "Business Rule"):
            uri = self.uri("br", item["identifier"])
            g.add((uri, RDF.type, MDR.BusinessRule))
            g.add((uri, MDR.context, URIRef(self.ns)))
            g.add((uri, SKOS.definition, self.text(item["rule"])))
            for dec in self.split(item["information requirements"]):
                g.add((uri, MDR.affects, self.uri("dec", dec)))
            for req in self.split(item["high level requirements"]):
                g.add((uri, MDR.implements, self.uri("requirement", req)))
            g.add((uri, MDR.transaction, self.uri("transaction", item["transaction"])))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.description = "Convert a spreadsheet to MDR RDF."
    ap.add_argument("xlsfile", help="input XLS(X) file")
    ap.add_argument("-N", "--namespace",
                    default="http://mdr.semic.eu/id/mycontext/",
                    help="output namespace (default: %(default)s)")
    ap.add_argument("-f", "--format", default="turtle",
                    help="serialization format (default: %(default)s)")
    args = ap.parse_args()
    edoc = EDocumentSpreadsheet(args.xlsfile, args.namespace)
    g = edoc.convert()
    print(g.serialize(format=args.format).decode())
