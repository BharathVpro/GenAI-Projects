"""
Processor Module
Handles the core Langextract processing logic
"""

import streamlit as st
import langextract as lx
import textwrap
import json
import os
import tempfile
from collections import Counter
from langextract.inference import OpenAILanguageModel

def create_prompt():
    """Create the extraction prompt"""
    return textwrap.dedent("""\
        Extract characters, emotions, and relationships from the given text.

        Provide meaningful attributes for every entity to add context and depth.

        Important: Use exact text from the input for extraction_text. Do not paraphrase.
        Extract entities in order of appearance with no overlapping text spans.

        Note: In play scripts, speaker names appear in ALL-CAPS followed by a period.""")

def create_examples():
    """Create extraction examples"""
    return [
        lx.data.ExampleData(
            text=textwrap.dedent("""\
                ROMEO. But soft! What light through yonder window breaks?
                It is the east, and Juliet is the sun.
                JULIET. O Romeo, Romeo! Wherefore art thou Romeo?"""),
            extractions=[
                lx.data.Extraction(
                    extraction_class="character",
                    extraction_text="ROMEO",
                    attributes={"emotional_state": "wonder"}
                ),
                lx.data.Extraction(
                    extraction_class="emotion",
                    extraction_text="But soft!",
                    attributes={"feeling": "gentle awe", "character": "Romeo"}
                ),
                lx.data.Extraction(
                    extraction_class="relationship",
                    extraction_text="Juliet is the sun",
                    attributes={"type": "metaphor", "character_1": "Romeo", "character_2": "Juliet"}
                ),
                lx.data.Extraction(
                    extraction_class="character",
                    extraction_text="JULIET",
                    attributes={"emotional_state": "yearning"}
                ),
                lx.data.Extraction(
                    extraction_class="emotion",
                    extraction_text="Wherefore art thou Romeo?",
                    attributes={"feeling": "longing question", "character": "Juliet"}
                ),
            ]
        )
    ]

def analyze_results(result):
    """
    Analyze extraction results and generate analytics
    
    Args:
        result: Langextract result object
        
    Returns:
        dict: Analytics data
    """
    characters = {}
    for e in result.extractions:
        if e.extraction_class == "character":
            char_name = e.extraction_text
            if char_name not in characters:
                characters[char_name] = {"count": 0, "attributes": set()}
            characters[char_name]["count"] += 1
            if e.attributes:
                for attr_key, attr_val in e.attributes.items():
                    characters[char_name]["attributes"].add(f"{attr_key}: {attr_val}")
    
    # Entity type breakdown
    entity_counts = Counter(e.extraction_class for e in result.extractions)
    
    # Create analytics dictionary
    analytics = {
        "total_entities": len(result.extractions),
        "text_length": len(result.text),
        "characters": characters,
        "entity_counts": dict(entity_counts),
        "top_characters": sorted(characters.items(), key=lambda x: x[1]["count"], reverse=True)[:10]
    }
    
    return analytics

def process_text(input_source, extraction_passes, max_workers, max_char_buffer):
    """
    Process text using Langextract with advanced settings
    
    Args:
        input_source: Text or URL to process
        extraction_passes: Number of extraction passes
        max_workers: Number of parallel workers
        max_char_buffer: Size of context window
        
    Returns:
        bool: Success status
    """
    try:
        # Show processing details
        progress_text = st.empty()
        progress_text.info(f"Processing with {extraction_passes} passes, {max_workers} workers...")
        
        # Create prompt and examples
        prompt = create_prompt()
        examples = create_examples()
        
        # Run advanced extraction
        result = lx.extract(
            text_or_documents=input_source,
            prompt_description=prompt,
            examples=examples,
            language_model_type=OpenAILanguageModel,
            model_id="gpt-4o-mini",
            api_key=os.getenv("OPENAI_API_KEY"),
            extraction_passes=extraction_passes,
            max_workers=max_workers,
            max_char_buffer=max_char_buffer
        )
        
        progress_text.success(f"Extracted {len(result.extractions)} entities from {len(result.text):,} characters")
        
        # Create a temporary directory
        with tempfile.TemporaryDirectory() as temp_dir:
            # Save the results
            json_path = os.path.join(temp_dir, "extraction_results.jsonl")
            lx.io.save_annotated_documents([result], output_name=json_path)
            
            # Read JSON data
            with open(json_path, 'r') as f:
                json_lines = f.readlines()
                json_data = [json.loads(line) for line in json_lines]
            
            # Generate visualization
            html_obj = lx.visualize(json_path)
            
            # Convert HTML object to string
            if hasattr(html_obj, '_repr_html_'):
                html_content = html_obj._repr_html_()
            elif hasattr(html_obj, 'to_html'):
                html_content = html_obj.to_html()
            else:
                html_content = str(html_obj)
        
        # Analyze results
        analytics = analyze_results(result)
        
        # Store in session state
        st.session_state.processed = True
        st.session_state.json_data = json_data
        st.session_state.html_content = html_content
        st.session_state.analytics = analytics
        
        progress_text.empty()
        return True
        
    except Exception as e:
        st.error(f"❌ Error: {str(e)}")
        st.info("Make sure you have set up your API credentials for Gemini.")
        return False