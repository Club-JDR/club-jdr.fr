REQUIRED = b'You should be redirected automatically to target URL: <a href="/login/">/login/</a>.'
POST_TXT = "Le Club JDR passe à la vitesse supérieure !".encode()
POST_URL = "/articles/club-jdr.fr-est-en-ligne"


def missing_menu_items(response):
    """
    Assert that GMs menu items ar not shown.
    """
    assert b"Ressources" not in response.data
    assert b"Wiki des GMs" not in response.data


def test_index(client):
    """
    Test index page : menu items should not be present.
    """
    response = client.get("/")
    assert b"Bienvenue au Club JDR" in response.data
    missing_menu_items(response)
    assert response.status_code == 200


def test_session(client):
    """
    Login page should redirect to Discord OAuth2.
    """
    response = client.get("/login")
    assert response.status_code == 308
    """
    Fake session as non GM: should see avatar instead of login button
    but neither Ressources and wiki des GMs menus.
    """
    with client.session_transaction() as session:
        session["username"] = "user"
        session["avatar"] = "avatar.png"
        session["gm"] = False
    response = client.get("/")
    missing_menu_items(response)
    assert response.status_code == 200
    icon = b'<img src="avatar.png" alt="user" class="rounded-circle floating">'
    assert icon in response.data
    assert response.status_code == 200
    """
    Fake session as GM: should see Ressources and wiki menu items.
    """
    with client.session_transaction() as session:
        session["gm"] = True
    response = client.get("/")
    assert b"Ressources" in response.data
    assert b"Wiki des GMs" in response.data
    """
    Logout should remove menu items and redirect.
    """
    response = client.get("/logout/")
    missing_menu_items(response)
    assert response.status_code == 302


def _unauthorized(client):
    """
    Ensure that pages that requires authorization redirect.
    """
    """
    Ensure pages that requires GM redirect.
    """
    response = client.get("/articles/edit/")
    assert response.status_code == 302
    assert REQUIRED in response.data


def test_contact(client):
    """
    Ensure contact page is showing properly.
    """
    response = client.get("/contact/")
    assert response.status_code == 200
    assert b"mailto:contact@club-jdr.fr" in response.data


def test_links(client):
    """
    Ensure links page is showing properly.
    """
    response = client.get("/liens/")
    assert response.status_code == 200
    assert b"https://www.aidedd.org" in response.data


def test_blog_home(client):
    """
    Ensure blog home list articles.
    """
    response = client.get("/articles/")
    assert response.status_code == 200
    assert b"Tous les articles" in response.data
    """
    Test logged-in no GM can't see button to add articles.
    """
    button = b"button icon solid fa-plus"
    with client.session_transaction() as session:
        session["username"] = "user"
        session["avatar"] = "avatar.png"
        session["gm"] = False
    response = client.get("/articles/")
    assert response.status_code == 200
    assert button not in response.data
    """
    Test Logged-in GM can see button to add articles.
    """
    with client.session_transaction() as session:
        session["username"] = "user"
        session["avatar"] = "avatar.png"
        session["gm"] = True
    response = client.get("/articles/")
    assert response.status_code == 200
    assert button in response.data


def test_blog_byTag(client):
    """
    Test post list by tag.
    """
    response = client.get("/articles/tag/dnd")
    assert response.status_code == 200
    assert b'Articles avec le tag "dnd"' in response.data


def test_blog_byAuthor(client):
    """
    Test post list by author.
    """
    response = client.get("/articles/by/Notsag")
    assert response.status_code == 200
    assert b'Articles de "Notsag"' in response.data


def test_blog_edit(client):
    """
    Ensure blog edit page is working.
    """
    response = client.get("/articles/edit/")
    assert response.status_code == 302
    assert REQUIRED in response.data
    with client.session_transaction() as session:
        session["username"] = "user"
        session["avatar"] = "avatar.png"
        session["gm"] = True
    # test creation
    response = client.get(
        "/articles/edit/", headers={"Referer": "http://localhost:5000/articles/"}
    )
    print(response.data)
    assert response.status_code == 200
    assert b'<textarea name="markdown"' in response.data
    # Now test edition
    response = client.get(
        "/articles/edit/", headers={"Referer": POST_URL}
    )
    assert response.status_code == 200
    assert b'<textarea name="markdown"' in response.data
    assert POST_TXT in response.data


def test_blog_post(client):
    """
    Ensure blog post page is working.
    """
    response = client.get(POST_URL)
    assert response.status_code == 200
    assert POST_TXT in response.data


def test_storage(client):
    """
    Ensure ressources page is working
    """
    response = client.get("/ressources/")
    assert response.status_code == 302
    assert REQUIRED in response.data
    with client.session_transaction() as session:
        session["username"] = "user"
        session["avatar"] = "avatar.png"
        session["gm"] = True
    response = client.get("/ressources/")
    assert response.status_code == 200
    assert b"Vous trouverez dans cette section toutes les ressources" in response.data


def test_wiki(client):
    """
    Ensure wiki page is working
    """
    response = client.get("/wiki/")
    assert response.status_code == 302
    assert REQUIRED in response.data
    with client.session_transaction() as session:
        session["username"] = "user"
        session["avatar"] = "avatar.png"
        session["gm"] = True
    response = client.get("/wiki/")
    assert response.status_code == 200
    assert b"Cette section contient les diverses proc" in response.data


def test_wiki_proc(client):
    """
    Test wiki proc page.
    """
    # Not logged-in means redirect
    response = client.get("/wiki/poster-une-annonce-de-partie")
    assert response.status_code == 302
    # Logged-in
    with client.session_transaction() as session:
        session["username"] = "user"
        session["avatar"] = "avatar.png"
        session["gm"] = True
    response = client.get("/wiki/poster-une-annonce-de-partie")
    assert response.status_code == 200
    assert b"Je veux proposer une partie de JdR sur le serveur" in response.data


def test_sitemap(client):
    response = client.get("/sitemap.xml")
    assert response.status_code == 200
    assert (
        b'<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">' in response.data
    )


def test_404(client):
    response = client.get("/invalid/")
    assert response.status_code == 404
    assert b"n'existe pas..." in response.data


def test_400(client):
    response = client.post("/articles/edit/")
    assert response.status_code == 400
    assert b"Mauvaise requ\xc3\xaate..." in response.data
