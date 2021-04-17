from flask import redirect, url_for, render_template, request
from flask import current_app, make_response, session
from urllib.parse import unquote
from website import app
from .models import who, parse_markdown_post, parse_markdown_wiki
import datetime
import collections
import functools
import os
import json
import re


DATE_FORMAT = "%Y-%m-%d"
BLOG_HOME_TPL = "blog_home.html"
BLOG_EDIT_TPL = "blog_edit.html"


def login_required(view):
    """View decorator that redirects anonymous users to the login page."""

    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if "username" not in session or not session["gm"]:
            return redirect(url_for("login"))

        return view(**kwargs)

    return wrapped_view


@app.route("/")
def home():
    payload = who()
    payload["home"] = True
    return render_template("home.html", payload=payload)


@app.route("/contact/")
def contact():
    payload = who()
    payload["contact"] = True
    return render_template("contact.html", payload=payload)


@app.route("/liens/")
def links():
    payload = who()
    payload["links"] = True
    return render_template("links.html", payload=payload)


@app.route("/articles/")
def blog_home():
    """
    Render the blog home page. First, iterate over all Markdown files in
    /content directory. Then parse each post for meta data. Add tag info to the
    dictionary of tags. Sort posts by date and tags alphabetically.
    """
    payload = who()
    payload["blog"] = True
    author_dict = dict()
    tag_dict = dict()
    posts = []
    content_path = os.path.join(app.root_path, "content")
    for file in os.listdir(content_path):
        if not file.endswith(".md"):
            continue
        full_path = os.path.join(content_path, file)
        post_obj = parse_markdown_post(full_path)
        posts.append(post_obj)
        author = post_obj.author
        if author not in author_dict.keys():
            author_dict[author] = 0
        author_dict[author] += 1
        for tag in post_obj.tags:
            if tag not in tag_dict.keys():
                tag_dict[tag] = 0
            tag_dict[tag] += 1
    sorted_author_dict = collections.OrderedDict()
    sorted_tag_dict = collections.OrderedDict()
    for key in sorted(author_dict.keys()):
        sorted_author_dict[key] = author_dict[key]
    for key in sorted(tag_dict.keys()):
        sorted_tag_dict[key] = tag_dict[key]
    sorted_posts = sorted(
        posts,
        key=lambda x: datetime.datetime.strptime(x.date, DATE_FORMAT),
        reverse=True,
    )
    return render_template(
        BLOG_HOME_TPL,
        posts=sorted_posts,
        tag_dict=sorted_tag_dict,
        author_dict=sorted_author_dict,
        payload=payload,
    )


@app.route("/articles/edit/", methods=["GET"])
@login_required
def blog_edit_page():
    """
    Render the blog edition page.
    """
    payload = who()
    payload["blog"] = True
    if re.match(".*/articles/?$", request.referrer):
        # New post
        return render_template(BLOG_EDIT_TPL, payload=payload)
    else:
        # post edition = fill the form
        md_path = os.path.join(
            app.root_path,
            "content",
            "%s.md" % request.referrer.split("/articles/", 1)[1],
        )
        post = parse_markdown_post(unquote(md_path))
        return render_template(BLOG_EDIT_TPL, post=post, payload=payload)


@app.route("/articles/edit/", methods=["POST"])
@login_required
def blog_edit_controller():
    """
    Create or edit the blog file from the form.
    """
    payload = who()
    payload["blog"] = True
    error = None
    title = request.values.get("title")
    summary = request.values.get("summary")
    if not title or not summary:
        error = 'Les champs "Titre" et "Résumé" doivent être remplis.'
    author = request.values.get("author")
    image = request.values.get("image")
    tags = request.values.get("tags")
    md = request.values.get("markdown")
    date = request.values.get("date")
    if not date:
        date = datetime.date.today().strftime(DATE_FORMAT)
    md_path = os.path.join(
        app.root_path, "content", "%s.md" % title.lower().replace(" ", "-")
    )
    if os.path.isfile(md_path) and not request.values.get("edit"):
        error = "Cet article existe déjà !"
    if error:
        return render_template(BLOG_EDIT_TPL, payload=payload, error=error)
    f = open(md_path, "w+")
    f.write(
        "title: {}\ndate: {}\ntags: {}\nsummary: {}\nauthor: {}\nimage: {}\n\n".format(
            title, date, tags, summary, author, image
        )
    )
    f.write(md)
    f.close()
    try:
        post = parse_markdown_post(md_path)
        return render_template("blog_post.html", post=post, payload=payload)
    except IOError:
        return render_template("500.html", payload=payload), 500


