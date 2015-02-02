import random
import struct
import socket

from thrift.protocol import TBinaryProtocol
from thrift.transport import TTransport

from ._thrift.zipkinCore import ttypes


def hex_str(n):
    return '%0.16x' % (n,)

def uniq_id():
    """
    Create a random 64-bit signed integer appropriate
    for use as trace and span IDs.

    XXX: By experimentation zipkin has trouble recording traces with ids
    larger than (2 ** 56) - 1

    @returns C{int}
    """
    return random.randint(0, (2 ** 56) - 1)

def base64_thrift(thrift_obj):
    trans = TTransport.TMemoryBuffer()
    tbp = TBinaryProtocol.TBinaryProtocol(trans)

    thrift_obj.write(tbp)

    return trans.getvalue().encode('base64').strip()

def ipv4_to_int(ipv4):
    return struct.unpack('!i', socket.inet_aton(ipv4))[0]



def binary_annotation_formatter(annotation, host=None):
    annotation_types = {
        'string': ttypes.AnnotationType.STRING,
        'bytes': ttypes.AnnotationType.BYTES,
    }

    annotation_type = annotation_types[annotation.annotation_type]

    value = annotation.value

    if isinstance(value, unicode):
        value = value.encode('utf-8')

    return ttypes.BinaryAnnotation(
        annotation.name,
        value,
        annotation_type,
        host)


def base64_thrift_formatter(trace, annotations):
    thrift_annotations = []
    binary_annotations = []

    for annotation in annotations:
        host = None
        if annotation.endpoint:
            host = ttypes.Endpoint(
                ipv4=ipv4_to_int(annotation.endpoint.ip),
                port=annotation.endpoint.port,
                service_name=annotation.endpoint.service_name)

        if annotation.annotation_type == 'timestamp':
            thrift_annotations.append(ttypes.Annotation(
                timestamp=annotation.value,
                value=annotation.name,
                host=host))
        else:
            binary_annotations.append(
                binary_annotation_formatter(annotation, host))

    thrift_trace = ttypes.Span(
        trace_id=trace.trace_id,
        name=trace.name,
        id=trace.span_id,
        parent_id=trace.parent_span_id,
        annotations=thrift_annotations,
        binary_annotations=binary_annotations
    )

    return base64_thrift(thrift_trace)
