from collections import MutableSequence
from collections import MutableMapping
from contextlib import contextmanager
import os
import shutil
import tempfile
import hashlib
import re
import logger
import logging
import json


log = logging.getLogger()
log.setLevel(logging.DEBUG)
log.addHandler(logger.FSMStreamHandler())


re_url_tail = re.compile('[^\/]+$')
re_url_head = re.compile('^[^\/]+')
re_url_long_tail = re.compile('\/.+$')
re_url_long_head = re.compile('^.+\/')


CHUNK_SIZE = 65536


class FileObject(object):
    def __init__(self, path, mode=0o600, temporary=False, parent=None):
        '''
        Create new file or use already existing one

        @param path: Path to file
        @type path: `str`
        @param parent: Parent resource
        @type parent: `DirectoryObject`
        @param mode: Mode bits of file
        @type mode: `int`
        @param temporary: Is this file has to be deleted when script is done?
        @type temporary: `bool`
        '''

        self._parent = None
        self.parent = parent
        self._path = os.path.abspath(path)
        self.temporary = temporary
        self.file_name = re_url_tail.search(self.path).group(0)
        self.file_path = re_url_long_head.search(self.path).group(0)

        if os.path.exists(self.path):
            self.mode = os.stat(self.path).st_mode
        else:
            self._mode = mode
            self.create()

    def __del__(self):
        if self.temporary and os.path.exists(self.path):
            self.remove()

    def __eq__(self, other):
        return isinstance(other, FileObject) and self.path == other.path

    def __repr__(self):
        return "{}({})".format(
            self.__class__.__name__, repr(self.path)
        )

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.remove()

    @property
    def path(self):
        return self._path

    @path.setter
    def path(self, value):
        new_abspath = os.path.abspath(value)
        if new_abspath != self.path:
            self.__init__(new_abspath, self.parent, self.mode, self.temporary)

    @path.deleter
    def path(self):
        del self._path

    @property
    def mode(self):
        self._mode = os.stat(self.path).st_mode & 0o777
        return self._mode

    @mode.setter
    def mode(self, value):
        self.chmod(value)

    @mode.deleter
    def mode(self):
        del self._mode

    @property
    def parent(self):
        return self._parent

    @parent.setter
    def parent(self, value):
        if isinstance(value, DirectoryObject) and value != self._parent:
            self._parent = value
            self.parent.append(self)

    @parent.deleter
    def parent(self):
        del self._parent

    def unparent(self):
        '''Remove FileObject from parent and set parent to None'''

        if self.parent:
            self.parent.pop(self.parent.index(self))
            self._parent = None

    def create(self):
        '''Create file on the system'''

        try:
            if not os.path.exists(self.path):
                f = open(self.path, 'w')
                f.close()
                self.chmod(self._mode)
        except IOError as exc:
            log.error("Can't create file")
            raise exc

    def remove(self):
        '''Remove file from the system'''

        try:
            os.remove(self.path)
            self.unparent()
        except OSError as exc:
            log.error("Can't remove file")
            raise exc

    def chmod(self, mode):
        '''
        Change mode bits of file

        @param mode: Mode bits of the the file
        @type mode: `int`
        '''

        try:
            os.chmod(self.path, mode)
            self._mode = mode
        except OSError as exc:
            if exc.errno == 1:
                log.error("Can't change file permissions under current user")
                raise exc
            else:
                log.error("Can't change file permissions")
                raise exc

    def move(self, dst):
        '''
        Move file to destination

        @param dst: Destination path with new file name included
        @type dst: `str`
        '''

        abs_dst = os.path.abspath(dst)
        try:
            os.rename(self.path, abs_dst)
            self._path = abs_dst
        except OSError as exc:
            log.error("Can't move file")
            raise exc

    def copy(self, dst, same_parent=True):
        '''
        Copy file to destination

        @param dst: Destination path with file name included
        @type dst: `str`
        @param same_parent: Is the new file has same parent?
        @type same_parent: `bool`
        @return: New FileObject binded with new file
        '''

        abs_dst = os.path.abspath(dst)
        try:
            shutil.copy2(self.path, abs_dst)
        except IOError as exc:
            log.error("Can't copy file")
            raise exc

        return FileObject(abs_dst, self.mode, self.temporary,
                          self.parent if same_parent else None)

    def md5(self):
        '''Get md5 hash sum of the file'''

        md5_sum = hashlib.md5()
        with open(self.path, 'rb') as f:
            while True:
                resources = f.read(CHUNK_SIZE)
                if not resources:
                    break
                md5_sum.update(resources)

        return md5_sum.hexdigest()

    def sha1(self):
        '''Get sha1 hash sum of the file'''

        sha1_sum = hashlib.sha1()
        with open(self.path, 'rb') as f:
            while True:
                resources = f.read(CHUNK_SIZE)
                if not resources:
                    break
                sha1_sum.update(resources)

        return sha1_sum.hexdigest()


