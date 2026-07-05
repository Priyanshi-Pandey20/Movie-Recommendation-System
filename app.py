from typing import Optional
import inspect

import requests
import streamlit as st

# =============================
# CONFIG
# =============================
API_BASE = "https://movie-rec-466x.onrender.com" or "http://127.0.0.1:8000"
TMDB_IMG = "https://image.tmdb.org/t/p/w500"

st.set_page_config(page_title="Cinematrix", page_icon="🎟️", layout="wide")

# =============================
# MARQUEE-LIGHT GENERATOR
# (signature hero animation — a row of chasing marquee bulbs,
#  each with a staggered delay so the glow travels across the strip)
# =============================
def marquee_lights_html(n=48):
    bulbs = "".join(
        f'<span style="animation-delay:{(i % 12) * 0.12:.2f}s"></span>' for i in range(n)
    )
    return f'<div class="marquee-lights">{bulbs}</div>'


# =============================
# CINEMA-MARQUEE DESIGN SYSTEM
# =============================
st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,500;0,700;1,500;1,600&family=Manrope:wght@400;500;600;700;800&display=swap');

:root {
    /* -- palette: monochrome film-noir — black, charcoal, silver -- */
    --bg-void: #090909;
    --bg-panel: #151515;
    --bg-panel-hover: #1e1e1e;
    --bg-sidebar: #0c0c0c;

    --gold: #c9c9c9;
    --gold-bright: #f2f2f2;
    --velvet: #6b6b6b;
    --velvet-bright: #9a9a9a;

    --text-cream: #eeeeee;
    --text-secondary: #a3a3a3;
    --text-muted: #6a6a6a;

    --border-subtle: rgba(255, 255, 255, 0.10);
    --border-strong: rgba(255, 255, 255, 0.38);

    --shadow-glow: 0 8px 28px rgba(255, 255, 255, 0.08);
    --shadow-lift: 0 16px 36px rgba(0, 0, 0, 0.55);
}

* {
    transition: background-color 0.25s ease, border-color 0.25s ease,
                box-shadow 0.25s ease, transform 0.25s ease, color 0.25s ease;
}

html, body, [data-testid="stAppViewContainer"] {
    background:
        radial-gradient(ellipse 900px 500px at 50% -10%, rgba(224,172,71,0.08), transparent 60%),
        var(--bg-void);
    color: var(--text-cream);
    font-family: 'Manrope', sans-serif;
}

[data-testid="stHeader"] { background: transparent; }

.block-container {
    padding-top: 1.5rem;
    padding-bottom: 4rem;
    max-width: 1400px;
}

/* ===== TYPOGRAPHY ===== */
h1, h2, h3, .hero-title, .detail-title, .section-title {
    font-family: 'Playfair Display', serif !important;
    letter-spacing: 0.3px;
    color: var(--text-cream) !important;
    font-weight: 600 !important;
}

.hero-title, .section-title {
    font-style: italic;
    font-weight: 500 !important;
}

h2 { font-size: 1.9rem !important; margin-top: 2rem !important; }
h3 { font-size: 1.4rem !important; letter-spacing: 0.3px; }
h4 {
    font-family: 'Manrope', sans-serif !important;
    font-size: 0.95rem !important;
    font-weight: 600 !important;
    color: var(--text-cream) !important;
}

.subtitle {
    color: var(--text-secondary);
    font-size: 1.02rem;
    line-height: 1.6;
    margin-bottom: 2rem;
}

.small-muted { color: var(--text-muted); font-size: 0.95rem; line-height: 1.65; }

/* ===== FILM STRIP (signature structural device) ===== */
.film-strip {
    height: 14px;
    width: 100%;
    background-color: var(--gold);
    background-image: repeating-linear-gradient(
        90deg,
        var(--bg-void) 0px, var(--bg-void) 7px,
        transparent 7px, transparent 19px
    );
    opacity: 0.85;
}
.film-strip-thin {
    height: 10px;
    margin: 0.4rem 0 1.6rem 0;
    border-radius: 2px;
}

