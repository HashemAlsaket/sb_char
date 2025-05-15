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

# Score color coding
score_colors = {
    "red": "#ff4e50",      # Low scores (0-39)
    "orange": "#fc913a",   # Medium-low scores (40-59)
    "yellow": "#f9d62e",   # Medium-high scores (60-79)
    "green": "#52bf90"     # High scores (80-100)
}

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
        width: 80px;
        height: 80px;
        border-radius: 50%;
        background: linear-gradient(to right, {primary_color}, #00e6e6);
        color: #000000;
        font-weight: bold;
        box-shadow: 0 4px 10px rgba(0, 0, 0, 0.3);
        border: 3px solid #ffffff;
    }}
    .score-value {{
        font-size: 28px;
        font-weight: 800;
    }}
    .score-label {{
        margin-top: 8px;
        font-size: 14px;
        font-weight: 600;
        color: {secondary_color};
        text-align: center;
    }}
    .score-explanation {{
        background-color: rgba(40, 40, 40, 0.4);
        padding: 15px;
        border-radius: 4px;
        margin-top: 10px;
        border-left: 3px solid {primary_color};
    }}

    /* Custom tab colors */
    .tab-red {{
        background-color: {score_colors["red"]} !important;
        color: white !important;
    }}
    .tab-orange {{
        background-color: {score_colors["orange"]} !important; 
        color: black !important;
    }}
    .tab-yellow {{
        background-color: {score_colors["yellow"]} !important;
        color: black !important;
    }}
    .tab-green {{
        background-color: {score_colors["green"]} !important;
        color: white !important;
    }}
    
    /* Category scores in tabs */
    .category-header {{
        display: flex;
        align-items: center;
        margin-bottom: 15px;
    }}
    .category-score-bubble {{
        display: inline-flex;
        align-items: center;
        justify-content: center;
        width: 40px;
        height: 40px;
        border-radius: 50%;
        font-size: 18px;
        font-weight: bold;
        margin-right: 10px;
    }}
    .category-score-bubble.red {{
        background-color: {score_colors["red"]};
        color: white;
    }}
    .category-score-bubble.orange {{
        background-color: {score_colors["orange"]};
        color: black;
    }}
    .category-score-bubble.yellow {{
        background-color: {score_colors["yellow"]};
        color: black;
    }}
    .category-score-bubble.green {{
        background-color: {score_colors["green"]};
        color: white;
    }}
    
    /* Mobile responsiveness */
    @media (max-width: 768px) {{
        /* Adjust tab display */
        .stTabs [data-baseweb="tab"] {{
            padding: 8px 12px;
            font-size: 12px;
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
            
            # Plain high-contrast button style
            st.markdown("""
            <style>
            /* Simple, high-contrast button with no animations or effects */
            button[kind="primaryFormSubmit"] {
                background-color: #00c2cb !important;
                color: #000000 !important;
                font-weight: bold !important;
                font-size: 18px !important;
                padding: 12px 20px !important;
                border: 2px solid #ffffff !important;
                border-radius: 4px !important;
                margin-top: 20px !important;
                cursor: pointer !important;
                width: 100% !important;
                text-transform: uppercase !important;
                letter-spacing: 1px !important;
                box-shadow: none !important;
                transform: none !important;
                transition: none !important;
            }
            
            /* No hover effects or animations */
            button[kind="primaryFormSubmit"]:hover {
                background-color: #00c2cb !important;
                color: #000000 !important;
                border: 2px solid #ffffff !important;
                transform: none !important;
                box-shadow: none !important;
            }
            
            /* Make sure text is visible */
            button[kind="primaryFormSubmit"] div, 
            button[kind="primaryFormSubmit"] span {
                color: #000000 !important;
                opacity: 1 !important;
                visibility: visible !important;
            }
            </style>
            """, unsafe_allow_html=True)
            
            # Simple button with no additional text or arrow
            login_button = st.form_submit_button("SIGN IN", use_container_width=True)

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

# Helper function to get color class based on score
def get_score_color(score):
    if score < 40:
        return "red"
    elif score < 60:
        return "orange"
    elif score < 80:
        return "yellow"
    else:
        return "green"

# --- FUNCTIONS ---
def search_player_info(player_name, num_results=50):
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

1. CATEGORY_SCORES
[Provide scores from 1-100 for EXACTLY 5 key categories of player perception. Use only these five categories: "On-Field Performance", "Leadership", "Team Relationship", "Public Image", and "Off-Field Conduct". For each category, show a score and a brief explanation on the SAME line. Format precisely as: "Category Name: Score - Brief explanation". For example: "Leadership: 85 - Demonstrates excellent leadership qualities both on and off the field."]

2. EXECUTIVE_SUMMARY
[Write a 1-2 paragraph summary that integrates insights from all five categories. Highlight key strengths and areas for improvement based on the category scores. Make connections between different categories where appropriate.]

3. PERFORMANCE_DETAILS
[Provide detailed analysis of the player's on-field performance perception with specific evidence and examples.]

4. LEADERSHIP_DETAILS
[Provide detailed analysis of the player's leadership qualities with specific evidence and examples.]

5. TEAM_RELATIONSHIP_DETAILS
[Provide detailed analysis of the player's relationship with team members and organization with specific evidence and examples.]

6. PUBLIC_IMAGE_DETAILS
[Provide detailed analysis of the player's public and media perception with specific evidence and examples.]

7. CONDUCT_DETAILS
[Provide detailed analysis of the player's off-field conduct and character with specific evidence and examples.]

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
            if line.startswith('1. CATEGORY_SCORES'):
                current_section = 'CATEGORY_SCORES'
                continue
            elif line.startswith('2. EXECUTIVE_SUMMARY'):
                if current_section:
                    sections[current_section] = '\n'.join(section_content).strip()
                current_section = 'EXECUTIVE_SUMMARY'
                section_content = []
                continue
            elif line.startswith('3. PERFORMANCE_DETAILS'):
                if current_section:
                    sections[current_section] = '\n'.join(section_content).strip()
                current_section = 'PERFORMANCE_DETAILS'
                section_content = []
                continue
            elif line.startswith('4. LEADERSHIP_DETAILS'):
                if current_section:
                    sections[current_section] = '\n'.join(section_content).strip()
                current_section = 'LEADERSHIP_DETAILS'
                section_content = []
                continue
            elif line.startswith('5. TEAM_RELATIONSHIP_DETAILS'):
                if current_section:
                    sections[current_section] = '\n'.join(section_content).strip()
                current_section = 'TEAM_RELATIONSHIP_DETAILS'
                section_content = []
                continue
            elif line.startswith('6. PUBLIC_IMAGE_DETAILS'):
                if current_section:
                    sections[current_section] = '\n'.join(section_content).strip()
                current_section = 'PUBLIC_IMAGE_DETAILS'
                section_content = []
                continue
            elif line.startswith('7. CONDUCT_DETAILS'):
                if current_section:
                    sections[current_section] = '\n'.join(section_content).strip()
                current_section = 'CONDUCT_DETAILS'
                section_content = []
                continue
            elif current_section:
                section_content.append(line)
        
        # Add the last section
        if current_section and section_content:
            sections[current_section] = '\n'.join(section_content).strip()
        
        # Extract category scores
        category_scores = {
            "On-Field Performance": {"score": 0, "explanation": ""},
            "Leadership": {"score": 0, "explanation": ""},
            "Team Relationship": {"score": 0, "explanation": ""},
            "Public Image": {"score": 0, "explanation": ""},
            "Off-Field Conduct": {"score": 0, "explanation": ""}
        }
        
        if 'CATEGORY_SCORES' in sections:
            category_lines = sections['CATEGORY_SCORES'].split('\n')
            for line in category_lines:
                line = line.strip()
                if line and ":" in line:
                    # Try to extract category, score and explanation
                    category_match = re.match(r'([^:]+):\s*(\d+)\s*-\s*(.+)', line)
                    if category_match:
                        category = category_match.group(1).strip()
                        score = int(category_match.group(2))
                        explanation = category_match.group(3).strip()
                        
                        # Match to our predefined categories (fuzzy matching)
                        if "field" in category.lower() and ("performance" in category.lower() or "skill" in category.lower()):
                            category_scores["On-Field Performance"]["score"] = score
                            category_scores["On-Field Performance"]["explanation"] = explanation
                        elif "leadership" in category.lower() or "lead" in category.lower():
                            category_scores["Leadership"]["score"] = score
                            category_scores["Leadership"]["explanation"] = explanation
                        elif "team" in category.lower() or "relationship" in category.lower() or "teammate" in category.lower():
                            category_scores["Team Relationship"]["score"] = score
                            category_scores["Team Relationship"]["explanation"] = explanation
                        elif "public" in category.lower() or "image" in category.lower() or "media" in category.lower():
                            category_scores["Public Image"]["score"] = score
                            category_scores["Public Image"]["explanation"] = explanation
                        elif "conduct" in category.lower() or "off-field" in category.lower() or "character" in category.lower():
                            category_scores["Off-Field Conduct"]["score"] = score
                            category_scores["Off-Field Conduct"]["explanation"] = explanation
        
        # Set default scores for any missing categories
        for category in category_scores:
            if category_scores[category]["score"] == 0:
                category_scores[category]["score"] = 65
                category_scores[category]["explanation"] = f"Default score for {category}."
                
        # Calculate overall score as the average of category scores
        overall_score = round(sum(category_scores[category]["score"] for category in category_scores) / len(category_scores))
        
        # Generate score explanation based on average score
        score_explanation = f"Average of all five character categories: {', '.join(category_scores.keys())}."
                
        # Create objects for the detailed sections
        details = {
            "performance": sections.get('PERFORMANCE_DETAILS', 'No details available.'),
            "leadership": sections.get('LEADERSHIP_DETAILS', 'No details available.'),
            "team_relationship": sections.get('TEAM_RELATIONSHIP_DETAILS', 'No details available.'),
            "public_image": sections.get('PUBLIC_IMAGE_DETAILS', 'No details available.'),
            "conduct": sections.get('CONDUCT_DETAILS', 'No details available.')
        }
            
        return {
            'overall_score': overall_score,
            'score_explanation': score_explanation,
            'category_scores': category_scores,
            'executive_summary': sections.get('EXECUTIVE_SUMMARY', ''),
            'details': details,
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
    
    # Display overall character score
    overall_score = analysis_result['overall_score']
    overall_color = get_score_color(overall_score)
    
    col1, col2 = st.columns([1, 3])
    with col1:
        # Create a circular score display with the appropriate color
        st.markdown(
            f"""
            <div class="character-score-container">
                <div class="character-score" style="background: linear-gradient(to right, {score_colors[overall_color]}, {score_colors[overall_color]}CC);">
                    <span class="score-value">{overall_score}</span>
                </div>
                <div class="score-label">Overall Character</div>
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
    
    # Prepare information for tabs
    tab_data = [
        {
            "name": "On-Field Performance", 
            "score": analysis_result['category_scores']["On-Field Performance"]["score"],
            "explanation": analysis_result['category_scores']["On-Field Performance"]["explanation"],
            "content": analysis_result['details']['performance']
        },
        {
            "name": "Leadership", 
            "score": analysis_result['category_scores']["Leadership"]["score"],
            "explanation": analysis_result['category_scores']["Leadership"]["explanation"],
            "content": analysis_result['details']['leadership']
        },
        {
            "name": "Team Relations", 
            "score": analysis_result['category_scores']["Team Relationship"]["score"],
            "explanation": analysis_result['category_scores']["Team Relationship"]["explanation"],
            "content": analysis_result['details']['team_relationship']
        },
        {
            "name": "Public Image", 
            "score": analysis_result['category_scores']["Public Image"]["score"],
            "explanation": analysis_result['category_scores']["Public Image"]["explanation"],
            "content": analysis_result['details']['public_image']
        },
        {
            "name": "Off-Field Conduct", 
            "score": analysis_result['category_scores']["Off-Field Conduct"]["score"],
            "explanation": analysis_result['category_scores']["Off-Field Conduct"]["explanation"],
            "content": analysis_result['details']['conduct']
        }
    ]
    
    # Get color classes for each tab
    tab_colors = [get_score_color(tab["score"]) for tab in tab_data]
    
    # Create colored tabs with scores
    tab_labels = [f"{tab['name']} ({tab['score']})" for tab in tab_data]
    
    # Create the tabs with streamlit - no custom HTML injection
    tabs = st.tabs(tab_labels)
    
    # Fill each tab with its content
    for i, tab in enumerate(tabs):
        with tab:
            data = tab_data[i]
            color = tab_colors[i]
            
            # Display score and explanation at top of tab
            st.markdown(f"""
            <div class="category-header">
                <span class="category-score-bubble {color}">{data['score']}</span>
                <span><strong>{data['explanation']}</strong></span>
            </div>
            """, unsafe_allow_html=True)
            
            # Display the detailed content
            st.markdown(data['content'])
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Sources at the bottom in an expander for technical staff
    with st.expander("Sources and References", expanded=False):
        st.markdown("### Information Sources")
        for i, result in enumerate(search_results):
            st.markdown(f"**Source {i+1}:** {result.get('title', 'No title')}")
            if 'link' in result and result['link']:
                st.markdown(f"[Link]({result['link']})")
            st.markdown("---")