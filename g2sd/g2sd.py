from typing import Iterable, NamedTuple
from re import compile
from collections import namedtuple
from subprocess import getoutput
from pathlib import Path
from sys import exit

import click


PREFIX = 'test'
SUFFIX = "g2sd"
RC_PARSE_ERR = 1

NAME_RE = compile("menuentry '(?P<name>[\w\d\W\D]*)' -")
KERNEL_RE = compile("linux(?:[\t ]*)(?P<kernel>.*) root=(?P<root>[\w\d\-=\/]*) (?P<options>.*)")
INIT_RE = compile("initrd(?:[\t ])(?P<initrd>.*)")


class MenuEntry(NamedTuple):
    name: str
    kernel: str
    root: str
    options: str
    initrd: str


def gen_menu_entries(input: Iterable[str]) -> Iterable[MenuEntry]:
    args = []

    for num, line in enumerate(input):
        try:
            line = line.strip()

            if line.startswith('menuentry'):
                if args:
                    args = []

                name = NAME_RE.findall(line)

                args.extend(name)

            elif line.startswith("linux"):
                all = KERNEL_RE.findall(line)
                args.extend(all[0])

            elif line.startswith("initrd"):
                init = INIT_RE.findall(line)
                args.extend(init)

                yield MenuEntry(*args)

                args = []

        except Exception as e:
            print("Error parsing file:", e)
            exit(RC_PARSE_ERR)


def convert_root_entry(root_str: str) -> str:
    if root_str.startswith('UUID'):
        _, uuid = root_str.split('=')
        cmd = f"blkid -t {root_str}"

    elif root_str.startswith("PARTUUID"):
        return root_str

    else:
        cmd = f"blkid {root_str}"

    blkid_out = getoutput(cmd)
    partuuid_str = blkid_out.split(' ')[-1]
    partuuid_str = partuuid_str.replace('"', '')

    return partuuid_str


def parse_options(options_str: str) -> str:
    options = options_str.split(' ')

    return ' '.join(option for option in options
                    if not option.startswith('$'))

def menuentry_to_systemd(me: MenuEntry) -> str:
    partuuid = convert_root_entry(me.root)
    options = ' '.join((partuuid, parse_options(me.options)))

    return f"title {me.name}\nlinux {me.kernel}\ninitrd {me.initrd}\noptions {options}"


@click.command()
@click.argument("grub_file")
@click.argument("path")
def cmd(grub_file: str, path: str):
    grub_file = Path(grub_file)
    grub_txt = grub_file.read_text().splitlines()

    for index, me in enumerate(gen_menu_entries(grub_txt)):
        file = Path(f'/loader/entries/{index}_{SUFFIX}.conf')
        file.write_text(menuentry_to_systemd(me))
        print(f"Wrote {me.name} to {file.name}")


if __name__ == "__main__":
    cmd()

