
_client = None

def init(host, port):
    global _client

    if not _client:
        socket = TSocket.TSocket(host=host, port=port)
        transport = TTransport.TFramedTransport(socket)
        protocol = TBinaryProtocol.TBinaryProtocol(trans=transport, strictRead=False, strictWrite=False)
        _client = scribe.Client(protocol)
        transport.open()


def log(trace):
    global _client

    if _client:
        messages = [base64_thrift_formatter(t, t.annotations) for t in trace.children()]
        log_entries = [scribe.LogEntry('zipkin', message) for message in messages]

        _client.Log(messages=log_entries)



