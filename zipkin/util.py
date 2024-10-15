import random
import struct
import socket

from base64 import b64encode
from thriftpy2.protocol import TBinaryProtocol
from thriftpy2.thrift import TType
from thriftpy2.protocol.binary import write_list_begin
from thriftpy2.transport import TMemoryBuffer
from thriftpy2.thrift import TDecodeException

from .zipkin import zipkincore_thrift as ttypes


def int_or_none(val):
    if val is None:
        return None

    return int(val, 16)


def hex_str(n):
    return "%0.16x" % (n,)


def uniq_id():
    """
    Create a random 64-bit signed integer appropriate
    for use as trace and span IDs.

    @returns C{int}
    """
    return random.randint(0, (2**64) - 1)


def base64_thrift(thrift_obj):
    trans = TMemoryBuffer()
    tbp = TBinaryProtocol(trans)

    thrift_obj.write(tbp)

    return b64encode(bytes(trans.getvalue())).strip()


def ipv4_to_int(ipv4):
    return struct.unpack("!i", socket.inet_aton(ipv4))[0]


def binary_annotation_formatter(annotation, host=None):
    annotation_types = {
        "string": ttypes.AnnotationType.STRING,
        "bytes": ttypes.AnnotationType.BYTES,
    }

    annotation_type = annotation_types[annotation.annotation_type]

    value = annotation.value

    if isinstance(value, str):
        value = value.encode("utf-8")

    return ttypes.BinaryAnnotation(annotation.name, value, annotation_type, host)


def base64_thrift_formatter(trace, annotations):
    thrift_annotations = []
    binary_annotations = []

    try:
        for annotation in annotations:
            host = None
            if annotation.endpoint:
                host = ttypes.Endpoint(
                    ipv4=ipv4_to_int(annotation.endpoint.ip),
                    port=annotation.endpoint.port,
                    service_name=annotation.endpoint.service_name,
                )

            if annotation.annotation_type == "timestamp":
                thrift_annotations.append(
                    ttypes.Annotation(
                        timestamp=annotation.value, value=annotation.name, host=host
                    )
                )
            else:
                binary_annotations.append(binary_annotation_formatter(annotation, host))

        thrift_trace = ttypes.Span(
            name=trace.name,
            trace_id=u64_as_i64(trace.trace_id),
            id=u64_as_i64(trace.span_id),
            parent_id=u64_as_i64(trace.parent_span_id),
            annotations=thrift_annotations,
            binary_annotations=binary_annotations,
        )

        return base64_thrift(thrift_trace)
    except TDecodeException as e:
        raise ValueError(e)


def u64_as_i64(value):
    if not value:
        return value

    try:
        data = struct.pack(">Q", value)
        data = struct.unpack(">q", data)
        return data[0]
    except struct.error as e:
        raise ValueError(e)


def span_to_bytes(thrift_span):
    """
    Returns a TBinaryProtocol encoded Thrift span.

    :param thrift_span: thrift object to encode.
    :returns: thrift object in TBinaryProtocol format bytes.
    """
    transport = TMemoryBuffer()
    protocol = TBinaryProtocol(transport)
    thrift_span.write(protocol)

    return bytes(transport.getvalue())


def base64_thrift_formatter_many(parent_trace):
    """
    Returns a TBinaryProtocol encoded list of Thrift objects.
    :param binary_thrift_obj_list: list of TBinaryProtocol objects to encode.
    :returns: bynary object representing the encoded list.
    """
    traces = list(parent_trace.children())
    transport = TMemoryBuffer()
    write_list_begin(transport, TType.STRUCT, len(traces))
    for trace in traces:
        thrift_annotations = []
        binary_annotations = []

        for annotation in trace.annotations:
            host = None
            if annotation.endpoint:
                host = ttypes.Endpoint(
                    ipv4=ipv4_to_int(annotation.endpoint.ip),
                    port=annotation.endpoint.port,
                    service_name=annotation.endpoint.service_name,
                )

            if annotation.annotation_type == "timestamp":
                thrift_annotations.append(
                    ttypes.Annotation(
                        timestamp=annotation.value, value=annotation.name, host=host
                    )
                )
            else:
                binary_annotations.append(binary_annotation_formatter(annotation, host))

        thrift_trace = ttypes.Span(
            name=trace.name,
            trace_id=u64_as_i64(trace.trace_id),
            id=u64_as_i64(trace.span_id),
            parent_id=u64_as_i64(trace.parent_span_id),
            annotations=thrift_annotations,
            binary_annotations=binary_annotations,
        )

        transport.write(span_to_bytes(thrift_trace))

    return bytes(transport.getvalue())
