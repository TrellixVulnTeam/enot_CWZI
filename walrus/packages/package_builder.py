from walrus.compiler.compiler_factory import get_compiler
from walrus.global_properties import WalrusGlobalProperties
from walrus.packages.config import config
from walrus.packages.config.config_factory import read_project
from walrus.packages.package import Package


class Builder:
    path = ""  # path in system of building project
    system_config = None  # system configuration
    packages = {}  # all project's packages

    def __init__(self, path: str):
        super().__init__()
        self.system_config = WalrusGlobalProperties()
        self.path = path

    def walrusify(self):
        project_config = read_project(self.path)
        if project_config.need_walrusify():
            package_content = project_config.get_valrus_package()
            config.write_walrus_file(self.path, package_content)

    # Parse package config, download missing deps to /tmp
    def populate(self):
        first_level = Package.frompath(self.path)
        self.__populate_deps(first_level.deps)
        return first_level

    def __populate_deps(self, deps):  # TODO add an ability to operate with deps in parallel
        for name, dep in deps.items():
            if name not in self.packages:
                print('new dep: ' + name)
            if self.system_config.cache.exists(dep):
                self.system_config.cache.get_package(dep)
            else:
                self.system_config.cache.fetch_package(dep)
            self.__populate_deps(dep.deps)

    # Build package, copy to cache, link with project
    def build_tree(self, package: Package):
        # TODO check if package.config.path exists
        if self.system_config.cache.exists(package):
            return True
        for dep in package.list_deps():
            print(self.system_config.cache.exists(dep))
            if not self.system_config.cache.exists(dep):  # if package not in cache - build and add to cache
                if not self.build_tree(dep):
                    raise RuntimeError('Can\'t built dep ' + dep.get_name())
            self.system_config.cache.link_package(dep, package.config.path)
        compiler = get_compiler(self.system_config, package.config)
        res = compiler.compile()
        if res:
            self.system_config.cache.add_package(package)
        return res
