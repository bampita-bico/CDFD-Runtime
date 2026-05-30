"""Shared runtime-session model for CLI, web app, reports, and tests."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping

from runtime.diagnostics import utc_timestamp


@dataclass(frozen=True)
class RuntimeSession:
    """Minimal persistent run identity shared across CDFD surfaces."""

    result: Mapping[str, Any]
    command: str
    label: str
    created_utc: str

    @classmethod
    def from_result(cls, result: Mapping[str, Any], *, label: str | None = None) -> "RuntimeSession":
        provenance = result.get("provenance", {}) if isinstance(result, Mapping) else {}
        command = str(provenance.get("command") or label or result.get("kind", "run"))
        return cls(
            result=result,
            command=command,
            label=label or str(result.get("kind") or "run"),
            created_utc=utc_timestamp(),
        )

    def manifest(
        self,
        *,
        run_dir: str | Path,
        result_path: str | Path,
        report_paths: Mapping[str, str | Path],
        plots_dir: str | Path,
    ) -> dict[str, Any]:
        finite = self.result.get("finite_audit", {}) if isinstance(self.result, Mapping) else {}
        return {
            "run_dir": str(run_dir),
            "result": str(result_path),
            "reports": {name: str(path) for name, path in report_paths.items()},
            "plots_dir": str(plots_dir),
            "kind": self.result.get("kind") if isinstance(self.result, Mapping) else None,
            "status": self.result.get("status") if isinstance(self.result, Mapping) else None,
            "finite_audit": finite,
            "command": self.command,
            "label": self.label,
            "timestamp_utc": self.created_utc,
            "provenance": self.result.get("provenance", {}) if isinstance(self.result, Mapping) else {},
        }
