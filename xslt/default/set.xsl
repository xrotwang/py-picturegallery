<?xml version = "1.0" encoding = "UTF-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0">
  <xsl:import href="../lib.xsl"/>

  <xsl:param name="title" select="/rsp/set/title"/>
  <xsl:param name="map" select="'True'"/>
  <xsl:param name="base_uri"/>

  <xsl:attribute-set name="body">
    <xsl:attribute name="onload"><xsl:if test="$map">load('locations.xml');</xsl:if></xsl:attribute>
    <xsl:attribute name="onunload"><xsl:if test="$map">GUnload();</xsl:if></xsl:attribute>
  </xsl:attribute-set>

  <xsl:template name="main_content">
    <h2><a href="http://flickr.com/photos/{$sets_data/@user_id}/sets/{/rsp/set/@id}/"
	   title="go to set page on flickr"><xsl:value-of select="/rsp/set/title"/></a></h2>
    <p>
      <xsl:value-of select="/rsp/set/description"/>
    </p>
    <xsl:if test="$map='True'"><div id="map" class="big"/></xsl:if>
    <xsl:apply-templates/>
  </xsl:template>
  
  <xsl:template match="photo">
    <xsl:variable name="p" select="document(concat($base_uri, '/photos/', @ref, '/md.xml'))/rsp/photo"/>
    
    <div class="thumbnail">
      <a href="{$relPath}photos/{$p/@id}/Large.jpg" 
	 rel="lightbox[set]"
	 title="{$p/description/text()}">
	<img src="{$relPath}photos/{$p/@id}/Thumbnail.jpg" 
	     alt="{$p/description/text()}" />
      </a>
      <div class="description">
	<xsl:choose>
	  <xsl:when test="string-length($p/title/text())&gt;35">
	    <xsl:value-of select="concat(substring($p/title/text(),1,32),'...')"/>
	  </xsl:when>
	  <xsl:otherwise>
	    <xsl:value-of select="$p/title/text()"/>
	  </xsl:otherwise>
	</xsl:choose>
	<br/>
	<a href="{$relPath}photos/{$p/@id}/index.html" title="details">[details]</a>
      </div>
    </div>
  </xsl:template>
</xsl:stylesheet>