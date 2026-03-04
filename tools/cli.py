"""CLI entry point for DBC-to-XML mapping tool."""

import click

from parser import load_dbc, list_messages
from mapper import select_signals
from xml_export import export_config


@click.command()
@click.argument("dbc_file", type=click.Path(exists=True))
@click.option("-o", "--output", default="config.xml", help="Output XML path")
def main(dbc_file: str, output: str) -> None:
    """Map DBC signals to ROS2 topics and generate bridge config XML."""
    db = load_dbc(dbc_file)
    messages = list_messages(db)
    click.echo(f"Loaded {len(messages)} message(s) from {dbc_file}")

    mappings = select_signals(messages)
    if not mappings:
        click.echo("No signals selected, exiting.")
        return

    export_config(mappings, output)


if __name__ == "__main__":
    main()
