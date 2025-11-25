import threading
from concurrent.futures import ThreadPoolExecutor

import streamlit as st  # Streamlit for UI rendering
from datetime import datetime  # For tracking start and end times
import plotly.graph_objects as go  # For creating grouped bar charts

from pyvis.network import Network  # For RDF graph visualization
import streamlit.components.v1 as components  # To embed HTML in Streamlit
from requests.exceptions import ConnectTimeout

# Direct imports (no try/except) since these modules and attributes are guaranteed to exist
from FES_evaluation import fes_evaluate_to_list, fes_evaluation_result_example
from FUJI_evaluation import fuji_evaluate_to_list, fuji_evaluation_result_example
from FC_evaluation import fairchecker_evaluate_to_list ,fc_evaluation_result_example

from doi_to_dqv import create_dqv_representation  # Function to generate RDF representation
from rdf_utils import extract_scores_from_rdf  # Utility to extract scores from RDF

# Example FES and FUJI evaluation results (use provided examples)
fes_evaluation_result = fes_evaluation_result_example
fuji_evaluation_result = fuji_evaluation_result_example
fc_evaluation_result = fc_evaluation_result_example

# Streamlit UI
st.title("DOI to FAIR Evaluation")

# Development toggle
development_mode = st.checkbox("Use cached result (Development Mode)", value=True)
# Warn if development mode is on but cached examples are unavailable
if development_mode and (not fes_evaluation_result or not fuji_evaluation_result or not fc_evaluation_result):
    st.info("Cached example results are not available; charts may be empty unless live evaluations are run.")

# Input field for DOI(s): one per line (also supports a single DOI)
st.markdown("Enter one or more DOIs, one per line. You can also enter a single DOI.")
data_dois_text = st.text_area(
    "DOI(s)",
    placeholder="10.1000/xyz123\n10.2000/abc456",
    height=120
)
data_dois = [line.strip() for line in data_dois_text.splitlines() if line.strip()]

# Provide a default DOI in developer mode if no input is provided
if development_mode and not data_dois:
    st.warning("Using default DOI for development mode.")
    data_dois = ["10.1000/xyz123"]

# Checkboxes to include FES and FUJI evaluations
include_fes = st.checkbox("Include FES Evaluation", value=True)
include_fuji = st.checkbox("Include F-UJI Evaluation", value=True)
include_fc = st.checkbox("Include FC Evaluation", value=True)

# Initialize session state for RDF representation and visualization toggle
if "dqv_representation" not in st.session_state:
    st.session_state["dqv_representation"] = None
if "show_rdf" not in st.session_state:
    st.session_state["show_rdf"] = False
if "bar_chart" not in st.session_state:
    st.session_state["bar_chart"] = None

def build_grouped_bar_chart(extracted_scores: dict, title: str) -> go.Figure:
    fair_dimensions = ["Findability", "Accessibility", "Interoperability", "Reusability"]

    # Always use whatever data exists in the extracted_scores
    fes_dimension_scores = extracted_scores.get("fes", {})
    fuji_dimension_scores = extracted_scores.get("fuji", {})
    fc_dimension_scores = extracted_scores.get("fc", {})

    fes_dimension_values = [
        fes_dimension_scores.get("findability_score", 0),
        fes_dimension_scores.get("accessibility_score", 0),
        fes_dimension_scores.get("interoperability_score", 0),
        fes_dimension_scores.get("reusability_score", 0),
    ]

    fuji_dimension_values = [
        fuji_dimension_scores.get("findability_score", 0),
        fuji_dimension_scores.get("accessibility_score", 0),
        fuji_dimension_scores.get("interoperability_score", 0),
        fuji_dimension_scores.get("reusability_score", 0),
    ]

    fc_dimension_values = [
        fc_dimension_scores.get("findability_score", 0),
        fc_dimension_scores.get("accessibility_score", 0),
        fc_dimension_scores.get("interoperability_score", 0),
        fc_dimension_scores.get("reusability_score", 0),
    ]

    fair_fig = go.Figure()
    if fes_dimension_scores:
        fair_fig.add_trace(go.Bar(x=fair_dimensions, y=fes_dimension_values, name="FES", marker={"color": "skyblue"}))
    if fuji_dimension_scores:
        fair_fig.add_trace(go.Bar(x=fair_dimensions, y=fuji_dimension_values, name="FUJI", marker={"color": "orange"}))
    if fc_dimension_scores:
        fair_fig.add_trace(go.Bar(x=fair_dimensions, y=fc_dimension_values, name="FC", marker={"color": "green"}))

    fair_fig.update_layout(
        title=title,
        xaxis_title="FAIR Dimensions",
        yaxis_title="Scores",
        barmode="group",
        legend_title="Source",
        yaxis=dict(range=[0, 1]),
    )
    return fair_fig

