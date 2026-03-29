from typing import Any

import nox
import nox_uv
from liblaf import nox_recipes as recipes
from liblaf.nox_recipes import Resolution

nox.options.default_venv_backend = "uv"
nox.options.reuse_existing_virtualenvs = True
nox.options.tags = ["test"]
PYPROJECT: dict[str, Any] = nox.project.load_toml("pyproject.toml")
PYTHON_VERSIONS: list[str] = nox.project.python_versions(PYPROJECT)


@nox_uv.session(reuse_venv=True, tags=["bench"], uv_groups=["test"], uv_quiet=True)
def bench(s: nox.Session) -> None:
    recipes.pytest_bench(s, suppress_no_test_exit_code=True)


@nox.session(python=PYTHON_VERSIONS, reuse_venv=True, tags=["test"])
@nox.parametrize(
    "resolution",
    [
        nox.param(Resolution.HIGHEST, id="highest", tags=["highest"]),
        nox.param(Resolution.LOWEST, id="lowest", tags=["lowest"]),
        nox.param(Resolution.LOWEST_DIRECT, id="lowest-direct", tags=["lowest-direct"]),
    ],
)
def test(s: nox.Session, resolution: Resolution | None) -> None:
    recipes.setup_uv(s, groups=["test"], resolution=resolution)
    recipes.pytest(s, suppress_no_test_exit_code=True)
