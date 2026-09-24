#!/usr/bin/env python3
import os
import re
import gzip
import time
import json
import zipfile
import urllib
import urllib.request
import urllib.error
import subprocess
from argparse import ArgumentParser
import requests
import rich
import concurrent.futures as futures
import pandas as pd
from rdflib import Graph

import hashlib

emso_branch = "develop"

owner_repo = "emso-eric/emso-metadata-specifications"
raw_github = f"https://raw.githubusercontent.com/{owner_repo}"

# ---------------------------------------------------------------------------------------------------------------
# Two manifests are generated, one per governance axis:
#
#   manifest.json      -> normative Markdown authored by EMSO ERIC. Changes only when EMSO makes a decision, so it
#                         is versioned with the repository tags. Indexed from git, no downloads involved.
#   vocabularies.json  -> vocabularies governed by third parties (NVS/SeaDataNet, Copernicus). Refreshed on their
#                         own cadence, independently of the specifications version, so there is a single current
#                         snapshot served from the develop branch.
#
# resources.json (legacy, v1 format) is still written for harmonizer <= 1.0.9. Do not remove it until those
# clients are gone.
# ---------------------------------------------------------------------------------------------------------------

# Normative documents, as (manifest key, repo-relative path, description). Paths are relative to the repository
# root, NOT to this script's working directory.
normative_documents = [
    ("EMSO_Metadata_Specifications", "EMSO_Metadata_Specifications.md",
     "Normative global/variable attribute tables and valid coordinates."),
    ("OceanSites_codes", "external-resources/oceansites/OceanSites_codes.md",
     "EMSO-curated subset of OceanSITES reference tables (sensor mount/orientation, data modes/types, "
     "parameter codes)."),
    ("DataCite_codes", "external-resources/datacite/DataCite_codes.md",
     "EMSO-curated subset of DataCite contributor types."),
    ("Data_Processing_Levels", "Data_Processing_Levels.md",
     "Normative data processing levels and steps."),
]

# Only tags at or above this version are indexed in manifest.json. Earlier tags predate the current layout.
min_indexed_version = (1, 0, 0)

version_regex = re.compile(r"^v?(\d+)\.(\d+)(?:\.(\d+))?$")

# Provenance and licensing for everything published in vocabularies.json.
#
# The licence is recorded per resource because most of this content is CC BY, which requires attribution and a
# statement of what was modified. Publishing it here means the obligation travels with the data instead of
# living only in a README, and downstream tools can surface it.
#
#   title, governed_by, source, licence (SPDX id), licence url, modifications
vocabulary_provenance = {
    "P01": ("BODC Parameter Usage Vocabulary", "NERC Vocabulary Server (NVS) / SeaDataNet"),
    "P02": ("SeaDataNet Parameter Discovery Vocabulary", "NERC Vocabulary Server (NVS) / SeaDataNet"),
    "P06": ("BODC-approved data storage units", "NERC Vocabulary Server (NVS) / SeaDataNet"),
    "P07": ("Climate and Forecast Standard Names", "NERC Vocabulary Server (NVS) / SeaDataNet"),
    "L05": ("SeaDataNet device categories", "NERC Vocabulary Server (NVS) / SeaDataNet"),
    "L06": ("SeaVoX Platform Categories", "NERC Vocabulary Server (NVS) / SeaDataNet"),
    "L22": ("SeaVoX Device Catalogue", "NERC Vocabulary Server (NVS) / SeaDataNet"),
    "L35": ("SenseOcean device developers and manufacturers", "NERC Vocabulary Server (NVS) / SeaDataNet"),
}

cc_by_4 = ("CC-BY-4.0", "https://creativecommons.org/licenses/by/4.0/")
cc_by_3 = ("CC-BY-3.0", "https://creativecommons.org/licenses/by/3.0/")
cc0 = ("CC0-1.0", "https://creativecommons.org/publicdomain/zero/1.0/")
public_domain = ("PD-US-GOV", "https://www.earthdata.nasa.gov/engage/open-data-services-software-policies")

sdn_modifications = "JSON-LD converted to CSV; broader/narrower/related relations extracted into JSON files."

# licence per resource key: (spdx id, licence url, modifications statement)
resource_licences = {
    **{code: (*cc_by_4, sdn_modifications) for code in vocabulary_provenance},
    "EDMO": (*cc_by_4, "SPARQL JSON results converted to CSV."),
    "Copernicus Parameters": (*cc_by_4, "XLSX parameter list converted to a Markdown table, columns subset."),
    "GCMD": (*public_domain,
             "Paginated RDF pages merged into one graph; concepts extracted to CSV with prefLabel expanded to "
             "the full hierarchical path."),
    "GEMET": (*cc_by_4, "Gzipped RDF decompressed, empty xsd:dateTime literals removed, concepts extracted to CSV."),
    "EuroSciVoc": (*cc_by_4, "SKOS-XL RDF converted to CSV (concept URI and English preferred label)."),
    "OSO": (*cc_by_4, "Turtle ontology converted to CSV tables; platform/site/regional-facility relations "
                      "resolved into a lookup table."),
    "ROR": (*cc0, "Zenodo CSV data dump subset to five columns (id, ror_display, acronym, country_name, "
                  "website); nested-schema column names shortened to their last path segment. Values "
                  "unchanged."),
    "spdx_licenses": (*cc_by_3, "Redistributed verbatim."),
    "dwc_terms": (*cc_by_4, "Columns subset to term_localName and term_iri."),
}

# Externally governed vocabularies that are NOT SeaDataNet: (title, governed_by, source)
keyword_vocabulary_provenance = {
    "GCMD": ("NASA Global Change Master Directory Science Keywords", "NASA Earthdata",
             "https://www.earthdata.nasa.gov/data/tools/gcmd-keyword-viewer"),
    "GEMET": ("GEneral Multilingual Environmental Thesaurus", "European Environment Agency / Eionet",
              "https://www.eionet.europa.eu/gemet/"),
    "EuroSciVoc": ("European Science Vocabulary", "Publications Office of the European Union",
                   "https://op.europa.eu/en/web/eu-vocabularies/euroscivoc"),
    "OSO": ("Observatories of the Seas Ontology", "EMSO ERIC",
            "https://github.com/emso-eric/oso-ontology"),
    "ROR": ("Research Organization Registry", "ROR (Research Organization Registry)",
            "https://doi.org/10.5281/zenodo.6347574"),
}

sdn_vocab_p01_url = "https://vocab.nerc.ac.uk/downloads/publish/P01.json"
sdn_vocab_p02_url = "https://vocab.nerc.ac.uk/collection/P02/current/?_profile=nvs&_mediatype=application/ld+json"
sdn_vocab_p06_url = "https://vocab.nerc.ac.uk/collection/P06/current/?_profile=nvs&_mediatype=application/ld+json"
sdn_vocab_p07_url = "https://vocab.nerc.ac.uk/collection/P07/current/?_profile=nvs&_mediatype=application/ld+json"
sdn_vocab_l05_url = "https://vocab.nerc.ac.uk/collection/L05/current/?_profile=nvs&_mediatype=application/ld+json"
sdn_vocab_l06_url = "https://vocab.nerc.ac.uk/collection/L06/current/?_profile=nvs&_mediatype=application/ld+json"
sdn_vocab_l22_url = "https://vocab.nerc.ac.uk/collection/L22/current/?_profile=nvs&_mediatype=application/ld+json"
sdn_vocab_l35_url = "https://vocab.nerc.ac.uk/collection/L35/current/?_profile=nvs&_mediatype=application/ld+json"
# standard_names = "https://vocab.nerc.ac.uk/standard_name/?_profile=nvs&_mediatype=application/ld+json"