# Add per-DOI storage and selection
if "dqv_by_doi" not in st.session_state:
    st.session_state["dqv_by_doi"] = {}
if "selected_doi" not in st.session_state:
    st.session_state["selected_doi"] = None

# Generate FAIR Evaluation button
if st.button("Generate FAIR Evaluation"):
    # Always reset the visualization state on click to avoid showing stale charts if evaluation fails
    st.session_state["dqv_representation"] = None
    st.session_state["bar_chart"] = None
    st.session_state["show_rdf"] = False
    st.session_state["dqv_by_doi"] = {}
    st.session_state["selected_doi"] = None

    # Prepare DOI list (sequential processing across DOIs; FES+FUJI run in parallel per DOI)
    dois_to_process = list(data_dois)

    if dois_to_process:
        # Visual feedback placeholders
        status_box = st.empty()
        log_box = st.empty()
        progress = st.progress(0)
        total = len(dois_to_process)

        for idx, current_doi in enumerate(dois_to_process, start=1):
            status_box.info(f"Processing DOI {idx}/{total}: {current_doi}")

            if development_mode:
                fes_evaluation_result_used = fes_evaluation_result if include_fes else None
                fuji_evaluation_result_used = fuji_evaluation_result if include_fuji else None
                fc_evaluation_result_used = fc_evaluation_result if include_fc else None
            else:
                # Run FES and FUJI in parallel (per DOI)
                fes_evaluation_result_used = None
                fuji_evaluation_result_used = None
                fc_evaluation_result_used = None

                def _now_ts():
                    return datetime.now().strftime("%H:%M:%S.%f")[:-3]

                def _fes_task(doi_1):
                    print(f"[{_now_ts()}] [Thread {threading.current_thread().name}] FES start for DOI: {doi_1}")
                    res = fes_evaluate_to_list(doi_1)
                    print(f"[{_now_ts()}] [Thread {threading.current_thread().name}] FES end for DOI: {doi_1}")
                    return res

                def _fuji_task(doi_2):
                    print(f"[{_now_ts()}] [Thread {threading.current_thread().name}] FUJI start for DOI: {doi_2}")
                    res = fuji_evaluate_to_list(doi_2)
                    print(f"[{_now_ts()}] [Thread {threading.current_thread().name}] FUJI end for DOI: {doi_2}")
                    return res

                def _fc_task(doi_3):
                    print(f"[{_now_ts()}] [Thread {threading.current_thread().name}] FC start for DOI: {doi_3}")
                    res = fairchecker_evaluate_to_list(doi_3)
                    print(f"[{_now_ts()}] [Thread {threading.current_thread().name}] FC end for DOI: {doi_3}")
                    return res

                with ThreadPoolExecutor(max_workers=4) as executor:
                    futures = {}
                    if include_fes:
                        futures["fes"] = executor.submit(_fes_task, current_doi)
                    if include_fuji:
                        futures["fuji"] = executor.submit(_fuji_task, current_doi)
                    if include_fc:
                        futures["fc"] = executor.submit(_fc_task, current_doi)

                    # Collect FES result
                    if "fes" in futures:
                        try:
                            fes_result, fes_error = futures["fes"].result()
                            fes_evaluation_result_used = fes_result
                            if fes_error:
                                st.error(fes_error)
                        except Exception as e:
                            st.error(f"FES evaluation failed: {e}")
                            fes_evaluation_result_used = None

                    # Collect FUJI result
                    if "fuji" in futures:
                        try:
                            fuji_evaluation_result_used = futures["fuji"].result()
                        except ConnectTimeout:
                            st.error("FUJI evaluation timed out. Please check your network connection or try again later.")
                            fuji_evaluation_result_used = None
                        except RuntimeError as e:
                            st.error(f"FUJI evaluation failed: {e}")
                            fuji_evaluation_result_used = None
                        except Exception as e:
                            st.error(f"FUJI evaluation failed: {e}")
                            fuji_evaluation_result_used = None

                    # Collect FC result
                    if "fc" in futures:
                        try:
                            fc_evaluation_result_used = futures["fc"].result()
                        except ConnectTimeout:
                            st.error(
                                "FC evaluation timed out. Please check your network connection or try again later.")
                            fc_evaluation_result_used = None
                        except RuntimeError as e:
                            st.error(f"FC evaluation failed: {e}")
                            fc_evaluation_result_used = None
                        except Exception as e:
                            st.error(f"FC evaluation failed: {e}")
                            fc_evaluation_result_used = None

            # If any result exists for this DOI, build graph and chart (shows last processed DOI)
            if fes_evaluation_result_used or fuji_evaluation_result_used or fc_evaluation_result_used:
                start_time = datetime.now()
                end_time = datetime.now()

                try:
                    dqv_representation = create_dqv_representation(
                        doi=current_doi,
                        fes_evaluation_result=fes_evaluation_result_used or {},
                        fuji_evaluation_result=fuji_evaluation_result_used or {},
                        fc_evaluation_result=fc_evaluation_result_used or {},
                        start_time=start_time,
                        end_time=end_time,
                    )
                    # Save the graph under the DOI and set selection to current DOI
                    st.session_state["dqv_by_doi"][current_doi] = dqv_representation
                    st.session_state["selected_doi"] = current_doi

                    scores_by_metric = extract_scores_from_rdf(dqv_representation)
            # Another duplicated chart-building section
                    chart_figure = build_grouped_bar_chart(
                        extracted_scores=scores_by_metric,
                        title=f"FAIR Dimension Scores (Grouped by FES, FUJI, FC) — {current_doi}"
                    )
                    st.session_state["bar_chart"] = chart_figure

                    log_box.success(f"Finished DOI {idx}/{total}: {current_doi}")
                except Exception as e:
                    st.error(f"Failed to process RDF representation for {current_doi}: {e}")
            else:
                st.error(f"No scores returned for DOI: {current_doi}")

            progress.progress(int(idx / total * 100))
        # Final state message
        status_box.success("All requested DOIs processed.")
    else:
        st.warning("Please enter at least one DOI.")