@app.route("/articles/<post_title>")
def blog_post(post_title):
    """
    Render the page for a blog post. Find the post in the /content directory
    based on the incoming URL and parse the post metadata.
    """
    payload = who()
    payload["blog"] = True
    try:
        md_path = os.path.join(app.root_path, "content", "%s.md" % post_title)
        post = parse_markdown_post(md_path)
        return render_template("blog_post.html", post=post, payload=payload)
    except IOError:
        return render_template("404.html", payload=payload), 404


@app.route("/articles/tag/<queried_tag>")
def get_tagged_posts(queried_tag):
    """
    Render the blog home page, but with posts filtered by a particular tag.
    First, iterate over all Markdown files in /content directory. Then parse
    each post for meta data. Ignore posts that lack the specified tag. Add tag
    info to the dictionary of tags. Sort posts by date and tags alphabetically.
    """
    payload = who()
    payload["blog"] = True
    author_dict = dict()
    tag_dict = dict()
    matching_posts = []
    content_path = os.path.join(app.root_path, "content")
    for file in os.listdir(content_path):
        if not file.endswith(".md"):
            continue
        full_path = os.path.join(content_path, file)
        post_obj = parse_markdown_post(full_path)
        author = post_obj.author
        if queried_tag in post_obj.tags:
            matching_posts.append(post_obj)
        if author not in author_dict.keys():
            author_dict[author] = 0
        author_dict[author] += 1
        for tag in post_obj.tags:
            if tag not in tag_dict.keys():
                tag_dict[tag] = 0
            tag_dict[tag] += 1
    sorted_author_dict = collections.OrderedDict()
    sorted_tag_dict = collections.OrderedDict()
    for key in sorted(author_dict.keys()):
        sorted_author_dict[key] = author_dict[key]
    for key in sorted(tag_dict.keys()):
        sorted_tag_dict[key] = tag_dict[key]
    sorted_posts = sorted(
        matching_posts,
        key=lambda x: datetime.datetime.strptime(x.date, DATE_FORMAT),
        reverse=True,
    )
    return render_template(
        BLOG_HOME_TPL,
        posts=sorted_posts,
        author_dict=sorted_author_dict,
        tag_dict=sorted_tag_dict,
        queried_tag=queried_tag,
        payload=payload,
    )


@app.route("/articles/by/<queried_author>")
def get_author_posts(queried_author):
    """
    Render the blog home page, but with posts filtered by a particular author.
    First, iterate over all Markdown files in /content directory. Then parse
    each post for meta data. Ignore posts that are not from specified author.
    Add tag info to the dictionary of tags. Sort posts by date.
    """
    payload = who()
    payload["blog"] = True
    author_dict = dict()
    tag_dict = dict()
    matching_posts = []
    content_path = os.path.join(app.root_path, "content")
    for file in os.listdir(content_path):
        if not file.endswith(".md"):
            continue
        full_path = os.path.join(content_path, file)
        post_obj = parse_markdown_post(full_path)
        author = post_obj.author
        if queried_author == author:
            matching_posts.append(post_obj)
        if author not in author_dict.keys():
            author_dict[author] = 0
        author_dict[author] += 1
        for tag in post_obj.tags:
            if tag not in tag_dict.keys():
                tag_dict[tag] = 0
            tag_dict[tag] += 1
    sorted_author_dict = collections.OrderedDict()
    sorted_tag_dict = collections.OrderedDict()
    for key in sorted(author_dict.keys()):
        sorted_author_dict[key] = author_dict[key]
    for key in sorted(tag_dict.keys()):
        sorted_tag_dict[key] = tag_dict[key]
    sorted_posts = sorted(
        matching_posts,
        key=lambda x: datetime.datetime.strptime(x.date, DATE_FORMAT),
        reverse=True,
    )
    return render_template(
        BLOG_HOME_TPL,
        posts=sorted_posts,
        tag_dict=sorted_tag_dict,
        author_dict=sorted_author_dict,
        queried_author=queried_author,
        payload=payload,
    )