edmo_codes_url = "https://edmo.seadatanet.org/sparql/sparql?query=SELECT%20%3Fs%20%3Fp%20%3Fo%20WHERE%20%7B%20%0D%0A%0" \
                 "9%3Fs%20%3Fp%20%3Fo%20%0D%0A%7D%20LIMIT%201000000&accept=application%2Fjson"

# EDMO SPARQL endpoints fails, so use instead static CSV at github

spdx_licenses_github = "https://raw.githubusercontent.com/spdx/license-list-data/main/licenses.md"

# Copernicus INS TAC Parameter list v3.2
copernicus_param_list = "https://archimer.ifremer.fr/doc/00422/53381/108480.xlsx"

cf_standard_name_units_url = "https://cfconventions.org/Data/cf-standard-names/90/src/cf-standard-name-table.xml"

dwc_terms_url = "https://raw.githubusercontent.com/tdwg/dwc/refs/heads/master/vocabulary/term_versions.csv"

edmo_codes_jsonld = ".temp/edmo_codes_jsonld.json"

oso_ontology_url = "https://raw.githubusercontent.com/emso-eric/oso-ontology/refs/heads/main/OSO.ttl"

oceansites_codes_url = f"https://raw.githubusercontent.com/emso-eric/emso-metadata-specifications/{emso_branch}/external-resources/oceansites/OceanSites_codes.md"
datacite_codes_url = f"https://raw.githubusercontent.com/emso-eric/emso-metadata-specifications/{emso_branch}/external-resources/datacite/DataCite_codes.md"

# ---------------------------------------------------------------------------------------------------------------
# Keyword vocabularies and OSO.
#
# These used to be downloaded and parsed by the harmonizer at runtime, which meant every user re-downloaded and
# re-parsed ~20 MB of RDF on a cold cache. The RDF handling now lives here: the graphs are queried once and the
# results published as plain CSV/JSON, so the harmonizer only ever reads pre-parsed files and does not need
# rdflib at all.
#
# Raw RDF/TTL stays in .temp/ and is deliberately NOT committed: only the parsed outputs are published.
# ---------------------------------------------------------------------------------------------------------------

# GCMD is served paginated, the pages are merged into a single graph
gcmd_urls = [
    "https://cmr.earthdata.nasa.gov/kms/concepts/concept_scheme/sciencekeywords/?format=rdf&page_num=1&page_size=2000",
    "https://cmr.earthdata.nasa.gov/kms/concepts/concept_scheme/sciencekeywords/?format=rdf&page_num=2&page_size=2000",
]
gcmd_alternative_urls = [
    "https://files.obsea.es/other/vocabs/gcmd_part0.rdf",
    "https://files.obsea.es/other/vocabs/gcmd_part1.rdf",
]
gcmd_concept_prefix = "https://cmr.earthdata.nasa.gov/kms/concept/"

gemet_url = "https://www.eionet.europa.eu/gemet/latest/gemet.rdf.gz"
gemet_alternative_url = "https://files.obsea.es/other/vocabs/gemet.rdf.gz"

euroscivoc_url = ("https://op.europa.eu/o/opportal-service/euvoc-download-handler?cellarURI=http%3A%2F%2F"
                  "publications.europa.eu%2Fresource%2Fdistribution%2Feuroscivoc%2F20250924-0%2Frdf%2Fskos_xl"
                  "%2FEuroSciVoc.rdf&fileName=EuroSciVoc.rdf")
euroscivoc_alternative_url = "https://files.obsea.es/other/vocabs/EuroSciVoc.rdf"

# OSO. The harmonizer used to reference two files, OSO.ttl and docs/ontology.ttl, but only ever parsed the
# latter: OSO.__init__ set self.graph from docs/ontology.ttl before calling load_vocab(), so the OSO.ttl
# download was discarded without being read. Both the concepts and the instances come from this single file.
oso_ontology_url = "https://raw.githubusercontent.com/emso-eric/oso-ontology/refs/heads/main/docs/ontology.ttl"

# ROR (Research Organization Registry). Published as periodic data dumps on Zenodo under a single concept DOI
# (10.5281/zenodo.6347574); the API resolves that to the newest version, so no release has to be hardcoded.
# Mirroring it replaces a live HTTPS request the harmonizer used to make per validated ROR identifier.
ror_zenodo_concept_id = "6347574"
ror_zenodo_api = "https://zenodo.org/api/records"

# Columns kept from the ROR CSV dump. The dump ships 35 columns of nested-schema paths; only these are useful
# downstream. Names are shortened to their last path segment (locations.geonames_details.country_name ->
# country_name).
ror_columns = [
    "id",
    "names.types.ror_display",
    "names.types.acronym",
    "locations.geonames_details.country_name",
    "links.type.website",
]

oso_class_uris = {
    "platforms": "https://w3id.org/earthsemantics/OSO#Platform",
    "sites": "https://w3id.org/earthsemantics/OSO#Site",
    "rfs": "https://w3id.org/earthsemantics/OSO#RegionalFacility",
}

# SPARQL used to extract concept/label pairs. Kept identical to what the harmonizer used to run at startup so
# the published CSVs are byte-compatible with the previous in-memory results.
sparql_generic_concepts = """
    PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

    SELECT ?concept ?prefLabel
    WHERE {
        ?concept rdf:type skos:Concept .
        OPTIONAL {
            ?concept skos:prefLabel ?prefLabel .
            FILTER(lang(?prefLabel) = "en")
        }
    }
    """

sparql_euroscivoc_concepts = """
    PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
    PREFIX skosxl: <http://www.w3.org/2008/05/skos-xl#>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

    SELECT ?concept ?prefLabel
    WHERE {
        ?concept rdf:type skos:Concept .
        OPTIONAL {
            ?concept skosxl:prefLabel/skosxl:literalForm ?prefLabel .
            FILTER(lang(?prefLabel) = "en")
        }
    }
    """

sparql_gemet_concepts = """
    PREFIX skos: <http://www.w3.org/2004/02/skos/core#>

    SELECT DISTINCT ?concept ?prefLabel
    WHERE {
        ?concept skos:prefLabel ?prefLabel .
        FILTER(lang(?prefLabel) = "en")
        FILTER(CONTAINS(STR(?concept), "/concept/"))
    }
    ORDER BY ?prefLabel
    """

sparql_oso_concepts = """
    PREFIX skos: <http://www.w3.org/2004/02/skos/core#>

    SELECT DISTINCT ?concept ?prefLabel
    WHERE {
        ?concept skos:prefLabel ?prefLabel .
        FILTER (lang(?prefLabel) = "en")
    }
    ORDER BY ?prefLabel
    """

sparql_skos_relations = """
    PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
    SELECT ?concept ?label ?broader ?narrower ?related
    WHERE {
        ?concept a skos:Concept .
        OPTIONAL { ?concept skos:prefLabel ?label . FILTER(lang(?label) = "en") }
        OPTIONAL { ?concept skos:broader ?broader . }
        OPTIONAL { ?concept skos:narrower ?narrower . }
        OPTIONAL { ?concept skos:related ?related . }
    }
    """


