import pkg_resources
import thriftpy

filename = pkg_resources.resource_filename('zipkin',
                                           'resources/zipkinCore.thrift')
zipkincore_thrift = thriftpy.load(filename, module_name='zipkincore_thrift')
