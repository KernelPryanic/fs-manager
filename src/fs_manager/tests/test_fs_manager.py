import traceback
import unittest
import os
import shutil
import json

from fs_manager import FSManager


class TestFSManager(unittest.TestCase):
    def test_init(self):
        try:
            fsm = FSManager(temporary=True)
            if not os.path.exists(fsm.prefix_path):
                raise Exception("FSManager hasn't been initialized")
        except Exception as exc:
            traceback.print_exc()
            self.fail(exc)

    def test_del(self):
        try:
            fsm = FSManager(temporary=True)
            prefix_path = fsm.prefix_path
            del fsm
            if os.path.exists(prefix_path):
                raise Exception("Destructor hasn't remove all files")
        except Exception as exc:
            traceback.print_exc()
            self.fail(exc)

    def test_init_from_precreated(self):
        try:
            precreated = "/tmp/precreated"
            os.mkdir(precreated)
            fsm = FSManager(precreated, 0o744, temporary=True)
            if oct(os.stat(precreated).st_mode & 0o777) != oct(0o744):
                raise Exception("Failed to initialize from pre-created")
        except Exception as exc:
            traceback.print_exc()
            self.fail(exc)
        finally:
            shutil.rmtree(precreated)

    def test_mkfile(self):
        try:
            fsm = FSManager(temporary=True)
            fsm.mkfile("test/test1")
            if not os.path.exists(os.path.join(fsm.prefix_path, "test")):
                raise Exception("File hasn't been created")
        except Exception as exc:
            traceback.print_exc()
            self.fail(exc)

    def test_mkdir(self):
        try:
            fsm = FSManager(temporary=True)
            fsm.mkdir("test/test1")
            if not os.path.exists(os.path.join(fsm.prefix_path, "test")):
                raise Exception("File hasn't been created")
        except Exception as exc:
            traceback.print_exc()
            self.fail(exc)

    def test_file(self):
        try:
            fsm = FSManager(temporary=True)
            fsm.mkfile(alias="rambo", path="test/test1")
            if fsm.file("rambo") is None:
                raise Exception("Couldn't find a file")
        except Exception as exc:
            traceback.print_exc()
            self.fail(exc)

    def test_dir(self):
        try:
            fsm = FSManager(temporary=True)
            fsm.mkdir(alias="rambo", path="test/test1")
            if fsm.dir("rambo") is None:
                raise Exception("Couldn't find a directory")
        except Exception as exc:
            traceback.print_exc()
            self.fail(exc)

    def test_open(self):
        try:
            fsm = FSManager(temporary=True)
            fsm.mkfile(alias="rambo", path="test/test1")
            with fsm.open("rambo", "w") as f:
                f.write("rambo test")
            with open(fsm.file("rambo").path) as f:
                if f.readline() != "rambo test":
                    raise Exception("Couldn't write to file")
        except Exception as exc:
            traceback.print_exc()
            self.fail(exc)

    def test_remove(self):
        try:
            fsm = FSManager(temporary=True)
            fsm.mkdir("test1/test2")
            fsm.mkfile("test3/test4/test_file")
            fsm.remove()
            if os.path.exists(fsm.prefix_path):
                raise Exception("Couldn't remove all resources under prefix")
        except Exception as exc:
            traceback.print_exc()
            self.fail(exc)

    def test_exists(self):
        try:
            fsm = FSManager(temporary=True)
            fsm.mkdir("test1/test2")
            if os.path.exists(fsm.dir("test1/test2").path) != \
                    fsm.exists("test1/test2"):
                raise Exception("Exists at relative doesn't work")
        except Exception as exc:
            traceback.print_exc()
            self.fail(exc)

    def test_chmod_file(self):
        try:
            fsm = FSManager(temporary=True)
            fsm.mkfile("rambo", "test1/test2/test3")
            fsm.chmod("rambo", 0o644)
            if oct(os.stat(fsm.file("rambo").path).
                   st_mode & 0o777) != oct(0o644):
                raise Exception("Wrong mode of file")
        except Exception as exc:
            traceback.print_exc()
            self.fail(exc)

    def test_chmod_dir(self):
        try:
            fsm = FSManager(temporary=True)
            fsm.mkdir("rambo", "test1/test2/test3")
            fsm.chmod("rambo", 0o644)
            if oct(os.stat(fsm.dir("rambo").path).
                   st_mode & 0o777) != oct(0o644):
                raise Exception("Wrong mode of directory")
        except Exception as exc:
            traceback.print_exc()
            self.fail(exc)

    def test_rm_file(self):
        try:
            fsm = FSManager(temporary=True)
            fsm.mkfile("rambo", "test1/test2/test3")
            fsm.rm("rambo")
            if fsm.exists("test1/test2/test3"):
                raise Exception("File hasn't been removed")
        except Exception as exc:
            traceback.print_exc()
            self.fail(exc)

    def test_rm_dir(self):
        try:
            fsm = FSManager(temporary=True)
            fsm.mkdir("rambo", "test1/test2/test3")
            fsm.rm("rambo")
            if fsm.exists("test1/test2/test3"):
                raise Exception("Directory hasn't been removed")
        except Exception as exc:
            traceback.print_exc()
            self.fail(exc)

    def test_cp_file(self):
        try:
            fsm = FSManager(temporary=True)
            fsm.mkfile("rambo", "test1/test2/test3")
            fsm.cp("rambo", "test1/test22/test33")
            if not fsm.exists("test1/test22/test33"):
                raise Exception("File hasn't been copied")
        except Exception as exc:
            traceback.print_exc()
            self.fail(exc)

    def test_cp_dir(self):
        try:
            fsm = FSManager(temporary=True)
            fsm.mkdir("rambo", "test1/test2/test3")
            fsm.cp("rambo", "test1/test22/test33")
            if not fsm.exists("test1/test22/test33"):
                raise Exception("Directory hasn't been copied")
        except Exception as exc:
            traceback.print_exc()
            self.fail(exc)

    def test_cp_file_abs(self):
        try:
            fsm = FSManager(temporary=True)
            fsm.mkfile("rambo", "test1/test2/test3")
            fsm.cp("rambo", os.path.join(fsm.prefix_path,
                                         "test1/test22/test33"))
            if not os.path.exists(os.path.join(fsm.prefix_path,
                                               "test1/test22/test33")):
                raise Exception("File hasn't been copied")
        except Exception as exc:
            traceback.print_exc()
            self.fail(exc)

    def test_cp_dir_abs(self):
        try:
            fsm = FSManager(temporary=True)
            fsm.mkdir("rambo", "test1/test2/test3")
            fsm.cp("rambo", os.path.join(fsm.prefix_path,
                                         "test1/test22/test33"))
            if not os.path.exists(os.path.join(fsm.prefix_path,
                                               "test1/test22/test33")):
                raise Exception("Directory hasn't been copied")
        except Exception as exc:
            traceback.print_exc()
            self.fail(exc)

    def test_mv_file(self):
        try:
            fsm = FSManager(temporary=True)
            fsm.mkfile("rambo", "test1/test2/test3")
            fsm.mv("rambo", "test1/test22/test33")
            if not fsm.exists("test1/test22/test33"):
                raise Exception("File hasn't been moved")
        except Exception as exc:
            traceback.print_exc()
            self.fail(exc)

    def test_mv_dir(self):
        try:
            fsm = FSManager(temporary=True)
            fsm.mkdir("rambo", "test1/test2/test3")
            fsm.mv("rambo", "test1/test22/test33")
            if not fsm.exists("test1/test22/test33"):
                raise Exception("Directory hasn't been moved")
        except Exception as exc:
            traceback.print_exc()
            self.fail(exc)

    def test_mv_file_abs(self):
        try:
            fsm = FSManager(temporary=True)
            fsm.mkfile("rambo", "test1/test2/test3")
            fsm.mv("rambo", os.path.join(fsm.prefix_path,
                                         "test1/test22/test33"))
            if not os.path.exists(os.path.join(fsm.prefix_path,
                                               "test1/test22/test33")):
                raise Exception("File hasn't been moved")
        except Exception as exc:
            traceback.print_exc()
            self.fail(exc)

    def test_mv_dir_abs(self):
        try:
            fsm = FSManager(temporary=True)
            fsm.mkdir("rambo", "test1/test2/test3")
            fsm.mv("rambo", os.path.join(fsm.prefix_path,
                                         "test1/test22/test33"))
            if not os.path.exists(os.path.join(fsm.prefix_path,
                                               "test1/test22/test33")):
                raise Exception("Directory hasn't been moved")
        except Exception as exc:
            traceback.print_exc()
            self.fail(exc)

    def test_small_manipulations(self):
        try:
            os.mkdir("/tmp/fsm_tests/")
            with FSManager(base_path="/tmp/fsm_tests/small_manipulations",
                           mode=0o744, temporary=False) as fsm:
                fsm.mkdir("rambo", "rambo_dir", 0o744, False)
                fsm.cd("rambo")
                fsm.mkfile("rambo", "rambo_file", True)
                fsm.ls()
                fsm.back()
                fsm.ls()
                fsm.rm("rambo")
                if os.path.exists(os.path.join("/tmp/fsm_tests/"
                                               "small_manipulations",
                                               "rambo_dir")):
                    raise Exception("Failed to remove directory")
                fsm.mkdir("rambo_dir")
            if not os.path.exists(os.path.join("/tmp/fsm_tests/"
                                               "small_manipulations",
                                               "rambo_dir")):
                raise Exception("Directory has been deleted")
        except Exception as exc:
            traceback.print_exc()
            self.fail(exc)
        finally:
            try:
                shutil.rmtree("/tmp/fsm_tests", ignore_errors=True)
            except:
                pass

    def test_save(self):
        try:
            os.mkdir("/tmp/fsm_tests/")
            with FSManager(base_path="/tmp/fsm_tests/save_test",
                           mode=0o744, temporary=False) as fsm:
                fsm.mkdir("test1")
                fsm.cd("test1")
                fsm.mkfile("test11")
            if not os.path.exists("/tmp/fsm_tests/"
                                  "save_test/.fs-structure.json"):
                raise Exception("Save of structure failed")
        except Exception as exc:
            traceback.print_exc()
            self.fail(exc)
        finally:
            try:
                shutil.rmtree("/tmp/fsm_tests", ignore_errors=True)
            except:
                pass

    def test_load(self):
        try:
            os.mkdir("/tmp/fsm_tests/")
            with FSManager(base_path="/tmp/fsm_tests/load_test",
                           mode=0o744, temporary=False) as fsm:
                fsm.mkdir("test1")
                fsm.cd("test1")
                fsm.mkdir("test11")
                fsm.cd("test11")
                fsm.mkfile("test111")
                fsm.cd_root()
                fsm.mkdir("test2")
                fsm.mkfile("test2/test22")
            with FSManager(base_path="/tmp/fsm_tests/load_test",
                           mode=0o744, temporary=False) as fsm:
                if fsm.file("test2/test22") is None:
                    raise Exception("Can't load structure")
        except Exception as exc:
            traceback.print_exc()
            self.fail(exc)
        finally:
            try:
                shutil.rmtree("/tmp/fsm_tests", ignore_errors=True)
            except:
                pass

    def test_snappy(self):
        try:
            os.mkdir("/tmp/fsm_tests/")
            os.makedirs("/tmp/fsm_tests/rules/plague")
            os.makedirs("/tmp/fsm_tests/water/fire")
            with open("/tmp/fsm_tests/water/fire/stone", "w") as f:
                f.write("stone")
            with FSManager(base_path="/tmp/fsm_tests/",
                           mode=0o744, temporary=False) as fsm:
                fsm.snappy()
                fsm.cd("water")
                fsm.cd("fire")
                if fsm.file("stone") is None:
                    raise Exception("Snappy doesn't work")
        except Exception as exc:
            traceback.print_exc()
            self.fail(exc)
        finally:
            try:
                shutil.rmtree("/tmp/fsm_tests", ignore_errors=True)
            except:
                pass

    def test_snappy_root_binded(self):
        try:
            os.mkdir("/tmp/fsm_tests/")
            os.makedirs("/tmp/fsm_tests/rules/plague")
            os.makedirs("/tmp/fsm_tests/water/fire")
            with open("/tmp/fsm_tests/water/fire/stone", "w") as f:
                f.write("stone")
            with FSManager(base_path="/tmp/fsm_tests/",
                           mode=0o744, temporary=False) as fsm:
                fsm.snappy(True)
                if fsm.file("water/fire/stone") is None:
                    raise Exception("Snappy doesn't work")
        except Exception as exc:
            traceback.print_exc()
            self.fail(exc)
        finally:
            try:
                shutil.rmtree("/tmp/fsm_tests", ignore_errors=True)
            except:
                pass

    def test_save_all(self):
        try:
            os.mkdir("/tmp/fsm_tests/")
            with FSManager(base_path="/tmp/fsm_tests/",
                           mode=0o744, temporary=False) as fsm:
                fsm.mkdir("test1")
                fsm.mkfile("test1/test11")
                fsm.mkdir("test2/test22")
                fsm.cd("test2/test22")
                fsm.mkfile("test222")
                fsm.save_all()
            if not os.path.exists("/tmp/fsm_tests/.fs-structure-full.json"):
                raise Exception("Failed to save full structure")
        except Exception as exc:
            traceback.print_exc()
            self.fail(exc)
        finally:
            try:
                shutil.rmtree("/tmp/fsm_tests", ignore_errors=True)
            except:
                pass

    def test_load_all(self):
        try:
            os.makedirs("/tmp/fsm_tests/save1")
            os.makedirs("/tmp/fsm_tests/save2")
            with FSManager(base_path="/tmp/fsm_tests/save1",
                           mode=0o744, temporary=False) as fsm:
                fsm.mkdir("test1")
                fsm.mkfile("test1/test11")
                fsm.mkdir("test2/test22")
                fsm.cd("test2/test22")
                fsm.mkfile("test222")
                fsm.save_all()
            shutil.copy("/tmp/fsm_tests/save1/.fs-structure-full.json",
                        "/tmp/fsm_tests/save2/.fs-structure-full.json")
            with FSManager(base_path="/tmp/fsm_tests/save2",
                           mode=0o744, temporary=False) as fsm:
                fsm.load_all()
                if fsm.file("test1/test11") is None:
                    raise Exception("Failed to load from full structure")
        except Exception as exc:
            traceback.print_exc()
            self.fail(exc)
        finally:
            try:
                shutil.rmtree("/tmp/fsm_tests", ignore_errors=True)
            except:
                pass

    def test_save_hashsums(self):
        try:
            os.makedirs("/tmp/fsm_tests")
            with FSManager(base_path="/tmp/fsm_tests/",
                           temporary=False) as fsm:
                fsm.mkdir("test1")
                fsm.mkfile("test1/test_file")
                fsm.mkdir("test2")
                fsm.cd("test2")
                fsm.mkfile("test_file")
                fsm.cd_root()
                fsm.save_hashsums()
            with open("/tmp/fsm_tests/test2/.fs-structure.json") as f:
                loaded = json.load(f)
                if "md5" not in loaded["test_file"]:
                    raise Exception("Hashsum hasn't been saved")
        except Exception as exc:
            traceback.print_exc()
            self.fail(exc)
        finally:
            try:
                shutil.rmtree("/tmp/fsm_tests", ignore_errors=True)
            except:
                pass

    def test_check_hassums(self):
        try:
            os.makedirs("/tmp/fsm_tests")
            with FSManager(base_path="/tmp/fsm_tests/",
                           temporary=False) as fsm:
                fsm.mkdir("test1")
                fsm.mkfile("test1/test_file")
                fsm.mkdir("test2")
                fsm.cd("test2")
                fsm.mkfile("test_file")
                fsm.cd_root()
                fsm.save_hashsums()
                with open("/tmp/fsm_tests/test2/test_file", "w") as f:
                    f.write("change hashsum")
                mismatch = fsm.check_hashsums(log_warnings=False)
                if not mismatch:
                    raise Exception("Checking of hashsums are failed")
        except Exception as exc:
            traceback.print_exc()
            self.fail(exc)
        finally:
            try:
                shutil.rmtree("/tmp/fsm_tests", ignore_errors=True)
            except:
                pass


if __name__ == "__main__":
    unittest.main()
