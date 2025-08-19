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

st.set_page_config(page_title="Instagram Friendship Analyzer", page_icon="📊", layout="wide")

st.title("📊 Instagram Friendship Analyzer")

st.markdown("""
## Welcome to Instagram Friendship Analyzer 👋
This tool analyzes your friendships using **messages, story interactions, close friends, and favorites**.

### How it works
1. **Request your full Instagram data** (not just messages).  
   👉 See the "How to download your data" guide below.  
   ⚠️ You can skip **Ads/Monetization** files — they're not needed.
2. **Download the ZIP** that Instagram emails you.
3. **Upload the ZIP here**.
4. The analyzer will **automatically process** your data and show results.  
   ✅ Includes **search & filter options** for exploring friends.

### Privacy
- Analysis runs **locally** in this app session.
- Only reads relevant metadata (timestamps, participants, interactions, counts).
- Media files and ad/monetization data are ignored.
""")

with st.expander("📥 How to Request & Download Your Instagram Data"):
    st.markdown("""
    ### Option A — Instagram app (mobile)
    1. Open **Instagram** → profile → **☰ Menu**.
    2. Go to **Settings and privacy** → **Your information and permissions**.
    3. Tap **Download your information** → **All of your information**.
    4. Select **JSON** format.
    5. (Optional) Pick a smaller **date range** if you want faster analysis.
    6. Submit the request, then download the ZIP from the email.
    7. ⚠️ You may skip **Ads/Monetization** files when requesting.

    <iframe width="400" height="225" 
    src="https://www.youtube.com/embed/zkgx9TCcR-4" 
    frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" 
    allowfullscreen></iframe>

    ### Option B — Instagram website (desktop)
    1. Go to **Instagram.com** → log in → profile.
    2. Click **Settings** → **Privacy and security**.
    3. Select **Download your information**.
    4. Choose **JSON** format, and request **All of your information**.
    5. (Optional) Pick a smaller **date range** if needed.
    6. Submit, then download the ZIP from your email.
    7. ⚠️ You may skip **Ads/Monetization** files when requesting.

    **Important:** Upload the ZIP without unzipping it.
    """, unsafe_allow_html=True)

