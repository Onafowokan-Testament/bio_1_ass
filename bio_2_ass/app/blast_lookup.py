from __future__ import annotations

import re
from typing import List

import requests


def _parse_title(title: str) -> tuple[str, str, str]:
    protein_name = title
    organism = "Unknown organism"
    function_hint = "No concise functional annotation available in this hit title."

    organism_match = re.search(r"\[(.+?)\]", title)
    if organism_match:
        organism = organism_match.group(1)

    if " " in title:
        protein_name = title.split(" ", 1)[1]

    if " OS=" in title:
        protein_name = title.split(" OS=", 1)[0]

    if " GN=" in title:
        function_hint = (
            f"Likely related to gene {title.split(' GN=', 1)[1].split(' ', 1)[0]}."
        )

    return protein_name.strip(), organism.strip(), function_hint


def uniprot_lookup(protein_sequence: str, max_hits: int = 5) -> List[dict]:
    if len(protein_sequence) < 8:
        return []

    url = "https://rest.uniprot.org/uniprotkb/search"
    params = {
        "query": f"sequence:{protein_sequence}",
        "format": "json",
        "size": max_hits,
        "fields": "accession,protein_name,organism_name,cc_function",
    }

    try:
        response = requests.get(url, params=params, timeout=20)
        response.raise_for_status()
        data = response.json()
    except requests.RequestException:
        return []

    hits: List[dict] = []
    for item in data.get("results", []):
        accession = item.get("primaryAccession", "")
        protein_desc = item.get("proteinDescription", {})
        rec_name = (
            protein_desc.get("recommendedName", {})
            .get("fullName", {})
            .get("value", "Unknown protein")
        )
        organism = item.get("organism", {}).get("scientificName", "Unknown organism")

        function_hint = (
            "Function annotation not available in the returned UniProt fields."
        )
        comments = item.get("comments", [])
        for comment in comments:
            if comment.get("commentType") == "FUNCTION":
                texts = comment.get("texts", [])
                if texts:
                    function_hint = texts[0].get("value", function_hint)
                    break

        hits.append(
            {
                "protein_name": str(rec_name),
                "organism": str(organism),
                "function": function_hint,
                "accession": str(accession),
            }
        )

    return hits
