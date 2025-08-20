import json
import os
import importlib
import inspect
from typing import Any, Dict, List, Optional, Tuple

import streamlit as st
from agno.document import Document
from agno.document.reader import Reader
from agno.document.reader.csv_reader import CSVReader
from agno.document.reader.docx_reader import DocxReader
from agno.document.reader.pdf_reader import PDFReader
from agno.document.reader.text_reader import TextReader
from agno.document.reader.website_reader import WebsiteReader
from agno.memory.v2 import Memory, UserMemory
from agno.team import Team
from agno.utils.log import logger
from halo import HaloConfig, create_halo
from config import config

async def initialize_session_state():
    logger.info(f"---*--- Initializing session state ---*---")
    if "halo" not in st.session_state:
        st.session_state["halo"] = None
    if "session_id" not in st.session_state:
        st.session_state["session_id"] = None
    if "messages" not in st.session_state:
        st.session_state["messages"] = []


import copy

async def add_message(
    role: str,
    content: str,
    tool_calls: Optional[List[Dict[str, Any]]] = None,
    intermediate_steps_displayed: bool = False,
    images: Optional[List[Any]] = None,
) -> None:
    """Safely add a message to the session state"""
    if role == "user":
        logger.info(f"👤  {role}: {content}")
    else:
        logger.info(f"🤖  {role}: {content}")
        
    # Create a deep copy of tool_calls to ensure they're preserved
    preserved_tool_calls = None
    if tool_calls:
        try:
            # Try to create a deep copy of the tool calls
            preserved_tool_calls = copy.deepcopy(tool_calls)
        except Exception as e:
            logger.warning(f"Could not deep copy tool calls: {e}")
            # Fallback: create a simplified representation
            preserved_tool_calls = []
            for tool in tool_calls:
                try:
                    if hasattr(tool, '__dict__'):
                        # For object-like tools
                        tool_copy = {}
                        for key, value in tool.__dict__.items():
                            if isinstance(value, (str, int, float, bool, type(None))):
                                tool_copy[key] = value
                            else:
                                tool_copy[key] = str(value)
                        preserved_tool_calls.append(tool_copy)
                    elif hasattr(tool, 'get') or isinstance(tool, dict):
                        # For dictionary-like tools
                        preserved_tool_calls.append(dict(tool))
                    else:
                        # For other types
                        preserved_tool_calls.append({"name": str(tool)})
                except Exception:
                    # Last resort fallback
                    preserved_tool_calls.append({"name": "Unknown Tool"})
    
    # Add the message with preserved tool calls and images to the session state
    message_data = {
        "role": role,
        "content": content,
        "tool_calls": preserved_tool_calls,
        "intermediate_steps_displayed": intermediate_steps_displayed,
    }
    
    # Add images if provided
    if images:
        message_data["images"] = images
        logger.info(f"Added {len(images)} images to message")
    
    st.session_state["messages"].append(message_data)


async def selected_model() -> str:
    """Get the selected model from configuration or allow override."""
    model_options = {
        "gpt-4o": "openai:gpt-4o",
        "gpt-4o-mini": "openai:gpt-4o-mini",
    }
    
    # Load model configuration
    model_config_file = os.path.join(os.path.dirname(__file__), "model_config.json")
    default_model = "gpt-4o"
    
    if os.path.exists(model_config_file):
        try:
            with open(model_config_file, 'r') as f:
                model_config = json.load(f)
                default_model = model_config.get("default_model", default_model)
        except (json.JSONDecodeError, FileNotFoundError):
            pass
    
    # Use the default model from configuration
    model_id = model_options.get(default_model, model_options["gpt-4o"])
    return model_id


async def selected_tools() -> List[str]:
    """Display a tool selector in the sidebar using toggle switches with presets."""
    tool_options = {
        "File I/O": "file_tools",
        "Shell Access": "shell_tools",
        #"GPTImage1": "gptimage1",
    }
    
    # Load presets
    presets = load_presets()
    selected_preset = st.session_state.get("agent_preset_selector", "Default")
    
    # Get default tools from preset if available
    default_tools = presets.get(selected_preset, {}).get("tools", [])
    
    # Initialize session state for tool toggles if not already present
    if "tool_toggles" not in st.session_state:
        # Set all tools to be enabled by default
        st.session_state.tool_toggles = {
            tool_name: True  # Enable all tools by default
            for tool_name in tool_options.keys()
        }
    
    st.sidebar.markdown(f"# :material/swords: {config.LEAD_AGENT_NAME} Tools")
    
    # Create a toggle for each tool
    selected_tools = []
    for tool_name, tool_id in tool_options.items():
        # Use a unique key for each toggle with a tool_ prefix
        toggle_key = f"tool_toggle_{tool_id}"
        
        # Get default value from session state or preset
        default_value = st.session_state.tool_toggles.get(tool_name, tool_id in default_tools)
        
        # Create the toggle switch with consistent styling
        is_enabled = st.sidebar.toggle(
            tool_name,
            value=default_value,
            key=toggle_key,
            help=f"Toggle {tool_name} tool"
        )
        
        # Update session state
        st.session_state.tool_toggles[tool_name] = is_enabled
        
        # Add to selected tools if enabled
        if is_enabled:
            selected_tools.append(tool_id)
    
    return selected_tools


