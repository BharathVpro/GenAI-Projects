"""
Results Viewer Module
Handles the display of extraction results and analytics
"""

import streamlit as st
import json

def render_analytics_summary():
    """Render the analytics summary section"""
    st.subheader("📊 Analysis Summary")
    
    analytics = st.session_state.analytics
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Entities", f"{analytics['total_entities']:,}")
    with col2:
        st.metric("Text Length", f"{analytics['text_length']:,} chars")
    with col3:
        st.metric("Unique Characters", len(analytics['characters']))
    with col4:
        st.metric("Entity Types", len(analytics['entity_counts']))
    
    # Top Characters
    st.markdown("### 👥 Top Characters by Mentions")
    char_cols = st.columns(5)
    for idx, (char_name, char_data) in enumerate(analytics['top_characters'][:5]):
        with char_cols[idx]:
            st.metric(char_name, char_data['count'])
            if char_data['attributes']:
                attrs_preview = list(char_data['attributes'])[:2]
                for attr in attrs_preview:
                    st.caption(attr)

def render_visual_tab():
    """Render the visual view tab"""
    st.markdown("### Interactive Visualization")
    st.components.v1.html(st.session_state.html_content, height=600, scrolling=True)
    
    col1, col2, col3 = st.columns([3, 1, 3])
    with col2:
        st.download_button(
            label="⬇️ Download HTML",
            data=st.session_state.html_content,
            file_name="langextract_visualization.html",
            mime="text/html",
            use_container_width=True
        )

def render_json_tab():
    """Render the JSON data tab"""
    st.markdown("### Extracted Data (JSON)")
    
    for i, doc in enumerate(st.session_state.json_data):
        with st.expander(f"Document {i+1}", expanded=False):
            st.json(doc)
    
    col1, col2, col3 = st.columns([3, 1, 3])
    with col2:
        json_str = json.dumps(st.session_state.json_data, indent=2)
        st.download_button(
            label="⬇️ Download JSON",
            data=json_str,
            file_name="langextract_data.json",
            mime="application/json",
            use_container_width=True
        )

def render_character_analysis_tab():
    """Render the character analysis tab"""
    st.markdown("### Character Analysis")
    
    # Character details table
    all_chars = sorted(st.session_state.analytics['characters'].items(), 
                      key=lambda x: x[1]["count"], reverse=True)
    
    for char_name, char_data in all_chars[:20]:  # Show top 20
        with st.expander(f"{char_name} - {char_data['count']} mentions"):
            if char_data['attributes']:
                st.markdown("**Attributes:**")
                for attr in sorted(char_data['attributes']):
                    st.write(f"• {attr}")
            else:
                st.write("No attributes found")

def render_entity_breakdown_tab():
    """Render the entity breakdown tab"""
    st.markdown("### Entity Type Breakdown")
    
    # Create a bar chart using columns
    for entity_type, count in sorted(st.session_state.analytics['entity_counts'].items(), 
                                   key=lambda x: x[1], reverse=True):
        percentage = (count / st.session_state.analytics['total_entities']) * 100
        
        col1, col2 = st.columns([3, 1])
        with col1:
            st.progress(percentage / 100)
        with col2:
            st.write(f"**{entity_type}**: {count} ({percentage:.1f}%)")

def render_results():
    """Render the complete results section"""
    st.divider()
    
    # Analytics Summary
    render_analytics_summary()
    
    st.divider()
    
    # Results tabs
    st.subheader("📋 Detailed Results")
    
    # Create tabs for different views
    tab1, tab2, tab3, tab4 = st.tabs([
        "🎨 Visual View", 
        "📋 Raw Data", 
        "👥 Character Analysis", 
        "📊 Entity Breakdown"
    ])
    
    with tab1:
        render_visual_tab()
    
    with tab2:
        render_json_tab()
    
    with tab3:
        render_character_analysis_tab()
    
    with tab4:
        render_entity_breakdown_tab()