#!/usr/bin/env python3
"""
MCP Server for Apache Jena Fuseki (SPARQL)
Optimized for FAIR assessment results using DQV ontology (fairagro namespace)
"""

import asyncio
import json
import os
from typing import Any

import httpx
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp import types

FUSEKI_URL = os.environ.get("FUSEKI_URL", "http://fuseki:3030").rstrip("/")
FUSEKI_USER = os.environ.get("FUSEKI_USER", "admin")
FUSEKI_PASSWORD = os.environ.get("FUSEKI_PASSWORD", "admin")

PREFIXES = """
PREFIX dqv: <http://www.w3.org/ns/dqv#>
PREFIX dcat: <http://www.w3.org/ns/dcat#>
PREFIX dcterms: <http://purl.org/dc/terms/>
PREFIX fairagro: <https://fairagro.net/ontology#>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
PREFIX prov: <http://www.w3.org/ns/prov#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
"""

# Dataset containing metric/dimension definitions
METRICS_DATASET = "FAIR_Metrics"

FORMAT_TO_CONTENT_TYPE = {
    "turtle": "text/turtle",
    "n-triples": "application/n-triples",
    "json-ld": "application/ld+json",
    "rdf+xml": "application/rdf+xml",
}

def auth():
    return (FUSEKI_USER, FUSEKI_PASSWORD)


async def sparql_query(dataset: str, query: str) -> Any:
    url = f"{FUSEKI_URL}/{dataset}/query"
    async with httpx.AsyncClient() as client:
        r = await client.post(
            url, content=query,
            headers={"Content-Type": "application/sparql-query",
                     "Accept": "application/sparql-results+json, application/ld+json, text/turtle"},
            auth=auth(), timeout=60,
        )
        r.raise_for_status()
        ct = r.headers.get("content-type", "")
        return r.json() if "json" in ct else r.text


async def sparql_update(dataset: str, update: str) -> dict:
    url = f"{FUSEKI_URL}/{dataset}/update"
    async with httpx.AsyncClient() as client:
        r = await client.post(
            url, content=update,
            headers={"Content-Type": "application/sparql-update"},
            auth=auth(), timeout=60,
        )
        r.raise_for_status()
        return {"success": True, "status": r.status_code}


async def list_datasets() -> Any:
    async with httpx.AsyncClient() as client:
        r = await client.get(f"{FUSEKI_URL}/$/datasets",
                             headers={"Accept": "application/json"},
                             auth=auth(), timeout=30)
        r.raise_for_status()
        return r.json()


async def ping() -> dict:
    async with httpx.AsyncClient() as client:
        try:
            r = await client.get(f"{FUSEKI_URL}/$/ping", auth=auth(), timeout=10)
            return {"reachable": r.is_success, "status": r.status_code, "url": FUSEKI_URL}
        except Exception as e:
            return {"reachable": False, "error": str(e), "url": FUSEKI_URL}


# ── FAIR-specific query helpers ───────────────────────────────────────────────
# Measurements live in the per-repository dataset (e.g. "bonares").
# Metric definitions (labels, dimensions) live in "FAIR_Metrics".
# We query both separately and join in Python.

async def _get_metric_definitions() -> dict:
    """Fetch all metric labels, definitions and dimensions from FAIR_Metrics."""
    query = PREFIXES + """
SELECT ?metric ?metricLabel ?metricDef ?dimension WHERE {
  ?metric a dqv:Metric ;
          skos:prefLabel ?metricLabel ;
          dqv:inDimension ?dim .
  ?dim skos:prefLabel ?dimension .
  OPTIONAL { ?metric skos:definition ?metricDef . }
}
"""
    result = await sparql_query(METRICS_DATASET, query)
    defs = {}
    for b in result.get("results", {}).get("bindings", []):
        uri = b["metric"]["value"]
        defs[uri] = {
            "label": b["metricLabel"]["value"],
            "definition": b.get("metricDef", {}).get("value", ""),
            "dimension": b["dimension"]["value"],
        }
    return defs


async def get_fair_summary(dataset: str, doi: str) -> Any:
    """All measurements for a DOI, enriched with metric metadata."""
    q = PREFIXES + f"""
SELECT ?metric ?value ?service WHERE {{
  ?measurement a dqv:QualityMeasurement ;
               dqv:isMeasurementOf ?metric ;
               dqv:value ?value ;
               dqv:computedBy ?service .
  FILTER(CONTAINS(STR(?measurement), "{doi}"))
}}
ORDER BY ?metric
"""
    measurements, defs = await asyncio.gather(
        sparql_query(dataset, q), _get_metric_definitions()
    )
    rows = []
    for b in measurements.get("results", {}).get("bindings", []):
        metric_uri = b["metric"]["value"]
        meta = defs.get(metric_uri, {})
        rows.append({
            "dimension": meta.get("dimension", "Unknown"),
            "metric": metric_uri.split("#")[-1],
            "label": meta.get("label", metric_uri.split("#")[-1]),
            "definition": meta.get("definition", ""),
            "value": float(b["value"]["value"]),
            "service": b["service"]["value"].split("#")[-1],
        })
    rows.sort(key=lambda r: (r["dimension"], r["label"]))
    return {"doi": doi, "measurements": rows, "total": len(rows)}


