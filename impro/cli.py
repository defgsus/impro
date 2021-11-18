import argparse
import json
from typing import List, Type, Union, Optional

from impro.pages.page import Page


def parse_args() -> dict:

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "command", type=str,
        choices=["render"],
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
    if command == "render":
        if not input:
            print("Need to specify at least one input")
            exit(1)

        page = Page.from_markdown(input[0])
        print(page.markup.front_matter)
        print("----")
        print(page.to_html())
        #print(json.dumps(page.to_ast(), indent=2))


if __name__ == "__main__":
    main(**parse_args())


