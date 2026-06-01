import logging
from modules.utils import logger

def calculate_lead_score(analysis_results, contacts, config=None):
    """
    Calculate lead score and assign lead priority based on CV and contact extraction.
    Returns: (score, priority, issues_list, suggestions_list)
    """
    if config is None:
        from modules.utils import load_config
        config = load_config()
        
    weights = config.get("scoring_weights", {
        "blur_penalty": -15,
        "contrast_penalty": -10,
        "colorfulness_penalty": -10,
        "ocr_penalty": -10,
        "clutter_penalty": -8,
        "consistency_penalty": -8,
        "resolution_penalty": -5,
        "email_bonus": 10,
        "socials_bonus": 5,
        "website_bonus": 5,
        "improvement_bonus": 10
    })

    score = 100
    issues = []
    suggestions = []
    
    # Check if analysis results are valid
    if not analysis_results:
        return 0, "Low Lead", ["No analysis possible"], ["Check channel videos"]
        
    # Gather issues from the latest thumbnails
    blur_count = 0
    contrast_count = 0
    dull_count = 0
    too_much_text_count = 0
    cluttered_count = 0
    low_res_count = 0
    no_face_count = 0
    dark_count = 0
    bright_count = 0
    
    total_analyzed = len(analysis_results)
    
    for res in analysis_results:
        if "error" in res:
            continue
        local_issues = res.get("issues", [])
        if "blurry" in local_issues:
            blur_count += 1
        if "low_contrast" in local_issues:
            contrast_count += 1
        if "dull_colors" in local_issues:
            dull_count += 1
        if "too_much_text" in local_issues:
            too_much_text_count += 1
        if "cluttered" in local_issues:
            cluttered_count += 1
        if "low_resolution" in local_issues:
            low_res_count += 1
        if "no_clear_face" in local_issues:
            no_face_count += 1
        if "low_brightness" in local_issues:
            dark_count += 1
        if "high_brightness" in local_issues:
            bright_count += 1

    # Apply penalties based on majority of recent videos
    if total_analyzed > 0:
        # Blur
        if blur_count >= (total_analyzed / 2):
            score += weights.get("blur_penalty", -15)
            issues.append("Blurry thumbnails")
            suggestions.append("Use higher resolution cameras or adjust focal depth to make thumbnails crisp and sharp.")
            
        # Low Contrast
        if contrast_count >= (total_analyzed / 2):
            score += weights.get("contrast_penalty", -10)
            issues.append("Low contrast layouts")
            suggestions.append("Apply a drop shadow or dark outer glow to subjects to contrast them against bright backgrounds.")
            
        # Dull Colors
        if dull_count >= (total_analyzed / 2):
            score += weights.get("colorfulness_penalty", -10)
            issues.append("Dull colors / flat tones")
            suggestions.append("Slightly increase the color saturation or shift HSL values to make thumbnails pop in a crowded feed.")
            
        # Brightness (too dark/too bright)
        if dark_count >= (total_analyzed / 2):
            score += -5
            issues.append("Thumbnails too dark")
            suggestions.append("Boost exposures or add high-contrast accent lights to brighten key visual elements.")
        elif bright_count >= (total_analyzed / 2):
            score += -5
            issues.append("Thumbnails overexposed")
            suggestions.append("Tone down whites and highlights to ensure important thumbnail details are not washed out.")
            
        # Too Much Text
        if too_much_text_count >= (total_analyzed / 2):
            score += weights.get("ocr_penalty", -10)
            issues.append("Excessive thumbnail text")
            suggestions.append("Reduce text to 1-4 high-impact keywords. Make typography large and bold enough to read easily on mobile screens.")
            
        # No Clear Face
        if no_face_count >= (total_analyzed / 2):
            # Not a heavy penalty but worth noting
            issues.append("No clear face or character focus")
            suggestions.append("Try adding close-ups of human faces displaying strong emotion (surprise, excitement, curiosity) to improve click-through rates (CTR).")
            
        # Cluttered Layout
        if cluttered_count >= (total_analyzed / 2):
            score += weights.get("clutter_penalty", -8)
            issues.append("Cluttered layouts")
            suggestions.append("Simplify layouts. Apply the rule of thirds, keep only 2-3 visual anchors, and maintain clean negative space.")
            
        # Low Resolution
        if low_res_count > 0:
            score += weights.get("resolution_penalty", -5)
            issues.append("Low resolution files")
            suggestions.append("Always export and upload standard HD 16:9 resolutions (1280x720 px) in JPEG/PNG.")

    # Consistency Check (if consistent score is provided in analysis metadata)
    # We will evaluate consistency outside or pull the flag
    # Let's say if we get an inconsistency flag
    brand_consistent = True
    if "brand_consistency" in analysis_results[0]: # Stored as a general status in the first entry
        brand_consistent = analysis_results[0]["brand_consistency"]
        
    if not brand_consistent:
        score += weights.get("consistency_penalty", -8)
        issues.append("Inconsistent branding/style")
        suggestions.append("Establish visual cohesion. Use a unified color palette, signature font styles, and a recurring layout format across uploads.")

    # Apply Bonuses
    has_contact = False
    
    # Email Bonus
    if contacts.get("email"):
        score += weights.get("email_bonus", 10)
        has_contact = True
    
    # Socials Bonus
    if contacts.get("instagram") or contacts.get("twitter_x") or contacts.get("facebook") or contacts.get("linktree"):
        score += weights.get("socials_bonus", 5)
        has_contact = True
        
    # Website Bonus
    if contacts.get("website"):
        score += weights.get("website_bonus", 5)
        has_contact = True

    # If absolutely no contact details are found, subtract heavily as outreach is difficult
    if not has_contact:
        score -= 20
        issues.append("No contact details found")
        suggestions.append("Try visiting the YouTube channel page manually to check if an email appears behind their protected Captcha wall.")
    
    # Bonus for clear improvement potential (if we had visual issues and we have contact info)
    if len(issues) > 0 and has_contact:
        score += weights.get("improvement_bonus", 10)

    # Normalize final score between 0 and 100
    final_score = max(0, min(100, score))
    
    # Assign Lead Priority
    if final_score >= 75:
        priority = "Hot Lead"
    elif final_score >= 50:
        priority = "Warm Lead"
    else:
        priority = "Low Lead"

    # Default suggestion if everything looks perfect
    if not suggestions:
        suggestions.append("Thumbnails look professional! Consider proposing minor variations or A/B testing typography.")
        
    return final_score, priority, issues, suggestions
