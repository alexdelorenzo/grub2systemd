from typing import Iterable
from re import compile
from collections import namedtuple
from subprocess import getoutput

import click


PREFIX = 'test'
SUFFIX = "g2sd"

NAME_RE = compile("menuentry '(?P<name>[\w\d\W\D]*)' -")
KERNEL_RE = compile("linux(?:[\t ]*)(?P<kernel>.*) root=(?P<root>[\w\d\-=\/]*)")
INIT_RE = compile("initrd(?:[\t ])(?P<initrd>.*)")


MenuEntry = namedtuple('MenuEntry', 'name kernel root initrd')


with open("grub.cfg", "r") as file:
    INPUT = file.read().splitlines()


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

        except Exception as ex:
            print(args, ex)
            break


def convert_root_entry(root_str: str) -> str:
    if root_str.startswith('UUID'):
        _, uuid = root_str.split('=')
        cmd = "blkid -t %s" % root_str

    elif root_str.startswith("PARTUUID"):
        return root_str

    else:
        cmd = "blkid %s" % root_str

    blkid_out = getoutput(cmd)
    partuuid_str = blkid_out.split(' ')[-1]
    partuuid_str = partuuid_str.replace('"', '')

    return partuuid_str


def menuentry_to_systemd(me: MenuEntry) -> str:
    partuuid = convert_root_entry(me.root)

    return "title %s\nlinux %s\ninitrd %s\noptions %s" % (me.name, me.kernel, me.initrd, partuuid)


@click.command()
@click.argument("grub_file")
@click.argument("path")
def cmd(grub_file: str, path: str):
    with open(grub_file, "r") as file:
        grub = file.read().splitlines()

    for index, me in enumerate(gen_menu_entries(grub)):
        with open(path + f'/loaders/entries/{index}_{SUFFIX}.conf', 'w') as file:
            file.write(menuentry_to_systemd(me))


if __name__ == "__main__":
    cmd()
