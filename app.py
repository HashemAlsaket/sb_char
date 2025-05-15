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
        border-radius: 4px;
        padding: 10px 15px;
        font-size: 16px;
    }}
    .stButton>button:hover {{
        background-color: {secondary_color};
        color: {accent_color};
    }}
    /* Form submit button - make it very clear */
    button[kind="primaryFormSubmit"] {{
        background-color: {primary_color} !important;
        color: {background_color} !important;
        border: none !important;
        padding: 12px 20px !important;
        font-size: 16px !important;
        font-weight: 600 !important;
        letter-spacing: 1px !important;
        margin-top: 15px !important;
    }}
    button[kind="primaryFormSubmit"]:hover {{
        background-color: {secondary_color} !important;
        color: {background_color} !important;
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
        background-color: rgba(40, 40, 40, 0.6) !important;
        color: {secondary_color} !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
        border-radius: 4px !important;
        padding: 10px !important;
    }}
    /* Form field focus */
    div[data-baseweb="input"]:focus-within input {{
        border-color: {primary_color} !important;
    }}
    /* Expander styling */
    div[data-testid="stExpander"] {{
        background-color: rgba(40, 40, 40, 0.6);
        border-radius: 4px;
    }}
    /* Markdown text */
    div.stMarkdown p {{
        color: {secondary_color};
    }}
    /* Spinner */
    div.stSpinner > div {{
        border-top-color: {primary_color} !important;
    }}
    /* Analysis container */
    .analysis-container {{
        background-color: rgba(40, 40, 40, 0.6);
        border-radius: 4px;
        padding: 20px;
        margin-top: 20px;
    }}
    /* Remove excess padding */
    div[data-baseweb="base-input"] {{
        margin-bottom: 15px;
    }}
    /* Error message styling */
    div[data-testid="stAlert"] {{
        background-color: rgba(220, 50, 50, 0.2);
        color: #ff6b6b;
        border: 1px solid rgba(220, 50, 50, 0.3);
        border-radius: 4px;
    }}
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {{
        gap: 5px;
        background-color: rgba(30, 30, 30, 0.3);
        border-radius: 4px;
        padding: 5px;
    }}
    .stTabs [data-baseweb="tab"] {{
        height: auto;
        white-space: normal;
        background-color: rgba(50, 50, 50, 0.5);
        border-radius: 4px;
        padding: 8px 16px;
        font-size: 14px;
    }}
    .stTabs [aria-selected="true"] {{
        background-color: {primary_color};
        color: {accent_color};
    }}
    /* Tab content */
    .stTabs [data-baseweb="tab-panel"] {{
        padding: 20px;
        background-color: rgba(40, 40, 40, 0.4);
        border-radius: 0 0 4px 4px;
        border-top: 2px solid {primary_color};
        margin-top: -2px;
    }}
    /* Executive summary block */
    .executive-summary {{
        padding: 15px;
        background-color: rgba(40, 40, 40, 0.3);
        border-left: 3px solid {primary_color};
        margin-bottom: 20px;
    }}
