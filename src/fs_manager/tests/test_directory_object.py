import traceback
import unittest
import os

from fs_manager import DirectoryObject


class TestDirectoryObject(unittest.TestCase):
    def test_init(self):
        try:
            do = DirectoryObject("test", temporary=True)
            if not os.path.exists(do.path):
                raise Exception("Directory has not been initialized")
        except Exception as exc:
            traceback.print_exc()
            self.fail(exc)

    def test_init_from_precreated(self):
        try:
            os.mkdir("test")
            perms = oct(os.stat("test").st_mode & 0o777)
            do = DirectoryObject("test", temporary=True)
            if oct(os.stat("test").st_mode & 0o777) != perms:
                raise Exception("Couldn't init from directory")
        except Exception as exc:
            traceback.print_exc()
            self.fail(exc)

    def test_del(self):
        try:
            do = DirectoryObject("test", temporary=True)
            del do
            if os.path.exists("test"):
                raise Exception("Destructor hasn't removed all directories")
        except Exception as exc:
            traceback.print_exc()
            self.fail(exc)

    def test_remove(self):
        try:
            do = DirectoryObject("test", temporary=True)
            do.remove()
            if os.path.exists(do.path):
                raise Exception("Directory has not been removed")
        except Exception as exc:
            traceback.print_exc()
            self.fail(exc)

    def test_create(self):
        try:
            do = DirectoryObject("test", temporary=True)
            do.remove()
            do.create()
            if not os.path.exists(do.path):
                raise Exception("Directory has not been created")
        except Exception as exc:
            traceback.print_exc()
            self.fail(exc)

    def test_move(self):
        try:
            do = DirectoryObject("test", temporary=True)
            do.move("test_move")
            if not os.path.exists("test_move"):
                raise Exception("Failed to move")
        except Exception as exc:
            traceback.print_exc()
            self.fail(exc)

    def test_copy(self):
        try:
            do = DirectoryObject("test", temporary=True)
            do_copy = do.copy("test_copy")
            if not isinstance(do_copy, DirectoryObject):
                raise Exception("DirectoryObject hasn't been returned as copy")
            if not os.path.exists("test_copy"):
                raise Exception("Failed to copy")
        except Exception as exc:
            traceback.print_exc()
            self.fail(exc)

    def test_chmod(self):
        try:
            do = DirectoryObject("test", temporary=True)
            do.chmod(0o644)
            if oct(os.stat(do.path).st_mode & 0o777) != oct(0o644):
                raise Exception("Wrong mode of moved directory")
        except Exception as exc:
            traceback.print_exc()
            self.fail(exc)

    def test_move_chmod(self):
        try:
            do = DirectoryObject("test", temporary=True)
            do.move("test_move")
            do.chmod(0o644)
            if oct(os.stat(do.path).st_mode & 0o777) != oct(0o644):
                raise Exception("Wrong mode of moved directory")
        except Exception as exc:
            traceback.print_exc()
            self.fail(exc)

    def test_copy_chmod(self):
        try:
            do = DirectoryObject("test", temporary=True)
            do_copy = do.copy("test_copy")
            do_copy.chmod(0o644)
            if oct(os.stat(do_copy.path).st_mode & 0o777) != oct(0o644):
                raise Exception("Wrong mode of copied directory")
        except Exception as exc:
            traceback.print_exc()
            self.fail(exc)


if __name__ == "__main__":
    unittest.main()
