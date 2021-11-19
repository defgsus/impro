import argparse
import json
from typing import List, Type, Union, Optional

from impro.pages.page import Page
from impro.site import Site


def parse_args() -> dict:

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "command", type=str,
        choices=["info", "site-info", "render"],
        help="Action",
    )
    parser.add_argument(
        "input", type=str, nargs="*",
        help="One or more inputs",
    )
    parser.add_argument(
        "-o", "--output", type=str, default=None,
        help="Output directory",
    )

    return vars(parser.parse_args())


def main(
        command: str,
        input: List[str],
        output: str,
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

        page = Page.from_file(input[0])
        print(page.markup.front_matter)
        print("----")
        print(page.elements)
        print("----")
        print(page.to_html())
        #print(json.dumps(page.to_ast(), indent=2))

    elif command == "site-info":
        site = Site()
        for filename in input:
            page = Page.from_file(filename)
            site.add_page(page)

        print(f"--- {site} ---")
        if site.associated_files:
            print("  files:")
            for file in site.associated_files:
                print(f'    ({file["type"]}) {file["path"]} {"(external)" if file["external"] else ""}')

    else:
        raise ValueError(f"Unknown command '{command}'")


if __name__ == "__main__":
    main(**parse_args())


