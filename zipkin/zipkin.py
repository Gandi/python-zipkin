import pkg_resources
import thriftpy2

filename = pkg_resources.resource_filename("zipkin", "resources/zipkinCore.thrift")
zipkincore_thrift = thriftpy2.load(filename, module_name="zipkincore_thrift")