def load_presets():
    """Load agent presets from presets.json"""
    import json
    import os
    
    presets_file = os.path.join(os.path.dirname(__file__), "presets.json")
    if os.path.exists(presets_file):
        with open(presets_file, 'r') as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return {}
    return {}


async def selected_agents() -> List[str]:
    st.sidebar.markdown(f"# :material/co_present: {config.TEAM_AGENT_NAME}")

    """Display a selector for agents in the sidebar using toggle switches with presets."""
    # Dynamically discover available agents from the agents directory
    agent_options = discover_available_agents()
    
    # Define tool options at the top level of the function
    tool_options = {
        "File I/O": "file_tools",
        "Shell Access": "shell_tools",
    }
    
    # Load presets
    presets = load_presets()
    preset_names = ["Default"] + [p for p in presets.keys() if p != "Default"]
    
    # Add some custom CSS for better visual feedback
    #st.sidebar.markdown("""
    #<style>
    #    .preset-header {
    #        display: flex;
    #        align-items: center;
    #        justify-content: space-between;
    #        margin-bottom: 0.5rem;
    #    }
    #    .active-preset {
    #        background-color: #f0f2f6;
    #        padding: 0.5rem;
    #        border-radius: 0.5rem;
    #        font-weight: 600;
    #        margin-bottom: 1rem;
    #        border-left: 4px solid #4CAF50;
    #    }
    #</style>
    #""", unsafe_allow_html=True)
    
    # Preset selector in sidebar with immediate effect
    #st.sidebar.markdown("<div class='preset-header'><h3>Agent Preset</h3></div>", unsafe_allow_html=True)
    
    # Add a callback to update toggles when preset changes
    def update_toggles():
        nonlocal agent_options, tool_options
        selected_preset = st.session_state.agent_preset_selector
        if selected_preset == "Default":
            return  # Don't update toggles for Default preset
            
        default_agents = presets.get(selected_preset, {}).get("agents", [])
        default_tools = presets.get(selected_preset, {}).get("tools", [])
        
        # Update agent toggles
        for agent_name, agent_id in agent_options.items():
            st.session_state.agent_toggles[agent_name] = agent_id in default_agents
        
        # Update tool toggles
        for tool_name, tool_id in tool_options.items():
            st.session_state.tool_toggles[tool_name] = tool_id in default_tools
    
    # Store the previous preset to detect changes
    if 'previous_preset' not in st.session_state:
        st.session_state.previous_preset = None
    
    selected_preset = st.sidebar.selectbox(
        "Select a preset",
        preset_names,
        key="agent_preset_selector",
        index=0,  # Default to first preset
        on_change=update_toggles,
        label_visibility="collapsed"
    )
    
    # Show current active preset with visual feedback
    #st.sidebar.markdown(f"<div class='active-preset'>Active: {selected_preset}</div>", unsafe_allow_html=True)
    
    # Force update toggles if preset has changed
    #if st.session_state.previous_preset != selected_preset:
    #    update_toggles()
    #    st.session_state.previous_preset = selected_preset
    #    st.rerun()  # Rerun to ensure UI updates
    
    # Get default agents from preset if available
    default_agents = presets.get(selected_preset, {}).get("agents", [])
    
    # Initialize session state for agent toggles if not already present
    if "agent_toggles" not in st.session_state:
        # Set all agents to be enabled by default
        st.session_state.agent_toggles = {
            agent_name: True  # Enable all agents by default
            for agent_name in agent_options.keys()
        }
    
    
    # Create a toggle for each agent
    selected_agents = []
    for agent_name, agent_id in agent_options.items():
        # Use a unique key for each toggle with an agent_ prefix
        toggle_key = f"agent_toggle_{agent_id}"
        
        # Get default value from session state or preset
        default_value = st.session_state.agent_toggles.get(agent_name, agent_id in default_agents)
        
        # Create the toggle switch with consistent styling
        is_enabled = st.sidebar.toggle(
            agent_name,
            value=default_value,
            key=toggle_key,
            help=f"Toggle {agent_name} agent"
        )
        
        # Update session state
        st.session_state.agent_toggles[agent_name] = is_enabled
        
        # Add to selected agents if enabled
        if is_enabled:
            selected_agents.append(agent_id)
    
    return selected_agents


