"""
Script to create the overall info files from
the various source files

"""

import json
import sqlite3
from pathlib import Path
import shutil
from datetime import datetime
import nbformat
import pandas as pd
from bs4 import BeautifulSoup
from htmltabletomd import convert_table
from nbconvert import MarkdownExporter
from nbconvert.preprocessors import ExecutePreprocessor
from traitlets.config import Config  # type: ignore
import rich
from typing import Any
from rich.traceback import install

# Turn on rich tracebacks
install(show_locals=False, width=None)

top_level = Path(__file__).parent.parent.parent

current_package = Path(top_level, "data", "packages", "uk_la_past_current")
future_package = Path(top_level, "data", "packages", "uk_la_future")
data_dir = Path(top_level, "data")


def to_json_and_csv(df: pd.DataFrame, directory: Path, filename: str):
    """
    Save the json and csv to the directory
    """
    df.to_json(Path(directory, f"{filename}.json"), orient="records", indent=4)

    df["alt-names"] = df["alt-names"].apply(",".join)
    df["former-gss-codes"] = df["former-gss-codes"].apply(",".join)

    df.to_csv(Path(directory, f"{filename}.csv"), index=False)


def create_overall_file(dest: Path):
    """
    Combine all json and lookup data into one json file that contains all info.
    Creates "future_uk_local_authorities.json", "future_uk_local_authorities.csv".

    These contain councils that have yet to be created.

    These are substancially the same file, but alt-names and former-gss-codes become comma seperated
    in the csv.

    """
    df = pd.read_json(
        Path(top_level, "data", "source", "local-authority-info.json"),
        typ="frame",
        orient="records",
    )

    # current authorities are all those that have no end time, or where the end time is in the future

    now = pd.Timestamp(datetime.now().date())

    no_end_time = df["end-date"] == ""
    in_future = pd.to_datetime(df["end-date"]) > now  # type: ignore

    df["current-authority"] = no_end_time | in_future

    for p in sorted(Path(top_level, "data", "source", "lookups").glob("*.csv")):
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

    to_json_and_csv(df, dest, "uk_local_authorities_future")


def create_without_future():
    """
    Some councils do not exist yet, and the current table has certain assumptions this would break
    if it was the primary table.

    Instead, we take the table and remove the future councils.

    To do this we:

    removes any councils with a start-date in the future
    blank out end-date and replaced-by when an end-date is in the future.
    an additional trigger for the build github action of a daily action to update the file when a significant date passes

    """

    now = pd.Timestamp(datetime.now().date())
    df = pd.read_json(
        Path(data_dir, "interim", "uk_local_authorities_future.json"),
        typ="frame",
        orient="records",
    )

    # remove future starting councils
    df = df.loc[~(pd.to_datetime(df["start-date"]) > now)]  # type: ignore

    end_date_in_future = pd.to_datetime(df["end-date"]) > now  # type: ignore
    df.loc[end_date_in_future, "end-date"] = ""  # type: ignore
    df.loc[end_date_in_future, "replaced-by"] = ""  # type: ignore

    to_json_and_csv(df, current_package, "uk_local_authorities_current")


def create_legacy_compatible():
    """
    Update a version of the file that may be referenced viagithub that predates the versioning system.

    The tracked problems are:

    The old file expects a 'unitary_or_lower' column rather than 'unitary-or-lower'.

    The source is uk_local_authorities_current.json

    """
    df = pd.read_json(
        Path(current_package, "uk_local_authorities_current.json"),
        typ="frame",
        orient="records",
    )
    df = df.rename(columns={"unitary-or-lower": "unitary_or_lower"})  # type: ignore

    to_json_and_csv(df, data_dir, "uk_local_authorities")


def create_name_lookup(future: bool = False):
    """
    Create a lookup from all variations of name to the single canonical three-letter-code
    """

    if future:
        out_dir = future_package
        df = pd.read_json(
            Path(future_package, "uk_local_authorities_future.json"),
            typ="frame",
            orient="records",
        )
    else:
        out_dir = current_package
        df = pd.read_json(
            Path(current_package, "uk_local_authorities_current.json"),
            typ="frame",
            orient="records",
        )
    df["la-name"] = df["official-name"].apply(lambda x: [x]) + df["alt-names"]

    ndf = (
        df.set_index("local-authority-code")["la-name"]
        .explode()
        .to_frame()
        .reset_index()
    )
    ndf = ndf[ndf.columns[::-1]]
    ndf.to_csv(Path(out_dir, "lookup_name_to_registry.csv"), index=False)


def create_gss_lookup():
    """
    Create a lookup from all present and last GSS codes to the canonical three-letter-code
    """

    df = pd.read_json(Path(current_package, "uk_local_authorities_current.json"))
    df["gss-code"] = df["gss-code"].apply(lambda x: [x]) + df["former-gss-codes"]

    ndf = (
        df.set_index("local-authority-code")["gss-code"]
        .explode()
        .to_frame()
        .reset_index()
    )
    ndf = ndf[ndf.columns[::-1]]  #
    ndf.to_csv(Path(data_dir, "lookup_gss_to_registry.csv"), index=False)
    ndf.to_csv(Path(current_package, "lookup_gss_to_registry.csv"), index=False)


def lsoa_to_registry():
    """
    update the lsoa lookup with any changes to la structure
    """
    df = pd.read_json(
        Path(current_package, "uk_local_authorities_current.json"),
        typ="frame",
        orient="records",
    )
    di = (
        df.loc[lambda x: ~(x["replaced-by"] == "")]
        .set_index("local-authority-code")["replaced-by"]
        .to_dict()
    )

    ldf = pd.read_csv(Path(top_level, "data", "source", "lsoa_la_2021.csv"))
    ldf["local-authority-code"] = ldf["local-authority-code"].apply(
        lambda x: di.get(x, x)
    )
    ldf.to_csv(Path(current_package, "lookup_lsoa_to_registry.csv"), index=False)
    ldf.to_csv(Path(data_dir, "lookup_lsoa_to_registry.csv"), index=False)


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
    nb = nbformat.read(Path(top_level, "notebooks", "coverage.ipynb"), as_version=4)

    c = Config()
    # needs to reexecuite
    c.MarkdownExporter.exclude_input = True  # type: ignore
    c.MarkdownExporter.exclude_input_prompt = True  # type: ignore

    c.MarkdownExporter.preprocessors = [ExecutePreprocessor]  # type: ignore

    exporter = MarkdownExporter(config=c)

    body, resources = exporter.from_notebook_node(nb, {})
    body = remove_tables(body)

    with open(Path(top_level, "README.md"), "r") as f:
        readme = f.read()

    readme = readme.split("# Dataset analysis")[0]
    readme += body

    with open(Path(top_level, "README.md"), "w") as f:
        f.write(readme)


def blue_print(text: str) -> None:
    rich.print(f"[blue]{text}[/blue]")


def create_future_only():
    blue_print("Creating future only file")
    create_overall_file(dest=future_package)


def create_all_files():
    blue_print("Creating overall file")
    create_overall_file(dest=data_dir / "interim")
    blue_print("Creating current version")
    create_without_future()
    blue_print("Creating name lookup")
    create_name_lookup()
    blue_print("Creating name lookup - future")
    create_name_lookup(future=True)
    blue_print("Creating gss lookup")
    create_gss_lookup()
    blue_print("Creating legacy compatible files")
    create_legacy_compatible()
    blue_print("Creating lsoa to registry map")
    lsoa_to_registry()
    blue_print("Updating readme file")
    render_readme()


if __name__ == "__main__":
    create_future_only()
    create_all_files()