def get_file_md5(filename):
    md5_hash = hashlib.md5()
    with open(filename, 'rb') as f:
        for chunk in iter(lambda: f.read(65536), b""):
            md5_hash.update(chunk)

    return md5_hash.hexdigest()


def __threadify_index_handler(index, handler, args):
    """
    This function adds the index to the return of the handler function. Useful to sort the results of a
    multithreaded operation
    :param index: index to be returned
    :param handler: function handler to be called
    :param args: list with arguments of the function handler
    :return: tuple with (index, xxx) where xxx is whatever the handler function returned
    """
    result = handler(*args)  # call the handler
    return index, result  # add index to the result


def threadify(arg_list, handler, max_threads=10):
    """
    Splits a repetitive task into several threads
    :param arg_list: each element in the list will crate a thread and its contents passed to the handler
    :param handler: function to be invoked by every thread
    :param max_threads: Max threads to be launched at once
    :return: a list with the results (ordered as arg_list)
    """
    index = 0  # thread index
    with futures.ThreadPoolExecutor(max_workers=max_threads) as executor:
        threads = []  # empty thread listimport concurrent.futures as futures

        results = []  # empty list of thread results
        for args in arg_list:
            # submit tasks to the executor and append the tasks to the thread list
            threads.append(executor.submit(__threadify_index_handler, index, handler, args))
            index += 1

        # wait for all threads to end
        for future in futures.as_completed(threads):
            future_result = future.result()  # result of the handler
            results.append(future_result)

        # sort the results by the index added by __threadify_index_handler
        sorted_results = sorted(results, key=lambda a: a[0])

        final_results = []  # create a new array without indexes
        for result in sorted_results:
            final_results.append(result[1])
        return final_results


def download_files(tasks, force_download=False):
    if len(tasks) == 1:
        return None
    args = []
    for url, file, name in tasks:
        if os.path.isfile(file) and not force_download:
            pass
        else:
            args.append((url, file))
    threadify(args, download_file)


def download_file(url, file):
    """
    wrapper for urllib.error.HTTPError
    """
    rich.print(f"downloading {file}...")
    try:
        a = urllib.request.urlretrieve(url, file)
        rich.print(f"{file} done!")
        return a
    except urllib.error.HTTPError as e:
        rich.print(f"[red]{str(e)}")
        rich.print(f"[red]Could not download from {url} to file {file}")
        raise e


def download_edmo(url, file, force_download=False):
    """
    EMDO endpoint is a bit picky, so we will create some custom user agent
    """

    headers = {
        #        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'User-Agent': 'Custom agent',
    }

    if not force_download and os.path.exists(file):
        return
    r = requests.get(url, headers=headers, stream=True)
    if r.status_code > 299:
        rich.print(r.text)
        raise ValueError(f"ERROR {r.status_code}")
    with open(file, "w") as f:
        f.write(r.text)


def load_sdn_vocab(filename):
    """
    Loads a SDN vocab into a pandas dataframe.
    """
    data, narrower, broader, related = parse_sdn_jsonld(filename)

    df = pd.DataFrame(data)
    df = df.rename(columns={"@id": "uri", "dc:identifier": "id"})
    return df, narrower, broader, related


def parse_sdn_jsonld(filename):
    """
    Opens a JSON-LD file from SeaDataNet and try to process it.
    :param filename: file path
    :returns: data (dict), narrower (list), broader (list), related (list)
    """
    with open(filename, encoding="utf-8") as f:
        contents = json.load(f)

    data = {
        "uri": [],
        "identifier": [],
        "prefLabel": [],
        "definition": [],
        "altLabel": []
    }

    alias = {  # key-> key to be stored in data dict, value -> all possible keys found in JSON-LD docs
        "definition": ["definition", "skos:definition"],
        "prefLabel": ["prefLabel", "skos:prefLabel"],
        "identifier": ["dc:identifier", "dce:identifier"],
        "altLabel": ["altLabel", "skos:altLabel"],
        "uri": ["@id"]
    }

    def get_value_by_alias(mydict, mykey):
        if mykey not in alias.keys():
            return mydict[mykey]
        for try_alias in alias[mykey]:
            try:
                return mydict[try_alias]
            except KeyError:
                pass
        return None

    narrower = {}
    broader = {}
    related = {}
    for element in contents["@graph"]:
        uri = element["@id"]
        if element["@type"] != "skos:Concept":
            continue
        for key in data.keys():
            value = get_value_by_alias(element, key)
            if type(value) == type(None):
                # Check that it is explicitly NoneType
                continue
            if type(value) is dict:
                value = value["@value"]
            elif type(value) is list:
                value = value[0]

            data[key].append(value)

        # Initialize as empty list
        narrower[uri] = []
        broader[uri] = []
        related[uri] = []

        def extract_related_elements(mydict, mykeys):
            for mykey in mykeys:
                if mykey not in mydict.keys():
                    continue
                if isinstance(mydict[mykey], dict):
                    return [mydict[mykey]["@id"]]  # generate a dict with the dict value
                elif isinstance(mydict[mykey], list):
                    newlist = []
                    for nested_value in mydict[mykey]:
                        if isinstance(nested_value, dict):
                            newlist.append(nested_value["@id"])
                        else:
                            newlist.append(nested_value)
                    return newlist
                elif isinstance(mydict[mykey], str):
                    return [mydict[mykey]]  # generate a list with the string
                else:
                    raise ValueError(f"Type {type(mydict[mykey])} not expected")
            return []

        # If present, store relationships
        narrower[uri] = extract_related_elements(element, ["skos:narrower", "narrower"])
        broader[uri] = extract_related_elements(element, ["skos:broader", "broader"])
        related[uri] = extract_related_elements(element, ["skos:related", "related"])

    # Remove prefixes like skos and dce
    prefixes = ["skos:", "dce:", "dc:"]
    for p in prefixes:
        for key in list(data.keys()):
            if key.startswith(p):
                new_key = key.replace(p, "")
                data[new_key] = data.pop(key)

    if "@id" in data.keys():
        data["uri"] = data.pop("@id")
    if "identifier" in data.keys():
        data["id"] = data.pop("identifier")

    return data, narrower, broader, related


def get_edmo_codes(file):
    with open(file, encoding="utf-8") as f:
        data = json.load(f)

    codes = []
    uris = []
    names = []
    for element in data["results"]["bindings"]:
        if element["p"]["value"] == "http://www.w3.org/ns/org#name":
            code = int(element["s"]["value"].split("/")[-1])
            uris.append(element["s"]["value"])
            codes.append(code)
            names.append(element["o"]["value"])

    df = pd.DataFrame({
        "uri": uris,
        "code": codes,
        "name": names,
    })
    return df


def dataframe_to_markdown(df, title, markdown_file):
    # 1. Create the Header Row
    headers = "| " + " | ".join(map(str, df.columns)) + " |"

    # 2. Create the Separator Row (the --- | --- part)
    separator = "| " + " | ".join(["---"] * len(df.columns)) + " |"

    # 3. Create Data Rows using iterrows
    body = []
    for _, row in df.iterrows():
        # Convert each element to string and join with pipes
        row_str = "| " + " | ".join(map(str, row.values)) + " |"
        body.append(row_str)

    # 4. Combine everything
    markdown_table = "\n".join([f"# {title}", "", headers, separator] + body)

    # 5. Write to file
    with open(markdown_file, "w", encoding="utf-8") as f:
        f.write(markdown_table)


