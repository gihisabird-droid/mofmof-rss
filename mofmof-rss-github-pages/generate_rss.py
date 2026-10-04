import re
import html
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from email.utils import format_datetime
from html.parser import HTMLParser

SOURCE = "https://mofmof-investor.com/column/"
OUT = "docs/rss.xml"
MAX_ITEMS = 50

class Parser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []
        self.in_h = False
        self.h_text = []
        self.current_href = None
    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "a" and a.get("href"):
            self.current_href = a["href"]
        if tag in ("h1","h2","h3","h4","h5","h6"):
            self.in_h = True
            self.h_text = []
    def handle_data(self, data):
        if self.in_h:
            self.h_text.append(data)
    def handle_endtag(self, tag):
        if tag == "a" and self.current_href:
            href = self.current_href
            if "/column/" in href and href.rstrip("/") != SOURCE.rstrip("/"):
                self.links.append((href, "".join(self.h_text).strip()))
            self.current_href = None
        if tag in ("h1","h2","h3","h4","h5","h6"):
            self.in_h = False

def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent":"Mozilla/5.0 RSS generator"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read().decode("utf-8", "ignore")

def abs_url(href):
    if href.startswith("http://") or href.startswith("https://"):
        return href
    if href.startswith("/"):
        return "https://mofmof-investor.com" + href
    return SOURCE.rstrip("/") + "/" + href

def clean_title(s):
    s = re.sub(r"\s+", " ", html.unescape(s or "")).strip()
    return s

def main():
    html_text = fetch(SOURCE)
    p = Parser()
    p.feed(html_text)

    seen = set()
    items = []
    for href, title in p.links:
        url = abs_url(href).split("#")[0]
        if url in seen:
            continue
        seen.add(url)
        title = clean_title(title)
        if not title:
            continue
        items.append((title, url))
        if len(items) >= MAX_ITEMS:
            break

    # If heading parsing is insufficient, collect article-looking URLs as fallback.
    if len(items) < 5:
        urls = re.findall(r'href=["\']([^"\']*?/column/[^"\']+)["\']', html_text, re.I)
        for href in urls:
            url = abs_url(html.unescape(href)).split("#")[0]
            if url.rstrip("/") == SOURCE.rstrip("/") or url in seen:
                continue
            seen.add(url)
            slug = url.rstrip("/").rsplit("/",1)[-1].replace("-"," ")
            items.append((slug.title(), url))
            if len(items) >= MAX_ITEMS:
                break

    now = datetime.now(timezone.utc)
    rss = ET.Element("rss", {"version":"2.0"})
    ch = ET.SubElement(rss, "channel")
    ET.SubElement(ch, "title").text = "もふもふ不動産｜投資・テクノロジー解説"
    ET.SubElement(ch, "link").text = SOURCE
    ET.SubElement(ch, "description").text = "もふもふ不動産の投資・テクノロジー解説"
    ET.SubElement(ch, "language").text = "ja"
    ET.SubElement(ch, "lastBuildDate").text = format_datetime(now)

    for title, url in items:
        it = ET.SubElement(ch, "item")
        ET.SubElement(it, "title").text = title
        ET.SubElement(it, "link").text = url
        ET.SubElement(it, "guid", {"isPermaLink":"true"}).text = url
        ET.SubElement(it, "pubDate").text = format_datetime(now)

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    ET.ElementTree(rss).write(OUT, encoding="utf-8", xml_declaration=True)

if __name__ == "__main__":
    main()
