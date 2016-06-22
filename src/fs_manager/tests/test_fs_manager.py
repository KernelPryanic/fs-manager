import traceback
import unittest
import os
import shutil

from fs_manager import FSManager


class TestFSManager(unittest.TestCase):
    def test_init(self):
        try:
            rm = FSManager(temporary=True, rand_prefix=True)
            if not os.path.exists(rm.prefix_path):
                raise Exception("FSManager hasn't been initialized")
        except Exception as exc:
            traceback.print_exc()
            self.fail(exc)

    def test_del(self):
        try:
            rm = FSManager(temporary=True, rand_prefix=True)
            prefix_path = rm.prefix_path
            del rm
            if os.path.exists(prefix_path):
                raise Exception("Destructor hasn't remove all files")
        except Exception as exc:
            traceback.print_exc()
            self.fail(exc)

    def test_mkfile(self):
        try:
            rm = FSManager(temporary=True, rand_prefix=True)
            rm.mkfile("test/test1")
            if not os.path.exists(os.path.join(rm.prefix_path, "test")):
                raise Exception("File hasn't been created")
        except Exception as exc:
            traceback.print_exc()
            self.fail(exc)

    def test_mkdir(self):
        try:
            rm = FSManager(temporary=True, rand_prefix=True)
            rm.mkdir("test/test1")
            if not os.path.exists(os.path.join(rm.prefix_path, "test")):
                raise Exception("File hasn't been created")
        except Exception as exc:
            traceback.print_exc()
            self.fail(exc)

    def test_file(self):
        try:
            rm = FSManager(temporary=True, rand_prefix=True)
            rm.mkfile(alias="rambo", path="test/test1")
            if rm.file("rambo") is None:
                raise Exception("Couldn't find a file")
        except Exception as exc:
            traceback.print_exc()
            self.fail(exc)

    def test_dir(self):
        try:
            rm = FSManager(temporary=True, rand_prefix=True)
            rm.mkdir(alias="rambo", path="test/test1")
            if rm.dir("rambo") is None:
                raise Exception("Couldn't find a directory")
        except Exception as exc:
            traceback.print_exc()
            self.fail(exc)

    def test_open(self):
        try:
            rm = FSManager(temporary=True, rand_prefix=True)
            rm.mkfile(alias="rambo", path="test/test1")
            with rm.open("rambo", "w") as f:
                f.write("rambo test")
            with open(rm.file("rambo").path) as f:
                if f.readline() != "rambo test":
                    raise Exception("Couldn't write to file")
        except Exception as exc:
            traceback.print_exc()
            self.fail(exc)

    def test_remove(self):
        try:
            rm = FSManager(temporary=True, rand_prefix=True)
            rm.mkdir("test1/test2")
            rm.mkfile("test3/test4/test_file")
            rm.remove()
            if os.path.exists(rm.prefix_path):
                raise Exception("Couldn't remove all resources under prefix")
        except Exception as exc:
            traceback.print_exc()
            self.fail(exc)

    def test_exists(self):
        try:
            rm = FSManager(temporary=True, rand_prefix=True)
            rm.mkdir("test1/test2")
            if os.path.exists(rm.dir("test1/test2").path) != \
                    rm.exists("test1/test2"):
                raise Exception("Exists at relative doesn't work")
        except Exception as exc:
            traceback.print_exc()
            self.fail(exc)

    def test_chmod_file(self):
        try:
            rm = FSManager(temporary=True, rand_prefix=True)
            rm.mkfile("rambo", "test1/test2/test3")
            rm.chmod("rambo", 0o644)
            if oct(os.stat(rm.file("rambo").path).
                   st_mode & 0o777) != oct(0o644):
                raise Exception("Wrong mode of file")
        except Exception as exc:
            traceback.print_exc()
            self.fail(exc)

    def test_chmod_dir(self):
        try:
            rm = FSManager(temporary=True, rand_prefix=True)
            rm.mkdir("rambo", "test1/test2/test3")
            rm.chmod("rambo", 0o644)
            if oct(os.stat(rm.dir("rambo").path).
                   st_mode & 0o777) != oct(0o644):
                raise Exception("Wrong mode of directory")
        except Exception as exc:
            traceback.print_exc()
            self.fail(exc)

    def test_rm_file(self):
        try:
            rm = FSManager(temporary=True, rand_prefix=True)
            rm.mkfile("rambo", "test1/test2/test3")
            rm.rm("rambo")
            if rm.exists("test1/test2/test3"):
                raise Exception("File hasn't been removed")
        except Exception as exc:
            traceback.print_exc()
            self.fail(exc)

    def test_rm_dir(self):
        try:
            rm = FSManager(temporary=True, rand_prefix=True)
            rm.mkdir("rambo", "test1/test2/test3")
            rm.rm("rambo")
            if rm.exists("test1/test2/test3"):
                raise Exception("Directory hasn't been removed")
        except Exception as exc:
            traceback.print_exc()
            self.fail(exc)

    def test_cp_file(self):
        try:
            rm = FSManager(temporary=True, rand_prefix=True)
            rm.mkfile("rambo", "test1/test2/test3")
            rm.cp("rambo", "test1/test22/test33")
            if not rm.exists("test1/test22/test33"):
                raise Exception("File hasn't been copied")
        except Exception as exc:
            traceback.print_exc()
            self.fail(exc)

    def test_cp_dir(self):
        try:
            rm = FSManager(temporary=True, rand_prefix=True)
            rm.mkdir("rambo", "test1/test2/test3")
            rm.cp("rambo", "test1/test22/test33")
            if not rm.exists("test1/test22/test33"):
                raise Exception("Directory hasn't been copied")
        except Exception as exc:
            traceback.print_exc()
            self.fail(exc)

    def test_cp_file_abs(self):
        try:
            rm = FSManager(temporary=True, rand_prefix=True)
            rm.mkfile("rambo", "test1/test2/test3")
            rm.cp("rambo", os.path.join(rm.prefix_path, "test1/test22/test33"))
            if not os.path.exists(os.path.join(rm.prefix_path,
                                               "test1/test22/test33")):
                raise Exception("File hasn't been copied")
        except Exception as exc:
            traceback.print_exc()
            self.fail(exc)

    def test_cp_dir_abs(self):
        try:
            rm = FSManager(temporary=True, rand_prefix=True)
            rm.mkdir("rambo", "test1/test2/test3")
            rm.cp("rambo", os.path.join(rm.prefix_path, "test1/test22/test33"))
            if not os.path.exists(os.path.join(rm.prefix_path,
                                               "test1/test22/test33")):
                raise Exception("Directory hasn't been copied")
        except Exception as exc:
            traceback.print_exc()
            self.fail(exc)

    def test_mv_file(self):
        try:
            rm = FSManager(temporary=True, rand_prefix=True)
            rm.mkfile("rambo", "test1/test2/test3")
            rm.mv("rambo", "test1/test22/test33")
            if not rm.exists("test1/test22/test33"):
                raise Exception("File hasn't been moved")
        except Exception as exc:
            traceback.print_exc()
            self.fail(exc)

    def test_mv_dir(self):
        try:
            rm = FSManager(temporary=True, rand_prefix=True)
            rm.mkdir("rambo", "test1/test2/test3")
            rm.mv("rambo", "test1/test22/test33")
            if not rm.exists("test1/test22/test33"):
                raise Exception("Directory hasn't been moved")
        except Exception as exc:
            traceback.print_exc()
            self.fail(exc)

    def test_mv_file_abs(self):
        try:
            rm = FSManager(temporary=True, rand_prefix=True)
            rm.mkfile("rambo", "test1/test2/test3")
            rm.mv("rambo", os.path.join(rm.prefix_path, "test1/test22/test33"))
            if not os.path.exists(os.path.join(rm.prefix_path,
                                               "test1/test22/test33")):
                raise Exception("File hasn't been moved")
        except Exception as exc:
            traceback.print_exc()
            self.fail(exc)

    def test_mv_dir_abs(self):
        try:
            rm = FSManager(temporary=True, rand_prefix=True)
            rm.mkdir("rambo", "test1/test2/test3")
            rm.mv("rambo", os.path.join(rm.prefix_path, "test1/test22/test33"))
            if not os.path.exists(os.path.join(rm.prefix_path,
                                               "test1/test22/test33")):
                raise Exception("Directory hasn't been moved")
        except Exception as exc:
            traceback.print_exc()
            self.fail(exc)

    def test_small_manipulations(self):
        try:
            with FSManager(base_path="/tmp/small_manipulations",
                           mode=0o744, temporary=False,
                           rand_prefix=False) as rm:
                rm.mkdir("rambo", "rambo_dir", 0o744, False)
                rm.cd("rambo")
                rm.mkfile("rambo", "rambo_file", True)
                rm.ls()
                rm.back()
                rm.ls()
                rm.rm("rambo")
                if os.path.exists(os.path.join("/tmp/small_manipulations",
                                               "rambo_dir")):
                    raise Exception("Failed to remove directory")
                rm.mkdir("rambo_dir")
            if not os.path.exists(os.path.join("/tmp/small_manipulations",
                                               "rambo_dir")):
                raise Exception("Directory has been deleted")
            shutil.rmtree("/tmp/small_manipulations")
        except Exception as exc:
            traceback.print_exc()
            self.fail(exc)


if __name__ == "__main__":
    unittest.main()
