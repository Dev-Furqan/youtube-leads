import re
import requests
from bs4 import BeautifulSoup
from modules.utils import logger

# Regex patterns
EMAIL_PATTERN = r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+'
# Match obfuscated emails like name [at] domain [dot] com or name(at)domain.com
OBFUSCATED_EMAIL_PATTERN = r'([a-zA-Z0-9_.-]+)\s*[\(\[_-]*\s*at\s*[\)\]_-]*\s*([a-zA-Z0-9_-]+)\s*[\(\[_-]*\s*dot\s*[\)\]_-]*\s*([a-zA-Z0-9.-]+)'

INSTAGRAM_PATTERN = r'(?:https?://)?(?:www\.)?instagram\.com/([a-zA-Z0-9_\.]+)'
TWITTER_X_PATTERN = r'(?:https?://)?(?:www\.)?(?:twitter\.com|x\.com)/([a-zA-Z0-9_]+)'
FACEBOOK_PATTERN = r'(?:https?://)?(?:www\.)?facebook\.com/([a-zA-Z0-9_\.]+)'
LINKTREE_PATTERN = r'(?:https?://)?(?:www\.)?linktr\.ee/([a-zA-Z0-9_\-]+)'

# General URLs (excluding popular social media domains to isolate business websites)
GENERIC_URL_PATTERN = r'https?://(?:www\.)?([a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)'
SOCIAL_DOMAINS = ['youtube.com', 'youtu.be', 'google.com', 'instagram.com', 'twitter.com', 'x.com', 'facebook.com', 'linktr.ee', 't.co', 'pinterest.com', 'tiktok.com', 'linkedin.com']

def clean_social_username(username):
    """Clean extracted usernames from trailing punctuation or subpaths."""
    if not username:
        return ""
    # Strip trailing slashes, question marks, or extra subpaths
    username = username.split('/')[0].split('?')[0].split('#')[0]
    return username.strip()

def extract_contacts_from_text(text):
    """
    Extract email, socials, and website links from a raw block of text.
    """
    contacts = {
        "email": "",
        "instagram": "",
        "twitter_x": "",
        "facebook": "",
        "linktree": "",
        "website": "",
        "other_links": []
    }
    
    if not text:
        return contacts
        
    # 1. Search for standard emails
    emails = re.findall(EMAIL_PATTERN, text)
    if emails:
        # Filter out common false positives if any
        contacts["email"] = emails[0]
    else:
        # 2. Search for obfuscated emails
        obfuscated = re.findall(OBFUSCATED_EMAIL_PATTERN, text, re.IGNORECASE)
        if obfuscated:
            user, domain, tld = obfuscated[0]
            contacts["email"] = f"{user}@{domain}.{tld}".lower()
            logger.info(f"Reconstructed obfuscated email: {contacts['email']}")

    # 3. Search for socials
    ig_matches = re.findall(INSTAGRAM_PATTERN, text, re.IGNORECASE)
    if ig_matches:
        contacts["instagram"] = f"https://instagram.com/{clean_social_username(ig_matches[0])}"
        
    tx_matches = re.findall(TWITTER_X_PATTERN, text, re.IGNORECASE)
    if tx_matches:
        contacts["twitter_x"] = f"https://x.com/{clean_social_username(tx_matches[0])}"
        
    fb_matches = re.findall(FACEBOOK_PATTERN, text, re.IGNORECASE)
    if fb_matches:
        contacts["facebook"] = f"https://facebook.com/{clean_social_username(fb_matches[0])}"
        
    lt_matches = re.findall(LINKTREE_PATTERN, text, re.IGNORECASE)
    if lt_matches:
        contacts["linktree"] = f"https://linktr.ee/{clean_social_username(lt_matches[0])}"

    # 4. Search for other links/websites
    urls = re.findall(r'https?://[a-zA-Z0-9-._~:/?#\[\]@!$&\'()*+,;=%]+', text)
    unique_links = list(set(urls))
    
    for url in unique_links:
        # Check if it's a social domain
        is_social = False
        for dom in SOCIAL_DOMAINS:
            if dom in url.lower():
                is_social = True
                break
        
        if not is_social:
            # We found a potential website
            contacts["other_links"].append(url)
            if not contacts["website"]:
                contacts["website"] = url
                
    return contacts

