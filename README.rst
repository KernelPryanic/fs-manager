|language| |license| |coverage|

fs-manager
==========

Description
~~~~~~~~~~~

This module is designed to relief and simplify interaction of your
python modules with the file system.

Installation
~~~~~~~~~~~~

``python setup.py install``

or

``pip install -e .``

or

``pip install fs-manager``

How to use
~~~~~~~~~~

For example, you can inherit your class from ``FSManager`` class

::

    from fs_manager import FSManager

    class Foo(FSManager, ...):
      FSManager.__init__(self, base_path="/some/base", mode=0o744, temporary=True, rand_prefix=True)
        ...

Or you can just use it as an object

::

    from fs_manager import FSManager

    with FSManager(base_path="/tmp/base", mode=0o744, temporary=True, rand_prefix=True) as fsm:
      fsm.mkdir(alias="tom", path="tom_dir", mode=0o744, temporary=True)
      fsm.cd("tom")
      fsm.mkdir("tom_dir")
      fsm.mkfile("jerry", "jerry_file", 0o644, True)
      fsm.ls()
      fsm.back()
      fsm.ls()
      fsm.rm("tom")

There is much more inside :)

.. |language| image:: https://img.shields.io/badge/language-python-blue.svg
.. |license| image:: https://img.shields.io/badge/license-Apache%202-blue.svg
.. |coverage| image:: https://img.shields.io/codecov/c/github/codecov/example-python.svg?maxAge=2592000
