from config import testing

# Template queries

DEFAULT_DOI = "10.20387/bonares-b4h2-yd8t"
ENCODED_DOI = "10.20387%2Fbonares-b4h2-yd8t"
if testing:
    FAIR_METRICS = "http://127.0.0.1:3030/FAIR_Metrics/sparql"
else:
    FAIR_METRICS = "http://localhost:3030/FAIR_Metrics/sparql"

FAIR_QUERIES = {
    "Basic Query": """PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX fairagro: <https://fairagro.net/ontology#>

    SELECT * WHERE {
      ?sub ?pred ?obj .
    } LIMIT 10
    """,

    "Dimensions and Definitions": """PREFIX dqv: <http://www.w3.org/ns/dqv#>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
PREFIX fairagro: <https://fairagro.net/ontology#>

    SELECT ?dimension ?definition WHERE {
      ?dimension a dqv:Dimension .
      OPTIONAL { ?dimension skos:definition ?definition }
    } ORDER BY ?dimension
    """,

 "Findability Metrics": """PREFIX dqv: <http://www.w3.org/ns/dqv#>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
PREFIX fairagro: <https://fairagro.net/ontology#>

    SELECT ?metric ?label ?definition WHERE {
      ?metric a dqv:Metric ;
              dqv:inDimension <https://fairagro.net/ontology#findability> .
      OPTIONAL { ?metric skos:prefLabel ?label }
      OPTIONAL { ?metric skos:definition ?definition }
    } ORDER BY ?metric
    """,

    "Accessibility Metrics": """PREFIX dqv: <http://www.w3.org/ns/dqv#>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
PREFIX fairagro: <https://fairagro.net/ontology#>

    SELECT ?metric ?label ?definition WHERE {
      ?metric a dqv:Metric ;
              dqv:inDimension <https://fairagro.net/ontology#accessibility> .
      OPTIONAL { ?metric skos:prefLabel ?label }
      OPTIONAL { ?metric skos:definition ?definition }
    } ORDER BY ?metric
    """,

    "Interoperability Metrics": """PREFIX dqv: <http://www.w3.org/ns/dqv#>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
PREFIX fairagro: <https://fairagro.net/ontology#>

    SELECT ?metric ?label ?definition WHERE {
      ?metric a dqv:Metric ;
              dqv:inDimension <https://fairagro.net/ontology#interoperability> .
      OPTIONAL { ?metric skos:prefLabel ?label }
      OPTIONAL { ?metric skos:definition ?definition }
    } ORDER BY ?metric
    """,

    "Reusability Metrics": """PREFIX dqv: <http://www.w3.org/ns/dqv#>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
PREFIX fairagro: <https://fairagro.net/ontology#>

    SELECT ?metric ?label ?definition WHERE {
      ?metric a dqv:Metric ;
              dqv:inDimension <https://fairagro.net/ontology#reusability> .
      OPTIONAL { ?metric skos:prefLabel ?label }
      OPTIONAL { ?metric skos:definition ?definition }
    } ORDER BY ?metric
    """,

"Fair is Fair (FUJI) Metrics": """PREFIX dqv: <http://www.w3.org/ns/dqv#>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
PREFIX fairagro: <https://fairagro.net/ontology#>

    SELECT ?metric ?label ?dimension ?definition WHERE {
      ?metric a dqv:Metric ;
              FILTER (STRSTARTS(STR(?metric), "https://fairagro.net/ontology#FsF-")).
      OPTIONAL { ?metric skos:prefLabel ?label }
      OPTIONAL { ?metric dqv:inDimension ?dimension }
      OPTIONAL { ?metric skos:definition ?definition }
    } ORDER BY ?dimension ?metric
    """,

    "Fair Evaluation Service (FES) Metrics": """PREFIX dqv: <http://www.w3.org/ns/dqv#>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
PREFIX fairagro: <https://fairagro.net/ontology#>

    SELECT ?metric ?label ?dimension ?definition WHERE {
      ?metric a dqv:Metric ;
              FILTER (STRSTARTS(STR(?metric), "https://fairagro.net/ontology#FES-")).
      OPTIONAL { ?metric skos:prefLabel ?label }
      OPTIONAL { ?metric dqv:inDimension ?dimension }
      OPTIONAL { ?metric skos:definition ?definition }
    } ORDER BY ?dimension ?metric
    """
}