# ================================================================================================ vocabularies
# RDF handling. Everything below used to live in the harmonizer's vocabularies.py and ran on every cold start.

def as_str(value):
    """
    Normalise an rdflib term to a plain str.

    This must be unconditional. rdflib's URIRef subclasses str but overrides __eq__ to be type-strict, so a
    URIRef and an equal str hash the same yet compare unequal - which silently breaks every dict lookup that
    mixes the two. A guard like `if not isinstance(a, str)` never fires for URIRef and is exactly the trap
    that produced KeyErrors when these relations were built at runtime.
    """
    return str(value) if value is not None else ""


def resolve_concept_uri(uri, concept_prefix=""):
    """
    Some graphs yield file:// URIs when parsed locally; rewrite them onto the vocabulary's concept prefix.
    """
    uri = as_str(uri)
    if uri.startswith("file:") and concept_prefix:
        return concept_prefix + uri.split("/")[-1]
    return uri


def download_with_fallback(url, file, alternative=""):
    """
    Download url, falling back to a mirror when the primary source refuses (several of these publishers block
    automated downloads intermittently).
    """
    os.makedirs(os.path.dirname(file) or ".", exist_ok=True)
    try:
        download_file(url, file)
    except Exception as e:
        if not alternative:
            raise
        rich.print(f"[yellow]primary source failed ({e}), trying mirror {alternative}")
        download_file(alternative, file)


def download_gemet_rdf(file, force_download=False):
    """
    GEMET ships gzipped, and its XML contains empty dateTime literals that rdflib refuses to parse.
    """
    if os.path.isfile(file) and not force_download:
        return
    gzip_file = os.path.join(".temp", "gemet.rdf.gz")
    rich.print("Downloading GEMET (gzip)...", end="")
    download_with_fallback(gemet_url, gzip_file, alternative=gemet_alternative_url)
    with gzip.open(gzip_file, "rt", encoding="utf-8") as f:
        content = f.read()
    for tag in ("created", "modified"):
        content = content.replace(
            f'rdf:datatype="http://www.w3.org/2001/XMLSchema#dateTime"></dcterms:{tag}>',
            f'></dcterms:{tag}>')
    with open(file, "w", encoding="utf-8") as f:
        f.write(content)
    rich.print("[green]done!")


def download_gcmd_rdf(file, force_download=False):
    """
    GCMD is served paginated; download every page and merge them into one RDF graph.
    """
    if os.path.isfile(file) and not force_download:
        return
    graph = None
    for i, (url, alternative) in enumerate(zip(gcmd_urls, gcmd_alternative_urls)):
        part = os.path.join(".temp", f"gcmd_part{i}.rdf")
        rich.print(f"Downloading GCMD part {i}...", end="")
        download_with_fallback(url, part, alternative=alternative)
        rich.print("[green]done!")
        part_graph = Graph()
        part_graph.parse(part, format="xml")
        graph = part_graph if graph is None else graph + part_graph
    graph.serialize(destination=file, format="xml")


def graph_concepts(graph, query, concept_prefix=""):
    """
    Run a concept/prefLabel query and return parallel lists of plain-str uris and labels.
    """
    uris, labels = [], []
    for row in graph.query(query):
        uris.append(resolve_concept_uri(row.concept, concept_prefix))
        labels.append(as_str(row.prefLabel) if row.prefLabel else "")
    return uris, labels


def graph_relations(graph, concept_prefix=""):
    """
    Extract broader / narrower / related as {uri: [uri, ...]} with plain-str keys and values.
    """
    broader, narrower, related = {}, {}, {}
    for row in graph.query(sparql_skos_relations):
        c = resolve_concept_uri(row.concept, concept_prefix)
        for target, value in ((broader, row.broader), (narrower, row.narrower), (related, row.related)):
            target.setdefault(c, [])
            v = resolve_concept_uri(value, concept_prefix) if value else ""
            if v and v not in target[c]:
                target[c].append(v)
    return broader, narrower, related


def gcmd_hierarchical_labels(uris, labels, broader):
    """
    Expand every GCMD concept into its full path, e.g.
        "SEA CLIFFS" -> "EARTH SCIENCE > SOLID EARTH > ... > SEA CLIFFS"

    Precomputing this here is what lets the harmonizer drop the recursive broader-walk (and with it the whole
    relations machinery) from startup.
    """
    label_from_uri = {u: l for u, l in zip(uris, labels)}

    def build_term(uri, previous=""):
        label = label_from_uri.get(uri, "")
        if label == "Science Keywords":  # do not include the scheme root in the path
            return previous
        if previous:
            label = label + " > " + previous
        parents = broader.get(uri, [])
        if len(parents) == 0:
            return label + previous
        if len(parents) == 1:
            return build_term(parents[0], label)
        raise ValueError(f"Unexpected multiple broader for {uri}")

    return [build_term(uri) for uri in uris]


def write_vocab_csv(filename, uris, labels):
    os.makedirs(os.path.dirname(filename) or ".", exist_ok=True)
    pd.DataFrame({"uri": uris, "prefLabel": labels}).to_csv(filename, index=False)
    return filename


def process_keyword_vocabularies(force_download=False):
    """
    Download and parse GCMD, GEMET and EuroSciVoc, publishing one CSV per vocabulary.

    GCMD's CSV carries the full hierarchical path in prefLabel, which is what the harmonizer used to build at
    runtime, so its keyword matching is unchanged.
    """
    outputs = {}

    # ======== GCMD ======== #
    gcmd_rdf = os.path.join(".temp", "gcmd.rdf")
    download_gcmd_rdf(gcmd_rdf, force_download=force_download)
    rich.print("Parsing GCMD graph...", end="")
    graph = Graph()
    graph.parse(gcmd_rdf, format="xml")
    uris, labels = graph_concepts(graph, sparql_generic_concepts, gcmd_concept_prefix)
    broader, _, _ = graph_relations(graph, gcmd_concept_prefix)
    labels = gcmd_hierarchical_labels(uris, labels, broader)
    outputs["GCMD"] = write_vocab_csv(os.path.join("keywords", "gcmd", "gcmd.csv"), uris, labels)
    rich.print(f"[green]done! ({len(uris)} concepts)")

    # ======== GEMET ======== #
    gemet_rdf = os.path.join(".temp", "gemet.rdf")
    download_gemet_rdf(gemet_rdf, force_download=force_download)
    rich.print("Parsing GEMET graph...", end="")
    graph = Graph()
    graph.parse(gemet_rdf, format="xml")
    uris, labels = graph_concepts(graph, sparql_gemet_concepts)
    outputs["GEMET"] = write_vocab_csv(os.path.join("keywords", "gemet", "gemet.csv"), uris, labels)
    rich.print(f"[green]done! ({len(uris)} concepts)")

    # ======== EuroSciVoc ======== #
    euroscivoc_rdf = os.path.join(".temp", "euroscivoc.rdf")
    if not os.path.isfile(euroscivoc_rdf) or force_download:
        rich.print("Downloading EuroSciVoc...", end="")
        download_with_fallback(euroscivoc_url, euroscivoc_rdf, alternative=euroscivoc_alternative_url)
        rich.print("[green]done!")
    rich.print("Parsing EuroSciVoc graph...", end="")
    graph = Graph()
    graph.parse(euroscivoc_rdf, format="xml")
    uris, labels = graph_concepts(graph, sparql_euroscivoc_concepts)
    outputs["EuroSciVoc"] = write_vocab_csv(os.path.join("keywords", "euroscivoc", "euroscivoc.csv"), uris, labels)
    rich.print(f"[green]done! ({len(uris)} concepts)")

    return outputs


