# grub2systemd

Convert your `grub.cfg` bootloader entries into `systemd-boot` loaders.

`GRUB_FILE` is usually located in `/boot/grub` and your ESP_PATH is usually `/boot` or `/boot/efi`.

## Requirements
Requires `blkid` to be installed on the system.

## Installation
`pip3 install g2sd`

## Usage

`g2sd /boot/grub/grub.cfg /boot`

### Help
```bash
Usage: g2sd.py [OPTIONS] GRUB_FILE ESP_PATH

  Convert your grub.cfg bootloader entries into systemd-boot loaders.
  GRUB_FILE is usually located in /boot/grub and your ESP_PATH is usually
  /boot.

Options:
  --help  Show this message and exit.
```

## License
See `LICENSE`. Message me if you'd like to use this project with a different license.