async def show_user_memories(halo_memory: Memory, user_id: str) -> None:
    """Show use memories in a streamlit container."""

    with st.container():
        user_memories = halo_memory.get_user_memories(user_id=user_id)
        with st.expander(f"💭 Memories for {user_id}", expanded=False):
            if len(user_memories) > 0:
                # Initialize session state for memory selection
                if "selected_memories" not in st.session_state:
                    st.session_state.selected_memories = {}
                
                # Create a dataframe from the memories with checkbox column
                memory_data = {
                    "Select": [st.session_state.selected_memories.get(i, False) for i in range(len(user_memories))],
                    "Memory": [memory.memory for memory in user_memories],
                    "Topics": [
                        ", ".join(memory.topics) if memory.topics else ""
                        for memory in user_memories
                    ],
                    "Last Updated": [
                        memory.last_updated.strftime("%Y-%m-%d %H:%M")
                        if memory.last_updated
                        else ""
                        for memory in user_memories
                    ],
                }

                # Display as an editable table with checkbox column
                edited_data = st.data_editor(
                    memory_data,
                    use_container_width=True,
                    column_config={
                        "Select": st.column_config.CheckboxColumn("Select", width="small"),
                        "Memory": st.column_config.TextColumn("Memory", width="medium", disabled=True),
                        "Topics": st.column_config.TextColumn("Topics", width="small", disabled=True),
                        "Last Updated": st.column_config.TextColumn(
                            "Last Updated", width="small", disabled=True
                        ),
                    },
                    hide_index=True,
                    key="memory_editor"
                )
                
                # Update session state with checkbox selections
                for i, selected in enumerate(edited_data["Select"]):
                    st.session_state.selected_memories[i] = selected
                
                # Count selected memories
                selected_count = sum(edited_data["Select"])
                
                # Show selection info
                if selected_count > 0:
                    st.info(f"{selected_count} memory/memories selected")
                
            else:
                st.info("No memories found, tell me about yourself!")
                selected_count = 0

            # Button layout - add delete button if memories are selected
            if len(user_memories) > 0 and selected_count > 0:
                col1, col2, col3 = st.columns([0.33, 0.33, 0.34])
            else:
                col1, col2 = st.columns([0.5, 0.5])
                col3 = None
            
            with col1:
                if st.button("Clear all memories", key="clear_all_memories"):
                    await add_message("user", "Clear all my memories")
                    if "memory_refresh_count" not in st.session_state:
                        st.session_state.memory_refresh_count = 0
                    st.session_state.memory_refresh_count += 1
            
            with col2:
                if st.button("Refresh memories", key="refresh_memories"):
                    if "memory_refresh_count" not in st.session_state:
                        st.session_state.memory_refresh_count = 0
                    st.session_state.memory_refresh_count += 1
            
            # Delete selected memories button
            if col3 is not None:
                with col3:
                    # Create two sub-columns for the delete buttons
                    subcol1, subcol2 = st.columns([0.5, 0.5])
                    with subcol2:
                        st.markdown(" ")
                    
                    #with subcol1:
                    #    if st.button(f"Forget ({selected_count})", key="delete_selected_memories", type="secondary", help="Send delete request to HALO"):
                    #        # Get selected memory indices
                    #        selected_indices = [i for i, selected in enumerate(edited_data["Select"]) if selected]
                    #        
                    #        if selected_indices:
                    #            # Create delete message with selected memories
                    #            selected_memories_text = []
                    #            for idx in selected_indices:
                    #                if idx < len(user_memories):
                    #                    memory_preview = user_memories[idx].memory[:100] + "..." if len(user_memories[idx].memory) > 100 else user_memories[idx].memory
                    #                    selected_memories_text.append(f"- {memory_preview}")
                    #            
                    #            delete_message = f"Update the following memories, that the user dislikes them:\n" + "\n".join(selected_memories_text)
                    #            await add_message("user", delete_message)
                    #            
                    #            # Clear selection state
                    #            st.session_state.selected_memories = {}
                    #            
                    #            # Trigger refresh
                    #            if "memory_refresh_count" not in st.session_state:
                    #                st.session_state.memory_refresh_count = 0
                    #            st.session_state.memory_refresh_count += 1
                    
                    with subcol2:
                        if st.button(f"Erase ({selected_count})", key="erase_selected_memories", type="primary", help="Directly erase from memory"):
                            # Get selected memory indices
                            selected_indices = [i for i, selected in enumerate(edited_data["Select"]) if selected]
                            
                            if selected_indices:
                                # Directly delete memories from halo_memory using their IDs
                                deleted_count = 0
                                failed_deletions = []
                                
                                for idx in selected_indices:
                                    if idx < len(user_memories):
                                        try:
                                            memory_to_delete = user_memories[idx]
                                            # Use the memory_id to delete directly from halo_memory
                                            if memory_to_delete.memory_id:
                                                halo_memory.delete_user_memory(
                                                    memory_id=memory_to_delete.memory_id,
                                                    user_id=user_id,
                                                    refresh_from_db=False  # We'll refresh once at the end
                                                )
                                                deleted_count += 1
                                            else:
                                                logger.warning(f"Memory at index {idx} has no memory_id")
                                                failed_deletions.append(f"Memory {idx + 1} (no ID)")
                                        except Exception as e:
                                            memory_id = getattr(memory_to_delete, 'memory_id', 'unknown')
                                            logger.error(f"Failed to delete memory {memory_id}: {e}")
                                            failed_deletions.append(f"Memory {idx + 1}")
                                
                                # Show results
                                if deleted_count > 0:
                                    st.success(f"Successfully erased {deleted_count} memory/memories")
                                
                                if failed_deletions:
                                    st.error(f"Failed to erase: {', '.join(failed_deletions)}")
                                
                                # Clear selection state
                                st.session_state.selected_memories = {}
                                
                                # Trigger refresh to reload the memory list
                                if "memory_refresh_count" not in st.session_state:
                                    st.session_state.memory_refresh_count = 0
                                st.session_state.memory_refresh_count += 1
                                
                                # Force page refresh to show updated memory list
                                st.rerun()