async def get_failed_metrics(dataset: str, doi: str) -> Any:
    """Only metrics where score = 0."""
    q = PREFIXES + f"""
SELECT ?metric ?service WHERE {{
  ?measurement a dqv:QualityMeasurement ;
               dqv:isMeasurementOf ?metric ;
               dqv:value ?value ;
               dqv:computedBy ?service .
  FILTER(CONTAINS(STR(?measurement), "{doi}"))
  FILTER(?value = 0.0)
}}
"""
    measurements, defs = await asyncio.gather(
        sparql_query(dataset, q), _get_metric_definitions()
    )
    rows = []
    for b in measurements.get("results", {}).get("bindings", []):
        metric_uri = b["metric"]["value"]
        meta = defs.get(metric_uri, {})
        rows.append({
            "dimension": meta.get("dimension", "Unknown"),
            "metric": metric_uri.split("#")[-1],
            "label": meta.get("label", metric_uri.split("#")[-1]),
            "definition": meta.get("definition", ""),
            "service": b["service"]["value"].split("#")[-1],
        })
    rows.sort(key=lambda r: (r["dimension"], r["label"]))
    return {"doi": doi, "failed_metrics": rows, "total_failed": len(rows)}


async def get_dimension_scores(dataset: str, doi: str) -> Any:
    """Average score per FAIR dimension."""
    q = PREFIXES + f"""
SELECT ?metric (AVG(?value) AS ?avgValue) WHERE {{
  ?measurement a dqv:QualityMeasurement ;
               dqv:isMeasurementOf ?metric ;
               dqv:value ?value .
  FILTER(CONTAINS(STR(?measurement), "{doi}"))
}}
GROUP BY ?metric
"""
    measurements, defs = await asyncio.gather(
        sparql_query(dataset, q), _get_metric_definitions()
    )
    dim_scores: dict[str, list] = {}
    for b in measurements.get("results", {}).get("bindings", []):
        metric_uri = b["metric"]["value"]
        meta = defs.get(metric_uri, {})
        dim = meta.get("dimension", "Unknown")
        dim_scores.setdefault(dim, []).append(float(b["avgValue"]["value"]))

    result = []
    for dim, scores in sorted(dim_scores.items()):
        result.append({
            "dimension": dim,
            "avgScore": round(sum(scores) / len(scores), 3),
            "numMetrics": len(scores),
        })
    return {"doi": doi, "dimensions": result}


async def list_assessed_datasets(dataset: str) -> Any:
    query = PREFIXES + """
SELECT DISTINCT ?dataset ?title ?accessURL ?assessmentTime WHERE {
  ?dataset a dcat:Dataset ;
           dcterms:title ?title ;
           dcat:distribution ?dist .
  ?dist dcat:accessURL ?accessURL .
  OPTIONAL {
    ?activity a prov:Activity ;
              prov:used ?dist ;
              prov:endedAtTime ?assessmentTime .
  }
}
ORDER BY DESC(?assessmentTime)
"""
    return await sparql_query(dataset, query)


async def compare_datasets(dataset: str, doi1: str, doi2: str) -> Any:
    """Compare dimension scores between two DOIs."""
    async def _scores(doi):
        r = await get_dimension_scores(dataset, doi)
        return {d["dimension"]: d["avgScore"] for d in r["dimensions"]}

    s1, s2 = await asyncio.gather(_scores(doi1), _scores(doi2))
    all_dims = sorted(set(s1) | set(s2))
    return {
        "doi1": doi1, "doi2": doi2,
        "comparison": [
            {"dimension": d, "score_doi1": s1.get(d), "score_doi2": s2.get(d)}
            for d in all_dims
        ]
    }


async def get_service_comparison(dataset: str, doi: str) -> Any:
    query = PREFIXES + f"""
SELECT ?service (AVG(?value) AS ?avgScore) (COUNT(?m) AS ?numMetrics) WHERE {{
  ?m a dqv:QualityMeasurement ;
     dqv:value ?value ;
     dqv:computedBy ?service .
  FILTER(CONTAINS(STR(?m), "{doi}"))
}}
GROUP BY ?service
"""
    return await sparql_query(dataset, query)


# ── MCP Server ────────────────────────────────────────────────────────────────

app = Server("fuseki-mcp")

