import streamlit as st
import os
from datetime import datetime

def inject_premium_styles():
    """
    Inject custom CSS to hide standard Streamlit appearance and apply a Luxury Dark SaaS Theme.
    Includes custom cards, animations, navigation triggers, and layout alignments.
    """
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap');
        
        /* Hide Default Streamlit Brand Elements */
        #MainMenu {visibility: hidden;}
        header {visibility: hidden;}
        footer {visibility: hidden;}
        
        /* Core Viewport Styles */
        html, body, [data-testid="stAppViewContainer"] {
            background-color: #0b0f19 !important;
            color: #d1d5db !important;
            font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif !important;
        }
        
        /* Remove default container margins */
        [data-testid="stAppViewBlockContainer"] {
            padding-top: 1.25rem !important;
            padding-bottom: 2rem !important;
            padding-left: 2rem !important;
            padding-right: 2rem !important;
            max-width: 100% !important;
        }
        
        /* Custom Sidebar Skinning */
        [data-testid="stSidebar"] {
            background-color: #0d1220 !important;
            border-right: 1px solid #1f2937 !important;
        }
        
        [data-testid="stSidebar"] [data-testid="stForm"] {
            border: 1px solid #1f2937 !important;
            background-color: #111827 !important;
        }
        
        /* Typography */
        h1, h2, h3, h4, h5, h6 {
            font-family: 'Plus Jakarta Sans', sans-serif !important;
            font-weight: 700 !important;
            color: #ffffff !important;
            letter-spacing: -0.02em !important;
        }
        
        /* Premium Card Containers */
        .saas-card {
            background-color: #111827;
            border: 1px solid #1f2937;
            border-radius: 14px;
            padding: 22px;
            margin-bottom: 18px;
            box-shadow: 0 4px 20px 0 rgba(0, 0, 0, 0.25);
            transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
        }
        
        .saas-card:hover {
            transform: translateY(-2px);
            border-color: rgba(108, 99, 255, 0.4);
            box-shadow: 0 10px 25px 0 rgba(108, 99, 255, 0.08);
        }
        
        /* Card Gradients */
        .saas-card-glow {
            background: linear-gradient(135deg, #111827 0%, #15102a 100%);
            border: 1px solid rgba(124, 77, 255, 0.2);
            border-radius: 14px;
            padding: 22px;
            margin-bottom: 18px;
            box-shadow: 0 4px 20px 0 rgba(124, 77, 255, 0.05);
        }
        
        /* SaaS Header Branding */
        .brand-logo-container {
            display: flex;
            align-items: center;
            padding: 10px 0;
            margin-bottom: 25px;
            border-bottom: 1px solid #1f2937;
        }
        
        .brand-logo-icon {
            background: linear-gradient(135deg, #6c63ff 0%, #00d4ff 100%);
            color: #ffffff;
            width: 38px;
            height: 38px;
            border-radius: 10px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.25rem;
            font-weight: 800;
            margin-right: 12px;
            box-shadow: 0 0 15px rgba(108, 99, 255, 0.4);
        }
        
        .brand-logo-text {
            font-size: 1.15rem;
            font-weight: 800;
            color: #ffffff;
            letter-spacing: -0.03em;
            background: linear-gradient(135deg, #ffffff 60%, #cbd5e1 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        
        /* SaaS Sidebar Menu Items */
        .nav-item-active {
            background: rgba(108, 99, 255, 0.12) !important;
            border: 1px solid rgba(108, 99, 255, 0.3) !important;
            border-radius: 8px;
            padding: 8px 12px;
            color: #ffffff !important;
            font-weight: 600;
            display: flex;
            align-items: center;
            margin-bottom: 8px;
            transition: all 0.2s ease;
        }
        
        .nav-item-inactive {
            background: transparent;
            border: 1px solid transparent;
            border-radius: 8px;
            padding: 8px 12px;
            color: #9ca3af !important;
            font-weight: 500;
            display: flex;
            align-items: center;
            margin-bottom: 8px;
            cursor: pointer;
            transition: all 0.2s ease;
        }
        
        .nav-item-inactive:hover {
            background: rgba(255, 255, 255, 0.03);
            color: #ffffff !important;
            border-color: rgba(255, 255, 255, 0.05);
        }
        
        /* Top Global Header Components */
        .global-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            background-color: #111827;
            border: 1px solid #1f2937;
            border-radius: 12px;
            padding: 12px 24px;
            margin-bottom: 24px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        }
        
        .header-project {
            display: flex;
            align-items: center;
            font-size: 0.9rem;
            font-weight: 500;
            color: #9ca3af;
        }
        
        .project-tag {
            background-color: rgba(14, 165, 233, 0.15);
            color: #0ea5e9;
            border: 1px solid rgba(14, 165, 233, 0.3);
            border-radius: 6px;
            padding: 2px 8px;
            font-size: 0.75rem;
            font-weight: 600;
            margin-left: 8px;
        }
        
        .header-meta {
            display: flex;
            align-items: center;
            gap: 15px;
        }
        
        .api-tag-active {
            background-color: rgba(16, 185, 129, 0.1);
            color: #10b981;
            border: 1px solid rgba(16, 185, 129, 0.3);
            border-radius: 20px;
            padding: 2px 10px;
            font-size: 0.75rem;
            font-weight: 600;
        }
        
        .api-tag-inactive {
            background-color: rgba(245, 158, 11, 0.1);
            color: #f59e0b;
            border: 1px solid rgba(245, 158, 11, 0.3);
            border-radius: 20px;
            padding: 2px 10px;
            font-size: 0.75rem;
            font-weight: 600;
        }
        
        .avatar-circle {
            width: 32px;
            height: 32px;
            border-radius: 50%;
            background: linear-gradient(135deg, #7c4dff 0%, #00d4ff 100%);
            color: white;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 0.85rem;
            font-weight: 700;
            border: 2px solid #1f2937;
        }
        
        /* KPI Metric Typography */
        .kpi-title {
            font-size: 0.8rem;
            font-weight: 600;
            color: #9ca3af;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            margin-bottom: 6px;
        }
        
        .kpi-value {
            font-family: 'Plus Jakarta Sans', sans-serif;
            font-size: 1.85rem;
            font-weight: 800;
            color: #ffffff;
            letter-spacing: -0.02em;
            line-height: 1;
            margin-bottom: 8px;
        }
        
        .kpi-trend {
            font-size: 0.75rem;
            font-weight: 600;
            display: flex;
            align-items: center;
            gap: 4px;
        }
        
        .trend-up {
            color: #10b981;
        }
        
        .trend-down {
            color: #ef4444;
        }
        
        /* Glowing Badges */
        .priority-badge-hot {
            background-color: rgba(239, 68, 68, 0.15);
            color: #f87171;
            border: 1px solid rgba(239, 68, 68, 0.3);
            border-radius: 6px;
            padding: 2px 8px;
            font-size: 0.75rem;
            font-weight: 600;
        }
        
        .priority-badge-warm {
            background-color: rgba(245, 158, 11, 0.15);
            color: #fbbf24;
            border: 1px solid rgba(245, 158, 11, 0.3);
            border-radius: 6px;
            padding: 2px 8px;
            font-size: 0.75rem;
            font-weight: 600;
        }
        
        .priority-badge-low {
            background-color: rgba(156, 163, 175, 0.15);
            color: #d1d5db;
            border: 1px solid rgba(156, 163, 175, 0.3);
            border-radius: 6px;
            padding: 2px 8px;
            font-size: 0.75rem;
            font-weight: 600;
        }
        
        /* Modern Sidebar Widgets */
        .sidebar-quota-box {
            background-color: rgba(255, 255, 255, 0.02);
            border: 1px solid #1f2937;
            border-radius: 8px;
            padding: 12px;
            margin-top: 30px;
        }
        
        .quota-text {
            font-size: 0.75rem;
            color: #9ca3af;
            margin-bottom: 5px;
        }
        
        .quota-bar-bg {
            background-color: #1f2937;
            border-radius: 4px;
            height: 6px;
            width: 100%;
            overflow: hidden;
            margin-bottom: 8px;
        }
        
        .quota-bar-fill {
            background: linear-gradient(90deg, #6c63ff 0%, #00d4ff 100%);
            height: 100%;
            border-radius: 4px;
        }
        
        /* Custom styled buttons */
        .stButton>button {
            background: linear-gradient(135deg, #6c63ff 0%, #7c4dff 100%) !important;
            color: #ffffff !important;
            font-family: 'Plus Jakarta Sans', sans-serif !important;
            font-weight: 600 !important;
            border: none !important;
            border-radius: 8px !important;
            box-shadow: 0 4px 12px rgba(108, 99, 255, 0.25) !important;
            transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1) !important;
            width: 100% !important;
        }
        
        .stButton>button:hover {
            transform: translateY(-1px) !important;
            box-shadow: 0 6px 18px rgba(108, 99, 255, 0.4) !important;
        }
        
        .stButton>button:active {
            transform: translateY(1px) !important;
        }
        
        /* Live Activity log Panel */
        .live-log-container {
            background-color: #07090e;
            border: 1px solid #1f2937;
            border-radius: 10px;
            padding: 14px;
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.8rem;
            color: #38bdf8;
            height: 200px;
            overflow-y: auto;
            white-space: pre-wrap;
            box-shadow: inset 0 2px 8px rgba(0,0,0,0.8);
        }
        
        /* Empty states styled illustration container */
        .empty-state-card {
            background-color: #111827;
            border: 1px dashed #374151;
            border-radius: 16px;
            padding: 40px;
            text-align: center;
            color: #9ca3af;
            box-shadow: 0 4px 20px rgba(0,0,0,0.1);
        }
        
        .empty-state-icon {
            font-size: 3rem;
            background: linear-gradient(135deg, #374151 0%, #1f2937 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 12px;
        }
        
        /* Circle quality score widget */
        .circle-gauge {
            width: 70px;
            height: 70px;
            border-radius: 50%;
            border: 4px solid #1f2937;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: 700;
            font-size: 1.1rem;
            color: white;
            margin: 0 auto;
        }
        
        .gauge-hot {
            border-color: #ef4444;
            background-color: rgba(239, 68, 68, 0.1);
        }
        
        .gauge-warm {
            border-color: #f59e0b;
            background-color: rgba(245, 158, 11, 0.1);
        }
        
        .gauge-low {
            border-color: #10b981;
            background-color: rgba(16, 185, 129, 0.1);
        }
        </style>
        """,
        unsafe_allow_html=True
    )

def get_saas_metrics(leads):
    """
    Generate styled HTML KPI Metric Blocks.
    """
    total = len(leads)
    hot = sum(1 for l in leads if l["lead_priority"] == "Hot Lead")
    emails = sum(1 for l in leads if l["contacts"].get("email"))
    socials = sum(1 for l in leads if l["contacts"].get("instagram") or l["contacts"].get("twitter_x"))
    
    return total, hot, emails, socials

def get_extended_mock_leads():
    """
    Returns an expanded set of 8 realistic mock YouTube channels representing diverse niches
    (gaming, cooking, travel, technology, fitness, beauty, finance, fashion) to support
    robust charts, distributions, and analytics rendering.
    """
    return [
        {
            "channel_id": "UC_mock_gaming_guru",
            "channel_name": "Pixel Arena Gaming",
            "channel_url": "https://youtube.com/@pixelarenagaming",
            "subscribers": 45200,
            "video_count": 86,
            "description": "Daily game reviews, retro consoles, and esports guides. Contact us at pixelarenabusiness@gmail.com for partnerships!",
            "recent_videos": [
                {"video_id": "mg1", "title": "Is This Retro Console Worth It in 2026?", "video_url": "https://www.youtube.com/watch?v=mg1", "thumbnail_url": "https://images.unsplash.com/photo-1538481199705-c710c4e965fc?w=600&auto=format&fit=crop&q=80", "description": "Reviewing emulators.", "published_at": "2026-05-30T12:00:00Z"},
                {"video_id": "mg2", "title": "Top 10 RPGs You Missed This Year!", "video_url": "https://www.youtube.com/watch?v=mg2", "thumbnail_url": "https://images.unsplash.com/photo-1607604276583-eef5d076aa5f?w=600&auto=format&fit=crop&q=80", "description": "RPGs you missed.", "published_at": "2026-05-25T14:30:00Z"},
                {"video_id": "mg3", "title": "Elden Ring: The Ultimate Lore Breakdown", "video_url": "https://www.youtube.com/watch?v=mg3", "thumbnail_url": "https://images.unsplash.com/photo-1511512578047-dfb367046420?w=600&auto=format&fit=crop&q=80", "description": "Lore breakdown.", "published_at": "2026-05-18T10:00:00Z"},
                {"video_id": "mg4", "title": "My New Streaming Setup (Budget Edition)", "video_url": "https://www.youtube.com/watch?v=mg4", "thumbnail_url": "https://images.unsplash.com/photo-1542751371-adc38448a05e?w=600&auto=format&fit=crop&q=80", "description": "Budget streaming gear.", "published_at": "2026-05-10T16:15:00Z"}
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
                {"blur_score": 45.3, "contrast_score": 8.4, "colorfulness_score": 15.6, "brightness_score": 38.0, "width": 1280, "height": 720, "ocr_char_count": 52, "face_detected": False, "clutter_score": 0.22, "issues": ["blurry", "low_contrast", "dull_colors", "low_brightness", "too_much_text", "no_clear_face", "cluttered"]},
                {"blur_score": 62.0, "contrast_score": 12.1, "colorfulness_score": 18.2, "brightness_score": 52.0, "width": 1280, "height": 720, "ocr_char_count": 40, "face_detected": False, "clutter_score": 0.18, "issues": ["blurry", "low_contrast", "dull_colors", "no_clear_face", "cluttered"]},
                {"blur_score": 80.5, "contrast_score": 14.3, "colorfulness_score": 24.1, "brightness_score": 42.0, "width": 1280, "height": 720, "ocr_char_count": 62, "face_detected": False, "clutter_score": 0.25, "issues": ["blurry", "low_contrast", "too_much_text", "no_clear_face", "cluttered", "low_brightness"]},
                {"blur_score": 55.1, "contrast_score": 9.2, "colorfulness_score": 16.8, "brightness_score": 35.0, "width": 1280, "height": 720, "ocr_char_count": 58, "face_detected": False, "clutter_score": 0.21, "issues": ["blurry", "low_contrast", "dull_colors", "low_brightness", "too_much_text", "no_clear_face", "cluttered"]}
            ],
            "brand_consistency": False,
            "lead_score": 38,
            "lead_priority": "Low Lead",
            "niche": "Gaming",
            "thumbnail_issues": ["Blurry thumbnails", "Low contrast layouts", "Dull colors / flat tones", "Thumbnails too dark", "Excessive thumbnail text", "Inconsistent branding/style", "Cluttered layouts"],
            "improvement_suggestions": [
                "Increase thumbnail image contrast using drop shadows or outlines on text panels.",
                "Boost color saturation and brightness: dark emulators make the feed look lifeless.",
                "Establish visual branding: retro-gaming channels require a recurring color theme.",
                "Reduce text density to 2-3 high-impact words rather than writing full sentences."
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
            "description": "Authentic Italian recipes. Email: mamacooksitalian@yahoo.com or DM on Instagram @MamaMiaCooks",
            "recent_videos": [
                {"video_id": "mc1", "title": "Secrets to the Perfect Neapolitan Pizza Crust", "video_url": "https://www.youtube.com/watch?v=mc1", "thumbnail_url": "https://images.unsplash.com/photo-1513104890138-7c749659a591?w=600&auto=format&fit=crop&q=80", "description": "Neapolitan crust secret.", "published_at": "2026-05-28T09:00:00Z"},
                {"video_id": "mc2", "title": "Grandma's Creamy Lasagna Recipe", "video_url": "https://www.youtube.com/watch?v=mc2", "thumbnail_url": "https://images.unsplash.com/photo-1574894709920-11b28e7367e3?w=600&auto=format&fit=crop&q=80", "description": "Beef lasagna recipe.", "published_at": "2026-05-22T11:00:00Z"},
                {"video_id": "mc3", "title": "Fast & Fresh 10-Minute Pasta Dinner", "video_url": "https://www.youtube.com/watch?v=mc3", "thumbnail_url": "https://images.unsplash.com/photo-1563379091339-03b21ab4a4f8?w=600&auto=format&fit=crop&q=80", "description": "Quick pasta dinner.", "published_at": "2026-05-15T10:00:00Z"},
                {"video_id": "mc4", "title": "How to Cure Pancetta at Home", "video_url": "https://www.youtube.com/watch?v=mc4", "thumbnail_url": "https://images.unsplash.com/photo-1608686207856-001b95cf60ca?w=600&auto=format&fit=crop&q=80", "description": "Home pancetta curing.", "published_at": "2026-05-08T08:30:00Z"}
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
                {"blur_score": 180.2, "contrast_score": 42.1, "colorfulness_score": 28.5, "brightness_score": 115.0, "width": 1280, "height": 720, "ocr_char_count": 5, "face_detected": False, "clutter_score": 0.08, "issues": ["no_clear_face"]},
                {"blur_score": 195.4, "contrast_score": 38.6, "colorfulness_score": 32.1, "brightness_score": 125.0, "width": 1280, "height": 720, "ocr_char_count": 7, "face_detected": False, "clutter_score": 0.09, "issues": ["no_clear_face"]},
                {"blur_score": 210.0, "contrast_score": 40.5, "colorfulness_score": 35.2, "brightness_score": 130.0, "width": 1280, "height": 720, "ocr_char_count": 5, "face_detected": False, "clutter_score": 0.07, "issues": ["no_clear_face"]},
                {"blur_score": 172.5, "contrast_score": 36.4, "colorfulness_score": 25.1, "brightness_score": 105.0, "width": 1280, "height": 720, "ocr_char_count": 8, "face_detected": False, "clutter_score": 0.10, "issues": ["no_clear_face"]}
            ],
            "brand_consistency": True,
            "lead_score": 85,
            "lead_priority": "Hot Lead",
            "niche": "Cooking",
            "thumbnail_issues": ["No clear face or character focus"],
            "improvement_suggestions": [
                "Thumbnails look beautiful, but are missing a human element.",
                "Try incorporating a high-resolution close-up of a face expressing excitement to taste the pasta.",
                "This emotional hook can dramatically increase the Click-Through Rate (CTR)."
            ],
            "status": "Processed",
            "manual_review_status": "Approved",
            "created_at": datetime.now().isoformat()
        },
        {
            "channel_id": "UC_mock_tech_unboxed",
            "channel_name": "Gizmo Unboxing",
            "channel_url": "https://youtube.com/@gizmounboxing",
            "subscribers": 68000,
            "video_count": 142,
            "description": "Tech unboxings. Collabs: collabs@gizmounbox.co. Website: gizmounbox.co",
            "recent_videos": [
                {"video_id": "mt1", "title": "This $10 Phone is Surprisingly Good!", "video_url": "https://www.youtube.com/watch?v=mt1", "thumbnail_url": "https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?w=600&auto=format&fit=crop&q=80", "description": "Reviewing phone.", "published_at": "2026-05-29T15:00:00Z"},
                {"video_id": "mt2", "title": "Is the New Smartwatch a Scam? (Honest Review)", "video_url": "https://www.youtube.com/watch?v=mt2", "thumbnail_url": "https://images.unsplash.com/photo-1508685096489-7aacd43bd3b1?w=600&auto=format&fit=crop&q=80", "description": "Smartwatch test.", "published_at": "2026-05-24T16:00:00Z"},
                {"video_id": "mt3", "title": "I Bought a Refurbished Laptop from a Sketchy Website", "video_url": "https://www.youtube.com/watch?v=mt3", "thumbnail_url": "https://images.unsplash.com/photo-1588872657578-7efd1f1555ed?w=600&auto=format&fit=crop&q=80", "description": "Laptop unbox.", "published_at": "2026-05-16T12:00:00Z"},
                {"video_id": "mt4", "title": "My Favorite Tech Accessories Under $25", "video_url": "https://www.youtube.com/watch?v=mt4", "thumbnail_url": "https://images.unsplash.com/photo-1468495244123-6c6c332eeece?w=600&auto=format&fit=crop&q=80", "description": "Budget gear.", "published_at": "2026-05-09T14:00:00Z"}
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
                {"blur_score": 160.5, "contrast_score": 28.1, "colorfulness_score": 11.2, "brightness_score": 85.0, "width": 1280, "height": 720, "ocr_char_count": 55, "face_detected": False, "clutter_score": 0.19, "issues": ["dull_colors", "too_much_text", "no_clear_face", "cluttered"]},
                {"blur_score": 140.2, "contrast_score": 26.5, "colorfulness_score": 14.5, "brightness_score": 90.0, "width": 1280, "height": 720, "ocr_char_count": 52, "face_detected": False, "clutter_score": 0.18, "issues": ["dull_colors", "too_much_text", "no_clear_face", "cluttered"]},
                {"blur_score": 182.1, "contrast_score": 30.2, "colorfulness_score": 9.8, "brightness_score": 80.0, "width": 1280, "height": 720, "ocr_char_count": 54, "face_detected": False, "clutter_score": 0.20, "issues": ["dull_colors", "too_much_text", "no_clear_face", "cluttered"]},
                {"blur_score": 150.8, "contrast_score": 24.3, "colorfulness_score": 13.0, "brightness_score": 75.0, "width": 1280, "height": 720, "ocr_char_count": 52, "face_detected": False, "clutter_score": 0.17, "issues": ["dull_colors", "too_much_text", "no_clear_face", "cluttered"]}
            ],
            "brand_consistency": True,
            "lead_score": 58,
            "lead_priority": "Warm Lead",
            "niche": "Technology",
            "thumbnail_issues": ["Dull colors / flat tones", "Excessive thumbnail text", "No clear face or character focus", "Cluttered layouts"],
            "improvement_suggestions": [
                "Contrast tech gadgets against highly saturated background glows (e.g. orange vs violet).",
                "Reduce text clutter: replace long summaries with short phrases like 'SCAM?' in massive fonts.",
                "Incorporate a close-up of a face reacting to the sketchy packaging to hook tech viewers."
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
            "description": "Makeup tutorials and glow-ups. Let's collaborate: contact@glowwithgrace.com",
            "recent_videos": [
                {"video_id": "mb1", "title": "My 5-Step Flawless Skincare Routine", "video_url": "https://www.youtube.com/watch?v=mb1", "thumbnail_url": "https://images.unsplash.com/photo-1598440947619-2c35fc9aa908?w=600&auto=format&fit=crop&q=80", "description": "Daily skin glow.", "published_at": "2026-05-30T10:00:00Z"},
                {"video_id": "mb2", "title": "Testing Viral TikTok Skincare Products", "video_url": "https://www.youtube.com/watch?v=mb2", "thumbnail_url": "https://images.unsplash.com/photo-1522335789203-aabd1fc54bc9?w=600&auto=format&fit=crop&q=80", "description": "Viral skincare review.", "published_at": "2026-05-23T11:00:00Z"},
                {"video_id": "mb3", "title": "Drugstore vs High-End Makeup Challenge", "video_url": "https://www.youtube.com/watch?v=mb3", "thumbnail_url": "https://images.unsplash.com/photo-1512496015851-a90fb38ba796?w=600&auto=format&fit=crop&q=80", "description": "Splurge vs save.", "published_at": "2026-05-15T09:00:00Z"},
                {"video_id": "mb4", "title": "How to Do Eyeliner for Beginners", "video_url": "https://www.youtube.com/watch?v=mb4", "thumbnail_url": "https://images.unsplash.com/photo-1487412720507-e7ab37603c6f?w=600&auto=format&fit=crop&q=80", "description": "Winged eyeliner guide.", "published_at": "2026-05-05T13:00:00Z"}
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
                {"blur_score": 38.2, "contrast_score": 45.1, "colorfulness_score": 32.4, "brightness_score": 160.0, "width": 1280, "height": 720, "ocr_char_count": 8, "face_detected": True, "clutter_score": 0.05, "issues": ["blurry"]},
                {"blur_score": 40.5, "contrast_score": 42.0, "colorfulness_score": 28.5, "brightness_score": 155.0, "width": 1280, "height": 720, "ocr_char_count": 12, "face_detected": True, "clutter_score": 0.06, "issues": ["blurry"]},
                {"blur_score": 29.8, "contrast_score": 38.6, "colorfulness_score": 30.1, "brightness_score": 165.0, "width": 1280, "height": 720, "ocr_char_count": 15, "face_detected": True, "clutter_score": 0.06, "issues": ["blurry"]},
                {"blur_score": 42.1, "contrast_score": 41.2, "colorfulness_score": 31.0, "brightness_score": 150.0, "width": 1280, "height": 720, "ocr_char_count": 15, "face_detected": True, "clutter_score": 0.05, "issues": ["blurry"]}
            ],
            "brand_consistency": True,
            "lead_score": 79,
            "lead_priority": "Hot Lead",
            "niche": "Beauty & Fashion",
            "thumbnail_issues": ["Blurry thumbnails"],
            "improvement_suggestions": [
                "Your camera closeups look beautiful, but export compression causes blurriness.",
                "Export thumbnails as high-quality PNGs in exact 1280x720 px to prevent pixelation.",
                "Apply a slight high-pass sharpening filter on eyelashes and skin textures."
            ],
            "status": "Processed",
            "manual_review_status": "Needs Manual Review",
            "created_at": datetime.now().isoformat()
        },
        {
            "channel_id": "UC_mock_nomad_travel",
            "channel_name": "Wanderlust Chronicles",
            "channel_url": "https://youtube.com/@wanderlustchronicles",
            "subscribers": 52000,
            "video_count": 94,
            "description": "Solo travel diaries and street food tours globally. Reach us: hello@wanderlustdiaries.com",
            "recent_videos": [
                {"video_id": "tr1", "title": "I Spent 48 Hours in Tokyo's Capsule Hotel", "video_url": "https://www.youtube.com/watch?v=tr1", "thumbnail_url": "https://images.unsplash.com/photo-1540959733332-eab4deceeaf7?w=600&auto=format&fit=crop&q=80", "description": "Tokyo capsule hotel.", "published_at": "2026-05-27T08:00:00Z"},
                {"video_id": "tr2", "title": "This Street Food Market is a Hidden Gem", "video_url": "https://www.youtube.com/watch?v=tr2", "thumbnail_url": "https://images.unsplash.com/photo-1504674900247-0877df9cc836?w=600&auto=format&fit=crop&q=80", "description": "Tokyo street food.", "published_at": "2026-05-20T10:00:00Z"}
            ],
            "contacts": {
                "email": "hello@wanderlustdiaries.com",
                "instagram": "https://instagram.com/wanderlust",
                "twitter_x": "",
                "facebook": "",
                "linktree": "",
                "website": "https://wanderlustdiaries.com",
                "other_links": []
            },
            "cv_analysis": [
                {"blur_score": 115.3, "contrast_score": 18.2, "colorfulness_score": 12.1, "brightness_score": 110.0, "width": 1280, "height": 720, "ocr_char_count": 48, "face_detected": False, "clutter_score": 0.26, "issues": ["dull_colors", "cluttered", "no_clear_face"]},
                {"blur_score": 130.4, "contrast_score": 14.5, "colorfulness_score": 9.2, "brightness_score": 95.0, "width": 1280, "height": 720, "ocr_char_count": 30, "face_detected": False, "clutter_score": 0.22, "issues": ["dull_colors", "cluttered", "no_clear_face", "low_contrast"]}
            ],
            "brand_consistency": False,
            "lead_score": 46,
            "lead_priority": "Low Lead",
            "niche": "Travel",
            "thumbnail_issues": ["Dull colors / flat tones", "Cluttered layouts", "No clear face or character focus"],
            "improvement_suggestions": [
                "Tokyo street food scenes look crowded and gray. Apply warm LUT filters.",
                "Clean up composition: place the capsule bed or food dish as a large visual center.",
                "Add a clean solo traveler face displaying shock or culinary delight."
            ],
            "status": "Processed",
            "manual_review_status": "Needs Manual Review",
            "created_at": datetime.now().isoformat()
        },
        {
            "channel_id": "UC_mock_fit_life",
            "channel_name": "Iron Mind Fitness",
            "channel_url": "https://youtube.com/@ironmindfit",
            "subscribers": 9500,
            "video_count": 52,
            "description": "Home workouts, bodybuilding, and macro science. Collabs: fitmindiron@outlook.com",
            "recent_videos": [
                {"video_id": "ft1", "title": "The Perfect 15-Minute Home Dumbbell Workout", "video_url": "https://www.youtube.com/watch?v=ft1", "thumbnail_url": "https://images.unsplash.com/photo-1517838277536-f5f99be501cd?w=600&auto=format&fit=crop&q=80", "description": "Home dumbbell routine.", "published_at": "2026-05-29T06:00:00Z"},
                {"video_id": "ft2", "title": "5 High-Protein Meals Under 500 Calories", "video_url": "https://www.youtube.com/watch?v=ft2", "thumbnail_url": "https://images.unsplash.com/photo-1546069901-ba9599a7e63c?w=600&auto=format&fit=crop&q=80", "description": "Bodybuilding recipes.", "published_at": "2026-05-22T08:00:00Z"}
            ],
            "contacts": {
                "email": "fitmindiron@outlook.com",
                "instagram": "https://instagram.com/ironmind",
                "twitter_x": "",
                "facebook": "",
                "linktree": "",
                "website": "",
                "other_links": []
            },
            "cv_analysis": [
                {"blur_score": 155.0, "contrast_score": 9.4, "colorfulness_score": 15.0, "brightness_score": 105.0, "width": 1280, "height": 720, "ocr_char_count": 6, "face_detected": True, "clutter_score": 0.08, "issues": ["low_contrast", "dull_colors"]},
                {"blur_score": 142.1, "contrast_score": 11.2, "colorfulness_score": 13.4, "brightness_score": 98.0, "width": 1280, "height": 720, "ocr_char_count": 8, "face_detected": True, "clutter_score": 0.09, "issues": ["low_contrast", "dull_colors"]}
            ],
            "brand_consistency": True,
            "lead_score": 72,
            "lead_priority": "Warm Lead",
            "niche": "Fitness",
            "thumbnail_issues": ["Low contrast layouts", "Dull colors / flat tones"],
            "improvement_suggestions": [
                "Boost the brightness and shadow details in gym clips.",
                "Fit and recipe thumbnails require high-contrast text bubbles (e.g. neon green background chips)."
            ],
            "status": "Processed",
            "manual_review_status": "Needs Manual Review",
            "created_at": datetime.now().isoformat()
        }
    ]
