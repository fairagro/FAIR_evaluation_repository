from rdflib import Graph, Literal, Namespace, URIRef
from rdflib.namespace import DCAT, DCTERMS, RDF, XSD, PROV, RDFS
from doi_info_fetcher import get_datacite_doi_info
from FES_evaluation import fes_evaluate_to_list
from FUJI_evaluation import fuji_evaluate_to_list
from datetime import datetime
from metric_mappings import fes_metric_mapping, fuji_metric_mapping

WRITE_METRICS = False
WRITE_AGENTS = False
WRITE_DIMENSIONS = False

# Namespaces
FAIRAGRO = Namespace("https://fairagro.net/ontology#")
DCAT = Namespace("http://www.w3.org/ns/dcat#")
DCTERMS = Namespace("http://purl.org/dc/terms/")
DQV = Namespace("http://www.w3.org/ns/dqv#")
SKOS = Namespace("http://www.w3.org/2004/02/skos/core#")

# Read the metrics and checkers Turtle files into separate graphs
metrics_graph = Graph()
metrics_graph.parse("fair_data_quality_metrics.ttl", format='turtle')

checkers_graph = Graph()
checkers_graph.parse("fair_quality_services.ttl", format='turtle')


def create_dqv_representation(doi: str, fes_evaluation_result: list, fuji_evaluation_result: dict, start_time: datetime, end_time: datetime):
    dataset_info = get_datacite_doi_info(doi)
    if not dataset_info:
        return None

    g = Graph()

    # Bind namespaces
    g.bind("dcat", DCAT)
    g.bind("dcterms", DCTERMS)
    g.bind("dqv", DQV)
    g.bind("skos", SKOS)
    g.bind("fairagro", FAIRAGRO)
    g.bind("prov", PROV)

    doi_slug = doi.replace('/', '-')
    dataset_uri = FAIRAGRO[f"dataset-{doi_slug}"]
    distribution_uri = FAIRAGRO[f"distribution-{doi_slug}"]
    fes_service_uri = FAIRAGRO["FAIREvaluationServices"]
    fuji_service_uri = FAIRAGRO["FUJIAutomatedFAIRDataAssessmentTool"]
    quality_metadata_uri = FAIRAGRO[f"qualityMetadata-{doi_slug}"]
    quality_checking_activity_uri = FAIRAGRO[f"qualityChecking-{doi_slug}"]

    # Adding dataset information
    g.add((dataset_uri, RDF.type, DCAT.Dataset))
    g.add((dataset_uri, DCTERMS.title, Literal(dataset_info["title"])))
    g.add((dataset_uri, DCAT.distribution, distribution_uri))

    # Adding distribution information
    g.add((distribution_uri, RDF.type, DCAT.Distribution))
    g.add((distribution_uri, DCTERMS.title, Literal("DOI distribution of dataset")))
    g.add((distribution_uri, DCAT.accessURL, URIRef(f"https://doi.org/{doi}")))
    g.add((distribution_uri, DCTERMS["format"], Literal(dataset_info["resource_type"])))

    if "byteSize" in dataset_info:
        g.add((distribution_uri, DCAT.byteSize, Literal(dataset_info["byteSize"], datatype=XSD.decimal)))

    # Adding quality metadata
    g.add((quality_metadata_uri, RDF.type, DQV.QualityMetadata))
    g.add((quality_metadata_uri, PROV.wasAttributedTo, fes_service_uri))
    g.add((quality_metadata_uri, PROV.wasAttributedTo, fuji_service_uri))
    g.add((quality_metadata_uri, PROV.generatedAtTime, Literal(datetime.now().isoformat(), datatype=XSD.dateTime)))
    g.add((quality_metadata_uri, PROV.wasGeneratedBy, quality_checking_activity_uri))

    # Adding quality checking activity
    g.add((quality_checking_activity_uri, RDF.type, PROV.Activity))
    g.add((quality_checking_activity_uri, RDFS.label,
           Literal("The checking of the dataset distribution's quality", datatype=XSD.string)))
    g.add((quality_checking_activity_uri, PROV.wasAssociatedWith, fes_service_uri))
    g.add((quality_checking_activity_uri, PROV.wasAssociatedWith, fuji_service_uri))
    g.add((quality_checking_activity_uri, PROV.used, distribution_uri))
    g.add((quality_checking_activity_uri, PROV.generated, quality_metadata_uri))
    g.add((quality_checking_activity_uri, PROV.startedAtTime, Literal(start_time.isoformat(), datatype=XSD.dateTime)))
    g.add((quality_checking_activity_uri, PROV.endedAtTime, Literal(end_time.isoformat(), datatype=XSD.dateTime)))

    if WRITE_DIMENSIONS:
        # Adding category and dimensions from the metrics_graph
        category_uri = fes_metric_mapping["category"]
        g.add((category_uri, RDF.type, DQV.Category))
        for s, p, o in metrics_graph.triples((category_uri, None, None)):
            g.add((s, p, o))

        for dimension_key, dimension_info in fes_metric_mapping["dimensions"].items():
            dimension_uri = dimension_info["dimension_uri"]
            g.add((dimension_uri, RDF.type, DQV.Dimension))
            g.add((dimension_uri, DQV.inCategory, category_uri))
            g.add((dimension_uri, SKOS.prefLabel, Literal(dimension_key.capitalize(), lang="en")))
            g.add((dimension_uri, SKOS.definition, Literal(dimension_info["definition"], lang="en")))
            for s, p, o in metrics_graph.triples((dimension_uri, None, None)):
                g.add((s, p, o))

    if WRITE_AGENTS:
        # Adding FES quality service if evaluation result exists
        if fes_evaluation_result:
            for s, p, o in checkers_graph.triples((fes_service_uri, None, None)):
                g.add((s, p, o))

        # Adding FUJI quality service if evaluation result exists
        if fuji_evaluation_result:
            for s, p, o in checkers_graph.triples((fuji_service_uri, None, None)):
                g.add((s, p, o))

    # Adding FES quality measurements and metrics
    measurements = []
    metric_index = 0
    for dimension_info in fes_metric_mapping["dimensions"].values():
        for metric_uri in dimension_info["metrics"]:
            if metric_index >= len(fes_evaluation_result):
                break
            result = fes_evaluation_result[metric_index]
            measurement_uri = FAIRAGRO[f"fes_measurement-{metric_index + 1}__{doi_slug}"]
            metric_index += 1

            if WRITE_METRICS:
                # Add metric to the graph
                for s, p, o in metrics_graph.triples((metric_uri, None, None)):
                    g.add((s, p, o))

            g.add((measurement_uri, RDF.type, DQV.QualityMeasurement))
            g.add((measurement_uri, DQV.isMeasurementOf, metric_uri))
            g.add((measurement_uri, DQV.value, Literal(result, datatype=XSD.float)))
            g.add((measurement_uri, DQV.computedBy, fes_service_uri))
            measurements.append(measurement_uri)

    # Linking measurements to the distribution
    for measurement in measurements:
        g.add((distribution_uri, DQV.hasQualityMeasurement, measurement))

    # Adding FUJI quality measurements and metrics
    measurements = []
    metric_index = 0
    for sub_metric, score in fuji_evaluation_result.items():
        metric_uri = fuji_metric_mapping.get(sub_metric)
        if not metric_uri:
            continue
        measurement_uri = FAIRAGRO[f"fuji_measurement-{metric_index + 1}__{doi_slug}"]
        metric_index += 1

        if WRITE_METRICS:
            # Add metric to the graph
            for s, p, o in metrics_graph.triples((metric_uri, None, None)):
                g.add((s, p, o))

        g.add((measurement_uri, RDF.type, DQV.QualityMeasurement))
        g.add((measurement_uri, DQV.isMeasurementOf, metric_uri))
        g.add((measurement_uri, DQV.value, Literal(score, datatype=XSD.float)))
        g.add((measurement_uri, DQV.computedBy, fuji_service_uri))
        measurements.append(measurement_uri)

    # Linking measurements to the distribution
    for measurement in measurements:
        g.add((distribution_uri, DQV.hasQualityMeasurement, measurement))

    return g


