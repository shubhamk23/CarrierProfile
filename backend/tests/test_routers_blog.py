"""Tests for the /api/blog router (app/routers/blog.py).

The blog router has no side effects — data is hardcoded — so these tests
require no mocking beyond the standard TestClient fixture.
"""
import pytest

BLOG_SLUG_VALID = "building-production-rag-systems"
BLOG_SLUG_INVALID = "this-post-does-not-exist"

REQUIRED_SUMMARY_FIELDS = {"slug", "title", "excerpt", "date", "readTime", "category"}


class TestGetBlogPosts:
    def test_returns_200(self, client):
        response = client.get("/api/blog")
        assert response.status_code == 200

    def test_returns_list(self, client):
        data = client.get("/api/blog").json()
        assert isinstance(data, list)

    def test_returns_exactly_three_posts(self, client):
        data = client.get("/api/blog").json()
        assert len(data) == 3

    def test_each_summary_has_required_fields(self, client):
        summaries = client.get("/api/blog").json()
        for summary in summaries:
            missing = REQUIRED_SUMMARY_FIELDS - summary.keys()
            assert not missing, f"Summary missing fields: {missing}"

    def test_summaries_do_not_include_content(self, client):
        """BlogPostSummary should not expose full content."""
        summaries = client.get("/api/blog").json()
        for summary in summaries:
            assert "content" not in summary

    def test_slugs_are_non_empty_strings(self, client):
        summaries = client.get("/api/blog").json()
        for summary in summaries:
            assert isinstance(summary["slug"], str)
            assert len(summary["slug"]) > 0


class TestGetBlogPost:
    def test_valid_slug_returns_200(self, client):
        response = client.get(f"/api/blog/{BLOG_SLUG_VALID}")
        assert response.status_code == 200

    def test_valid_slug_returns_content_field(self, client):
        post = client.get(f"/api/blog/{BLOG_SLUG_VALID}").json()
        assert "content" in post
        assert len(post["content"]) > 0

    def test_valid_slug_returns_correct_title(self, client):
        post = client.get(f"/api/blog/{BLOG_SLUG_VALID}").json()
        assert "RAG" in post["title"] or "LangChain" in post["title"]

    def test_valid_slug_has_all_required_fields(self, client):
        post = client.get(f"/api/blog/{BLOG_SLUG_VALID}").json()
        required = REQUIRED_SUMMARY_FIELDS | {"content"}
        missing = required - post.keys()
        assert not missing, f"BlogPost missing fields: {missing}"

    def test_invalid_slug_returns_404(self, client):
        response = client.get(f"/api/blog/{BLOG_SLUG_INVALID}")
        assert response.status_code == 404

    def test_invalid_slug_error_message(self, client):
        body = client.get(f"/api/blog/{BLOG_SLUG_INVALID}").json()
        assert "detail" in body

    def test_all_three_slugs_are_accessible(self, client):
        summaries = client.get("/api/blog").json()
        for summary in summaries:
            response = client.get(f"/api/blog/{summary['slug']}")
            assert response.status_code == 200, (
                f"Expected 200 for slug '{summary['slug']}', got {response.status_code}"
            )
