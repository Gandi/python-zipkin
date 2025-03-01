0.9.3 - Released on 2024-10-15
------------------------------
* Update depenencies 

Changelog
=========

0.9.3  (2024-09-25)
-------------------
- Don't update the log factory, user must install it manually.

0.9.2  (2024-09-24)
-------------------
- Remove python2.7 support.
- Migrate packaging to poetry.

0.9.1  (2024-09-24)
-------------------
- Remove python2.6 support.
- Add trace_id and span_id in the python logging context.

0.8.4  (2021-07-21)
-------------------

- Fix django issue on missing trace.

0.8.3  (2021-06-28)
-------------------

- Fix issue for django on slow request logs. The reset of the stack must
  be done on every requests.

0.8.2  (2021-06-28)
-------------------

- Ensure we never raise an exception if we cannot collect a trace,
  avoid side effect to clients.

0.8.1  (2021-06-25)
-------------------

- Hotfix Pyramid slow query logger that does not cleanup the trace stack.


0.8.0  (2021-06-25)
-------------------

- Rewrite Pyramid binding.
- Add settings for pyramid to log slow queries only with a configurable time.
- Add a setting to list what library should be traced.
- Make socket timout configurable and change default timeout to 1 second.

0.7.2  (2021-06-22)
-------------------

- Make the scribe async/sync socket configurable
- Add a middleware/setting for Django to track only slow query

0.7.1  (2021-06-22)
-------------------

- Add a Trace context manager for more flexibility
- Add django support using a django middleware and app.
- Add psycopg2 cursor support to trace sql query
- Add an http client (synchronous) to push trace, client transport is
  configurable.

0.6.10 (2020-01-28)
-------------------

- update logging level to avoid errors logs for SQL query outside http context
- remove deprecated log.warn

0.6.9 (2019-09-26)
------------------

- requests: fixup infinite recursion

0.6.8 (2019-09-23)
------------------

- pyramid: fixup tests if zipkin not configured

0.6.7 (2019-09-23)
------------------

- pyramid: fixup tweenview init

0.6.6 (2019-09-23)
------------------

- pyramid: register trace in a tweenview

0.6.5 (2019-09-17)
------------------

- advertise version in pyramid module

0.6.4 (2019-09-18)
------------------

- do not throw exception when trying to format to thrift

0.6.3 (2019-09-18)
------------------

- ensure zipkin does not raise when trace id is larger than expected

0.6.2 (2019-09-17)
------------------

- do not throw warning on configuration mistakes

0.6.1 (2019-09-17)
------------------

- fixup python2 support

0.6.0 (2019-09-17)
------------------

- refactor pyramid plugin
- fix reporter

0.5 (2019-09-10)
----------------

- Use thriftpy2

0.4 (2015-08-21)
----------------

-  Flask bindings
-  xmlrpclib client bindings
-  Filtered parameters in sqlalchemy binding
-  Implement exponential backoff on connection


0.3 (2015-02-16)
----------------

-  Make the service name configurable for pyramid application


0.2 (2015-02-16)
----------------

-  Keep @trace usable when zipkin is not configured


0.1 (2015-02-16)
----------------

-  Initial version
