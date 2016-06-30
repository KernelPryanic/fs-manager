|language| |license| |coverage|

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
      FSManager.__init__(self, base_path="/some/base", mode=0o744, temporary=True)
        ...

Or you can just use it as an object

::

    from fs_manager import FSManager

    with FSManager(base_path="/tmp/base", mode=0o744, temporary=True) as fsm:
      fsm.mkdir(alias="tom", path="tom_dir", mode=0o744, temporary=True)
      fsm.cd("tom")
      fsm.mkdir("tom_dir")
      fsm.mkfile("jerry", "jerry_file", 0o644, True)
      fsm.ls()
      fsm.up()
      fsm.ls()
      fsm.rm("tom")

Save what you did

::

    from fs_manager import FSManager

    with FSManager(base_path="/tmp/base", mode=0o744, temporary=True) as fsm:
      fsm.mkdir(alias="tom", path="tom_dir", mode=0o744, temporary=True)
      fsm.cd("tom")
      fsm.mkdir("tom_dir")
      fsm.mkfile("jerry", "jerry_file", 0o644, True)
      fsm.ls()
      fsm.save_all()

    ...
    shutil.copy("/tmp/base/.fs-structure-full.json", "/tmp/another_base/.fs-structure-full.json")
    ...
    
    with FSManager(base_path="/tmp/another_base", mode=0o744, temporary=True) as fsm:
      fsm.load_all()

Structure will be saved at root to ".fs-structure-full.json". But structure
saves automatically when ``temporary=False``. So if you initialize
from the same directory, structure loads anyway.

Initialize you fs-manager from the directory on your disk

::

    from fs_manager import FSManager

    with FSManager(base_path="/tmp/base", mode=0o744, temporary=False) as fsm:
      fsm.snappy(root_binded=True)
      fsm.cd("some/path")

Thus, if ``root_binded=True`` your structure will be initialized from one root.
In other words, you'll be able to ``cd`` right from the root fs-manager object.

Also you can verify hashsum of files under any prefix like that

::

    from fs_manager import FSManager

    with FSManager(base_path="/tmp/base", mode=0o744, temporary=False) as fsm:
      fsm.snappy(root_binded=True)
      fsm.cd("some/path")
      fsm.save_hashsums("sha1")
      ...
      mismatches = fsm.check_hashsums(type="sha1", log_warnings=False)

There is much more inside :)

.. |language| image:: https://img.shields.io/badge/language-python-blue.svg
.. |license| image:: https://img.shields.io/badge/license-Apache%202-blue.svg
.. |coverage| image:: https://img.shields.io/codecov/c/github/codecov/example-python.svg?maxAge=2592000
