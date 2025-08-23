import streamlit as st
import pandas as pd
import numpy as np
import re
import zipfile as zp
import json
import altair as alt
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

st.set_page_config(
    page_title="Instagram Friendship Analyzer", 
    page_icon="📊", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for enhanced UI
st.markdown("""
<h1 class="main-title"><span class="emoji">📊</span> Instagram Friendship Analyzer</h1>
<style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Main app styling */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    
    /* Custom title styling */
    .main-title {
        font-family: 'Inter', sans-serif;
        font-size: 3rem;
        font-weight: 700;
        text-align: center;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 1rem;
        animation: fadeInUp 0.8s ease-out;
    }.emoji {
    -webkit-text-fill-color: initial !important; /* restores emoji color */
    background: none !important;
    }
    
    /* Subtitle styling */
    .subtitle {
        font-family: 'Inter', sans-serif;
        font-size: 1.2rem;
        text-align: center;
        opacity: 0.8;
        margin-bottom: 2rem;
        animation: fadeInUp 0.8s ease-out 0.2s both;
    }
    
    /* Feature cards */
    .feature-card {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 16px;
        padding: 1.5rem;
        margin: 1rem 0;
        transition: all 0.3s ease;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
    }
    
    .feature-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 30px rgba(0, 0, 0, 0.15);
        border-color: rgba(255, 255, 255, 0.2);
    }
    
    /* Custom buttons */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 0.6rem 1.5rem;
        font-weight: 600;
        font-family: 'Inter', sans-serif;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
        background: linear-gradient(135deg, #5a6fd8 0%, #6a4190 100%);
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        background: linear-gradient(180deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.1) 100%);
    }
    
    /* Metrics styling */
    [data-testid="metric-container"] {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        padding: 1rem;
        border-radius: 12px;
        backdrop-filter: blur(10px);
        transition: all 0.3s ease;
    }
    
    [data-testid="metric-container"]:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
    }
    
    /* File uploader styling */
    .stFileUploader > div > div {
        background: rgba(255, 255, 255, 0.05);
        border: 2px dashed rgba(102, 126, 234, 0.5);
        border-radius: 16px;
        padding: 2rem;
        text-align: center;
        transition: all 0.3s ease;
    }
    
    .stFileUploader > div > div:hover {
        border-color: rgba(102, 126, 234, 0.8);
        background: rgba(102, 126, 234, 0.1);
    }
    
    /* Expander styling */
    .streamlit-expanderHeader {
        background: rgba(255, 255, 255, 0.05);
        border-radius: 12px;
        font-weight: 600;
        padding: 1rem;
    }
    
    /* Dataframe styling */
    .stDataFrame {
        border-radius: 12px;
        overflow: hidden;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
    }
    
    /* Progress indicators */
    .progress-container {
        background: rgba(255, 255, 255, 0.05);
        border-radius: 12px;
        padding: 1rem;
        margin: 1rem 0;
        backdrop-filter: blur(10px);
    }
    
    /* Animations */
    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(30px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    @keyframes pulse {
        0%, 100% {
            transform: scale(1);
        }
        50% {
            transform: scale(1.05);
        }
    }
    
    /* Icon styling */
    .icon-large {
        font-size: 2rem;
        margin: 0.5rem;
        animation: pulse 2s infinite;
    }
    
    /* Success/warning/error styling */
    .stSuccess, .stWarning, .stError, .stInfo {
        border-radius: 12px;
        backdrop-filter: blur(10px);
        border: none;
    }
    
    /* Chart containers */
    .chart-container {
        background: rgba(255, 255, 255, 0.02);
        border-radius: 16px;
        padding: 1.5rem;
        margin: 1rem 0;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    /* Dark theme adjustments */
    @media (prefers-color-scheme: dark) {
        .feature-card {
            background: rgba(255, 255, 255, 0.02);
            border-color: rgba(255, 255, 255, 0.05);
        }
        
        [data-testid="metric-container"] {
            background: rgba(255, 255, 255, 0.02);
            border-color: rgba(255, 255, 255, 0.05);
        }
    }
    
    /* Light theme adjustments */
    @media (prefers-color-scheme: light) {
        .feature-card {
            background: rgba(0, 0, 0, 0.02);
            border-color: rgba(0, 0, 0, 0.05);
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.05);
        }
        
        [data-testid="metric-container"] {
            background: rgba(0, 0, 0, 0.02);
            border-color: rgba(0, 0, 0, 0.05);
        }
    }
    
    /* Loading animation */
    .loading-spinner {
        display: inline-block;
        width: 20px;
        height: 20px;
        border: 3px solid rgba(255, 255, 255, 0.3);
        border-radius: 50%;
        border-top-color: #667eea;
        animation: spin 1s ease-in-out infinite;
    }
    
    @keyframes spin {
        to { transform: rotate(360deg); }
    }
</style>
""", unsafe_allow_html=True)

# Main title with animation
st.markdown('<p class="subtitle">Discover the hidden patterns in your Instagram connections</p>', unsafe_allow_html=True)

# Welcome section with enhanced cards
st.markdown("""
<div class="feature-card">
    <h2>🎯 Welcome to Instagram Friendship Analyzer</h2>
    <p>This powerful tool analyzes your friendships using <strong>messages, story interactions, close friends, and favorites</strong> to provide deep insights into your social connections.</p>
</div>
""", unsafe_allow_html=True)

# How it works section
with st.container():
    st.markdown("## 🚀 How It Works")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="feature-card">
            <div style="text-align: center;">
                <span class="icon-large">📥</span>
                <h3>1. Download Data</h3>
                <p>Request your full Instagram data export (not just messages)</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="feature-card">
            <div style="text-align: center;">
                <span class="icon-large">📤</span>
                <h3>2. Upload ZIP</h3>
                <p>Upload the ZIP file that Instagram emails you</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="feature-card">
            <div style="text-align: center;">
                <span class="icon-large">📊</span>
                <h3>3. Get Insights</h3>
                <p>View comprehensive friendship analytics with different options</p>
            </div>
        </div>
        """, unsafe_allow_html=True)

# Privacy section
st.markdown("""
<div class="feature-card">
    <h3>🔒 Privacy & Security</h3>
    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 1rem; margin-top: 1rem;">
        <div>
            <strong>🖥️ Local Processing:</strong> Analysis runs entirely in your browser session
        </div>
        <div>
            <strong>📊 Metadata Only:</strong> Only reads timestamps, participants, and interaction counts
        </div>
        <div>
            <strong>🚫 No Storage:</strong> Media files and ad data are completely ignored
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# Enhanced download instructions
with st.expander("📥 **How to Request & Download Your Instagram Data**", expanded=False):
    tab1, tab2 = st.tabs(["📱 Mobile App", "💻 Desktop"])
    
    with tab1:
        st.markdown("""
        <div class="feature-card">
            <h4>📱 Instagram Mobile App Instructions</h4>
            <ol>
                <li>Open <strong>Instagram</strong> → tap your profile → <strong>☰ Menu</strong></li>
                <li>Go to <strong>Settings and privacy</strong> → <strong>Your information and permissions</strong></li>
                <li>Tap <strong>Download your information</strong> → <strong>All of your information</strong></li>
                <li>Select <strong>JSON</strong> format for better compatibility</li>
                <li>🎯 <strong>Optional:</strong> Choose a smaller date range for faster processing</li>
                <li>Submit request and download the ZIP from your email</li>
                <li>⚠️ You can skip <strong>Ads/Monetization</strong> files - they're not needed</li>
            </ol>
            <div style="margin-top: 1rem;">
                <iframe width="100%" height="315" src="https://www.youtube.com/embed/zkgx9TCcR-4" 
                frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" 
                allowfullscreen style="border-radius: 12px;"></iframe>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with tab2:
        st.markdown("""
        <div class="feature-card">
            <h4>💻 Instagram Desktop Instructions</h4>
            <ol>
                <li>Go to <strong>Instagram.com</strong> → log in → click your profile</li>
                <li>Click <strong>Settings</strong> → <strong>Privacy and security</strong></li>
                <li>Select <strong>Download your information</strong></li>
                <li>Choose <strong>JSON</strong> format and <strong>All of your information</strong></li>
                <li>🎯 <strong>Optional:</strong> Pick a smaller date range if needed</li>
                <li>Submit and download the ZIP from your email</li>
                <li>⚠️ You can skip <strong>Ads/Monetization</strong> files when requesting</li>
            </ol>
            <div style="background: linear-gradient(135deg, #667eea20, #764ba220); padding: 1rem; border-radius: 12px; margin-top: 1rem;">
                <strong>💡 Pro Tip:</strong> Upload the ZIP file without unzipping it for best results!
            </div>
        </div>
        """, unsafe_allow_html=True)

# Enhanced file upload section
st.markdown("## 📂 Upload Your Data")
uploaded_zip = st.file_uploader(
    "Choose your Instagram data ZIP file", 
    type=["zip"],
    help="Upload the ZIP file Instagram emailed you. No need to unzip it first!"
)

# Sidebar with enhanced styling
st.sidebar.markdown("""
<div style="text-align: center; padding: 1rem;">
    <h2>🎯 Control Panel</h2>
    <p style="opacity: 0.8;">Search & filter your friendship data</p>
</div>
""", unsafe_allow_html=True)

def safe_encode_decode(text):
    """Safely encode and decode text to handle special characters."""
    try:
        return text.encode('latin1').decode('utf-8')
    except (UnicodeEncodeError, UnicodeDecodeError):
        try:
            return text.encode('utf-8').decode('utf-8')
        except (UnicodeEncodeError, UnicodeDecodeError):
            logger.warning(f"Could not properly decode text: {text}")
            return str(text)  # Fallback to string conversion

def calculate_reply_times(messages):
    """
    Calculate reply times between messages from different participants.
    Returns: (avg_reply_time, fastest_reply_time, longest_reply_time) in seconds.
    """
    try:
        if not messages or len(messages) < 2:
            return 0, 0, 0
        
        reply_times = []

        # Sort messages by timestamp (oldest first)
        try:
            sorted_messages = sorted(messages, key=lambda x: x.get('timestamp_ms', 0))
        except (KeyError, TypeError) as e:
            logger.warning(f"Error sorting messages by timestamp: {e}")
            return 0, 0, 0

        for i in range(1, len(sorted_messages)):
            try:
                prev_msg = sorted_messages[i - 1]
                curr_msg = sorted_messages[i]

                # Check if required fields exist
                if not all(key in prev_msg for key in ['sender_name', 'timestamp_ms']) or \
                   not all(key in curr_msg for key in ['sender_name', 'timestamp_ms']):
                    continue

                # Only calculate reply time if it's a different sender replying
                if prev_msg['sender_name'] != curr_msg['sender_name']:
                    time_diff_ms = curr_msg['timestamp_ms'] - prev_msg['timestamp_ms']
                    if time_diff_ms > 0:  # Ensure positive time difference
                        time_diff_seconds = time_diff_ms / 1000
                        reply_times.append(time_diff_seconds)
            except (KeyError, TypeError, ValueError) as e:
                logger.warning(f"Error processing message pair at index {i}: {e}")
                continue

        # Calculate statistics
        if reply_times:
            try:
                avg_reply_time = sum(reply_times) / len(reply_times)
                fastest_reply_time = min(reply_times)
                longest_reply_time = max(reply_times)
                return avg_reply_time, fastest_reply_time, longest_reply_time
            except (ValueError, ZeroDivisionError) as e:
                logger.warning(f"Error calculating reply time statistics: {e}")
                return 0, 0, 0
        else:
            return 0, 0, 0
    except Exception as e:
        logger.error(f"Unexpected error in calculate_reply_times: {e}")
        return 0, 0, 0

def format_time(seconds):
    """Format seconds into human-readable time format."""
    try:
        seconds = int(float(seconds))  # Handle potential float inputs
        if seconds < 0:
            return "0s"
        elif seconds < 60:
            return f"{seconds}s"
        elif seconds < 3600:
            mins, sec = divmod(seconds, 60)
            return f"{mins}m {sec}s"
        elif seconds < 86400:  # less than a day
            hrs, rem = divmod(seconds, 3600)
            mins, sec = divmod(rem, 60)
            return f"{hrs}h {mins}m {sec}s"
        else:
            days, rem = divmod(seconds, 86400)
            hrs, rem = divmod(rem, 3600)
            mins, sec = divmod(rem, 60)
            return f"{days}d {hrs}h {mins}m {sec}s"
    except (ValueError, TypeError):
        return "N/A"

if uploaded_zip is not None:
    # Processing indicator
    with st.spinner('🔄 Processing your Instagram data...'):
        try:
            with zp.ZipFile(uploaded_zip) as z:
                try:
                    # Get top folder name from the ZIP
                    file_list = z.namelist()
                    if not file_list:
                        st.error("❌ The uploaded ZIP file appears to be empty.")
                        st.stop()
                    
                    top_folder = str(uploaded_zip)

                    # Extract username between "instagram-" and "-YYYY-MM-DD"
                    match = re.search(r"instagram-(.+?)-\d{4}-\d{2}-\d{2}", top_folder)
                    if match:
                        raw_username = match.group(1)

                        # Simple encoding: UTF-8 → hex
                        try:
                            encoded_username = raw_username.encode("utf-8").hex()
                            st.success(f"📌 **Detected username:** `{raw_username}`")
                        except UnicodeEncodeError as e:
                            logger.warning(f"Error encoding username: {e}")
                            st.warning("⚠️ Username detected but contains special characters.")
                    else:
                        st.error("❌ Could not detect username from folder name.")
                        st.stop()
                except Exception as e:
                    st.error(f"❌ Error reading ZIP file structure: {e}")
                    st.stop()

                # Target inbox path
                inbox_path_prefix = "your_instagram_activity/messages/inbox/"

                # Collect all `message_1.json` files in subfolders
                message_jsons = []
                deactivated_accounts = set()
                
                try:
                    for file_name in z.namelist():
                        try:
                            parts = file_name[len(inbox_path_prefix):].split('/')

                            if len(parts) > 1:
                                folder_name = parts[0]
                                if folder_name.startswith('instagramuser_'):
                                    deactivated_accounts.add(folder_name)

                            if file_name.startswith(inbox_path_prefix) and file_name.endswith("message_1.json"):
                                try:
                                    with z.open(file_name) as f:
                                        data = json.load(f)
                                        if isinstance(data, dict) and 'messages' in data:
                                            message_jsons.append(data)
                                        else:
                                            logger.warning(f"Invalid JSON structure in {file_name}")
                                except json.JSONDecodeError as e:
                                    st.warning(f"Invalid JSON in {file_name}: {e}")
                                except Exception as e:
                                    st.warning(f"Error reading {file_name}: {e}")
                        except Exception as e:
                            logger.warning(f"Error processing file {file_name}: {e}")
                            continue
                except Exception as e:
                    st.error(f"❌ Error scanning ZIP contents: {e}")
                    st.stop()

                # Initialize data structures
                Users = {
                    'names': [],
                    'msgs_count': [],
                    'avg_reply_time': [],
                    'longest_reply_time': [],
                    'fastest_reply_time': []
                }
                
                groups = 0

                # Process message data with progress
                try:
                    if len(message_jsons) > 0:
                        progress_bar = st.progress(0)
                        status_text = st.empty()
                        
                        for idx, msg in enumerate(message_jsons):
                            try:
                                # Update progress
                                progress = (idx + 1) / len(message_jsons)
                                progress_bar.progress(progress)
                                status_text.text(f'Processing conversation {idx + 1} of {len(message_jsons)}...')
                                
                                # Check if required fields exist
                                if 'participants' not in msg or 'messages' not in msg:
                                    logger.warning("Missing required fields in message JSON")
                                    continue
                                    
                                # Skip group chats
                                if len(msg['participants']) > 2:
                                    groups += 1
                                    continue
                                    
                                # Skip Instagram User or empty participants
                                if (not msg['participants'] or 
                                    len(msg['participants']) == 0 or 
                                    msg['participants'][0].get('name') == 'Instagram User'):
                                    continue
                                    
                                participant_name = msg['participants'][0].get('name', 'Unknown')
                                if participant_name in Users['names'] or participant_name == 'Unknown':
                                    continue
                                
                                # Calculate reply times for this conversation
                                try:
                                    avg_reply, fastest_reply, longest_reply = calculate_reply_times(msg['messages'])
                                except Exception as e:
                                    logger.warning(f"Error calculating reply times for {participant_name}: {e}")
                                    avg_reply, fastest_reply, longest_reply = 0, 0, 0
                                
                                # Safely decode the name
                                safe_name = safe_encode_decode(participant_name)
                                
                                Users['names'].append(safe_name)
                                Users['msgs_count'].append(len(msg['messages']))
                                Users['avg_reply_time'].append(avg_reply)
                                Users['fastest_reply_time'].append(fastest_reply)
                                Users['longest_reply_time'].append(longest_reply)
                                
                            except Exception as e:
                                logger.warning(f"Error processing message conversation: {e}")
                                continue
                        
                        # Clear progress indicators
                        progress_bar.empty()
                        status_text.empty()
                    else:
                        st.warning("⚠️ No message files found in the expected location.")
                except Exception as e:
                    st.error(f"❌ Error processing message data: {e}")

                st.info(f"📭 Found **{len(deactivated_accounts)} deactivated accounts** & **{groups} group chats** - skipped from analysis")
                st.success(f"✅ Successfully processed **{len(message_jsons)}** conversations from your inbox")
                
                # Create DataFrame with error handling
                try:
                    inbox_df = pd.DataFrame(Users)
                    if not inbox_df.empty:
                        inbox_df = inbox_df[inbox_df['avg_reply_time'] != 0]
                        inbox_df = inbox_df.sort_values(by='msgs_count', ascending=False).reset_index(drop=True)
                    else:
                        st.warning("⚠️ No valid conversation data found.")
                except Exception as e:
                    st.error(f"❌ Error creating inbox DataFrame: {e}")
                    inbox_df = pd.DataFrame()

                # Process story interactions
                story_likes = None
                story_path = "your_instagram_activity/story_interactions/"
                
                try:
                    for file_name in z.namelist():
                        if file_name.startswith(story_path) and file_name.endswith("story_likes.json"):
                            try:
                                with z.open(file_name) as f:
                                    data = json.load(f)
                                    story_likes = data
                                    break
                            except json.JSONDecodeError as e:
                                st.warning(f"Invalid JSON in story likes file: {e}")
                            except Exception as e:
                                logger.warning(f"Error reading story likes file: {e}")
                except Exception as e:
                    logger.warning(f"Error processing story interactions: {e}")
                
                user_by_story = {}
                story_df = pd.DataFrame()
                
                try:
                    if story_likes and 'story_activities_story_likes' in story_likes:
                        for user in story_likes['story_activities_story_likes']:
                            try:
                                title = user.get('title', 'Unknown')
                                if title != 'Unknown':
                                    user_by_story[title] = user_by_story.get(title, 0) + 1
                            except Exception as e:
                                logger.warning(f"Error processing story like entry: {e}")
                                continue
                        
                        if user_by_story:
                            story_df = pd.Series(user_by_story).reset_index().rename(columns={'index': 'User_Name', 0: 'Story_Likes'})
                            story_df.sort_values(by='Story_Likes', ascending=False, inplace=True)
                            story_df.reset_index(inplace=True, drop=True)
                except Exception as e:
                    logger.warning(f"Error processing story data: {e}")
                    
                # Process followers and following data
                new_path = "connections/followers_and_following/"
                followers = []
                followings = {"relationships_following": []}
                close_friends = {"relationships_close_friends": []}

                try:
                    for file_name in z.namelist():
                        try:
                            if file_name.startswith(new_path):
                                if file_name.endswith("followers_1.json"):
                                    try:
                                        with z.open(file_name) as f:
                                            data = json.load(f)
                                            followers = data if isinstance(data, list) else []
                                    except json.JSONDecodeError as e:
                                        st.warning(f"Invalid JSON in followers file: {e}")
                                
                                elif file_name.endswith("following.json"):
                                    try:
                                        with z.open(file_name) as f:
                                            data = json.load(f)
                                            followings = data if isinstance(data, dict) else {"relationships_following": []}
                                    except json.JSONDecodeError as e:
                                        st.warning(f"Invalid JSON in following file: {e}")
                                
                                elif file_name.endswith("close_friends.json"):
                                    try:
                                        with z.open(file_name) as f:
                                            data = json.load(f)
                                            close_friends = data if isinstance(data, dict) else {"relationships_close_friends": []}
                                    except json.JSONDecodeError as e:
                                        st.warning(f"Invalid JSON in close friends file: {e}")
                        except Exception as e:
                            logger.warning(f"Error processing connection file {file_name}: {e}")
                            continue
                except Exception as e:
                    logger.warning(f"Error processing connection data: {e}")

        except zp.BadZipFile:
            st.error("❌ The uploaded file is not a valid ZIP file or is corrupted.")
            st.stop()
        except Exception as e:
            st.error(f"❌ An unexpected error occurred while processing the ZIP file: {e}")
            st.stop()

    # Enhanced metrics display
    try:
        st.markdown("## 📊 Your Instagram Stats")
        st.markdown("*Insights are limited to the data provided within your chosen timeframe*")

        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            try:
                follower_count = len(followers) if followers else 0
                st.metric(
                    label="👥 Followers", 
                    value=f"{follower_count:,}", 
                    help="Total number of accounts following you"
                )
            except Exception as e:
                st.metric(label="👥 Followers", value="N/A")
                logger.warning(f"Error displaying follower count: {e}")

        with col2:
            try:
                following_count = len(followings.get("relationships_following", [])) if followings else 0
                st.metric(
                    label="🔗 Following", 
                    value=f"{following_count:,}", 
                    help="Total number of accounts you follow"
                )
            except Exception as e:
                st.metric(label="🔗 Following", value="N/A")
                logger.warning(f"Error displaying following count: {e}")
            
        with col3:
            try:
                close_friends_count = len(close_friends.get("relationships_close_friends", [])) if close_friends else 0
                st.metric(
                    label="💎 Close Friends", 
                    value=f"{close_friends_count:,}", 
                    help="Number of accounts in your close friends list"
                )
            except Exception as e:
                st.metric(label="💎 Close Friends", value="N/A")
                logger.warning(f"Error displaying close friends count: {e}")
                
        with col4:
            try:
                total_conversations = len(inbox_df) if not inbox_df.empty else 0
                st.metric(
                    label="💬 Active Chats", 
                    value=f"{total_conversations:,}", 
                    help="Number of active conversation threads"
                )
            except Exception as e:
                st.metric(label="💬 Active Chats", value="N/A")
                logger.warning(f"Error displaying conversation count: {e}")

        # Enhanced sidebar controls
        st.sidebar.markdown("---")
        
        # Create friends list for dropdown
        try:
            friends_list = list(inbox_df['names']) if not inbox_df.empty else []
            friends_list.insert(0, '🌟 ALL FRIENDS')
            selected_friend = st.sidebar.selectbox(
                '🔍 **Filter By Friend**', 
                friends_list,
                help="Select a specific friend to view detailed analytics"
            )
        except Exception as e:
            logger.error(f"Error creating friends list: {e}")
            selected_friend = '🌟 ALL FRIENDS'
            st.sidebar.error("❌ Error loading friends list")

        st.sidebar.markdown("---")
        
        # Enhanced message count filter
        if not inbox_df.empty:
            min_msgs = st.sidebar.slider(
                "📊 Minimum Messages",
                min_value=1,
                max_value=int(inbox_df['msgs_count'].max()),
                value=1,
                help="Filter friends by minimum message count"
            )
        else:
            min_msgs = 1

        # Story likes section
        st.sidebar.markdown("### 📸 Story Interactions")
        if st.sidebar.button("👍 View Story Likes", use_container_width=True):
            if uploaded_zip is None:
                st.sidebar.warning('⚠️ Please upload your ZIP file first')
            else:
                with st.expander("👍 **Friends' Stories You Liked**", expanded=True):
                    try:
                        if not story_df.empty:
                            st.markdown("*Showing accounts whose stories you've liked most*")
                            st.dataframe(
                                story_df.head(20), 
                                use_container_width=True,
                                hide_index=True
                            )
                        else:
                            st.info("📭 No story interaction data found in your export.")
                    except Exception as e:
                        st.error(f"❌ Error displaying story data: {e}")

        st.sidebar.markdown("---")
        st.sidebar.markdown("### 🏆 Quick Analytics")
        st.sidebar.caption("*Based on reply times & message counts*")

        # Enhanced action buttons
        col1, col2 = st.sidebar.columns(2)
        
        press_1 = False
        press_2 = False

        with col1:
            if st.button("👑 Best Friends", use_container_width=True):
                if uploaded_zip is None:
                    st.sidebar.warning('⚠️ Upload ZIP first')
                else:
                    press_1 = True

        with col2:
            if st.button("🐌 Slow Repliers", use_container_width=True):
                if uploaded_zip is None:
                    st.sidebar.warning('⚠️ Upload ZIP first')
                else:
                    press_2 = True
        
        # Enhanced analysis results
        try:
            if press_1:
                try:
                    filtered_df = inbox_df[inbox_df['msgs_count'] >= min_msgs]
                    new_df = filtered_df[filtered_df['msgs_count'] > 50]
                    if not new_df.empty:
                        new_df = new_df.nsmallest(columns='avg_reply_time', n=10)
                        with st.expander("👑 **Your Top 10 Best Friends** (Fastest Repliers)", expanded=True):
                            st.markdown("*Friends who reply to you the fastest (minimum 50 messages)*")
                            
                            # Add formatted columns for better display
                            display_df = new_df.copy()
                            display_df['Avg Reply Time'] = display_df['avg_reply_time'].apply(format_time)
                            display_df['Fastest Reply'] = display_df['fastest_reply_time'].apply(format_time)
                            display_df['Slowest Reply'] = display_df['longest_reply_time'].apply(format_time)
                            
                            # Select and rename columns for display
                            display_columns = ['names', 'msgs_count', 'Avg Reply Time', 'Fastest Reply', 'Slowest Reply']
                            display_df = display_df[display_columns]
                            display_df.columns = ['Friend Name', 'Total Messages', 'Avg Reply Time', 'Fastest Reply', 'Slowest Reply']
                            
                            st.dataframe(display_df, use_container_width=True, hide_index=True)
                    else:
                        st.warning("⚠️ No friends with more than 50 messages found.")
                except Exception as e:
                    st.error(f"❌ Error generating best friends analysis: {e}")

            elif press_2:
                try:
                    filtered_df = inbox_df[inbox_df['msgs_count'] >= min_msgs]
                    new_df = filtered_df[filtered_df['msgs_count'] > 50]
                    if not new_df.empty:
                        new_df = new_df.nlargest(columns='avg_reply_time', n=10)
                        with st.expander("🐌 **Top 10 Slow Repliers** (Just for Fun!)", expanded=True):
                            st.markdown("*Friends who take the longest to reply (minimum 50 messages)*")
                            st.info("😄 **Note:** This is just for fun - they're still your friends!")
                            
                            # Add formatted columns for better display
                            display_df = new_df.copy()
                            display_df['Avg Reply Time'] = display_df['avg_reply_time'].apply(format_time)
                            display_df['Fastest Reply'] = display_df['fastest_reply_time'].apply(format_time)
                            display_df['Slowest Reply'] = display_df['longest_reply_time'].apply(format_time)
                            
                            # Select and rename columns for display
                            display_columns = ['names', 'msgs_count', 'Avg Reply Time', 'Fastest Reply', 'Slowest Reply']
                            display_df = display_df[display_columns]
                            display_df.columns = ['Friend Name', 'Total Messages', 'Avg Reply Time', 'Fastest Reply', 'Slowest Reply']
                            
                            st.dataframe(display_df, use_container_width=True, hide_index=True)
                    else:
                        st.warning("⚠️ No friends with more than 50 messages found.")
                except Exception as e:
                    st.error(f"❌ Error generating slow repliers analysis: {e}")
            
            else:
                with st.expander(f"📊 **Friendship Data** - {selected_friend}", expanded=True):
                    try:
                        if selected_friend == '🌟 ALL FRIENDS':
                            if not inbox_df.empty:
                                # Apply minimum message filter
                                filtered_df = inbox_df[inbox_df['msgs_count'] >= min_msgs]
                                
                                if not filtered_df.empty:
                                    # Add formatted columns for better display
                                    display_df = filtered_df.copy()
                                    display_df['Avg Reply Time'] = display_df['avg_reply_time'].apply(format_time)
                                    display_df['Fastest Reply'] = display_df['fastest_reply_time'].apply(format_time)
                                    display_df['Slowest Reply'] = display_df['longest_reply_time'].apply(format_time)
                                    
                                    # Select and rename columns for display
                                    display_columns = ['names', 'msgs_count', 'Avg Reply Time', 'Fastest Reply', 'Slowest Reply']
                                    display_df = display_df[display_columns]
                                    display_df.columns = ['Friend Name', 'Total Messages', 'Avg Reply Time', 'Fastest Reply', 'Slowest Reply']
                                    
                                    st.markdown(f"*Showing {len(display_df)} friends with {min_msgs}+ messages*")
                                    st.dataframe(display_df, use_container_width=True, hide_index=True)
                                else:
                                    st.info(f"No friends found with {min_msgs}+ messages.")
                            else:
                                st.info("📭 No friendship data available.")
                        else:
                            clean_friend_name = selected_friend.replace('🌟 ', '')
                            filtered_df = inbox_df[inbox_df['names'] == clean_friend_name]
                            if not filtered_df.empty:
                                # Add formatted columns for better display
                                display_df = filtered_df.copy()
                                display_df['Avg Reply Time'] = display_df['avg_reply_time'].apply(format_time)
                                display_df['Fastest Reply'] = display_df['fastest_reply_time'].apply(format_time)
                                display_df['Slowest Reply'] = display_df['longest_reply_time'].apply(format_time)
                                
                                # Select and rename columns for display
                                display_columns = ['names', 'msgs_count', 'Avg Reply Time', 'Fastest Reply', 'Slowest Reply']
                                display_df = display_df[display_columns]
                                display_df.columns = ['Friend Name', 'Total Messages', 'Avg Reply Time', 'Fastest Reply', 'Slowest Reply']
                                
                                st.dataframe(display_df, use_container_width=True, hide_index=True)
                            else:
                                st.info(f"📭 No data found for {clean_friend_name}.")
                    except Exception as e:
                        st.error(f"❌ Error displaying friendship data: {e}")
        except Exception as e:
            st.error(f"❌ Error in analysis display: {e}")

    except Exception as e:
        st.error(f"❌ An unexpected error occurred while displaying results: {e}")

# Enhanced charts and visualizations section
try:
    if uploaded_zip is not None and (press_1 or press_2):
        st.markdown("---")
        st.markdown("""
        <div class="chart-container">
            <h2 style="text-align: center; margin-bottom: 2rem;">🏆 Visual Friendship Insights</h2>
        </div>
        """, unsafe_allow_html=True)

        try:
            if press_1:
                st.markdown("### 👑 Top 10 Best Friends (Fastest Repliers)")
                st.markdown("*These friends reply to your messages the quickest (minimum 50 messages)*")
                
                new_df = inbox_df[inbox_df['msgs_count'] > 50]
                if not new_df.empty:
                    new_df = new_df.nsmallest(columns='avg_reply_time', n=10)

                    try:
                        # Create enhanced chart with better styling
                        base_chart = alt.Chart(new_df).add_params(
                            alt.selection_point()
                        )
                        
                        chart = base_chart.mark_bar(
                            cornerRadius=8,
                            stroke='white',
                            strokeWidth=2
                        ).encode(
                            x=alt.X("names:N", 
                                   title="Friend Name", 
                                   sort=alt.EncodingSortField(field="avg_reply_time", order="ascending"),
                                   axis=alt.Axis(labelAngle=-45)),
                            y=alt.Y("avg_reply_time:Q", 
                                   title="Average Reply Time (seconds)",
                                   axis=alt.Axis(format=',.0f')),
                            color=alt.Color("names:N", 
                                          legend=None,
                                          scale=alt.Scale(scheme="viridis")),
                            tooltip=[
                                alt.Tooltip("names:N", title="Friend"),
                                alt.Tooltip("avg_reply_time:Q", title="Avg Reply Time (s)", format='.1f'),
                                alt.Tooltip("msgs_count:Q", title="Total Messages")
                            ]
                        ).properties(
                            height=400,
                            title=alt.TitleParams(
                                text="Best Friends by Reply Speed",
                                fontSize=16,
                                fontWeight='bold'
                            )
                        )
                        
                        st.altair_chart(chart, use_container_width=True)
                        
                        # Add summary stats
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            avg_time = new_df['avg_reply_time'].mean()
                            st.metric("📊 Average Reply Time", format_time(avg_time))
                        with col2:
                            fastest_friend = new_df.iloc[0]
                            st.metric("⚡ Fastest Friend", f"{fastest_friend['names']}")
                        with col3:
                            total_msgs = new_df['msgs_count'].sum()
                            st.metric("💬 Total Messages", f"{total_msgs:,}")
                            
                    except Exception as e:
                        st.error(f"Error creating best friends chart: {e}")
                        st.dataframe(new_df, use_container_width=True)
                else:
                    st.warning("⚠️ No friends with sufficient message history for analysis.")

            if press_2:
                st.markdown("---")
                st.markdown("### 🐌 Top 10 Slow Repliers")
                st.markdown("*Friends who take longer to reply (minimum 50 messages)*")
                st.info("😄 **Remember:** This is just for fun - response time doesn't measure friendship quality!")
                
                new_df = inbox_df[inbox_df['msgs_count'] > 50]
                if not new_df.empty:
                    new_df = new_df.nlargest(columns='avg_reply_time', n=10)

                    try:
                        # Create enhanced chart for slow repliers
                        base_chart = alt.Chart(new_df).add_params(
                            alt.selection_point()
                        )
                        
                        chart = base_chart.mark_bar(
                            cornerRadius=8,
                            stroke='white',
                            strokeWidth=2
                        ).encode(
                            x=alt.X("names:N", 
                                   title="Friend Name",
                                   sort=alt.EncodingSortField(field="avg_reply_time", order="descending"),
                                   axis=alt.Axis(labelAngle=-45)),
                            y=alt.Y("avg_reply_time:Q", 
                                   title="Average Reply Time (seconds)",
                                   axis=alt.Axis(format=',.0f')),
                            color=alt.Color("names:N", 
                                          legend=None,
                                          scale=alt.Scale(scheme="plasma")),
                            tooltip=[
                                alt.Tooltip("names:N", title="Friend"),
                                alt.Tooltip("avg_reply_time:Q", title="Avg Reply Time (s)", format='.1f'),
                                alt.Tooltip("msgs_count:Q", title="Total Messages")
                            ]
                        ).properties(
                            height=400,
                            title=alt.TitleParams(
                                text="Slow Repliers (Just for Fun!)",
                                fontSize=16,
                                fontWeight='bold'
                            )
                        )
                        
                        st.altair_chart(chart, use_container_width=True)
                        
                        # Add summary stats
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            avg_time = new_df['avg_reply_time'].mean()
                            st.metric("📊 Average Reply Time", format_time(avg_time))
                        with col2:
                            slowest_friend = new_df.iloc[0]
                            st.metric("🐌 Slowest Friend", f"{slowest_friend['names']}")
                        with col3:
                            total_msgs = new_df['msgs_count'].sum()
                            st.metric("💬 Total Messages", f"{total_msgs:,}")
                            
                    except Exception as e:
                        st.error(f"Error creating slow repliers chart: {e}")
                        st.dataframe(new_df, use_container_width=True)
                else:
                    st.warning("⚠️ No friends with sufficient message history for analysis.")
        except Exception as e:
            st.error(f"❌ Error in friendship insights display: {e}")

    # Individual friend detailed analysis
    if uploaded_zip is not None and selected_friend != '🌟 ALL FRIENDS' and not (press_1 or press_2):
        try:
            clean_friend_name = selected_friend.replace('🌟 ', '')
            
            st.markdown("---")
            st.markdown(f"""
            <div class="chart-container">
                <h2 style="text-align: center;">🔍 Deep Dive: {clean_friend_name}</h2>
                <p style="text-align: center; opacity: 0.8;">Detailed friendship analytics</p>
            </div>
            """, unsafe_allow_html=True)

            # Filter data for this friend
            new_df = inbox_df[inbox_df['names'] == clean_friend_name]

            if not new_df.empty:
                try:
                    row = new_df.iloc[0]

                    # Enhanced metrics display with better styling
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        st.metric(
                            label="💬 Total Messages", 
                            value=f"{row['msgs_count']:,}",
                            help="Total messages in this conversation"
                        )
                    with col2:
                        st.metric(
                            label="⏱️ Average Reply Time", 
                            value=format_time(row['avg_reply_time']),
                            help="Average time to reply to each other"
                        )
                    with col3:
                        st.metric(
                            label="⚡ Fastest Reply", 
                            value=format_time(row['fastest_reply_time']),
                            help="The quickest response time recorded"
                        )
                    with col4:
                        st.metric(
                            label="🐢 Slowest Reply", 
                            value=format_time(row['longest_reply_time']),
                            help="The longest response time recorded"
                        )

                    # Create enhanced individual friend visualization
                    try:
                        chart_df = pd.DataFrame({
                            "Metric Type": ["Fastest Reply", "Average Reply", "Slowest Reply"],
                            "Reply Time (seconds)": [
                                row['fastest_reply_time'],
                                row['avg_reply_time'],
                                row['longest_reply_time']
                            ],
                            "Display Time": [
                                format_time(row['fastest_reply_time']),
                                format_time(row['avg_reply_time']),
                                format_time(row['longest_reply_time'])
                            ]
                        })

                        # Create horizontal bar chart
                        chart = alt.Chart(chart_df).mark_bar(
                            cornerRadius=8,
                            height=30
                        ).encode(
                            x=alt.X("Reply Time (seconds):Q", 
                                   title="Reply Time (seconds)",
                                   axis=alt.Axis(format=',.0f')),
                            y=alt.Y("Metric Type:N", 
                                   sort=["Fastest Reply", "Average Reply", "Slowest Reply"], 
                                   title="",
                                   axis=alt.Axis(labelFontSize=12)),
                            color=alt.Color("Metric Type:N", 
                                          scale=alt.Scale(
                                              domain=["Fastest Reply", "Average Reply", "Slowest Reply"],
                                              range=["#2E8B57", "#4682B4", "#DC143C"]
                                          ),
                                          legend=None),
                            tooltip=[
                                alt.Tooltip("Metric Type:N", title="Type"),
                                alt.Tooltip("Display Time:N", title="Time"),
                                alt.Tooltip("Reply Time (seconds):Q", title="Seconds", format='.1f')
                            ]
                        ).properties(
                            height=200,
                            title=alt.TitleParams(
                                text=f"Reply Time Analysis for {clean_friend_name}",
                                fontSize=16,
                                fontWeight='bold'
                            )
                        )

                        st.altair_chart(chart, use_container_width=True)
                        
                        # Add friendship insights
                        st.markdown("### 💡 Friendship Insights")
                        
                        insight_cols = st.columns(2)
                        
                        with insight_cols[0]:
                            st.markdown("""
                            <div class="feature-card">
                                <h4>📊 Communication Style</h4>
                                <ul>
                            """, unsafe_allow_html=True)
                            
                            if row['avg_reply_time'] < 300:  # Less than 5 minutes
                                st.markdown("• ⚡ **Quick Responder** - Usually replies within minutes")
                            elif row['avg_reply_time'] < 3600:  # Less than 1 hour
                                st.markdown("• 📱 **Regular Responder** - Typically replies within an hour")
                            else:
                                st.markdown("• 🎯 **Thoughtful Responder** - Takes time to craft responses")
                                
                            if row['msgs_count'] > 1000:
                                st.markdown("• 💬 **Very Active** - Lots of conversation history")
                            elif row['msgs_count'] > 500:
                                st.markdown("• 🗣️ **Good Chat** - Regular messaging")
                            else:
                                st.markdown("• 👋 **Casual Contact** - Occasional messaging")
                                
                            st.markdown("</ul></div>", unsafe_allow_html=True)
                        
                        with insight_cols[1]:
                            st.markdown("""
                            <div class="feature-card">
                                <h4>🏆 Friendship Rank</h4>
                            """, unsafe_allow_html=True)
                            
                            # Calculate friend's rank
                            sorted_df = inbox_df.sort_values('avg_reply_time')
                            friend_rank = sorted_df[sorted_df['names'] == clean_friend_name].index[0] + 1
                            total_friends = len(sorted_df)
                            percentile = (1 - (friend_rank / total_friends)) * 100
                            
                            st.markdown(f"• 🎯 **Reply Speed Rank:** #{friend_rank} out of {total_friends}")
                            st.markdown(f"• 📊 **Speed Percentile:** Top {percentile:.1f}%")
                            
                            if percentile >= 80:
                                st.markdown("• 🌟 **Category:** Super Fast Friend")
                            elif percentile >= 60:
                                st.markdown("• ⚡ **Category:** Quick Friend")
                            elif percentile >= 40:
                                st.markdown("• 📱 **Category:** Average Friend")
                            else:
                                st.markdown("• 🐌 **Category:** Slow & Steady Friend")
                                
                            st.markdown("</div>", unsafe_allow_html=True)

                    except Exception as e:
                        st.error(f"Error creating individual friend chart: {e}")
                        # Fallback to simple display
                        st.markdown("### 📊 Quick Stats")
                        st.write(f"**Average Reply Time:** {format_time(row['avg_reply_time'])}")
                        st.write(f"**Fastest Reply:** {format_time(row['fastest_reply_time'])}")
                        st.write(f"**Slowest Reply:** {format_time(row['longest_reply_time'])}")

                except (IndexError, KeyError) as e:
                    st.error(f"❌ Error accessing friend data: {e}")
            else:
                st.warning("📭 No data available for this friend.")
        except Exception as e:
            st.error(f"❌ Error displaying individual friend analysis: {e}")

    # Overview analytics section
    if uploaded_zip is not None and selected_friend == '🌟 ALL FRIENDS' and not (press_1 or press_2):
        try:
            if not inbox_df.empty:
                st.markdown("---")
                st.markdown("""
                <div class="chart-container">
                    <h2 style="text-align: center;">📈 Overall Friendship Analytics</h2>
                    <p style="text-align: center; opacity: 0.8;">Insights from all your conversations</p>
                </div>
                """, unsafe_allow_html=True)
                
                # Create overview charts
                col1, col2 = st.columns(2)
                
                with col1:
                    # Message count distribution
                    try:
                        filtered_df = inbox_df[inbox_df['msgs_count'] >= min_msgs].head(20)
                        
                        if not filtered_df.empty:
                            msg_chart = alt.Chart(filtered_df).mark_bar(
                                cornerRadius=4
                            ).encode(
                                x=alt.X("names:N", 
                                       title="Friends",
                                       sort=alt.EncodingSortField(field="msgs_count", order="descending"),
                                       axis=alt.Axis(labels=False)),
                                y=alt.Y("msgs_count:Q", 
                                       title="Message Count"),
                                color=alt.Color("msgs_count:Q",
                                              scale=alt.Scale(scheme="blues"),
                                              legend=None),
                                tooltip=[
                                    alt.Tooltip("names:N", title="Friend"),
                                    alt.Tooltip("msgs_count:Q", title="Messages")
                                ]
                            ).properties(
                                height=300,
                                title="Top 20 Friends by Message Count"
                            )
                            
                            st.altair_chart(msg_chart, use_container_width=True)
                    except Exception as e:
                        st.error(f"Error creating message count chart: {e}")
                
                with col2:
                    # Reply time distribution
                    try:
                        reply_time_df = inbox_df[inbox_df['msgs_count'] >= min_msgs].head(20)
                        
                        if not reply_time_df.empty:
                            reply_chart = alt.Chart(reply_time_df).mark_bar(
                                cornerRadius=4
                            ).encode(
                                x=alt.X("names:N", 
                                       title="Friends",
                                       sort=alt.EncodingSortField(field="avg_reply_time", order="ascending"),
                                       axis=alt.Axis(labels=False)),
                                y=alt.Y("avg_reply_time:Q", 
                                       title="Avg Reply Time (seconds)"),
                                color=alt.Color("avg_reply_time:Q",
                                              scale=alt.Scale(scheme="oranges"),
                                              legend=None),
                                tooltip=[
                                    alt.Tooltip("names:N", title="Friend"),
                                    alt.Tooltip("avg_reply_time:Q", title="Avg Reply Time (s)", format='.1f')
                                ]
                            ).properties(
                                height=300,
                                title="Top 20 Friends by Reply Speed"
                            )
                            
                            st.altair_chart(reply_chart, use_container_width=True)
                    except Exception as e:
                        st.error(f"Error creating reply time chart: {e}")
                
                # Summary statistics
                st.markdown("### 📊 Your Messaging Summary")
                
                summary_col1, summary_col2, summary_col3, summary_col4 = st.columns(4)
                
                with summary_col1:
                    total_messages = inbox_df['msgs_count'].sum()
                    st.metric("💬 Total Messages", f"{total_messages:,}")
                
                with summary_col2:
                    avg_reply_time = inbox_df['avg_reply_time'].mean()
                    st.metric("⏱️ Overall Avg Reply", format_time(avg_reply_time))
                
                with summary_col3:
                    most_active = inbox_df.loc[inbox_df['msgs_count'].idxmax(), 'names']
                    st.metric("🏆 Most Active Chat", most_active)
                
                with summary_col4:
                    fastest_replier = inbox_df.loc[inbox_df['avg_reply_time'].idxmin(), 'names']
                    st.metric("⚡ Fastest Replier", fastest_replier)
                
        except Exception as e:
            st.error(f"❌ Error displaying overview analytics: {e}")

except Exception as e:
    logger.error(f"Unexpected error in main application flow: {e}")
    st.error("❌ An unexpected error occurred. Please try refreshing the page and uploading your file again.")

# Footer with additional information
if uploaded_zip is not None:
    st.markdown("---")
    st.markdown("""
    <div class="feature-card" style="margin-top: 2rem;">
        <h3>💡 Understanding Your Results</h3>
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 1rem;">
            <div>
                <strong>⚡ Reply Times:</strong> Calculated from actual message timestamps. Faster times indicate more responsive conversations.
            </div>
            <div>
                <strong>📊 Message Counts:</strong> Total messages in each conversation thread, including both sent and received.
            </div>
            <div>
                <strong>🎯 Data Scope:</strong> Analysis limited to the timeframe of your Instagram data export request.
            </div>
            <div>
                <strong>🔒 Privacy:</strong> All processing happens locally in your browser - no data is stored or transmitted.
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# Tips and tricks section
with st.expander("💡 **Tips & Tricks for Better Analysis**"):
    st.markdown("""
    <div class="feature-card">
        <h4>🎯 Getting the Best Results</h4>
        <ul>
            <li><strong>📅 Date Range:</strong> For comprehensive analysis, request "All time" data when downloading from Instagram</li>
            <li><strong>📊 Minimum Messages:</strong> Use the sidebar filter to focus on meaningful conversations (e.g., 50+ messages)</li>
            <li><strong>🔍 Individual Analysis:</strong> Select specific friends from the dropdown for detailed insights</li>
            <li><strong>📱 Mobile vs Desktop:</strong> Both download methods work equally well - choose what's convenient for you</li>
            <li><strong>⚡ Performance:</strong> Larger exports may take longer to process - be patient during upload</li>
        </ul>
        <h4>🤔 Understanding Your Data</h4>
        <ul>
            <li><strong>Reply Times:</strong> Based on actual message timestamps, not read receipts</li>
            <li><strong>Group Chats:</strong> Automatically excluded to focus on 1-on-1 friendships</li>
            <li><strong>Deactivated Accounts:</strong> Filtered out as they can't reply anymore</li>
            <li><strong>Story Interactions:</strong> Shows stories you've liked, indicating your engagement level</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

# Final call-to-action if no file uploaded
if uploaded_zip is None:
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; padding: 2rem; background: linear-gradient(135deg, rgba(102, 126, 234, 0.1), rgba(118, 75, 162, 0.1)); border-radius: 16px; margin: 2rem 0;">
        <h3>🚀 Ready to Discover Your Instagram Friendships?</h3>
        <p style="font-size: 1.1rem; opacity: 0.9;">Upload your Instagram data ZIP file above to get started!</p>
        <p style="opacity: 0.7;">The analysis will reveal fascinating insights about your social connections.</p>
    </div>
    """, unsafe_allow_html=True)