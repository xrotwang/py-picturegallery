<?xml version = "1.0" encoding = "UTF-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0">
  <xsl:param name="location">
    <xsl:choose>
      <xsl:when test="$lang='de'">Lage</xsl:when>
      <xsl:otherwise>location</xsl:otherwise>
    </xsl:choose>
  </xsl:param>
  <xsl:param name="latitude">
    <xsl:choose>
      <xsl:when test="$lang='de'">Breite</xsl:when>
      <xsl:otherwise>latitude</xsl:otherwise>
    </xsl:choose>
  </xsl:param>
  <xsl:param name="longitude">
    <xsl:choose>
      <xsl:when test="$lang='de'">Laenge</xsl:when>
      <xsl:otherwise>longitude</xsl:otherwise>
    </xsl:choose>
  </xsl:param>
  <xsl:param name="locality">
    <xsl:choose>
      <xsl:when test="$lang='de'">Ort</xsl:when>
      <xsl:otherwise>locality</xsl:otherwise>
    </xsl:choose>
  </xsl:param>
  <xsl:param name="county">
    <xsl:choose>
      <xsl:when test="$lang='de'">Gemeinde</xsl:when>
      <xsl:otherwise>county</xsl:otherwise>
    </xsl:choose>
  </xsl:param>
  <xsl:param name="region">
    <xsl:choose>
      <xsl:when test="$lang='de'">Region</xsl:when>
      <xsl:otherwise>region</xsl:otherwise>
    </xsl:choose>
  </xsl:param>
  <xsl:param name="country">
    <xsl:choose>
      <xsl:when test="$lang='de'">Land</xsl:when>
      <xsl:otherwise>country</xsl:otherwise>
    </xsl:choose>
  </xsl:param>
  <xsl:param name="tags">
    <xsl:choose>
      <xsl:when test="$lang='de'">Schlagworte</xsl:when>
      <xsl:otherwise>Tags</xsl:otherwise>
    </xsl:choose>
  </xsl:param>
  <xsl:param name="image_sizes">
    <xsl:choose>
      <xsl:when test="$lang='de'">Andere Bildgroessen</xsl:when>
      <xsl:otherwise>Other image sizes</xsl:otherwise>
    </xsl:choose>
  </xsl:param>
</xsl:stylesheet>