uploaded_zip = st.file_uploader("📂 Upload your Instagram messages ZIP", type=["zip"])
st.sidebar.title('🎯 Search & Filter Friends')

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
    try:
        with zp.ZipFile(uploaded_zip) as z:
            try:
                # Get top folder name from the ZIP
                file_list = z.namelist()
                if not file_list:
                    st.error("❌ The uploaded ZIP file appears to be empty.")
                    st.stop()
                
                top_folder = file_list[0].split('/')[0]

                # Extract username between "instagram-" and "-YYYY-MM-DD"
                match = re.search(r"instagram-(.+?)-\d{4}-\d{2}-\d{2}", top_folder)
                if match:
                    raw_username = match.group(1)

                    # Simple encoding: UTF-8 → hex
                    try:
                        encoded_username = raw_username.encode("utf-8").hex()
                        st.info(f"📌 Detected username: **{raw_username}**")
                    except UnicodeEncodeError as e:
                        logger.warning(f"Error encoding username: {e}")
                        st.warning("⚠️ Username detected but contains special characters.")
                else:
                    st.warning("❌ Could not detect username from folder name.")
                    st.stop()
            except Exception as e:
                st.error(f"❌ Error reading ZIP file structure: {e}")
                st.stop()

            # Target inbox path
            inbox_path_prefix = f"{top_folder}/your_instagram_activity/messages/inbox/"

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

            # Process message data
            try:
                if len(message_jsons) > 0:
                    for msg in message_jsons:
                        try:
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
                else:
                    st.warning("⚠️ No message files found in the expected location.")
            except Exception as e:
                st.error(f"❌ Error processing message data: {e}")

            st.info(f"📭 {len(deactivated_accounts)} deactivated accounts & {groups} group chats found! Skipping analysis for these.")
            st.success(f"✅ Found {len(message_jsons)} message files in inbox.")
            
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
            story_path = f"{top_folder}/your_instagram_activity/story_interactions/"
            
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
            new_path = f"{top_folder}/connections/followers_and_following/"
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

    # Display metrics and interface
    try:
        st.write('\n\n\n\n')
        st.markdown("⚠️ Insights are limited to the data provided within the chosen timeframe.")

        cols = st.columns(3)
        with cols[0]:
            try:
                follower_count = len(followers) if followers else 0
                st.metric(label='Followers', value=follower_count, border=True)
            except Exception as e:
                st.metric(label='Followers', value='N/A', border=True)
                logger.warning(f"Error displaying follower count: {e}")

        with cols[1]:
            try:
                following_count = len(followings.get("relationships_following", [])) if followings else 0
                st.metric(label='Following', value=following_count, border=True)
            except Exception as e:
                st.metric(label='Following', value='N/A', border=True)
                logger.warning(f"Error displaying following count: {e}")
            
        with cols[2]:
            try:
                close_friends_count = len(close_friends.get("relationships_close_friends", [])) if close_friends else 0
                st.metric(label='Close Friends', value=close_friends_count, border=True)
            except Exception as e:
                st.metric(label='Close Friends', value='N/A', border=True)
                logger.warning(f"Error displaying close friends count: {e}")

        st.sidebar.write('\n\n\n\n')

        # Create friends list for dropdown
        try:
            friends_list = list(inbox_df['names']) if not inbox_df.empty else []
            friends_list.insert(0, 'ALL FRIENDS')
            selected_friend = st.sidebar.selectbox('**Filter By Friends**', friends_list)
        except Exception as e:
            logger.error(f"Error creating friends list: {e}")
            selected_friend = 'ALL FRIENDS'
            st.sidebar.error("Error loading friends list")

        st.sidebar.write('\n\n\n\n')

        # Story likes button
        if st.sidebar.button("👍 Your Likes on Friends' Stories"):
            if uploaded_zip is None:
                st.sidebar.warning('Please Upload The Zip File First')
            else:
                with st.expander("👍 Number of Friends' Stories You Liked"):
                    try:
                        if not story_df.empty:
                            st.dataframe(story_df)
                        else:
                            st.info("No story interaction data found.")
                    except Exception as e:
                        st.error(f"Error displaying story data: {e}")

        st.sidebar.write('\n\n\n\n')
        st.sidebar.markdown("### 🏆 Friendship Insights")
        st.sidebar.markdown("**Based on average reply times & message counts**")

        press_1 = False
        press_2 = False

        with st.sidebar:
            col1, col2 = st.columns([0.4, 0.4])

            with col1:
                if st.button("👥 Top 10 Friends"):
                    if uploaded_zip is None:
                        st.warning('Please Upload The Zip File First')
                    else:
                        press_1 = True

            with col2:
                if st.button("🐍 Top 10 Snakes"):
                    if uploaded_zip is None:
                        st.warning('Please Upload The Zip File First')
                    else:
                        press_2 = True
        
        # Display analysis results
        try:
            if press_1:
                try:
                    new_df = inbox_df[inbox_df['msgs_count'] > 50]
                    if not new_df.empty:
                        new_df = new_df.nsmallest(columns='avg_reply_time', n=10)
                        with st.expander("📊 Preview Or Download Your Friendship Data ➡️ (Top 10 Friends)"):
                            st.dataframe(new_df)
                    else:
                        st.warning("No friends with more than 50 messages found.")
                except Exception as e:
                    st.error(f"Error generating top friends analysis: {e}")

            elif press_2:
                try:
                    new_df = inbox_df[inbox_df['msgs_count'] > 50]
                    if not new_df.empty:
                        new_df = new_df.nlargest(columns='avg_reply_time', n=10)
                        with st.expander("📊 Preview Or Download Your Friendship Data ➡️ (Top 10 Snakes)"):
                            st.dataframe(new_df)
                    else:
                        st.warning("No friends with more than 50 messages found.")
                except Exception as e:
                    st.error(f"Error generating top snakes analysis: {e}")
            
            else:
                with st.expander(f"📊 Preview Or Download Your Friendship Data ➡️ ({selected_friend})"):
                    try:
                        if selected_friend == 'ALL FRIENDS':
                            if not inbox_df.empty:
                                st.dataframe(inbox_df)
                            else:
                                st.info("No friendship data available.")
                        else:
                            filtered_df = inbox_df[inbox_df['names'] == selected_friend]
                            if not filtered_df.empty:
                                st.dataframe(filtered_df)
                            else:
                                st.info(f"No data found for {selected_friend}.")
                    except Exception as e:
                        st.error(f"Error displaying friendship data: {e}")
        except Exception as e:
            st.error(f"Error in analysis display: {e}")

    except Exception as e:
        st.error(f"❌ An unexpected error occurred while displaying results: {e}")

# Container and charts section
container = st.container

