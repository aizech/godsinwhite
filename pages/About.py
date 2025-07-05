"""
About Page
This page provides information about the GodsinWhite Agent Interface.
"""

import os
import streamlit as st
import sys
import datetime

# Add the parent directory to the path to import config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import config

# Set page config
st.set_page_config(
    page_title=f"{config.APP_NAME} - About",
    page_icon="ℹ️",
    layout="wide",
)

# Logo in sidebar
st.logo(config.LOGO_TEXT_PATH,
    size="large",
    icon_image=config.LOGO_ICON_PATH
)

# Page title
one_cola = st.columns([1])[0]
with one_cola:
    col1a, col2a = st.columns([2, 6])

    with col1a:
        team_image = config.LOGO_TEAM_PATH
        st.image(team_image, width=400)
    with col2a:
        st.markdown("""
        # Welcome to GodsinWhite  
        With GodsinWhite, we are committed to making AI accessible and useful for everyone. We believe that AI should be a tool for everyone, not just a luxury for the wealthy. GodsinWhite is a platform for creating, assembling and reusing AI-Agents and Tools specically for medical purposes.
        """, unsafe_allow_html=True)

height = 50
st.markdown(f'<div style="height: {height}px;"></div>', unsafe_allow_html=True)

# --- Content ---
st.markdown("""
## :material/potted_plant: Mission

We will create an AI-Multi-Agent-Framework for an AI-Fabric with reusable AI-Agents and reusable Tools. 
And we will develop a Creation Tool for creating, assembling and reusing AI-Agents and Tools.

## :material/rocket_launch: Our Mission
We believe that the future of work lies in the collaboration between humans and machines. Our AI platform and agents are designed to optimize business processes, scale automation, and relieve teams so they can focus on strategic decisions.

## :material/star: Our Vision
We strive to fundamentally change the way how Bertrandt works. By leveraging our innovative AI platform technologies, we aim to increase productivity and maximize efficiency. We shape the future of humans and AI.

## :material/settings_heart: Our Technology
We offer a flexible and customizable AI infrastructure. Our agents and tools are individually designed and can be seamlessly integrated into existing ecosystems. Whether for small businesses or large corporations, we have the right solution for every challenge. Our AI platform is built as a self-learning system. The system learns itself with every project, process, agency, agent and tools we create. Therefore, our innovative platform is extremely flexible, scalable and secure for enterprise usage.

## :material/favorite: Our Founder 
#### Bernhard Zechmann (Founder of GodsinWhite, Watunga.ai and Corpus Analytica)
Bernhard Zechmann is the founder of Corpus Analytica and Watunga.AI. 
In addition to his entrepreneurial ventures, he serves as the Vice President IT at Bertrandt AG, where he focuses on shaping and developing corporate IT strategies and operation with his team of about 170 IT professionals.

His expertise spans several key areas:
- **IT Engineer**: He is passionate about IT strategy, IT technologies, IT management, organization, methods, processes, platforms, programming, cybersecurity, digitalization, and digital transformation.
- **Software Engineer**: He has been creating homepages since 1994. He has worked on various Open Source projects for CMS systems like Mambo, Joomla, Magento, and Typo3, and is now focused on WordPress, programming plugins and applications. He is familiar with many new programming tools.
- **Digital Health Engineer**: Since 2022, he has been programming software in the medical field. He further developed functions for the SaaS platform Corpus Analytica through Radiologic-Reviews.com.
- **AI Engineer**: His engagement with Artificial Intelligence (AI) dates back to his study of neural networks in 1996. Since 2019, he has intensified his focus on AI, including Transformers, programming, concepts, methods, and Multi-Agent-Frameworks. This work led to the creation of watunga.ai, described as one of the most modern AI Multi-Agent Frameworks.

""")

height = 50
st.markdown(f'<div style="height: {height}px;"></div>', unsafe_allow_html=True)

