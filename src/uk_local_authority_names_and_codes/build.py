"""
Script to create the overall info files from
the various source files

"""

import json
import sqlite3
from pathlib import Path

import nbformat
import pandas as pd
from bs4 import BeautifulSoup
from htmltabletomd import convert_table
from nbconvert import MarkdownExporter
from nbconvert.preprocessors import ExecutePreprocessor
from traitlets.config import Config  # type: ignore
import rich


def create_overall_file():
    """
    Combine all json and lookup data into one json file that contains all info.
    Creates "uk_local_authorities.json", "uk_local_authorities.csv".

    This are substancially the same time, but alt-names and former-gss-codes become comma seperated
    in the csv.

    """
    df = pd.read_json(Path("data", "source", "local-authority-info.json"), typ="frame")

    df["current-authority"] = df["end-date"] == ""

    for p in sorted(Path("data", "source", "lookups").glob("*.csv")):
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
    """
    Create a lookup from all variations of name to the single canonical three-letter-code
    """

    df = pd.read_json(Path("data", "source", "local-authority-info.json"))
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
    """
    Create a lookup from all present and last GSS codes to the canonical three-letter-code
    """

    df = pd.read_json(Path("data", "source", "local-authority-info.json"))
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
    df = pd.read_json(Path("data", "source", "local-authority-info.json"), typ="frame")
    di = (
        df.loc[lambda x: ~(x["replaced-by"] == "")]
        .set_index("local-authority-code")["replaced-by"]
        .to_dict()
    )

    ldf = pd.read_csv(Path("data", "source", "lsoa_la_2021.csv"))
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
    """
    Render the coverage notebook and add the information back into the markdown file
    """
    nb = nbformat.read(Path("notebooks", "coverage.ipynb"), as_version=4)

    c = Config()
    # needs to reexecuite
    c.MarkdownExporter.exclude_input = True  # type: ignore
    c.MarkdownExporter.exclude_input_prompt = True  # type: ignore

    c.MarkdownExporter.preprocessors = [ExecutePreprocessor]  # type: ignore

    exporter = MarkdownExporter(config=c)

    body, resources = exporter.from_notebook_node(nb, {})
    body = remove_tables(body)

    with open("README.md", "r") as f:
        readme = f.read()

    readme = readme.split("# Dataset analysis")[0]
    readme += body

    with open("README.md", "w") as f:
        f.write(readme)


def make_sqlite():
    """
    combine output (except lsoa) into sqlite table
    """

    sqlite_file = Path("data", "uk_local_authorities.sqlite")

    if sqlite_file.exists():
        sqlite_file.unlink()
    con = sqlite3.connect(sqlite_file)

    files = {
        "uk_local_authorities.csv": "authorities",
        "lookup_name_to_registry.csv": "alt_names",
        "lookup_gss_to_registry.csv": "gss",
        # "lookup_lsoa_to_registry.csv": "lsoa"
    }

    for filename, tablename in files.items():
        df = pd.read_csv(Path("data", filename)).rename(
            columns=lambda x: x.replace("-", "_")
        )
        df.to_sql(tablename, con, index=False)

    con.close()


def blue_print(text: str) -> None:
    rich.print(f"[blue]{text}[/blue]")


def create_all_files():
    blue_print("Creating overall file")
    create_overall_file()
    blue_print("Creating name lookup")
    create_name_lookup()
    blue_print("Creating gss lookup")
    create_gss_lookup()
    blue_print("Creating lsoa to registry map")
    lsoa_to_registry()
    blue_print("Making sqlite")
    make_sqlite()
    blue_print("Updating sql file")
    render_readme()
    blue_print("Updating readme with new analysis")


if __name__ == "__main__":
    create_all_files()
