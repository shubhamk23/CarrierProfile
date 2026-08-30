from pydantic import BaseModel, EmailStr, Field


class ContactMessage(BaseModel):
    """Contact form submission.

    Lengths are capped at the database column widths (see
    app/database/models.py) so oversized input is rejected at the trust
    boundary with a 422 rather than failing later on INSERT.
    """

    name: str = Field(min_length=1, max_length=255)
    email: EmailStr = Field(max_length=255)
    subject: str = Field(min_length=1, max_length=500)
    message: str = Field(min_length=1, max_length=5000)


class ContactResponse(BaseModel):
    success: bool
    message: str
