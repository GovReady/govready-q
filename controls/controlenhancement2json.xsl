<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet version="1.1"
    xmlns:c="http://scap.nist.gov/schema/sp800-53/2.0"
    xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:xlink="http://www.w3.org/1999/xlink"
    xmlns:controls="http://scap.nist.gov/schema/sp800-53/feed/2.0"
    xmlns:xhtml="http://www.w3.org/1999/xhtml"
    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
    pub_date="2014-07-29T16:28:52.538-04:00"
    xsi:schemaLocation="http://scap.nist.gov/schema/sp800-53/feed/2.0 http://scap.nist.gov/schema/sp800-53/feed/2.0/sp800-53-feed_2.0.xsd"
    >

<!--
****************************************************************************************

Copyright: Greg Elin, 2014

This file provides a relitvely simple xslt transformation on 800-54v4 800-53-controls.xml file
to generate a set of json files representing the control enhancements as controls.

usage: $> xsltproc - -stringparam paramname paramvalue controlenhancement2json.xsl 800-53-controls.xml
example: $>  xsltproc - -stringparam controlnumber AU-3(1) lib/controlenhancement2json.xsl data/800-53-controls.xml

namespace notes: 
    It is necessary to explicitly define and use the default name space `xmlns="http://scap.nist.gov/schema/sp800-53/2.0"` 
    in the xsl file that is defined in the 800-53-controls file. 
    See: http://nvd.nist.gov/static/feeds/xml/sp80053/rev4/800-53-transform.xsl

-->

<xsl:param name="controlnumber">AC-6</xsl:param>
<xsl:strip-space elements="*"/>
<xsl:output method="text" encoding="utf-8" />

<xsl:variable name="new-line" select="'&#10;'" />
<!--xsl:variable name="new-line" select="'&#A;'" /-->
<xsl:variable name="new-line-fix" select="'\n'" />

<xsl:template name="replace-string">
    <xsl:param name="text"/>
    <xsl:param name="replace"/>
    <xsl:param name="with"/>
    <xsl:choose>
      <xsl:when test="contains($text,$replace)">
        <xsl:value-of select="substring-before($text,$replace)"/>
        <xsl:value-of select="$with"/>
        <xsl:call-template name="replace-string">
          <xsl:with-param name="text"
select="substring-after($text,$replace)"/>
          <xsl:with-param name="replace" select="$replace"/>
          <xsl:with-param name="with" select="$with"/>
        </xsl:call-template>
      </xsl:when>
      <xsl:otherwise>
        <xsl:value-of select="$text"/>
      </xsl:otherwise>
    </xsl:choose>
</xsl:template>

<xsl:template match="/">
    <xsl:apply-templates/>
</xsl:template>

<xsl:template match="controls:controls/controls:control/c:control-enhancements/c:control-enhancement">
    <xsl:if test="c:number=$controlnumber">
    <xsl:variable name="filename" select="concat( c:number, '.md' )"/>{ "id": "<xsl:value-of select='c:number'/>",
  "title": "<xsl:value-of select='c:title'/>",
  "family": "<xsl:value-of select='c:family'/>",
  "description": "<xsl:value-of select='c:statement/c:description'/>",
  "control_enhancements": "N/A",
  "supplemental_guidance": "<xsl:call-template name="replace-string">
  <xsl:with-param name="text" select='c:supplemental-guidance/c:description'/>
  <xsl:with-param name="replace" select="$new-line" />
  <xsl:with-param name="with" select="$new-line-fix"/>
</xsl:call-template>"
}
<xsl:text>
</xsl:text>
    </xsl:if>
</xsl:template>

<!-- include to stop leakage from builtin tempaltes -->
<xsl:template match='node()' mode='engine-results'/>
<xsl:template match="text()"/>

</xsl:stylesheet>