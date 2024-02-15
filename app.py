import streamlit as st
from run import run

st.title("Welcome to WAFER!")
outer_col1, outer_col2 = st.columns(2)

with outer_col1:
    review_rows = st.number_input(
        "Review amount", min_value=0, step=1, key="review_rows")
with outer_col2:
    member_rows = st.number_input(
        "Members", min_value=1, step=1, key="member_rows")

with st.form("Form"):
    st.subheader("Album Info")
    st.text_input("Album URL", key="album_url",
                  placeholder="https://tidal.com/browse/album/...")

    if review_rows > 0:
        st.subheader(
            "Reviews", help="Enter complete URL!. See About for currently supported review pages!")
        for i in range(1, review_rows+1):
            st.text_input(
                label=f"Review {i}", key=f"review_{i}", placeholder="Link to review site")

    st.subheader("Members")
    col1, col2 = st.columns(2)
    for i in range(1, member_rows+1):
        with col1:
            st.text_input(f"Member {i}", key=f"member_{i}")
        with col2:
            st.text_input(
                "Instrument(s)", key=f"instrument_{i}",
                help="If multiple, space out with a comma, ie 'guitar, singing'")

    st.subheader("External links")

    st.text_input("Discogs", key="discogs_url",
                  placeholder="Discogs release (master) URL")
    st.text_input(label="Metal-Archives link", key="metal_archives_url",
                  placeholder="Link to Metal-Archives album page")
    st.text_input("Bandcamp", key="bandcamp_url",
                  placeholder="Discogs album page")

    submitted = st.form_submit_button("Generate")

if submitted:
    link = st.session_state["album_url"]

    reviews = []

    for i in range(1, review_rows+1):
        if st.session_state[f"review_{i}"]:
            reviews.append(st.session_state[f"review_{i}"])

    members = []

    for i in range(1, member_rows+1):
        name = st.session_state[f"member_{i}"]
        instrument = st.session_state[f"instrument_{i}"]
        if name and instrument:
            members.append({
                "name": name,
                "instruments": instrument
            })

    external_links = [
        {"name": "discogs", "url": st.session_state["discogs_url"]},
        {"name": "metal_archives",
            "url": st.session_state["metal_archives_url"]},
        {"name": "bandcamp", "url": st.session_state["bandcamp_url"]}
    ]

    run(link, reviews, members, external_links)
