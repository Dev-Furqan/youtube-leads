import os
import pandas as pd
from datetime import datetime
from modules.utils import logger, EXPORTS_DIR

def build_leads_dataframe(leads_list):
    """
    Compile a structured pandas DataFrame from a list of lead dictionaries.
    """
    if not leads_list:
        return pd.DataFrame()
        
    rows = []
    for lead in leads_list:
        # Extract recent video data for list compression
        videos = lead.get("recent_videos", [])
        vid_titles = "; ".join([v.get("title", "") for v in videos])
        vid_urls = "; ".join([v.get("video_url", "") for v in videos])
        thumb_urls = "; ".join([v.get("thumbnail_url", "") for v in videos])
        
        contacts = lead.get("contacts", {})
        
        # Format arrays to strings
        issues = "; ".join(lead.get("thumbnail_issues", []))
        suggestions = " | ".join(lead.get("improvement_suggestions", []))
        other_links = ", ".join(contacts.get("other_links", []))
        
        has_contact = "Yes" if (contacts.get("email") or contacts.get("instagram") or contacts.get("twitter_x") or contacts.get("facebook") or contacts.get("website")) else "No"
        
        row = {
            "Channel Name": lead.get("channel_name", ""),
            "Channel URL": lead.get("channel_url", ""),
            "Channel ID": lead.get("channel_id", ""),
            "Subscribers": lead.get("subscribers", 0),
            "Video Count": lead.get("video_count", 0),
            "Email": contacts.get("email", ""),
            "Instagram": contacts.get("instagram", ""),
            "X/Twitter": contacts.get("twitter_x", ""),
            "Facebook": contacts.get("facebook", ""),
            "Website": contacts.get("website", ""),
            "Other Links": other_links,
            "Recent Video Titles": vid_titles,
            "Recent Video Links": vid_urls,
            "Thumbnail URLs": thumb_urls,
            "Thumbnail Issues": issues,
            "Improvement Suggestions": suggestions,
            "Lead Score": lead.get("lead_score", 0),
            "Lead Priority": lead.get("lead_priority", "Low Lead"),
            "Contact Found": has_contact,
            "Status": lead.get("status", "Processed"),
            "Manual Review Status": lead.get("manual_review_status", "Needs Manual Review"),
            "Created At": lead.get("created_at", datetime.now().isoformat())
        }
        rows.append(row)
        
    return pd.DataFrame(rows)

def filter_dataframe(df, export_filter):
    """
    Apply requested filters to the leads DataFrame.
    Filters: 'All', 'Only Approved', 'Only Hot', 'Only with Contact Info', 'Only with Email', 'Only with Instagram/X'
    """
    if df.empty:
        return df
        
    filtered_df = df.copy()
    
    if export_filter == "Only Approved":
        filtered_df = filtered_df[filtered_df["Manual Review Status"] == "Approved"]
    elif export_filter == "Only Hot":
        filtered_df = filtered_df[filtered_df["Lead Priority"] == "Hot Lead"]
    elif export_filter == "Only with Contact Info":
        filtered_df = filtered_df[filtered_df["Contact Found"] == "Yes"]
    elif export_filter == "Only with Email":
        filtered_df = filtered_df[filtered_df["Email"].astype(str).str.strip() != ""]
    elif export_filter == "Only with Instagram/X":
        filtered_df = filtered_df[
            (filtered_df["Instagram"].astype(str).str.strip() != "") | 
            (filtered_df["X/Twitter"].astype(str).str.strip() != "")
        ]
        
    return filtered_df

def export_leads(leads_list, export_filter="All", format_type="XLSX", filename_prefix="youtube_leads"):
    """
    Export leads list based on requested filter and format (CSV/XLSX).
    Saves file in data/exports/ and returns (success, file_path, row_count).
    """
    if not leads_list:
        return False, "No leads to export.", 0
        
    df = build_leads_dataframe(leads_list)
    filtered_df = filter_dataframe(df, export_filter)
    
    if filtered_df.empty:
        return False, f"No records matched filter '{export_filter}'.", 0
        
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    ext = "xlsx" if format_type.upper() == "XLSX" else "csv"
    filename = f"{filename_prefix}_{export_filter.lower().replace(' ', '_').replace('/', '_')}_{timestamp}.{ext}"
    file_path = os.path.join(EXPORTS_DIR, filename)
    
    try:
        if format_type.upper() == "XLSX":
            # Save as Excel XLSX
            filtered_df.to_excel(file_path, index=False, engine='openpyxl')
        else:
            # Save as CSV
            filtered_df.to_csv(file_path, index=False, encoding='utf-8-sig')
            
        logger.info(f"Leads successfully exported to {file_path} ({len(filtered_df)} items).")
        return True, file_path, len(filtered_df)
    except Exception as e:
        err_msg = f"Export failed due to write error: {e}"
        logger.error(err_msg)
        return False, err_msg, 0
