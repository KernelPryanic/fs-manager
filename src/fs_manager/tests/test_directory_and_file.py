import traceback
import unittest

from fs_manager import FileObject
from fs_manager import DirectoryObject


class TestDirectoryAndFile(unittest.TestCase):
    def test_index_file(self):
        try:
            fo = FileObject("test_file", temporary=True)
            do = DirectoryObject("test_dir", temporary=True)
            fo.parent = do
            if do.index(fo) is None:
                raise Exception("Parent hasn't been set")
        except Exception as exc:
            traceback.print_exc()
            self.fail(exc)

    def test_index_dir(self):
        try:
            do1 = DirectoryObject("test_dir1", temporary=True)
            do2 = DirectoryObject("test_dir2", temporary=True)
            do1.parent = do2
            if do2.index(do1) is None:
                raise Exception("Parent hasn't been set")
        except Exception as exc:
            traceback.print_exc()
            self.fail(exc)

    def test_index_file_path(self):
        try:
            fo = FileObject("test_file", temporary=True)
            do = DirectoryObject("test_dir", temporary=True)
            fo.parent = do
            if do.index(path=fo.path) is None:
                raise Exception("Parent hasn't been set")
        except Exception as exc:
            traceback.print_exc()
            self.fail(exc)

    def test_index_dir_path(self):
        try:
            do1 = DirectoryObject("test_dir1", temporary=True)
            do2 = DirectoryObject("test_dir2", temporary=True)
            do1.parent = do2
            if do2.index(path=do1.path) is None:
                raise Exception("Parent hasn't been set")
        except Exception as exc:
            traceback.print_exc()
            self.fail(exc)

    def test_unparent_file(self):
        try:
            fo = FileObject("test_file", temporary=True)
            do = DirectoryObject("test_dir", temporary=True)
            fo.parent = do
            fo.unparent()
            if fo.parent == do or do.index(fo) is not None:
                raise Exception("Parent hasn't been unset")
        except Exception as exc:
            traceback.print_exc()
            self.fail(exc)

    def test_unparent_dir(self):
        try:
            do1 = DirectoryObject("test_dir1", temporary=True)
            do2 = DirectoryObject("test_dir2", temporary=True)
            do1.parent = do2
            do1.unparent()
            if do1.parent == do2 or do2.index(do1) is not None:
                raise Exception("Parent hasn't been unset")
        except Exception as exc:
            traceback.print_exc()
            self.fail(exc)

    def test_append_file(self):
        try:
            fo = FileObject("test_file", temporary=True)
            do = DirectoryObject("test_dir", temporary=True)
            do.append(fo)
            if fo.parent != do or do.index(fo) is None:
                raise Exception("Parent hasn't been set")
        except Exception as exc:
            traceback.print_exc()
            self.fail(exc)

    def test_append_dir(self):
        try:
            do1 = DirectoryObject("test_dir1", temporary=True)
            do2 = DirectoryObject("test_dir2", temporary=True)
            do2.append(do1)
            if do1.parent != do2 or do2.index(do1) is None:
                raise Exception("Parent hasn't been set")
        except Exception as exc:
            traceback.print_exc()
            self.fail(exc)

    def test_insert_file(self):
        try:
            fo = FileObject("test_file", temporary=True)
            do = DirectoryObject("test_dir", temporary=True)
            do.insert(0, fo)
            if fo.parent != do or do.index(fo) is None:
                raise Exception("Parent hasn't been set")
        except Exception as exc:
            traceback.print_exc()
            self.fail(exc)

    def test_insert_dir(self):
        try:
            do1 = DirectoryObject("test_dir1", temporary=True)
            do2 = DirectoryObject("test_dir2", temporary=True)
            do2.insert(0, do1)
            if do1.parent != do2 or do2.index(do1) is None:
                raise Exception("Parent hasn't been set")
        except Exception as exc:
            traceback.print_exc()
            self.fail(exc)

    def test_pop_file(self):
        try:
            fo = FileObject("test_file", temporary=True)
            do = DirectoryObject("test_dir", temporary=True)
            do.append(fo)
            poped = do.pop(0)
            if not isinstance(poped, FileObject) and \
                    not isinstance(poped, DirectoryObject):
                raise Exception("FileObject/DirectoryObject hasn't "
                                "been returned as copy")
            if fo.parent == do or do.index(fo) is not None:
                raise Exception("Parent hasn't been unset")
        except Exception as exc:
            traceback.print_exc()
            self.fail(exc)

    def test_pop_dir(self):
        try:
            do1 = DirectoryObject("test_dir1", temporary=True)
            do2 = DirectoryObject("test_dir2", temporary=True)
            do2.append(do1)
            poped = do2.pop(0)
            if not isinstance(poped, FileObject) and \
                    not isinstance(poped, DirectoryObject):
                raise Exception("FileObject/DirectoryObject hasn't "
                                "been returned as copy")
            if do1.parent == do2 or do2.index(do1) is not None:
                raise Exception("Parent hasn't been unset")
        except Exception as exc:
            traceback.print_exc()
            self.fail(exc)


if __name__ == "__main__":
    unittest.main()
