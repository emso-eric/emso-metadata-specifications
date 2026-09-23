import os
import re
import time
import json
import urllib
import urllib.request
import urllib.error
import subprocess
from argparse import ArgumentParser
import requests
import rich
import concurrent.futures as futures
import pandas as pd

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

# Provenance for the externally governed vocabularies listed in vocabularies.json
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


def vocabulary_entry(local_path, title, governed_by, source, file_key):
    """
    Build one vocabularies.json resource entry. local_path is relative to this script (e.g. 'sdn/P01.csv'), and
    is converted to the repository-relative path stored in the manifest.
    """
    with open(local_path, "rb") as f:
        data = f.read()
    return {
        "title": title,
        "governed_by": governed_by,
        "source": source,
        "files": {file_key: {
            "path": f"external-resources/{local_path}".replace(os.sep, "/"),
            "md5": md5_bytes(data),
            "bytes": len(data),
        }},
    }


def build_vocabularies():
    """
    Describe the single current snapshot of externally governed vocabularies, read from the files this script
    has just regenerated. There is deliberately no version selection here: these vocabularies are maintained by
    third parties and apply to every specifications version.
    """
    resources = {}

    for vocab, (title, governed_by) in vocabulary_provenance.items():
        files = {}
        paths = {"csv": os.path.join("sdn", f"{vocab}.csv")}
        for relation in ["narrower", "broader", "related"]:
            paths[relation] = os.path.join("sdn", f"{vocab}.{relation}.json")

        for file_key, local_path in paths.items():
            if not os.path.isfile(local_path):
                continue
            with open(local_path, "rb") as f:
                data = f.read()
            files[file_key] = {
                "path": f"external-resources/{local_path}".replace(os.sep, "/"),
                "md5": md5_bytes(data),
                "bytes": len(data),
            }

        resources[vocab] = {
            "title": title,
            "governed_by": governed_by,
            "source": f"https://vocab.nerc.ac.uk/collection/{vocab}/current/",
            "files": files,
        }

    resources["EDMO"] = vocabulary_entry(
        os.path.join("edmo", "EDMO.csv"), "European Directory of Marine Organisations", "SeaDataNet",
        "https://edmo.seadatanet.org/", "csv")

    resources["Copernicus Parameters"] = vocabulary_entry(
        os.path.join("copernicus", "copernicus_variables.md"), "Copernicus Marine In Situ TAC parameter list",
        "Copernicus Marine Service / Ifremer", copernicus_param_list, "md")

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

    # ======== Write the manifests =========#
    # Legacy v1 manifest, still consumed by harmonizer <= 1.0.9. Keep writing it until those clients are gone.
    if not args.no_legacy:
        write_json("resources.json", resources)

    # Axis B: the vocabularies just regenerated above.
    write_json("vocabularies.json", build_vocabularies())

    # Axis A: the normative documents, indexed per version straight from git.
    manifest = build_manifest()
    if manifest is None:
        rich.print("[yellow]Could not read git tags, manifest.json left untouched "
                   "(run with --manifest-only from a git checkout to regenerate it)")
    else:
        write_json("manifest.json", manifest)
        rich.print(f"[green]Indexed {len(manifest['versions'])} versions, latest is {manifest['latest']}")

    rich.print(f"[green]Resources updated!")