from typing import Iterable, NamedTuple, List
from collections import namedtuple
from subprocess import getoutput
from re import compile, Pattern
from pathlib import Path
from sys import exit
import logging

import click


RC_PARSE_ERR: int = 1

SUFFIX: str = "g2sd"
SYSD_FMT: str = """title {name}
linux {kernel}
initrd {initrd}
options {options}"""
    
NAME_RE: Pattern = compile("menuentry '(?P<name>[\w\d\W\D]*)' -")
KERNEL_RE: Pattern = compile("linux(?:[\t ]*)(?P<kernel>.*) root=(?P<root>[\w\d\-=\/]*) (?P<options>.*)")
INIT_RE: Pattern = compile("initrd(?:[\t ])(?P<initrd>.*)")


class MenuEntry(NamedTuple):
    name: str
    kernel: str
    root: str
    options: str
    initrd: str


def gen_menu_entries(grub_lines: Iterable[str]) -> Iterable[MenuEntry]:
    args: List[str] = []

    for line in grub_lines:
        try:
            line = line.strip()

            if line.startswith('menuentry'):
                if args:
                    args = []

                name = NAME_RE.findall(line)
                args.extend(name)

            elif line.startswith("linux"):
                kernel, *_ = KERNEL_RE.findall(line)
                args.extend(kernel)

            elif line.startswith("initrd"):
                init = INIT_RE.findall(line)
                args.extend(init)

                yield MenuEntry(*args)
                args = []

        except Exception as e:
            logging.exception(e)
            logging.error(f"Error parsing file: {e}")
            exit(RC_PARSE_ERR)


def convert_root_entry(root_str: str) -> str:
    if root_str.startswith("PARTUUID"):
        return root_str

    if root_str.startswith('UUID'):
        cmd = f"blkid -t {root_str}"
        # _, uuid = root_str.split('=')
        # cmd = f"blkid -t {uuid}"

    else:
        cmd = f"blkid {root_str}"

    blkid_out = getoutput(cmd)
    *_, partuuid_str = blkid_out.split(' ')
    partuuid_str = partuuid_str.replace('"', '')

    return partuuid_str


def parse_options(options_str: str) -> str:
    options = options_str.split(' ')

    return ' '.join(
        option 
        for option in options
        if not option.startswith('$')
    )


def menuentry_to_systemd(me: MenuEntry) -> str:
    partuuid = convert_root_entry(me.root)
    options = parse_options(me.options)
    line = partuuid, options
    opt_str = ' '.join(line)

    return SYSD_FMT.format(
        **me._asdict(),
        options=opt_str
    )


@click.command()
@click.argument("grub_file")
@click.argument("path")
def cmd(grub_file: str, path: str):
    grub_file = Path(grub_file)
    grub_lines = grub_file.read_text().splitlines()
    entries_gen = gen_menu_entries(grub_lines)

    for index, me in enumerate(entries_gen):
        file = Path(f'{path}/loader/entries/{index}_{SUFFIX}.conf')
        text = menuentry_to_systemd(me)

        file.write_text(text)
        logging.info(f"Wrote {me.name} to {file.name}")


if __name__ == "__main__":
    cmd()
