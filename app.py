import streamlit as st
import os
import time
import json
import pandas as pd
from datetime import datetime

# Streamlit Page Config
st.set_page_config(
    page_title="YouTube Thumbnail Lead Finder",
    page_icon="🎥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Import our custom modules
from modules.utils import (
    logger, load_config, save_config, get_streamlit_logs, 
    clear_streamlit_logs, mark_channel_processed, load_processed_channels,
    setup_directories, THUMBNAILS_DIR
)
from modules.youtube_api import search_channels_api, fetch_recent_videos_api
from modules.yt_dlp_search import search_channels_ytdlp, fetch_recent_videos_ytdlp
from modules.contact_extractor import extract_channel_lead_contacts
from modules.thumbnail_analysis import download_thumbnail, analyze_single_thumbnail, analyze_brand_consistency
from modules.scoring import calculate_lead_score
from modules.exporter import export_leads
from modules.ui_helpers import inject_premium_styles, inject_metric_card, get_mock_leads

# Ensure directories exist
setup_directories()

# Initialize session state for lead data
if "leads" not in st.session_state:
    st.session_state.leads = []
if "is_searching" not in st.session_state:
    st.session_state.is_searching = False
if "current_channel" not in st.session_state:
    st.session_state.current_channel = ""
if "processed_count" not in st.session_state:
    st.session_state.processed_count = 0
if "search_logs" not in st.session_state:
    st.session_state.search_logs = ""

# Load configurations
config = load_config()

# Inject custom styles for dark SaaS theme
inject_premium_styles()

# ----------------- SIDEBAR CONFIGURATION -----------------
st.sidebar.markdown(
    """
    <div style='text-align: center; padding-bottom: 20px;'>
        <h2 style='margin-bottom: 0px;'>🎥 Controls</h2>
        <p style='color: #64748b; font-size: 0.85rem;'>Configure the lead generation engine</p>
    </div>
    """,
    unsafe_allow_html=True
)

# Section: Niche & API Mode
st.sidebar.markdown("### 🔍 Search Settings")
niche_query = st.sidebar.text_input("Niche / Keyword", value="gaming reviews", help="Keywords to search YouTube for channel candidates.")
country_code = st.sidebar.text_input("Country Code (ISO)", value="US", max_chars=2, help="Filter channel searches to specific regions (e.g. US, GB, CA). Leave blank for global.")
max_scan = st.sidebar.slider("Max Channels to Scan", min_value=1, max_value=50, value=config.get("max_channels_scan", 10))

st.sidebar.markdown("### 🛡️ API & Backend Mode")
backend_mode = st.sidebar.selectbox(
    "Search Mode",
    ["Hybrid Mode", "YouTube API", "yt-dlp fallback"],
    index=["Hybrid Mode", "YouTube API", "yt-dlp fallback"].index(config.get("backend_mode", "Hybrid Mode"))
)
api_key = st.sidebar.text_input("YouTube API Key", value=config.get("api_key", ""), type="password", help="Standard YouTube Data API v3 key. Free to obtain from Google Cloud.")

# Section: Filtering Limits
st.sidebar.markdown("### 📊 Target Filters")
sub_min = st.sidebar.number_input("Min Subscribers", min_value=0, max_value=10000000, value=config.get("subscribers_min", 1000), step=500)
sub_max = st.sidebar.number_input("Max Subscribers", min_value=0, max_value=10000000, value=config.get("subscribers_max", 70000), step=500)
min_videos = st.sidebar.number_input("Min Video Uploads", min_value=0, max_value=10000, value=config.get("min_videos", 4), step=1)

# Section: CV Scoring Threshold Controls
st.sidebar.markdown("### 🎛️ Thumbnail Thresholds")
t_blur = st.sidebar.slider("Blur Threshold (Variance)", min_value=10.0, max_value=500.0, value=config.get("thresholds", {}).get("blur_variance", 100.0), step=5.0, help="Lower values flag more blur. Default 100.0")
t_contrast = st.sidebar.slider("Contrast Threshold", min_value=0.01, max_value=0.2, value=config.get("thresholds", {}).get("contrast_low", 0.05), step=0.01, help="Fraction threshold for low contrast check. Default 0.05")
t_colorful = st.sidebar.slider("Colorfulness Threshold", min_value=5.0, max_value=100.0, value=config.get("thresholds", {}).get("colorfulness_low", 20.0), step=2.0, help="Average colorfulness metric. Default 20.0")
t_ocr_max = st.sidebar.slider("Max OCR Characters", min_value=10, max_value=200, value=config.get("thresholds", {}).get("max_ocr_text_length", 50), step=5, help="Flags excess text on thumbnail. Default 50")
t_clutter = st.sidebar.slider("Clutter Edge Ratio", min_value=0.05, max_value=0.5, value=config.get("thresholds", {}).get("clutter_ratio", 0.15), step=0.01, help="Edge density threshold. Default 0.15")
t_consistency = st.sidebar.slider("Branding Consistency", min_value=0.1, max_value=1.0, value=config.get("thresholds", {}).get("consistency_threshold", 0.8), step=0.05, help="HSV correlation average limit. Default 0.8")

# Section: Advanced Toggles
st.sidebar.markdown("### ⚙️ Advanced Settings")
enable_ocr = st.sidebar.checkbox("Enable OCR Text Check", value=config.get("ocr_enabled", True))
enable_face = st.sidebar.checkbox("Enable Face Detection", value=config.get("face_detection_enabled", True))
enable_website = st.sidebar.checkbox("Enable Website Scraping", value=config.get("website_scraping_enabled", True))
skip_processed = st.sidebar.checkbox("Skip Processed Channels", value=config.get("skip_processed", True))

mock_mode = st.sidebar.checkbox("🎨 Use Mock Data (UI Testing)", value=False, help="Disable real search & scraping, load instant mock dataset with thumbnails.")

# Save updated config
if st.sidebar.button("💾 Save Config Defaults"):
    updated_config = {
        "api_key": api_key,
        "subscribers_min": int(sub_min),
        "subscribers_max": int(sub_max),
        "min_videos": int(min_videos),
        "max_channels_scan": int(max_scan),
        "backend_mode": backend_mode,
        "ocr_enabled": enable_ocr,
        "face_detection_enabled": enable_face,
        "website_scraping_enabled": enable_website,
        "export_format": config.get("export_format", "XLSX"),
        "skip_processed": skip_processed,
        "thresholds": {
            "blur_variance": t_blur,
            "contrast_low": t_contrast,
            "colorfulness_low": t_colorful,
            "max_ocr_text_length": t_ocr_max,
            "clutter_ratio": t_clutter,
            "consistency_threshold": t_consistency
        },
        "scoring_weights": config.get("scoring_weights", {})
    }
    save_config(updated_config)
    st.sidebar.success("Defaults saved to config.json!")

# ----------------- MAIN DASHBOARD HEADER -----------------
st.markdown("<h1 class='main-title'>YouTube Thumbnail Lead Finder</h1>", unsafe_allow_html=True)
st.markdown("<p class='main-subtitle'>Find high-potential outreach leads with poor thumbnails and public contact details.</p>", unsafe_allow_html=True)

# Toggle mock dataset if selected
if mock_mode:
    if not st.session_state.leads or any(not str(lead["channel_id"]).startswith("UC_mock_") for lead in st.session_state.leads):
        st.session_state.leads = get_mock_leads()
        st.session_state.processed_count = len(st.session_state.leads)
        logger.info("Sandbox Mode: Realistic mock leads loaded.")
else:
    # Clear mock leads if we toggle back to real crawling
    if st.session_state.leads and any(str(lead["channel_id"]).startswith("UC_mock_") for lead in st.session_state.leads):
        st.session_state.leads = []
        st.session_state.processed_count = 0

# ----------------- METRIC CARDS GRID -----------------
leads_data = st.session_state.leads

# Calculate lead metrics
channels_scanned = st.session_state.processed_count
valid_leads = len(leads_data)
contacts_found = sum(1 for lead in leads_data if any(lead.get("contacts", {}).values()))
emails_found = sum(1 for lead in leads_data if lead.get("contacts", {}).get("email"))
avg_score = int(pd.Series([lead["lead_score"] for lead in leads_data]).mean()) if leads_data else 0

hot_count = sum(1 for lead in leads_data if lead["lead_priority"] == "Hot Lead")
warm_count = sum(1 for lead in leads_data if lead["lead_priority"] == "Warm Lead")
low_count = sum(1 for lead in leads_data if lead["lead_priority"] == "Low Lead")

m_col1, m_col2, m_col3, m_col4, m_col5 = st.columns(5)
with m_col1:
    inject_metric_card("Channels Scanned", channels_scanned)
with m_col2:
    inject_metric_card("Valid Leads", valid_leads)
with m_col3:
    inject_metric_card("Emails Found", emails_found)
with m_col4:
    inject_metric_card("Avg Lead Score", f"{avg_score}/100")
with m_col5:
    st.markdown(
        f"""
        <div class="metric-card" style="border-color: rgba(239, 68, 68, 0.25);">
            <div class="metric-label" style="color: #ef4444;">Hot / Warm Leads</div>
            <div class="metric-value" style="color: #ef4444;">{hot_count} <span style="font-size: 1rem; color:#f59e0b;">/ {warm_count}</span></div>
        </div>
        """,
        unsafe_allow_html=True
    )

st.markdown("<div style='margin-bottom: 25px;'></div>", unsafe_allow_html=True)

# ----------------- TRIGGER SEARCH / CANCEL SECTION -----------------
t_col1, t_col2 = st.columns([1, 4])
with t_col1:
    if st.session_state.is_searching:
        if st.button("🛑 Stop Scan"):
            st.session_state.is_searching = False
            logger.info("Search scanning stopped by user.")
            st.rerun()
    else:
        if st.button("🚀 Start Lead Scan", disabled=mock_mode):
            st.session_state.is_searching = True
            st.session_state.processed_count = 0
            st.session_state.leads = []
            clear_streamlit_logs()
            logger.info("Search initiated by user.")
            st.rerun()

with t_col2:
    if st.session_state.is_searching:
        st.markdown(
            f"""
            <div style="background-color: rgba(59, 130, 246, 0.1); border: 1px solid rgba(59, 130, 246, 0.2); border-radius: 8px; padding: 10px 15px; color: #60a5fa;">
                🧬 Scanning Channel: <b>{st.session_state.current_channel if st.session_state.current_channel else 'Searching candidates...'}</b>
            </div>
            """, 
            unsafe_allow_html=True
        )
    elif mock_mode:
        st.markdown(
            """
            <div style="background-color: rgba(168, 85, 247, 0.1); border: 1px solid rgba(168, 85, 247, 0.2); border-radius: 8px; padding: 10px 15px; color: #c084fc;">
                🎨 <b>Sandbox Mock Mode is active.</b> Real web scraping and API limits are bypassed for testing the Streamlit UI.
            </div>
            """, 
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            """
            <div style="background-color: rgba(22, 28, 38, 0.5); border: 1px solid rgba(255, 255, 255, 0.05); border-radius: 8px; padding: 10px 15px; color: #94a3b8;">
                ⚠️ <b>Ready to search.</b> Enter keywords and press 'Start Lead Scan' (uses Hybrid Mode automatically).
            </div>
            """,
            unsafe_allow_html=True
        )

# ----------------- REAL-TIME CRAWLING PIPELINE -----------------
if st.session_state.is_searching and not mock_mode:
    # Set up UI placeholder components
    progress_bar = st.progress(0.0)
    status_msg = st.empty()
    
    # 1. Identify Search Mode & Gather Channel Candidates
    mode_to_use = backend_mode
    channels = []
    
    # Check Hybrid resolution
    if mode_to_use == "Hybrid Mode":
        if api_key:
            mode_to_use = "YouTube API"
            logger.info("Hybrid Mode: API key provided, initiating YouTube API search.")
        else:
            mode_to_use = "yt-dlp fallback"
            logger.warning("Hybrid Mode: API Key missing. Falling back to yt-dlp scraping automatically.")
            
    # Run Search
    try:
        if mode_to_use == "YouTube API":
            channels = search_channels_api(
                api_key=api_key,
                keyword=niche_query,
                max_results=max_scan,
                region_code=country_code if country_code else None,
                sub_min=sub_min,
                sub_max=sub_max,
                min_videos=min_videos
            )
        else:
            channels = search_channels_ytdlp(
                keyword=niche_query,
                max_results=max_scan,
                sub_min=sub_min,
                sub_max=sub_max,
                min_videos=min_videos
            )
    except Exception as e:
        logger.error(f"Channel search failed: {e}")
        # In hybrid mode, try to fallback if first failed
        if backend_mode == "Hybrid Mode" and mode_to_use == "YouTube API":
            logger.warning("Attempting yt-dlp fallback search after API failed...")
            try:
                channels = search_channels_ytdlp(
                    keyword=niche_query,
                    max_results=max_scan,
                    sub_min=sub_min,
                    sub_max=sub_max,
                    min_videos=min_videos
                )
            except Exception as ex:
                logger.error(f"Fallback search failed too: {ex}")
                st.error("Both YouTube API and yt-dlp search failed. Check your internet connection or try again.")
                st.session_state.is_searching = False
                st.rerun()
        else:
            st.error(f"Search failed: {e}")
            st.session_state.is_searching = False
            st.rerun()

    # If no channels found
    if not channels:
        logger.warning("No channel candidates matched the search filters.")
        st.session_state.is_searching = False
        st.info("No channels found. Try adjusting keywords or subscriber ranges.")
        st.rerun()

    # Load previously processed duplicate tracker
    processed_channels = load_processed_channels()

    # Start loop over found channels
    scanned_lead_items = []
    
    for idx, channel in enumerate(channels):
        # Stop scan check
        if not st.session_state.is_searching:
            break
            
        channel_id = channel["channel_id"]
        channel_name = channel["channel_name"]
        
        st.session_state.current_channel = channel_name
        st.session_state.processed_count = idx + 1
        
        # Update progress
        progress_val = float((idx + 1) / len(channels))
        progress_bar.progress(progress_val)
        status_msg.markdown(f"**Scanning Channel {idx+1}/{len(channels)}:** `{channel_name}`")
        
        # Check duplicate
        if skip_processed and channel_id in processed_channels:
            logger.info(f"Duplicate found. Skipping already processed channel: {channel_name}")
            continue

        # Load threshold config mapping
        cv_thresholds = {
            "blur_variance": t_blur,
            "contrast_low": t_contrast,
            "colorfulness_low": t_colorful,
            "max_ocr_text_length": t_ocr_max,
            "clutter_ratio": t_clutter
        }

        # 2. Gather Recent Video Uploads
        logger.info(f"Processing candidate channel: '{channel_name}'...")
        videos = []
        if mode_to_use == "YouTube API":
            videos = fetch_recent_videos_api(
                api_key=api_key,
                uploads_playlist_id=channel["uploads_playlist_id"],
                limit=4
            )
        else:
            videos = fetch_recent_videos_ytdlp(
                channel_url=channel["channel_url"],
                limit=4
            )
            
        if not videos or len(videos) < 1:
            logger.warning(f"Could not retrieve recent uploads for channel: {channel_name}. Skipping.")
            continue

        # 3. Public Contact Extraction
        contacts = extract_channel_lead_contacts(
            channel_desc=channel["description"],
            videos=videos,
            enable_web_scraping=enable_website
        )

        # 4. Download and CV Quality Analysis
        thumbnails_analysis = []
        downloaded_paths = []
        
        for vid in videos:
            t_url = vid.get("thumbnail_url")
            v_id = vid.get("video_id")
            
            local_img_path = download_thumbnail(channel_id, v_id, t_url)
            if local_img_path:
                downloaded_paths.append(local_img_path)
                # Analyze single image
                cv_res = analyze_single_thumbnail(
                    local_path=local_img_path,
                    ocr_enabled=enable_ocr,
                    face_enabled=enable_face,
                    thresholds=cv_thresholds
                )
                thumbnails_analysis.append(cv_res)
            else:
                logger.warning(f"Skipped CV analysis for video {v_id} due to failed thumbnail download.")
                
        # Skip channel if no thumbnails could be analyzed
        if not thumbnails_analysis:
            logger.warning(f"No thumbnails downloaded for channel {channel_name}. Skipping.")
            continue

        # 5. Evaluate Style Consistency
        consistent, cons_score = analyze_brand_consistency(
            thumbnail_paths=downloaded_paths,
            consistency_threshold=t_consistency
        )
        
        # Inject consistency flag inside first video analysis block for the scorer
        for item in thumbnails_analysis:
            item["brand_consistency"] = consistent

        # 6. Apply Rules & Score Leads
        score_val, priority_val, issues_val, suggestions_val = calculate_lead_score(
            analysis_results=thumbnails_analysis,
            contacts=contacts,
            config={"scoring_weights": config.get("scoring_weights", {})}
        )

        # Compile final Lead structure
        lead_item = {
            "channel_id": channel_id,
            "channel_name": channel_name,
            "channel_url": channel_url if (channel.get("channel_url") is None or not channel["channel_url"]) else channel["channel_url"],
            "subscribers": channel["subscribers"],
            "video_count": channel["video_count"],
            "contacts": contacts,
            "recent_videos": videos,
            "cv_analysis": thumbnails_analysis,
            "brand_consistency": consistent,
            "lead_score": score_val,
            "lead_priority": priority_val,
            "thumbnail_issues": issues_val,
            "improvement_suggestions": suggestions_val,
            "status": "Processed",
            "manual_review_status": "Needs Manual Review",
            "created_at": datetime.now().isoformat()
        }
        
        scanned_lead_items.append(lead_item)
        mark_channel_processed(channel_id, channel_name)
        
        # Log lead summary
        logger.info(f"Scored Lead '{channel_name}': Score={score_val}/100, Priority={priority_val}. Issues count={len(issues_val)}")
        
        # Dynamic UI Update: append lead to state and force refresh lists
        st.session_state.leads.append(lead_item)
        
        # Take a gentle breath to prevent API rate limits
        time.sleep(1)

    # Done with search loop
    st.session_state.is_searching = False
    logger.info(f"Crawling complete. Extracted {len(scanned_lead_items)} leads.")
    st.success("Lead scan completed!")
    st.rerun()

# ----------------- FILTERS ABOVE RESULTS TABLE -----------------
st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
st.markdown("### 📋 Filter & Manage Extracted Leads")

if not leads_data:
    st.info("No leads available. Start a search scan or enable Mock Mode in the sidebar to populate data.")
else:
    f_col1, f_col2, f_col3 = st.columns([1, 1, 1])
    with f_col1:
        priority_filter = st.selectbox(
            "Priority Filter",
            ["All Leads", "Hot Leads Only", "Warm Leads Only", "Low Leads Only"]
        )
    with f_col2:
        contact_filter = st.selectbox(
            "Contact Availability",
            ["All Records", "Has Any Contact", "Has Email", "Has Instagram / X", "Needs Manual Review"]
        )
    with f_col3:
        review_filter = st.selectbox(
            "Manual Review State",
            ["All", "Approved Only", "Rejected Only", "Needs Review Only"]
        )

    # Compile Table DataFrame
    rows = []
    for idx, lead in enumerate(leads_data):
        contacts = lead.get("contacts", {})
        has_contact = "Yes" if any(contacts.values()) else "No"
        
        rows.append({
            "Index": idx,
            "Channel ID": lead["channel_id"],
            "Channel Name": lead["channel_name"],
            "Channel URL": lead["channel_url"],
            "Subscribers": lead["subscribers"],
            "Videos": lead["video_count"],
            "Email": contacts.get("email", ""),
            "Instagram": contacts.get("instagram", ""),
            "X/Twitter": contacts.get("twitter_x", ""),
            "Website": contacts.get("website", ""),
            "Lead Score": lead["lead_score"],
            "Lead Priority": lead["lead_priority"],
            "Issues Count": len(lead["thumbnail_issues"]),
            "Contact Found": has_contact,
            "Manual Review Status": lead.get("manual_review_status", "Needs Manual Review")
        })
        
    df_leads = pd.DataFrame(rows)

    # Apply Table filters
    filtered_df = df_leads.copy()
    
    if priority_filter == "Hot Leads Only":
        filtered_df = filtered_df[filtered_df["Lead Priority"] == "Hot Lead"]
    elif priority_filter == "Warm Leads Only":
        filtered_df = filtered_df[filtered_df["Lead Priority"] == "Warm Lead"]
    elif priority_filter == "Low Leads Only":
        filtered_df = filtered_df[filtered_df["Lead Priority"] == "Low Lead"]
        
    if contact_filter == "Has Any Contact":
        filtered_df = filtered_df[filtered_df["Contact Found"] == "Yes"]
    elif contact_filter == "Has Email":
        filtered_df = filtered_df[filtered_df["Email"].astype(str).str.strip() != ""]
    elif contact_filter == "Has Instagram / X":
        filtered_df = filtered_df[
            (filtered_df["Instagram"].astype(str).str.strip() != "") | 
            (filtered_df["X/Twitter"].astype(str).str.strip() != "")
        ]
    elif contact_filter == "Needs Manual Review":
        # Keep cases where contact found is 'No'
        filtered_df = filtered_df[filtered_df["Contact Found"] == "No"]
        
    if review_filter == "Approved Only":
        filtered_df = filtered_df[filtered_df["Manual Review Status"] == "Approved"]
    elif review_filter == "Rejected Only":
        filtered_df = filtered_df[filtered_df["Manual Review Status"] == "Rejected"]
    elif review_filter == "Needs Review Only":
        filtered_df = filtered_df[filtered_df["Manual Review Status"] == "Needs Manual Review"]

    # Show active interactive dataframe
    if filtered_df.empty:
        st.warning("No records match the selected grid filters.")
    else:
        st.markdown(f"Matching Leads found: **{len(filtered_df)}**")
        
        # Display editable results table to modify reviews
        edited_df = st.data_editor(
            filtered_df.drop(columns=["Index"]),
            column_config={
                "Manual Review Status": st.column_config.SelectboxColumn(
                    "Manual Review Status",
                    help="Update validation status",
                    width="medium",
                    options=["Needs Manual Review", "Approved", "Rejected"],
                    required=True
                ),
                "Channel URL": st.column_config.LinkColumn("Channel URL"),
                "Website": st.column_config.LinkColumn("Website")
            },
            disabled=["Channel ID", "Channel Name", "Subscribers", "Videos", "Email", "Instagram", "X/Twitter", "Lead Score", "Lead Priority", "Issues Count", "Contact Found"],
            hide_index=True,
            use_container_width=True,
            key="leads_editor"
        )
        
        # Synchronize manual review changes from data_editor back to session state!
        if st.session_state.get("leads_editor") and "edited_rows" in st.session_state.leads_editor:
            changes = st.session_state.leads_editor["edited_rows"]
            for row_idx_str, change_dict in changes.items():
                if "Manual Review Status" in change_dict:
                    new_val = change_dict["Manual Review Status"]
                    # Map filtered row index back to original index
                    match_idx = filtered_df.iloc[int(row_idx_str)]["Index"]
                    # Update source state
                    st.session_state.leads[match_idx]["manual_review_status"] = new_val
                    logger.info(f"Updated status of lead '{st.session_state.leads[match_idx]['channel_name']}' to: {new_val}")
                    st.rerun()

st.markdown("</div>", unsafe_allow_html=True)

# ----------------- LEADS DETAILED COMPARISON PREVIEW CARDS -----------------
st.markdown("## 🔎 Thumbnail Deep Dive & Lead Details")

if not leads_data:
    st.write("Perform a scan to inspect channels here.")
else:
    # Filter lead objects for cards display
    visible_leads = []
    for idx, lead in enumerate(leads_data):
        contacts = lead.get("contacts", {})
        has_contact = "Yes" if any(contacts.values()) else "No"
        
        # Apply filters in sync with table selection
        p_match = True
        if priority_filter == "Hot Leads Only" and lead["lead_priority"] != "Hot Lead":
            p_match = False
        elif priority_filter == "Warm Leads Only" and lead["lead_priority"] != "Warm Lead":
            p_match = False
        elif priority_filter == "Low Leads Only" and lead["lead_priority"] != "Low Lead":
            p_match = False
            
        c_match = True
        if contact_filter == "Has Any Contact" and has_contact == "No":
            c_match = False
        elif contact_filter == "Has Email" and not contacts.get("email"):
            c_match = False
        elif contact_filter == "Has Instagram / X" and not (contacts.get("instagram") or contacts.get("twitter_x")):
            c_match = False
        elif contact_filter == "Needs Manual Review" and has_contact == "Yes":
            c_match = False
            
        r_match = True
        if review_filter == "Approved Only" and lead.get("manual_review_status") != "Approved":
            r_match = False
        elif review_filter == "Rejected Only" and lead.get("manual_review_status") != "Rejected":
            r_match = False
        elif review_filter == "Needs Review Only" and lead.get("manual_review_status") != "Needs Manual Review":
            r_match = False
            
        if p_match and c_match and r_match:
            # Keep original index reference for updates
            visible_leads.append((idx, lead))

    if not visible_leads:
        st.info("No detailed cards match current filters.")
    else:
        for orig_idx, lead in visible_leads:
            priority_tag = ""
            if lead["lead_priority"] == "Hot Lead":
                priority_tag = "<span class='tag-hot'>🔥 Hot Lead</span>"
            elif lead["lead_priority"] == "Warm Lead":
                priority_tag = "<span class='tag-warm'>⚡ Warm Lead</span>"
            else:
                priority_tag = "<span class='tag-low'>❄️ Low Priority</span>"

            st.markdown(
                f"""
                <div class="glass-card">
                    <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid rgba(255,255,255,0.06); padding-bottom: 15px; margin-bottom: 15px;">
                        <div>
                            <h3 style="margin: 0px; font-size: 1.4rem;">👤 {lead['channel_name']}</h3>
                            <a href="{lead['channel_url']}" target="_blank" style="color: #60a5fa; font-size: 0.9rem; text-decoration: none;">🔗 Visit Channel URL</a>
                        </div>
                        <div style="text-align: right;">
                            <div style="font-size: 1.25rem; font-weight: 700; color: #ffffff;">Score: <span style="color:#10b981;">{lead['lead_score']}/100</span></div>
                            {priority_tag}
                        </div>
                    </div>
                """,
                unsafe_allow_html=True
            )

            # Details: Statistics, Contacts, Issues, and Actions
            col_d1, col_d2, col_d3 = st.columns([1, 1, 1.2])
            
            with col_d1:
                st.markdown("#### 📊 Stats")
                st.write(f"👥 **Subscribers:** {lead['subscribers']:,}")
                st.write(f"🎬 **Upload Count:** {lead['video_count']}")
                st.write(f"🏷️ **Branding Consistent:** {'Yes ✅' if lead.get('brand_consistency', True) else 'No ❌'}")
                
            with col_d2:
                st.markdown("#### 📞 Public Contacts")
                contacts = lead.get("contacts", {})
                st.write(f"✉️ **Email:** `{contacts.get('email') if contacts.get('email') else 'Not Found'}`")
                st.write(f"📸 **Instagram:** {f'[Profile]({contacts.get('instagram')})' if contacts.get('instagram') else '`Not Found` '}")
                st.write(f"🐦 **X/Twitter:** {f'[Profile]({contacts.get('twitter_x')})' if contacts.get('twitter_x') else '`Not Found` '}")
                st.write(f"🌐 **Website:** {f'[Visit Website]({contacts.get('website')})' if contacts.get('website') else '`Not Found` '}")
                
            with col_d3:
                st.markdown("#### 🎯 Outreach Review Decision")
                st.write(f"Current State: **{lead.get('manual_review_status', 'Needs Manual Review')}**")
                
                # Manual review buttons inside columns
                b_c1, b_c2, b_c3 = st.columns(3)
                with b_c1:
                    if st.button("Approve 👍", key=f"app_{orig_idx}"):
                        st.session_state.leads[orig_idx]["manual_review_status"] = "Approved"
                        logger.info(f"Approved channel lead: {lead['channel_name']}")
                        st.rerun()
                with b_c2:
                    if st.button("Reject 👎", key=f"rej_{orig_idx}"):
                        st.session_state.leads[orig_idx]["manual_review_status"] = "Rejected"
                        logger.info(f"Rejected channel lead: {lead['channel_name']}")
                        st.rerun()
                with b_c3:
                    if st.button("Reset 🔄", key=f"rst_{orig_idx}"):
                        st.session_state.leads[orig_idx]["manual_review_status"] = "Needs Manual Review"
                        logger.info(f"Reset channel lead status: {lead['channel_name']}")
                        st.rerun()

            # Thumbnail previews grid (latest 4 thumbnails side-by-side)
            st.markdown("#### 🖼️ Recent Uploads & Quality Metrics")
            videos = lead.get("recent_videos", [])
            cv_results = lead.get("cv_analysis", [])
            
            thumb_cols = st.columns(len(videos))
            for i, vid in enumerate(videos):
                with thumb_cols[i]:
                    st.markdown(
                        f"""
                        <div style="border: 1px solid rgba(255,255,255,0.05); border-radius: 8px; padding: 10px; background-color: rgba(7, 9, 14, 0.4); text-align: center; height: 100%;">
                            <img src="{vid['thumbnail_url']}" style="width: 100%; border-radius: 6px; aspect-ratio: 16/9; object-fit: cover; margin-bottom: 8px;"/>
                            <div style="font-size: 0.8rem; font-weight: 600; text-overflow: ellipsis; overflow: hidden; white-space: nowrap; width: 100%; color: #ffffff;" title="{vid['title']}">
                                {vid['title']}
                            </div>
                        """,
                        unsafe_allow_html=True
                    )
                    
                    # Display metrics if CV successfully evaluated
                    if i < len(cv_results) and "error" not in cv_results[i]:
                        cv = cv_results[i]
                        st.markdown(
                            f"""
                            <div style="text-align: left; font-size: 0.75rem; color: #94a3b8; margin-top: 8px; border-top: 1px solid rgba(255,255,255,0.05); padding-top: 5px;">
                                ❄️ <b>Blur Score:</b> {cv['blur_score']:.1f}<br/>
                                🎨 <b>Contrast Std:</b> {cv['contrast_score']:.1f}<br/>
                                🌈 <b>Colorfulness:</b> {cv['colorfulness_score']:.1f}<br/>
                                ✍️ <b>OCR chars:</b> {cv['ocr_char_count']}<br/>
                                👤 <b>Face Detected:</b> {'Yes ✅' if cv['face_detected'] else 'No ❌'}<br/>
                                🕸️ <b>Clutter:</b> {cv['clutter_score'] * 100:.1f}%<br/>
                            </div>
                            """,
                            unsafe_allow_html=True
                        )
                        
                        # Show individual issues for this specific thumbnail
                        local_issues = cv.get("issues", [])
                        if local_issues:
                            issue_badges = " ".join([f"<span style='background-color:#991b1b; color:#f87171; border-radius:4px; padding:1px 4px; font-size:0.65rem; margin-right:2px;'>{iss.replace('_', ' ')}</span>" for iss in local_issues])
                            st.markdown(f"<div style='margin-top: 5px;'>{issue_badges}</div>", unsafe_allow_html=True)
                            
                    st.markdown("</div>", unsafe_allow_html=True)

            # Lead Issues and Suggestions list
            col_iss, col_sug = st.columns(2)
            with col_iss:
                st.markdown("<p style='font-weight: 600; color: #ef4444; margin-top: 15px;'>🚨 Primary Visual Flaws Detected</p>", unsafe_allow_html=True)
                issues = lead.get("thumbnail_issues", [])
                if issues:
                    st.markdown("\n".join([f"- **{iss}**" for iss in issues]))
                else:
                    st.markdown("- No major issues detected.")
            with col_sug:
                st.markdown("<p style='font-weight: 600; color: #10b981; margin-top: 15px;'>💡 Tailored Pitch Suggestions</p>", unsafe_allow_html=True)
                suggestions = lead.get("improvement_suggestions", [])
                if suggestions:
                    st.markdown("\n".join([f"- {sug}" for sug in suggestions]))
                else:
                    st.markdown("- Pitch standard thumbnail refresh service.")

            st.markdown("</div>", unsafe_allow_html=True)

# ----------------- LEADS EXPORTER CONTROLS -----------------
st.markdown("## 💾 Export Collected Leads")
st.markdown("<div class='glass-card'>", unsafe_allow_html=True)

if not leads_data:
    st.info("No leads available to export yet. Perform a scan or activate Sandbox mode.")
else:
    e_col1, e_col2, e_col3, e_col4 = st.columns(4)
    with e_col1:
        e_filter = st.selectbox(
            "Filter Leads to Export",
            ["All", "Only Approved", "Only Hot", "Only with Contact Info", "Only with Email", "Only with Instagram/X"]
        )
    with e_col2:
        e_format = st.selectbox(
            "Spreadsheet Format",
            ["XLSX", "CSV"]
        )
    with e_col3:
        e_prefix = st.text_input(
            "Filename Prefix",
            value="youtube_thumbnail_leads"
        )
    with e_col4:
        st.markdown("<div style='margin-top: 28px;'></div>", unsafe_allow_html=True)
        if st.button("📤 Export File"):
            success, result_msg, count = export_leads(
                leads_list=leads_data,
                export_filter=e_filter,
                format_type=e_format,
                filename_prefix=e_prefix
            )
            if success:
                st.success(f"Successfully exported {count} leads!")
                st.info(f"Saved to: `{result_msg}`")
                
                # Provide instant download button directly in Streamlit!
                try:
                    with open(result_msg, "rb") as f:
                        file_data = f.read()
                    
                    st.download_button(
                        label=f"⬇️ Download {os.path.basename(result_msg)}",
                        data=file_data,
                        file_name=os.path.basename(result_msg),
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet" if e_format == "XLSX" else "text/csv"
                    )
                except Exception as ex:
                    logger.error(f"Download button generation failed: {ex}")
            else:
                st.error(f"Export failed: {result_msg}")

st.markdown("</div>", unsafe_allow_html=True)

# ----------------- SYSTEM LOGS STREAMING PANEL -----------------
st.markdown("## 📜 Real-Time System Log Terminal")
st.markdown("<div class='glass-card'>", unsafe_allow_html=True)

# Auto-update checkbox
log_container = st.empty()
log_str = get_streamlit_logs()
log_container.markdown(f"<div class='log-panel'>{log_str if log_str else '[System Active - Awaiting crawl instructions]'}</div>", unsafe_allow_html=True)

l_col1, l_col2 = st.columns([1, 6])
with l_col1:
    if st.button("🧹 Clear Log Terminal"):
        clear_streamlit_logs()
        st.rerun()
with l_col2:
    st.caption("Logs display search statuses, skipped duplicates, website scrapers, CV scores, and tesseract warnings.")

st.markdown("</div>", unsafe_allow_html=True)
