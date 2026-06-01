import streamlit as st
import os
import json
from datetime import datetime

def inject_premium_styles():
    """
    Inject custom CSS to create a premium dark SaaS dashboard experience.
    """
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700&family=Space+Grotesk:wght@400;600;700&display=swap');
        
        /* Main page adjustments */
        html, body, [data-testid="stAppViewContainer"] {
            background-color: #0d0f14;
            color: #e2e8f0;
            font-family: 'Outfit', -apple-system, BlinkMacSystemFont, sans-serif;
        }
        
        [data-testid="stSidebar"] {
            background-color: #151922 !important;
            border-right: 1px solid #2d3748;
        }
        
        /* Headings styling */
        h1, h2, h3, h4, h5, h6 {
            font-family: 'Space Grotesk', sans-serif;
            color: #ffffff;
            font-weight: 600;
        }
        
        /* Main title gradient */
        .main-title {
            background: linear-gradient(135deg, #3b82f6 0%, #a855f7 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-size: 2.8rem;
            font-weight: 700;
            margin-bottom: 0.1rem;
            text-align: left;
            letter-spacing: -0.05em;
        }
        
        .main-subtitle {
            color: #94a3b8;
            font-size: 1.1rem;
            margin-bottom: 2rem;
        }
        
        /* Metric cards */
        .metric-card {
            background: rgba(30, 41, 59, 0.45);
            backdrop-filter: blur(10px);
            -webkit-backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.06);
            border-radius: 12px;
            padding: 18px;
            text-align: center;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
            transition: transform 0.2s ease, border-color 0.2s ease;
        }
        
        .metric-card:hover {
            transform: translateY(-2px);
            border-color: rgba(59, 130, 246, 0.4);
        }
        
        .metric-value {
            font-size: 1.8rem;
            font-weight: 700;
            color: #ffffff;
            margin: 5px 0;
            font-family: 'Space Grotesk', sans-serif;
        }
        
        .metric-label {
            font-size: 0.85rem;
            color: #94a3b8;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }
        
        /* Glowing Accent tags */
        .tag-hot {
            background: linear-gradient(135deg, rgba(239, 68, 68, 0.2) 0%, rgba(249, 115, 22, 0.2) 100%);
            color: #f87171;
            border: 1px solid rgba(239, 68, 68, 0.4);
            border-radius: 6px;
            padding: 3px 8px;
            font-size: 0.8rem;
            font-weight: 600;
            display: inline-block;
        }
        
        .tag-warm {
            background: linear-gradient(135deg, rgba(245, 158, 11, 0.2) 0%, rgba(234, 179, 8, 0.2) 100%);
            color: #fbbf24;
            border: 1px solid rgba(245, 158, 11, 0.4);
            border-radius: 6px;
            padding: 3px 8px;
            font-size: 0.8rem;
            font-weight: 600;
            display: inline-block;
        }
        
        .tag-low {
            background: rgba(148, 163, 184, 0.15);
            color: #cbd5e1;
            border: 1px solid rgba(148, 163, 184, 0.3);
            border-radius: 6px;
            padding: 3px 8px;
            font-size: 0.8rem;
            font-weight: 600;
            display: inline-block;
        }
        
        /* Glass card container for elements */
        .glass-card {
            background: rgba(21, 25, 34, 0.6);
            backdrop-filter: blur(12px);
            -webkit-backdrop-filter: blur(12px);
            border: 1px solid rgba(255, 255, 255, 0.04);
            border-radius: 16px;
            padding: 24px;
            margin-bottom: 20px;
            box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.2);
        }
        
        /* Streamlit UI overrides */
        .stButton>button {
            background: linear-gradient(135deg, #2563eb 0%, #7c3aed 100%) !important;
            color: white !important;
            border: none !important;
            border-radius: 8px !important;
            font-weight: 600 !important;
            padding: 10px 24px !important;
            box-shadow: 0 4px 14px rgba(99, 102, 241, 0.3) !important;
            transition: all 0.2s ease !important;
        }
        
        .stButton>button:hover {
            transform: translateY(-1px) !important;
            box-shadow: 0 6px 20px rgba(99, 102, 241, 0.5) !important;
            border: none !important;
        }
        
        /* Log panel styling */
        .log-panel {
            background-color: #07090e;
            border: 1px solid #1f2937;
            border-radius: 8px;
            padding: 12px;
            font-family: 'Courier New', Courier, monospace;
            font-size: 0.85rem;
            color: #38bdf8;
            max-height: 250px;
            overflow-y: auto;
            white-space: pre-wrap;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

def inject_metric_card(label, value, extra_cls=""):
    """
    Inject a customized visual metric card.
    """
    st.markdown(
        f"""
        <div class="metric-card {extra_cls}">
            <div class="metric-label">{label}</div>
            <div class="metric-value">{value}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

def get_mock_leads():
    """
    Returns a set of 6 highly realistic mock YouTube channels with various visual thumbnail issues
    and public contact details for demonstration, sandbox, and UI verification.
    """
    return [
        {
            "channel_id": "UC_mock_gaming_guru",
            "channel_name": "Pixel Arena Gaming",
            "channel_url": "https://youtube.com/@pixelarenagaming",
            "subscribers": 45200,
            "video_count": 86,
            "description": "Daily game reviews, retro consoles, and esports guides. Contact us at pixelarenabusiness@gmail.com for partnerships or reach out on Twitter @PixelArena!",
            "uploads_playlist_id": "PL_mock_gaming_playlist",
            "recent_videos": [
                {
                    "video_id": "mock_game_v1",
                    "title": "Is This Retro Console Worth It in 2026?",
                    "video_url": "https://www.youtube.com/watch?v=mock_game_v1",
                    "thumbnail_url": "https://images.unsplash.com/photo-1538481199705-c710c4e965fc?w=600&auto=format&fit=crop&q=80",
                    "description": "Today we test the latest retro emulator console! Business email: pixelarenabusiness@gmail.com",
                    "published_at": "2026-05-30T12:00:00Z"
                },
                {
                    "video_id": "mock_game_v2",
                    "title": "Top 10 RPGs You Missed This Year!",
                    "video_url": "https://www.youtube.com/watch?v=mock_game_v2",
                    "thumbnail_url": "https://images.unsplash.com/photo-1607604276583-eef5d076aa5f?w=600&auto=format&fit=crop&q=80",
                    "description": "RPGs that deserve your attention. Twitter: @PixelArena",
                    "published_at": "2026-05-25T14:30:00Z"
                },
                {
                    "video_id": "mock_game_v3",
                    "title": "Elden Ring: The Ultimate Lore Breakdown",
                    "video_url": "https://www.youtube.com/watch?v=mock_game_v3",
                    "thumbnail_url": "https://images.unsplash.com/photo-1511512578047-dfb367046420?w=600&auto=format&fit=crop&q=80",
                    "description": "Analyzing every detail. Retro consoles gaming gear reviews.",
                    "published_at": "2026-05-18T10:00:00Z"
                },
                {
                    "video_id": "mock_game_v4",
                    "title": "My New Streaming Setup (Budget Edition)",
                    "video_url": "https://www.youtube.com/watch?v=mock_game_v4",
                    "thumbnail_url": "https://images.unsplash.com/photo-1542751371-adc38448a05e?w=600&auto=format&fit=crop&q=80",
                    "description": "Upgrading the battlestation. Sub for more retro emulation content.",
                    "published_at": "2026-05-10T16:15:00Z"
                }
            ],
            "contacts": {
                "email": "pixelarenabusiness@gmail.com",
                "instagram": "https://instagram.com/pixelarena",
                "twitter_x": "https://x.com/PixelArena",
                "facebook": "",
                "linktree": "https://linktr.ee/pixelarena",
                "website": "https://pixelarenagaming.com",
                "other_links": ["https://pixelarenagaming.com"]
            },
            "cv_analysis": [
                {
                    "blur_score": 45.3,  # Blurry
                    "contrast_score": 8.4,  # Low Contrast
                    "colorfulness_score": 15.6,  # Dull
                    "brightness_score": 38.0, # Too dark
                    "width": 1280,
                    "height": 720,
                    "ocr_text": "RETRO CONSOLE Emulators Retro Gaming Setup Worth It?",
                    "ocr_char_count": 52, # Too much text
                    "face_detected": False,
                    "clutter_score": 0.22, # Cluttered
                    "issues": ["blurry", "low_contrast", "dull_colors", "low_brightness", "too_much_text", "no_clear_face", "cluttered"]
                },
                {
                    "blur_score": 62.0,
                    "contrast_score": 12.1,
                    "colorfulness_score": 18.2,
                    "brightness_score": 52.0,
                    "width": 1280,
                    "height": 720,
                    "ocr_text": "TOP 10 RPGs You MUST PLAY, Missed Gems",
                    "ocr_char_count": 40,
                    "face_detected": False,
                    "clutter_score": 0.18,
                    "issues": ["blurry", "low_contrast", "dull_colors", "no_clear_face", "cluttered"]
                },
                {
                    "blur_score": 80.5,
                    "contrast_score": 14.3,
                    "colorfulness_score": 24.1,
                    "brightness_score": 42.0,
                    "width": 1280,
                    "height": 720,
                    "ocr_text": "ELDEN RING LORE BREAKDOWN The Lands Between Details Explained",
                    "ocr_char_count": 62,
                    "face_detected": False,
                    "clutter_score": 0.25,
                    "issues": ["blurry", "low_contrast", "too_much_text", "no_clear_face", "cluttered", "low_brightness"]
                },
                {
                    "blur_score": 55.1,
                    "contrast_score": 9.2,
                    "colorfulness_score": 16.8,
                    "brightness_score": 35.0,
                    "width": 1280,
                    "height": 720,
                    "ocr_text": "MY NEW GAMING STREAMING SETUP Budget Setup Emulation console",
                    "ocr_char_count": 58,
                    "face_detected": False,
                    "clutter_score": 0.21,
                    "issues": ["blurry", "low_contrast", "dull_colors", "low_brightness", "too_much_text", "no_clear_face", "cluttered"]
                }
            ],
            "brand_consistency": False,
            "lead_score": 38,
            "lead_priority": "Low Lead",
            "thumbnail_issues": ["Blurry thumbnails", "Low contrast layouts", "Dull colors / flat tones", "Thumbnails too dark", "Excessive thumbnail text", "Inconsistent branding/style", "Cluttered layouts"],
            "improvement_suggestions": [
                "Increase thumbnail image contrast using drop shadows or outlines on text panels.",
                "Boost color saturation and brightness: dark emulators make the feed look lifeless.",
                "Establish visual branding: retro-gaming channels require a recurring color theme (e.g. neon yellow and blue border).",
                "Reduce text density to 2-3 high-impact words rather than writing full sentences.",
                "Include a clean character focal point or face displaying curiosity."
            ],
            "status": "Processed",
            "manual_review_status": "Needs Manual Review",
            "created_at": datetime.now().isoformat()
        },
        {
            "channel_id": "UC_mock_cooking_secrets",
            "channel_name": "Mama Mia Cooking",
            "channel_url": "https://youtube.com/@mamamiacooking",
            "subscribers": 15800,
            "video_count": 34,
            "description": "Authentic Italian family recipes made easy. Email me at mamacooksitalian@yahoo.com or send a DM on Instagram @MamaMiaCooks!",
            "uploads_playlist_id": "PL_mock_cooking_playlist",
            "recent_videos": [
                {
                    "video_id": "mock_cook_v1",
                    "title": "The Secrets to the Perfect Neapolitan Pizza Crust",
                    "video_url": "https://www.youtube.com/watch?v=mock_cook_v1",
                    "thumbnail_url": "https://images.unsplash.com/photo-1513104890138-7c749659a591?w=600&auto=format&fit=crop&q=80",
                    "description": "Making real Neapolitan pizza dough. Follow me on Instagram: @MamaMiaCooks",
                    "published_at": "2026-05-28T09:00:00Z"
                },
                {
                    "video_id": "mock_cook_v2",
                    "title": "Grandma's Creamy Lasagna Recipe",
                    "video_url": "https://www.youtube.com/watch?v=mock_cook_v2",
                    "thumbnail_url": "https://images.unsplash.com/photo-1574894709920-11b28e7367e3?w=600&auto=format&fit=crop&q=80",
                    "description": "The best classic beef lasagna. Email: mamacooksitalian@yahoo.com",
                    "published_at": "2026-05-22T11:00:00Z"
                },
                {
                    "video_id": "mock_cook_v3",
                    "title": "Fast & Fresh 10-Minute Pasta Dinner",
                    "video_url": "https://www.youtube.com/watch?v=mock_cook_v3",
                    "thumbnail_url": "https://images.unsplash.com/photo-1563379091339-03b21ab4a4f8?w=600&auto=format&fit=crop&q=80",
                    "description": "A quick dinner recipe. Instagram: @MamaMiaCooks",
                    "published_at": "2026-05-15T10:00:00Z"
                },
                {
                    "video_id": "mock_cook_v4",
                    "title": "How to Cure Pancetta at Home",
                    "video_url": "https://www.youtube.com/watch?v=mock_cook_v4",
                    "thumbnail_url": "https://images.unsplash.com/photo-1608686207856-001b95cf60ca?w=600&auto=format&fit=crop&q=80",
                    "description": "Home curing pancetta guide. Reach out via email.",
                    "published_at": "2026-05-08T08:30:00Z"
                }
            ],
            "contacts": {
                "email": "mamacooksitalian@yahoo.com",
                "instagram": "https://instagram.com/mamamiacooks",
                "twitter_x": "",
                "facebook": "",
                "linktree": "",
                "website": "",
                "other_links": []
            },
            "cv_analysis": [
                {
                    "blur_score": 180.2, # Sharp
                    "contrast_score": 42.1, # Good Contrast
                    "colorfulness_score": 28.5, # Good colorfulness
                    "brightness_score": 115.0, # Good brightness
                    "width": 1280,
                    "height": 720,
                    "ocr_text": "PIZZA",
                    "ocr_char_count": 5, # Great text limit
                    "face_detected": False, # Missing Face/Human connection
                    "clutter_score": 0.08, # Minimalist
                    "issues": ["no_clear_face"]
                },
                {
                    "blur_score": 195.4,
                    "contrast_score": 38.6,
                    "colorfulness_score": 32.1,
                    "brightness_score": 125.0,
                    "width": 1280,
                    "height": 720,
                    "ocr_text": "LASAGNA",
                    "ocr_char_count": 7,
                    "face_detected": False,
                    "clutter_score": 0.09,
                    "issues": ["no_clear_face"]
                },
                {
                    "blur_score": 210.0,
                    "contrast_score": 40.5,
                    "colorfulness_score": 35.2,
                    "brightness_score": 130.0,
                    "width": 1280,
                    "height": 720,
                    "ocr_text": "PASTA",
                    "ocr_char_count": 5,
                    "face_detected": False,
                    "clutter_score": 0.07,
                    "issues": ["no_clear_face"]
                },
                {
                    "blur_score": 172.5,
                    "contrast_score": 36.4,
                    "colorfulness_score": 25.1,
                    "brightness_score": 105.0,
                    "width": 1280,
                    "height": 720,
                    "ocr_text": "PANCETTA",
                    "ocr_char_count": 8,
                    "face_detected": False,
                    "clutter_score": 0.10,
                    "issues": ["no_clear_face"]
                }
            ],
            "brand_consistency": True,
            "lead_score": 85,
            "lead_priority": "Hot Lead",
            "thumbnail_issues": ["No clear face or character focus"],
            "improvement_suggestions": [
                "Thumbnails look beautiful and sharp, but are missing a human element.",
                "Try incorporating a high-resolution close-up of a face expressing excitement, taste-testing, or showing the final bite.",
                "This emotional hook can dramatically increase the Click-Through Rate (CTR) for cooking videos.",
                "Ensure your brand colors (like Italian flag details) are consistently placed in corners."
            ],
            "status": "Processed",
            "manual_review_status": "Needs Manual Review",
            "created_at": datetime.now().isoformat()
        },
        {
            "channel_id": "UC_mock_tech_unboxed",
            "channel_name": "Gizmo Unboxing",
            "channel_url": "https://youtube.com/@gizmounboxing",
            "subscribers": 68000,
            "video_count": 142,
            "description": "Unboxing the newest tech, smartphones, and weird gadgets. Business inquiries: collabs@gizmounbox.co. Website: gizmounbox.co",
            "uploads_playlist_id": "PL_mock_tech_playlist",
            "recent_videos": [
                {
                    "video_id": "mock_tech_v1",
                    "title": "This $10 Phone is Surprisingly Good!",
                    "video_url": "https://www.youtube.com/watch?v=mock_tech_v1",
                    "thumbnail_url": "https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?w=600&auto=format&fit=crop&q=80",
                    "description": "Reviewing the cheapest phone. Website: https://gizmounbox.co",
                    "published_at": "2026-05-29T15:00:00Z"
                },
                {
                    "video_id": "mock_tech_v2",
                    "title": "Is the New Smartwatch a Scam? (Honest Review)",
                    "video_url": "https://www.youtube.com/watch?v=mock_tech_v2",
                    "thumbnail_url": "https://images.unsplash.com/photo-1508685096489-7aacd43bd3b1?w=600&auto=format&fit=crop&q=80",
                    "description": "Testing the battery life. Email: collabs@gizmounbox.co",
                    "published_at": "2026-05-24T16:00:00Z"
                },
                {
                    "video_id": "mock_tech_v3",
                    "title": "I Bought a Refurbished Laptop from a Sketchy Website",
                    "video_url": "https://www.youtube.com/watch?v=mock_tech_v3",
                    "thumbnail_url": "https://images.unsplash.com/photo-1588872657578-7efd1f1555ed?w=600&auto=format&fit=crop&q=80",
                    "description": "Unboxing laptop. Collabs: collabs@gizmounbox.co",
                    "published_at": "2026-05-16T12:00:00Z"
                },
                {
                    "video_id": "mock_tech_v4",
                    "title": "My Favorite Tech Accessories Under $25",
                    "video_url": "https://www.youtube.com/watch?v=mock_tech_v4",
                    "thumbnail_url": "https://images.unsplash.com/photo-1468495244123-6c6c332eeece?w=600&auto=format&fit=crop&q=80",
                    "description": "Cool gadgets under $25.",
                    "published_at": "2026-05-09T14:00:00Z"
                }
            ],
            "contacts": {
                "email": "collabs@gizmounbox.co",
                "instagram": "",
                "twitter_x": "https://x.com/gizmounbox",
                "facebook": "",
                "linktree": "",
                "website": "https://gizmounbox.co",
                "other_links": ["https://gizmounbox.co"]
            },
            "cv_analysis": [
                {
                    "blur_score": 160.5,
                    "contrast_score": 28.1,
                    "colorfulness_score": 11.2, # Dull colors
                    "brightness_score": 85.0,
                    "width": 1280,
                    "height": 720,
                    "ocr_text": "CHEAP PHONE $10 SMART PHONE UNBOXING AND REVIEW WORTH IT?",
                    "ocr_char_count": 55, # Too much text
                    "face_detected": False,
                    "clutter_score": 0.19, # Cluttered
                    "issues": ["dull_colors", "too_much_text", "no_clear_face", "cluttered"]
                },
                {
                    "blur_score": 140.2,
                    "contrast_score": 26.5,
                    "colorfulness_score": 14.5, # Dull
                    "brightness_score": 90.0,
                    "width": 1280,
                    "height": 720,
                    "ocr_text": "SMART WATCH SCAM OR REAL HONEST REVIEW BATTERY TEST",
                    "ocr_char_count": 52, # Too much text
                    "face_detected": False,
                    "clutter_score": 0.18, # Cluttered
                    "issues": ["dull_colors", "too_much_text", "no_clear_face", "cluttered"]
                },
                {
                    "blur_score": 182.1,
                    "contrast_score": 30.2,
                    "colorfulness_score": 9.8, # Dull
                    "brightness_score": 80.0,
                    "width": 1280,
                    "height": 720,
                    "ocr_text": "LAPTOP UNBOXING CHEAP SKETCHY REFURBISHED LAPTOP SCAM",
                    "ocr_char_count": 54, # Too much text
                    "face_detected": False,
                    "clutter_score": 0.20,
                    "issues": ["dull_colors", "too_much_text", "no_clear_face", "cluttered"]
                },
                {
                    "blur_score": 150.8,
                    "contrast_score": 24.3,
                    "colorfulness_score": 13.0, # Dull
                    "brightness_score": 75.0,
                    "width": 1280,
                    "height": 720,
                    "ocr_text": "BEST ACCESSORIES UNDER $25 COOL TECH YOU NEED TO BUY",
                    "ocr_char_count": 52, # Too much text
                    "face_detected": False,
                    "clutter_score": 0.17,
                    "issues": ["dull_colors", "too_much_text", "no_clear_face", "cluttered"]
                }
            ],
            "brand_consistency": True,
            "lead_score": 58,
            "lead_priority": "Warm Lead",
            "thumbnail_issues": ["Dull colors / flat tones", "Excessive thumbnail text", "No clear face or character focus", "Cluttered layouts"],
            "improvement_suggestions": [
                "Contrast tech gadgets clearly with high saturation background glows (e.g. orange vs neon purple).",
                "Reduce OCR text clutter: replace long sentences like 'UNBOXING AND REVIEW WORTH IT' with 'SCAM?' or '$10 PHONE!' in massive letters.",
                "Incorporate a close-up of a human face reacting to the sketchy packaging or device to hook tech viewers.",
                "Ensure clean margins around main subjects."
            ],
            "status": "Processed",
            "manual_review_status": "Needs Manual Review",
            "created_at": datetime.now().isoformat()
        },
        {
            "channel_id": "UC_mock_makeup_beauty",
            "channel_name": "Glow with Grace",
            "channel_url": "https://youtube.com/@glowwithgrace",
            "subscribers": 3200,
            "video_count": 18,
            "description": "Makeup tutorials, skincare science, and glow-ups. Let's collaborate: contact@glowwithgrace.com",
            "uploads_playlist_id": "PL_mock_beauty_playlist",
            "recent_videos": [
                {
                    "video_id": "mock_beauty_v1",
                    "title": "My 5-Step Flawless Skincare Routine",
                    "video_url": "https://www.youtube.com/watch?v=mock_beauty_v1",
                    "thumbnail_url": "https://images.unsplash.com/photo-1598440947619-2c35fc9aa908?w=600&auto=format&fit=crop&q=80",
                    "description": "Sharing my daily glow-up tips. Email: contact@glowwithgrace.com",
                    "published_at": "2026-05-30T10:00:00Z"
                },
                {
                    "video_id": "mock_beauty_v2",
                    "title": "Testing Viral TikTok Skincare Products",
                    "video_url": "https://www.youtube.com/watch?v=mock_beauty_v2",
                    "thumbnail_url": "https://images.unsplash.com/photo-1522335789203-aabd1fc54bc9?w=600&auto=format&fit=crop&q=80",
                    "description": "Do these actually work? Reach out via contact@glowwithgrace.com",
                    "published_at": "2026-05-23T11:00:00Z"
                },
                {
                    "video_id": "mock_beauty_v3",
                    "title": "Drugstore vs High-End Makeup (Half Face Challenge)",
                    "video_url": "https://www.youtube.com/watch?v=mock_beauty_v3",
                    "thumbnail_url": "https://images.unsplash.com/photo-1512496015851-a90fb38ba796?w=600&auto=format&fit=crop&q=80",
                    "description": "Splurge vs save comparison.",
                    "published_at": "2026-05-15T09:00:00Z"
                },
                {
                    "video_id": "mock_beauty_v4",
                    "title": "How to Do Eyeliner for Beginners",
                    "video_url": "https://www.youtube.com/watch?v=mock_beauty_v4",
                    "thumbnail_url": "https://images.unsplash.com/photo-1487412720507-e7ab37603c6f?w=600&auto=format&fit=crop&q=80",
                    "description": "Step-by-step winged liner guide.",
                    "published_at": "2026-05-05T13:00:00Z"
                }
            ],
            "contacts": {
                "email": "contact@glowwithgrace.com",
                "instagram": "https://instagram.com/glowwithgrace",
                "twitter_x": "",
                "facebook": "",
                "linktree": "",
                "website": "",
                "other_links": []
            },
            "cv_analysis": [
                {
                    "blur_score": 38.2, # Blurry
                    "contrast_score": 45.1,
                    "colorfulness_score": 32.4,
                    "brightness_score": 160.0,
                    "width": 1280,
                    "height": 720,
                    "ocr_text": "SKINCARE",
                    "ocr_char_count": 8,
                    "face_detected": True, # Face is present!
                    "clutter_score": 0.05,
                    "issues": ["blurry"]
                },
                {
                    "blur_score": 40.5, # Blurry
                    "contrast_score": 42.0,
                    "colorfulness_score": 28.5,
                    "brightness_score": 155.0,
                    "width": 1280,
                    "height": 720,
                    "ocr_text": "VIRAL TIKTOK",
                    "ocr_char_count": 12,
                    "face_detected": True,
                    "clutter_score": 0.06,
                    "issues": ["blurry"]
                },
                {
                    "blur_score": 29.8, # Blurry
                    "contrast_score": 38.6,
                    "colorfulness_score": 30.1,
                    "brightness_score": 165.0,
                    "width": 1280,
                    "height": 720,
                    "ocr_text": "SPLURGE VS SAVE",
                    "ocr_char_count": 15,
                    "face_detected": True,
                    "clutter_score": 0.06,
                    "issues": ["blurry"]
                },
                {
                    "blur_score": 42.1, # Blurry
                    "contrast_score": 41.2,
                    "colorfulness_score": 31.0,
                    "brightness_score": 150.0,
                    "width": 1280,
                    "height": 720,
                    "ocr_text": "WINGED EYELINER",
                    "ocr_char_count": 15,
                    "face_detected": True,
                    "clutter_score": 0.05,
                    "issues": ["blurry"]
                }
            ],
            "brand_consistency": True,
            "lead_score": 79,
            "lead_priority": "Hot Lead",
            "thumbnail_issues": ["Blurry thumbnails"],
            "improvement_suggestions": [
                "Your compositions and faces are beautiful, but the exported images are blurry and lack crisp focal points.",
                "Export thumbnails as high-quality PNGs directly in 1280x720 to prevent compression artifacts.",
                "Apply a slight high-pass sharpening filter in Photoshop/Canva on close-ups of eyelashes and skincare textures to make details pop."
            ],
            "status": "Processed",
            "manual_review_status": "Needs Manual Review",
            "created_at": datetime.now().isoformat()
        }
    ]
