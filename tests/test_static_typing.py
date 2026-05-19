from __future__ import annotations

import subprocess
import sys
from pathlib import Path

PROJECT_ROOT: Path = Path(__file__).resolve().parents[1]
POSITIVE_STATIC_TYPING_FILE: Path = (
    PROJECT_ROOT / "tests" / "static_typing" / "tuple_type_preservation_positive.py"
)
NEGATIVE_STATIC_TYPING_FILE: Path = (
    PROJECT_ROOT
    / "tests"
    / "static_typing_negative"
    / "tuple_type_preservation_negative.py"
)


def run_command(command_arguments: list[str]) -> subprocess.CompletedProcess[str]:
    completed_process: subprocess.CompletedProcess[str] = subprocess.run(
        command_arguments,
        cwd=PROJECT_ROOT,
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    return completed_process


def test_mypy_keeps_exact_type_inside_reduce_tuple() -> None:
    completed_process: subprocess.CompletedProcess[str] = run_command(
        [
            sys.executable,
            "-m",
            "mypy",
            str(POSITIVE_STATIC_TYPING_FILE),
        ]
    )

    assert completed_process.returncode == 0, completed_process.stdout


def test_pyright_keeps_exact_type_inside_reduce_tuple() -> None:
    completed_process: subprocess.CompletedProcess[str] = run_command(
        [
            sys.executable,
            "-m",
            "pyright",
            str(POSITIVE_STATIC_TYPING_FILE),
        ]
    )

    assert completed_process.returncode == 0, completed_process.stdout


def write_negative_static_typing_case(tmp_path: Path) -> Path:
    copied_static_typing_file: Path = tmp_path / NEGATIVE_STATIC_TYPING_FILE.name
    negative_static_typing_source: str = NEGATIVE_STATIC_TYPING_FILE.read_text(
        encoding="utf-8",
    )
    copied_static_typing_file.write_text(
        negative_static_typing_source,
        encoding="utf-8",
    )
    return copied_static_typing_file


def test_mypy_rejects_cross_type_assignment_from_reduce_tuple(tmp_path: Path) -> None:
    copied_static_typing_file: Path = write_negative_static_typing_case(tmp_path)

    completed_process: subprocess.CompletedProcess[str] = run_command(
        [
            sys.executable,
            "-m",
            "mypy",
            str(copied_static_typing_file),
        ]
    )

    assert completed_process.returncode != 0
    assert "Incompatible types" in completed_process.stdout


def test_pyright_rejects_wrong_type_from_reduce_tuple(
    tmp_path: Path,
) -> None:
    copied_static_typing_file: Path = write_negative_static_typing_case(tmp_path)

    completed_process: subprocess.CompletedProcess[str] = run_command(
        [
            sys.executable,
            "-m",
            "pyright",
            str(copied_static_typing_file),
        ]
    )

    assert completed_process.returncode != 0
    assert "is not assignable" in completed_process.stdout
