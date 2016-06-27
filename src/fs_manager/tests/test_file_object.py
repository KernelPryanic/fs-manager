import traceback
import unittest
import os

from fs_manager import FileObject


class TestFileObject(unittest.TestCase):
    def test_init(self):
        try:
            fo = FileObject("test", temporary=True)
            if not os.path.exists(fo.path):
                raise Exception("File has not been initialized")
        except Exception as exc:
            traceback.print_exc()
            self.fail(exc)

    def test_init_from_precreated(self):
        try:
            with open("test", "w") as f:
                f.write("rambo test")
            perms = oct(os.stat("test").st_mode & 0o777)
            fo = FileObject("test", temporary=True)
            if oct(os.stat("test").st_mode & 0o777) != perms:
                raise Exception("Couldn't init from file")
        except Exception as exc:
            traceback.print_exc()
            self.fail(exc)

    def test_del(self):
        try:
            fo = FileObject("test", temporary=True)
            del fo
            if os.path.exists("test"):
                raise Exception("Destructor hasn't removed all files")
        except Exception as exc:
            traceback.print_exc()
            self.fail(exc)

    def test_remove(self):
        try:
            fo = FileObject("test", temporary=True)
            fo.remove()
            if os.path.exists(fo.path):
                raise Exception("File has not been removed")
        except Exception as exc:
            traceback.print_exc()
            self.fail(exc)

    def test_create(self):
        try:
            fo = FileObject("test", temporary=True)
            fo.remove()
            fo.create()
            if not os.path.exists(fo.path):
                raise Exception("File has not been created")
        except Exception as exc:
            traceback.print_exc()
            self.fail(exc)

    def test_move(self):
        try:
            fo = FileObject("test", temporary=True)
            fo.move("test_move")
            if not os.path.exists("test_move"):
                raise Exception("Failed to move")
        except Exception as exc:
            traceback.print_exc()
            self.fail(exc)

    def test_copy(self):
        try:
            fo = FileObject("test", temporary=True)
            fo_copy = fo.copy("test_copy")
            if not isinstance(fo_copy, FileObject):
                raise Exception("FileObject hasn't been returned as copy")
            if not os.path.exists("test_copy"):
                raise Exception("Failed to copy")
        except Exception as exc:
            traceback.print_exc()
            self.fail(exc)

    def test_chmod(self):
        try:
            fo = FileObject("test", temporary=True)
            fo.chmod(0o644)
            if oct(os.stat(fo.path).st_mode & 0o777) != oct(0o644):
                raise Exception("Wrong mode of file")
        except Exception as exc:
            traceback.print_exc()
            self.fail(exc)

    def test_move_chmod(self):
        try:
            fo = FileObject("test", temporary=True)
            fo.move("test_move")
            fo.chmod(0o644)
            if oct(os.stat(fo.path).st_mode & 0o777) != oct(0o644):
                raise Exception("Wrong mode of moved file")
        except Exception as exc:
            traceback.print_exc()
            self.fail(exc)

    def test_copy_chmod(self):
        try:
            fo = FileObject("test", temporary=True)
            fo_copy = fo.copy("test_copy")
            fo_copy.chmod(0o644)
            if oct(os.stat(fo_copy.path).st_mode & 0o777) != oct(0o644):
                raise Exception("Wrong mode of copied file")
        except Exception as exc:
            traceback.print_exc()
            self.fail(exc)


if __name__ == "__main__":
    unittest.main()
