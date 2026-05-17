"""Markdown / frontmatter helpers for the knowledge hub."""

import re
from pathlib import Path
from typing import Optional

import frontmatter


_VALID_LEVELS = ("beginner", "intermediate", "advanced")


def slugify(text: str) -> str:
    """URL-slug a free-form string (lowercase, hyphenated, ascii-ish)."""
    text = text.lower().strip()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_]+", "-", text)
    text = re.sub(r"-+", "-", text)
    return text.strip("-")


def extract_first_paragraph(content: str) -> str:
    """Return the first non-heading, non-code paragraph (≤300 chars).

    Tracks fenced-code-block state so lines *inside* a ```...``` block are
    skipped, not just the fences themselves.
    """
    in_code = False
    for line in content.splitlines():
        stripped = line.strip()
        if stripped.startswith("```"):
            in_code = not in_code
            continue
        if in_code or not stripped or stripped.startswith("#"):
            continue
        clean = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", stripped)
        clean = re.sub(r"[*_`~]", "", clean)
        return clean[:300]
    return ""


def parse_note_file(file_path: Path) -> dict:
    """Parse a markdown file with YAML frontmatter into a dict of fields.

    Frontmatter fields win; sane defaults are derived from the file name and
    body when fields are missing or malformed.
    """
    post = frontmatter.load(str(file_path))

    slug = str(post.get("slug", "") or slugify(file_path.stem))
    title = str(
        post.get("title", "") or file_path.stem.replace("-", " ").title()
    )
    content: str = post.content or ""

    tags = post.get("tags", [])
    if isinstance(tags, str):
        tags = [t.strip() for t in tags.split(",") if t.strip()]
    elif not isinstance(tags, list):
        tags = []

    summary = str(post.get("summary", "") or extract_first_paragraph(content))
    visibility = str(post.get("visibility", "public"))
    word_count = len(content.split())
    read_time = max(1, word_count // 200)

    level_raw = str(post.get("level", "beginner")).lower().strip()
    level = level_raw if level_raw in _VALID_LEVELS else "beginner"

    return {
        "title": title,
        "slug": slug,
        "tags": tags,
        "summary": summary,
        "visibility": visibility,
        "level": level,
        "content": content,
        "word_count": word_count,
        "read_time": read_time,
        "created_at": post.get("created_at", None),
    }


def build_frontmatter_string(
    title: str,
    slug: str,
    tags: list,
    visibility: str,
    summary: Optional[str],
    content: str,
    level: str = "beginner",
) -> str:
    """Render a markdown file string (YAML frontmatter + body)."""
    tags_yaml = ", ".join(f'"{t}"' for t in tags) if tags else ""
    summary_line = f'summary: "{summary}"' if summary else 'summary: ""'
    return (
        f"---\n"
        f'title: "{title}"\n'
        f"slug: {slug}\n"
        f"{summary_line}\n"
        f"tags: [{tags_yaml}]\n"
        f"visibility: {visibility}\n"
        f"level: {level}\n"
        f"---\n\n"
        f"{content}\n"
    )