async def example_inputs() -> None:
    """Show example inputs on the sidebar."""
    with st.sidebar:
        st.markdown("# :material/wand_stars: Try me!")
        if st.button("Diabetes Risk Assessment"):
            await add_message(
                "user",
                "Calculate the 10-year risk of developing diabetes for a 45-year-old male with a BMI of 28.5 and a family history of diabetes.",
            )

        if st.button("Medical Text Analysis"):
            await add_message(
                "user",
                "Analyze the given medical text and extract the diagnosis, symptoms, and treatment: \"Patient presents with fever, headache, and fatigue. Blood test reveals high white blood cell count.\"",
            )

        if st.button("Medication Side Effects Analysis"):
            await add_message(
                "user",
                "Analyze the side effects of the following medications: Aspirin, Metformin, and Lisinopril. Provide a list of potential side effects and their likelihood.",
            )

        if st.button("Symptom Checker"):
            await add_message(
                "user",
                "I have a fever, headache, and fatigue. What are the possible causes and recommended treatments?",
            )

        if st.button("Medical Imaging Analysis"):
            await add_message(
                "user",
                "Analyze the given MRI image and detect any abnormalities: https://github.com/aizech/godsinwhite/tree/main/demo_data/medical_image_test.dcm",
            )

        if st.button("Medical Literature Search"):
            await add_message(
                "user",
                "Find the top 5 most relevant medical research papers on the topic of \"Artificial Intelligence in Healthcare\" published in the last 6 months. Provide the links to the papers.",
            )

        if st.button("Medical Diagnosis"):
            await add_message(
                "user",
                "I have a cough, fever, and chest pain. What is the most likely diagnosis and recommended treatment?",
            )

        if st.button("Medical Diagnosis with Medical History"):
            await add_message(
                "user",
                "What is the medical diagnosis for this medical history document: https://github.com/aizech/godsinwhite/tree/main/demo_data/medical_history.txt",
            )

async def about():
    """Show information about in the sidebar"""
    with st.sidebar:
        st.markdown("# :material/help: Need Help?")
        st.markdown(
            f"If you have any questions, catch us on our [Support Page]({config.SUPPORT_URL})."
        )


def is_json(myjson):
    """Check if a string is valid JSON"""
    try:
        json.loads(myjson)
    except (ValueError, TypeError):
        return False
    return True