</style>
""", unsafe_allow_html=True)

# --- SIGN IN FLOW ---
def show_signin():
    st.session_state["authenticated"] = False

    # Clean, modern sign-in form
    col1, col2, col3 = st.columns([1, 3, 1])
    with col2:
        st.image("char_img.png", width=100)
        st.markdown("<h2 style='text-align: center; color: #00c2cb; margin-bottom: 20px;'>Player Perception Dashboard</h2>", unsafe_allow_html=True)
        
        # Simple form with clear instructions
        st.markdown("<p style='text-align: center; margin-bottom: 25px;'>Enter your credentials to access the dashboard</p>", unsafe_allow_html=True)
        
        # Create form with clearer fields
        with st.form("SignIn", clear_on_submit=False):
            user = st.text_input("Email")
            pw = st.text_input("Password", type="password")
            
            # Large, clearly labeled button
            st.markdown("<p style='text-align: center; margin-top: 30px;'>", unsafe_allow_html=True)
            login_button = st.form_submit_button("SIGN IN", use_container_width=True)
            st.markdown("</p>", unsafe_allow_html=True)

            if login_button:
                # Use appropriate credential checking based on your setup
                try:
                    if user == st.secrets["credentials"]["username"] and pw == st.secrets["credentials"]["password"]:
                        st.session_state["authenticated"] = True
                    else:
                        st.error("Invalid credentials. Please try again.")
                except Exception:
                    # Fallback for local development without secrets
                    if user == "admin" and pw == "password":
                        st.session_state["authenticated"] = True
                    else:
                        st.error("Invalid credentials. Please try again.")

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

Your character report must follow this EXACT format for proper parsing:

1. EXECUTIVE_SUMMARY
[Write a 1-2 paragraph executive summary of the player's overall public perception. Include approximate percentages for positive, negative, or mixed perception.]

2. PERCEPTION_THEMES
[Identify exactly 4 main themes in how the player is discussed. Number each theme and give it a clear title.]

3. THEME_1_DETAILS
[Provide detailed analysis of the first theme with specific evidence and examples.]

4. THEME_2_DETAILS
[Provide detailed analysis of the second theme with specific evidence and examples.]

5. THEME_3_DETAILS
[Provide detailed analysis of the third theme with specific evidence and examples.]

6. THEME_4_DETAILS
[Provide detailed analysis of the fourth theme with specific evidence and examples.]

7. FAN_VS_MEDIA
[Analyze differences between fan perception vs media perception with examples.]

8. ON_VS_OFF_FIELD
[Compare on-field reputation vs off-field character with specific examples.]

9. STRENGTHS_WEAKNESSES
[List the strongest and weakest aspects of the player's public image with evidence.]

Make sure to use the exact section headers as shown above, as they will be used for parsing the response.
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
        
        # Parse the sections
        sections = {}
        current_section = None
        section_content = []
        
        for line in analysis_text.split('\n'):
            if line.startswith('1. EXECUTIVE_SUMMARY'):
                current_section = 'EXECUTIVE_SUMMARY'
                continue
            elif line.startswith('2. PERCEPTION_THEMES'):
                if current_section:
                    sections[current_section] = '\n'.join(section_content).strip()
                current_section = 'PERCEPTION_THEMES'
                section_content = []
                continue
            elif line.startswith('3. THEME_1_DETAILS'):
                if current_section:
                    sections[current_section] = '\n'.join(section_content).strip()
                current_section = 'THEME_1_DETAILS'
                section_content = []
                continue
            elif line.startswith('4. THEME_2_DETAILS'):
                if current_section:
                    sections[current_section] = '\n'.join(section_content).strip()
                current_section = 'THEME_2_DETAILS'
                section_content = []
                continue
            elif line.startswith('5. THEME_3_DETAILS'):
                if current_section:
                    sections[current_section] = '\n'.join(section_content).strip()
                current_section = 'THEME_3_DETAILS'
                section_content = []
                continue
            elif line.startswith('6. THEME_4_DETAILS'):
                if current_section:
                    sections[current_section] = '\n'.join(section_content).strip()
                current_section = 'THEME_4_DETAILS'
                section_content = []
                continue
            elif line.startswith('7. FAN_VS_MEDIA'):
                if current_section:
                    sections[current_section] = '\n'.join(section_content).strip()
                current_section = 'FAN_VS_MEDIA'
                section_content = []
                continue
            elif line.startswith('8. ON_VS_OFF_FIELD'):
                if current_section:
                    sections[current_section] = '\n'.join(section_content).strip()
                current_section = 'ON_VS_OFF_FIELD'
                section_content = []
                continue
            elif line.startswith('9. STRENGTHS_WEAKNESSES'):
                if current_section:
                    sections[current_section] = '\n'.join(section_content).strip()
                current_section = 'STRENGTHS_WEAKNESSES'
                section_content = []
                continue
            elif current_section:
                section_content.append(line)
        
        # Add the last section
        if current_section and section_content:
            sections[current_section] = '\n'.join(section_content).strip()
        
        # Extract theme titles from the PERCEPTION_THEMES section
        theme_titles = []
        if 'PERCEPTION_THEMES' in sections:
            theme_lines = sections['PERCEPTION_THEMES'].split('\n')
            for line in theme_lines:
                if line.strip().startswith(('1.', '2.', '3.', '4.')):
                    # Extract just the theme title without the number
                    parts = line.strip().split(' ', 1)
                    if len(parts) > 1:
                        theme_titles.append(parts[1])
                    else:
                        theme_titles.append(f"Theme {len(theme_titles) + 1}")
        
        # Ensure we have 4 theme titles
        while len(theme_titles) < 4:
            theme_titles.append(f"Theme {len(theme_titles) + 1}")
            
        return {
            'executive_summary': sections.get('EXECUTIVE_SUMMARY', ''),
            'perception_themes': sections.get('PERCEPTION_THEMES', ''),
            'theme_1': sections.get('THEME_1_DETAILS', ''),
            'theme_2': sections.get('THEME_2_DETAILS', ''),
            'theme_3': sections.get('THEME_3_DETAILS', ''),
            'theme_4': sections.get('THEME_4_DETAILS', ''),
            'fan_vs_media': sections.get('FAN_VS_MEDIA', ''),
            'on_vs_off_field': sections.get('ON_VS_OFF_FIELD', ''),
            'strengths_weaknesses': sections.get('STRENGTHS_WEAKNESSES', ''),
            'theme_titles': theme_titles,
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
    
    # Executive Summary at the top
    st.markdown("### Executive Summary")
    st.markdown("<div class='executive-summary'>", unsafe_allow_html=True)
    st.markdown(analysis_result['executive_summary'])
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Tabbed interface for the themes
    theme_tabs = st.tabs([
        f"Theme 1: {analysis_result['theme_titles'][0]}", 
        f"Theme 2: {analysis_result['theme_titles'][1]}", 
        f"Theme 3: {analysis_result['theme_titles'][2]}", 
        f"Theme 4: {analysis_result['theme_titles'][3]}",
        "Fan vs Media",
        "On/Off Field",
        "Strengths & Weaknesses"
    ])
    
    # Fill each tab with its content
    with theme_tabs[0]:
        st.markdown(analysis_result['theme_1'])
        
    with theme_tabs[1]:
        st.markdown(analysis_result['theme_2'])
        
    with theme_tabs[2]:
        st.markdown(analysis_result['theme_3'])
        
    with theme_tabs[3]:
        st.markdown(analysis_result['theme_4'])
        
    with theme_tabs[4]:
        st.markdown("### Fan vs Media Perception")
        st.markdown(analysis_result['fan_vs_media'])
        
    with theme_tabs[5]:
        st.markdown("### On-Field vs Off-Field Reputation")
        st.markdown(analysis_result['on_vs_off_field'])
        
    with theme_tabs[6]:
        st.markdown("### Reputation Strengths & Weaknesses")
        st.markdown(analysis_result['strengths_weaknesses'])
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Sources at the bottom in an expander for technical staff
    with st.expander("Sources and References", expanded=False):
        st.markdown("### Information Sources")
        for i, result in enumerate(search_results):
            st.markdown(f"**Source {i+1}:** {result.get('title', 'No title')}")
            if 'link' in result and result['link']:
                st.markdown(f"[Link]({result['link']})")
            st.markdown("---")