RDI_QUERIES = {
    "Basic Query": """PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX fairagro: <https://fairagro.net/ontology#>

SELECT ?subject ?predicate ?object WHERE {
  ?subject ?predicate ?object .
} LIMIT 10
""",

    "Explore Datasets": """PREFIX dcat: <http://www.w3.org/ns/dcat#>
PREFIX dcterms: <http://purl.org/dc/terms/>
PREFIX dqv: <http://www.w3.org/ns/dqv#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX fairagro: <https://fairagro.net/ontology#>

SELECT ?dataset ?title ?distribution ?metric ?metric_name ?value ?computedBy WHERE {
  ?dataset a dcat:Dataset ;
           dcterms:title ?title ;
           dcat:distribution ?distribution .

  ?distribution dqv:hasQualityMeasurement ?measurement .
  ?measurement a dqv:QualityMeasurement ;
               dqv:computedBy ?computedBy ;
               dqv:isMeasurementOf ?metric ;
               dqv:value ?value .

  OPTIONAL { ?metric rdfs:label ?metric_name }
} ORDER BY ?dataset ?metric
""",

    "All Measurements per Dataset": """PREFIX dcat: <http://www.w3.org/ns/dcat#>
PREFIX dcterms: <http://purl.org/dc/terms/>
PREFIX dqv: <http://www.w3.org/ns/dqv#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX fairagro: <https://fairagro.net/ontology#>

SELECT ?dataset ?title ?metric ?metric_name ?value ?computedBy WHERE {
  ?dataset a dcat:Dataset ;
           dcterms:title ?title ;
           dcat:distribution ?distribution .

  ?distribution dqv:hasQualityMeasurement ?measurement .
  ?measurement a dqv:QualityMeasurement ;
               dqv:computedBy ?computedBy ;
               dqv:isMeasurementOf ?metric ;
               dqv:value ?value .

  OPTIONAL { ?metric rdfs:label ?metric_name }
} ORDER BY ?dataset ?metric
""",

"Measurements for Specific DOI": f"""PREFIX dcat: <http://www.w3.org/ns/dcat#>
PREFIX dqv: <http://www.w3.org/ns/dqv#>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>

SELECT ?prefLabel ?altLabel ?value ?definition ?computedBy WHERE {{
  ?dataset a dcat:Dataset ;
           dcat:distribution ?distribution .

  ?distribution dcat:accessURL <https://doi.org/{ENCODED_DOI}> ;
                dqv:hasQualityMeasurement ?measurement .

  ?measurement a dqv:QualityMeasurement ;
               dqv:computedBy ?computedBy ;
               dqv:isMeasurementOf ?metric ;
               dqv:value ?value .

  SERVICE <{FAIR_METRICS}> {{
    ?metric a dqv:Metric ;
            skos:altLabel ?altLabel ;
            skos:prefLabel ?prefLabel ;
            skos:definition ?definition .
  }}
}}
ORDER BY ?prefLabel
""",

"Measurements Below Threshold with Metric Definitions": f"""PREFIX dcat: <http://www.w3.org/ns/dcat#>
PREFIX dqv: <http://www.w3.org/ns/dqv#>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

SELECT ?prefLabel ?altLabel ?value ?definition ?computedBy WHERE {{
  ?dataset a dcat:Dataset ;
           dcat:distribution ?distribution .

  ?distribution dcat:accessURL <https://doi.org/{ENCODED_DOI}> ;
                dqv:hasQualityMeasurement ?measurement .

  ?measurement a dqv:QualityMeasurement ;
               dqv:computedBy ?computedBy ;
               dqv:isMeasurementOf ?metric ;
               dqv:value ?value .

  FILTER(?value < 1.0)

  SERVICE <{FAIR_METRICS}> {{
    ?metric a dqv:Metric ;
            skos:altLabel ?altLabel ;
            skos:prefLabel ?prefLabel ;
            skos:definition ?definition .
  }}
}}
ORDER BY ?prefLabel
"""

}