if __name__ == "__main__":
    # Fixed DOI for testing
    doi = "10.20387/bonares-tdgx-339v"

    # Define the start time before the evaluation
    start_time = datetime.now()

    # Get the evaluation result from FES
    fes_evaluation_result = fes_evaluate_to_list(doi)
    # fes_evaluation_result = ['1', '1', '0', '1', '1', '0', '0', '0', '0', '1', '0', '1', '0', '1', '1', '0', '0', '1',
    #                          '0', '1', '0', '1']
    if fes_evaluation_result:
        print("FES Evaluation Result:", fes_evaluation_result)

    # Get the evaluation result from FUJI
    fuji_evaluation_result = fuji_evaluate_to_list(doi)
    # fuji_evaluation_result = {
    #     "FsF-F1-01D-1": 0.8, "FsF-F1-01D-2": 0.6, "FsF-F1-02D-1": 1.0, "FsF-F1-02D-2": 0.9,
    #     "FsF-F2-01M-1": 1.0, "FsF-F2-01M-2": 0.8, "FsF-F2-01M-3": 0.9, "FsF-F3-01M-1": 0.7,
    #     "FsF-F3-01M-2": 0.6, "FsF-F4-01M-1": 0.9, "FsF-F4-01M-2": 0.8, "FsF-A1-01M-1": 0.9,
    #     "FsF-A1-01M-2": 0.7, "FsF-A1-01M-3": 0.8, "FsF-A1-02M-1": 0.9, "FsF-A1-03D-1": 1.0,
    #     "FsF-I1-01M-1": 0.8, "FsF-I1-01M-2": 0.7, "FsF-I2-01M-1": 0.6, "FsF-I2-01M-2": 0.9,
    #     "FsF-I3-01M-1": 0.8, "FsF-I3-01M-2": 0.7, "FsF-R1-01MD-1": 0.9, "FsF-R1-01MD-1a": 0.8,
    #     "FsF-R1-01MD-1b": 0.7, "FsF-R1-01MD-2": 0.9, "FsF-R1-01MD-2a": 0.8, "FsF-R1-01MD-2b": 0.7,
    #     "FsF-R1-01MD-3": 0.9, "FsF-R1-01MD-4": 0.8, "FsF-R1.1-01M-1": 0.9, "FsF-R1.1-01M-2": 0.8,
    #     "FsF-R1.2-01M-1": 0.7, "FsF-R1.2-01M-2": 0.9, "FsF-R1.3-01M-1": 0.8, "FsF-R1.3-01M-2": 0.7,
    #     "FsF-R1.3-01M-3": 0.9, "FsF-R1.3-02D-1": 0.8, "FsF-R1.3-02D-1a": 0.7, "FsF-R1.3-02D-1b": 0.9,
    #     "FsF-R1.3-02D-1c": 0.8
    # }
    if fuji_evaluation_result:
        print("FUJI Evaluation Result:", fuji_evaluation_result)

    # Define the end time after the evaluation
    end_time = datetime.now()

    # Create DQV representation
    graph = create_dqv_representation(doi, fes_evaluation_result, fuji_evaluation_result, start_time, end_time)
    if graph:
        output_file = f"output_{doi.replace('/', '_')}.ttl"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(graph.serialize(format='turtle'))
        print(f"Output written to {output_file}")
    else:
        print("Failed to create DQV representation.")
