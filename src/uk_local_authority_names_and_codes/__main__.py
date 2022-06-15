from data_common.management.cli import cli, set_doc_collection
from data_common.management.render_processing import DocumentCollection
from pathlib import Path
import rich_click as click
from uk_local_authority_names_and_codes.build import create_all_files

if Path("render.yaml").exists():
    doc_collection = DocumentCollection.from_yaml("render.yaml")
    set_doc_collection(doc_collection)


@cli.command()
def build():
    create_all_files()


def main():
    cli()


if __name__ == "__main__":
    main()