/* ===== HERO ===== */
.hero {
    background: linear-gradient(180deg, #171a25 0%, #0f121a 100%);
    border: 1px solid var(--border-subtle);
    border-radius: 6px;
    margin-bottom: 3rem;
    overflow: hidden;
    box-shadow: var(--shadow-lift);
}

.hero-inner {
    padding: 3rem 3rem 2.4rem 3rem;
    position: relative;
}

.hero-eyebrow {
    font-family: 'Manrope', sans-serif;
    font-size: 0.78rem;
    font-weight: 700;
    letter-spacing: 4px;
    color: var(--velvet-bright);
    text-transform: uppercase;
    margin-bottom: 0.6rem;
}

.hero-title {
    font-size: 4.6rem !important;
    letter-spacing: 3px !important;
    color: var(--gold-bright) !important;
    margin: 0 0 0.6rem 0 !important;
    line-height: 1 !important;
    text-shadow: 0 0 40px rgba(224, 172, 71, 0.25);
}

.hero-tagline {
    font-size: 1.05rem;
    color: var(--text-secondary);
    max-width: 560px;
    line-height: 1.6;
    margin: 0;
}

/* Chasing marquee bulbs */
.marquee-lights {
    display: flex;
    gap: 12px;
    flex-wrap: wrap;
    margin-top: 1.8rem;
}
.marquee-lights span {
    width: 6px;
    height: 6px;
    border-radius: 50%;
    background: var(--gold);
    box-shadow: 0 0 6px 1px rgba(224, 172, 71, 0.55);
    animation: bulbPulse 2.6s ease-in-out infinite;
}
@keyframes bulbPulse {
    0%, 100% { opacity: 0.3; transform: scale(0.8); }
    50% { opacity: 1; transform: scale(1.2); background: var(--gold-bright); }
}
@media (prefers-reduced-motion: reduce) {
    .marquee-lights span { animation: none; opacity: 0.8; }
}

/* ===== SECTION HEADERS ===== */
.section-header { margin-top: 2.2rem; margin-bottom: 1.2rem; }
.section-eyebrow {
    font-family: 'Manrope', sans-serif;
    font-size: 0.72rem;
    font-weight: 700;
    letter-spacing: 3px;
    text-transform: uppercase;
    color: var(--velvet-bright);
    margin-bottom: 0.3rem;
}
.section-title {
    font-size: 1.9rem !important;
    color: var(--gold-bright) !important;
    letter-spacing: 1.5px !important;
    margin: 0 !important;
}

/* ===== CARDS ===== */
.glass-card, .poster-card {
    background: var(--bg-panel);
    border: 1px solid var(--border-subtle);
    border-radius: 4px;
    box-shadow: 0 4px 14px rgba(0,0,0,0.3);
}

.glass-card { padding: 2rem; }
.glass-card:hover {
    border-color: var(--border-strong);
    box-shadow: var(--shadow-glow);
}

.poster-card {
    padding: 0.7rem 0.7rem 1rem 0.7rem;
    margin-bottom: 0.8rem;
}
.poster-card:hover {
    border-color: var(--border-strong);
    box-shadow: var(--shadow-glow);
    transform: translateY(-4px);
}

/* Movie title */
.movie-title {
    font-family: 'Manrope', sans-serif;
    font-size: 0.92rem;
    font-weight: 600;
    line-height: 1.4;
    height: 2.6rem;
    overflow: hidden;
    color: var(--text-cream);
    margin: 0.7rem 0 0.5rem 0;
    display: -webkit-box;
    -webkit-line-clamp: 2;
    -webkit-box-orient: vertical;
}

/* Images */
img {
    border-radius: 3px;
    border: 1px solid var(--border-subtle);
}
[data-testid="stColumn"] img:hover {
    border-color: var(--border-strong);
}

/* ===== BUTTONS (ticket-stub styling) ===== */
button {
    background: var(--gold) !important;
    color: #14171f !important;
    border: none !important;
    border-radius: 3px !important;
    font-family: 'Manrope', sans-serif !important;
    font-weight: 700 !important;
    font-size: 0.82rem !important;
    letter-spacing: 0.6px;
    text-transform: uppercase;
    padding: 0.55rem 1.2rem !important;
    margin: 0.3rem 0 !important;
    cursor: pointer !important;
    box-shadow: 0 3px 10px rgba(224, 172, 71, 0.25) !important;
}
button:hover {
    background: var(--gold-bright) !important;
    box-shadow: 0 6px 18px rgba(224, 172, 71, 0.4) !important;
    transform: translateY(-2px) !important;
}
button:active { transform: translateY(0) !important; }

/* ===== INPUTS ===== */
[data-testid="stTextInput"] input {
    background: var(--bg-panel) !important;
    border: 1px solid var(--border-subtle) !important;
    color: var(--text-cream) !important;
    border-radius: 3px !important;
    padding: 0.8rem 1.1rem !important;
    font-size: 1rem !important;
}
[data-testid="stTextInput"] input:focus {
    border-color: var(--gold) !important;
    box-shadow: 0 0 0 3px rgba(224, 172, 71, 0.15) !important;
}
[data-testid="stTextInput"] input::placeholder { color: var(--text-muted) !important; }

[data-testid="stSelectbox"] div[role="combobox"] {
    background: var(--bg-panel) !important;
    border: 1px solid var(--border-subtle) !important;
    border-radius: 3px !important;
    color: var(--text-cream) !important;
}
[data-testid="stSelectbox"] div[role="combobox"]:hover { border-color: var(--gold); }

[data-testid="stSlider"] [role="slider"] { background: var(--gold) !important; }

/* ===== SIDEBAR ===== */
[data-testid="stSidebar"] {
    background: var(--bg-sidebar);
    border-right: 1px solid var(--border-subtle);
}
[data-testid="stSidebar"] h2 {
    margin-top: 0 !important;
    color: var(--gold-bright) !important;
    font-size: 1.7rem !important;
}
[data-testid="stSidebar"] button { width: 100%; text-align: left; justify-content: flex-start; }
[data-testid="stSidebar"] [role="separator"] { border-color: var(--border-subtle) !important; }

/* ===== ALERTS ===== */
[data-testid="stAlert"] {
    background: rgba(224, 172, 71, 0.08) !important;
    border: 1px solid rgba(224, 172, 71, 0.25) !important;
    border-radius: 3px !important;
    color: var(--text-cream) !important;
}
[data-testid="stAlert"][kind="warning"] {
    background: rgba(156, 49, 72, 0.14) !important;
    border-color: rgba(156, 49, 72, 0.35) !important;
}

/* ===== DETAIL PAGE ===== */
.detail-title {
    font-size: 3rem !important;
    letter-spacing: 2px !important;
    color: var(--gold-bright) !important;
    margin-bottom: 1rem !important;
    line-height: 1.1 !important;
}

.detail-meta { display: flex; gap: 0.8rem; margin-bottom: 1.6rem; flex-wrap: wrap; }
.detail-chip {
    display: flex;
    flex-direction: column;
    gap: 0.25rem;
    background: rgba(224, 172, 71, 0.06);
    border: 1px solid var(--border-subtle);
    border-radius: 3px;
    padding: 0.55rem 1rem;
}
.detail-chip-label {
    font-family: 'Manrope', sans-serif;
    font-size: 0.68rem;
    font-weight: 700;
    color: var(--text-muted);
    text-transform: uppercase;
    letter-spacing: 1px;
}
.detail-chip-value {
    font-family: 'Manrope', sans-serif;
    font-size: 0.95rem;
    font-weight: 600;
    color: var(--text-cream);
}

[role="separator"] { border-color: var(--border-subtle) !important; margin: 2rem 0 !important; }
[data-testid="stCaption"] { color: var(--text-muted) !important; }

/* Responsive */
@media (max-width: 768px) {
    .hero-inner { padding: 2rem 1.5rem; }
    .hero-title { font-size: 2.6rem !important; }
    .detail-title { font-size: 2rem !important; }
    .glass-card { padding: 1.4rem; }
    [data-testid="stSidebar"] { border-right: none; border-bottom: 1px solid var(--border-subtle); }
}

/* Scrollbar */
::-webkit-scrollbar { width: 9px; }
::-webkit-scrollbar-track { background: var(--bg-void); }
::-webkit-scrollbar-thumb { background: var(--gold); border-radius: 5px; }
::-webkit-scrollbar-thumb:hover { background: var(--gold-bright); }

button:focus, input:focus { outline: 2px solid var(--gold); outline-offset: 2px; }
html { scroll-behavior: smooth; }
</style>
""",
    unsafe_allow_html=True,
)

# =============================
# STATE + ROUTING
# =============================
if "view" not in st.session_state:
    st.session_state.view = "home"
if "selected_tmdb_id" not in st.session_state:
    st.session_state.selected_tmdb_id = None

qp_view = st.query_params.get("view")
qp_id = st.query_params.get("id")
if qp_view in ("home", "details"):
    st.session_state.view = qp_view
if qp_id:
    try:
        st.session_state.selected_tmdb_id = int(qp_id)
        st.session_state.view = "details"
    except:
        pass


def goto_home():
    st.session_state.view = "home"
    st.query_params["view"] = "home"
    if "id" in st.query_params:
        del st.query_params["id"]
    st.rerun()


def goto_details(tmdb_id: int):
    st.session_state.view = "details"
    st.session_state.selected_tmdb_id = int(tmdb_id)
    st.query_params["view"] = "details"
    st.query_params["id"] = str(int(tmdb_id))
    st.rerun()


# =============================
# VERSION-SAFE WIDTH HANDLING
# Different Streamlit versions accept different width kwargs
# (use_container_width vs use_column_width vs neither). Detect
# once via signature inspection instead of relying on exceptions.
# =============================
def _width_kwarg_for(func) -> str:
    try:
        params = inspect.signature(func).parameters
    except (TypeError, ValueError):
        return ""
    if "use_container_width" in params:
        return "use_container_width"
    if "use_column_width" in params:
        return "use_column_width"
    return ""


_IMAGE_WIDTH_KWARG = _width_kwarg_for(st.image)
_BUTTON_WIDTH_KWARG = _width_kwarg_for(st.button)


def show_image(src):
    """Render an image full-width regardless of installed Streamlit version."""
    if _IMAGE_WIDTH_KWARG:
        st.image(src, **{_IMAGE_WIDTH_KWARG: True})
    else:
        st.image(src)


def wide_button(label, key=None):
    """Render a full-width button regardless of installed Streamlit version."""
    kwargs = {"key": key} if key else {}
    if _BUTTON_WIDTH_KWARG:
        kwargs[_BUTTON_WIDTH_KWARG] = True
    return st.button(label, **kwargs)


@st.cache_data(ttl=30)
def api_get_json(path: str, params: Optional[dict] = None):
    try:
        r = requests.get(f"{API_BASE}{path}", params=params, timeout=25)
        if r.status_code >= 400:
            return None, f"HTTP {r.status_code}: {r.text[:300]}"
        return r.json(), None
    except Exception as e:
        return None, f"Request failed: {e}"


def section_header(eyebrow: str, title: str):
    st.markdown(
        f"""
        <div class="section-header">
            <div class="section-eyebrow">{eyebrow}</div>
            <h2 class="section-title">{title}</h2>
            <div class="film-strip film-strip-thin"></div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def poster_grid(cards, cols=6, key_prefix="grid"):
    if not cards:
        st.info("No movies to display.")
        return

    rows = (len(cards) + cols - 1) // cols
    idx = 0
    for r in range(rows):
        colset = st.columns(cols)
        for c in range(cols):
            if idx >= len(cards):
                break
            m = cards[idx]
            idx += 1

            tmdb_id = m.get("tmdb_id")
            title = m.get("title", "Untitled")
            poster = m.get("poster_url")

            with colset[c]:
                st.markdown("<div class='poster-card'>", unsafe_allow_html=True)

                if poster:
                    show_image(poster)
                else:
                    st.write("No poster available")

                st.markdown(
                    f"<div class='movie-title'>{title}</div>", unsafe_allow_html=True
                )

                if st.button("View Details", key=f"{key_prefix}_{r}_{c}_{idx}_{tmdb_id}"):
                    if tmdb_id:
                        goto_details(tmdb_id)

                st.markdown("</div>", unsafe_allow_html=True)


def to_cards_from_tfidf_items(tfidf_items):
    cards = []
    for x in tfidf_items or []:
        tmdb = x.get("tmdb") or {}
        if tmdb.get("tmdb_id"):
            cards.append(
                {
                    "tmdb_id": tmdb["tmdb_id"],
                    "title": tmdb.get("title") or x.get("title") or "Untitled",
                    "poster_url": tmdb.get("poster_url"),
                }
            )
    return cards


def parse_tmdb_search_to_cards(data, keyword: str, limit: int = 24):
    """
    Returns:
      suggestions: list[(label, tmdb_id)]
      cards: list[{tmdb_id,title,poster_url}]
    """
    keyword_l = keyword.strip().lower()

    if isinstance(data, dict) and "results" in data:
        raw = data.get("results") or []
        raw_items = []
        for m in raw:
            title = (m.get("title") or "").strip()
            tmdb_id = m.get("id")
            poster_path = m.get("poster_path")
            if not title or not tmdb_id:
                continue
            raw_items.append(
                {
                    "tmdb_id": int(tmdb_id),
                    "title": title,
                    "poster_url": f"{TMDB_IMG}{poster_path}" if poster_path else None,
                    "release_date": m.get("release_date", ""),
                }
            )

    elif isinstance(data, list):
        raw_items = []
        for m in data:
            tmdb_id = m.get("tmdb_id") or m.get("id")
            title = (m.get("title") or "").strip()
            poster_url = m.get("poster_url")
            if not title or not tmdb_id:
                continue
            raw_items.append(
                {
                    "tmdb_id": int(tmdb_id),
                    "title": title,
                    "poster_url": poster_url,
                    "release_date": m.get("release_date", ""),
                }
            )
    else:
        return [], []

    matched = [x for x in raw_items if keyword_l in x["title"].lower()]
    final_list = matched if matched else raw_items

    suggestions = []
    for x in final_list[:10]:
        year = (x.get("release_date") or "")[:4]
        label = f"{x['title']} ({year})" if year else x["title"]
        suggestions.append((label, x["tmdb_id"]))

    cards = [
        {"tmdb_id": x["tmdb_id"], "title": x["title"], "poster_url": x["poster_url"]}
        for x in final_list[:limit]
    ]
    return suggestions, cards


# =============================
# SIDEBAR
# =============================
with st.sidebar:
    st.markdown("## Cinematrix")
    if wide_button("Home"):
        goto_home()

    st.markdown("---")
    st.markdown("### Collections")
    home_category = st.selectbox(
        "Select category:",
        ["trending", "popular", "top_rated", "now_playing", "upcoming"],
        index=0,
    )
    grid_cols = st.slider("Grid columns", 4, 8, 6)

# =============================
# HERO SECTION
# =============================
st.markdown(
    f"""
    <div class="hero">
        <div class="film-strip"></div>
        <div class="hero-inner">
            <div class="hero-eyebrow">Now Screening</div>
            <h1 class="hero-title">CINEMATRIX</h1>
            <p class="hero-tagline">Discover extraordinary films, explore curated collections,
            and find your next masterpiece — one showing at a time.</p>
            {marquee_lights_html()}
        </div>
        <div class="film-strip"></div>
    </div>
    """,
    unsafe_allow_html=True,
)

# ==========================================================
# VIEW: HOME
# ==========================================================
if st.session_state.view == "home":
    typed = st.text_input(
        "Search movies",
        placeholder="Search by title..."
    )

    st.divider()

    if typed.strip():
        if len(typed.strip()) < 2:
            st.caption("Enter at least 2 characters to search")
        else:
            data, err = api_get_json("/tmdb/search", params={"query": typed.strip()})

            if err or data is None:
                st.error(f"Search unavailable: {err}")
            else:
                suggestions, cards = parse_tmdb_search_to_cards(
                    data, typed.strip(), limit=24
                )

                if suggestions:
                    labels = ["Select a movie"] + [s[0] for s in suggestions]
                    selected = st.selectbox("Results:", labels, index=0)

                    if selected != "Select a movie":
                        label_to_id = {s[0]: s[1] for s in suggestions}
                        goto_details(label_to_id[selected])
                else:
                    st.info("No results found. Try a different search.")

                section_header("Matches Found", "Search Results")
                poster_grid(cards, cols=grid_cols, key_prefix="search_results")

        st.stop()

    section_header("Curated Collection", home_category.replace("_", " ").title())
    st.markdown(
        f"<p class='small-muted'>A hand-picked reel of {home_category.replace('_', ' ')} titles</p>",
        unsafe_allow_html=True,
    )

    home_cards, err = api_get_json(
        "/home", params={"category": home_category, "limit": 24}
    )
    if err or not home_cards:
        st.error(f"Feed unavailable: {err or 'Unknown error'}")
        st.stop()

    poster_grid(home_cards, cols=grid_cols, key_prefix="home_feed")

# ==========================================================
# VIEW: DETAILS
# ==========================================================
elif st.session_state.view == "details":
    tmdb_id = st.session_state.selected_tmdb_id
    if not tmdb_id:
        st.warning("No movie selected.")
        if st.button("Go Back"):
            goto_home()
        st.stop()

    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown("### Feature Presentation")
    with col2:
        if wide_button("Back to Home"):
            goto_home()

    data, err = api_get_json(f"/movie/id/{tmdb_id}")
    if err or not data:
        st.error(f"Could not load details: {err or 'Unknown error'}")
        st.stop()

    left, right = st.columns([1, 2.4], gap="large")

    with left:
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        if data.get("poster_url"):
            show_image(data["poster_url"])
        else:
            st.write("No poster available")
        st.markdown("</div>", unsafe_allow_html=True)

    with right:
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        st.markdown(f"<div class='detail-title'>{data.get('title','')}</div>", unsafe_allow_html=True)

        release = data.get("release_date") or "N/A"
        genres = ", ".join([g["name"] for g in data.get("genres", [])]) or "N/A"

        st.markdown(
            f"""
            <div class='detail-meta'>
                <div class='detail-chip'>
                    <span class='detail-chip-label'>Release Date</span>
                    <span class='detail-chip-value'>{release}</span>
                </div>
                <div class='detail-chip'>
                    <span class='detail-chip-label'>Genres</span>
                    <span class='detail-chip-value'>{genres}</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

        st.markdown("<div class='film-strip film-strip-thin'></div>", unsafe_allow_html=True)
        st.markdown("### Synopsis")
        st.markdown(f"<p class='small-muted'>{data.get('overview') or 'No overview available'}</p>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    if data.get("backdrop_url"):
        section_header("Behind The Scenes", "Featured Still")
        show_image(data["backdrop_url"])

    st.divider()

    title = (data.get("title") or "").strip()
    if title:
        bundle, err2 = api_get_json(
            "/movie/search",
            params={"query": title, "tfidf_top_n": 12, "genre_limit": 12},
        )

        if not err2 and bundle:
            section_header("You Might Also Like", "Similar Movies")
            poster_grid(
                to_cards_from_tfidf_items(bundle.get("tfidf_recommendations")),
                cols=grid_cols,
                key_prefix="details_tfidf",
            )

            section_header("Same Genre", "More Like This")
            poster_grid(
                bundle.get("genre_recommendations", []),
                cols=grid_cols,
                key_prefix="details_genre",
            )
        else:
            st.info("Showing genre-based recommendations.")
            genre_only, err3 = api_get_json(
                "/recommend/genre", params={"tmdb_id": tmdb_id, "limit": 18}
            )
            if not err3 and genre_only:
                poster_grid(
                    genre_only, cols=grid_cols, key_prefix="details_genre_fallback"
                )
            else:
                st.warning("No recommendations available at this time.")
    else:
        st.warning("Cannot compute recommendations without title.")