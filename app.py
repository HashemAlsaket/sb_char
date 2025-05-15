import streamlit as st
import requests
import pandas as pd
import os
import json
import time
import openai

# --- SETUP ---
st.set_page_config(page_title="Player Perception Dashboard", layout="wide")

# --- CUSTOM THEME ---
primary_color = "#00c2cb"  # Light blue/teal from logo
secondary_color = "#ffffff"  # White from logo
accent_color = "#121212"   # Dark background
background_color = "#0a0a0a"  # Near black background

# Custom CSS with theme to match logo - simplified for clarity
st.markdown(f"""
<style>
    .stApp {{
        background-color: {background_color};
        color: {secondary_color};
    }}
    .stButton>button {{
        background-color: {primary_color};
        color: {accent_color};
        font-weight: bold;
        border: none;
        border-radius: 20px;
    }}
    .stButton>button:hover {{
        background-color: {secondary_color};
        color: {accent_color};
    }}
    h1, h2, h3, h4, h5, h6 {{
        color: {secondary_color};
    }}
    .stSidebar .stButton>button {{
        width: 100%;
    }}
    a {{
        color: {primary_color};
    }}
    /* Text input styling */
    div[data-baseweb="input"] input {{
        background-color: rgba(10, 10, 10, 0.6) !important;
        color: {secondary_color} !important;
        border: 1px solid {primary_color} !important;
        border-radius: 10px !important;
    }}
    /* Expander styling */
    div[data-testid="stExpander"] {{
        background-color: rgba(18, 18, 18, 0.6);
        border-radius: 10px;
        border: 1px solid rgba(0, 194, 203, 0.2);
    }}
    /* Markdown text */
    div.stMarkdown p {{
        color: {secondary_color};
    }}
    /* Spinner */
    div.stSpinner > div {{
        border-top-color: {primary_color} !important;
    }}
    /* Sign in form */
    div.signin-form {{
        max-width: 500px;
        margin: 0 auto;
        padding: 30px;
        background-color: rgba(18, 18, 18, 0.8);
        border-radius: 10px;
        border: 1px solid rgba(0, 194, 203, 0.3);
    }}
    div.signin-header {{
        text-align: center;
        margin-bottom: 20px;
    }}
    /* Analysis container */
    .analysis-container {{
        background-color: rgba(18, 18, 18, 0.6);
        border-radius: 10px;
        padding: 20px;
        margin-top: 20px;
        border: 1px solid rgba(0, 194, 203, 0.2);
    }}
    /* Remove padding from form inputs */
    div[data-baseweb="base-input"] {{
        margin-bottom: 10px;
    }}
</style>
""", unsafe_allow_html=True)

# --- SIGN IN FLOW ---
def show_signin():
    st.session_state["authenticated"] = False

    st.markdown("<div class='signin-form'>", unsafe_allow_html=True)
    st.markdown("<div class='signin-header'>", unsafe_allow_html=True)
    st.image("char_img.png", width=120)
    st.markdown("</div>", unsafe_allow_html=True)
    
    st.markdown("<h2 style='text-align: center; color: #00c2cb;'>Player Perception Dashboard</h2>", unsafe_allow_html=True)
    st.write("Please sign in with your team credentials")
    
    with st.form("SignIn"):
        user = st.text_input("Team Email")
        pw = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Sign In", use_container_width=True)

        if submitted:
            # Use appropriate credential checking based on your setup
            try:
                if user == st.secrets["credentials"]["username"] and pw == st.secrets["credentials"]["password"]:
                    st.session_state["authenticated"] = True
                else:
                    st.error("Invalid credentials. Please try again or contact technical support.")
            except Exception:
                # Fallback for local development without secrets
                if user == "admin" and pw == "password":
                    st.session_state["authenticated"] = True
                else:
                    st.error("Invalid credentials. Please try again or contact technical support.")
    
    st.markdown("</div>", unsafe_allow_html=True)

# --- FUNCTIONS ---
def search_player_info(player_name, num_results=5):
    """Search for information about an NFL player using SearchAPI"""
    SEARCH_URL = "https://www.searchapi.io/api/v1/search"
    
    # General info search
    search_results = []
    
    try:
        # General info search
        general_params = {
            "engine": "google",
            "q": f"{player_name} nfl player stats career info",
            "num": num_results
        }
        
        general_response = requests.get(
            SEARCH_URL, 
            params=general_params, 
            headers={"Authorization": f"Bearer {st.session_state['searchapi_key']}"}
        )
        
        if general_response.status_code == 200:
            general_data = general_response.json()
            for result in general_data.get("organic_results", []):
                search_results.append({
                    'title': result.get("title", "No title"),
                    'link': result.get("link", ""),
                    'snippet': result.get("snippet", "No snippet"),
                    'source': 'general'
                })
        
        # News search
        news_params = {
            "engine": "google",
            "q": f"{player_name} nfl news recent",
            "num": num_results,
            "tbm": "nws"  # News search
        }
        
        news_response = requests.get(
            SEARCH_URL, 
            params=news_params, 
            headers={"Authorization": f"Bearer {st.session_state['searchapi_key']}"}
        )
        
        if news_response.status_code == 200:
            news_data = news_response.json()
            for result in news_data.get("organic_results", []):
                search_results.append({
                    'title': result.get("title", "No title"),
                    'link': result.get("link", ""),
                    'snippet': result.get("snippet", "No snippet"),
                    'source': 'news'
                })
        
        return search_results
    except Exception as e:
        st.error(f"Error gathering information: {str(e)}")
        return []

