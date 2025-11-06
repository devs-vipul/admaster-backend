"""
AdMaster-Crawler service
Extracts basic brand intel from a business website:
- description (meta description or best paragraph)
- logo (favicon or og:image fallback)
- brand colors (theme-color + simple CSS heuristics)
- language (from html lang or detected from text)
- tone suggestions (heuristic list)

This is intentionally lightweight and dependency-minimal so it runs reliably.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional, Tuple
from urllib.parse import urljoin
import re

import httpx
from bs4 import BeautifulSoup
from langdetect import detect, LangDetectException


@dataclass
class CrawlResult:
    description: str
    logo_url: Optional[str]
    brand_colors: List[str]
    tone_of_voice: List[str]
    language: str


_DEFAULT_TONES = [
    "Professional",
    "Casual",
    "Humorous",
    "Informative",
    "Motivating",
    "Optimistic",
]


class AdMasterCrawlerService:
    """Lightweight crawler to extract brand intel."""

    @staticmethod
    async def fetch_html(url: str) -> Tuple[str, str]:
        async with httpx.AsyncClient(follow_redirects=True, timeout=20) as client:
            resp = await client.get(url)
            resp.raise_for_status()
            base_url = str(resp.url)
            return resp.text, base_url

    @staticmethod
    def _extract_description(soup: BeautifulSoup) -> str:
        # Try meta description
        desc = (
            soup.find("meta", attrs={"name": "description"})
            or soup.find("meta", attrs={"property": "og:description"})
        )
        if desc and desc.get("content"):
            return desc["content"].strip()

        # Fallback: pick the longest paragraph text
        paragraphs = [p.get_text(" ", strip=True) for p in soup.find_all("p")]
        paragraphs = [p for p in paragraphs if len(p.split()) >= 6]
        return max(paragraphs, key=len) if paragraphs else ""

    @staticmethod
    def _extract_logo_url(soup: BeautifulSoup, base_url: str) -> Optional[str]:
        # Priority 1: Common favicon / logo meta tags
        rel_candidates = [
            ("link", {"rel": ["icon", "shortcut icon", "apple-touch-icon"]}),
            ("meta", {"property": "og:image"}),
            ("meta", {"name": "og:image"}),
        ]
        for tag_name, attrs in rel_candidates:
            for tag in soup.find_all(tag_name):
                # Normalize rel list
                if tag_name == "link":
                    rel = tag.get("rel") or []
                    rel_set = {r.lower() for r in (rel if isinstance(rel, list) else [rel])}
                    if rel_set & {"icon", "shortcut icon", "apple-touch-icon"}:
                        href = tag.get("href")
                        if href:
                            return urljoin(base_url, href)
                else:
                    # Check both property and name for og:image
                    if (tag.get("property") == "og:image" or tag.get("name") == "og:image") and tag.get("content"):
                        return urljoin(base_url, tag["content"])

        # Priority 2: Find <img> with logo-like alt/class/id in header/nav
        logo_like = re.compile(r"logo|brand", re.I)
        # Check header/nav first (most common logo location)
        header = soup.find("header") or soup.find("nav") or soup.find("div", class_=re.compile(r"header|nav|navbar", re.I))
        if header:
            img = (
                header.find("img", attrs={"alt": logo_like}) 
                or header.find("img", class_=logo_like)
                or header.find("img", id=logo_like)
            )
            if img and img.get("src"):
                return urljoin(base_url, img["src"])

        # Priority 3: Find any <img> with logo-like alt/class/id
        img = (
            soup.find("img", attrs={"alt": logo_like}) 
            or soup.find("img", class_=logo_like)
            or soup.find("img", id=logo_like)
        )
        if img and img.get("src"):
            return urljoin(base_url, img["src"])

        # Priority 4: Check for SVG logos (common in modern sites)
        svg_logo = soup.find("svg", class_=logo_like) or soup.find("svg", id=logo_like)
        if svg_logo:
            # For SVG, we'd need to return the SVG data or a data URL
            # For now, skip SVG and return None
            pass

        return None

    @staticmethod
    def _extract_theme_colors(soup: BeautifulSoup) -> List[str]:
        colors: List[str] = []

        # Priority 1: meta theme-color (most reliable)
        for meta in soup.find_all("meta", attrs={"name": "theme-color"}):
            content = (meta.get("content") or "").strip()
            if AdMasterCrawlerService._is_hex_color(content):
                colors.append(AdMasterCrawlerService._normalize_hex(content))

        # Priority 2: CSS variables in inline <style> tags
        # Look for common brand color variable names
        color_var_patterns = [
            r"--[^:]*primary[^:]*:\s*(#[0-9a-fA-F]{3,8})",
            r"--[^:]*brand[^:]*:\s*(#[0-9a-fA-F]{3,8})",
            r"--[^:]*main[^:]*:\s*(#[0-9a-fA-F]{3,8})",
            r"--[^:]*accent[^:]*:\s*(#[0-9a-fA-F]{3,8})",
            r"--[^:]*color[^:]*:\s*(#[0-9a-fA-F]{3,8})",
        ]
        for style in soup.find_all("style"):
            text = style.get_text("\n")
            for pattern in color_var_patterns:
                for match in re.findall(pattern, text, re.I):
                    colors.append(AdMasterCrawlerService._normalize_hex(match))

        # Priority 3: Extract hex colors from inline styles and CSS
        # Look for background-color, color, border-color in inline styles
        inline_style_pattern = r"(?:background-|border-)?color\s*:\s*(#[0-9a-fA-F]{3,8})"
        for element in soup.find_all(attrs={"style": True}):
            style_attr = element.get("style", "")
            for match in re.findall(inline_style_pattern, style_attr, re.I):
                colors.append(AdMasterCrawlerService._normalize_hex(match))

        # Priority 4: Extract from <style> tags (not just variables)
        # Look for actual color declarations in CSS
        css_color_pattern = r"(?:background-|border-|color)\s*:\s*(#[0-9a-fA-F]{3,8})"
        for style in soup.find_all("style"):
            text = style.get_text("\n")
            # Find colors in CSS rules (avoid common grays/whites)
            for match in re.findall(css_color_pattern, text, re.I):
                hex_color = AdMasterCrawlerService._normalize_hex(match)
                # Filter out common neutral colors
                if hex_color not in ["#ffffff", "#000000", "#f5f5f5", "#e5e5e5", "#cccccc", "#999999", "#666666", "#333333"]:
                    colors.append(hex_color)

        # Priority 5: Check for common color meta tags
        color_meta_names = ["msapplication-TileColor", "apple-mobile-web-app-status-bar-style"]
        for meta in soup.find_all("meta"):
            name = meta.get("name", "").lower()
            if any(color_name in name for color_name in color_meta_names):
                content = (meta.get("content") or "").strip()
                if AdMasterCrawlerService._is_hex_color(content):
                    colors.append(AdMasterCrawlerService._normalize_hex(content))

        # Deduplicate while preserving order
        dedup: List[str] = []
        for c in colors:
            if c not in dedup:
                dedup.append(c)
        
        # Return up to 4 most common/relevant colors
        return dedup[:4]

    @staticmethod
    def _normalize_hex(value: str) -> str:
        v = value.strip().lower()
        if not v.startswith("#"):
            v = "#" + v
        # Clamp to 7 chars (#rrggbb)
        return v[:7]

    @staticmethod
    def _is_hex_color(value: str) -> bool:
        return bool(re.fullmatch(r"#?[0-9a-fA-F]{3,8}", value.strip()))

    @staticmethod
    def _detect_language(text: str, soup: BeautifulSoup) -> str:
        # Priority: html[lang]
        html = soup.find("html")
        if html and html.get("lang"):
            return html.get("lang").split("-")[0].lower()
        # Fallback: langdetect
        try:
            if text and len(text.split()) >= 10:
                return detect(text)
        except LangDetectException:
            pass
        return "en"

    @staticmethod
    def _tone_suggestions(description: str) -> List[str]:
        # Very light heuristic: optimistic/motivating for positive verbs
        desc = description.lower()
        suggestions = set()
        if any(w in desc for w in ["help", "improve", "grow", "save", "better"]):
            suggestions.add("Motivating")
            suggestions.add("Optimistic")
        if any(w in desc for w in ["platform", "manage", "analyze", "data", "ai"]):
            suggestions.add("Informative")
            suggestions.add("Professional")
        # Always ensure a small default set
        if not suggestions:
            suggestions.update(["Professional", "Informative"]) 
        # Keep order consistent vs defaults
        ordered = [t for t in _DEFAULT_TONES if t in suggestions]
        return ordered[:3]

    @staticmethod
    async def crawl(website: str) -> CrawlResult:
        html, base_url = await AdMasterCrawlerService.fetch_html(website)
        soup = BeautifulSoup(html, "lxml")

        description = AdMasterCrawlerService._extract_description(soup)
        logo_url = AdMasterCrawlerService._extract_logo_url(soup, base_url)
        colors = AdMasterCrawlerService._extract_theme_colors(soup)
        language = AdMasterCrawlerService._detect_language(description, soup)
        tones = AdMasterCrawlerService._tone_suggestions(description)

        return CrawlResult(
            description=description,
            logo_url=logo_url,
            brand_colors=colors,
            tone_of_voice=tones,
            language=language,
        )

