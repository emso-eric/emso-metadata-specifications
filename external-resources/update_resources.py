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
    os.makedirs("relations", exist_ok=True)
    os.makedirs(".temp", exist_ok=True)

    emso_version = "develop"

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

    rich.print("Setting up the download tasks...", end="")
    tasks = [  # list of resources (URL, temp_file, csv_file)
        #"EDMO": ["emso_codes_url", "EDMO_codes.csv"]
        [sdn_vocab_p01_url, ".temp/sdn_vocab_p01.json", "P01.csv"],
        [sdn_vocab_p02_url, ".temp/sdn_vocab_p02.json", "P02.csv"],
        [sdn_vocab_p06_url, ".temp/sdn_vocab_p06.json", "P06.csv"],
        [sdn_vocab_p07_url, ".temp/sdn_vocab_p07.json", "P07.csv"],
        [sdn_vocab_l05_url, ".temp/sdn_vocab_l05.json", "L05.csv"],
        [sdn_vocab_l06_url, ".temp/sdn_vocab_l06.json", "L06.csv"],
        [sdn_vocab_l22_url, ".temp/sdn_vocab_l22.json", "L22.csv"],
        [sdn_vocab_l35_url, ".temp/sdn_vocab_l35.json", "L35.csv"],
    ]
    rich.print(f"[green]done")
    download_files(tasks, force_download=args.force_download)

    rich.print(f"downloading EDMO codes...", end="")
    download_edmo(edmo_codes_url, edmo_codes_jsonld, force_download=args.force_download)
    rich.print(f"[green]done")

    sdn_vocabs = {
        "P01": ".temp/sdn_vocab_p01.json",
        "P02": ".temp/sdn_vocab_p02.json",
        "P06": ".temp/sdn_vocab_p06.json",
        "P07": ".temp/sdn_vocab_p07.json",
        "L05": ".temp/sdn_vocab_l05.json",
        "L06": ".temp/sdn_vocab_l06.json",
        "L22": ".temp/sdn_vocab_l22.json",
        "L35": ".temp/sdn_vocab_l35.json",
    }

    sdn_vocabs_ids = {}
    sdn_vocabs_pref_label = {}
    sdn_vocabs_alt_label = {}
    sdn_vocabs_uris = {}
    sdn_vocabs_narrower = {}
    sdn_vocabs_broader = {}
    sdn_vocabs_related = {}

    t = time.time()
    # Process raw SeaDataNet JSON-ld files and store them sliced in short JSON files
    for vocab, jsonld_file in sdn_vocabs.items():
        csv_filename = os.path.join(f"{vocab}.csv")
        frelated = os.path.join("relations", f"{vocab}.related.json")
        fnarrower = os.path.join("relations", f"{vocab}.narrower.json")
        fbroader = os.path.join("relations", f"{vocab}.broader.json")

        rich.print(f"Loading SDN {vocab}...", end="")
        df, narrower, broader, related = load_sdn_vocab(jsonld_file)
        rich.print("[green]done!")
        for filename, values in {fnarrower: narrower, fbroader: broader, frelated: related}.items():
            with open(filename, "w") as f:
                json.dump(values, f)

        # for vocab, df in sdn_vocabs.items():
        # Storing to CSV to make it easier to search
        filename = os.path.join(f"{vocab}.csv")
        df.to_csv(filename, index=False)
        resources[vocab] = filename
        for relation in ["narrower", "related", "broader"]:
            resources[f"{vocab}.{relation}"] = os.path.join("relations", f"{vocab}.{relation}.json")

    # Add EDMO
    edmo_codes = get_edmo_codes(edmo_codes_jsonld)
    edmo_codes.to_csv("EDMO.csv", index=False)
    resources["EDMO"] = "EDMO.csv"


    source_url = "https://raw.githubusercontent.com/emso-eric/emso-metadata-specifications/refs/heads/develop/"

    for key, value in resources.items():
        hash = get_file_md5(value)
        resources[key] = {
            "url": source_url + value,
            "hash": hash
        }

    rich.print(resources)
    with open("manifest.json", "w") as f:
        f.write(json.dumps(resources, indent=2))