def analyze_with_openai(player_name, search_results):
    """Analyze player perception using OpenAI"""
    # Set OpenAI API key
    openai.api_key = st.session_state["openai_api_key"]
    
    # Format the search results for the LLM
    formatted_articles = []
    
    for idx, result in enumerate(search_results):
        formatted_articles.append(
            f"Article {idx+1} ({result.get('source', 'unknown')}):\n"
            f"Title: {result.get('title', 'No title')}\n"
            f"Content: {result.get('snippet', 'No content')}\n"
        )
    
    # Join formatted results with newlines
    articles_text = "\n\n".join(formatted_articles)
    
    # Create the prompt for the LLM
    prompt = f"""
You are analyzing news coverage and information for NFL player {player_name}. Given the following articles, create a detailed character report.

Articles:
{articles_text}

Your character report should include:

1. Executive Summary
- Overall public perception (positive, negative, or mixed with approximate percentages)
- 1-2 paragraph summary of how the player is viewed by the public

2. Key Perception Themes
- Identify 3-5 main themes in how the player is discussed
- For each theme, provide evidence from the articles

3. Fan vs Media Perception
- Analyze any differences between how fans perceive the player vs official media
- Provide examples of these differences

4. On-Field vs Off-Field Reputation
- Compare the player's reputation for their athletic performance vs their character off the field
- Include specific examples

5. Reputation Strengths & Weaknesses
- List the strongest and weakest aspects of the player's public image
- Include quotes or paraphrases from the articles as evidence
"""
        
    try:
        # Call OpenAI API
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an expert NFL analyst specializing in player perception and reputation analysis."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.5
        )
        
        analysis_text = response.choices[0].message.content
            
        return {
            'analysis': analysis_text,
            'raw_data': search_results
        }
        
    except Exception as e:
        return {
            'error': str(e)
        }

# --- AUTHENTICATION CHECK ---
# Check authentication state
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

# Handle sign in flow
if not st.session_state["authenticated"]:
    show_signin()
    st.stop()

# --- INITIALIZE API KEYS SILENTLY ---
if "openai_api_key" not in st.session_state:
    # Try to get from secrets
    try:
        st.session_state["openai_api_key"] = st.secrets["OPENAI_API_KEY"]
    except Exception:
        st.session_state["openai_api_key"] = None

if "searchapi_key" not in st.session_state:
    # Try to get from secrets
    try:
        st.session_state["searchapi_key"] = st.secrets["SEARCHAPI_API_KEY"]
    except Exception:
        st.session_state["searchapi_key"] = None

# Silently check if API keys are available
api_keys_available = (st.session_state["openai_api_key"] is not None and 
                     st.session_state["searchapi_key"] is not None)

# --- HEADER WITH LOGO ---
col1, col2 = st.columns([1, 6])
with col1:
    st.image("char_img.png", width=80)
with col2:
    st.title("Player Perception Dashboard")

# --- MAIN APP ---
player_name = st.text_input("Enter Player Name", "Patrick Mahomes")

analyze_col1, analyze_col2, analyze_col3 = st.columns([1, 2, 1])
with analyze_col2:
    analyze_button = st.button("Generate Report", type="primary", use_container_width=True)

# Only process analysis when button is clicked
if analyze_button:
    if not api_keys_available:
        st.error("System configuration error. Please contact technical support.")
        st.stop()
        
    with st.spinner(f"Generating comprehensive report for {player_name}..."):
        # Step 1: Search for player information (without showing technical details)
        search_results = search_player_info(player_name)
        
        if not search_results:
            st.error(f"Unable to find sufficient information for {player_name}. Please check the spelling or try another player.")
            st.stop()
        
        # Step 2: Analyze the search results with OpenAI (without technical details)
        analysis_result = analyze_with_openai(player_name, search_results)
        
        if "error" in analysis_result:
            st.error(f"Error generating report: {analysis_result['error']}")
            st.stop()
    
    # Display results
    st.markdown(f"## Player Report: {player_name}")
    
    # Display analysis in a clean container
    st.markdown("<div class='analysis-container'>", unsafe_allow_html=True)
    st.markdown(analysis_result['analysis'])
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Sources at the bottom in an expander for technical staff
    with st.expander("Sources and References", expanded=False):
        st.markdown("### Information Sources")
        for i, result in enumerate(search_results):
            st.markdown(f"**Source {i+1}:** {result.get('title', 'No title')}")
            if 'link' in result and result['link']:
                st.markdown(f"[Link]({result['link']})")
            st.markdown("---")