@app.route("/ressources/")
@login_required
def storage():
    """
    Render the storage page.
    """
    payload = who()
    payload["storage"] = True
    storage_path = os.path.join(app.root_path, "storage.json")
    with open(storage_path) as json_file:
        data = json.load(json_file)
    return render_template("storage.html", data=data, payload=payload)


@app.route("/wiki/")
@login_required
def wiki():
    """
    Render the GM wiki page.
    """
    payload = who()
    payload["wiki"] = True
    posts = []
    content_path = os.path.join(app.root_path, "wiki")
    for file in os.listdir(content_path):
        if not file.endswith(".md"):
            continue
        full_path = os.path.join(content_path, file)
        post_obj = parse_markdown_wiki(full_path)
        posts.append(post_obj)
    sorted_posts = sorted(
        posts,
        key=lambda x: x.order,
    )
    return render_template("wiki_home.html", posts=sorted_posts, payload=payload)


@app.route("/wiki/<wiki_title>")
@login_required
def wiki_post(wiki_title):
    """
    Render the page for a wiki post. Find the post in the /wiki directory
    based on the incoming URL and parse the post metadata.
    """
    payload = who()
    payload["wiki"] = True
    try:
        md_path = os.path.join(app.root_path, "wiki", "%s.md" % wiki_title)
        post = parse_markdown_wiki(md_path)
        return render_template("wiki_post.html", post=post, payload=payload)
    except IOError:
        return render_template("404.html", payload=payload), 404


@app.route("/login/")
def login():
    """
    Login using Discord OAuth2.
    """
    session.permanent = True
    return current_app.discord.create_session()


@app.route("/logout/")
def logout():
    """
    Logout by removing username from session.
    """
    session.pop("username")
    return redirect(url_for("home"))


@app.route("/callback/")
def callback():
    """
    Login callback redirect to homepage.
    """
    current_app.discord.callback()
    user = current_app.discord.fetch_user()
    session["username"] = user.name
    session["avatar"] = user.avatar_url
    guilds = current_app.discord.fetch_guilds()
    is_gm = False
    for guild in guilds:
        if guild.name == app.config["GUILD_NAME"]:
            is_gm = guild.permissions.priority_speaker
    session["gm"] = is_gm
    return redirect(url_for("home"))


@app.route("/sitemap.xml")
def sitemap():
    """
    Generate a sitemap.xml for search engines. Add home page, blog home page
    and blog posts to list of pages in site map. Return an XML response.
    """
    pages = []
    pages.append(["https://club-jdr.fr/", "2021-04-04"])
    pages.append(["https://club-jdr.fr/articles", "2021-04-04"])

    content_path = os.path.join(app.root_path, "content")
    for file in os.listdir(content_path):
        if not file.endswith(".md"):
            continue
        full_path = os.path.join(content_path, file)
        post_obj = parse_markdown_post(full_path)
        url = "https://club-jdr.fr/articles/%s" % file.replace(".md", "")
        last_mod = post_obj.date
        pages.append([url, last_mod])

    response = make_response(render_template("sitemap.xml", pages=pages))
    response.headers["Content-Type"] = "application/xml"
    return response


@app.errorhandler(400)
def bad_request(e):
    """
    Error method for handling 400.
    """
    return render_template("400.html", payload=who()), 400


@app.errorhandler(404)
def page_not_found(e):
    """
    Error method for handling 404.
    """
    return render_template("404.html", payload=who()), 404


@app.errorhandler(500)
def internal_service_error(e):
    """
    Error method for handling 500.
    """
    return render_template("500.html", payload=who()), 500


@app.template_filter("format_date")
def format_date(value, format="%d %b %Y"):
    """
    Jinja filter to format date like this: 25 décembre 2000.
    """
    if value is None:
        return ""
    if isinstance(value, str):
        return datetime.datetime.strptime(value, DATE_FORMAT).strftime(format)
    return value.strftime(format)


@app.template_filter("format_tags")
def format_tags(value):
    """
    Jinja filter to convert tags to string.
    """
    return ", ".join(value)
