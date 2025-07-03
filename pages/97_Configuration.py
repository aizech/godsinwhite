import streamlit as st
import json
import os
import sys

# Add the parent directory to the path to import config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import config

# Page config
st.set_page_config(
    page_title=f"{config.APP_NAME} - Configuration",
    page_icon=config.APP_ICON,
    layout="wide",
    #initial_sidebar_state="collapsed",
    menu_items=config.MENU_ITEMS
)

# Logo in sidebar
logo_text_path = os.path.join(config.ASSETS_DIR, "logo_text.png")
logo_icon_path = os.path.join(config.ASSETS_DIR, "logo.png")
st.logo(logo_text_path,
    size="large",
    icon_image=logo_icon_path
)


# Agent and tool options
AGENT_OPTIONS = {
    "Calculator": "calculator",
    "Data Analyst": "data_analyst",
    "Python Agent": "python_agent",
    "Research Agent": "research_agent",
    "Investment Agent": "investment_agent",
    "GPTImage1": "gptimage1",
    "Resource Manager": "resource_manager",
    "Task Planner": "task_planner",
    "Project Manager": "project_manager",
    "Airbnb Search": "airbnb",
    "Onlyfy MCP": "onlyfy_mcp",
    "Media Trend Analysis": "media_trend_analysis",
}

# Tool options (example - adjust based on your actual tools)
TOOL_OPTIONS = {
    "Web Search": "web_search",
    "File Operations": "file_ops",
    "Code Execution": "code_exec",
    "Database Access": "db_access",
    "MCP Tools": "mcp_tools",
}

# Preset configurations
DEFAULT_PRESETS = {
    "Speed Offering": {
        "agents": ["project_manager", "task_planner", "resource_manager"],
        "tools": ["web_search", "file_ops"]
    },
    "Data Analysis": {
        "agents": ["data_analyst", "python_agent"],
        "tools": ["db_access", "code_exec"]
    },
    "Travel Planning": {
        "agents": ["airbnb", "research_agent"],
        "tools": ["mcp_tools", "web_search"]
    },
    "Default": {
        "agents": [],
        "tools": []
    }
}

# Load presets from file
def load_presets():
    presets_file = os.path.join(os.path.dirname(__file__), "..", "presets.json")
    if os.path.exists(presets_file):
        with open(presets_file, 'r') as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return DEFAULT_PRESETS
    return DEFAULT_PRESETS

# Save presets to file
def save_presets(presets):
    presets_file = os.path.join(os.path.dirname(__file__), "..", "presets.json")
    with open(presets_file, 'w') as f:
        json.dump(presets, f, indent=2)

# Main function
def main():
    st.title(f"{config.APP_ICON} Agent and Tool Configuration")
    
    # Load presets
    presets = load_presets()
    
    # Create tabs for different configuration sections
    tab1, tab2 = st.tabs(["Presets", "Agent Selection"])
    
    with tab1:
        st.header("Preset Management")
        
        # Select or create preset
        preset_names = list(presets.keys())
        selected_preset = st.selectbox(
            "Select or create a preset",
            preset_names + ["Create New..."]
        )
        
        if selected_preset == "Create New...":
            new_preset_name = st.text_input("New preset name")
            if new_preset_name and new_preset_name not in presets:
                if st.button("Create Preset"):
                    presets[new_preset_name] = {"agents": [], "tools": []}
                    save_presets(presets)
                    st.success(f"Preset '{new_preset_name}' created!")
                    st.rerun()
        
        # Delete preset (if not default)
        if selected_preset != "Create New..." and selected_preset != "Default":
            if st.button("Delete Preset", type="secondary"):
                del presets[selected_preset]
                save_presets(presets)
                st.success(f"Preset '{selected_preset}' deleted!")
                st.rerun()
    
    with tab2:
        if selected_preset != "Create New..." and selected_preset in presets:
            st.header(f"Configure {selected_preset}")
            
            # Agent selection
            st.subheader("Agents")
            agent_columns = st.columns(3)
            selected_agents = []
            
            for i, (agent_name, agent_id) in enumerate(AGENT_OPTIONS.items()):
                with agent_columns[i % 3]:
                    if st.checkbox(
                        agent_name,
                        value=agent_id in presets[selected_preset]["agents"],
                        key=f"agent_{agent_id}"
                    ):
                        selected_agents.append(agent_id)
            
            # Tool selection
            st.subheader("Tools")
            tool_columns = st.columns(2)
            selected_tools = []
            
            for i, (tool_name, tool_id) in enumerate(TOOL_OPTIONS.items()):
                with tool_columns[i % 2]:
                    if st.checkbox(
                        tool_name,
                        value=tool_id in presets[selected_preset].get("tools", []),
                        key=f"tool_{tool_id}"
                    ):
                        selected_tools.append(tool_id)
            
            # Save button
            if st.button("Save Configuration"):
                presets[selected_preset]["agents"] = selected_agents
                presets[selected_preset]["tools"] = selected_tools
                save_presets(presets)
                st.success("Configuration saved!")

if __name__ == "__main__":
    main()

# Footer
st.markdown("---")
st.sidebar.markdown(f"© {config.APP_NAME} | Made with :material/favorite: by [{config.COMPANY}]({config.COMPANY_URL})")
