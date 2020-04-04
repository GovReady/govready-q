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
to generate a set of json files representing the controls.

usage: $> xsltproc - -stringparam paramname paramvalue control2json.xsl 800-53-controls.xml
example: $>  xsltproc - -stringparam controlnumber AT-3 lib/control2json.xsl data/800-53-controls.xml

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

<xsl:template match="controls:controls/controls:control">
    <xsl:if test="c:number=$controlnumber">
    <xsl:variable name="filename" select="concat( c:number, '.md' )"/>{ "id": "<xsl:value-of select='c:number'/>",
  "title": "<xsl:value-of select='c:title'/>",
  "family": "<xsl:value-of select='c:family'/>",
  "description": "<xsl:value-of select='c:statement/c:description'/>
  <xsl:for-each select='c:statement/c:statement'>\n<xsl:value-of select="translate(c:number,$controlnumber,'')"/><xsl:text> </xsl:text><xsl:value-of select='c:description'/><xsl:text></xsl:text><xsl:for-each select='c:statement'>\n<xsl:text>\t</xsl:text><xsl:value-of select="c:number"/><xsl:text> </xsl:text><xsl:value-of select="c:description"/></xsl:for-each></xsl:for-each>",
    "control_enhancements": "<xsl:for-each select='c:control-enhancements/c:control-enhancement'><xsl:value-of select="c:number"/><xsl:text> </xsl:text><xsl:value-of select='c:title'/><xsl:text>:\n</xsl:text><xsl:for-each select='c:statement'><xsl:value-of select="c:description"/></xsl:for-each><xsl:for-each select='c:supplemental-guidance'> (Supplemental-guidance: <xsl:value-of select="c:description"/>) </xsl:for-each><xsl:text>\n\n</xsl:text></xsl:for-each>",
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