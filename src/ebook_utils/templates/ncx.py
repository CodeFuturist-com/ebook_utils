content="""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE ncx PUBLIC "-//NISO//DTD ncx 2005-1//EN"
   "http://www.daisy.org/z3986/2005/ncx-2005-1.dtd">
<ncx xmlns="http://www.daisy.org/z3986/2005/ncx/" version="2005-1">
  <head>
    <meta name="dtb:uid" content="{0}"/>
    <meta name="dtb:depth" content="1" />
    <meta name="dtb:totalPageCount" content="0" />
    <meta name="dtb:maxPageNumber" content="0" />
  </head>
  <docTitle>
    <text>{1}</text>
  </docTitle>
  <navMap>
    <navPoint id="navPoint-1" playOrder="1">
      <navLabel>
        <text>{1}</text>
      </navLabel>
      <content src="Text/frontpage.xhtml" />
    </navPoint>
    <navPoint id="navPoint-2" playOrder="2">
      <navLabel>
        <text>Table of Contents</text>
      </navLabel>
      <content src="Text/contents.xhtml" />
    </navPoint>
    {2}
  </navMap>
</ncx>"""