class DirectoryObject(MutableSequence, object):
    def __init__(self, path, mode=0o700, temporary=False, parent=None):
        '''
        Create new directory or use already existing one

        @param path: Path to directory
        @type path: `str`
        @param parent: Parent resource
        @type parent: `DirectoryObject`
        @param mode: Mode bits of directory
        @type mode: `int`
        @param temporary: Is this directory has to be deleted
        when script is done?
        @type temporary: `bool`
        '''

        self._path = os.path.abspath(path)
        self.temporary = temporary
        self.dir_name = re_url_tail.search(self.path).group(0)
        self.dir_path = re_url_long_head.search(self.path).group(0)
        self.resources = []
        self._parent = None
        self.parent = parent

        if os.path.exists(self.path):
            self._mode = os.stat(self.path).st_mode
        else:
            self._mode = mode
            self.create()

    # Collection methods start

    def __getitem__(self, index):
        return self.resources[index]

    def __setitem__(self, index, value):
        self.resources[index] = value

    def __delitem__(self, index):
        del self.resources[index]

    def __iter__(self):
        return iter(self.resources)

    def __len__(self):
        return len(self.resources)

    # Collection methods end

    def __del__(self):
        if self.temporary and os.path.exists(self.path):
            self.remove()

    def __eq__(self, other):
        return isinstance(other, DirectoryObject) and self.path == other.path

    def __repr__(self):
        return "{}({})".format(
            self.__class__.__name__, repr(self.path)
        )

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.remove()

    @property
    def path(self):
        return self._path

    @path.setter
    def path(self, value):
        new_abspath = os.path.abspath(value)
        if new_abspath != self.path:
            self.__init__(new_abspath, self.parent, self.mode, self.temporary)

    @path.deleter
    def path(self):
        del self._path

    @property
    def mode(self):
        self._mode = os.stat(self.path).st_mode & 0o777
        return self._mode

    @mode.setter
    def mode(self, value):
        self.chmod(value)

    @mode.deleter
    def mode(self):
        del self._mode

    @property
    def parent(self):
        return self._parent

    @parent.setter
    def parent(self, value):
        if isinstance(value, DirectoryObject) and value != self._parent:
            self._parent = value
            self.parent.append(self)

    @parent.deleter
    def parent(self):
        del self._parent

    def unparent(self):
        '''Remove DirectoryObject from parent and set parent to None'''

        if self.parent:
            self.parent.pop(self.parent.index(self))
            self._parent = None

    def create(self):
        '''Create directory on the system'''

        try:
            if not os.path.exists(self.path):
                os.mkdir(self.path, self._mode)
        except OSError as exc:
            log.error("Can't create directory")
            raise exc

    def remove(self):
        '''Remove directory from the system'''

        try:
            shutil.rmtree(self.path)
            self.unparent()
            for el in self.resources:
                el.parent = None
        except IOError as exc:
            log.error("Can't remove directory")
            raise exc

    def chmod(self, mode):
        '''
        Change mode bits of the directory

        @param mode: Mode bits of the file
        @type mode: `int`
        '''

        try:
            os.chmod(self.path, mode)
            self._mode = mode
        except OSError as exc:
            if exc.errno == 1:
                log.error("Can't change directory "
                          "permissions under current user")
                raise exc
            else:
                log.error(exc)
                raise exc

    def move(self, dst):
        '''
        Move directory to destination

        @param dst: Destination path with new file name included
        @type dst: `str`
        '''

        abs_dst = os.path.abspath(dst)
        try:
            os.rename(self.path, abs_dst)
            self._path = abs_dst
        except OSError as exc:
            raise exc

    def copy(self, dst, same_parent=True):
        '''
        Copy directory to destination

        @param dst: Destination path with directory name included
        @type dst: `str`
        @param same_parent: Is the new directory has same parent?
        @type same_parent: `bool`
        @return: New DirectoryObject binded with new directory
        '''

        abs_dst = os.path.abspath(dst)
        try:
            shutil.copytree(self.path, abs_dst)
        except IOError as exc:
            log.error("Can't copy directory")
            raise exc

        return DirectoryObject(abs_dst, self.mode, self.temporary,
                               self.parent if same_parent else None)

    # Collection methods start

    def append(self, resource):
        '''Append a resource object into collection'''

        if isinstance(resource, FileObject) or \
            isinstance(resource, DirectoryObject) and \
                self.index(resource) is None:
            self.resources.append(resource)
            resource._parent = self

    def insert(self, index, resource):
        '''Insert a resource object into collection'''

        if isinstance(resource, FileObject) or \
            isinstance(resource, DirectoryObject) and \
                self.index(resource) is None:
            self.resources.insert(index, resource)
            resource._parent = self

    def index(self, resource=None, path=None):
        '''Return the index of resource'''

        for el_idx, el in enumerate(self.resources):
            if el == resource or path == el.path:
                return el_idx

    def pop(self, idx):
        '''Return resource on "idx" index and delete it then'''

        self.resources[idx]._parent = None
        return self.resources.pop(idx)

    # Collection methods end