try:
    if uploaded_zip is not None and (press_1 or press_2):
        with container(border=True):
            st.markdown("<h3 style='text-align: center;'>🏆 Friendship Insights</h3>", unsafe_allow_html=True)

            try:
                if press_1:
                    st.markdown("### 👑 Top 10 Closest Friends")
                    st.markdown("These are your friends with the **fastest reply times** (and at least 50+ messages).")
                    new_df = inbox_df[inbox_df['msgs_count'] > 50]
                    if not new_df.empty:
                        new_df = new_df.nsmallest(columns='avg_reply_time', n=10)

                        try:
                            chart = (
                                alt.Chart(new_df)
                                .mark_bar()
                                .encode(
                                    x=alt.X("names:N", title="Friend"),
                                    y=alt.Y("avg_reply_time:Q", title="Average Reply Time (seconds)"),
                                    color=alt.Color("names:N", legend=None),
                                    tooltip=["names", "avg_reply_time"]
                                )
                            )
                            st.altair_chart(chart, use_container_width=True)
                        except Exception as e:
                            st.error(f"Error creating chart: {e}")
                            st.dataframe(new_df)  # Fallback to table
                    else:
                        st.warning("No friends with sufficient message history for analysis.")

                if press_2:
                    st.markdown("### 🐍 Top 10 Snakes")
                    st.markdown("Friends who took the **longest to reply** (50+ messages). 🕐")
                    st.info("⚠️ Just for fun — they're not real snakes, promise! 🐍😂")
                    new_df = inbox_df[inbox_df['msgs_count'] > 50]
                    if not new_df.empty:
                        new_df = new_df.nlargest(columns='avg_reply_time', n=10)

                        try:
                            chart = (
                                alt.Chart(new_df)
                                .mark_bar()
                                .encode(
                                    x=alt.X("names:N", title="Friend"),
                                    y=alt.Y("avg_reply_time:Q", title="Average Reply Time (seconds)"),
                                    color=alt.Color("names:N", legend=None),
                                    tooltip=["names", "avg_reply_time"]
                                )
                            )
                            st.altair_chart(chart, use_container_width=True)
                        except Exception as e:
                            st.error(f"Error creating chart: {e}")
                            st.dataframe(new_df)  # Fallback to table
                    else:
                        st.warning("No friends with sufficient message history for analysis.")
            except Exception as e:
                st.error(f"Error in friendship insights display: {e}")

    # Individual friend analysis
    if uploaded_zip is not None and selected_friend != 'ALL FRIENDS' and not (press_1 or press_2):
        try:
            with container(border=True):
                st.markdown(
                    f"<h3 style='text-align: center;'>🏆 {selected_friend} Friendship Insights</h3>",
                    unsafe_allow_html=True
                )

                # Filter data for this friend
                new_df = inbox_df[inbox_df['names'] == selected_friend]

                if not new_df.empty:
                    try:
                        row = new_df.iloc[0]

                        # Metrics display
                        cols = st.columns(3)
                        with cols[0]:
                            st.metric(label="⏱️ Average Reply Time", value=format_time(row['avg_reply_time']), border=True)
                        with cols[1]:
                            st.metric(label="⚡ Fastest Reply Time", value=format_time(row['fastest_reply_time']), border=True)
                        with cols[2]:
                            st.metric(label="🐢 Slowest Reply Time", value=format_time(row['longest_reply_time']), border=True)

                        # Chart creation
                        try:
                            chart_df = pd.DataFrame({
                                "Type": ["Average", "Fastest", "Slowest"],
                                "Reply Time (s)": [
                                    row['avg_reply_time'],
                                    row['fastest_reply_time'],
                                    row['longest_reply_time']
                                ]
                            })

                            chart = (
                                alt.Chart(chart_df)
                                .mark_bar(cornerRadius=6)
                                .encode(
                                    x=alt.X("Reply Time (s):Q", title="Reply Time (seconds)"),
                                    y=alt.Y("Type:N", sort=["Fastest", "Average", "Slowest"], title=""),
                                    color=alt.Color("Type:N", scale=alt.Scale(
                                        domain=["Average", "Fastest", "Slowest"],
                                        range=["#4CAF50", "#2196F3", "#FF5722"]
                                    )),
                                    tooltip=["Type", "Reply Time (s)"]
                                )
                                .properties(height=200, width=400, title="Reply Time Breakdown")
                            )

                            st.altair_chart(chart, use_container_width=True)
                        except Exception as e:
                            st.error(f"Error creating individual friend chart: {e}")
                            # Fallback to simple display
                            st.write(f"**Reply Time Statistics for {selected_friend}:**")
                            st.write(f"- Average: {format_time(row['avg_reply_time'])}")
                            st.write(f"- Fastest: {format_time(row['fastest_reply_time'])}")
                            st.write(f"- Slowest: {format_time(row['longest_reply_time'])}")

                    except (IndexError, KeyError) as e:
                        st.error(f"Error accessing friend data: {e}")
                else:
                    st.warning("No data available for this friend.")
        except Exception as e:
            st.error(f"Error displaying individual friend analysis: {e}")

except Exception as e:
    logger.error(f"Unexpected error in main application flow: {e}")
    st.error("❌ An unexpected error occurred. Please try refreshing the page and uploading your file again.")