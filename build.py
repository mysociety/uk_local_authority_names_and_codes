"""
Script to create the overall info files from
the various source files

"""

import json
from pathlib import Path

import nbformat
import pandas as pd
from bs4 import BeautifulSoup
from nbconvert import MarkdownExporter
from traitlets.config import Config
from htmltabletomd import convert_table
from nbconvert.preprocessors import ExecutePreprocessor


def create_overall_file():

    df = pd.read_json(Path("source", "local-authority-info.json"))

    df["current-authority"] = df["end-date"] == ""

    for p in sorted(Path("source", "lookups").glob("*.csv")):
        ndf = pd.read_csv(p)
        df = df.merge(ndf, how="left")

    df = df.fillna("")

    new_cols = [
        x
        for x in df.columns
        if x not in ["local-authority-type", "local-authority-type-name"]
    ]
    new_cols = (
        new_cols[:9]
        + ["local-authority-type", "local-authority-type-name"]
        + new_cols[9:]
    )
    df = df[new_cols]

    df = df.sort_values("local-authority-code")

    di = df.to_dict("records")

    with open(Path("data", "uk_local_authorities.json"), "w") as f:
        json.dump(di, f, indent=4)

    df["alt-names"] = df["alt-names"].apply(",".join)
    df["former-gss-codes"] = df["former-gss-codes"].apply(",".join)

    df.to_csv(Path("data", "uk_local_authorities.csv"), index=False)


def create_name_lookup():

    df = pd.read_json(Path("source", "local-authority-info.json"))
    df["la-name"] = df["official-name"].apply(lambda x: [x]) + df["alt-names"]

    ndf = (
        df.set_index("local-authority-code")["la-name"]
        .explode()
        .to_frame()
        .reset_index()
    )
    ndf = ndf[ndf.columns[::-1]]
    ndf.to_csv(Path("data", "lookup_name_to_registry.csv"), index=False)


def create_gss_lookup():

    df = pd.read_json(Path("source", "local-authority-info.json"))
    df["gss-code"] = df["gss-code"].apply(lambda x: [x]) + df["former-gss-codes"]

    ndf = (
        df.set_index("local-authority-code")["gss-code"]
        .explode()
        .to_frame()
        .reset_index()
    )
    ndf = ndf[ndf.columns[::-1]]
    ndf.to_csv(Path("data", "lookup_gss_to_registry.csv"), index=False)


def lsoa_to_registry():
    """
    update the lsoa lookup with any changes to la structure
    """
    df = pd.read_json(Path("source", "local-authority-info.json"))
    di = (
        df[lambda x: ~(x["replaced-by"] == "")]
        .set_index("local-authority-code")["replaced-by"]
        .to_dict()
    )

    ldf = pd.read_csv(Path("source", "lsoa_la_2021.csv"))
    ldf["local-authority-code"] = ldf["local-authority-code"].apply(
        lambda x: di.get(x, x)
    )
    ldf.to_csv(Path("data", "lookup_lsoa_to_registry.csv"), index=False)


def remove_tables(body: str) -> str:
    """
    notebook is still outputing html tables
    conver to markdown

    """
    body = body.replace('<tr style="text-align: right;">\n      <th></th>', "<tr>")
    soup = BeautifulSoup(body, "html.parser")
    for div in soup.find_all("table"):
        table = convert_table(str(div))
        div.replaceWith(table)
    for div in soup.find_all("style"):
        div.replaceWith("")

    body = str(soup)
    body = body.replace("&lt;br/&gt;", "<br/>")
    body = body.replace("![png]", "![]")
    body = body.replace('<style type="text/css">', "")
    body = body.replace("</style>", "")
    body = body.replace("<div>", "")
    body = body.replace("</div>", "")
    while "\n\n\n" in body:
        body = body.replace("\n\n\n", "\n\n")

    return body


def render_readme():
    nb = nbformat.read("coverage.ipynb", as_version=4)

    c = Config()
    # needs to reexecuite
    c.MarkdownExporter.exclude_input = True
    c.MarkdownExporter.exclude_input_prompt = True

    c.MarkdownExporter.preprocessors = [ExecutePreprocessor]

    exporter = MarkdownExporter(config=c)

    body, resources = exporter.from_notebook_node(nb, {})
    body = remove_tables(body)

    with open("README.md", "r") as f:
        readme = f.read()

    readme = readme.split("# Dataset analysis")[0]
    readme += body

    with open("README.md", "w") as f:
        f.write(readme)


if __name__ == "__main__":
    create_overall_file()
    create_name_lookup()
    create_gss_lookup()
    lsoa_to_registry()
    render_readme()
