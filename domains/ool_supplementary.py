"""Load and run Origins_of_life_series supplementary scripts (import-safe main())."""
import importlib.util
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
_OOL_SCRIPT_DIRS = (
    _REPO_ROOT / "Part_II_Origins_of_Life_and_Tri_Regime_Bioenergetics" / "scripts",
    _REPO_ROOT / "Part_II_Origins_of_Life_and_Tri_Regime_Bioenergetics" / "scripts",
    _REPO_ROOT / "Part_II_Origins_of_Life_and_Tri_Regime_Bioenergetics" / "scripts",
)
OOL_PAPER_MAX = 11


def supplementary_script_path(paper: int) -> Path:
    if paper < 1 or paper > OOL_PAPER_MAX:
        raise ValueError(f"paper must be between 1 and {OOL_PAPER_MAX} inclusive")
    name = f"supplementary_ool_{paper:02d}.py"
    for folder in _OOL_SCRIPT_DIRS:
        path = folder / name
        if path.is_file():
            return path
    return _OOL_SCRIPT_DIRS[0] / name


def run_ool_paper(paper: int) -> int:
    """Execute supplementary_ool_{paper}.py main(); return its exit code (0 default)."""
    path = supplementary_script_path(paper)
    if not path.is_file():
        raise FileNotFoundError(path)

    mod_name = f"cdfd_ool_supplementary_{paper}"
    spec = importlib.util.spec_from_file_location(mod_name, path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Cannot load {path}")
    # Allow supplementary scripts to import local helpers in their own folder.
    ool_dir = str(path.parent)
    if ool_dir not in sys.path:
        sys.path.insert(0, ool_dir)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)

    main = getattr(mod, "main", None)
    if main is None or not callable(main):
        # Older restored OOL scripts execute their demo at import time.
        return 0

    rc = main()
    return 0 if rc is None else int(rc)