def display_tool_calls(tool_calls_container, tools):
    """Display tool calls in a streamlit container with expandable sections.

    Args:
        tool_calls_container: Streamlit container to display the tool calls
        tools: List of tool call dictionaries containing name, args, content, and metrics
    """
    # Early return if tools is None to prevent errors
    if tools is None:
        logger.debug("No tools provided to display_tool_calls")
        return
        
    # Ensure we have a valid container
    if tool_calls_container is None:
        logger.warning("No container provided to display_tool_calls")
        return
        
    try:
        with tool_calls_container.container():
            # Handle single tool_call dict case and other possible formats
            if isinstance(tools, dict):
                tools = [tools]
            elif isinstance(tools, (str, int, float, bool)):
                # Handle primitive types by wrapping them in a simple structure
                tools = [{"name": "Tool Call", "content": str(tools)}]
            elif not isinstance(tools, list):
                # Try to convert to list if it's an iterable
                try:
                    tools = list(tools)
                except (TypeError, ValueError):
                    logger.warning(
                        f"Unexpected tools format: {type(tools)}. Skipping display."
                    )
                    return
                    
            # Skip if empty list
            if not tools:
                logger.debug("Empty tools list provided to display_tool_calls")
                return

            for tool_call in tools:
                # Initialize default values
                tool_name = "Unknown Tool"
                tool_args = {}
                content = None
                metrics = None
                
                try:
                    # Normalize access to tool details based on object type
                    if tool_call is None:
                        continue
                        
                    if hasattr(tool_call, 'get'):
                        # Old style: dictionary-like object with get method
                        tool_name = tool_call.get("tool_name") or tool_call.get(
                            "name", "Unknown Tool"
                        )
                        tool_args = tool_call.get("tool_args") or tool_call.get("args", {})
                        content = tool_call.get("content", None)
                        metrics = tool_call.get("metrics", None)
                    else:
                        # New style: ToolExecution object in Agno 1.5.5
                        tool_name = getattr(tool_call, "tool_name", None) or getattr(
                            tool_call, "name", "Unknown Tool"
                        )
                        tool_args = getattr(tool_call, "tool_args", None) or getattr(
                            tool_call, "args", {}
                        )
                        content = getattr(tool_call, "content", None)
                        metrics = getattr(tool_call, "metrics", None)
                        
                    # Ensure tool_name is a string
                    if tool_name is None:
                        tool_name = "Unknown Tool"
                    tool_name = str(tool_name)
                except Exception as e:
                    logger.error(f"Error extracting tool details: {str(e)}")
                    # Continue with default values set above

                # Add timing information safely
                execution_time_str = "N/A"
                try:
                    if metrics is not None:
                        # Handle both object and dictionary metrics
                        if hasattr(metrics, "time"):
                            execution_time = metrics.time
                            if execution_time is not None:
                                execution_time_str = f"{execution_time:.4f}s"
                        elif isinstance(metrics, dict) and "time" in metrics:
                            execution_time = metrics["time"]
                            if execution_time is not None:
                                execution_time_str = f"{execution_time:.4f}s"
                except Exception as e:
                    logger.error(f"Error getting tool metrics time: {str(e)}")
                    # Keep default "N/A"

                # Check if this is a transfer task or memory task with more robust detection
                try:
                    # Convert tool_name to string if it's not already to prevent attribute errors
                    tool_name_str = str(tool_name).lower() if tool_name is not None else ""
                    
                    # More robust pattern matching for different tool types
                    is_task_transfer = any(transfer_term in tool_name_str for transfer_term in [
                        "transfer_task", "delegate", "assign_to", "handoff", "task_to_member"
                    ])
                    
                    is_memory_task = any(memory_term in tool_name_str for memory_term in [
                        "user_memory", "memory", "remember", "recall", "store_memory"
                    ])
                    
                    # Default expander title
                    expander_title = ":material/construction:"
                    
                    if is_task_transfer:
                        # Handle both dictionary and object access for tool_args with better error handling
                        member_id = "Unknown Member"
                        try:
                            if hasattr(tool_args, 'get'):
                                member_id = tool_args.get("member_id", "")
                                if not member_id:
                                    # Try alternative keys
                                    member_id = (tool_args.get("agent_id") or 
                                                tool_args.get("agent") or 
                                                tool_args.get("member") or 
                                                "Unknown Member")
                            else:
                                member_id = getattr(tool_args, "member_id", "")
                                if not member_id:
                                    # Try alternative attributes
                                    member_id = (getattr(tool_args, "agent_id", None) or 
                                                getattr(tool_args, "agent", None) or 
                                                getattr(tool_args, "member", None) or 
                                                "Unknown Member")
                        except Exception as e:
                            logger.debug(f"Error getting member_id: {e}")
                            member_id = "Unknown Member"
                            
                        # Ensure member_id is a string and properly formatted
                        member_id = str(member_id).replace("_", " ").title()
                        expander_title = f":material/smart_toy: {member_id}"
                    elif is_memory_task:
                        expander_title = f":material/network_intelligence_update: Updating Memory"
                    else:
                        # Format the tool name for better readability
                        formatted_tool_name = tool_name_str.replace("_", " ").title()
                        expander_title = f":material/construction: {formatted_tool_name}"
                except Exception as e:
                    logger.debug(f"Error determining tool type: {e}")
                    # Fallback to a generic title with the raw tool name
                    expander_title = f":material/construction: Tool Call"

                if execution_time_str != "N/A":
                    expander_title += f" ({execution_time_str})"

                try:
                    with st.expander(
                        expander_title,
                        expanded=False,
                    ):
                        try:
                            # Show query/code/command with syntax highlighting with better error handling
                            if tool_args is not None:
                                # Handle dictionary-like tool_args
                                if isinstance(tool_args, dict):
                                    # Check for special keys with robust error handling
                                    for key, lang in [("query", "sql"), ("code", "python"), ("command", "bash")]:
                                        if key in tool_args and tool_args[key] is not None:
                                            try:
                                                st.code(str(tool_args[key]), language=lang)
                                                break  # Only show one code block if multiple are present
                                            except Exception as e:
                                                logger.debug(f"Error displaying {key}: {e}")
                                                st.error(f"Could not display {key} content.")
                                
                                # Handle object-like tool_args
                                elif hasattr(tool_args, "__dict__"):
                                    for key, lang in [("query", "sql"), ("code", "python"), ("command", "bash")]:
                                        if hasattr(tool_args, key) and getattr(tool_args, key) is not None:
                                            try:
                                                value = getattr(tool_args, key)
                                                if value:  # Check if not empty
                                                    st.code(str(value), language=lang)
                                                    break  # Only show one code block if multiple are present
                                            except Exception as e:
                                                logger.debug(f"Error displaying {key}: {e}")
                                                st.error(f"Could not display {key} content.")
                        except Exception as e:
                            logger.debug(f"Error displaying code/query/command: {e}")
                        
                        # Display arguments with improved error handling
                        try:
                            args_to_show = {}
                            
                            # Extract arguments based on tool_args type
                            if isinstance(tool_args, dict):
                                args_to_show = {
                                    k: v
                                    for k, v in tool_args.items()
                                    if k not in ["query", "code", "command"] and v is not None
                                }
                            elif hasattr(tool_args, "__dict__"):
                                args_to_show = {
                                    k: v
                                    for k, v in tool_args.__dict__.items()
                                    if k not in ["query", "code", "command"] and v is not None
                                }
                            elif tool_args is not None:
                                # For other types, try to create a simple representation
                                args_to_show = {"value": str(tool_args)}
                                
                            # Display arguments if they exist
                            if args_to_show:
                                st.markdown("**Arguments:**")
                                try:
                                    # Try to convert to JSON-serializable format
                                    import json
                                    # Test if serializable
                                    json.dumps(args_to_show)
                                    st.json(args_to_show)
                                except (TypeError, ValueError, OverflowError):
                                    # Fallback for non-serializable args
                                    st.write(str(args_to_show))
                        except Exception as e:
                            logger.debug(f"Error displaying tool arguments: {e}")
                            st.error("Could not display tool arguments.")

                        # Display content/results with improved error handling
                        if content is not None:
                            try:
                                st.markdown("**Results:**")
                                
                                # Handle different content types
                                if isinstance(content, str):
                                    if is_json(content):
                                        try:
                                            parsed_json = json.loads(content)
                                            st.json(parsed_json)
                                        except Exception:
                                            st.code(content, language="json")
                                    elif content.strip().startswith("<html") or content.strip().startswith("<!DOCTYPE"):
                                        st.code(content, language="html")
                                    elif len(content) > 1000:
                                        # For very long content, use a scrollable code block
                                        st.code(content)
                                    else:
                                        # Regular text content
                                        st.write(content)
                                elif isinstance(content, (dict, list)):
                                    # Handle dictionary and list content
                                    try:
                                        st.json(content)
                                    except Exception:
                                        st.write(str(content))
                                else:
                                    # Handle other content types
                                    st.write(str(content))
                            except Exception as e:
                                logger.debug(f"Could not display tool content: {e}")
                                st.error("Could not display tool results.")
                except (Exception, RuntimeError) as e:
                    # Handle both general exceptions and Streamlit runtime errors
                    if isinstance(e, RuntimeError) and "This Streamlit app is no longer running" in str(e):
                        logger.debug("Streamlit app no longer running, skipping display")
                    else:
                        logger.error(f"Error displaying tool call: {str(e)}")
                        # Fallback minimal display if expander fails
                        st.error(f"Tool call: {tool_name} (display error)")
                        
                # Add a small separator between tool calls for better readability
                st.markdown("")
                
    except Exception as e:
        logger.error(f"Error displaying tool calls: {str(e)}")
        tool_calls_container.error("Failed to display tool results")


