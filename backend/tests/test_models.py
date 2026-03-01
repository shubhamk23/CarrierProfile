"""Unit tests for Pydantic models defined in app/models.py."""
import pytest
from pydantic import ValidationError

from app.models import (
    ContactMessage,
    ContactResponse,
    BlogPost,
    BlogPostSummary,
    Certification,
    Award,
    Education,
    Experience,
    Project,
    Skills,
    Profile,
)


# ---------------------------------------------------------------------------
# ContactMessage
# ---------------------------------------------------------------------------

class TestContactMessage:
    def test_valid_contact_message(self):
        msg = ContactMessage(
            name="Alice",
            email="alice@example.com",
            subject="Hello",
            message="Hi there!",
        )
        assert msg.name == "Alice"
        assert str(msg.email) == "alice@example.com"

    def test_invalid_email_raises_validation_error(self):
        with pytest.raises(ValidationError) as exc_info:
            ContactMessage(
                name="Alice",
                email="not-an-email",
                subject="Hello",
                message="Hi!",
            )
        assert "email" in str(exc_info.value).lower()

    def test_missing_name_raises_validation_error(self):
        with pytest.raises(ValidationError):
            ContactMessage(
                email="alice@example.com",
                subject="Hello",
                message="Hi!",
            )

    def test_missing_subject_raises_validation_error(self):
        with pytest.raises(ValidationError):
            ContactMessage(
                name="Alice",
                email="alice@example.com",
                message="Hi!",
            )

    def test_missing_message_raises_validation_error(self):
        with pytest.raises(ValidationError):
            ContactMessage(
                name="Alice",
                email="alice@example.com",
                subject="Hello",
            )


# ---------------------------------------------------------------------------
# ContactResponse
# ---------------------------------------------------------------------------

class TestContactResponse:
    def test_valid_contact_response(self):
        resp = ContactResponse(success=True, message="Sent!")
        assert resp.success is True
        assert resp.message == "Sent!"

    def test_success_false(self):
        resp = ContactResponse(success=False, message="Failed")
        assert resp.success is False


# ---------------------------------------------------------------------------
# BlogPostSummary
# ---------------------------------------------------------------------------

class TestBlogPostSummary:
    def test_all_required_fields_present(self):
        summary = BlogPostSummary(
            slug="my-post",
            title="My Post",
            excerpt="Short excerpt",
            date="2024-01-01",
            readTime="5 min read",
            category="Tech",
        )
        assert summary.slug == "my-post"
        assert summary.title == "My Post"
        assert summary.excerpt == "Short excerpt"
        assert summary.date == "2024-01-01"
        assert summary.readTime == "5 min read"
        assert summary.category == "Tech"

    def test_missing_slug_raises_error(self):
        with pytest.raises(ValidationError):
            BlogPostSummary(
                title="My Post",
                excerpt="Excerpt",
                date="2024-01-01",
                readTime="5 min",
                category="Tech",
            )


# ---------------------------------------------------------------------------
# BlogPost
# ---------------------------------------------------------------------------

class TestBlogPost:
    def test_blog_post_includes_content(self):
        post = BlogPost(
            slug="my-post",
            title="My Post",
            excerpt="Excerpt",
            content="Full content here",
            date="2024-01-01",
            readTime="5 min read",
            category="Tech",
        )
        assert post.content == "Full content here"

    def test_missing_content_raises_error(self):
        with pytest.raises(ValidationError):
            BlogPost(
                slug="my-post",
                title="My Post",
                excerpt="Excerpt",
                date="2024-01-01",
                readTime="5 min read",
                category="Tech",
            )


# ---------------------------------------------------------------------------
# Certification & Award
# ---------------------------------------------------------------------------

class TestCertification:
    def test_valid_certification(self):
        cert = Certification(title="AWS SAA", issuer="Amazon")
        assert cert.title == "AWS SAA"
        assert cert.issuer == "Amazon"


class TestAward:
    def test_valid_award(self):
        award = Award(title="Best Paper", year="2023", description="Won it")
        assert award.year == "2023"


# ---------------------------------------------------------------------------
# Education
# ---------------------------------------------------------------------------

class TestEducation:
    def test_valid_education(self):
        edu = Education(
            degree="B.E. CS",
            institution="Test Uni",
            location="Pune",
            period="2015-2019",
        )
        assert edu.degree == "B.E. CS"


# ---------------------------------------------------------------------------
# Experience
# ---------------------------------------------------------------------------

class TestExperience:
    def test_valid_experience(self):
        exp = Experience(
            company="ACME",
            role="Engineer",
            location="Remote",
            period="2020-2023",
            description=["Built things"],
            technologies=["Python"],
        )
        assert isinstance(exp.description, list)
        assert isinstance(exp.technologies, list)


# ---------------------------------------------------------------------------
# Project
# ---------------------------------------------------------------------------

class TestProject:
    def test_valid_project(self):
        proj = Project(
            title="Cool Project",
            period="2023",
            technologies=["Python", "FastAPI"],
            description="A great project",
            highlights=["Achievement 1"],
        )
        assert proj.title == "Cool Project"
        assert "FastAPI" in proj.technologies


# ---------------------------------------------------------------------------
# Skills
# ---------------------------------------------------------------------------

class TestSkills:
    def test_all_seven_categories_required(self):
        skills = Skills(
            languages=["Python"],
            ml_dl_frameworks=["PyTorch"],
            computer_vision=["OpenCV"],
            generative_ai_nlp=["LangChain"],
            mlops_devops=["Docker"],
            cloud_data=["Azure"],
            software_engineering=["FastAPI"],
        )
        assert "Python" in skills.languages

    def test_missing_category_raises_error(self):
        with pytest.raises(ValidationError):
            Skills(
                languages=["Python"],
                # ml_dl_frameworks missing
                computer_vision=["OpenCV"],
                generative_ai_nlp=["LangChain"],
                mlops_devops=["Docker"],
                cloud_data=["Azure"],
                software_engineering=["FastAPI"],
            )
