import streamlit as st
import os
import time
import json
import pandas as pd
import numpy as np
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go

# Streamlit Page Config
st.set_page_config(
    page_title="YouTube Thumbnail Lead Finder",
    page_icon="🎥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Import custom modules
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
from modules.ui_helpers import inject_premium_styles, get_saas_metrics, get_extended_mock_leads

# Ensure directories exist
setup_directories()

# Initialize session state variables
if "leads" not in st.session_state:
    st.session_state.leads = []
if "is_searching" not in st.session_state:
    st.session_state.is_searching = False
if "current_channel" not in st.session_state:
    st.session_state.current_channel = ""
if "processed_count" not in st.session_state:
    st.session_state.processed_count = 0
if "search_presets" not in st.session_state:
    st.session_state.search_presets = {}
if "selected_lead_idx" not in st.session_state:
    st.session_state.selected_lead_idx = 0
if "page" not in st.session_state:
    st.session_state.page = "🏠 Dashboard"
if "manual_notes" not in st.session_state:
    st.session_state.manual_notes = {}

# Load configurations
config = load_config()

# Inject premium dark luxury styles
inject_premium_styles()

# ----------------- LEFT SIDEBAR NAVIGATION -----------------
st.sidebar.markdown(
    """
    <div class="brand-logo-container">
        <div class="brand-logo-icon">🎥</div>
        <div class="brand-logo-text">Thumbnail Lead Bot</div>
    </div>
    """,
    unsafe_allow_html=True
)

st.sidebar.markdown("<p style='color: #4b5563; font-size: 0.75rem; font-weight: 700; text-transform: uppercase; margin-bottom: 8px; letter-spacing: 0.05em;'>Navigation</p>", unsafe_allow_html=True)

# State-driven Sidebar Navigation
pages = ["🏠 Dashboard", "🔍 Search Workspace", "🎯 Extracted Leads", "📊 Premium Analytics", "📁 Export Center", "⚙️ System Settings"]
for p in pages:
    is_active = st.session_state.page == p
    cls = "nav-item-active" if is_active else "nav-item-inactive"
    
    # Styled sidebar button representing a navigation menu
    if st.sidebar.button(p, key=f"btn_{p}", use_container_width=True):
        st.session_state.page = p
        st.rerun()

# Sidebar Quota Indicator
st.sidebar.markdown(
    """
    <div class="sidebar-quota-box">
        <div class="quota-text">⚡ API DAILY QUOTA LIMIT</div>
        <div class="quota-bar-bg"><div class="quota-bar-fill" style="width: 14%;"></div></div>
        <div style="display:flex; justify-content:space-between; font-size:0.7rem; color:#6b7280; font-weight: 600;">
            <span>140 / 10,000 units</span>
            <span style="color:#10b981;">Active</span>
        </div>
        <div style="font-size:0.7rem; color:#4b5563; margin-top:12px; border-top:1px solid #1f2937; padding-top:8px; text-align:center; font-family: 'JetBrains Mono', monospace;">
            v1.4.0 (Enterprise) • System Online
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

# ----------------- MOCK DATA MANAGEMENT -----------------
# We pull leads from session state
leads_data = st.session_state.leads

# ----------------- TOP GLOBAL HEADER -----------------
niche_query = config.get("last_search_niche", "Gaming Reviews")
st.markdown(
    f"""
    <div class="global-header">
        <div class="header-project">
            📁 Active Campaign: <span class="project-tag">{str(niche_query).upper()}</span>
        </div>
        <div class="header-meta">
            <span class="{"api-tag-active" if config.get("api_key") else "api-tag-inactive"}">
                {"YouTube API V3 Active" if config.get("api_key") else "yt-dlp Scraper Fallback"}
            </span>
            <div class="avatar-circle">AF</div>
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

# ----------------- THREE-PANEL LAYOUT GRID -----------------
# Split the viewport into a Workspace panel (Left/Center) and an Insights panel (Right)
workspace_col, insights_col = st.columns([3.1, 1.2])

# ----------------- 🏠 DASHBOARD PAGE -----------------
if st.session_state.page == "🏠 Dashboard":
    with workspace_col:
        st.markdown("## 🏠 Dashboard Campaign Overview")
        
        # Load mock data if list is empty to provide instant preview
        if not leads_data:
            st.session_state.leads = get_extended_mock_leads()
            st.session_state.processed_count = len(st.session_state.leads)
            leads_data = st.session_state.leads
            logger.info("Sandbox Mode: Loaded 6 structured mock channels.")
            
        # Metric Cards Row
        total_leads, hot_leads, emails, socials = get_saas_metrics(leads_data)
        
        col_m1, col_m2, col_m3, col_m4 = st.columns(4)
        with col_m1:
            st.markdown(
                f"""
                <div class="saas-card">
                    <div class="kpi-title">Channels Scanned</div>
                    <div class="kpi-value">{st.session_state.processed_count}</div>
                    <div class="kpi-trend trend-up">📈 +14.2% <span style="color:#6b7280; font-weight:normal;">since yesterday</span></div>
                </div>
                """,
                unsafe_allow_html=True
            )
        with col_m2:
            st.markdown(
                f"""
                <div class="saas-card" style="border-color: rgba(124, 77, 255, 0.3);">
                    <div class="kpi-title" style="color: #7c4dff;">Valid Leads</div>
                    <div class="kpi-value">{total_leads}</div>
                    <div class="kpi-trend trend-up">⚡ High Conversion Potential</div>
                </div>
                """,
                unsafe_allow_html=True
            )
        with col_m3:
            st.markdown(
                f"""
                <div class="saas-card" style="border-color: rgba(16, 185, 129, 0.3);">
                    <div class="kpi-title" style="color: #10b981;">Public Emails</div>
                    <div class="kpi-value">{emails}</div>
                    <div class="kpi-trend trend-up">✉️ {int(emails/total_leads * 100) if total_leads else 0}% Contact Rate</div>
                </div>
                """,
                unsafe_allow_html=True
            )
        with col_m4:
            st.markdown(
                f"""
                <div class="saas-card" style="border-color: rgba(239, 68, 68, 0.35);">
                    <div class="kpi-title" style="color: #ef4444;">Hot Lead Candidates</div>
                    <div class="kpi-value" style="color: #f87171;">{hot_leads}</div>
                    <div class="kpi-trend trend-up" style="color: #ef4444;">🔥 Ready for Outreach</div>
                </div>
                """,
                unsafe_allow_html=True
            )

        # Main Workspace Card: List of Hot Leads
        st.markdown("<div class='saas-card-glow'>", unsafe_allow_html=True)
        st.markdown("### 🔥 Top Hot Lead Matches")
        
        hot_lead_items = [l for l in leads_data if l["lead_priority"] == "Hot Lead"]
        if not hot_lead_items:
            st.write("No hot leads found in the active scan pool.")
        else:
            for hl in hot_lead_items[:4]:
                st.markdown(
                    f"""
                    <div style="display:flex; justify-content:space-between; align-items:center; background-color: rgba(255,255,255,0.02); padding:12px 18px; border-radius:8px; margin-bottom:8px; border:1px solid #1f2937;">
                        <div>
                            <span style="font-weight:700; color:#ffffff;">👤 {hl['channel_name']}</span>
                            <span style="color:#9ca3af; font-size:0.8rem; margin-left:10px;">👥 {hl['subscribers']:,} subscribers</span>
                        </div>
                        <div style="display:flex; align-items:center; gap: 15px;">
                            <span style="color:#38bdf8; font-size:0.8rem; font-family:'JetBrains Mono';">✉️ {hl['contacts'].get('email', 'Email Available')}</span>
                            <span class="priority-badge-hot">Score: {hl['lead_score']}/100</span>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Guide banner
        st.markdown(
            """
            <div class="saas-card">
                <h3>💡 Quick Outreach Campaign Recipe</h3>
                <p style="color: #9ca3af; font-size: 0.9rem; line-height: 1.5; margin-bottom: 0px;">
                    1. Go to the <b>Search Workspace</b> tab to query a specific YouTube niche.<br/>
                    2. Analyze recent channel thumbnails automatically utilizing built-in computer vision rules.<br/>
                    3. Navigate to the <b>Extracted Leads</b> tab to review generated pitch checklists and copy customized designer tips.<br/>
                    4. Export results as formatted Excel sheets in the <b>Export Center</b> for seamless mail merges.
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )

    with insights_col:
        st.markdown("### 📊 AI Quality Index")
        st.markdown("<div class='saas-card'>", unsafe_allow_html=True)
        
        # Compute overall quality metrics
        avg_lead_score = int(pd.Series([l["lead_score"] for l in leads_data]).mean()) if leads_data else 0
        consistent_channels = sum(1 for l in leads_data if l.get("brand_consistency", True))
        
        st.markdown(
            f"""
            <div style='text-align: center; margin-bottom: 25px;'>
                <div class="circle-gauge gauge-hot" style="width: 90px; height: 90px; font-size: 1.7rem; border-width: 5px;">
                    {avg_lead_score}
                </div>
                <div style="color: #9ca3af; font-size: 0.8rem; font-weight: 600; margin-top: 10px; text-transform: uppercase;">Average Lead Quality</div>
            </div>
            
            <div style="border-top:1px solid #1f2937; padding-top:15px;">
                <div style="display:flex; justify-content:space-between; margin-bottom:10px; font-size:0.85rem;">
                    <span style="color:#9ca3af;">Branding Consistent Channels</span>
                    <span style="color:#ffffff; font-weight:700;">{consistent_channels}/{len(leads_data)}</span>
                </div>
                <div style="display:flex; justify-content:space-between; margin-bottom:10px; font-size:0.85rem;">
                    <span style="color:#9ca3af;">Avg Video Upload Volume</span>
                    <span style="color:#ffffff; font-weight:700;">{int(pd.Series([l['video_count'] for l in leads_data]).mean()) if leads_data else 0} videos</span>
                </div>
                <div style="display:flex; justify-content:space-between; font-size:0.85rem;">
                    <span style="color:#9ca3af;">Niches Captured</span>
                    <span style="color:#ffffff; font-weight:700;">{len(set([l.get('niche', 'General') for l in leads_data]))} categories</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
        st.markdown("</div>", unsafe_allow_html=True)
        
        # System Activity Logs preview
        st.markdown("#### 💬 Latest System Activity")
        log_str = get_streamlit_logs()
        st.markdown(f"<div class='live-log-container' style='height: 195px;'>{log_str if log_str else '[Idle - Waiting for active scan instructions]'}</div>", unsafe_allow_html=True)

# ----------------- 🔍 SEARCH WORKSPACE PAGE -----------------
elif st.session_state.page == "🔍 Search Workspace":
    # Preset presets list
    if "saved_presets" not in st.session_state:
        st.session_state.saved_presets = {
            "Gaming Standard": {"niche": "gaming reviews", "sub_min": 1000, "sub_max": 70000, "min_vids": 4},
            "Tech Creators": {"niche": "gadget unboxing", "sub_min": 5000, "sub_max": 100000, "min_vids": 8},
            "Baking Channels": {"niche": "cake baking", "sub_min": 2000, "sub_max": 50000, "min_vids": 4}
        }
        
    with workspace_col:
        st.markdown("## 🔍 Search & Discovery Center")
        
        # Active Search Trigger Cards
        st.markdown("<div class='saas-card-glow'>", unsafe_allow_html=True)
        st.markdown("#### Save & Load Search Presets")
        p_col1, p_col2 = st.columns(2)
        with p_col1:
            load_p = st.selectbox("Load Search Preset", ["Select Preset"] + list(st.session_state.saved_presets.keys()))
            if load_p != "Select Preset" and st.button("📥 Load Preset Filters"):
                preset = st.session_state.saved_presets[load_p]
                config["last_search_niche"] = preset["niche"]
                st.sidebar.success(f"Preset '{load_p}' loaded successfully!")
                time.sleep(0.5)
                st.rerun()
        with p_col2:
            new_preset_name = st.text_input("New Preset Name", value="My Custom Campaign")
            if st.button("💾 Save Current Filters as Preset"):
                st.session_state.saved_presets[new_preset_name] = {
                    "niche": niche_query,
                    "sub_min": int(sub_min),
                    "sub_max": int(sub_max),
                    "min_vids": int(min_videos)
                }
                st.success(f"Preset '{new_preset_name}' stored in system state!")
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Primary Search Form Block
        st.markdown("<div class='saas-card'>", unsafe_allow_html=True)
        st.markdown("#### Primary Search Parameters")
        
        s_col1, s_col2 = st.columns([2, 1])
        with s_col1:
            search_input = st.text_input("Active Search Niche", value=config.get("last_search_niche", "gaming reviews"))
        with s_col2:
            region_input = st.text_input("Country Limit (ISO Code)", value=country_code, max_chars=2, help="Filter channel searches to specific regions (e.g. US, GB, CA). Leave blank for global.")
            
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Advanced Filters Accordion
        with st.expander("⚙️ Advanced visual Crawler Filters & Mode Settings", expanded=False):
            ac_col1, ac_col2 = st.columns(2)
            with ac_col1:
                st.write("**Scraper Mode Toggles**")
                st.checkbox("Enable OCR Text Extraction", value=enable_ocr)
                st.checkbox("Enable Built-in Face Checker", value=enable_face)
                st.checkbox("Crawling External Business Websites", value=enable_website)
            with ac_col2:
                st.write("**Filter Overrides**")
                st.checkbox("Skip Previously Processed Duplicates", value=skip_processed)
                
        # Trigger Panel Row
        st.markdown("<div style='margin-bottom:15px;'></div>", unsafe_allow_html=True)
        bt_col1, bt_col2 = st.columns([1, 1])
        with bt_col1:
            # Re-write config parameter to check against
            if st.session_state.is_searching:
                st.info("Scanning process is running...")
            else:
                if st.button("🚀 INITIATE LIVE SCANNING ENGINE"):
                    # Save last keyword in config
                    config["last_search_niche"] = search_input
                    save_config(config)
                    st.session_state.is_searching = True
                    st.session_state.processed_count = 0
                    st.session_state.leads = []
                    clear_streamlit_logs()
                    st.rerun()
        with bt_col2:
            if st.session_state.is_searching:
                if st.button("🛑 HALT CRAWLER ENGINE"):
                    st.session_state.is_searching = False
                    st.rerun()

    with insights_col:
        st.markdown("### 🧬 AI Agent Activity")
        
        if st.session_state.is_searching:
            st.markdown("<div class='saas-card-glow'>", unsafe_allow_html=True)
            st.markdown(
                f"""
                <div style='text-align: center;'>
                    <span style='font-size: 2.2rem;'>🧠</span>
                    <h4 style='margin-top: 10px; color:#ffffff;'>AI Scraper Running</h4>
                    <p style='color:#a855f7; font-size:0.8rem;'>Processing candidates...</p>
                </div>
                
                <div style='margin-top: 20px; border-top: 1px solid rgba(255,255,255,0.06); padding-top: 15px;'>
                    <div style='display:flex; justify-content:space-between; font-size:0.8rem; margin-bottom:8px;'>
                        <span style='color:#9ca3af;'>Scanning Lead:</span>
                        <span style='color:#ffffff; font-weight:700;'>{st.session_state.current_channel if st.session_state.current_channel else 'Searching candidates'}</span>
                    </div>
                    <div style='display:flex; justify-content:space-between; font-size:0.8rem; margin-bottom:8px;'>
                        <span style='color:#9ca3af;'>Processed Count:</span>
                        <span style='color:#ffffff; font-weight:700;'>{st.session_state.processed_count}/{max_scan}</span>
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )
            st.markdown("</div>", unsafe_allow_html=True)
        else:
            st.markdown("<div class='empty-state-card'>", unsafe_allow_html=True)
            st.markdown(
                """
                <div class="empty-state-icon">🤖</div>
                <h4>Agent Idle</h4>
                <p style="font-size: 0.8rem; margin-top: 6px;">Initiate a live scan workspace query to activate the crawler.</p>
                """,
                unsafe_allow_html=True
            )
            st.markdown("</div>", unsafe_allow_html=True)

# ----------------- 🎯 LEADS TAB (DATA GRID & DETAIL DRAWER) -----------------
elif st.session_state.page == "🎯 Extracted Leads":
    with workspace_col:
        st.markdown("## 🎯 Extracted Leads Registry")
        
        if not leads_data:
            st.markdown("<div class='empty-state-card'>", unsafe_allow_html=True)
            st.markdown(
                """
                <div class="empty-state-icon">📂</div>
                <h4>No Leads in Registry</h4>
                <p>Run a Search Campaign or turn off Mock Sandbox to fetch channels.</p>
                """,
                unsafe_allow_html=True
            )
            st.markdown("</div>", unsafe_allow_html=True)
        else:
            # Inline filters above grid
            g_col1, g_col2 = st.columns(2)
            with g_col1:
                pr_filter = st.selectbox("Filter Leads by Priority Match", ["All Priorities", "Hot Leads Only", "Warm Leads Only", "Low Leads Only"])
            with g_col2:
                co_filter = st.selectbox("Filter Leads by Contact details", ["All Records", "Has Public Email", "Has Social Account", "Needs Manual Review"])

            # Render custom list
            rows = []
            for idx, lead in enumerate(leads_data):
                contacts = lead.get("contacts", {})
                has_contact = "Yes" if any(contacts.values()) else "No"
                
                rows.append({
                    "Index": idx,
                    "Channel Name": lead["channel_name"],
                    "Subscribers": lead["subscribers"],
                    "Videos": lead["video_count"],
                    "Email": contacts.get("email", ""),
                    "Lead Score": lead["lead_score"],
                    "Lead Priority": lead["lead_priority"],
                    "Manual Review Status": lead.get("manual_review_status", "Needs Manual Review"),
                    "Contact Found": has_contact
                })
                
            df_leads = pd.DataFrame(rows)
            filtered_df = df_leads.copy()
            
            # Apply filters
            if pr_filter == "Hot Leads Only":
                filtered_df = filtered_df[filtered_df["Lead Priority"] == "Hot Lead"]
            elif pr_filter == "Warm Leads Only":
                filtered_df = filtered_df[filtered_df["Lead Priority"] == "Warm Lead"]
            elif pr_filter == "Low Leads Only":
                filtered_df = filtered_df[filtered_df["Lead Priority"] == "Low Lead"]
                
            if co_filter == "Has Public Email":
                filtered_df = filtered_df[filtered_df["Email"].astype(str).str.strip() != ""]
            elif co_filter == "Has Social Account":
                filtered_df = filtered_df[filtered_df["Contact Found"] == "Yes"]
            elif co_filter == "Needs Manual Review":
                filtered_df = filtered_df[filtered_df["Contact Found"] == "No"]
                
            # Selection table
            st.markdown(f"**Registry Count:** `{len(filtered_df)} matched`")
            
            # Select item inside grid to highlight in Side Drawer
            select_lead_name = st.selectbox(
                "🎯 Select Channel to open in Detailed Audit Drawer (Right Panel)",
                options=filtered_df["Channel Name"].tolist() if not filtered_df.empty else ["No Leads Matched"]
            )
            
            # Find selected lead index
            if select_lead_name and select_lead_name != "No Leads Matched":
                for idx, l in enumerate(leads_data):
                    if l["channel_name"] == select_lead_name:
                        st.session_state.selected_lead_idx = idx
                        break

            # Styled Leads dataframe list
            st.dataframe(
                filtered_df.drop(columns=["Index", "Contact Found"]),
                column_config={
                    "Subscribers": st.column_config.NumberColumn(format="%d"),
                    "Lead Score": st.column_config.ProgressColumn("Lead Score", min_value=0, max_value=100, format="%d"),
                    "Lead Priority": "Priority",
                    "Manual Review Status": "Review State"
                },
                hide_index=True,
                use_container_width=True
            )
            
            # Visual recent thumbnail slider inside main column
            selected_lead = leads_data[st.session_state.selected_lead_idx]
            st.markdown("<div style='margin-bottom: 20px;'></div>", unsafe_allow_html=True)
            st.markdown(f"### 🖼️ Recent Uploads for `{selected_lead['channel_name']}`")
            
            v_cols = st.columns(4)
            vids = selected_lead.get("recent_videos", [])
            for v_idx, vid in enumerate(vids[:4]):
                with v_cols[v_idx]:
                    st.markdown(
                        f"""
                        <div style="background-color:#111827; border: 1px solid #1f2937; border-radius:10px; padding:8px; text-align:center;">
                            <img src="{vid['thumbnail_url']}" style="width:100%; border-radius:6px; aspect-ratio:16/9; object-fit:cover;"/>
                            <div style="font-size:0.75rem; font-weight:600; text-overflow:ellipsis; overflow:hidden; white-space:nowrap; width:100%; margin-top:6px; color:#ffffff;">
                                {vid['title']}
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

    with insights_col:
        # RIGHT PANEL: LEAD DETAIL DRAWER
        selected_lead = leads_data[st.session_state.selected_lead_idx]
        
        st.markdown(f"### 📋 Audit Drawer: `{selected_lead['channel_name']}`")
        st.markdown("<div class='saas-card-glow'>", unsafe_allow_html=True)
        
        # Overall Score Gauge
        lead_sc = selected_lead["lead_score"]
        gauge_cls = "gauge-hot" if lead_sc >= 75 else ("gauge-warm" if lead_sc >= 50 else "gauge-low")
        
        st.markdown(
            f"""
            <div style='text-align:center;'>
                <div class="circle-gauge {gauge_cls}" style="width: 80px; height: 80px; font-size: 1.5rem; border-width: 4px;">
                    {lead_sc}
                </div>
                <div style="font-size: 0.75rem; font-weight:600; color:#9ca3af; text-transform:uppercase; margin-top:8px;">Outreach Score</div>
                <span class="{"priority-badge-hot" if lead_sc >= 75 else ("priority-badge-warm" if lead_sc >= 50 else "priority-badge-low")}" style="margin-top:5px; display:inline-block;">
                    {selected_lead['lead_priority']}
                </span>
            </div>
            
            <div style="border-top:1px solid rgba(255,255,255,0.06); padding-top:15px; margin-top:15px;">
                <p style="font-size:0.85rem; margin-bottom:5px;">👥 <b>Subs:</b> {selected_lead['subscribers']:,}</p>
                <p style="font-size:0.85rem; margin-bottom:5px;">✉️ <b>Email:</b> <code>{selected_lead['contacts'].get('email', 'Not Found')}</code></p>
                <p style="font-size:0.85rem; margin-bottom:5px;">📸 <b>Instagram:</b> {f"<a href='{selected_lead['contacts'].get('instagram')}' style='color:#0ea5e9; text-decoration:none;'>Visit Profile</a>" if selected_lead['contacts'].get('instagram') else 'Not Found'}</p>
                <p style="font-size:0.85rem; margin-bottom:5px;">🐦 <b>Twitter/X:</b> {f"<a href='{selected_lead['contacts'].get('twitter_x')}' style='color:#0ea5e9; text-decoration:none;'>Visit Profile</a>" if selected_lead['contacts'].get('twitter_x') else 'Not Found'}</p>
                <p style="font-size:0.85rem; margin-bottom:5px;">🌐 <b>Website:</b> {f"<a href='{selected_lead['contacts'].get('website')}' style='color:#0ea5e9; text-decoration:none;'>Visit</a>" if selected_lead['contacts'].get('website') else 'Not Found'}</p>
            </div>
            """,
            unsafe_allow_html=True
        )
        
        # Display Visual Flaws
        st.markdown("<p style='font-size:0.85rem; font-weight:700; color:#ef4444; margin-top:15px; margin-bottom:5px;'>🚨 Target Thumbnail Defects</p>", unsafe_allow_html=True)
        t_issues = selected_lead.get("thumbnail_issues", [])
        if t_issues:
            for iss in t_issues[:3]:
                st.markdown(f"<div style='font-size:0.8rem; margin-bottom:3px; color:#cbd5e1;'>❌ {iss}</div>", unsafe_allow_html=True)
        else:
            st.markdown("<div style='font-size:0.8rem; color:#10b981;'>✅ No major visual issues detected</div>", unsafe_allow_html=True)
            
        # Display tailored pitch suggestions
        st.markdown("<p style='font-size:0.85rem; font-weight:700; color:#10b981; margin-top:15px; margin-bottom:5px;'>💡 Tailored Pitch Idea</p>", unsafe_allow_html=True)
        suggestions = selected_lead.get("improvement_suggestions", [])
        if suggestions:
            st.markdown(f"<div style='font-size:0.8rem; line-height:1.4; color:#9ca3af;'>{suggestions[0]}</div>", unsafe_allow_html=True)
            
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Review Override Actions
        st.markdown("#### Review Override Decisions")
        act_col1, act_col2 = st.columns(2)
        with act_col1:
            if st.button("Approve 👍", key=f"dr_app_{selected_lead['channel_id']}"):
                st.session_state.leads[st.session_state.selected_lead_idx]["manual_review_status"] = "Approved"
                logger.info(f"Manual Review approved for: {selected_lead['channel_name']}")
                st.rerun()
        with act_col2:
            if st.button("Reject 👎", key=f"dr_rej_{selected_lead['channel_id']}"):
                st.session_state.leads[st.session_state.selected_lead_idx]["manual_review_status"] = "Rejected"
                logger.info(f"Manual Review rejected for: {selected_lead['channel_name']}")
                st.rerun()
                
        # Manual Outreach Notes Form
        st.markdown("#### Manual Outreach Notes")
        notes_key = f"notes_{selected_lead['channel_id']}"
        curr_notes = st.session_state.manual_notes.get(notes_key, "")
        updated_notes = st.text_area("Write comments / pitch details:", value=curr_notes, height=80, key=f"area_{selected_lead['channel_id']}")
        if updated_notes != curr_notes:
            st.session_state.manual_notes[notes_key] = updated_notes
            st.success("Outreach notes saved locally!")

# ----------------- 📊 PREMIUM ANALYTICS PAGE -----------------
elif st.session_state.page == "📊 Premium Analytics":
    with workspace_col:
        st.markdown("## 📊 Premium AI Campaign Analytics")
        
        if not leads_data:
            st.markdown("<div class='empty-state-card'>", unsafe_allow_html=True)
            st.markdown(
                """
                <div class="empty-state-icon">📊</div>
                <h4>No Scan Data Available</h4>
                <p>Run a channel query to construct interactive analytical distributions.</p>
                """,
                unsafe_allow_html=True
            )
            st.markdown("</div>", unsafe_allow_html=True)
        else:
            # Plotly Chart 1: Lead Score Distribution Histogram
            st.markdown("<div class='saas-card'>", unsafe_allow_html=True)
            st.markdown("#### Lead Score Distribution")
            scores = [l["lead_score"] for l in leads_data]
            fig_hist = px.histogram(
                x=scores,
                nbins=10,
                color_discrete_sequence=['#6c63ff'],
                labels={'x': 'Lead Score', 'y': 'Count'}
            )
            fig_hist.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font_color='#ffffff',
                margin=dict(l=20, r=20, t=10, b=20),
                height=250,
                xaxis=dict(gridcolor='#1f2937'),
                yaxis=dict(gridcolor='#1f2937')
            )
            st.plotly_chart(fig_hist, use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)

            # Row for Pie & Bar Charts
            c_col1, c_col2 = st.columns(2)
            
            with c_col1:
                st.markdown("<div class='saas-card'>", unsafe_allow_html=True)
                st.markdown("#### Campaign Niche Breakdown")
                niches = [l.get("niche", "General Gaming") for l in leads_data]
                df_niches = pd.Series(niches).value_counts().reset_index()
                df_niches.columns = ["Niche", "Count"]
                
                fig_pie = px.pie(
                    df_niches,
                    values="Count",
                    names="Niche",
                    color_discrete_sequence=['#6c63ff', '#7c4dff', '#00d4ff', '#0ea5e9', '#10b981']
                )
                fig_pie.update_layout(
                    paper_bgcolor='rgba(0,0,0,0)',
                    font_color='#ffffff',
                    margin=dict(l=10, r=10, t=10, b=10),
                    height=200,
                    showlegend=False
                )
                st.plotly_chart(fig_pie, use_container_width=True)
                st.markdown("</div>", unsafe_allow_html=True)
                
            with c_col2:
                st.markdown("<div class='saas-card'>", unsafe_allow_html=True)
                st.markdown("#### Visual Flaws Matrix")
                
                flaws = []
                for l in leads_data:
                    flaws.extend(l.get("thumbnail_issues", []))
                
                if flaws:
                    df_flaws = pd.Series(flaws).value_counts().reset_index()
                    df_flaws.columns = ["Defect", "Volume"]
                    
                    fig_bar = px.bar(
                        df_flaws.head(5),
                        x="Volume",
                        y="Defect",
                        orientation="h",
                        color_discrete_sequence=['#00d4ff']
                    )
                    fig_bar.update_layout(
                        paper_bgcolor='rgba(0,0,0,0)',
                        plot_bgcolor='rgba(0,0,0,0)',
                        font_color='#ffffff',
                        margin=dict(l=20, r=20, t=10, b=20),
                        height=200,
                        xaxis=dict(gridcolor='#1f2937'),
                        yaxis=dict(gridcolor='#1f2937')
                    )
                    st.plotly_chart(fig_bar, use_container_width=True)
                else:
                    st.write("No flaw entries recorded.")
                st.markdown("</div>", unsafe_allow_html=True)

    with insights_col:
        st.markdown("### 📈 Conversion Funnel")
        st.markdown("<div class='saas-card-glow'>", unsafe_allow_html=True)
        
        # Calculate statistics
        c_tot = len(leads_data)
        c_email = sum(1 for l in leads_data if l["contacts"].get("email"))
        c_ig = sum(1 for l in leads_data if l["contacts"].get("instagram"))
        c_web = sum(1 for l in leads_data if l["contacts"].get("website"))
        
        st.markdown(
            f"""
            <div style="font-size: 0.9rem; line-height: 1.6;">
                <div style="display:flex; justify-content:space-between; margin-bottom:12px; border-bottom:1px solid rgba(255,255,255,0.05); padding-bottom:5px;">
                    <span style="color:#9ca3af;">Total Crawled Leads:</span>
                    <span style="color:#ffffff; font-weight:700;">{c_tot}</span>
                </div>
                <div style="display:flex; justify-content:space-between; margin-bottom:12px; border-bottom:1px solid rgba(255,255,255,0.05); padding-bottom:5px;">
                    <span style="color:#9ca3af;">Direct email outreach:</span>
                    <span style="color:#10b981; font-weight:700;">{c_email} ({int(c_email/c_tot*100) if c_tot else 0}%)</span>
                </div>
                <div style="display:flex; justify-content:space-between; margin-bottom:12px; border-bottom:1px solid rgba(255,255,255,0.05); padding-bottom:5px;">
                    <span style="color:#9ca3af;">Instagram DM potential:</span>
                    <span style="color:#7c4dff; font-weight:700;">{c_ig} ({int(c_ig/c_tot*100) if c_tot else 0}%)</span>
                </div>
                <div style="display:flex; justify-content:space-between; padding-bottom:5px;">
                    <span style="color:#9ca3af;">Agency website scan:</span>
                    <span style="color:#0ea5e9; font-weight:700;">{c_web} ({int(c_web/c_tot*100) if c_tot else 0}%)</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
        st.markdown("</div>", unsafe_allow_html=True)
        
        st.markdown(
            """
            <div class="saas-card" style="margin-top: 15px;">
                <h4>💡 Conversion tip</h4>
                <p style="color:#9ca3af; font-size:0.75rem; line-height:1.4; margin-bottom:0px;">
                    Cold emails targeting channels with low-contrast branding have an average 22% higher response rate when you attach a mock-up redesign of their latest thumbnail!
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )

# ----------------- 📁 EXPORT CENTER PAGE -----------------
elif st.session_state.page == "📁 Export Center":
    with workspace_col:
        st.markdown("## 📁 Exports Dispatcher")
        
        if not leads_data:
            st.markdown("<div class='empty-state-card'>", unsafe_allow_html=True)
            st.markdown(
                """
                <div class="empty-state-icon">📁</div>
                <h4>No Leads to Export</h4>
                <p>Run a search or enable Sandbox mode to export lists.</p>
                """,
                unsafe_allow_html=True
            )
            st.markdown("</div>", unsafe_allow_html=True)
        else:
            # Export controls
            st.markdown("<div class='saas-card'>", unsafe_allow_html=True)
            st.markdown("#### Configure Spreadsheet Output")
            
            ex_col1, ex_col2 = st.columns(2)
            with ex_col1:
                ex_filter = st.selectbox(
                    "Export Filter Rule",
                    ["All Leads", "Only Approved", "Only Hot", "Only with Contact Info", "Only with Email", "Only with Instagram/X"]
                )
                ex_prefix = st.text_input("Spreadsheet Filename Prefix", value="youtube_leads")
            with ex_col2:
                ex_format = st.selectbox("File Format Type", ["XLSX", "CSV"])
                st.markdown("<div style='margin-top: 28px;'></div>", unsafe_allow_html=True)
                
                # Perform export
                if st.button("📤 COMPILE & DISPATCH EXPORT FILE"):
                    success, res_msg, count = export_leads(
                        leads_list=leads_data,
                        export_filter=ex_filter,
                        format_type=ex_format,
                        filename_prefix=ex_prefix
                    )
                    if success:
                        st.success(f"Spreadsheet generated successfully! Compiled {count} matched leads.")
                        
                        # Generate file download link directly in browser
                        try:
                            with open(res_msg, "rb") as f:
                                binary_data = f.read()
                            st.download_button(
                                label=f"⬇️ DOWNLOAD {os.path.basename(res_msg)}",
                                data=binary_data,
                                file_name=os.path.basename(res_msg),
                                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet" if ex_format == "XLSX" else "text/csv"
                            )
                        except Exception as e:
                            logger.error(f"Download button generation failed: {e}")
                    else:
                        st.error(f"Spreadsheet generation failed: {res_msg}")
            
            st.markdown("</div>", unsafe_allow_html=True)

    with insights_col:
        st.markdown("### 📋 Export Logs & Directories")
        st.markdown("<div class='saas-card'>", unsafe_allow_html=True)
        st.write("All compiled spreadsheets are saved locally inside your project folder under:")
        st.code("data/exports/")
        st.write("Ensure you have Microsoft Excel or a CSV viewer installed to open compiled files.")
        st.markdown("</div>", unsafe_allow_html=True)

# ----------------- ⚙️ System Settings PAGE -----------------
elif st.session_state.page == "⚙️ System Settings":
    with workspace_col:
        st.markdown("## ⚙️ System Parameters & Configurations")
        
        # Tabs for grouping settings
        tab_general, tab_scoring, tab_cv, tab_api = st.tabs(["📋 General Rules", "🎛️ Scoring Penalties", "🔍 CV Thresholds", "🔑 API Keys"])
        
        with tab_general:
            st.markdown("#### Default Crawling Thresholds")
            set_sub_min = st.number_input("Minimum Subscriber Count", value=sub_min, step=500)
            set_sub_max = st.number_input("Maximum Subscriber Count", value=sub_max, step=500)
            set_min_vids = st.number_input("Minimum Uploaded Videos", value=min_videos, step=1)
            
        with tab_scoring:
            st.markdown("#### Rule Penalty weights (Deducted from 100)")
            w_blur = st.slider("Blur Penalty value", min_value=-50, max_value=0, value=config.get("scoring_weights", {}).get("blur_penalty", -15))
            w_contrast = st.slider("Low Contrast Penalty value", min_value=-50, max_value=0, value=config.get("scoring_weights", {}).get("contrast_penalty", -10))
            w_color = st.slider("Dull Colors Penalty value", min_value=-50, max_value=0, value=config.get("scoring_weights", {}).get("colorfulness_penalty", -10))
            w_ocr = st.slider("Too much Text Penalty value", min_value=-50, max_value=0, value=config.get("scoring_weights", {}).get("ocr_penalty", -10))
            w_clutter = st.slider("Cluttered Layout Penalty value", min_value=-50, max_value=0, value=config.get("scoring_weights", {}).get("clutter_penalty", -8))
            w_consistency = st.slider("Style Inconsistency Penalty value", min_value=-50, max_value=0, value=config.get("scoring_weights", {}).get("consistency_penalty", -8))
            w_res = st.slider("Low Resolution Penalty value", min_value=-50, max_value=0, value=config.get("scoring_weights", {}).get("resolution_penalty", -5))
            
        with tab_cv:
            st.markdown("#### Computer Vision Thresholds")
            set_blur_t = st.slider("Blur Threshold (Variance of Laplacian)", min_value=10.0, max_value=500.0, value=t_blur)
            set_contrast_t = st.slider("Low Contrast Fraction Limit", min_value=0.01, max_value=0.2, value=t_contrast)
            set_colorful_t = st.slider("Minimum Colorfulness Index", min_value=5.0, max_value=100.0, value=t_colorful)
            set_ocr_t = st.slider("Maximum OCR Text length", min_value=10, max_value=200, value=t_ocr_max)
            set_clutter_t = st.slider("Maximum Clutter Edge Density Ratio", min_value=0.05, max_value=0.5, value=t_clutter)
            set_consistency_t = st.slider("Minimum Branding Consistency Index", min_value=0.1, max_value=1.0, value=t_consistency)
            
        with tab_api:
            st.markdown("#### YouTube Data API Key")
            set_api_key = st.text_input("Enter developer API Key", value=api_key, type="password")
            
        # Update config mapping
        if st.button("💾 SAVE CONFIG CHANGES"):
            new_conf = {
                "api_key": set_api_key,
                "subscribers_min": int(set_sub_min),
                "subscribers_max": int(set_sub_max),
                "min_videos": int(set_min_vids),
                "max_channels_scan": int(max_scan),
                "backend_mode": backend_mode,
                "ocr_enabled": enable_ocr,
                "face_detection_enabled": enable_face,
                "website_scraping_enabled": enable_website,
                "export_format": config.get("export_format", "XLSX"),
                "skip_processed": skip_processed,
                "thresholds": {
                    "blur_variance": set_blur_t,
                    "contrast_low": set_contrast_t,
                    "colorfulness_low": set_colorful_t,
                    "max_ocr_text_length": set_ocr_t,
                    "clutter_ratio": set_clutter_t,
                    "consistency_threshold": set_consistency_t
                },
                "scoring_weights": {
                    "blur_penalty": w_blur,
                    "contrast_penalty": w_contrast,
                    "colorfulness_penalty": w_color,
                    "ocr_penalty": w_ocr,
                    "clutter_penalty": w_clutter,
                    "consistency_penalty": w_consistency,
                    "resolution_penalty": w_res,
                    "email_bonus": config.get("scoring_weights", {}).get("email_bonus", 10),
                    "socials_bonus": config.get("scoring_weights", {}).get("socials_bonus", 5),
                    "website_bonus": config.get("scoring_weights", {}).get("website_bonus", 5),
                    "improvement_bonus": config.get("scoring_weights", {}).get("improvement_bonus", 10)
                }
            }
            save_config(new_conf)
            st.success("System configurations updated and saved to config.json!")
            time.sleep(0.5)
            st.rerun()

    with insights_col:
        st.markdown("### 📋 Configuration Schema")
        st.markdown("<div class='saas-card'>", unsafe_allow_html=True)
        st.write("Visual and scoring rules adjust how leads are flagged and qualified.")
        st.warning("Ensure Tesseract OCR engine is locally installed in system PATH for the OCR Text limits settings to execute.")
        st.markdown("</div>", unsafe_allow_html=True)
