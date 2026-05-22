"""Load and run Compiled_AFL_Papers supplementary scripts (import-safe main())."""
import importlib.util
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
_AFL_COMPILED_CANDIDATES = (
    _REPO_ROOT / "Part_III_AFL_Biology_and_Medicine" / "notebooks",
    _REPO_ROOT / "Part_III_AFL_Biology_and_Medicine" / "notebooks",
)


def supplementary_script_path(paper: int) -> Path:
    if paper < 1 or paper > 20:
        raise ValueError("paper must be between 1 and 20 inclusive")
    name = f"supplementary_afl_{paper:02d}.py"
    for folder in _AFL_COMPILED_CANDIDATES:
        p = folder / name
        if p.is_file():
            return p
    return _AFL_COMPILED_CANDIDATES[0] / name


def run_afl_paper(paper: int) -> int:
    """Execute supplementary_afl_{paper}.py main(); return its exit code (0 default)."""
    path = supplementary_script_path(paper)
    if not path.is_file():
        raise FileNotFoundError(path)

    mod_name = f"cdfd_afl_supplementary_{paper}"
    spec = importlib.util.spec_from_file_location(mod_name, path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Cannot load {path}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)

    main = getattr(mod, "main", None)
    if main is None or not callable(main):
        raise AttributeError(f"{path.name} must define callable main()")

    rc = main()
    return 0 if rc is None else int(rc)
