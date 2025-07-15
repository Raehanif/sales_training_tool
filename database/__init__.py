# Database package initialization
from .models import db, save_generated_script, get_generated_scripts

__all__ = ['db', 'save_generated_script', 'get_generated_scripts'] 