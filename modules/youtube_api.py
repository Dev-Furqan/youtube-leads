import os
import logging
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from modules.utils import logger, RAW_API_DIR
import json

def get_youtube_client(api_key):
    """Build the YouTube API client."""
    if not api_key:
        raise ValueError("YouTube API Key is missing.")
    return build("youtube", "v3", developerKey=api_key)

def search_channels_api(api_key, keyword, max_results=10, region_code=None, sub_min=1000, sub_max=70000, min_videos=4):
    """
    Search for channels using YouTube Data API.
    Returns a list of structured channel metadata dicts.
    """
    logger.info(f"Starting API channel search for niche: '{keyword}' (max {max_results} channels)...")
    try:
        youtube = get_youtube_client(api_key)
    except Exception as e:
        logger.error(f"Failed to initialize YouTube client: {e}")
        raise e

    channels = []
    
    try:
        # Step 1: Search for channel items
        search_kwargs = {
            "q": keyword,
            "type": "channel",
            "part": "snippet",
            "maxResults": min(max_results * 2, 50)  # Search for extra because we filter
        }
        if region_code:
            search_kwargs["regionCode"] = region_code
            
        search_response = youtube.search().list(**search_kwargs).execute()
        
        # Save raw JSON for debugging/audit
        raw_path = os.path.join(RAW_API_DIR, f"search_{keyword.replace(' ', '_')}.json")
        with open(raw_path, "w", encoding="utf-8") as f:
            json.dump(search_response, f, indent=2)

        items = search_response.get("items", [])
        if not items:
            logger.info("No channels found for the keyword.")
            return []

        channel_ids = [item["snippet"]["channelId"] for item in items if "channelId" in item["snippet"]]
        
        # Step 2: Get detailed channel info in batches of 50
        if not channel_ids:
            return []
            
        # Get details for these channels
        channel_chunks = [channel_ids[i:i + 50] for i in range(0, len(channel_ids), 50)]
        
        for chunk in channel_chunks:
            details_response = youtube.channels().list(
                id=",".join(chunk),
                part="snippet,statistics,contentDetails"
            ).execute()
            
            for ch in details_response.get("items", []):
                stats = ch.get("statistics", {})
                snippet = ch.get("snippet", {})
                content_details = ch.get("contentDetails", {})
                
                sub_count = int(stats.get("subscriberCount", 0))
                video_count = int(stats.get("videoCount", 0))
                channel_id = ch["id"]
                channel_name = snippet.get("title", "")
                
                logger.info(f"Evaluating channel '{channel_name}' (ID: {channel_id}): Subs={sub_count}, Videos={video_count}")
                
                # Apply filters
                if sub_count < sub_min or sub_count > sub_max:
                    logger.info(f"Skipping '{channel_name}': Subscribers ({sub_count}) outside range [{sub_min}, {sub_max}]")
                    continue
                if video_count < min_videos:
                    logger.info(f"Skipping '{channel_name}': Video count ({video_count}) below minimum ({min_videos})")
                    continue
                
                uploads_playlist_id = content_details.get("relatedPlaylists", {}).get("uploads")
                
                custom_url = snippet.get("customUrl", "")
                channel_url = f"https://youtube.com/{custom_url}" if custom_url else f"https://youtube.com/channel/{channel_id}"

                channels.append({
                    "channel_id": channel_id,
                    "channel_name": channel_name,
                    "channel_url": channel_url,
                    "subscribers": sub_count,
                    "video_count": video_count,
                    "description": snippet.get("description", ""),
                    "uploads_playlist_id": uploads_playlist_id
                })
                
                if len(channels) >= max_results:
                    break
            
            if len(channels) >= max_results:
                break
                
        logger.info(f"API search complete. Found {len(channels)} valid channels after filters.")
        return channels

    except HttpError as e:
        err_msg = str(e)
        if "quotaExceeded" in err_msg:
            logger.error("YouTube Data API Quota Exceeded!")
        else:
            logger.error(f"YouTube Data API error: {e}")
        raise e
    except Exception as e:
        logger.error(f"Unexpected error in search_channels_api: {e}")
        raise e

def fetch_recent_videos_api(api_key, uploads_playlist_id, limit=4):
    """
    Fetch the latest 'limit' videos from a playlist.
    """
    if not uploads_playlist_id:
        return []
        
    try:
        youtube = get_youtube_client(api_key)
        response = youtube.playlistItems().list(
            playlistId=uploads_playlist_id,
            part="snippet",
            maxResults=limit
        ).execute()
        
        videos = []
        for item in response.get("items", []):
            snippet = item.get("snippet", {})
            resource = snippet.get("resourceId", {})
            video_id = resource.get("videoId")
            
            if not video_id:
                continue
                
            # Thumbnail selection (prefer high quality)
            thumbs = snippet.get("thumbnails", {})
            thumb_url = ""
            for res in ["maxres", "standard", "high", "medium", "default"]:
                if res in thumbs:
                    thumb_url = thumbs[res]["url"]
                    break
            
            videos.append({
                "video_id": video_id,
                "title": snippet.get("title", ""),
                "video_url": f"https://youtube.com/watch?v={video_id}",
                "thumbnail_url": thumb_url,
                "description": snippet.get("description", ""),
                "published_at": snippet.get("publishedAt", "")
            })
            
        return videos
    except Exception as e:
        logger.error(f"Error fetching recent videos for playlist {uploads_playlist_id}: {e}")
        return []
