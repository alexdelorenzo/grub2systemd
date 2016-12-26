from setuptools import setup

with open('requirements.txt', 'r') as file:
    requirements = file.readlines()

setup(name="g2sd",
      version="0.2",
      description="Extract and save Skype chats.",
      url="https://github.com/thismachinechills/grub2systemd",
      author="thismachinechills (Alex)",
      license="AGPL 3.0",
      packages=['g2sd'],
      zip_safe=True,
      install_requires=requirements,
      keywords="grub2 grub systemd systemd-boot menuentry efi efiboot uefi".split(' '),
      entry_points={"console_scripts":
                        ["g2sd = g2sd.g2sd:cmd"]})