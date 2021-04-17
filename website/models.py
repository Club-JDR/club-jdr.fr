from pygments.lexers import get_lexer_by_name
from pygments import highlight
from pygments.formatters import html
from flask import session, render_template
import mistune
import os
import re


class Procedure:
    def __init__(self, title, summary, href, content_md, order):
        self.title = title
        self.summary = summary
        self.order = order
        self.href = href
        self.content_md = content_md
        self.content_html = md_to_html(content_md)


class Post:
    def __init__(self, title, date, tags, summary, href, content_md, author, image):
        self.title = title
        self.date = date
        self.tags = tags
        self.summary = summary
        self.href = href
        self.content_md = content_md
        self.content_html = md_to_html(content_md)
        self.author = author
        self.image = image


class HighlightRenderer(mistune.Renderer):
    """
    Extend renderer built into mistune module. This object unables code
    highlighting during Markdown-to-HTML conversions.
    """

    def block_code(self, code, lang):
        """
        Get the language indicated in each fenced code block. Get the
        appropriate Pygments lexer based on this language and parse code
        accordingly into HTML format. If not language is detected, use vanilla
        <code> blocks.
        """
        if not lang:
            return "\n<pre>%s</pre>\n" % mistune.escape(code)
        lexer = get_lexer_by_name(lang, stripall=True)
        formatter = html.HtmlFormatter()
        return highlight(code, lexer, formatter)


def md_to_html(md_string):
    """
    Convert a Markdown string to HTML.
    """
    markdown_formatter = mistune.Markdown(
        renderer=HighlightRenderer(parse_block_html=True)
    )
    html = markdown_formatter(md_string)
    return html


def parse_markdown_post(md_path):
    """
    Use a regular expression to parse the components of a Markdown post's
    header and the post body. Return an assembled Post object,
    """
    with open(md_path, "rt") as f:
        markdown = f.read()
    re_pat = re.compile(
        r"title: (?P<title>[^\n]*)\sdate: (?P<date>\d{4}-\d{2}-\d{2})\s"
        r"tags: (?P<tags>[^\n]*)\ssummary: (?P<summary>[^\n]*)\s"
        r"author: (?P<author>[^\n]*)\simage: (?P<image>[^\n]*)"
    )
    match_obj = re.match(re_pat, markdown)
    title = match_obj.group("title")
    date = match_obj.group("date")
    summary = match_obj.group("summary")
    author = match_obj.group("author")
    image = None
    if match_obj.group("image") != "None":
        image = match_obj.group("image")
    tags = sorted([tag.strip() for tag in match_obj.group("tags").split(",")])
    href = os.path.join("/articles", title.lower().replace(" ", "-"))
    content_md = re.split(re_pat, markdown)[-1]
    return Post(title, date, tags, summary, href, content_md, author, image)


def parse_markdown_wiki(md_path):
    """
    Use a regular expression to parse the components of a Markdown post's
    header and the post body. Return an assembled Procedure object,
    """
    with open(md_path, "rt") as f:
        markdown = f.read()
    re_pat = re.compile(
        r"title: (?P<title>[^\n]*)\s"
        r"order: (?P<order>[^\n]*)\s"
        r"summary: (?P<summary>[^\n]*)"
    )
    match_obj = re.match(re_pat, markdown)
    title = match_obj.group("title")
    order = match_obj.group("order")
    summary = match_obj.group("summary")
    href = os.path.join("/wiki", title.lower().replace(" ", "-"))
    content_md = re.split(re_pat, markdown)[-1]
    return Procedure(title, summary, href, content_md, order)


def who():
    payload = {}
    if "username" in session:
        payload["username"] = session["username"]
        payload["avatar"] = session["avatar"]
        if session["gm"]:
            payload["gm"] = session["gm"]
    return payload
