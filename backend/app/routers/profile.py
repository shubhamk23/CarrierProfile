from fastapi import APIRouter, HTTPException
from typing import List
import json
from pathlib import Path

from app.models import Profile, Experience, Skills, Project, Education, Certification, Award

router = APIRouter()

# Load profile data
DATA_PATH = Path(__file__).parent.parent / "data" / "profile.json"


def load_profile_data() -> dict:
    try:
        with open(DATA_PATH, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        raise HTTPException(status_code=500, detail="Profile data not found")


@router.get("/profile", response_model=Profile)
async def get_profile():
    """Get full profile data"""
    data = load_profile_data()
    return data


@router.get("/experience", response_model=List[Experience])
async def get_experience():
    """Get work experience list"""
    data = load_profile_data()
    return data["experience"]


@router.get("/skills", response_model=Skills)
async def get_skills():
    """Get skills by category"""
    data = load_profile_data()
    return data["skills"]


@router.get("/projects", response_model=List[Project])
async def get_projects():
    """Get project details"""
    data = load_profile_data()
    return data["projects"]


@router.get("/education", response_model=Education)
async def get_education():
    """Get education details"""
    data = load_profile_data()
    return data["education"]


@router.get("/certifications", response_model=List[Certification])
async def get_certifications():
    """Get certifications list"""
    data = load_profile_data()
    return data["certifications"]


@router.get("/achievements", response_model=List[Award])
async def get_achievements():
    """Get awards and achievements"""
    data = load_profile_data()
    return data["awards"]
