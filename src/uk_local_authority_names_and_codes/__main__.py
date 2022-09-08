import rich_click as click
from uk_local_authority_names_and_codes.build import (
    create_all_files,
    create_future_only,
)


@click.group()
def cli():
    pass


@cli.command()
def build():
    create_future_only()
    create_all_files()


def main():
    cli()


if __name__ == "__main__":
    main()
