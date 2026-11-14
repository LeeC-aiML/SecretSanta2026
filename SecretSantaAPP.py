import streamlit as st
import random
import csv
import io
from github import Github, GithubException

# Set page configuration
st.set_page_config(page_title="Secret Santa Matching", page_icon="🎄", layout="centered")

st.title("🎄 Secret Santa Secret Draw 🎄")
st.write("Enter your name below to reveal who you are buying a gift for. No one else will see your match!")

# Define the participants list
PASSWORDS = {
    "Grandpa":"gp58dl",
    "Uncle Jim":"uj15jc",
    "Uncle Scott":"us45sc",
    "Uncle Lee":"ul05lc",
    "Aunt Cathie":"ac84cp",
    "Nia":"ni12nw",
    "Michael":"mi81mc",
    "John":"jo82jp",
    "Aunt Stacy":"as15sc",
    "Riley":"ri12rc",
    "Gabby":"ga81gc"
    }
PARTICIPANTS = list(PASSWORDS.keys())
CSV_FILE = "secret_santa_matches.csv"

# Securely load credentials and diagnose issues
try:
    if "GITHUB_TOKEN" not in st.secrets:
        st.error("🔑 Missing 'GITHUB_TOKEN' in Streamlit Secrets!")
        st.stop()
    if "GITHUB_REPO" not in st.secrets:
        st.error("📂 Missing 'GITHUB_REPO' in Streamlit Secrets!")
        st.stop()

    GITHUB_TOKEN = st.secrets["GITHUB_TOKEN"]
    GITHUB_REPO = st.secrets["GITHUB_REPO"] 
    BRANCH = st.secrets.get("GITHUB_BRANCH", "main")
    
    g = Github(GITHUB_TOKEN)
    repo = g.get_repo(GITHUB_REPO)
except Exception as e:
    st.error(f"❌ Configuration error: {str(e)}")
    st.info("Double-check that your secrets are correctly configured under Settings > Secrets on Streamlit Cloud.")
    st.stop()

def load_matches_from_github():
    try:
        file_content = repo.get_contents(CSV_FILE, ref=BRANCH)
        decoded_content = file_content.decoded_content.decode('utf-8')
        reader = csv.reader(io.StringIO(decoded_content))
        return {row[0]: row[1] for row in reader if row}
    except GithubException as e:
        # File doesn't exist yet
        if e.status == 404:
            return None
        raise e
    
def save_matches_to_github(matches):
    # Generate CSV string
    output = io.StringIO()
    writer = csv.writer(output)
    for giver, receiver in matches.items():
        writer.writerow([giver, receiver])
    csv_data = output.getvalue()
    
    try:
        # Try to update if it exists
        file_content = repo.get_contents(CSV_FILE, ref=BRANCH)
        repo.update_file(CSV_FILE, "Update Secret Santa matches", csv_data, file_content.sha, branch=BRANCH)
    except GithubException as e:
        if e.status == 404:
            # Create file if it does not exist
            repo.create_file(CSV_FILE, "Create Secret Santa matches", csv_data, branch=BRANCH)
        else:
            raise e

# Securely initialize or load matches
if "matches" not in st.session_state:
    with st.spinner("Loading secure configurations..."):
        try:
            saved_matches = load_matches_from_github()
            if saved_matches:
                st.session_state["matches"] = saved_matches
            else:
                # Generate new matches and save them straight to GitHub
                while True:
                    targets = PARTICIPANTS.copy()
                    random.shuffle(targets)
                    if not any(giver == receiver for giver, receiver in zip(PARTICIPANTS, targets)):
                        generated_matches = dict(zip(PARTICIPANTS, targets))
                        st.session_state["matches"] = generated_matches
                        save_matches_to_github(generated_matches)
                        break
        except Exception as ex:
            st.error(f"An error occurred accessing GitHub: {ex}")
            st.stop()

# User selection
selected_user = st.selectbox("Select your name:", ["-- Choose --"] + PARTICIPANTS)

if selected_user != "-- Choose --":
    # Require password input
    password_input = st.text_input(f"Enter the private password for {selected_user}:", type="password")

    if password_input:
        # Check if password is correct
        if password_input == PASSWORDS[selected_user]:
            st.warning("Make sure no one is looking over your shoulder!")

            # Use button to reveal match so it is not visible instantly
            if st.button(f"Reveal my match as {selected_user}"):
                assigned_match = st.session_state["matches"][selected_user]
                st.success(f"🎁 Hi {selected_user}, you are the Secret Santa for: **{assigned_match}**!")
                st.balloons()
        else:
            st.error("Incorrect password. Please try again.")