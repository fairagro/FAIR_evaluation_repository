import streamlit as st  # Streamlit for UI rendering
from datetime import datetime  # For tracking start and end times
import plotly.graph_objects as go  # For creating grouped bar charts
from FES_evaluation import fes_evaluate_to_list, fes_evaluation_result_example, \
    fes_evaluate_to_list_alternative  # Cached FES evaluation results
from doi_to_dqv import create_dqv_representation  # Function to generate RDF representation
from rdf_utils import extract_scores_from_rdf  # Utility to extract scores from RDF
from pyvis.network import Network  # For RDF graph visualization
import streamlit.components.v1 as components  # To embed HTML in Streamlit
from FUJI_evaluation import fuji_evaluation_result_example, fuji_evaluate_to_list  # Cached FUJI evaluation results
from requests.exceptions import ConnectTimeout

# Example FES and FUJI evaluation results
fes_evaluation_result = fes_evaluation_result_example
fuji_evaluation_result = fuji_evaluation_result_example

# Streamlit UI
st.title("DOI to FAIR Evaluation")

# Development toggle
development_mode = st.checkbox("Use cached result (Development Mode)", value=True)

# Input field for DOI
data_doi = st.text_input("Enter a DOI:", placeholder="10.1000/xyz123")

# Provide a default DOI in developer mode if no input is provided
if development_mode and not data_doi:
    st.warning("Using default DOI for development mode.")
    data_doi = "10.1000/xyz123"

# Checkboxes to include FES and FUJI evaluations
include_fes = st.checkbox("Include FES Evaluation", value=True)
include_fuji = st.checkbox("Include FUJI Evaluation", value=True)

# Initialize session state for RDF representation and visualization toggle
if "dqv_representation" not in st.session_state:
    st.session_state["dqv_representation"] = None
if "show_rdf" not in st.session_state:
    st.session_state["show_rdf"] = False
if "bar_chart" not in st.session_state:
    st.session_state["bar_chart"] = None

# Generate FAIR Evaluation button
if st.button("Generate FAIR Evaluation"):
    if data_doi or development_mode:
        if development_mode:
            st.warning("Using cached result for development.")
            fes_evaluation_result_used = fes_evaluation_result if include_fes else None
            fuji_evaluation_result_used = fuji_evaluation_result if include_fuji else None
        else:
            # Handle FES evaluation errors
            if include_fes:
                result, error = fes_evaluate_to_list(data_doi)
                fes_evaluation_result_used = result
                if error:
                    st.error(error)
            else:
                fes_evaluation_result_used = None

            # Handle FUJI evaluation errors
            if include_fuji:
                try:
                    fuji_evaluation_result_used = fuji_evaluate_to_list(data_doi)
                except ConnectTimeout:
                    st.error("FUJI evaluation timed out. Please check your network connection or try again later.")
                    fes_evaluation_result_used = None
                except RuntimeError as e:
                    st.error(f"FUJI evaluation failed: {e}")
                    fuji_evaluation_result_used = None
            else:
                fuji_evaluation_result_used = None

        if fes_evaluation_result_used or fuji_evaluation_result_used:
            start_time = datetime.now()
            end_time = datetime.now()

            try:
                # Pass empty dictionaries if results are not available
                dqv_representation = create_dqv_representation(
                    doi=data_doi,
                    fes_evaluation_result=fes_evaluation_result_used or {},
                    fuji_evaluation_result=fuji_evaluation_result_used or {},
                    start_time=start_time,
                    end_time=end_time,
                )

                # Save RDF graph to session state for visualization
                st.session_state["dqv_representation"] = dqv_representation

                scores_by_metric = extract_scores_from_rdf(dqv_representation)

                fes_scores = scores_by_metric.get("fes", {}) if include_fes else {}
                fuji_scores = scores_by_metric.get("fuji", {}) if include_fuji else {}

                dimensions = ["Findability", "Accessibility", "Interoperability", "Reusability"]

                fes_values = [
                    fes_scores.get("findability_score", 0),
                    fes_scores.get("accessibility_score", 0),
                    fes_scores.get("interoperability_score", 0),
                    fes_scores.get("reusability_score", 0),
                ] if include_fes else [0, 0, 0, 0]

                fuji_values = [
                    fuji_scores.get("findability_score", 0),
                    fuji_scores.get("accessibility_score", 0),
                    fuji_scores.get("interoperability_score", 0),
                    fuji_scores.get("reusability_score", 0),
                ] if include_fuji else [0, 0, 0, 0]

                # Create a grouped bar chart with Plotly
                fig = go.Figure()
                if include_fes:
                    fig.add_trace(go.Bar(
                        x=dimensions,
                        y=fes_values,
                        name="FES",
                        marker={"color": "skyblue"}  # Use marker dictionary for color
                    ))
                if include_fuji:
                    fig.add_trace(go.Bar(
                        x=dimensions,
                        y=fuji_values,
                        name="FUJI",
                        marker={"color": "orange"}  # Use marker dictionary for color
                    ))

                # Update layout for grouped bars
                fig.update_layout(
                    title="FAIR Dimension Scores (Grouped by FES and FUJI)",
                    xaxis_title="FAIR Dimensions",
                    yaxis_title="Scores",
                    barmode="group",  # Group the bars side by side
                    legend_title="Source",
                    yaxis=dict(range=[0, 1]),
                )

                # Save the bar chart figure to session state
                st.session_state["bar_chart"] = fig

            except Exception as e:
                st.error(f"Failed to process RDF representation: {e}")
        else:
            st.error("No scores returned for the selected evaluations.")
    else:
        st.warning("Please enter a DOI.")