def process_ror(force_download=False):
    """
    Download the latest ROR data dump from Zenodo and publish the subset the harmonizer needs.

    The dump is a ~37 MB zip containing a full JSON and a 55 MB CSV; only five columns of the CSV are kept,
    which brings the published file down to ~15 MB. Values are left exactly as ROR publishes them (including
    the "no_lang_code: " / "en: " language prefixes on name fields and ";"-separated multi-valued acronyms).
    """
    csv_out = os.path.join("ror", "ror.csv")
    zip_file = os.path.join(".temp", "ror-data.zip")

    if not os.path.isfile(zip_file) or force_download:
        rich.print("Resolving latest ROR release on Zenodo...", end="")
        with urllib.request.urlopen(f"{ror_zenodo_api}/{ror_zenodo_concept_id}") as response:
            concept = json.load(response)
        with urllib.request.urlopen(concept["links"]["latest"]) as response:
            record = json.load(response)
        dump = next(f for f in record["files"] if f["key"].endswith(".zip"))
        rich.print(f"[green] {record['metadata']['title']} {dump['key']}")
        rich.print(f"Downloading ROR dump ({dump['size'] / 1e6:.0f} MB)...", end="")
        download_file(dump["links"]["self"], zip_file)
        rich.print("[green]done!")

    rich.print("Extracting ROR CSV...", end="")
    with zipfile.ZipFile(zip_file) as archive:
        name = next(n for n in archive.namelist() if n.endswith(".csv"))
        with archive.open(name) as f:
            df = pd.read_csv(f, usecols=ror_columns, low_memory=False)

    # Shorten the nested-schema column names, keeping the requested order
    df = df.rename(columns={c: c.split(".")[-1] for c in ror_columns})
    df = df[[c.split(".")[-1] for c in ror_columns]]

    os.makedirs(os.path.dirname(csv_out), exist_ok=True)
    df.to_csv(csv_out, index=False)
    rich.print(f"[green]done! ({len(df):,} organisations)")
    return {"csv": csv_out}


def process_oso(force_download=False):
    """
    Publish OSO as plain tables so the harmonizer needs no RDF at runtime:

        oso.csv                SKOS concepts used for keyword validation
        platforms/sites/rfs    instances with their labels
        platform_metadata.json platform uri -> {site, regional facility}

    The last one replaces a per-platform SPARQL query the harmonizer ran on demand. The platform set is finite,
    so the whole mapping is resolved here in a single query.
    """
    outputs = {}

    ontology_ttl = os.path.join(".temp", "oso_ontology.ttl")
    if not os.path.isfile(ontology_ttl) or force_download:
        rich.print("Downloading OSO ontology...", end="")
        download_with_fallback(oso_ontology_url, ontology_ttl)
        rich.print("[green]done!")
    rich.print("Parsing OSO ontology...", end="")
    graph = Graph().parse(ontology_ttl)

    # ======== concepts ======== #
    uris, labels = graph_concepts(graph, sparql_oso_concepts)
    outputs["csv"] = write_vocab_csv(os.path.join("oso", "oso.csv"), uris, labels)

    # ======== instances ======== #

    for name, class_uri in oso_class_uris.items():
        query = f"""
            SELECT ?instance ?label
            WHERE {{
                ?instance a <{class_uri}> .
                OPTIONAL {{ ?instance rdfs:label ?label . }}
            }}
            """
        rows = [{"uri": as_str(row.instance), "label": as_str(row.label)} for row in graph.query(query)]
        df = pd.DataFrame(rows, columns=["uri", "label"]).drop_duplicates(keep="first")
        filename = os.path.join("oso", f"{name}.csv")
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        df.to_csv(filename, index=False)
        outputs[name] = filename

    # ======== platform -> site / regional facility ======== #
    query = """
        PREFIX OSO: <https://w3id.org/earthsemantics/OSO#>
        PREFIX skos: <http://www.w3.org/2004/02/skos/core#>

        SELECT ?platform ?siteName ?rfName WHERE {
            ?site OSO:containsPlatform ?platform .
            ?site skos:prefLabel ?siteName .
            OPTIONAL {
                ?rf OSO:containsSite ?site .
                ?rf skos:prefLabel ?rfName .
                FILTER (LANG(?rfName) = "en")
            }
            FILTER (LANG(?siteName) = "en")
        }
        """
    platform_metadata = {}
    for row in graph.query(query):
        platform = as_str(row.platform)
        if platform in platform_metadata:
            continue  # the harmonizer's query used LIMIT 1, keep the first match
        platform_metadata[platform] = {
            "site": as_str(row.siteName),
            "regional_facility": as_str(row.rfName) if row.rfName else "",
        }

    filename = os.path.join("oso", "platform_metadata.json")
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(platform_metadata, f, indent=2, ensure_ascii=False)
    outputs["platform_metadata"] = filename
    rich.print(f"[green]done! ({len(platform_metadata)} platforms mapped)")

    return outputs


def repo_root():
    """
    Absolute path of the repository root. This script runs from external-resources/, but manifests store
    repository-relative paths so that base_url + path resolves on any ref or mirror.
    """
    return os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))


def git(*args, binary=False):
    """
    Run a git command in the repository. Returns None if git is unavailable or the command fails, so that a
    missing git never breaks a vocabulary refresh.
    """
    try:
        result = subprocess.run(["git", "-C", repo_root(), *args], capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError, OSError):
        return None
    return result.stdout if binary else result.stdout.decode("utf-8", "replace").strip()


def git_blob(ref, path):
    """
    Contents of a repository-relative path at a given ref, or None if it does not exist there.
    """
    return git("show", f"{ref}:{path}", binary=True)


def md5_bytes(data):
    return hashlib.md5(data).hexdigest()


def parse_version(tag):
    """
    Convert a tag into a sortable tuple, or None if it is not a version tag. 'v1.0.7' -> (1, 0, 7)
    """
    match = version_regex.match(tag)
    if not match:
        return None
    major, minor, patch = match.groups()
    return int(major), int(minor), int(patch) if patch else 0


def list_spec_versions():
    """
    Version tags at or above min_indexed_version, oldest first. Sorting is numeric, so v1.10.0 > v1.9.0.
    """
    tags = git("tag", "--list")
    if tags is None:
        return []
    versions = []
    for tag in tags.splitlines():
        tag = tag.strip()
        parsed = parse_version(tag)
        if parsed and parsed >= min_indexed_version:
            versions.append((parsed, tag))
    return [tag for _, tag in sorted(versions)]


