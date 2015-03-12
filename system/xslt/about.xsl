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
  xmlns:mdr="http://mdr.semic.eu/def#"
  exclude-result-prefixes="xsl rdf rdfs dc dcterms skos">

  <xsl:include href="file://mdr/xslt/include.xsl" />

  <!-- Entry point -->
  <xsl:template match="rdf:RDF">
    <xsl:call-template name="about" />
  </xsl:template>

  <!-- Main template -->
  <xsl:template name="content">
    <xsl:call-template name="info" />
    <xsl:call-template name="properties" />
    <xsl:call-template name="skos-properties" />
    <xsl:call-template name="inverse-properties" />
  </xsl:template>

  <!-- Print the information section -->
  <xsl:template name="info">
    <section>
      <!-- Header -->
      <h2><xsl:value-of select="$subject-label" /></h2>
      <!-- Description -->
      <xsl:for-each select="$subject/rdfs:comment | $subject/dc:description | $subject/dcterms:description | $subject/skos:definition">
        <p>
          <xsl:call-template name="rdf-value">
            <xsl:with-param name="element" select="." />
          </xsl:call-template>
        </p>
      </xsl:for-each>
      <!-- General RDF info -->
      <xsl:call-template name="rdf-info" />
    </section>
  </xsl:template>

  <!-- Print the Properties table -->
  
  <xsl:template name="properties">
    <xsl:variable name="elements" select="$subject/*[not(self::skos:exactMatch or self::skos:closeMatch or self::skos:narrowMatch)]" />
    <xsl:if test="count($elements) &gt; 0">
      <section>
        <h2>Meta-data</h2>
        <table class="results"><tbody>
          <xsl:for-each select="$elements">
						<tr>
							<td>
								<xsl:call-template name="rdf-property">
									<xsl:with-param name="element" select="." />
								</xsl:call-template>
							</td>
							<td>
								<xsl:call-template name="rdf-value">
									<xsl:with-param name="element" select="." />
									<xsl:with-param name="strip-uri" select="not(self::mdr:context)" />
								</xsl:call-template>
							</td>
						</tr>
          </xsl:for-each>
        </tbody></table>
      </section>
    </xsl:if>
  </xsl:template>

  <xsl:template name="skos-properties">
    <xsl:variable name="elements" select="//skos:exactMatch | //skos:narrowMatch | //skos:closeMatch | //skos:broadMatch " />
    <xsl:if test="count($elements) &gt; 0">
      <section>
        <h2>Mappings</h2>
        <table class="results"><tbody>
          <xsl:for-each select="$elements">
            <tr>
              <td>
                <xsl:call-template name="rdf-property">
                  <xsl:with-param name="element" select="." />
                </xsl:call-template>
              </td>
              <td>
                <xsl:call-template name="rdf-value">
                  <xsl:with-param name="element" select="." />
                </xsl:call-template>
              </td>
							<td>
                <xsl:call-template name="rdf-value">
                  <xsl:with-param name="element" select="mdr:context" />
                </xsl:call-template>
							</td>
            </tr>
          </xsl:for-each>
        </tbody></table>
      </section>
    </xsl:if>
  </xsl:template>

  <!-- Print the Inverse Properties table -->
  <xsl:template name="inverse-properties">
    <xsl:variable name="elements" select="//rdf:Description/*[@rdf:resource=$subject-uri]" />
    <xsl:if test="count($elements) &gt; 0">
      <section>
        <h2>Referenced by</h2>
        <table class="results"><tbody>
          <xsl:for-each select="$elements">
            <tr>
              <td>
                <xsl:call-template name="rdf-property">
                  <xsl:with-param name="element" select="." />
                </xsl:call-template>
              </td>
              <td>
                <xsl:call-template name="rdf-value">
                  <xsl:with-param name="element" select=".." />
                </xsl:call-template>
              </td>
							<td>
                <xsl:call-template name="rdf-value">
                  <xsl:with-param name="element" select="mdr:context" />
                </xsl:call-template>
							</td>
            </tr>
          </xsl:for-each>
        </tbody></table>
      </section>
    </xsl:if>
  </xsl:template>

</xsl:stylesheet>
<!-- vim:set ts=2 sw=2 et: -->
