<?xml version = "1.0" encoding = "UTF-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0">
  <xsl:import href="../lib.xsl"/>

  <xsl:param name="title" select="'Gallery'"/>
  <xsl:param name="relPath" select="''"/>

  <xsl:template name="main_content">
    <div class="section">
      <h2><xsl:value-of select="$sets_data/@selection"/></h2>
      <p>
	Select one of the galleries linked from the menu in the sidebar.
      </p>
      <p>
	From <a href="http://www.flickr.com/photos/{$sets_data/@user_id}/">flickr</a>
      </p>
    </div>
  </xsl:template>
</xsl:stylesheet>