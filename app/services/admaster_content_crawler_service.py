"""
AdMaster Content Crawler Service
Deep crawls a website by following internal links and extracting all content
Used for comprehensive brand analysis and intelligence layer
"""
import httpx
from bs4 import BeautifulSoup
from typing import List, Set, Dict, Optional
from urllib.parse import urljoin, urlparse
import asyncio
from datetime import datetime


class AdMasterContentCrawlerService:
    """
    Deep content crawler that visits all internal pages of a website
    Extracts comprehensive content for intelligence layer analysis
    """
    
    def __init__(self, max_pages: int = 50, max_depth: int = 3):
        """
        Initialize content crawler
        
        Args:
            max_pages: Maximum number of pages to crawl
            max_depth: Maximum depth to crawl (homepage = depth 0)
        """
        self.max_pages = max_pages
        self.max_depth = max_depth
        self.visited_urls: Set[str] = set()
        self.crawled_content: List[Dict[str, any]] = []
        self.base_domain: Optional[str] = None
    
    def _is_valid_url(self, url: str, base_url: str) -> bool:
        """Check if URL is valid, internal, and uses HTTPS protocol"""
        try:
            # Check if URL has colons (required for valid URLs with protocol)
            if ':' not in url:
                return False
            
            parsed = urlparse(url)
            base_parsed = urlparse(base_url)
            
            # Must use HTTPS protocol only
            if parsed.scheme and parsed.scheme.lower() != 'https':
                return False
            
            # Must have a valid netloc (domain)
            if not parsed.netloc:
                return False
            
            # Must be same domain
            if parsed.netloc != base_parsed.netloc:
                return False
            
            # Skip common non-content URLs
            skip_extensions = {'.pdf', '.jpg', '.jpeg', '.png', '.gif', '.svg', '.css', '.js', '.zip', '.exe', '.mp4', '.mp3', '.avi', '.mov'}
            if any(url.lower().endswith(ext) for ext in skip_extensions):
                return False
            
            # Skip common non-content paths
            skip_paths = {'/login', '/signup', '/logout', '/admin', '/api', '/cdn', '/static', '/assets', '/wp-admin', '/wp-content'}
            if any(path in url.lower() for path in skip_paths):
                return False
            
            return True
        except Exception:
            return False
    
    def _extract_internal_links(self, soup: BeautifulSoup, base_url: str) -> Set[str]:
        """Extract all internal links from a page (HTTPS only)"""
        links = set()
        
        for tag in soup.find_all('a', href=True):
            href = tag['href']
            
            # Skip empty or invalid hrefs
            if not href or not href.strip():
                continue
            
            # Convert to absolute URL
            absolute_url = urljoin(base_url, href)
            
            # Remove fragments
            absolute_url = absolute_url.split('#')[0]
            
            # Ensure URL has https:// protocol
            parsed = urlparse(absolute_url)
            if not parsed.scheme:
                # If no scheme, assume it's relative and add https://
                absolute_url = f"https://{parsed.netloc or self.base_domain}{parsed.path}{'?' + parsed.query if parsed.query else ''}"
            elif parsed.scheme.lower() != 'https':
                # Skip non-HTTPS URLs
                continue
            
            # Check if URL has colons (required for valid URLs)
            if ':' not in absolute_url:
                continue
            
            # Validate URL
            if self._is_valid_url(absolute_url, base_url):
                links.add(absolute_url)
        
        return links
    
    def _extract_page_content(self, soup: BeautifulSoup, url: str) -> Dict[str, any]:
        """Extract all content from a page"""
        # Remove script and style tags
        for script in soup(["script", "style"]):
            script.decompose()
        
        # Extract text content
        text_content = soup.get_text(separator=' ', strip=True)
        
        # Extract headings
        headings = {
            'h1': [h.get_text(strip=True) for h in soup.find_all('h1')],
            'h2': [h.get_text(strip=True) for h in soup.find_all('h2')],
            'h3': [h.get_text(strip=True) for h in soup.find_all('h3')],
        }
        
        # Extract meta tags
        meta_tags = {}
        for meta in soup.find_all('meta'):
            name = meta.get('name') or meta.get('property')
            content = meta.get('content')
            if name and content:
                meta_tags[name] = content
        
        # Extract images
        images = []
        for img in soup.find_all('img', src=True):
            images.append({
                'src': urljoin(url, img['src']),
                'alt': img.get('alt', ''),
            })
        
        # Extract links
        links = []
        for a in soup.find_all('a', href=True):
            links.append({
                'href': urljoin(url, a['href']),
                'text': a.get_text(strip=True),
            })
        
        return {
            'url': url,
            'text_content': text_content,
            'headings': headings,
            'meta_tags': meta_tags,
            'images': images,
            'links': links,
            'word_count': len(text_content.split()),
        }
    
    async def crawl(self, start_url: str) -> Dict[str, any]:
        """
        Crawl website starting from start_url (HTTPS only)
        
        Returns:
            Dictionary with crawled content and statistics
        """
        # Ensure start_url uses HTTPS
        parsed_start = urlparse(start_url)
        if not parsed_start.scheme:
            start_url = f"https://{parsed_start.netloc or parsed_start.path}"
        elif parsed_start.scheme.lower() != 'https':
            # Convert HTTP to HTTPS
            start_url = start_url.replace('http://', 'https://', 1)
        
        # Validate start URL has colons
        if ':' not in start_url:
            raise ValueError(f"Invalid URL format: {start_url} (must contain ':' for protocol)")
        
        self.base_domain = urlparse(start_url).netloc
        self.visited_urls.clear()
        self.crawled_content.clear()
        
        # Queue: (url, depth)
        queue: List[tuple[str, int]] = [(start_url, 0)]
        
        async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as client:
            while queue and len(self.visited_urls) < self.max_pages:
                url, depth = queue.pop(0)
                
                # Skip if already visited or too deep
                if url in self.visited_urls or depth > self.max_depth:
                    continue
                
                try:
                    # Fetch page
                    response = await client.get(url)
                    response.raise_for_status()
                    
                    # Parse HTML
                    soup = BeautifulSoup(response.text, 'html.parser')
                    
                    # Extract content
                    page_content = self._extract_page_content(soup, url)
                    self.crawled_content.append(page_content)
                    self.visited_urls.add(url)
                    
                    # Extract internal links for next level
                    if depth < self.max_depth:
                        internal_links = self._extract_internal_links(soup, url)
                        for link in internal_links:
                            if link not in self.visited_urls:
                                queue.append((link, depth + 1))
                    
                    # Small delay to be respectful
                    await asyncio.sleep(0.5)
                    
                except Exception as e:
                    print(f"⚠️  Error crawling {url}: {e}")
                    continue
        
        # Aggregate statistics
        total_words = sum(page['word_count'] for page in self.crawled_content)
        all_text = ' '.join(page['text_content'] for page in self.crawled_content)
        
        return {
            'base_url': start_url,
            'pages_crawled': len(self.crawled_content),
            'total_words': total_words,
            'pages': self.crawled_content,
            'aggregated_text': all_text,
            'crawled_at': datetime.utcnow().isoformat(),
        }

