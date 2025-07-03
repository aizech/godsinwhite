from pathlib import Path

class Config:
    COMPANY = "GodsinWhite"
    COMPANY_URL = "https://www.godsinwhite.com/"

    SUPPORT_URL = "https://www.godsinwhite.com/support"

    # --- Constants & Directories ---
    APP_NAME      = "GodsinWhite"
    APP_ICON      = ":material/smart_toy:"
    APP_URL       = "https://www.godsinwhite.com/"
    CONTACT_EMAIL = "ai@godsinwhite.com"

    THIS_DIR      = Path(__file__).parent
    #STYLES_DIR    = THIS_DIR / "styles"
    #CSS_FILE      = THIS_DIR / "styles" / "custom.css"
    ASSETS_DIR    = THIS_DIR / "assets"
    
    APP_DESCRIPTION = "GodsinWhite is an AI interface for orchestrating multiple AI Agents and Teams of AI Agents in the medical field"

    MENU_ITEMS = {
        'Get Help': f"{APP_URL}/help",
        'Report a bug': f"{APP_URL}/about",
        'About': "## This is the " + APP_NAME + " App!  Made with " + ":heart: by " + COMPANY
    }

    MASTER_AGENT_ICON = ASSETS_DIR / "godsinwhite_team.png"

    LOGO_TEXT_PATH = ASSETS_DIR / "godsinwhite_logo_text.png"
    LOGO_ICON_PATH = ASSETS_DIR / "godsinwhite_logo.png"
    LOGO_TEAM_PATH = ASSETS_DIR / "godsinwhite_team.png"

    LEAD_AGENT_NAME = "Lead Agent"
    TEAM_AGENT_NAME = "Specialists"

# Create a single instance to be imported by other modules
config = Config()
