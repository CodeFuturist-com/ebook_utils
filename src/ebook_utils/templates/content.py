content = """<?xml version="1.0" encoding="utf-8"?>
<package xmlns="http://www.idpf.org/2007/opf" unique-identifier="ISBN" version="2.0">
  <metadata xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:opf="http://www.idpf.org/2007/opf">
    <dc:identifier id="ISBN" opf:scheme="ISBN">{0}</dc:identifier>
    <dc:title>{1}</dc:title>
    <dc:language>en</dc:language>
    <dc:creator>{2}</dc:creator>
    <dc:publisher>{3}</dc:publisher>
  </metadata>
  <manifest>
    <item id="ncx" href="toc.ncx" media-type="application/x-dtbncx+xml" />
    {4}
  </manifest>
  <spine toc="ncx">
    {5}
  </spine>
  <guide>
    <reference type="toc" title="Table of Contents" href="Text/part0001.xhtml" />
  </guide>
</package>"""
