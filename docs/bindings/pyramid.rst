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