async def knowledge_widget(halo: Team) -> None:
    """Display a knowledge widget in the sidebar."""
    st.sidebar.markdown("# :material/network_intel_node: Knowledge")
    if halo is not None and halo.knowledge is not None:
        # Add websites to knowledge base
        if "url_scrape_key" not in st.session_state:
            st.session_state["url_scrape_key"] = 0
        input_url = st.sidebar.text_input(
            "Add URL to Knowledge Base",
            type="default",
            key=st.session_state["url_scrape_key"],
        )
        add_url_button = st.sidebar.button("Add URL")
        if add_url_button:
            if input_url is not None:
                alert = st.sidebar.info("Processing URLs...", icon="ℹ️")
                if f"{input_url}_scraped" not in st.session_state:
                    scraper = WebsiteReader(max_links=2, max_depth=1)
                    web_documents: List[Document] = scraper.read(input_url)
                    if web_documents:
                        halo.knowledge.load_documents(web_documents, upsert=True)
                    else:
                        st.sidebar.error("Could not read website")
                    st.session_state[f"{input_url}_uploaded"] = True
                alert.empty()

        # Add documents to knowledge base
        if "file_uploader_key" not in st.session_state:
            st.session_state["file_uploader_key"] = 100
        uploaded_file = st.sidebar.file_uploader(
            "Add a Document (.pdf, .csv, .txt, or .docx)",
            key=st.session_state["file_uploader_key"],
        )
        if uploaded_file is not None:
            alert = st.sidebar.info("Processing document...", icon="🧠")
            document_name = uploaded_file.name.split(".")[0]
            if f"{document_name}_uploaded" not in st.session_state:
                file_type = uploaded_file.name.split(".")[-1].lower()

                reader: Reader
                if file_type == "pdf":
                    reader = PDFReader()
                elif file_type == "csv":
                    reader = CSVReader()
                elif file_type == "txt":
                    reader = TextReader()
                elif file_type == "docx":
                    reader = DocxReader()
                else:
                    st.sidebar.error("Unsupported file type")
                    return
                uploaded_file_documents: List[Document] = reader.read(uploaded_file)
                if uploaded_file_documents:
                    halo.knowledge.load_documents(uploaded_file_documents, upsert=True)
                else:
                    st.sidebar.error("Could not read document")
                st.session_state[f"{document_name}_uploaded"] = True
            alert.empty()

        # Load and delete knowledge
        if st.sidebar.button(":material/delete: Delete Knowledge"):
            halo.knowledge.delete()
            st.sidebar.success("Knowledge deleted!")


