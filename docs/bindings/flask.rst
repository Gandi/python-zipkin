Flask
=====

Flask is easy to be configured using signals (signals in Flask require blinker
package to be installed).

You need a configuration with those entries:

* ``zipkin.collector`` configuration key is mandatory, otherwise,
the plugin stay unconfigured.

* ``zipkin.collector.port`` is the TCP port of the zipkin parameter, defaulting
to the default value of the zipkin service. So you update it if you have
tweaked the zipkin collector service.

* ``zipkin.service_name`` is the name of the service you are going to query in
your zipkin web interface or API. It defaults to the Flask application name.

To trace your requests, you have to bind your Flask application to a zipkin
endpoint.

Check the following example:

.. code-block:: python

  import zipkin
  from zipkin.binding.flask import bind as bind_zipkin

  endpoint = zipkin.configure('My Flask application',
                              {'zipkin.collector': 'www.remote.url',
                               'zipkin.service_name': 'My Flask application'})
  bind_zipkin(application, endpoint)