def scrape_website_for_contacts(url):
    """
    Gently scrape a website's homepage to find email/social handles.
    Respect timeouts and handle failures gracefully.
    """
    if not url:
        return {}
        
    logger.info(f"Attempting to scan external website homepage: {url}...")
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.0.0 Safari/537.36'
    }
    
    scraped_contacts = {}
    
    try:
        response = requests.get(url, headers=headers, timeout=5)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            page_text = soup.get_text()
            
            # Extract emails and social links from the page
            page_contacts = extract_contacts_from_text(page_text)
            
            # Extract standard href attributes to double-check links
            for link in soup.find_all('a', href=True):
                href = link['href']
                
                # Check for mailto
                if href.startswith('mailto:'):
                    email = href.replace('mailto:', '').split('?')[0].strip()
                    if email and re.match(EMAIL_PATTERN, email):
                        scraped_contacts['email'] = email
                        
                # Check for social profile links
                if 'instagram.com/' in href:
                    ig_user = href.split('instagram.com/')[-1].split('/')[0]
                    scraped_contacts['instagram'] = f"https://instagram.com/{clean_social_username(ig_user)}"
                elif 'twitter.com/' in href or 'x.com/' in href:
                    t_user = href.split('.com/')[-1].split('/')[0]
                    scraped_contacts['twitter_x'] = f"https://x.com/{clean_social_username(t_user)}"
                elif 'facebook.com/' in href:
                    fb_user = href.split('facebook.com/')[-1].split('/')[0]
                    scraped_contacts['facebook'] = f"https://facebook.com/{clean_social_username(fb_user)}"
                    
            if page_contacts['email'] and 'email' not in scraped_contacts:
                scraped_contacts['email'] = page_contacts['email']
                
            logger.info(f"Website scrape completed. Extracted: {scraped_contacts}")
            
    except Exception as e:
        logger.warning(f"Failed to scrape external website {url}: {e}")
        
    return scraped_contacts

def extract_channel_lead_contacts(channel_desc, videos, enable_web_scraping=True):
    """
    Aggregate and extract contacts from channel description and video descriptions.
    """
    logger.info("Running contact extractor...")
    
    # 1. Start with channel description
    contacts = extract_contacts_from_text(channel_desc)
    
    # 2. Add video descriptions
    for idx, video in enumerate(videos):
        vid_desc = video.get("description", "")
        if vid_desc:
            vid_contacts = extract_contacts_from_text(vid_desc)
            
            # Fill in blank values
            for field in ["email", "instagram", "twitter_x", "facebook", "linktree"]:
                if not contacts[field] and vid_contacts[field]:
                    contacts[field] = vid_contacts[field]
                    logger.info(f"Found contact {field} in video {idx+1} description: {vid_contacts[field]}")
            
            # Combine other links
            if vid_contacts["other_links"]:
                contacts["other_links"].extend(vid_contacts["other_links"])
                
    # Deduplicate other links
    contacts["other_links"] = list(set(contacts["other_links"]))
    
    # Normalize website if not set but we have other links
    if not contacts["website"] and contacts["other_links"]:
        contacts["website"] = contacts["other_links"][0]

    # 3. Scrape linked website if enabled and website URL is present
    if enable_web_scraping and contacts["website"]:
        web_contacts = scrape_website_for_contacts(contacts["website"])
        for field in ["email", "instagram", "twitter_x", "facebook"]:
            if not contacts[field] and field in web_contacts and web_contacts[field]:
                contacts[field] = web_contacts[field]
                logger.info(f"Found contact {field} from external website scan: {web_contacts[field]}")

    return contacts
