import os
import time
import json
import urllib
import urllib.request
import urllib.error
from argparse import ArgumentParser
import requests
import rich
import concurrent.futures as futures
import pandas as pd

import hashlib

emso_branch = "main"


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

oso_ontology_url = "https://raw.githubusercontent.com/emso-eric/oso-ontology/refs/heads/main/docs/ontology.ttl"

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


if __name__ == "__main__":
    argparser = ArgumentParser()
    argparser.add_argument("-f", "--force-download", action="store_true", help="Force file download even if exists locally")

    resources = {}

    args = argparser.parse_args()
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


    #======== Process SeaDataNet / BODC Vocabularies ========#
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

        df.to_csv(filename, index=False)

        resources[vocab]["csv"] = source_url + filename
        for relation in ["narrower", "related", "broader"]:
            resources[vocab][relation] = source_url + f"sdn/{vocab}.{relation}.json"

    #======== Process EDMO Codes ========#
    edmo_codes = get_edmo_codes(edmo_codes_jsonld)
    os.makedirs("edmo", exist_ok=True)
    edmo_codes.to_csv("edmo/EDMO.csv", index=False)
    resources["EDMO"] = {"csv": source_url + "edmo/EDMO.csv", "hash": get_file_md5(edmo_codes_jsonld)}

    #======== Process EDMO Codes ========#
    # Copernicus parameter list
    df = pd.read_excel(copernicus_params_file, sheet_name="Parameters", keep_default_na=False, header=1)
    variables = df["variable name"].dropna().values
    variables = [v.split(" (")[0] for v in variables]  # remove citations
    copernicus_variables = [v for v in variables if len(v) > 1]  # remove empty lines
    os.makedirs("copernicus", exist_ok=True)
    filename = "copernicus/codes.json"
    with open(filename, "w") as f:
        f.write(json.dumps(copernicus_variables, indent=2))
    resources["Copernicus Parameters"]= {
        "json": source_url + "copernicus/codes.json",
        "hash": get_file_md5(filename)
    }

    #======== OeanSITES Codes =========#
    rich.print("Adding OceanSITES codes...", end="")
    filename = "datacite/DataCite_codes.md"
    resources["OceanSites_codes"]= {
        "md": source_url + filename,
        "hash": get_file_md5(filename)
    }
    rich.print("[green]done!")

    #======== DataCite codes =========#
    rich.print("Adding DataCite codes...", end="")
    filename = "oceansites/OceanSites_codes.md"
    resources["DataCite_codes"]= {
        "md": source_url + filename ,
        "hash": get_file_md5(filename)
    }
    rich.print("[green]done!")

    #======== DataCite codes =========#
    rich.print("Adding EMSO_Metadata_Specifications codes...", end="")
    filename = "EMSO_Metadata_Specifications.md"
    resources["EMSO_Metadata_Specifications"]= {
        "md": base_url + filename ,
        "hash": get_file_md5("../" + filename)
    }
    rich.print("[green]done!")

    with open("resources.json", "w") as f:
        f.write(json.dumps(resources, indent=2))

    rich.print(f"[green]Resources updated!")