# Reset button to clear session state
if st.button("Reset Visualization and Chart"):
    st.session_state["dqv_representation"] = None
    st.session_state["bar_chart"] = None
    st.session_state["show_rdf"] = False
    st.success("Visualization and chart reset successfully.")

# Always display the grouped bar chart
if st.session_state["bar_chart"] and isinstance(st.session_state["bar_chart"], go.Figure):
    st.plotly_chart(st.session_state["bar_chart"])
else:
    st.warning("No valid chart available.")

# Button to toggle RDF graph visualization
if st.session_state["dqv_representation"] is not None:
    if st.button("Visualize RDF Graph"):
        st.session_state["show_rdf"] = not st.session_state["show_rdf"]

    # Conditionally render the RDF graph below the bar chart
    if st.session_state["show_rdf"]:
        rdf_graph = st.session_state["dqv_representation"]
        net = Network(height="500px", width="100%", notebook=True)

        # Add nodes and edges to the Pyvis graph
        for subj, pred, obj in rdf_graph:
            net.add_node(str(subj), label=str(subj), color="blue")
            net.add_node(str(obj), label=str(obj), color="green")
            net.add_edge(str(subj), str(obj), title=str(pred))

        # Save the Pyvis graph to an HTML file and display it in Streamlit
        net.save_graph("rdf_graph.html")
        st.subheader("RDF Graph Visualization")
        components.html(open("rdf_graph.html", "r").read(), height=500)

# Initialize download format selection in session state
if "download_format" not in st.session_state:
    st.session_state["download_format"] = "Turtle"

# Dropdown menu for format selection (always shown if the graph is available)
if st.session_state["dqv_representation"]:
    download_format = st.selectbox(
        "Select the format to download the RDF representation:",
        ["Turtle", "XML", "N-Triples", "JSON-LD"],
        index=0
    )

    # Save the selected format in session state
    st.session_state["download_format"] = download_format

    # Define a mapping for formats and file extensions
    format_mapping = {
        "Turtle": ("turtle", "ttl"),
        "XML": ("xml", "xml"),
        "N-Triples": ("nt", "nt"),
        "JSON-LD": ("json-ld", "jsonld")
    }

    # Display a single download button
    selected_format, file_extension = format_mapping[st.session_state["download_format"]]
    rdf_graph = st.session_state["dqv_representation"]

    # Serialize the graph to the selected format
    try:
        rdf_data = rdf_graph.serialize(format=selected_format)

        # Provide the download button
        st.download_button(
            label="Download RDF Graph",
            data=rdf_data,
            file_name=f"rdf_graph.{file_extension}",
            mime="text/plain"
        )
    except Exception as e:
        st.error(f"Failed to serialize RDF graph: {e}")

# Footer
st.markdown("---")
