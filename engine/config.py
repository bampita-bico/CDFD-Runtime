import os

# ── Profile selection ─────────────────────────────────────────────────────────
# local — dev default | lowmem — T420-class (6GB): small grids, single worker
# cloud — large grids, optional Ray/GPU via env flags
PROFILE = os.environ.get("ENGINE_PROFILE", "local")

# ── Grid defaults ─────────────────────────────────────────────────────────────
if PROFILE == "cloud":
    DEFAULT_NX = 512
    DEFAULT_NY = 512
elif PROFILE == "lowmem":
    DEFAULT_NX = 16
    DEFAULT_NY = 16
else:
    DEFAULT_NX = 32
    DEFAULT_NY = 32

# ── Time step ─────────────────────────────────────────────────────────────────
DEFAULT_DT = float(os.environ.get("ENGINE_DT", "0.01"))

# ── AFL tensor defaults ───────────────────────────────────────────────────────
DEFAULT_ALPHA = 0.1
DEFAULT_BETA  = 0.05
DEFAULT_GAMMA = 0.1

# ── History rolling window ────────────────────────────────────────────────────
# Keeps only the last N snapshots in state.history to prevent OOM on long runs.
_DEFAULT_HISTORY = "40" if PROFILE == "lowmem" else "100"
HISTORY_WINDOW = int(os.environ.get("ENGINE_HISTORY_WINDOW", _DEFAULT_HISTORY))

# ── Parallel runtime ──────────────────────────────────────────────────────────
# cloud profile: Ray across all available cores; local/lowmem: thread pool only
USE_RAY = (
    PROFILE == "cloud"
    and os.environ.get("ENGINE_USE_RAY", "1") == "1"
)
_MAX_DEFAULT = "4" if PROFILE == "cloud" else ("1" if PROFILE == "lowmem" else "2")
MAX_WORKERS = int(os.environ.get("ENGINE_MAX_WORKERS", _MAX_DEFAULT))

# ── GPU ───────────────────────────────────────────────────────────────────────
USE_GPU = os.environ.get("ENGINE_USE_GPU", "0") == "1"

# ── AI module ─────────────────────────────────────────────────────────────────
USE_AI = False
AI_TIMEOUT = 5

# ── Logging ───────────────────────────────────────────────────────────────────
LOG_FAILURES = True
