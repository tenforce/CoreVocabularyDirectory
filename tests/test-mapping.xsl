<?xml version="1.0" encoding="utf-8"?>
<!--
  XSLT script to show a detailed view about a particular resource.
  This script is used in description.vsp.

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

-->
<xsl:stylesheet version="1.0"
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
  xmlns:rdfs="http://www.w3.org/2000/01/rdf-schema#"
  xmlns:dc="http://purl.org/dc/elements/1.1/"
  xmlns:dcterms="http://purl.org/dc/terms/"
  xmlns:skos="http://www.w3.org/2004/02/skos/core#"
  xmlns:vdm="http://vocabs.tenforce.com/def#"
  exclude-result-prefixes="xsl rdf rdfs dc dcterms skos">

  <xsl:param name="subject-uri"/>

  <xsl:include href="../system/xslt/about.xsl" />

	<xsl:template match="rdf:RDF">
    <xsl:call-template name="skos-properties" />
	</xsl:template>

</xsl:stylesheet>