TOOLS = [
    types.Tool(
        name="sparql_select",
        description="Execute a raw SPARQL SELECT or ASK query against a Fuseki dataset.",
        inputSchema={"type": "object",
                     "properties": {"dataset": {"type": "string"}, "query": {"type": "string"}},
                     "required": ["dataset", "query"]},
    ),
    types.Tool(
        name="sparql_update",
        description="Execute a SPARQL UPDATE (INSERT DATA, DELETE DATA, etc.).",
        inputSchema={"type": "object",
                     "properties": {"dataset": {"type": "string"}, "update": {"type": "string"}},
                     "required": ["dataset", "update"]},
    ),
    types.Tool(
        name="list_datasets",
        description="List all datasets available on the Fuseki server.",
        inputSchema={"type": "object", "properties": {}},
    ),
    types.Tool(
        name="ping_fuseki",
        description="Check if the Fuseki server is reachable.",
        inputSchema={"type": "object", "properties": {}},
    ),
    types.Tool(
        name="fair_get_summary",
        description="Get a full FAIR assessment summary for a dataset by DOI. Returns all DQV quality measurements grouped by FAIR dimension (Findability, Accessibility, Interoperability, Reusability) with metric labels, definitions, scores, and assessment service.",
        inputSchema={"type": "object",
                     "properties": {"dataset": {"type": "string", "description": "Fuseki dataset name"},
                                    "doi": {"type": "string", "description": "DOI or partial DOI, e.g. '10.20387/bonares-1a58-yk35'"}},
                     "required": ["dataset", "doi"]},
    ),
    types.Tool(
        name="fair_get_failed_metrics",
        description="Get only the metrics where a dataset scored 0 (failed). Use this to generate targeted improvement recommendations.",
        inputSchema={"type": "object",
                     "properties": {"dataset": {"type": "string"}, "doi": {"type": "string"}},
                     "required": ["dataset", "doi"]},
    ),
    types.Tool(
        name="fair_get_dimension_scores",
        description="Get the average FAIR score per dimension (Findability, Accessibility, Interoperability, Reusability) for a dataset as a quick overview.",
        inputSchema={"type": "object",
                     "properties": {"dataset": {"type": "string"}, "doi": {"type": "string"}},
                     "required": ["dataset", "doi"]},
    ),
    types.Tool(
        name="fair_list_assessed_datasets",
        description="List all datasets that have been FAIR-assessed and stored in Fuseki, with titles, DOI URLs, and assessment timestamps.",
        inputSchema={"type": "object",
                     "properties": {"dataset": {"type": "string"}},
                     "required": ["dataset"]},
    ),
    types.Tool(
        name="fair_compare_datasets",
        description="Compare FAIR dimension scores between two datasets side by side using their DOIs.",
        inputSchema={"type": "object",
                     "properties": {"dataset": {"type": "string"},
                                    "doi1": {"type": "string"}, "doi2": {"type": "string"}},
                     "required": ["dataset", "doi1", "doi2"]},
    ),
    types.Tool(
        name="fair_compare_services",
        description="Compare average scores given by FUJI vs FAIREvaluationServices (FES) for a dataset.",
        inputSchema={"type": "object",
                     "properties": {"dataset": {"type": "string"}, "doi": {"type": "string"}},
                     "required": ["dataset", "doi"]},
    ),
]


@app.list_tools()
async def list_tools() -> list[types.Tool]:
    return TOOLS


@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[types.TextContent]:
    try:
        match name:
            case "sparql_select":   result = await sparql_query(arguments["dataset"], arguments["query"])
            case "sparql_update":   result = await sparql_update(arguments["dataset"], arguments["update"])
            case "list_datasets":   result = await list_datasets()
            case "ping_fuseki":     result = await ping()
            case "fair_get_summary":          result = await get_fair_summary(arguments["dataset"], arguments["doi"])
            case "fair_get_failed_metrics":   result = await get_failed_metrics(arguments["dataset"], arguments["doi"])
            case "fair_get_dimension_scores": result = await get_dimension_scores(arguments["dataset"], arguments["doi"])
            case "fair_list_assessed_datasets": result = await list_assessed_datasets(arguments["dataset"])
            case "fair_compare_datasets":     result = await compare_datasets(arguments["dataset"], arguments["doi1"], arguments["doi2"])
            case "fair_compare_services":     result = await get_service_comparison(arguments["dataset"], arguments["doi"])
            case _: raise ValueError(f"Unknown tool: {name}")

        return [types.TextContent(type="text", text=json.dumps(result, indent=2))]
    except Exception as e:
        return [types.TextContent(type="text", text=f"Error: {e}")]


async def main():
    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, app.create_initialization_options())

if __name__ == "__main__":
    asyncio.run(main())