<?xml version = "1.0" encoding = "UTF-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0">
  <xsl:import href="../lib.xsl"/>
  <xsl:import href="../lang.xsl"/>

  <xsl:param name="title" select="//photo/title/text()"/>

  <xsl:template name="head_content">
    <script src="../../js/photonotes.js" type="text/javascript"/>
    <link href="../../css/photonotes.css" rel="stylesheet" type="text/css" />
  </xsl:template>

  <xsl:template name="main_content">
    <xsl:apply-templates/>
  </xsl:template>
  
  <xsl:template match="photo">
    <h2><a href="http://flickr.com/photos/{$sets_data/@user_id}/{@id}/"
	   title="go to photo page on flickr"><xsl:value-of select="title/text()"/></a></h2>
    <div class="fn-container" id="PhotoContainer">
      <img src="Large.jpg"/>
    </div>
    <script type="text/javascript">
      <xsl:text>
var notes = new PhotoNoteContainer(document.getElementById('PhotoContainer'));
var note;
var size;
      </xsl:text>
      <xsl:for-each select="notes/note">
size = new PhotoNoteRect(2*<xsl:value-of select="@x"/>,2*<xsl:value-of select="@y"/>,2*<xsl:value-of select="@w"/>,2*<xsl:value-of select="@h"/>);  //r.left,r.top,r.width,r.height
note = new PhotoNote('<xsl:value-of select="text()"/>',<xsl:value-of select="position()"/>, size);
note.onsave = function (note) { return 1; };
note.ondelete = function (note) { return true; };
notes.AddNote(note);
      </xsl:for-each>
    </script>
    <p>
      <xsl:value-of select="description/text()"/>
    </p>
    <xsl:for-each select="//location">
      <h3><xsl:value-of select="$location"/>:</h3>
      <p>
	<a href="http://maps.google.com/?ll={@latitude},{@longitude}&amp;t=h&amp;z=13">open in Google maps</a>
      </p>
      <div id="map" class="small"/>
      <dl>
	<dt><xsl:value-of select="$latitude"/></dt><dd><xsl:value-of select="@latitude"/></dd>
	<dt><xsl:value-of select="$longitude"/></dt><dd><xsl:value-of select="@longitude"/></dd>
	<dt><xsl:value-of select="$locality"/></dt><dd><xsl:value-of select="locality/text()"/></dd>
	<dt><xsl:value-of select="$county"/></dt><dd><xsl:value-of select="county/text()"/></dd>
	<dt><xsl:value-of select="$region"/></dt><dd><xsl:value-of select="region/text()"/></dd>
	<dt><xsl:value-of select="$country"/></dt><dd><xsl:value-of select="country/text()"/></dd>
      </dl>
      <script type="text/javascript">
  if (GBrowserIsCompatible()) {
    var map = new GMap2(document.getElementById("map"));

    map.addControl(new GSmallMapControl());
    map.addControl(new GMapTypeControl());
    map.setCenter(new GLatLng(12,0), 3, G_HYBRID_MAP);
    
    var bounds = new GLatLngBounds();
    var point = new GLatLng(<xsl:value-of select="@latitude"/>, <xsl:value-of select="@longitude"/>);
    bounds.extend(point);
    var marker = new GMarker(point);
    map.addOverlay(marker);

    map.setCenter(bounds.getCenter());
    map.setZoom(Math.min(12, map.getBoundsZoomLevel(bounds)-1));
  }
      </script>
    </xsl:for-each>
    <h3><xsl:value-of select="$tags"/>:</h3>
    <ul id="tags">
      <xsl:for-each select="//tag">
	<li>
	  <a href="http://www.flickr.com/photos/{$user_name}/tags/{text()}/"
	     title="see photos tagged with on flickr">
	    <xsl:value-of select="@raw"/>
	  </a>
	</li>
      </xsl:for-each>
    </ul>
    <h3><xsl:value-of select="$image_sizes"/>:</h3>
    <ul id="sizes">
      <li><a href="Thumbnail.jpg" title="Thumbnail">Thumbnail</a></li>
      <li><a href="Square.jpg" title="Square">Square</a></li>
      <li><a href="Small.jpg" title="Small">Small</a></li>
      <li><a href="Medium.jpg" title="Medium">Medium</a></li>
      <li><a href="Original.jpg" title="Original">Original</a></li>
    </ul>
  </xsl:template>
</xsl:stylesheet>