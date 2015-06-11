/*
  Javascript functionalities for index.html

  Copyright 2014 European Union
  Author: Vianney le Clément de Saint-Marcq (PwC EU Services)

  Licensed under the EUPL, Version 1.1 or - as soon they
  will be approved by the European Commission - subsequent
  versions of the EUPL (the "Licence");
  You may not use this work except in compliance with the
  Licence.
  You may obtain a copy of the Licence at:
  http://ec.europa.eu/idabc/eupl

  Unless required by applicable law or agreed to in
  writing, software distributed under the Licence is
  distributed on an "AS IS" basis,
  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either
  express or implied.
  See the Licence for the specific language governing
  permissions and limitations under the Licence.
*/

// Small jQuery extension to filter and find at the same time
$.fn.filterfind = function(selector) {
  return this.filter(selector).add(this.find(selector));
};

// Perform a search
function doSearch() {
  var query = $("#query").val();
  $("#results")
    .empty()
    .append('<p class="more"><a href="/vdm/search?' +
            $.param({'q': query}) +
            '">See all results &raquo;</a></p>');
  $.get("/vdm/search", {
    'q': query,
    'limit': 10
  }, function(data) {
    $("#results").prepend($(data).filterfind("#results").contents());
  });
}

function fillExample(key, sparql) {
  var select = "#example-" + key;
  console.log("Executing query: " + sparql);
  $.get("/sparql", {
    'query': sparql,
    'default-graph-uri': "http://mapping.semic.eu/DAV",
    'format': "application/sparql-results+xml",
    'xslt-uri': "file://vdm/xslt/sparql-table.xsl"
  }, function(data) {
    $(select).prepend($(data).filterfind("#results").contents());
  });
}

$(function() {
  $("#searchform").submit(function(event) {
    doSearch();
    event.preventDefault();
  });
  fillExample('goals', 'SELECT DISTINCT ?id ?name ?description WHERE { ?id a vdm:Goal ; rdfs:label ?name ; rdfs:comment ?description } ORDER BY ?id');
  fillExample('transactions', 'SELECT DISTINCT ?id ?name ?description ?goal WHERE { ?id a vdm:Transaction ; rdfs:label ?name ; rdfs:comment ?description ; vdm:implements ?goal } ORDER BY ?id ?goal');
  fillExample('requirements', 'SELECT DISTINCT ?id ?name ?statement ?rationale ?transaction ?goal WHERE { ?id a vdm:HighLevelRequirement ; rdfs:label ?name ; skos:definition ?statement ; vdm:rationale ?rationale ; vdm:transaction ?transaction ; vdm:implements ?goal } ORDER BY ?id ?goal');
  fillExample('information', 'SELECT DISTINCT ?id ?name ?definition ?transaction ?requirement WHERE { ?id a vdm:InformationRequirement ; rdfs:label ?name ; skos:definition ?definition ; vdm:transaction ?transaction ; vdm:implements ?requirement } ORDER BY ?id');
  fillExample('rules', 'SELECT DISTINCT ?id ?rule ?transaction ?ir ?requirement WHERE { ?id a vdm:BusinessRule ; skos:definition ?rule ; vdm:transaction ?transaction ; vdm:affects ?ir ; vdm:implements ?requirement } ORDER BY ?id');
});

/* vim:set ts=2 sw=2 et: */
