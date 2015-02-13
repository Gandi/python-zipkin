SQLAlchemy
==========

To trace your sql request, you have to bing SQLAlchemy engine to a zipkin
endpoint.

Check the follosing exemple:

.. code-block:: python

  from zipkin.models import Endpoint
  from zipkin.binding.sqlalchemy import bind as bind_zipkin

  from sqlalchemy import create_engine
  engine = create_engine('postgresql://scott:tiger@localhost:5432/mydatabase')
  bind_zipkin(engine, Endpoint('my_database'))

