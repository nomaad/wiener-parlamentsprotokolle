
"""Werkzeuge zum Parsen von Wortprotokollen der politischen Gremien der Stadt Wien"""

from .parser import parse_many, parse_protokoll

__all__ = ["parse_many", "parse_protokoll"]