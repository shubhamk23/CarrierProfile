from pydantic import BaseModel, EmailStr
from typing import List, Dict, Optional
from datetime import datetime


class ContactMessage(BaseModel):
    name: str
    email: EmailStr
    subject: str
    message: str


class ContactResponse(BaseModel):
    success: bool
    message: str


class Certification(BaseModel):
    title: str
    issuer: str


class Award(BaseModel):
    title: str
    year: str
    description: str


class Education(BaseModel):
    degree: str
    institution: str
    location: str
    period: str


class Experience(BaseModel):
    company: str
    role: str
    location: str
    period: str
    description: List[str]
    technologies: List[str]


class Project(BaseModel):
    title: str
    period: str
    technologies: List[str]
    description: str
    highlights: List[str]


class Skills(BaseModel):
    languages: List[str]
    ml_dl_frameworks: List[str]
    computer_vision: List[str]
    generative_ai_nlp: List[str]
    mlops_devops: List[str]
    cloud_data: List[str]
    software_engineering: List[str]


class Profile(BaseModel):
    name: str
    title: str
    subtitle: str
    location: str
    phone: str
    email: str
    linkedin: str
    github: str
    summary: str
    skills: Skills
    experience: List[Experience]
    projects: List[Project]
    education: Education
    certifications: List[Certification]
    awards: List[Award]


class BlogPost(BaseModel):
    slug: str
    title: str
    excerpt: str
    content: str
    date: str
    readTime: str
    category: str


class BlogPostSummary(BaseModel):
    slug: str
    title: str
    excerpt: str
    date: str
    readTime: str
    category: str
