import os
from website import models

POST_PATH = os.path.join(os.path.dirname(__file__), "test.md")
WIKI_PATH = os.path.join(os.path.dirname(__file__), "wiki.md")
TITLE = "test"
DATE = "2021-01-01"
TAGS = ["test", "test2"]
SUMMARY = "This is the summary"
AUTHOR = "test"
IMAGE = "test.jpg"
POST_HREF = "/articles/test"
WIKI_HREF = "/wiki/test"
MARKDOWN = """

# title
**BOLD**

```
ls
```

```sh
ls
```
"""
HTML = """<h1>title</h1>
<p><strong>BOLD</strong></p>

<pre>ls</pre>
<div class="highlight"><pre><span></span>ls
</pre></div>
"""
ORDER = "01"


def test_post():
    """
    Test Post object correspond to mardown file.
    """
    post = models.parse_markdown_post(POST_PATH)
    assert post.title == TITLE
    assert post.summary == SUMMARY
    assert post.author == AUTHOR
    assert post.tags == TAGS
    assert post.date == DATE
    assert post.image == IMAGE
    assert post.href == POST_HREF
    assert post.content_md == MARKDOWN
    assert post.content_html == HTML


def test_proc():
    """
    Test Procedure object corredpond to markdown file.
    """
    proc = models.parse_markdown_wiki(WIKI_PATH)
    assert proc.title == TITLE
    assert proc.summary == SUMMARY
    assert proc.order == ORDER
    assert proc.href == WIKI_HREF
    assert proc.content_md == MARKDOWN
    assert proc.content_html == HTML