def build_manifest():
    """
    Index every published version of the normative documents, reading content straight out of git. Tagged
    versions are immutable, so they carry an md5 the client can trust forever. The develop entry is mutable and
    carries md5 = null: any hash would be stale the moment something is pushed.

    Returns None if git is unavailable.
    """
    tags = list_spec_versions()
    if not tags:
        return None

    versions = {}
    for ref_name, ref, status, mutable in (
            [(tag, f"refs/tags/{tag}", "stable", False) for tag in tags]
            + [(emso_branch, f"refs/heads/{emso_branch}", "development", True)]):

        files = {}
        for key, path, description in normative_documents:
            data = git_blob(ref, path)
            if data is None:
                continue  # document does not exist at this version, clients must tolerate missing keys
            files[key] = {
                "path": path,
                "md5": None if mutable else md5_bytes(data),
                "bytes": None if mutable else len(data),
                "description": description,
            }

        if not files:
            continue

        versions[ref_name] = {
            "ref": ref,
            "released": None if mutable else git("log", "-1", "--format=%ad", "--date=short", ref),
            "status": status,
            "mutable": mutable,
            "base_url": f"{raw_github}/{ref}/",
            "files": files,
        }

    latest = tags[-1]
    return {
        "schema": "emso-specs-manifest/1",
        "title": "EMSO Metadata Specifications - normative document index",
        "description":
            "Index of every published version of the EMSO Metadata Specifications and the normative Markdown "
            "documents belonging to each. These documents are authored by EMSO ERIC and change only when EMSO "
            "makes a decision; they are versioned with the repository tags. Externally governed vocabularies "
            "(SeaDataNet/NVS, EDMO, Copernicus) are NOT listed here - see vocabularies.json.",
        "canonical_url": f"{raw_github}/refs/heads/main/external-resources/manifest.json",
        "latest": latest,
        "default": latest,
        "notes": [
            "Always fetch this file from canonical_url (a mutable ref). Copies of this file inside tags are "
            "frozen at tagging time and cannot list versions released later.",
            "Resolve a file as base_url + files.<key>.path",
            "Entries with mutable=true have md5=null: the content behind the ref can change at any time. "
            "Clients should apply a staleness policy (e.g. re-check after 24h) instead of trusting a hash.",
            "Entries with mutable=false are immutable: verify md5 once, then cache indefinitely.",
            "Versions before v1.0.4 have no Data_Processing_Levels; before v1.0.3 the OceanSITES tables were "
            "not yet split out. Clients must tolerate missing keys.",
            "Key names are fixed: OceanSites_codes maps to OceanSites_codes.md and DataCite_codes maps to "
            "DataCite_codes.md. This corrects a crossed mapping present in the legacy resources.json.",
            f"Versions older than v{'.'.join(str(n) for n in min_indexed_version)} are not indexed and are "
            "not supported.",
        ],
        "versions": versions,
    }


def file_entry(local_path):
    """
    Describe one published file. local_path is relative to this script (e.g. 'sdn/P01.csv') and is converted to
    the repository-relative path stored in the manifest.
    """
    with open(local_path, "rb") as f:
        data = f.read()
    return {
        "path": f"external-resources/{local_path}".replace(os.sep, "/"),
        "md5": md5_bytes(data),
        "bytes": len(data),
    }


def licence_fields(key):
    """
    Attribution block for a resource. CC BY requires credit, a link to the licence and a statement of changes,
    so all three are published rather than only the licence id.
    """
    spdx, url, modifications = resource_licences[key]
    return {"license": spdx, "license_url": url, "modifications": modifications}


def vocabulary_entry(title, governed_by, source, key, files):
    """
    One vocabularies.json resource. `files` maps a file key ("csv", "md", ...) to a path relative to this script.
    """
    return {
        "title": title,
        "governed_by": governed_by,
        "source": source,
        **licence_fields(key),
        "files": {name: file_entry(path) for name, path in files.items() if os.path.isfile(path)},
    }


def build_vocabularies():
    """
    Describe the single current snapshot of externally governed vocabularies, read from the files this script
    has just regenerated. There is deliberately no version selection here: these vocabularies are maintained by
    third parties and apply to every specifications version.
    """
    resources = {}

    # ======== SeaDataNet / NVS ======== #
    for vocab, (title, governed_by) in vocabulary_provenance.items():
        files = {"csv": os.path.join("sdn", f"{vocab}.csv")}
        for relation in ["narrower", "broader", "related"]:
            files[relation] = os.path.join("sdn", f"{vocab}.{relation}.json")
        resources[vocab] = vocabulary_entry(
            title, governed_by, f"https://vocab.nerc.ac.uk/collection/{vocab}/current/", vocab, files)

    resources["EDMO"] = vocabulary_entry(
        "European Directory of Marine Organisations", "SeaDataNet", "https://edmo.seadatanet.org/", "EDMO",
        {"csv": os.path.join("edmo", "EDMO.csv")})

    resources["Copernicus Parameters"] = vocabulary_entry(
        "Copernicus Marine In Situ TAC parameter list", "Copernicus Marine Service / Ifremer",
        copernicus_param_list, "Copernicus Parameters",
        {"md": os.path.join("copernicus", "copernicus_variables.md")})

    # ======== Keyword vocabularies ======== #
    # Published pre-parsed so the harmonizer never needs to touch RDF
    keyword_files = {
        "GCMD": {"csv": os.path.join("keywords", "gcmd", "gcmd.csv")},
        "GEMET": {"csv": os.path.join("keywords", "gemet", "gemet.csv")},
        "EuroSciVoc": {"csv": os.path.join("keywords", "euroscivoc", "euroscivoc.csv")},
        "OSO": {
            "csv": os.path.join("oso", "oso.csv"),
            "platforms": os.path.join("oso", "platforms.csv"),
            "sites": os.path.join("oso", "sites.csv"),
            "rfs": os.path.join("oso", "rfs.csv"),
            "platform_metadata": os.path.join("oso", "platform_metadata.json"),
        },
        "ROR": {"csv": os.path.join("ror", "ror.csv")},
    }
    for key, files in keyword_files.items():
        title, governed_by, source = keyword_vocabulary_provenance[key]
        entry = vocabulary_entry(title, governed_by, source, key, files)
        if entry["files"]:  # skip if this run did not regenerate them
            resources[key] = entry

    return {
        "schema": "emso-vocabularies/1",
        "title": "EMSO Metadata Specifications - external vocabulary snapshot",
        "description":
            "Pre-processed snapshot of externally governed vocabularies mirrored by EMSO ERIC. These "
            "vocabularies are maintained by third parties (NVS/SeaDataNet, Copernicus) and are refreshed on "
            "their own cadence, independently of the EMSO Metadata Specifications version. There is exactly "
            "one current snapshot: it is NOT selectable per specification version.",
        "canonical_url": f"{raw_github}/refs/heads/{emso_branch}/external-resources/vocabularies.json",
        "ref": f"refs/heads/{emso_branch}",
        "mutable": True,
        "snapshot_date": time.strftime("%Y-%m-%d"),
        "base_url": f"{raw_github}/refs/heads/{emso_branch}/",
        "notes": [
            "Resolve a file as base_url + resources.<key>.files.<name>.path",
            "This snapshot always tracks the tip of develop. It applies to every specification version; do not "
            "cache it under a version-specific key.",
            "md5 values describe the snapshot at the time this file was generated. Because the ref is mutable, "
            "a download whose md5 does not match means the snapshot moved: re-fetch this file. Clients should "
            "treat a mismatch as a cache-refresh signal, not an error.",
            "Re-check policy: compare this file's md5 values against the local cache; a 24h staleness window "
            "is sufficient given the refresh cadence (a few times per year).",
        ],
        "resources": resources,
    }


