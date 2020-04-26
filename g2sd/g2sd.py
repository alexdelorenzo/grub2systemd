from typing import Iterable, NamedTuple
from re import compile
from collections import namedtuple
from subprocess import getoutput
from sys import exit

import click


PREFIX = 'test'
SUFFIX = "g2sd"

NAME_RE = compile("menuentry '(?P<name>[\w\d\W\D]*)' -")
KERNEL_RE = compile("linux(?:[\t ]*)(?P<kernel>.*) root=(?P<root>[\w\d\-=\/]*) (?P<options>.*)")
INIT_RE = compile("initrd(?:[\t ])(?P<initrd>.*)")


#MenuEntry = namedtuple('MenuEntry', 'name kernel root initrd')
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

        except Exception as ex:
            print(args, ex)
            exit(1)


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


def parse_options(options_str: str) -> str:
    options = options_str.split(' ')

    return ' '.join(option for option in options
                    if not option.startswith('$'))


def menuentry_to_systemd(me: MenuEntry) -> str:
    partuuid = convert_root_entry(me.root)
    options = ' '.join((partuuid, parse_options(me.options)))

    return "title %s\nlinux %s\ninitrd %s\noptions %s" % (me.name, me.kernel, me.initrd, options)


@click.command(help="Convert your grub.cfg bootloader entries into systemd-boot loaders. GRUB_FILE is usually located in /boot/grub and your ESP_PATH is usually /boot.")
@click.argument("grub_file", type=click.Path(dir_okay=False, exists=True, readable=True))
@click.argument("esp_path", type=click.Path(dir_okay=True, exists=True, writable=True))
def cmd(grub_file: str, esp_path: str):
    with open(grub_file, "r") as file:
        grub = file.read().splitlines()

    for index, me in enumerate(gen_menu_entries(grub)):
        with open(esp_path + f'/loader/entries/{index}_{SUFFIX}.conf', 'w+') as file:
            file.write(menuentry_to_systemd(me))
            print("Wrote %s to %s" % (me.name, file.name))

            
if __name__ == "__main__":
    cmd()
