from __future__ import annotations

import re
from pathlib import Path

import pytest
import yaml

REPOSITORY_ROOT = Path(__file__).parents[1]
SKILL_FILES = tuple(sorted(REPOSITORY_ROOT.glob("*/SKILL.md")))
SKILL_NAME_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


def _frontmatter(skill_file: Path) -> dict[str, object]:
    contents = skill_file.read_text(encoding="utf-8")
    assert contents.startswith("---\n"), f"{skill_file} has no YAML frontmatter"

    try:
        frontmatter_text, _body = contents[4:].split("\n---\n", maxsplit=1)
    except ValueError as exc:
        raise AssertionError(f"{skill_file} has unclosed YAML frontmatter") from exc

    metadata = yaml.safe_load(frontmatter_text)
    assert isinstance(metadata, dict), f"{skill_file} frontmatter must be a mapping"
    return metadata


def test_repository_contains_skills() -> None:
    assert SKILL_FILES, "repository must contain at least one skill"


@pytest.mark.parametrize("skill_file", SKILL_FILES, ids=lambda path: path.parent.name)
def test_skill_metadata_is_valid(skill_file: Path) -> None:
    metadata = _frontmatter(skill_file)
    name = metadata.get("name")
    description = metadata.get("description")

    assert name == skill_file.parent.name
    assert isinstance(name, str) and len(name) <= 64
    assert SKILL_NAME_PATTERN.fullmatch(name)
    assert isinstance(description, str) and description.strip()