readme_marker_start = "<!-- BEGIN GENERATED ATTRIBUTION TABLE -->"
readme_marker_end = "<!-- END GENERATED ATTRIBUTION TABLE -->"


def write_attribution_readme(vocabularies, filename="README.md"):
    """
    Regenerate the attribution table in README.md from vocabularies.json.

    Most of this content is CC BY, which requires credit, a link to the licence and a statement of what was
    changed. Generating the table from the manifest means the three can never drift apart from what is actually
    published, which is the whole point of recording them per resource.
    """
    rows = ["| Resource | Description | Source | Licence | Modifications |",
            "|----------|-------------|--------|---------|---------------|"]
    for key, resource in vocabularies["resources"].items():
        licence = f"[{resource['license']}]({resource['license_url']})"
        rows.append(f"| `{key}` | {resource['title']} | [link]({resource['source']}) | {licence} "
                    f"| {resource['modifications']} |")

    table = "\n".join(rows)

    if not os.path.isfile(filename):
        rich.print(f"[yellow]{filename} not found, attribution table not written")
        return

    with open(filename, encoding="utf-8") as f:
        content = f.read()

    block = f"{readme_marker_start}\n\n{table}\n\n{readme_marker_end}"
    if readme_marker_start in content and readme_marker_end in content:
        head = content.split(readme_marker_start)[0]
        tail = content.split(readme_marker_end)[1]
        content = head + block + tail
    else:
        content = content.rstrip() + "\n\n" + block + "\n"

    with open(filename, "w", encoding="utf-8") as f:
        f.write(content)
    rich.print(f"[green]wrote attribution table for {len(vocabularies['resources'])} resources to {filename}")


