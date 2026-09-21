#!/usr/bin/env python3
"""Create one reviewable alignment Skill candidate in the shared drop directory."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import os
from pathlib import Path
import sys
import unicodedata


DEFAULT_DROP_DIR = Path("/home/public/zjj/skills_pr")
DROP_DIR_ENV = "DEPLOY_SKILLS_CANDIDATE_DIR"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Create a uniquely named alignment Skill candidate."
    )
    parser.add_argument("--task", required=True, help="Short summary of the task")
    parser.add_argument(
        "--skill", required=True, help="Short summary of the newly discovered skill"
    )
    parser.add_argument(
        "--evidence-level",
        choices=("observed", "validated", "repeated"),
        default="observed",
    )
    parser.add_argument(
        "--drop-dir",
        type=Path,
        help=f"Override the shared directory (or set {DROP_DIR_ENV})",
    )
    return parser.parse_args()


def normalize_summary(value: str, field: str) -> str:
    summary = " ".join(value.split())
    if not summary:
        raise ValueError(f"{field} must contain visible characters")
    return summary


def truncate_utf8(value: str, byte_limit: int) -> str:
    encoded = value.encode("utf-8")
    if len(encoded) <= byte_limit:
        return value
    encoded = encoded[:byte_limit]
    while encoded:
        try:
            return encoded.decode("utf-8")
        except UnicodeDecodeError:
            encoded = encoded[:-1]
    return ""


def filename_part(value: str, fallback: str) -> str:
    normalized = unicodedata.normalize("NFKC", value)
    result: list[str] = []
    separator_pending = False
    for character in normalized:
        category = unicodedata.category(character)
        if character.isalnum():
            if separator_pending and result:
                result.append("-")
            result.append(character)
            separator_pending = False
        elif character.isspace() or category.startswith(("P", "S")):
            separator_pending = True
    slug = "".join(result).strip("-") or fallback
    return truncate_utf8(slug, 72).rstrip("-") or fallback


def config_drop_dir() -> Path | None:
    deploy_root = Path(__file__).resolve().parents[4]
    config_file = deploy_root / "candidate-drop.conf"
    if not config_file.is_file():
        return None
    values = [
        line.strip()
        for line in config_file.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    ]
    if len(values) != 1:
        raise ValueError(f"{config_file} must contain exactly one directory path")
    configured = Path(values[0]).expanduser()
    if not configured.is_absolute():
        raise ValueError(f"candidate drop directory must be absolute: {configured}")
    return configured


def resolve_drop_dir(override: Path | None) -> Path:
    if override is not None:
        candidate = override.expanduser()
    elif os.environ.get(DROP_DIR_ENV):
        candidate = Path(os.environ[DROP_DIR_ENV]).expanduser()
    else:
        candidate = config_drop_dir() or DEFAULT_DROP_DIR
    if not candidate.is_absolute():
        raise ValueError(f"candidate drop directory must be absolute: {candidate}")
    return candidate


def candidate_content(
    task: str, skill: str, created_at: str, evidence_level: str
) -> str:
    return f"""# Alignment Skill Candidate

- task: {task}
- new_skill: {skill}
- created_at: {created_at}
- status: candidate
- evidence_level: {evidence_level}
- candidate_key: <proposed-target/reusable-invariant-slug>
- proposed_action: <new-skill|skill-extension|routing-trigger|reference|script>
- proposed_target: <formal skill or new skill name>
- formal_skills_checked: <comma-separated names>
- related_candidates: <comma-separated filenames or none>

## Trigger

<When this method should be used.>

## Not Applicable

<When this method should not be used.>

## Reusable Problem

<Problem stated without project-specific names or values.>

## Reusable Method

1. <Step>
2. <Step>
3. <Validation or escalation step>

## Cheapest Discriminating Check

<The lowest-cost check that distinguishes the relevant hypotheses.>

## Evidence

- task/workspace: <sanitized context>
- code/config evidence: <relative paths or symbols>
- command/experiment: <sanitized command or experiment>
- observed result: <measured result>
- validation: <what passed, failed, or remains unverified>

## General Rule vs Project Facts

- general rule: <candidate Skill content>
- project facts: <specific names, paths, parameters, and one-off values>

## Promotion Requirements

- [ ] <additional validation or cleanup>
"""


def create_candidate(
    drop_dir: Path, task: str, skill: str, evidence_level: str
) -> Path:
    if not drop_dir.exists():
        raise FileNotFoundError(f"candidate drop directory does not exist: {drop_dir}")
    if not drop_dir.is_dir():
        raise NotADirectoryError(f"candidate drop path is not a directory: {drop_dir}")
    if not os.access(drop_dir, os.W_OK):
        raise PermissionError(f"candidate drop directory is not writable: {drop_dir}")

    now = datetime.now(timezone.utc)
    timestamp = now.strftime("%Y%m%dT%H%M%SZ")
    created_at = now.isoformat(timespec="seconds").replace("+00:00", "Z")
    stem = (
        f"{filename_part(task, 'task')}__"
        f"{filename_part(skill, 'skill')}__{timestamp}"
    )
    content = candidate_content(task, skill, created_at, evidence_level)

    for sequence in range(1000):
        suffix = "" if sequence == 0 else f"__{sequence:02d}"
        destination = drop_dir / f"{stem}{suffix}.md"
        try:
            descriptor = os.open(
                destination, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o644
            )
        except FileExistsError:
            continue
        os.fchmod(descriptor, 0o644)
        with os.fdopen(descriptor, "w", encoding="utf-8") as output:
            output.write(content)
        return destination
    raise FileExistsError(f"too many candidates share the same name: {stem}")


def main() -> int:
    args = parse_args()
    try:
        task = normalize_summary(args.task, "task")
        skill = normalize_summary(args.skill, "skill")
        destination = create_candidate(
            resolve_drop_dir(args.drop_dir), task, skill, args.evidence_level
        )
    except (OSError, ValueError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print(destination)
    return 0

if __name__ == "__main__":
    raise SystemExit(main())

