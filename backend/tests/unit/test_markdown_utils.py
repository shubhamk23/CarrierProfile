"""Unit tests for app.knowledge.markdown_utils."""

import pytest

from app.knowledge.markdown_utils import (
    build_frontmatter_string,
    extract_first_paragraph,
    parse_note_file,
    slugify,
)

pytestmark = pytest.mark.unit


class TestSlugify:
    def test_lowercases_and_hyphenates(self):
        assert slugify("Hello World") == "hello-world"

    def test_strips_special_characters(self):
        assert slugify("Attention!!!") == "attention"

    def test_collapses_whitespace_and_underscores(self):
        assert slugify("  Foo   bar___baz  ") == "foo-bar-baz"

    def test_strips_leading_trailing_hyphens(self):
        assert slugify("--lead-trail--") == "lead-trail"

    def test_empty_string_safe(self):
        assert slugify("") == ""


class TestExtractFirstParagraph:
    def test_skips_headings_and_codeblocks(self):
        body = "# Heading\n\n```python\ncode\n```\n\nThis is the first real line."
        assert extract_first_paragraph(body) == "This is the first real line."

    def test_strips_inline_markdown(self):
        body = "See **bold** and `code` and [a link](https://example.com)."
        out = extract_first_paragraph(body)
        assert "**" not in out
        assert "`" not in out
        assert "a link" in out
        assert "https://example.com" not in out

    def test_caps_to_300_chars(self):
        body = "x" * 1000
        assert len(extract_first_paragraph(body)) == 300

    def test_returns_empty_for_only_headings(self):
        assert extract_first_paragraph("# only heading\n## another") == ""


class TestParseNoteFile:
    def test_happy_path(self, tmp_path):
        path = tmp_path / "demo.md"
        path.write_text(
            '---\n'
            'title: "Demo"\n'
            'slug: demo\n'
            'summary: "A short summary"\n'
            'tags: ["a", "b"]\n'
            'visibility: public\n'
            'level: advanced\n'
            '---\n\n'
            'This is the body.\n'
        )
        parsed = parse_note_file(path)
        assert parsed["title"] == "Demo"
        assert parsed["slug"] == "demo"
        assert parsed["summary"] == "A short summary"
        assert parsed["tags"] == ["a", "b"]
        assert parsed["visibility"] == "public"
        assert parsed["level"] == "advanced"
        assert "body" in parsed["content"]
        assert parsed["word_count"] == 4

    def test_derives_slug_and_title_from_filename(self, tmp_path):
        path = tmp_path / "my-cool-note.md"
        path.write_text("---\n---\nbody\n")
        parsed = parse_note_file(path)
        assert parsed["slug"] == "my-cool-note"
        assert parsed["title"] == "My Cool Note"

    def test_tags_as_comma_string_split(self, tmp_path):
        path = tmp_path / "x.md"
        path.write_text('---\ntags: "a, b, c"\n---\nhello\n')
        parsed = parse_note_file(path)
        assert parsed["tags"] == ["a", "b", "c"]

    def test_unknown_level_falls_back_to_beginner(self, tmp_path):
        path = tmp_path / "x.md"
        path.write_text('---\nlevel: "wizard"\n---\nhello\n')
        assert parse_note_file(path)["level"] == "beginner"

    def test_derives_summary_from_body_when_missing(self, tmp_path):
        path = tmp_path / "x.md"
        path.write_text(
            '---\n---\n# Heading\n\nThis is the first real sentence.\n'
        )
        parsed = parse_note_file(path)
        assert "first real sentence" in parsed["summary"]

    def test_read_time_minimum_one_minute(self, tmp_path):
        path = tmp_path / "x.md"
        path.write_text("---\n---\nshort\n")
        assert parse_note_file(path)["read_time"] == 1


class TestBuildFrontmatterString:
    def test_round_trips_through_parse(self, tmp_path):
        content = "## Body\n\nLine one. Line two."
        rendered = build_frontmatter_string(
            title="Round trip",
            slug="round-trip",
            tags=["a", "b"],
            visibility="public",
            summary="A summary",
            content=content,
            level="intermediate",
        )
        path = tmp_path / "round.md"
        path.write_text(rendered)
        parsed = parse_note_file(path)
        assert parsed["title"] == "Round trip"
        assert parsed["slug"] == "round-trip"
        assert parsed["tags"] == ["a", "b"]
        assert parsed["visibility"] == "public"
        assert parsed["level"] == "intermediate"
        assert "Line one" in parsed["content"]

    def test_empty_tags_renders_empty_list(self):
        out = build_frontmatter_string(
            title="t",
            slug="t",
            tags=[],
            visibility="public",
            summary=None,
            content="body",
        )
        assert "tags: []" in out
        assert 'summary: ""' in out
