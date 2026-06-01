# YouTube Thumbnail Lead Finder 🎥💼

A fully working, professional, and completely free Python YouTube lead-generation bot for graphic designers, thumbnail artists, and agency owners. 

The bot crawls YouTube channels in a specific niche and size range (e.g., 1,000 to 70,000 subscribers by default), downloads their recent thumbnails, conducts deep computer vision quality checks, extracts their publicly available contact info (email, social accounts, external websites), scores each lead based on visual improvement potential, and compiles them in a beautiful dark SaaS-style Streamlit dashboard.

---

## Key Features 🚀

- **Flexible Backend modes**:
  - **YouTube API Mode**: Fast search utilizing Google's official client.
  - **yt-dlp Fallback Mode**: Scraping fallback when API key is missing or quota is exhausted.
  - **Hybrid Mode**: Attempts to run YouTube API first and automatically falls back to yt-dlp on quota errors.
- **Advanced public Contact Scraper**: Finds emails, Linktree, Instagram, X/Twitter, Facebook, and external website links in channel and video descriptions. Gently crawls linked business websites for public contact info.
- **Rule-Based Computer Vision Analysis**:
  - **Blur Detection** (Variance of Laplacian)
  - **Contrast Assessment** (Skimage contrast standard deviation)
  - **Colorfulness Score** (Hasler and Suesstrunk opponent color space formula)
  - **Brightness & Exposure Checks** (HSV-based lighting metrics)
  - **Resolution Verification** (Checks for ideal HD 16:9 1280x720 px dimensions)
  - **Face Detection** (OpenCV frontal Haar cascades to check for person presence)
  - **Clutter Ratio** (Canny edge density checks)
  - **Style Consistency** (Average HSV histogram correlation check across all 4 recent uploads)
- **Intelligent Lead Scoring**: Automatically calculates a normalized outreach priority score (0–100) assigning leads to **Hot**, **Warm**, or **Low** priority tiers. Generates actionable designer advice for each issue.
- **Premium Dark Streamlit UI**: Offers real-time crawler logs, interactive filtered results tables (`st.data_editor`), manual review toggles, visual thumbnail side-by-side cards with overlay statistics, and a spreadsheet exporter.
- **Offline Sandbox / Mock Mode**: Toggle mock data in a single click to test all UI capabilities immediately.

---

## 🛠️ Step-by-Step Installation

### Step 1: Install Python
Ensure you have Python 3.10+ installed on your machine.
- **Windows**: Download the installer from [python.org](https://www.python.org/downloads/). During installation, **make sure to check the box: "Add Python to PATH"**.
- **macOS/Linux**: Usually pre-installed. You can install/upgrade via Homebrew: `brew install python`.

Verify in your terminal:
```bash
python --version
```

### Step 2: Clone/Download and Install Dependencies
Open your terminal or command prompt inside the project folder (`youtube_thumbnail_leads` or your workspace) and install the packages listed in `requirements.txt`:
```bash
pip install -r requirements.txt
```

### Step 3: Install Tesseract OCR (Highly Recommended)
Tesseract OCR is required for the *OCR Text Check* feature to measure how much text is placed on a thumbnail. If Tesseract is not installed, the bot will run completely fine but will skip text parsing and log a gentle warning.

- **Windows**:
  1. Download the Windows installer from [UB Mannheim's Tesseract Page](https://github.com/UB-Mannheim/tesseract/wiki).
  2. Run the installer and note down the installation path (typically `C:\Program Files\Tesseract-OCR`).
  3. Add the installation folder to your Windows system Environment Variable **PATH**:
     - Search "Environment Variables" in Windows Search.
     - Select "Environment Variables..."
     - Find the `Path` variable under "User variables" or "System variables", click Edit.
     - Click **New** and paste the folder path (e.g. `C:\Program Files\Tesseract-OCR`). Click OK on all windows.
- **macOS**:
  ```bash
  brew install tesseract
  ```
- **Linux (Ubuntu/Debian)**:
  ```bash
  sudo apt-get install tesseract-ocr
  ```

---

## 🔑 Acquiring a Free YouTube API Key

1. Visit the [Google Cloud Console](https://console.cloud.google.com/).
2. Create a new project (e.g., "YouTube Lead Bot").
3. In the sidebar, navigate to **APIs & Services** > **Library**.
4. Search for **YouTube Data API V3** and click **Enable**.
5. Go to the **Credentials** tab on the left sidebar.
6. Click **+ Create Credentials** at the top and select **API Key**.
7. Copy your generated key and paste it directly into the Streamlit sidebar or the `config.json` file.
   *Note: Free API keys have a daily limit of 10,000 units. To conserve quota, we recommend running in Hybrid Mode.*

---

## ⚡ How to Run the App

Launch the Streamlit server from your terminal:
```bash
streamlit run app.py
```
This will automatically open your default web browser to:
`http://localhost:8501`

---

## 📊 How Lead Scoring & Priority Works

The lead scorer begins with an initial perfect score of **100**.

### Flaw Deductions (Penalties):
- **Blurry thumbnails**: `-15` (Average Laplacian variance is below threshold)
- **Low contrast layouts**: `-10` (Low-contrast check or standard deviation is low)
- **Dull colors / flat tones**: `-10` (Colorfulness score is below threshold)
- **Excessive thumbnail text**: `-10` (OCR character count exceeds limit)
- **Cluttered visual layouts**: `-8` (Edge pixel density is high)
- **Inconsistent branding**: `-8` (Average HSV histogram correlation is low)
- **Low resolution files**: `-5` (Uploaded file is under 640x360 px)
- **No contact details found**: `-20` (outreach is difficult)

### Contact Bonuses:
- **Email found**: `+10`
- **Socials found (IG/X/FB/Linktree)**: `+5`
- **Website found**: `+5`
- **Improvement potential**: `+10` (Awarded when at least one visual flaw is present and contact is available)

### Priority Tiers:
- **Hot Lead** (Score `75–100`): Perfect outreach candidate. High visual improvement potential and active public contact info.
- **Warm Lead** (Score `50–74`): Good outreach candidate. Improvable thumbnails, contact info exists, minor scoring deductions.
- **Low Lead** (Score `< 50`): Poor candidate (either thumbnails look excellent already, or no contact info is available).

---

## ⚖️ Legal Disclaimer & TOS Warnings

This tool is designed strictly for **marketing outreach and manual business development**.
- **Do not spam**: High-frequency cold emailing or automated DMs violates spam laws (CAN-SPAM, GDPR). Use this bot to select high-quality leads, and pitch them personalized, manually reviewed thumbnail improvements.
- **TOS Compliance**: We do not scrape hidden YouTube database fields, bypass recaptchas, or query restricted APIs. All information collected is publicly visible to any standard browser client.

---

## 🛠️ Troubleshooting

- **Error: "TesseractNotFoundError"**:
  Ensure Tesseract is installed and that you added the folder path to your system's Environment Variable **PATH**. Restart your terminal and web editor after updating system paths for changes to apply.
- **API Quota Exceeded**:
  If you run out of YouTube API quota, toggle the dashboard search setting to **yt-dlp fallback** mode or delete the API key to use the scraping engine.
- **OpenCV/Tkinter conflicts inside headless environments**:
  Ensure you are using `opencv-python` (which includes precompiled binaries). Do not use headless unless you are running inside a server without a monitor.
