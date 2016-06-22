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
        @type path: L{str}
        @param parent: Parent resource
        @type parent: L{DirectoryObject}
        @param mode: Mode bits of file
        @type mode: L{int}
        @param temporary: Is this file has to be deleted when script is done?
        @type temporary: L{bool}
        '''

        self._parent = None
        self.parent = parent
        self._path = os.path.abspath(path)
        self.temporary = temporary
        self.file_name = re_url_tail.search(self.path).group(0)
        self.file_path = re_url_long_head.search(self.path).group(0)

        if os.path.exists(self.path):
            self.mode = mode
        else:
            self._mode = mode
            self.create()

    def __del__(self):
        if self.temporary and os.path.exists(self.path):
            self.remove()

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
        @type mode: L{int}
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
        @type dst: L{str}
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
        @type dst: L{str}
        @param same_parent: Is the new file has same parent?
        @type same_parent: L{bool}
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
        @type path: L{str}
        @param parent: Parent resource
        @type parent: L{DirectoryObject}
        @param mode: Mode bits of directory
        @type mode: L{int}
        @param temporary: Is this directory has to be deleted
        when script is done?
        @type temporary: L{bool}
        '''

        self._parent = None
        self.parent = parent
        self._path = os.path.abspath(path)
        self.temporary = temporary
        self.dir_name = re_url_tail.search(self.path).group(0)
        self.dir_path = re_url_long_head.search(self.path).group(0)
        self.resources = []

        if os.path.exists(self.path):
            self.mode = mode
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
        @type mode: L{int}
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
        @type dst: L{str}
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
        @type dst: L{str}
        @param same_parent: Is the new directory has same parent?
        @type same_parent: L{bool}
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

    # `pop` overwrites because of overwriting of `__getitem__` method such way
    # `pop` tries to get element by index, but here is accepts key instead
    def pop(self, idx):
        '''Return resource on "idx" index and delete it then'''

        self.resources[idx]._parent = None
        return self.resources.pop(idx)