async def session_selector(halo: Team, halo_config: HaloConfig) -> None:
    """Display a session selector in the sidebar, if a new session is selected, HALO is restarted with the new session."""

    if not halo.storage:
        return

    try:
        # Get all agent sessions.
        halo_sessions = halo.storage.get_all_sessions()
        if not halo_sessions:
            st.sidebar.info("No saved sessions found.")
            return

        # Get session names if available, otherwise use IDs.
        sessions_list = []
        for session in halo_sessions:
            session_id = session.session_id
            session_name = (
                session.session_data.get("session_name", None)
                if session.session_data
                else None
            )
            display_name = session_name if session_name else session_id
            sessions_list.append({"id": session_id, "display_name": display_name})

        # Display session selector.
        st.sidebar.markdown("# :material/chat: Session")
        selected_session = st.sidebar.selectbox(
            "Session",
            options=[s["display_name"] for s in sessions_list],
            key="session_selector",
            label_visibility="collapsed",
        )
        # Find the selected session ID.
        selected_session_id = next(
            s["id"] for s in sessions_list if s["display_name"] == selected_session
        )
        # Update the agent session if it has changed.
        if st.session_state["session_id"] != selected_session_id:
            logger.info(f"---*--- Loading HALO session: {selected_session_id} ---*---")
            st.session_state["halo"] = create_halo(
                config=halo_config,
                session_id=selected_session_id,
            )
            st.rerun()

        # Show the rename session widget.
        container = st.sidebar.container()
        session_row = container.columns([3, 1], vertical_alignment="center")

        # Initialize session_edit_mode if needed.
        if "session_edit_mode" not in st.session_state:
            st.session_state.session_edit_mode = False

        # Show the session name.
        with session_row[0]:
            if st.session_state.session_edit_mode:
                new_session_name = st.text_input(
                    "Session Name",
                    value=halo.session_name,
                    key="session_name_input",
                    label_visibility="collapsed",
                )
            else:
                st.markdown(f"Session Name: **{halo.session_name}**")

        # Show the rename session button.
        with session_row[1]:
            if st.session_state.session_edit_mode:
                if st.button("✓", key="save_session_name", type="primary"):
                    if new_session_name:
                        halo.rename_session(new_session_name)
                        st.session_state.session_edit_mode = False
                        container.success("Renamed!")
                        # Trigger a rerun to refresh the sessions list
                        st.rerun()
            else:
                if st.button("✎", key="edit_session_name"):
                    st.session_state.session_edit_mode = True
    except Exception as e:
        logger.error(f"Error in session selector: {str(e)}")
        st.sidebar.error("Failed to load sessions")


