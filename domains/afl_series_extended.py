"""Load and run AFL supplementary scripts for Earth / Engineered / Socioeconomic LaTeX series."""
import importlib.util
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]

_SERIES = {
    "earth": (
        _REPO_ROOT / "Part_IV_Universal_AFL_Synthesis" / "Part_A_Earth_Systems" / "notebooks",
        12,
        "supplementary_earth_{n:02d}.py",
    ),
    "engineered": (
        _REPO_ROOT / "Part_IV_Universal_AFL_Synthesis" / "Part_B_Engineered_Systems" / "notebooks",
        12,
        "supplementary_eng_{n:02d}.py",
    ),
    "socioeconomic": (
        _REPO_ROOT / "Part_IV_Universal_AFL_Synthesis" / "Part_C_Socioeconomic_Systems" / "notebooks",
        10,
        "supplementary_soc_{n:02d}.py",
    ),
}


def series_keys() -> tuple[str, ...]:
    return tuple(sorted(_SERIES.keys()))


def series_paper_count(series: str) -> int:
    key = series.strip().lower()
    if key not in _SERIES:
        raise ValueError(f"unknown series {series!r}; expected one of {series_keys()}")
    return _SERIES[key][1]


def series_script_path(series: str, paper: int) -> Path:
    key = series.strip().lower()
    if key not in _SERIES:
        raise ValueError(f"unknown series {series!r}; expected one of {series_keys()}")
    folder, max_n, pattern = _SERIES[key]
    if paper < 1 or paper > max_n:
        raise ValueError(f"paper must be between 1 and {max_n} for series {key!r}")
    return folder / pattern.format(n=paper)


def run_afl_series_paper(series: str, paper: int) -> int:
    path = series_script_path(series, paper)
    if not path.is_file():
        raise FileNotFoundError(path)

    key = series.strip().lower()
    mod_name = f"cdfd_afl_series_{key}_{paper}"
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


def parse_afl_ext(spec: str) -> tuple[str, int]:
    """Parse ``earth:3`` / ``engineered:12`` style selector."""
    parts = spec.strip().split(":")
    if len(parts) != 2:
        raise ValueError("expected SERIES:PAPER, e.g. earth:1")
    series, paper_s = parts[0].strip().lower(), parts[1].strip()
    try:
        paper = int(paper_s)
    except ValueError as e:
        raise ValueError(f"paper must be an integer, got {paper_s!r}") from e
    return series, paper