# Reset button to clear the session state
if st.button("Reset Visualization and Chart"):
    st.session_state["dqv_representation"] = None
    st.session_state["bar_chart"] = None
    st.session_state["show_rdf"] = False
    st.session_state["dqv_by_doi"] = {}
    st.session_state["selected_doi"] = None
    st.success("Visualization and chart reset successfully.")

# Selector and chart for chosen DOI (supports multiple results)
if st.session_state["dqv_by_doi"]:
    # Ensure a stable initial selection only once
    if "selected_doi" not in st.session_state or st.session_state["selected_doi"] not in st.session_state["dqv_by_doi"]:
        first_doi = next(iter(st.session_state["dqv_by_doi"].keys()))
        st.session_state["selected_doi"] = first_doi

    doi_options = list(st.session_state["dqv_by_doi"].keys())

    # Anchor to keep the view from jumping to top on rerun
    st.markdown('<div id="results-anchor"></div>', unsafe_allow_html=True)

    # Bind directly to the session state; do NOT pass index to avoid resetting selection
    st.selectbox(
        "Select DOI to view results:",
        doi_options,
        key="selected_doi"
    )
    selected_doi = st.session_state["selected_doi"]

    # Keep the viewport near results after rerun
    st.markdown(
        '<script>document.getElementById("results-anchor").scrollIntoView({behavior: "instant", block: "start"});</script>',
        unsafe_allow_html=True
    )

    # Build chart for selected DOI
    try:
        rdf_graph_sel = st.session_state["dqv_by_doi"][selected_doi]
        scores_by_metric = extract_scores_from_rdf(rdf_graph_sel)
        fes_scores = scores_by_metric.get("fes", {}) if include_fes else {}
        fuji_scores = scores_by_metric.get("fuji", {}) if include_fuji else {}
        fc_scores = scores_by_metric.get("fc", {}) if include_fc else {}

        chart_figure = build_grouped_bar_chart(
            extracted_scores=scores_by_metric,
            title=f"FAIR Dimension Scores (Grouped by FES, FUJI, FC) — {selected_doi}"
        )
        st.plotly_chart(chart_figure)
    except Exception as e:
        st.error(f"Failed to build chart for {selected_doi}: {e}")
