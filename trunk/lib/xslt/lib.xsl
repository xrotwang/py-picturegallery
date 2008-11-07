<?xml version = "1.0" encoding = "UTF-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0">
  <xsl:output method="html" 
	      doctype-system="http://www.w3.org/TR/html4/loose.dtd"
	      doctype-public="-//W3C//DTD HTML 4.01 Transitional//EN"
	      encoding="utf-8" 
	      indent="yes"
	      omit-xml-declaration="yes"/>

  <xsl:param name="sidebar" select="true()"/>
  <xsl:param name="relPath" select="'../../'"/>
  <xsl:param name="lang" select="'en'"/>
  <xsl:param name="sets" select="''"/>
  <xsl:param name="sets_data" select="document($sets)/sets"/>

  <xsl:template match="/">
    <html>
      <head>
	<title><xsl:value-of select="$title"/></title>	
	<script type="text/javascript" src="{$relPath}js/prototype.js"/>
	<script type="text/javascript" src="{$relPath}js/scriptaculous.js?load=effects"/>
	<script type="text/javascript" src="{$relPath}js/lightbox.js"/>
	<link href="{$relPath}css/lightbox.css" type="text/css" rel="stylesheet"/>
	<script src="http://maps.google.com/maps?file=api&amp;v=2&amp;key=ABQIAAAAOMA8r9FfwJogWTKhmkIfxRTwM0brOpm-All5BF6PoaKBxRWWERRsB-WWaAeGx-hBoRQW01T9jZT7wg" 
		type="text/javascript"/>
	<link href="{$relPath}css/style.css" type="text/css" rel="stylesheet"/>
	<xsl:call-template name="head"/>
      </head>
      <body xsl:use-attribute-sets="body">
	<div id="topborder"></div>
	<xsl:if test="$sidebar">
	  <div id="sidebar">
	    <h1>Galleries</h1>

	    <p><a href="{$relPath}index.html">Index</a></p>
	    <ul id="nav">
	      <xsl:for-each select="$sets_data/set">
		<xsl:sort select="text()"/>
		<li>
		  <a href="{$relPath}sets/{@id}/index.html" title="{text()}">
		    <xsl:value-of select="text()"/>
		  </a>
		</li>
	      </xsl:for-each>
	    </ul>


	  </div>   
	</xsl:if> 
	<div id="content">
	  <xsl:if test="not($sidebar)">
	    <xsl:attribute name="style">width: 100%; margin: 23px 10% 5em 1em;</xsl:attribute>
	  </xsl:if>
	  <div class="section">
	    <xsl:call-template name="body"/>
	  </div>
	</div>
      </body>
    </html>
  </xsl:template>

  <xsl:attribute-set name="body"/>

  <xsl:template name="head"/>
</xsl:stylesheet>