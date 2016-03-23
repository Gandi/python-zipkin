import pkg_resources
import thriftpy

filename = pkg_resources.resource_filename('zipkin', 'resources/scribe.thrift')
scribe_thrift = thriftpy.load(filename, module_name='scribe_thrift')
