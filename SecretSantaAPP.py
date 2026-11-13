import streamlit as st
import random

# Set page configuration
st.set_page_config(page_title="Secret Santa Matching", page_icon="🎄", layout="centered")

st.title("🎄 Secret Santa Secret Draw 🎄")
st.write("Enter your name below to reveal who you are buying a gift for. No one else will see your match!")

# Define the participants list
PARTICIPANTS = ["Grandpa", "Uncle Jim", "Uncle Scott", "Uncle Lee", "Aunt Cathie", "Nia", "Michael", "John", "Aunt Stacy", "Riley"]

# Securely initialize matches in session state so it's hidden from the UI
if "matches" not in st.session_state:
    # Generate unique, non-self matches
    while True:
        targets = PARTICIPANTS.copy()
        random.shuffle(targets)
        if not any(giver == receiver for giver, receiver in zip(PARTICIPANTS, targets)):
            st.session_state["matches"] = dict(zip(PARTICIPANTS, targets))
            break

# User selection
selected_user = st.selectbox("Select your name:", ["-- Choose --"] + PARTICIPANTS)

if selected_user != "-- Choose --":
    st.warning("Make sure no one is looking over your shoulder!")
    
    # Use button to reveal match so it is not visible instantly
    if st.button(f"Reveal my match as {selected_user}"):
        assigned_match = st.session_state["matches"][selected_user]
        st.success(f"🎁 Hi {selected_user}, you are the Secret Santa for: **{assigned_match}**!")
        st.balloons()