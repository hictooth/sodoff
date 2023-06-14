from io import StringIO

XML_HEADER = '<?xml version="1.0" encoding="utf-8"?>'

def generate_ds_to_string(ds_object, add_xmlns=False):
  out = StringIO()
  ds_object.export(out, level=0, pretty_print=False)
  xml = out.getvalue()
  if add_xmlns:
    xml = xml.replace('xmlns:xsd=', 'xmlns="http://api.jumpstart.com/" xmlns:xsd=')
  return add_xml_header(xml)


def add_xml_header(xml):
  return '{header}{xml}'.format(header=XML_HEADER, xml=xml)