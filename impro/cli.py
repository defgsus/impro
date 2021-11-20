import argparse
import json
from pathlib import Path
from typing import List, Type, Union, Optional

from impro.pages.page import Page
from impro.site import Site
from impro.server import run_server


def parse_args() -> dict:

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "command", type=str,
        choices=["info", "site-info", "render", "serve"],
        help="Action",
    )
    parser.add_argument(
        "input", type=str, nargs="*",
        help="One or more inputs",
    )
    parser.add_argument(
        "-o", "--output", type=str, default="-",
        help="Output directory, or '-' for stdout",
    )
    parser.add_argument(
        "-f", "--format", type=str, default="md",
        choices=["md", "html"],
        help="Output format",
    )

    return vars(parser.parse_args())


def main(
        command: str,
        input: List[str],
        output: str,
        format: str,
):
    if command == "info":
        for filename in input:
            page = Page.from_file(filename)
            print(f"--- {page} ---")
            print(f"  format: {page.markup.format}")
            print(f"  title: '{page.title}'")
            print(f"  slug: '{page.slug}'")
            print(f"  front-matter: {page.markup.front_matter}")
            if page.associated_files:
                print("  files:")
                for file in page.associated_files:
                    print(f'    ({file["type"]}) {file["path"]} {"(external)" if file["external"] else ""}')

    elif command == "render":
        if not input:
            print("Need to specify at least one input")
            exit(1)

        site = Site()
        for filename in input:
            page = Page.from_file(filename)
            site.add_page(page, path="docs")

        if output == "-":
            for filename, content in site.iter_files(format=format):
                print()
                print("-"*32, filename, "-"*32)
                if isinstance(content, bytes):
                    print(len(content), "bytes")
                else:
                    print(content)

        else:
            output = Path(output).absolute()
            site.write_files(root=output, format=format)

    elif command == "site-info":
        site = Site()
        for filename in input:
            page = Page.from_file(filename)
            site.add_page(page, path="docs")

        print(f"--- {site} ---")
        print("  files:")
        for filename, content in site.iter_files(format):
            print(f'    {len(content):9d} {filename}')

    elif command == "serve":
        site = Site()
        for filename in input:
            page = Page.from_file(filename)
            site.add_page(page, path="docs")

        run_server(site)

    else:
        raise ValueError(f"Unknown command '{command}'")


if __name__ == "__main__":
    main(**parse_args())


