"""
Milestone 3 — ingestion helper.

Extracts the article/comment body text out of the raw HTML pages saved in
.raw_html/ and writes clean .txt files into documents/.

Uses only the Python standard library (html.parser) so there are no extra
dependencies. The extractor captures text only while inside an HTML element
whose class attribute matches a target token/substring for that source, which
keeps site navigation, related-story rails, and footers out of the output.
"""

import html
import re
from html.parser import HTMLParser
from pathlib import Path

RAW_DIR = Path(".raw_html")
OUT_DIR = Path("documents")
SKIP_CONTENT_TAGS = {"script", "style", "noscript"}
# Tags whose text should be separated by a blank line (paragraph-ish blocks).
BLOCK_TAGS = {"p", "div", "li", "h1", "h2", "h3", "h4", "br", "blockquote"}


class TargetTextExtractor(HTMLParser):
    """Collect text only while inside an element matching `targets`.

    Each target is (value, mode):
      - ("md", "token")      -> class attribute has the exact token "md"
      - ("sno-story-body-content", "substr") -> substring appears in class attr
    """

    def __init__(self, targets):
        super().__init__(convert_charrefs=True)
        self.targets = targets
        self.capture_stack = 0      # how many open target elements we are inside
        self.skip_stack = 0         # inside script/style/etc.
        self.depth_since_capture = 0
        self.blocks = []            # list of captured text fragments
        self._open_target_depths = []
        self._tag_depth = 0

    def _matches(self, attrs):
        cls = dict(attrs).get("class", "") or ""
        tokens = cls.split()
        for value, mode in self.targets:
            if mode == "token" and value in tokens:
                return True
            if mode == "substr" and value in cls:
                return True
        return False

    def handle_starttag(self, tag, attrs):
        if tag in SKIP_CONTENT_TAGS:
            self.skip_stack += 1
            return
        self._tag_depth += 1
        if self._matches(attrs):
            self.capture_stack += 1
            self._open_target_depths.append(self._tag_depth)
        if tag in BLOCK_TAGS and self.capture_stack > 0:
            self.blocks.append("\n")

    def handle_endtag(self, tag):
        if tag in SKIP_CONTENT_TAGS:
            self.skip_stack = max(0, self.skip_stack - 1)
            return
        if self._open_target_depths and self._tag_depth == self._open_target_depths[-1]:
            self._open_target_depths.pop()
            self.capture_stack = max(0, self.capture_stack - 1)
        self._tag_depth = max(0, self._tag_depth - 1)
        if tag in BLOCK_TAGS and self.capture_stack > 0:
            self.blocks.append("\n")

    def handle_data(self, data):
        if self.skip_stack == 0 and self.capture_stack > 0:
            self.blocks.append(data)

    def get_text(self):
        text = "".join(self.blocks)
        text = html.unescape(text)
        # collapse runs of spaces/tabs, normalise newlines
        lines = [re.sub(r"[ \t]+", " ", ln).strip() for ln in text.split("\n")]
        lines = [ln for ln in lines if ln]
        return "\n\n".join(lines)


def extract(raw_file, targets, start_after=None):
    html_text = Path(raw_file).read_text(encoding="utf-8", errors="ignore")
    parser = TargetTextExtractor(targets)
    parser.feed(html_text)
    text = parser.get_text()
    if start_after:
        idx = text.find(start_after)
        if idx != -1:
            text = text[idx + len(start_after):].lstrip("\n ")
    return text


# (raw file, output file, header lines, extraction targets, start_after)
JOBS = [
    (
        "04_gge_top5.html",
        "04_gge_top5_off_campus_eateries.txt",
        [
            "Source: Top five off-campus eateries around SFSU (Golden Gate Xpress)",
            "URL: https://goldengatexpress.org/113255/opinion/opinion-top-five-off-campus-eateries-around-sfsu/",
            "Type: blog post",
        ],
        [("sno-story-body-content", "substr")],
        None,
    ),
    (
        "07_gge_monarca.html",
        "07_gge_monarca_dining_hall.txt",
        [
            "Source: Gator Take — Monarca dining hall (formerly City Eats) is not bad (Golden Gate Xpress)",
            "URL: https://goldengatexpress.org/107839/opinion/gator-take-monarca-dining-hall-formerly-city-eats-is-not-bad/",
            "Type: blog post",
        ],
        [("sno-story-body-content", "substr")],
        None,
    ),
    (
        "10_xpress_bestsf.html",
        "10_xpress_best_of_sf.txt",
        [
            "Source: The best of San Francisco: SF State edition (Xpress Magazine)",
            "URL: https://xpressmagazine.org/5585/fall-2013/the-best-of-san-francisco-sf-state-edition/",
            "Type: article",
        ],
        [("sno-story-body-content", "substr")],
        None,
    ),
    (
        "01_reddit_bestfood.html",
        "01_reddit_best_food_on_campus.txt",
        [
            "Source: Best Food on Campus or off (r/SFSU)",
            "URL: https://www.reddit.com/r/SFSU/comments/1fe4on9/best_food_on_campus_or_off/",
            "Type: forum thread",
        ],
        [("md", "token")],
        "Any comments or links posted here are not the opinion of the University",
    ),
]


def main():
    OUT_DIR.mkdir(exist_ok=True)
    for raw_name, out_name, header, targets, start_after in JOBS:
        raw_path = RAW_DIR / raw_name
        if not raw_path.exists():
            print(f"SKIP {raw_name}: not found")
            continue
        body = extract(raw_path, targets, start_after)
        content = "\n".join(header) + "\n\n" + body + "\n"
        (OUT_DIR / out_name).write_text(content, encoding="utf-8")
        print(f"{len(body):6d} chars body -> documents/{out_name}")


if __name__ == "__main__":
    main()
