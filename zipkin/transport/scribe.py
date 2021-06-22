import pkg_resources
import thriftpy2

filename = pkg_resources.resource_filename("zipkin", "resources/scribe.thrift")
scribe_thrift = thriftpy2.load(filename, module_name="scribe_thrift")
