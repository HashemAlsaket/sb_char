import streamlit as st
import requests
import pandas as pd
import os
import json
import time
import openai

# --- SETUP ---
st.set_page_config(page_title="Player Perception Analyzer", layout="wide")

# --- CUSTOM THEME ---
primary_color = "#00c2cb"  # Light blue/teal from logo
secondary_color = "#ffffff"  # White from logo
accent_color = "#121212"   # Dark background
background_color = "#0a0a0a"  # Near black background

# Custom CSS with theme to match logo
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
    div[data-testid="stMetricValue"] {{
        color: {primary_color};
        font-weight: bold;
    }}
    div[data-testid="stExpander"] {{
        border-left-color: {primary_color} !important;
    }}
    .stTabs [data-baseweb="tab-list"] {{
        gap: 24px;
    }}
    .stTabs [data-baseweb="tab"] {{
        height: 50px;
        white-space: pre-wrap;
        background-color: {accent_color};
        border-radius: 4px 4px 0 0;
        gap: 1px;
        padding-top: 10px;
        padding-bottom: 10px;
    }}
    .stTabs [aria-selected="true"] {{
        background-color: {primary_color};
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
    .main-header {{
        font-size: 2.5rem;
        color: {primary_color};
        text-align: center;
        margin-bottom: 1rem;
        font-weight: 800;
    }}
    .sub-header {{
        font-size: 1.5rem;
        color: {secondary_color};
        margin-bottom: 2rem;
        text-align: center;
        opacity: 0.8;
    }}
    .insight-box {{
        background-color: rgba(10, 10, 10, 0.6);
        border-left: 5px solid {primary_color};
        padding: 1.5rem;
        margin-bottom: 1rem;
        border-radius: 5px;
    }}
    .positive {{
        color: #00ff9d;
        font-weight: bold;
    }}
    .neutral {{
        color: {secondary_color};
        font-weight: bold;
    }}
    .negative {{
        color: #ff5e5e;
        font-weight: bold;
    }}
    .metric-card {{
        background-color: rgba(10, 10, 10, 0.6);
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
        padding: 1rem;
        text-align: center;
        border: 1px solid rgba(0, 194, 203, 0.2);
    }}
    .thinking-process {{
        background-color: rgba(10, 10, 10, 0.6);
        border-left: 5px solid {primary_color};
        padding: 1rem;
        margin-bottom: 1rem;
        font-family: monospace;
        border-radius: 5px;
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
    /* Login form */
    div.login-form {{
        max-width: 500px;
        margin: 0 auto;
        padding: 30px;
        background-color: rgba(18, 18, 18, 0.8);
        border-radius: 10px;
        border: 1px solid rgba(0, 194, 203, 0.3);
    }}
    div.login-header {{
        text-align: center;
        margin-bottom: 20px;
    }}
</style>
""", unsafe_allow_html=True)

# --- LOGIN FLOW ---
def login():
    st.session_state["authenticated"] = False

    st.markdown("<div class='login-form'>", unsafe_allow_html=True)
    st.markdown("<div class='login-header'>", unsafe_allow_html=True)
    st.image("https://i.ibb.co/RvJL8PK/sports-analytics-logo.png", width=120)
    st.markdown("</div>", unsafe_allow_html=True)
    
    st.markdown("<h2 style='text-align: center; color: #00c2cb;'>Player Perception Analyzer</h2>", unsafe_allow_html=True)
    st.write("Please log in to continue")
    
    with st.form("Login"):
        user = st.text_input("Username")
        pw = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Login", use_container_width=True)

        if submitted:
            # Use appropriate credential checking based on your setup
            try:
                if user == st.secrets["credentials"]["username"] and pw == st.secrets["credentials"]["password"]:
                    st.session_state["authenticated"] = True
                else:
                    st.error("Invalid credentials")
            except Exception:
                # Fallback for local development without secrets
                if user == "admin" and pw == "password":
                    st.session_state["authenticated"] = True
                else:
                    st.error("Invalid credentials")
    
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
        st.error(f"Error searching for player info: {str(e)}")
        return []

def analyze_with_openai(player_name, search_results, thinking_container=None):
    """Analyze player perception using OpenAI"""
    # Set OpenAI API key
    openai.api_key = st.session_state["openai_api_key"]
    
    if thinking_container:
        thinking_container.markdown("### LLM Agent Thinking Process")
        thinking_container.markdown("#### 1. Organizing search results")
    
    # Organize search results by category
    general_info = [r for r in search_results if r.get('source') == 'general']
    news_articles = [r for r in search_results if r.get('source') == 'news']
    
    if thinking_container:
        thinking_container.markdown(f"- Found {len(general_info)} general information results")
        thinking_container.markdown(f"- Found {len(news_articles)} news articles")
        thinking_container.markdown("#### 2. Preparing data for analysis")
    
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
    
    if thinking_container:
        thinking_container.markdown("#### 3. Sending to LLM for analysis")
    
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

    if thinking_container:
        thinking_container.markdown("#### 4. Generating analysis")
        
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
        
        if thinking_container:
            thinking_container.markdown("#### 5. Analysis complete")
            thinking_container.markdown("The LLM has successfully analyzed the player perception data")
            
        return {
            'analysis': analysis_text,
            'raw_data': search_results
        }
        
    except Exception as e:
        if thinking_container:
            thinking_container.markdown(f"**Error:** {str(e)}")
        return {
            'error': str(e)
        }

# Check authentication state
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

# Handle login flow
if not st.session_state["authenticated"]:
    login()
    st.stop()

# --- INITIALIZE API KEYS ---
if "openai_api_key" not in st.session_state:
    # Try to get from secrets
    try:
        st.session_state["openai_api_key"] = st.secrets["OPENAI_API_KEY"]
    except Exception:
        # Will prompt user to enter API key later
        st.session_state["openai_api_key"] = None

if "searchapi_key" not in st.session_state:
    # Try to get from secrets
    try:
        st.session_state["searchapi_key"] = st.secrets["SEARCHAPI_API_KEY"]
    except Exception:
        # Will prompt user to enter API key later
        st.session_state["searchapi_key"] = None

# --- HEADER WITH LOGO ---
col1, col2 = st.columns([1, 5])
with col1:
    st.image("https://i.ibb.co/RvJL8PK/sports-analytics-logo.png", width=80)
with col2:
    st.title("Player Perception Analyzer")

# --- API KEY CHECKS ---
# OpenAI API Key input (if not already set)
if not st.session_state["openai_api_key"]:
    api_key = st.sidebar.text_input("OpenAI API Key", type="password")
    if api_key:
        st.session_state["openai_api_key"] = api_key
    else:
        st.warning("Please enter your OpenAI API key in the sidebar to continue.")
        st.stop()

# SearchAPI Key input (if not already set)
if not st.session_state["searchapi_key"]:
    searchapi_key = st.sidebar.text_input("SearchAPI Key", type="password")
    if searchapi_key:
        st.session_state["searchapi_key"] = searchapi_key
    else:
        st.warning("Please enter your SearchAPI key in the sidebar to continue.")
        st.stop()

# --- SIDEBAR ---
st.sidebar.image("https://i.ibb.co/RvJL8PK/sports-analytics-logo.png", width=80)
st.sidebar.header("Player Analysis")

# --- MAIN APP ---
st.markdown("<div style='background-color: rgba(10, 10, 10, 0.6); padding: 20px; border-radius: 10px; border: 1px solid rgba(0, 194, 203, 0.2);'>", unsafe_allow_html=True)
player_name = st.text_input("Enter Player Name", "Patrick Mahomes")

analyze_col1, analyze_col2, analyze_col3 = st.columns([1, 2, 1])
with analyze_col2:
    analyze_button = st.button("Analyze Player Perception", type="primary", use_container_width=True)
st.markdown("</div>", unsafe_allow_html=True)

# Only process analysis when button is clicked
if analyze_button:
    # Create a container for the thinking process
    thinking_container = st.expander("Agent Thinking Process", expanded=True)
    
    # Step 1: Search for player information
    with st.spinner(f"Searching for information about {player_name}..."):
        thinking_container.markdown("### Search Process")
        thinking_container.markdown(f"Searching for information about {player_name} using SearchAPI...")
        
        search_results = search_player_info(player_name)
        
        if not search_results:
            st.error(f"No results found for {player_name}. Please check the name and try again.")
            st.stop()
        else:
            thinking_container.markdown(f"Found {len(search_results)} relevant results")
    
    # Step 2: Analyze the search results with OpenAI
    with st.spinner("Analyzing player perception with OpenAI..."):
        analysis_result = analyze_with_openai(player_name, search_results, thinking_container)
        
        if "error" in analysis_result:
            st.error(f"Error during analysis: {analysis_result['error']}")
            st.stop()
    
    # Display results
    st.markdown(f"## Perception Analysis for {player_name}")
    
    # Display search results
    with st.expander("View Search Results", expanded=False):
        st.markdown("### Information Sources")
        for i, result in enumerate(search_results):
            st.markdown(f"**Source {i+1}:** {result.get('title', 'No title')}")
            st.markdown(f"*{result.get('snippet', 'No content')}*")
            if 'link' in result and result['link']:
                st.markdown(f"[Link]({result['link']})")
            st.markdown("---")
    
    # Display analysis
    st.markdown("<div style='background-color: rgba(10, 10, 10, 0.6); padding: 20px; border-radius: 10px; border: 1px solid rgba(0, 194, 203, 0.2);'>", unsafe_allow_html=True)
    st.markdown("### Analysis")
    st.markdown(analysis_result['analysis'])
    st.markdown("</div>", unsafe_allow_html=True)