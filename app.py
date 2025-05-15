import streamlit as st
import requests
import pandas as pd
import os
import json
import time
import openai
import re

# --- SETUP ---
st.set_page_config(page_title="Player Character Measurement", layout="wide")

# --- CUSTOM THEME ---
primary_color = "#00c2cb"  # Light blue/teal from logo
secondary_color = "#ffffff"  # White from logo
accent_color = "#121212"   # Dark background
background_color = "#0a0a0a"  # Near black background

# Custom CSS with theme to match logo - simplified for clarity
st.markdown(f"""
<style>
    /* Base styles */
    .stApp {{
        background-color: {background_color};
        color: {secondary_color};
    }}
    
    /* Button styling */
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
    
    /* SIGN IN BUTTON - VERY CLEAR */
    button[kind="primaryFormSubmit"] {{
        background-color: {primary_color} !important;
        color: #000000 !important;
        border: 2px solid white !important;
        padding: 15px 20px !important;
        font-size: 18px !important;
        font-weight: 800 !important;
        letter-spacing: 1px !important;
        margin-top: 15px !important;
        text-transform: uppercase !important;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3) !important;
        position: relative !important;
    }}
    button[kind="primaryFormSubmit"]::after {{
        content: "→" !important;
        margin-left: 10px !important;
        font-size: 20px !important;
    }}
    button[kind="primaryFormSubmit"]:hover {{
        background-color: {secondary_color} !important;
        color: {accent_color} !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 8px rgba(0, 0, 0, 0.4) !important;
    }}
    
    /* Text elements */
    h1, h2, h3, h4, h5, h6 {{
        color: {secondary_color};
    }}
    .stSidebar .stButton>button {{
        width: 100%;
    }}
    a {{
        color: {primary_color};
    }}
    
    /* Input fields */
    div[data-baseweb="input"] input {{
        background-color: rgba(40, 40, 40, 0.6) !important;
        color: {secondary_color} !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
        border-radius: 4px !important;
        padding: 10px !important;
    }}
    div[data-baseweb="input"]:focus-within input {{
        border-color: {primary_color} !important;
    }}
    
    /* UI elements */
    div[data-testid="stExpander"] {{
        background-color: rgba(40, 40, 40, 0.6);
        border-radius: 4px;
    }}
    div.stMarkdown p {{
        color: {secondary_color};
    }}
    div.stSpinner > div {{
        border-top-color: {primary_color} !important;
    }}
    
    /* Analysis elements */
    .analysis-container {{
        background-color: rgba(40, 40, 40, 0.6);
        border-radius: 4px;
        padding: 20px;
        margin-top: 20px;
    }}
    div[data-baseweb="base-input"] {{
        margin-bottom: 15px;
    }}
    div[data-testid="stAlert"] {{
        background-color: rgba(220, 50, 50, 0.2);
        color: #ff6b6b;
        border: 1px solid rgba(220, 50, 50, 0.3);
        border-radius: 4px;
    }}
    
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {{
        gap: 2px;
        background-color: rgba(30, 30, 30, 0.3);
        border-radius: 4px;
        padding: 5px;
        overflow-x: auto;
        flex-wrap: nowrap;
        scrollbar-width: none;
    }}
    .stTabs [data-baseweb="tab-list"]::-webkit-scrollbar {{
        display: none;
    }}
    .stTabs [data-baseweb="tab"] {{
        height: auto;
        white-space: nowrap;
        background-color: rgba(50, 50, 50, 0.5);
        border-radius: 4px;
        padding: 8px 16px;
        font-size: 14px;
        min-width: auto;
        flex-shrink: 0;
    }}
    .stTabs [aria-selected="true"] {{
        background-color: {primary_color};
        color: {accent_color};
    }}
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
    
    /* Character Score */
    .character-score-container {{
        display: flex;
        flex-direction: column;
        align-items: center;
        margin-bottom: 20px;
    }}
    .character-score {{
        display: flex;
        align-items: center;
        justify-content: center;
        width: 100px;
        height: 100px;
        border-radius: 50%;
        background: linear-gradient(to right, {primary_color}, #00e6e6);
        color: #000000;
        font-weight: bold;
        box-shadow: 0 4px 10px rgba(0, 0, 0, 0.3);
        border: 3px solid #ffffff;
    }}
    .score-value {{
        font-size: 36px;
        font-weight: 800;
    }}
    .score-label {{
        margin-top: 10px;
        font-size: 16px;
        font-weight: 600;
        color: {secondary_color};
    }}
    .score-explanation {{
        background-color: rgba(40, 40, 40, 0.4);
        padding: 15px;
        border-radius: 4px;
        margin-top: 10px;
        border-left: 3px solid {primary_color};
    }}
    
    /* Color coded tabs based on score */
    .score-red {{
        background-color: #E53935 !important;
        color: white !important;
    }}
    .score-orange {{
        background-color: #FB8C00 !important;
        color: black !important;
    }}
    .score-yellow {{
        background-color: #FFD600 !important;
        color: black !important;
    }}
    .score-green {{
        background-color: #43A047 !important;
        color: white !important;
    }}
    
    /* Mobile responsiveness */
    @media (max-width: 768px) {{
        /* Adjust tab display */
        .stTabs [data-baseweb="tab"] {{
            padding: 8px 12px;
            font-size: 12px;
        }}
        
        /* Adjust character score for mobile */
        .character-score {{
            width: 80px;
            height: 80px;
        }}
        .score-value {{
            font-size: 28px;
        }}
        
        /* Make content fit better on small screens */
        .stApp > header {{
            padding-left: 10px;
            padding-right: 10px;
        }}
        section[data-testid="stSidebar"] {{
            min-width: 200px !important;
            max-width: 200px !important;
        }}
        div[role="main"] [data-testid="stVerticalBlock"] {{
            padding-left: 10px;
            padding-right: 10px;
        }}
    }}
    
    @media (max-width: 480px) {{
        /* Further adjust for very small screens */
        .character-score {{
            width: 70px;
            height: 70px;
        }}
        .score-value {{
            font-size: 24px;
        }}
        .score-label {{
            font-size: 14px;
        }}
        
        /* Simplify tab display */
        .stTabs [data-baseweb="tab"] {{
            padding: 6px 8px;
            font-size: 11px;
        }}
        
        /* Adjust header */
        h1, h2 {{
            font-size: 1.5rem !important;
        }}
        h3 {{
            font-size: 1.2rem !important;
        }}
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
        st.markdown("<h2 style='text-align: center; color: #00c2cb; margin-bottom: 20px;'>Player Character Measurement</h2>", unsafe_allow_html=True)
        
        # Simple form with clear instructions
        st.markdown("<p style='text-align: center; margin-bottom: 25px;'>Enter your credentials to access the dashboard</p>", unsafe_allow_html=True)
        
        # Create form with clearer fields
        with st.form("SignIn", clear_on_submit=False):
            user = st.text_input("Email")
            pw = st.text_input("Password", type="password")
            
            # Large, clearly labeled button
            st.markdown("<div style='padding: 20px 0;'>", unsafe_allow_html=True)
            login_button = st.form_submit_button("SIGN IN", use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)
            
            # Additional text to clarify button
            st.markdown("<p style='text-align: center; font-size: 12px; margin-top: -10px;'>Click the button above to sign in</p>", unsafe_allow_html=True)

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

# Function to get score color class
def get_score_color_class(score):
    if score < 40:
        return "score-red"
    elif score < 60:
        return "score-orange"
    elif score < 80:
        return "score-yellow"
    else:
        return "score-green"

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
You are analyzing news coverage and information for NFL player {player_name}. Given the following articles, create a detailed character report with a focus on the 5 most important character measurements.

Articles:
{articles_text}

Your character report must follow this EXACT format for proper parsing:

1. CHARACTER_SCORE
[Provide a character score from 1-100 based on your analysis. Consider both on-field and off-field reputation, with higher scores indicating more positive perception. Also provide a one-sentence explanation of this score.]

2. EXECUTIVE_SUMMARY
[Write a 1-2 paragraph executive summary of the player's overall public perception. Include approximate percentages for positive, negative, or mixed perception.]

3. CHARACTER_CATEGORY_1
[Title this category with one of the 5 most important character measurements - for example "Leadership", "Community Impact", "Off-Field Behavior", "Integrity", "Work Ethic", "Teamwork", etc. Then provide detailed analysis with specific evidence and examples. Assign this category a score from 1-100.]

4. CHARACTER_CATEGORY_2
[Title this category with the second most important character measurement. Provide detailed analysis with specific evidence and examples. Assign this category a score from 1-100.]

5. CHARACTER_CATEGORY_3
[Title this category with the third most important character measurement. Provide detailed analysis with specific evidence and examples. Assign this category a score from 1-100.]

6. CHARACTER_CATEGORY_4
[Title this category with the fourth most important character measurement. Provide detailed analysis with specific evidence and examples. Assign this category a score from 1-100.]

7. CHARACTER_CATEGORY_5
[Title this category with the fifth most important character measurement. Provide detailed analysis with specific evidence and examples. Assign this category a score from 1-100.]

Make sure to use the exact section headers as shown above, as they will be used for parsing the response.
"""
        
    try:
        # Call OpenAI API
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an expert NFL analyst specializing in player perception and character assessment."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.5
        )
        
        analysis_text = response.choices[0].message.content
        
        # Parse the sections
        sections = {}
        current_section = None
        section_content = []
        category_scores = {}  # To store scores for each category
        
        for line in analysis_text.split('\n'):
            if line.startswith('1. CHARACTER_SCORE'):
                current_section = 'CHARACTER_SCORE'
                continue
            elif line.startswith('2. EXECUTIVE_SUMMARY'):
                if current_section:
                    sections[current_section] = '\n'.join(section_content).strip()
                current_section = 'EXECUTIVE_SUMMARY'
                section_content = []
                continue
            elif line.startswith('3. CHARACTER_CATEGORY_1'):
                if current_section:
                    sections[current_section] = '\n'.join(section_content).strip()
                current_section = 'CHARACTER_CATEGORY_1'
                section_content = []
                continue
            elif line.startswith('4. CHARACTER_CATEGORY_2'):
                if current_section:
                    sections[current_section] = '\n'.join(section_content).strip()
                current_section = 'CHARACTER_CATEGORY_2'
                section_content = []
                continue
            elif line.startswith('5. CHARACTER_CATEGORY_3'):
                if current_section:
                    sections[current_section] = '\n'.join(section_content).strip()
                current_section = 'CHARACTER_CATEGORY_3'
                section_content = []
                continue
            elif line.startswith('6. CHARACTER_CATEGORY_4'):
                if current_section:
                    sections[current_section] = '\n'.join(section_content).strip()
                current_section = 'CHARACTER_CATEGORY_4'
                section_content = []
                continue
            elif line.startswith('7. CHARACTER_CATEGORY_5'):
                if current_section:
                    sections[current_section] = '\n'.join(section_content).strip()
                current_section = 'CHARACTER_CATEGORY_5'
                section_content = []
                continue
            elif current_section:
                section_content.append(line)
        
        # Add the last section
        if current_section and section_content:
            sections[current_section] = '\n'.join(section_content).strip()
        
        # Extract category titles and scores from each category section
        category_titles = []
        category_scores = []
        
        for i in range(1, 6):
            key = f'CHARACTER_CATEGORY_{i}'
            if key in sections:
                content = sections[key]
                
                # Extract title by finding the first line that's not empty
                lines = content.split('\n')
                title = None
                for line in lines:
                    if line.strip():
                        title = line.strip()
                        break
                
                if not title:
                    title = f"Category {i}"
                    
                category_titles.append(title)
                
                # Look for a score between 1-100 in the content
                score_match = re.search(r'\b([1-9][0-9]?|100)\b', content)
                if score_match:
                    category_scores.append(int(score_match.group(1)))
                else:
                    # If no score found, assign a default based on overall score
                    if 'CHARACTER_SCORE' in sections:
                        score_text = sections['CHARACTER_SCORE']
                        overall_score_match = re.search(r'\b([1-9][0-9]?|100)\b', score_text)
                        if overall_score_match:
                            default_score = int(overall_score_match.group(1))
                        else:
                            default_score = 70
                    else:
                        default_score = 70
                    
                    category_scores.append(default_score)
        
        # Make sure we have 5 categories
        while len(category_titles) < 5:
            category_titles.append(f"Category {len(category_titles) + 1}")
            
        while len(category_scores) < 5:
            if 'CHARACTER_SCORE' in sections:
                score_text = sections['CHARACTER_SCORE']
                overall_score_match = re.search(r'\b([1-9][0-9]?|100)\b', score_text)
                if overall_score_match:
                    default_score = int(overall_score_match.group(1))
                else:
                    default_score = 70
            else:
                default_score = 70
            
            category_scores.append(default_score)
            
        # Extract character score
        character_score = 70  # Default score
        score_explanation = "Based on overall public perception"
        if 'CHARACTER_SCORE' in sections:
            score_text = sections['CHARACTER_SCORE']
            # Look for a number between 1-100
            score_match = re.search(r'\b([1-9][0-9]?|100)\b', score_text)
            if score_match:
                character_score = int(score_match.group(1))
            
            # Get the explanation (usually a sentence after the score)
            sentences = re.split(r'(?<=[.!?])\s+', score_text)
            if len(sentences) > 0:
                for sentence in sentences:
                    if not re.search(r'\b([1-9][0-9]?|100)\b', sentence):
                        score_explanation = sentence.strip()
                        break
            
        return {
            'character_score': character_score,
            'score_explanation': score_explanation,
            'executive_summary': sections.get('EXECUTIVE_SUMMARY', ''),
            'category_1': sections.get('CHARACTER_CATEGORY_1', ''),
            'category_2': sections.get('CHARACTER_CATEGORY_2', ''),
            'category_3': sections.get('CHARACTER_CATEGORY_3', ''),
            'category_4': sections.get('CHARACTER_CATEGORY_4', ''),
            'category_5': sections.get('CHARACTER_CATEGORY_5', ''),
            'category_titles': category_titles,
            'category_scores': category_scores,
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
    st.title("Player Character Measurement")

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
    
    # Display character score
    col1, col2 = st.columns([1, 3])
    with col1:
        # Create a circular score display
        st.markdown(
            f"""
            <div class="character-score-container">
                <div class="character-score">
                    <span class="score-value">{analysis_result['character_score']}</span>
                </div>
                <div class="score-label">Character Score</div>
            </div>
            """, 
            unsafe_allow_html=True
        )
    with col2:
        st.markdown("<div class='score-explanation'>", unsafe_allow_html=True)
        st.markdown(f"**Why this score:** {analysis_result['score_explanation']}")
        st.markdown("</div>", unsafe_allow_html=True)
    
    # Display analysis in a clean container
    st.markdown("<div class='analysis-container'>", unsafe_allow_html=True)
    
    # Executive Summary at the top
    st.markdown("### Executive Summary")
    st.markdown("<div class='executive-summary'>", unsafe_allow_html=True)
    st.markdown(analysis_result['executive_summary'])
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Get color classes for each category based on their scores
    category_color_classes = [get_score_color_class(score) for score in analysis_result['category_scores']]
    
    # Inject custom HTML to create colored tabs
    tab_html = f"""
    <div class="stTabs">
        <div data-baseweb="tab-list" role="tablist">
    """
    
    for i, (title, color_class) in enumerate(zip(analysis_result['category_titles'], category_color_classes)):
        # Create each tab with score in title and color based on the score
        score = analysis_result['category_scores'][i]
        is_selected = i == 0  # First tab is selected by default
        selected_attr = 'aria-selected="true"' if is_selected else 'aria-selected="false"'
        
        tab_html += f"""
        <button id="tab-{i}" {selected_attr} role="tab" data-baseweb="tab" class="{color_class}">
            {title} ({score})
        </button>
        """
    
    tab_html += """
        </div>
    </div>
    """
    
    # Insert the custom HTML
    st.markdown(tab_html, unsafe_allow_html=True)
    
    # Now create the actual tabs with streamlit
    # The custom HTML above is just for visual styling,
    # we still need real tabs for functionality
    tabs = st.tabs([f"{title} ({score})" for title, score in zip(analysis_result['category_titles'], analysis_result['category_scores'])])
    
    # Fill each tab with its content
    with tabs[0]:
        st.markdown(analysis_result['category_1'])
        
    with tabs[1]:
        st.markdown(analysis_result['category_2'])
        
    with tabs[2]:
        st.markdown(analysis_result['category_3'])
        
    with tabs[3]:
        st.markdown(analysis_result['category_4'])
        
    with tabs[4]:
        st.markdown(analysis_result['category_5'])
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Sources at the bottom in an expander for technical staff
    with st.expander("Sources and References", expanded=False):
        st.markdown("### Information Sources")
        for i, result in enumerate(search_results):
            st.markdown(f"**Source {i+1}:** {result.get('title', 'No title')}")
            if 'link' in result and result['link']:
                st.markdown(f"[Link]({result['link']})")
            st.markdown("---")