def export_chat_history():
    """Export chat history in markdown format.

    Returns:
        str: Formatted markdown string of the chat history
    """
    if "messages" not in st.session_state or not st.session_state["messages"]:
        return f"# HALO - Chat History\n\nNo messages to export."

    chat_text = f"# HALO - Chat History\n\n"
    for msg in st.session_state["messages"]:
        role_label = "🤖 Assistant" if msg["role"] == "assistant" else "👤 User"
        chat_text += f"### {role_label}\n{msg['content']}\n\n"

        # Include tool calls if present
        if msg.get("tool_calls"):
            chat_text += "#### Tool Calls:\n"
            for i, tool_call in enumerate(msg["tool_calls"]):
                # Handle both dictionary-like objects and ToolExecution objects
                if hasattr(tool_call, 'get'):
                    # Old style: dictionary-like object with get method
                    tool_name = tool_call.get("name", "Unknown Tool")
                    arguments = tool_call.get("arguments", "")
                    content = tool_call.get("content", "")
                else:
                    # New style: ToolExecution object in Agno 1.5.5
                    tool_name = getattr(tool_call, "name", "Unknown Tool")
                    arguments = getattr(tool_call, "arguments", "")
                    content = getattr(tool_call, "content", "")
                
                chat_text += f"**{i + 1}. {tool_name}**\n\n"
                if arguments:
                    chat_text += f"Arguments: ```json\n{arguments}\n```\n\n"
                if content:
                    chat_text += f"Results: ```\n{content}\n```\n\n"

    return chat_text


async def utilities_widget(halo: Team) -> None:
    """Display a utilities widget in the sidebar."""
    st.sidebar.markdown("# :material/construction: Utilities")
    col1, col2 = st.sidebar.columns(2)
    with col1:
        if st.button(":material/edit_square: New Chat"):
            restart_halo()
    with col2:
        fn = f"halo_chat_history.md"
        if "session_id" in st.session_state:
            fn = f"halo_{st.session_state['session_id']}.md"
        if st.download_button(
            ":material/download: Export Chat",
            export_chat_history(),
            file_name=fn,
            mime="text/markdown",
        ):
            st.sidebar.success("Chat history exported!")


def restart_halo():
    logger.debug("---*--- Restarting HALO ---*---")
    st.session_state["halo"] = None
    st.session_state["session_id"] = None
    st.session_state["messages"] = []
    if "url_scrape_key" in st.session_state:
        st.session_state["url_scrape_key"] += 1
    if "file_uploader_key" in st.session_state:
        st.session_state["file_uploader_key"] += 1
    st.rerun()


def discover_available_agents() -> Dict[str, str]:
    """
    Dynamically discover available agents from the agents directory.
    
    Returns:
        Dict[str, str]: Dictionary mapping display names to agent IDs
    """
    agent_options = {}
    
    # Get the agents directory path
    agents_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "agents")
    
    # Find all potential agent modules (files ending with _agent.py)
    for filename in os.listdir(agents_dir):
        if filename.endswith('_agent.py') and filename != '__init__.py':
            module_name = filename[:-3]  # Remove .py extension
            
            # Skip commented out modules
            if module_name == 'crawler_agent':
                continue
                
            try:
                # Import the module
                module = importlib.import_module(f'agents.{module_name}')
                
                # Find factory functions (those starting with create_)
                for name, obj in inspect.getmembers(module):
                    if name.startswith('create_') and inspect.isfunction(obj):
                        # Extract agent name from function name (remove 'create_' and '_agent' if present)
                        agent_id = name.replace('create_', '', 1)
                        if agent_id.endswith('_agent'):
                            agent_id = agent_id[:-6]
                        
                        # Create a display name (convert snake_case to Title Case)
                        display_name = ' '.join(word.capitalize() for word in agent_id.split('_'))
                        
                        # Special case for gptimage1
                        if agent_id == 'gptimage1':
                            display_name = 'Image Agent'
                            
                        # Add to agent options
                        agent_options[display_name] = agent_id
            except ImportError as e:
                logger.warning(f"Could not import agent module {module_name}: {e}")
    
    return agent_options
