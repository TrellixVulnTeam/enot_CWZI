import json
from os.path import join
from tarfile import TarFile

from coon.action.prebuild import action_factory

from coon.compiler.compiler_type import Compiler
from coon.packages.config.config import ConfigFile
from coon.utils.file_utils import read_file


class CoonConfig(ConfigFile):
    def __init__(self, config: dict, url=None):
        super().__init__()
        self._name = config['name']
        self._drop_unknown = config.get('drop_unknown_deps', True)
        self._with_source = config.get('with_source', True)
        self.__parse_prebuild(config)
        self.__parse_build_vars(config)
        self.__parse_deps(config.get('deps', {}))
        self._conf_vsn = config.get('app_vsn', None)
        self._git_vsn = config.get('tag', None)
        self.set_url(config.get('url', url))

    @classmethod
    def from_path(cls, path: str, url=None) -> 'CoonConfig':
        content = read_file(join(path, 'coonfig.json'))
        return cls(json.loads(content), url=url)

    @classmethod
    def from_package(cls, package: TarFile, url: str) -> 'CoonConfig':
        f = package.extractfile('coonfig.json')
        content = f.read()
        return cls(json.loads(content.decode('utf-8')), url=url)

    def need_coonsify(self):
        return False

    def get_compiler(self):
        return Compiler.COON

    def __parse_deps(self, deps: list):
        for dep in deps:
            name = dep['name']
            self.deps[name] = (dep['url'], dep['tag'])

    def __parse_prebuild(self, parsed):
        for step in parsed.get('prebuild', []):
            [(action_type, params)] = step.items()
            self.prebuild.append(action_factory.get_action(action_type, params))

    def __parse_build_vars(self, parsed):
        self._build_vars = parsed.get('build_vars', [])
        self._c_build_vars = parsed.get('c_build_vars', [])