class FSManager(object):
    default_aliases = ["Mercury", "Venus", "Earth", "Mars", "Jupiter",
                       "Saturn", "Uranus", "Neptune", "Plutone"]
    alias_n = {"file": 0, "dir": 0}

    def __init__(self, base_path="/tmp/resource-manager/", mode=0o700,
                 temporary=False, rand_prefix=False):
        '''
        Initialize ResourceManger within the prefix path

        @param base_path: Base path of the resources
        @type base_path: L{str}
        @param mode: Mode bits of directory
        @type mode: L{int}
        @param temporary: Is this FSManager has to be deleted
        with all the resources under it after script is done?
        @type temporary: L{bool}
        @param rand_prefix: Is the prefix have to be created randomly
        with tempfile?
        @type rand_prefix: L{bool}
        '''

        self.base_path = os.path.abspath(base_path)
        self.temporary = temporary
        DirectoryObject(self.base_path, mode)
        self.prefix_path = tempfile.mkdtemp(prefix=self.base_path + "/") \
            if rand_prefix else self.base_path
        self.resources = AliasedDirectoryObject(self.prefix_path, mode,
                                                temporary)
        self.current_directory = self.resources

    def __del__(self):
        if self.temporary and os.path.exists(self.prefix_path):
            self.remove()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.__del__()

    @staticmethod
    def _prepare(path):
        '''
        Pre-create row of the directories for resource

        @param path: Initial path. Tail - name of file/directory, head - path.
        @type path: L{str}
        '''

        prefix = re_url_long_head.search(path).group(0)
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
        @type alias: L{str}
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
        @type alias: L{str}
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
        @type alias: L{str}
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
        @type alias: L{str}
        '''

        if self.dir(alias) is not None:
            self.prefix_path = self.dir(alias).path
            self.current_directory = self.dir(alias)
        else:
            log.info("There is no such alias '{}'".format(alias))

    def back(self):
        '''Switch prefix path to parent'''

        if self.current_directory.parent:
            self.prefix_path = self.abspath(self.current_directory.parent.path)
            self.current_directory = self.current_directory.parent

    @contextmanager
    def open(self, alias, mode="r"):
        '''Open file at relative path'''

        if self.file(alias) is not None:
            try:
                f = open(self.file(alias).path, mode)
                yield f
                f.close()
            except IOError as exc:
                log.error("Can't open file")
                raise exc

    def remove(self):
        '''CAUTION: Remove all the resources under prefix path'''

        try:
            shutil.rmtree(self.resources.path)
        except IOError as exc:
            log.error("Can't remove prefix path")
            raise exc

    def exists(self, path=""):
        '''
        Check if resource exists at relative path

        @param path: Relative path
        @type path: L{str}
        '''

        return os.path.exists(self.abspath(path))

    def abspath(self, path=""):
        '''
        Return absolute path instead of relative one

        @param path: Relative or absolute path
        @type path: L{str}
        '''
        if path.startswith("/"):
            return os.path.abspath(path)
        else:
            return os.path.abspath(os.path.join(self.prefix_path, path))

    def mkfile(self, alias=None, path=None, mode=0o600, temporary=False):
        '''
        Make the file within prefix path

        @param alias: Alias name of the file to make
        @type alias: L{str}
        @param path: Path with the file name included
        @type path: L{str}
        @param mode: Mode bits of file
        @type mode: L{int}
        '''

        if alias is None:
            _alias = self.generate_alias("file")
        else:
            _alias = alias
        if path is None:
            _path = _alias
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

    def mkdir(self, alias=None, path=None, mode=0o700, temporary=False):
        '''
        Make the directory within prefix path

        @param alias: Alias name of the directory to make
        @type alias: L{str}
        @param path: Path with the directory name included
        @type path: L{str}
        @param mode: Mode bits of directory
        @type mode: L{int}
        '''

        if alias is None:
            _alias = self.generate_alias("dir")
        else:
            _alias = alias
        if path is None:
            _path = _alias
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

    def chmod(self, alias, mode):
        '''
        Change mode bits of the resource

        @param alias: Alias name of the resource
        @type alias: L{str}
        @param mode: Mode bits of the resource
        @type mode: L{int}
        '''

        if self.resource(alias) is not None:
            self.current_directory[alias].chmod(mode)

    def rm(self, alias):
        '''
        Remove the resource

        @param alias: Alias name of the resource to remove
        @type alias: L{str}
        '''

        if self.resource(alias) is not None:
            self.current_directory[alias].remove()
            del self.current_directory[alias]

    def cp(self, alias, dst):
        '''
        Make a copy of resource

        @param alias: Alias name of the resource to copy
        @type alias: L{str}
        @param dst: Destination path with the resource name included
        @type dst: L{str}
        '''

        if self.resource(alias) is not None:
            self._prepare(self.abspath(dst))
            self.current_directory[alias].copy(self.abspath(dst))

    def mv(self, alias, dst):
        '''
        Move the resource

        @param alias: Alias name of the resource to move
        @type alias: L{str}
        @param dst: Destination path with the resource name included
        @type dst: L{str}
        '''

        if self.resource(alias) is not None:
            self._prepare(self.abspath(dst))
            self.current_directory[alias].move(self.abspath(dst))

    def ls(self):
        '''List all the resources under prefix'''

        if not self.current_directory:
            return "No one resource has been created yet"

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
            res += "{0}{3}{4}{2}{1}\n".format(key, val.path, dash * 5,
                                              tabs, type)
        print res

    def generate_alias(self, type):
        '''
        Generate alias

        @param type: Type of the alias (file/dir)
        @type type: L{str}
        @return: Generated alias
        '''

        x = self.alias_n[type] / len(self.default_aliases)
        idx = self.alias_n[type] - x * len(self.default_aliases)

        new_alias = self.default_aliases[idx]
        if type == "dir":
            new_alias += "Dir"
        elif type == "file":
            new_alias += "File"
        if x:
            new_alias += str(x)
        self.alias_n[type] += 1

        return new_alias
