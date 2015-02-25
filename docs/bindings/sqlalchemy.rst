SQLAlchemy
==========

To trace your sql request, you have to bind SQLAlchemy engine to a zipkin
endpoint.

Check the following example:

.. code-block:: python

  from zipkin.models import Endpoint
  from zipkin.binding.sqlalchemy import bind as bind_zipkin

  from sqlalchemy import create_engine
  engine = create_engine('postgresql://scott:tiger@localhost:5432/mydatabase')
  bind_zipkin(engine, Endpoint('my_database'))



Security Consideration
----------------------

This will log all the thinks, but, it is possible to hide some part
of data logged in parameters by adding a parameter 'logged_value' on
parameters value like the exemple below.


.. code-block:: python

    class SensitiveData(str):  # bytes for python 3
        def __init__(self, value):
            super(SensitiveData, self).__init__(value)
            self.logged_value = '*' * 8

    # ....

    session.query(Model).where(Model.sensitive == SensitiveData(str))



It's a duck!
~~~~~~~~~~~~

``python-zipkin`` does not create the class for you, it just check
if the parameter have the parameter. It let you decide in your code
if ``python-zipkin`` is optional or a real dependency.

