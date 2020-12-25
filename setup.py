from pathlib import Path
from setuptools import setup


reqs = Path('requirements.txt') \
         .read_text() \
         .split('\n')

setup(name="g2sd",
      version="1.3.1",
      description="Convert GRUB menu entries into Systemd-boot boot loaders.",
      url="https://github.com/thismachinechills/grub2systemd",
      author="thismachinechills (Alex)",
      license="AGPL 3.0",
      packages=['g2sd'],
      zip_safe=True,
      install_requires=reqs,
      keywords="grub2 grub systemd systemd-boot menuentry efi efiboot uefi".split(' '),
      entry_points={"console_scripts":
                        ["g2sd = g2sd.g2sd:cmd"]})
