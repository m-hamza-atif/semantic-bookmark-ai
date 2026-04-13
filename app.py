import streamlit as st
import requests
import os

# Uses the cloud URL if it exists, otherwise falls back to localhost for your own testing
API_URL = os.getenv("API_URL", "http://127.0.0.1:8000/api/v1")

st.set_page_config(page_title="Semantic Bookmark AI", page_icon="🔖")
st.title("🔖 Semantic Bookmark AI")

def get_bookmarks() -> list[dict]:
    """Fetches bookmarks metadata from backend."""
    try:
        response = requests.get(f"{API_URL}/bookmarks")
        if response.status_code == 200:
            return response.json().get("bookmarks", [])
    except requests.exceptions.ConnectionError:
        return []
    return []

# === SIDEBAR FOR ADDING BOOKMARKS ===
with st.sidebar:
    st.header("Add to Knowledge Base")
    new_url = st.text_area("Paste Article URL:", height=100)
    
    if st.button("Save Bookmark", type="primary"):
        cleaned_url = new_url.strip()

        if not cleaned_url:
            st.warning("Please enter a URL.")
        else:
            with st.spinner("Saving bookmark..."):
                try:
                    # Hitting the FastAPI POST /bookmarks route
                    response = requests.post(f"{API_URL}/bookmarks", json={"url": cleaned_url})
                    if response.status_code == 200:
                        st.success("Bookmark saved successfully!")
                    else:
                        st.error(response.json().get('detail', 'Unknown error'))
                except requests.exceptions.ConnectionError:
                    st.error("Cannot currently connect to backend.")
    
    st.divider()
    st.subheader("Saved Bookmarks")
    bookmarks = get_bookmarks()

    with st.container(height=100, border=True):
        if bookmarks:
            for idx, bookmark in enumerate(bookmarks, start=1):
                bookmark_url = bookmark.get("url", "")
                bookmark_title = bookmark.get("title") or "(No title retrieved)"
                idx_col, link_col = st.columns([1, 9], gap="small")
                idx_col.markdown(f"{idx}.")
                link_col.link_button(
                    label=bookmark_title,
                    url=bookmark_url,
                    use_container_width=True,
                )
        else:
            st.caption("No bookmarks to display yet.")

    st.divider()
    st.caption("**Disclaimer:** The full conversation is visible, but the assistant does not remember earlier messages when responding.", text_alignment="justify")

# === MAIN CHAT INTERFACE ===

# 1. Initialize chat history in session state
if "messages" not in st.session_state:
    # st.session_state.messages = [{"role": "assistant", "content": "Hello! Upload a bookmark (web articles, wikipedia pages...) and ask me anything about them."}]
    st.session_state.messages = [{
        "role": "assistant", 
        "content": "Welcome to your Semantic Knowledge Base!\n\nI am an AI assistant strictly grounded in the articles you save. Paste a URL in the sidebar to build your library, then ask me related questions!"
    }]
    # Messages is a list of dictionaries for preserving chat conversation

# 2. Display the chat messages on screen
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 3. Handle New User Input
prompt = st.chat_input("Ask a question about your bookmarks...")
if prompt:
    # Show user message on screen and save it to state
    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    # 4. Fetch AI response from Backend
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                # Hitting the FastAPI POST /search route
                response = requests.post(f"{API_URL}/search", json={"query": prompt})
                
                if response.status_code == 200:
                    data = response.json()
                    answer = data["answer"]
                    sources = data["sources_used"]
                    
                    # Show AI response on screen and save it to state
                    st.markdown(answer)
                    st.caption(f"Sources checked: {sources}")
                    st.session_state.messages.append({"role": "assistant", "content": answer})
                else:
                    err_msg = response.json().get('detail', 'Unknown error')
                    st.error(err_msg)
                    
            except requests.exceptions.ConnectionError:
                st.error("Cannot currently connect to backend.")