Getting Started
===============

Installation
------------

You may use a virtualenv and pip

::

  pip install python-zipkin


Usage
-----

You need to configure it in your project, like this:


.. code-block:: python

  import zipkin

  config = {
      'zipkin.collector': 'my-collector.hostname',
      # 'zipkin.collector.port': 9410,  # not mandatory, default value
  }
  zipkin.configure('name', config)


Currently, there is binding for few libraries you may use, so you can easily
trace without any configuration.
There is some way to integrate zipkin in your web framework.

Fill free to add support of what is missing by pull request!
