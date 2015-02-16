Pyramid
=======

Pyramid get a simple way to configure using plugins.

So, you can simply use zipkin by activate the binding as a pyramid plugin,
following the example below:


.. code-block:: ini


  [app:main]
  # ...
  pyramid.includes =
      zipkin.binding.pyramid

  # Configure the collector service of zipkin here
  zipkin.collector = zipkincollector-hostname
  # zipkin.collector.port = 9410
  # zipkin.service_name = 


* ``zipkin.collector`` configuration key is mandatory, otherwise,
the plugin stay unconfigured.

* ``zipkin.collector.port`` is the TCP port of the zipkin parameter, defaulting
to the default value of the zipkin service. So you update it if you have
tweaked the zipkin collector service.

* ``zipkin.service_name`` is the name of the service you are going to query in
your zipkin web interface or API. It defaults to the egg name of the web
application.
