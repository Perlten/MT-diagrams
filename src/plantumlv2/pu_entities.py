from src.core.bt_module import BTModule
from src.plantumlv2.utils import get_pu_package_name_from_bt_package
from enum import Enum


class EntityState(str, Enum):
    DELETED = "#Red"
    NEUTRAL = ""
    CREATED = "#Green"


class PuPackage:
    name = ""
    state: EntityState = EntityState.NEUTRAL
    pu_dependency_list: list["PuDependency"] = None
    bt_package: BTModule = None

    def __init__(self, bt_package: BTModule) -> None:
        self.pu_dependency_list = []
        # TODO: allow name to no be path
        self.name = get_pu_package_name_from_bt_package(bt_package)
        self.bt_package = bt_package

    @property
    def path(self):
        return get_pu_package_name_from_bt_package(self.bt_package)

    def setup_dependencies(self, pu_package_map: dict[str, "PuPackage"]):
        bt_dependencies = self.bt_package.get_module_dependencies()
        for bt_package_dependency in bt_dependencies:
            pu_path = get_pu_package_name_from_bt_package(
                bt_package_dependency
            )
            pu_package_dependency = pu_package_map[pu_path]
            self.pu_dependency_list.append(
                PuDependency(
                    self,
                    pu_package_dependency,
                    self.bt_package,
                    bt_package_dependency,
                )
            )

    def render_package(self) -> str:
        return f'package "{self.name}" {self.state}'

    def render_dependency(self) -> str:
        return "\n".join(
            [
                pu_dependency.render()
                for pu_dependency in self.pu_dependency_list
            ]
        )

    def filter_excess_packages_dependencies(
        self, used_packages: set["PuPackage"]
    ):
        filtered_dependency_list: list[PuDependency] = []

        for dependency in self.pu_dependency_list:
            if dependency.to_package in used_packages:
                filtered_dependency_list.append(dependency)
        self.pu_dependency_list = filtered_dependency_list

    def get_dependency_map(self) -> dict[str, "PuDependency"]:
        return {
            dependency.to_package.path: dependency
            for dependency in self.pu_dependency_list
        }


class PuDependency:
    state: EntityState = EntityState.NEUTRAL

    from_package: PuPackage = None
    to_package: PuPackage = None

    from_bt_package: BTModule = None
    to_bt_package: BTModule = None

    dependency_count = 0

    def __init__(
        self,
        from_package: PuPackage,
        to_package: PuPackage,
        from_bt_package: BTModule,
        to_bt_package: BTModule,
    ) -> None:
        self.from_package = from_package
        self.to_package = to_package
        self.from_bt_package = from_bt_package
        self.to_bt_package = to_bt_package
        self.dependency_count = self.from_bt_package.get_dependency_count(
            self.to_bt_package
        )

    def render(self) -> str:
        from_name = self.from_package.name
        to_name = self.to_package.name
        return f'"{from_name}"-->"{to_name}" {self.state}: {self.dependency_count}'
