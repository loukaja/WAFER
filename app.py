import streamlit as st
import clipman
from run import run

st.title("Welcome to WAFER!")

if "template" not in st.session_state:
    st.session_state["template"] = ""


def form_callback(text):
    st.session_state.template = text
    clipman.init()
    clipman.set(st.session_state.template)

with st.container(border=True):
    st.subheader("Form options")
    outer_col1, outer_col2, outer_col3 = st.columns(3)

    with outer_col1:
        review_rows = st.number_input(
            "Review amount", min_value=0, step=1, key="review_rows")
        stub = st.checkbox("Mark article as stub")
    with outer_col2:
        member_rows = st.number_input(
            "Members", min_value=1, step=1, key="member_rows")
        toc = st.checkbox("Generate Table of Contents", value=True)
    with outer_col3:
        class_rows = st.number_input(
            "Class amount", min_value=1, step=1, key="class_rows")
        st.selectbox("Album type", ('Studio', 'Live', 'EP', 'Single', 'Demo'), index=None, placeholder="Choose album type...", key="album_type")

with st.form("Form"):
    st.subheader("Album Info")
    st.text_input("Album URL", key="album_url",
                  placeholder="https://tidal.com/browse/album/...")
    
    st.text_input("Producer", key="producer", help="Who produced the album")
    st.text_input("Recorded", key="recorded", help="When the album was recorded")
    st.text_input("Studio", key="studio", help="Where the album was produced/mixed etc")
    st.text_input("Genre", key="genre", help="Enter album genre, separate multiple genres with comma")

    if review_rows > 0:
        st.subheader(
            "Reviews", help="Enter complete URL! See About for currently supported review pages!")
        for i in range(1, review_rows+1):
            st.text_input(
                label=f"Review {i}", key=f"review_{i}", placeholder="Link to review site")

    st.subheader("Members")
    col1, col2 = st.columns(2)
    for i in range(1, member_rows+1):
        with col1:
            st.text_input(f"Member", key=f"member_{i}",
                          placeholder="FirstName LastName")
        with col2:
            st.text_input(
                "Instrument(s)", key=f"instrument_{i}", placeholder="Guitars, vocals",
                help="If multiple, space out with a comma, ie 'guitar, singing'")

    st.subheader("External links")

    st.text_input("Discogs", key="discogs_url",
                  placeholder="Discogs release (master) URL")
    st.text_input(label="Metal-Archives link", key="metal_archives_url",
                  placeholder="Link to Metal-Archives album page")
    st.text_input("Bandcamp", key="bandcamp_url",
                  placeholder="Bandcamp album page")

    st.subheader("Classes")
    for i in range(1, class_rows+1):
        st.text_input("Class", key=f"class_{i}")

    submitted = st.form_submit_button("Generate")

with st.container(border=True):

    # Initialize wiki_template with an empty string to ensure the text area is visible
    st.text_area(label="Template", height=500, value=st.session_state.template)

if submitted:
    album_info = {}

    album_info['link'] = st.session_state["album_url"]
    album_info['type'] = st.session_state["album_type"]
    album_info['recorded'] = st.session_state["recorded"]
    album_info['producer'] = st.session_state["producer"]
    album_info['studio'] = st.session_state["studio"]
    album_info['genres'] = st.session_state["genre"].split(',')
    album_info['toc'] = toc
    album_info['stub'] = stub

    reviews = []

    for i in range(1, review_rows+1):
        if st.session_state[f"review_{i}"]:
            reviews.append(st.session_state[f"review_{i}"])

    album_info['reviews'] = reviews

    members = []

    for i in range(1, member_rows+1):
        name = st.session_state[f"member_{i}"]
        instrument = st.session_state[f"instrument_{i}"]
        if name and instrument:
            members.append({
                "name": name,
                "instruments": instrument
            })

    album_info['members'] = members

    external_links = [
        {"name": "discogs", "url": st.session_state["discogs_url"]},
        {"name": "metal_archives",
            "url": st.session_state["metal_archives_url"]},
        {"name": "bandcamp", "url": st.session_state["bandcamp_url"]}
    ]

    album_info['external_links'] = external_links

    classes = []

    for i in range(1, class_rows+1):
        if st.session_state[f"class_{i}"]:
            classes.append(st.session_state[f"class_{i}"])

    album_info['classes'] = classes

    wiki_template = run(album_info)
    form_callback(wiki_template)
    st.rerun()