def write_notice(vocabularies):
    """
    Regenerate the repository's NOTICE file.

    The root LICENSE is MIT and covers what EMSO ERIC authored. It cannot cover external-resources/, which
    redistributes third-party works under their own terms - NVS/SeaDataNet, GEMET, EuroSciVoc and Copernicus are
    CC BY, which requires attribution and a statement of changes. NOTICE is the conventional place to record
    that, and it sits at the repository root so it is findable without digging into subdirectories.
    """
    filename = os.path.join(repo_root(), "NOTICE")

    lines = [
        "EMSO Metadata Specifications",
        "Copyright 2026 EMSO ERIC",
        "",
        "This repository is licensed under the MIT License (see LICENSE). That licence covers the material",
        "authored by EMSO ERIC: the normative specifications, the reference tables under",
        "external-resources/oceansites/ and external-resources/datacite/, and the scripts in",
        "external-resources/.",
        "",
        "It does NOT cover the contents of external-resources/ that are mirrored from third parties. Those",
        "works remain under the licences of their respective publishers and are redistributed here unmodified",
        "in substance, reformatted as described below. Where a work is licensed CC BY, this file together with",
        "the per-resource fields in external-resources/vocabularies.json provides the required attribution,",
        "link to the licence, and indication of changes.",
        "",
        "This file is generated by external-resources/update_resources.py - do not edit it by hand.",
        "",
        "=" * 110,
        "",
    ]

    for key, resource in vocabularies["resources"].items():
        paths = sorted(f["path"] for f in resource["files"].values())
        lines += [
            f"{resource['title']} ({key})",
            f"    Publisher    : {resource['governed_by']}",
            f"    Source       : {resource['source']}",
            f"    Licence      : {resource['license']}  <{resource['license_url']}>",
            f"    Modifications: {resource['modifications']}",
            f"    Files        : {paths[0]}",
        ]
        lines += [f"                   {p}" for p in paths[1:]]
        lines.append("")

    lines += [
        "=" * 110,
        "",
        "The OceanSITES and DataCite reference tables under external-resources/ are EMSO ERIC's curated",
        "subsets of the OceanSITES data format reference tables and the DataCite Metadata Schema",
        "respectively, and are covered by the MIT licence above. The upstream standards are acknowledged:",
        "    OceanSITES  <https://www.ocean-ops.org/oceansites/>",
        "    DataCite    <https://schema.datacite.org/>",
        "",
    ]

    with open(filename, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    rich.print(f"[green]wrote NOTICE for {len(vocabularies['resources'])} third-party resources")


def write_json(filename, document):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(document, f, indent=2, ensure_ascii=False)
        f.write("\n")
    rich.print(f"[green]wrote {filename} ({os.path.getsize(filename)} bytes)")


if __name__ == "__main__":
    argparser = ArgumentParser(
        description="Refresh the external vocabularies and regenerate the resource manifests.")
    argparser.add_argument("-f", "--force-download", action="store_true",
                           help="Force file download even if exists locally")
    argparser.add_argument("-m", "--manifest-only", action="store_true",
                           help="Only regenerate manifest.json from the git tags. Downloads nothing. Use this "
                                "after tagging a new specifications release.")
    argparser.add_argument("--no-legacy", action="store_true",
                           help="Do not write the legacy resources.json (breaks harmonizer <= 1.0.9)")

    resources = {}

    args = argparser.parse_args()

    # manifest.json indexes git tags and never needs the vocabularies, so cutting a release does not require
    # re-downloading ~115 MB from NVS.
    if args.manifest_only:
        manifest = build_manifest()
        if manifest is None:
            rich.print("[red]Could not read git tags, manifest.json not written")
            raise SystemExit(1)
        write_json("manifest.json", manifest)
        rich.print(f"[green]Indexed {len(manifest['versions'])} versions, latest is {manifest['latest']}")
        raise SystemExit(0)

    os.makedirs(".temp", exist_ok=True)

    copernicus_params_file = os.path.join(".temp", "copernicus_param_list.xlsx")
    cf_std_name_units_file = os.path.join(".temp", "standard_name_units.xml")
    dwc_terms_file = os.path.join(".temp", "dwc_terms.csv")
    oso_ontology_file = os.path.join(".temp", "oso.ttl")
    spdx_licenses_file = os.path.join(".temp", "spdx_licenses.md")

    sdn_vocab_p01_file = os.path.join(".temp", "sdn_vocab_p01.json")
    sdn_vocab_p02_file = os.path.join(".temp", "sdn_vocab_p02.json")
    sdn_vocab_p06_file = os.path.join(".temp", "sdn_vocab_p06.json")
    sdn_vocab_p07_file = os.path.join(".temp", "sdn_vocab_p07.json")
    sdn_vocab_l05_file = os.path.join(".temp", "sdn_vocab_l05.json")
    sdn_vocab_l06_file = os.path.join(".temp", "sdn_vocab_l06.json")
    sdn_vocab_l22_file = os.path.join(".temp", "sdn_vocab_l22.json")
    sdn_vocab_l35_file = os.path.join(".temp", "sdn_vocab_l35.json")

    oceansites_file = os.path.join(".temp", "oceansites.md")
    datacite_file = os.path.join(".temp", "datacite.md")

    rich.print("Setting up the download tasks...", end="")
    tasks = [  # list of resources (URL, temp_file, csv_file)
        [sdn_vocab_p01_url, sdn_vocab_p01_file, "P01.csv"],
        [sdn_vocab_p02_url, sdn_vocab_p02_file, "P02.csv"],
        [sdn_vocab_p06_url, sdn_vocab_p06_file, "P06.csv"],
        [sdn_vocab_p07_url, sdn_vocab_p07_file, "P07.csv"],
        [sdn_vocab_l05_url, sdn_vocab_l05_file, "L05.csv"],
        [sdn_vocab_l06_url, sdn_vocab_l06_file, "L06.csv"],
        [sdn_vocab_l22_url, sdn_vocab_l22_file, "L22.csv"],
        [sdn_vocab_l35_url, sdn_vocab_l35_file, "L35.csv"],
        [copernicus_param_list, copernicus_params_file, "spdx licenses"],
        [cf_standard_name_units_url, cf_std_name_units_file, "CF units"],
        [dwc_terms_url, dwc_terms_file, "DwC terms"],
        [oso_ontology_url, oso_ontology_file, "OSO"],
        [spdx_licenses_github, spdx_licenses_file, "spdx licenses"]

    ]
    rich.print(f"[green]done")
    download_files(tasks, force_download=args.force_download)

    rich.print(f"downloading EDMO codes...", end="")
    download_edmo(edmo_codes_url, edmo_codes_jsonld, force_download=args.force_download)
    rich.print(f"[green]done")

    sdn_vocabs = {
        "P01": sdn_vocab_p01_file,
        "P02": sdn_vocab_p02_file,
        "P06": sdn_vocab_p06_file,
        "P07": sdn_vocab_p07_file,
        "L05": sdn_vocab_l05_file,
        "L06": sdn_vocab_l06_file,
        "L22": sdn_vocab_l22_file,
        "L35": sdn_vocab_l35_file,
    }

    sdn_vocabs_ids = {}
    sdn_vocabs_pref_label = {}
    sdn_vocabs_alt_label = {}
    sdn_vocabs_uris = {}
    sdn_vocabs_narrower = {}
    sdn_vocabs_broader = {}
    sdn_vocabs_related = {}

    source_url = f"https://raw.githubusercontent.com/emso-eric/emso-metadata-specifications/refs/heads/{emso_branch}/external-resources/"
    base_url = f"https://raw.githubusercontent.com/emso-eric/emso-metadata-specifications/refs/heads/{emso_branch}/"

    # ======== Process SeaDataNet / BODC Vocabularies ========#
    # Process raw SeaDataNet JSON-ld files and store them sliced in short JSON files
    os.makedirs("sdn", exist_ok=True)
    for vocab, jsonld_file in sdn_vocabs.items():
        resources[vocab] = {}
        resources[vocab]["hash"] = get_file_md5(jsonld_file)
        csv_filename = os.path.join("sdn", f"{vocab}.csv")
        frelated = os.path.join("sdn", f"{vocab}.related.json")
        fnarrower = os.path.join("sdn", f"{vocab}.narrower.json")
        fbroader = os.path.join("sdn", f"{vocab}.broader.json")

        rich.print(f"Loading SDN {vocab}...", end="")
        df, narrower, broader, related = load_sdn_vocab(jsonld_file)
        rich.print("[green]done!")
        for filename, values in {fnarrower: narrower, fbroader: broader, frelated: related}.items():
            with open(filename, "w") as f:
                json.dump(values, f)

        df.to_csv(csv_filename, index=False)

        resources[vocab]["csv"] = source_url + csv_filename
        for relation in ["narrower", "related", "broader"]:
            resources[vocab][relation] = source_url + f"sdn/{vocab}.{relation}.json"

    # ======== Process EDMO Codes ========#
    edmo_codes = get_edmo_codes(edmo_codes_jsonld)
    os.makedirs("edmo", exist_ok=True)
    edmo_codes.to_csv("edmo/EDMO.csv", index=False)
    resources["EDMO"] = {"csv": source_url + "edmo/EDMO.csv", "hash": get_file_md5(edmo_codes_jsonld)}

    # ======== Process EDMO Codes ========#
    # Copernicus parameter list
    print(copernicus_params_file)
    df = pd.read_excel(copernicus_params_file, sheet_name="Parameters", keep_default_na=False, header=1)
    df = df[["variable name", "long_name","CF standard_name", "unit", "SDN Param", "SDN UoM"]]
    df = df[df["variable name"] !=  ""]
    df["variable name"] = df["variable name"].str.split(" (", regex=False).str[0]

    variables = df["variable name"].dropna().values # remove blank lines produced by parsing excel
    variables = [v.split(" (")[0] for v in variables]  # remove citations

    os.makedirs("copernicus", exist_ok=True)
    filename = "copernicus/copernicus_variables.md"
    dataframe_to_markdown(df, "Copernicus variables", filename)


    resources["Copernicus Parameters"] = {
        "md": source_url + filename,
        "hash": get_file_md5(filename)
    }

    # ======== OeanSITES Codes =========#
    # NOTE: until 2026 these two keys were crossed (OceanSites_codes pointed at DataCite_codes.md and vice
    # versa). It went unnoticed because the harmonizer derives the local filename from the URL and then reads
    # both files by hardcoded path, so the content still landed where it was expected. Fixed here and in
    # manifest.json; old clients only see one extra 5 KB download when the hash changes.
    rich.print("Adding OceanSITES codes...", end="")
    filename = "oceansites/OceanSites_codes.md"
    resources["OceanSites_codes"] = {
        "md": source_url + filename,
        "hash": get_file_md5(filename)
    }
    rich.print("[green]done!")

    # ======== DataCite codes =========#
    rich.print("Adding DataCite codes...", end="")
    filename = "datacite/DataCite_codes.md"
    resources["DataCite_codes"] = {
        "md": source_url + filename,
        "hash": get_file_md5(filename)
    }
    rich.print("[green]done!")

    # ======== DataCite codes =========#
    rich.print("Adding EMSO_Metadata_Specifications codes...", end="")
    filename = "EMSO_Metadata_Specifications.md"
    resources["EMSO_Metadata_Specifications"] = {
        "md": base_url + filename,
        "hash": get_file_md5("../" + filename)
    }
    rich.print("[green]done!")

    # ======== Keyword vocabularies and OSO =========#
    # GCMD / GEMET / EuroSciVoc / OSO used to be downloaded and parsed by the harmonizer on every cold start.
    # The RDF work happens here now and only the parsed tables are published.
    process_keyword_vocabularies(force_download=args.force_download)
    process_oso(force_download=args.force_download)
    process_ror(force_download=args.force_download)

    # ======== Write the manifests =========#
    # Legacy v1 manifest, still consumed by harmonizer <= 1.0.9. Keep writing it until those clients are gone.
    if not args.no_legacy:
        write_json("resources.json", resources)

    # Axis B: the vocabularies just regenerated above.
    vocabularies = build_vocabularies()
    write_json("vocabularies.json", vocabularies)
    write_attribution_readme(vocabularies)
    write_notice(vocabularies)

    # Axis A: the normative documents, indexed per version straight from git.
    manifest = build_manifest()
    if manifest is None:
        rich.print("[yellow]Could not read git tags, manifest.json left untouched "
                   "(run with --manifest-only from a git checkout to regenerate it)")
    else:
        write_json("manifest.json", manifest)
        rich.print(f"[green]Indexed {len(manifest['versions'])} versions, latest is {manifest['latest']}")

    rich.print(f"[green]Resources updated!")