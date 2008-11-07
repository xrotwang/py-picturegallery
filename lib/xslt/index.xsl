<?xml version = "1.0" encoding = "UTF-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0">
  <xsl:import href="lib.xsl"/>

  <xsl:param name="title" select="'Gallery'"/>
  <xsl:param name="subtitle" select="'Roberts Photos'"/>
  <xsl:param name="relPath" select="''"/>

  <xsl:template name="body">
    <div class="section">
      <h2><xsl:value-of select="$subtitle"/></h2>
      <p>
	Select one of the galleries linked from the menu in the sidebar.
      </p>
      <p>
	From <a href="http://www.flickr.com/photos/47285573@N00/">flickr</a>
      </p>
    </div>
  </xsl:template>

</xsl:stylesheet>