elif st.session_state["bar_chart"] and isinstance(st.session_state["bar_chart"], go.Figure):
    # Fallback for single-DOI legacy path
    st.plotly_chart(st.session_state["bar_chart"])
else:
    st.warning("No valid chart available.")

# Button to toggle RDF graph visualization
if st.session_state["dqv_representation"] is not None or st.session_state["dqv_by_doi"]:
    if st.button("Visualize RDF Graph"):
        st.session_state["show_rdf"] = not st.session_state["show_rdf"]

    # Conditionally render the RDF graph below the bar chart
    if st.session_state["show_rdf"]:
        # Use selected DOI graph if available
        rdf_graph = None
        if st.session_state["dqv_by_doi"] and st.session_state["selected_doi"] in st.session_state["dqv_by_doi"]:
            rdf_graph = st.session_state["dqv_by_doi"][st.session_state["selected_doi"]]
        else:
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

# Initialize download format selection in the session state
if "download_format" not in st.session_state:
    st.session_state["download_format"] = "Turtle"

# Dropdown menu for format selection (always shown if the graph is available)
rdf_graph = None
sel = st.session_state.get("selected_doi")
if st.session_state["dqv_by_doi"] and sel in st.session_state["dqv_by_doi"]:
    rdf_graph = st.session_state["dqv_by_doi"][sel]
elif st.session_state["dqv_representation"]:
    rdf_graph = st.session_state["dqv_representation"]

format_mapping = None

if rdf_graph:
    download_format = st.selectbox(
        "Select the format to download the RDF representation:",
        ["Turtle", "XML", "N-Triples", "JSON-LD"],
        index=0
    )
    st.session_state["download_format"] = download_format
    format_mapping = {
        "Turtle": ("turtle", "ttl"),
        "XML": ("xml", "xml"),
        "N-Triples": ("nt", "nt"),
        "JSON-LD": ("json-ld", "jsonld")
    }
    selected_format, file_extension = format_mapping[st.session_state["download_format"]]
    try:
        rdf_data = rdf_graph.serialize(format=selected_format)
        safe_name = (sel or "current").replace("/", "_") if sel else "current"
        st.download_button(
            label=f"Download RDF Graph for {sel or 'current'}",
            data=rdf_data,
            file_name=f"rdf_graph_{safe_name}.{file_extension}",
            mime="text/plain"
        )
    except Exception as e:
        st.error(f"Failed to serialize RDF graph: {e}")

# --- Add Download All Files button if multiple DOIs exist ---
if len(st.session_state["dqv_by_doi"]) > 1:
    all_zip_name = "all_dqv_files.zip"
    import io, zipfile

    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zipf:
        for doi, rdf_graph in st.session_state["dqv_by_doi"].items():
            try:
                selected_format, file_extension = format_mapping[st.session_state["download_format"]]
                rdf_data = rdf_graph.serialize(format=selected_format)
                safe_name = doi.replace("/", "_")
                zipf.writestr(f"rdf_graph_{safe_name}.{file_extension}", rdf_data)
            except Exception as e:
                st.warning(f"Skipping {doi} due to serialization error: {e}")
    zip_buffer.seek(0)

    st.download_button(
        label="Download All RDF Graphs as ZIP",
        data=zip_buffer,
        file_name=all_zip_name,
        mime="application/zip"
    )


# Footer
st.markdown("---")