class AliasedDirectoryObject(MutableMapping, DirectoryObject, object):
    def __init__(self, path, mode=0o700, temporary=False, parent=None):
        self.aliases = dict()
        DirectoryObject.__init__(self, path, mode, temporary, parent)

    # Collection methods start

    def __getitem__(self, key):
        return self.resources[self.aliases[key]]

    def __setitem__(self, key, value):
        self.aliases[key] = self.resources.index(value)

    def __delitem__(self, key):
        del self.aliases[key]

    def __iter__(self):
        return iter(self.aliases)

    def __len__(self):
        return len(self.aliases)

    # Collection methods end

    def __eq__(self, other):
        return isinstance(other, DirectoryObject) and self.path == other.path

    # `pop` overwrites because of overwriting of `__getitem__` method
    #  thus `pop` tries to get element by index
    #  but `__getitem__` accepts key instead
    def pop(self, idx):
        '''Return resource on "idx" index and delete it then'''

        self.resources[idx]._parent = None
        return self.resources.pop(idx)


class FSManager(object):
    def __init__(self, base_path="/tmp/fs-manager/", mode=0o700,
                 temporary=False):
        '''
        Initialize ResourceManger within the prefix path

        @param base_path: Base path of the resources
        @type base_path: `str`
        @param mode: Mode bits of directory
        @type mode: `int`
        @param temporary: Is this FSManager has to be deleted
        with all the resources under it after script is done?
        Also randomly generated directory will be used as prefix.
        @type temporary: `bool`
        '''

        self.base_path = os.path.abspath(base_path)
        self._temporary = temporary
        DirectoryObject(self.base_path, mode).chmod(mode)

        self.prefix_path = tempfile.mkdtemp(prefix=self.base_path + "/") \
            if self.temporary else self.base_path

        self.root_directory = AliasedDirectoryObject(self.prefix_path, mode,
                                                     temporary)
        self.current_directory = self.root_directory
        self.pred = self.current_directory
        self.load()

    def __del__(self):
        if self.temporary and os.path.exists(self.root_directory.path):
            self.remove()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.__del__()

    @property
    def temporary(self):
        return self._temporary

    @temporary.setter
    def temporary(self, value):
        pass

    @temporary.deleter
    def temporary(self):
        del self.temporary

    def _prepare(self, path):
        '''
        Pre-create row of the directories for resource

        @param path: Initial path. Tail - name of file/directory, head - path.
        @type path: `str`
        '''

        abs_path = self.abspath(path)
        prefix = re_url_long_head.search(abs_path).group(0)
        if not os.path.exists(prefix):
            try:
                os.makedirs(prefix)
            except OSError as exc:
                log.error("Can't create prefix for path")
                raise exc

    def resource(self, alias):
        '''
        Return FileObject/DirectoryObject resource if it's in there

        @param alias: Alias name of the resource
        @type alias: `str`
        @return: FileObject/DirectoryObject resource
        '''

        if alias in self.current_directory:
            if not os.path.exists(self.current_directory[alias].path):
                log.warning("There is no such resource at {}".
                            format(self.current_directory[alias].path))

            return self.current_directory[alias]

    def file(self, alias):
        '''
        Return FileObject resource if it's in there

        @param alias: Alias name of the resource
        @type alias: `str`
        @return: FileObject resource
        '''

        if alias in self.current_directory and \
                isinstance(self.current_directory[alias], FileObject):
            if not os.path.exists(self.current_directory[alias].path):
                log.warning("There is no such file at {}".
                            format(self.current_directory[alias]))

            return self.current_directory[alias]

    def dir(self, alias):
        '''
        Return DirectoryObject resource if it's in there

        @param alias: Alias name of the resource
        @type alias: `str`
        @return: DirectoryObject resource
        '''

        if alias in self.current_directory and \
                isinstance(self.current_directory[alias], DirectoryObject):
            if not os.path.exists(self.current_directory[alias].path):
                log.warning("There is no such directory at {}".
                            format(self.current_directory[alias]))

            return self.current_directory[alias]

    def cd(self, alias):
        '''
        Switch prefix path

        @param alias: Alias of new prefix path
        @type alias: `str`
        '''

        if self.dir(alias) is not None:
            self.pred = self.current_directory
            self.prefix_path = self.dir(alias).path
            self.current_directory = self.dir(alias)
        else:
            log.info("There is no such directory '{}'".format(alias))

    def up(self):
        '''Switch to parent directory'''

        if self.current_directory.parent:
            self.pred = self.current_directory
            self.prefix_path = self.abspath(self.current_directory.parent.path)
            self.current_directory = self.current_directory.parent

    def back(self):
        '''Switch to previous directory'''

        self.prefix_path = self.abspath(self.pred.path)
        self.current_directory = self.pred

    def cd_root(self):
        '''Return working directory to the prefix path'''

        self.prefix_path = self.root_directory.path
        self.current_directory = self.root_directory

    @contextmanager
    def open(self, alias, mode="r"):
        '''
        Open file at relative path

        @param alias: Alias or relative path
        @type alias: `str`
        @param mode: Mode of operating
        @param mode: `str`
        '''

        if self.file(alias) is not None:
            f = open(self.file(alias).path, mode)
        else:
            try:
                f = open(self.abspath(alias), mode)
            except IOError as exc:
                log.error("Can't open file {}".format(self.abspath(alias)))
                raise exc

        try:
            yield f
            f.close()
        except IOError as exc:
            log.error("Can't open file {}".format(self.abspath(alias)))
            raise exc

    def remove(self):
        '''CAUTION: Remove all the resources under prefix path'''

        try:
            shutil.rmtree(self.root_directory.path)
        except IOError as exc:
            log.error("Can't remove prefix path")
            raise exc

    def exists(self, path=""):
        '''
        Check if resource exists at relative path

        @param path: Relative path
        @type path: `str`
        '''

        return os.path.exists(self.abspath(path))

    def abspath(self, path=""):
        '''
        Return absolute path instead of relative one

        @param path: Relative or absolute path
        @type path: `str`
        '''
        if path.startswith("/"):
            return os.path.abspath(path)
        else:
            return os.path.abspath(os.path.join(self.prefix_path, path))

    def mkfile(self, alias=None, path=None, mode=0o600, temporary=False):
        '''
        Make the file within prefix path

        @param alias: Alias name of the file to make
        @type alias: `str`
        @param path: Path with the file name included
        @type path: `str`
        @param mode: Mode bits of file
        @type mode: `int`
        '''

        if alias is None and path is None:
            log.info("Please, specify either alias or path")
            return

        if alias is None:
            _alias = path
        else:
            _alias = alias
        if path is None:
            _path = alias
        else:
            _path = path

        if self.resource(_alias):
            log.info("File hasn't been created. "
                     "There is already such an alias '{}'".format(_alias))
        else:
            abs_path = self.abspath(_path)
            self._prepare(abs_path)
            self.current_directory[_alias] = FileObject(abs_path, mode,
                                                        temporary,
                                                        self.current_directory)
            if not self.temporary:
                self.save()

    def mkdir(self, alias=None, path=None, mode=0o700, temporary=False):
        '''
        Make the directory within prefix path

        @param alias: Alias name of the directory to make
        @type alias: `str`
        @param path: Path with the directory name included
        @type path: `str`
        @param mode: Mode bits of directory
        @type mode: `int`
        '''

        if alias is None and path is None:
            log.info("Please, specify either alias or path")
            return

        if alias is None:
            _alias = path
        else:
            _alias = alias
        if path is None:
            _path = alias
        else:
            _path = path

        if self.resource(_alias):
            log.info("Directory hasn't been created. "
                     "There is already such an alias '{}'".format(_alias))
        else:
            abs_path = self.abspath(_path)
            self._prepare(abs_path)
            self.current_directory[_alias] = \
                AliasedDirectoryObject(abs_path, mode, temporary,
                                       self.current_directory)
            if not self.temporary:
                self.save()

    def chmod(self, alias, mode):
        '''
        Change mode bits of the resource

        @param alias: Alias name of the resource
        @type alias: `str`
        @param mode: Mode bits of the resource
        @type mode: `int`
        '''

        if self.resource(alias) is not None:
            self.current_directory[alias].chmod(mode)
            if not self.temporary:
                self.save()

    def rm(self, alias):
        '''
        Remove the resource

        @param alias: Alias name of the resource to remove
        @type alias: `str`
        '''

        if self.resource(alias) is not None:
            self.current_directory[alias].remove()
            del self.current_directory[alias]
            if not self.temporary:
                self.save()

    def cp(self, alias, dst):
        '''
        Make a copy of resource

        @param alias: Alias name of the resource to copy
        @type alias: `str`
        @param dst: Destination path with the resource name included
        @type dst: `str`
        '''

        if self.resource(alias) is not None:
            self._prepare(self.abspath(dst))
            self.current_directory[alias].copy(self.abspath(dst))

    def mv(self, alias, dst):
        '''
        Move the resource

        @param alias: Alias name of the resource to move
        @type alias: `str`
        @param dst: Destination path with the resource name included
        @type dst: `str`
        '''

        if self.resource(alias) is not None:
            self._prepare(self.abspath(dst))
            self.current_directory[alias].move(self.abspath(dst))
            if not self.temporary:
                self.save()

    def ls(self):
        '''List all the resources under prefix'''

        if not self.current_directory:
            return ""

        res = ""
        dash = " ------- "

        max_len = len(max(self.current_directory.keys(), key=len))
        max_tabs = max_len / 8
        max_tabs += 1 if max_len % 8 else 0

        for key, val in self.current_directory.iteritems():
            tabs_n = max_tabs - len(key) / 8
            tabs = "\t" * tabs_n
            type = "[File]\t\t" if isinstance(val, FileObject) \
                else "[Directory]\t"
            res += "{0}{3}{4}{5}\t{2}{1}\n".format(key, val.path, dash * 5,
                                                   tabs, type, oct(val.mode))
        print res

    def save(self):
        '''Save current fs entry to structure .json file'''

        current_fs_struct = dict()
        for alias, value in self.current_directory.iteritems():
            current_fs_struct[alias] = \
                {"path": os.path.relpath(value.path, self.root_directory.path),
                 "mode": value.mode,
                 "temporary": value.temporary}

            if isinstance(value, FileObject):
                current_fs_struct[alias]["type"] = "file"
            else:
                current_fs_struct[alias]["type"] = "directory"

        with self.open(".fs-structure.json", "w") as f:
            f.write(unicode(json.dumps(current_fs_struct,
                                       indent=4,
                                       separators=(',', ':'),
                                       ensure_ascii=False)))

    def load(self):
        '''Load current fs entry from structure .json file'''

        if self.exists(".fs-structure.json"):
            current_fs_struct = dict()
            with self.open(".fs-structure.json", "r") as f:
                current_fs_struct = json.load(f)

            for alias, value in current_fs_struct.iteritems():
                if value["type"] == "file":
                    self.mkfile(alias, value["path"], value["mode"],
                                value["temporary"])
                else:
                    self.mkdir(alias, value["path"], value["mode"],
                               value["temporary"])
                    self.cd(alias)
                    self.load()
                    self.up()

    def snappy(self, root_binded=False):
        '''
        Creates structure by walking for current directory and subdirectories

        @param root_binded: All the resources of fs structure will be binded
        within one root if that parameter is True
        @type root_binded: `bool`
        '''

        def dir_cerator(long_path):
            head = re_url_head.search(long_path)
            tail = re_url_long_tail.search(long_path)
            if head:
                self.mkdir(head.group(0))
                self.cd(head.group(0))
                if tail:
                    dir_cerator(tail.group(0)[1:])
                self.up()

        def file_creator(long_path):
            head = re_url_head.search(long_path)
            tail = re_url_long_tail.search(long_path)
            if head:
                if tail:
                    self.cd(head.group(0))
                    file_creator(tail.group(0)[1:])
                else:
                    self.mkfile(head.group(0))
                self.up()

        for path, dirs, files in os.walk(self.prefix_path):
            for dir_entry in dirs:
                full_path = os.path.relpath(os.path.join(path, dir_entry),
                                            self.prefix_path)
                if root_binded:
                    self.mkdir(full_path)
                else:
                    dir_cerator(full_path)
            for file_entry in files:
                full_path = os.path.relpath(os.path.join(path, file_entry),
                                            self.prefix_path)
                if root_binded:
                    self.mkfile(full_path)
                else:
                    file_creator(full_path)

    def save_all(self, path=".fs-structure-full.json"):
        '''
        Save full file system structure to one file

        @param path: Path to the structure file
        @type path: `str`
        '''

        self.cd_root()
        fs_struct = dict()

        def decompose(current_fs_struct):
            for alias, value in self.current_directory.iteritems():
                current_fs_struct[alias] = \
                    {"path": os.path.relpath(value.path,
                                             self.root_directory.path),
                     "mode": value.mode,
                     "temporary": value.temporary}

                if isinstance(value, DirectoryObject):
                    current_fs_struct[alias]["resources"] = dict()
                    self.cd(alias)
                    decompose(current_fs_struct[alias]["resources"])
                    self.up()

        decompose(fs_struct)
        with self.open(path, "w") as f:
            f.write(unicode(json.dumps(fs_struct,
                                       indent=4,
                                       separators=(',', ':'),
                                       ensure_ascii=False)))

    def load_all(self, path=".fs-structure-full.json"):
        '''
        Load full system structure from one file

        @param path: Path to the structure file
        @type path: `str`
        '''

        self.cd_root()
        fs_struct = dict()

        def compose(current_fs_struct):
            for alias, value in current_fs_struct.iteritems():
                if "resources" in value:
                    self.mkdir(alias, value["path"], value["mode"],
                               value["temporary"])
                    self.cd(alias)
                    compose(current_fs_struct[alias]["resources"])
                    self.up()
                else:
                    self.mkfile(alias, value["path"], value["mode"],
                                value["temporary"])

        with self.open(path, "r") as f:
            fs_struct = json.load(f)
        compose(fs_struct)

    def save_hashsums(self, type="md5"):
        '''
        Save file's hashes to .json structure file

        @param type: Hashsum method
        @type type: `str`
        '''

        if self.exists(".fs-structure.json"):
            current_fs_struct = dict()
            with self.open(".fs-structure.json", "r") as f:
                current_fs_struct = json.load(f)

            if type in ["md5", "sha1"]:
                for alias, value in self.current_directory.iteritems():
                    if isinstance(value, FileObject):
                        current_fs_struct[alias][type] = getattr(value, type)()
                    else:
                        self.cd(alias)
                        self.save_hashsums(type)
                        self.up()

            with self.open(".fs-structure.json", "w") as f:
                f.write(unicode(json.dumps(current_fs_struct,
                                           indent=4,
                                           separators=(',', ':'),
                                           ensure_ascii=False)))

    def check_hashsums(self, type="md5", log_warnings=True, mismatch=[]):
        '''
        Compare current file hashes to saved in the .json structure file

        @param type: Hashsum method
        @type type: `str`
        @param log_warnings: Log warnings about mismatch
        @type log_warnings: `bool`
        @return: List of mismatches
        '''

        if self.exists(".fs-structure.json"):
            loaded_fs_struct = dict()
            with self.open(".fs-structure.json", "r") as f:
                loaded_fs_struct = json.load(f)

            if type in ["md5", "sha1"]:

                for alias, value in self.current_directory.iteritems():
                    if isinstance(value, FileObject):
                        if loaded_fs_struct[alias][type] != getattr(value,
                                                                    type)():
                            if log_warnings:
                                log.warning("Hashsum mismatch for {}".
                                            format(value.path))
                            mismatch.append(value)
                    else:
                        self.cd(alias)
                        self.check_hashsums(type, log_warnings, mismatch)
                        self.up()

            return mismatch
