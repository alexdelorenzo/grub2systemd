# Convert your [GRUB2](https://www.gnu.org/software/grub/manual/grub/grub.html) config to [systemd-boot](https://wiki.archlinux.org/title/systemd-boot)
Convert your GRUB `grub.cfg` bootloader entries to `systemd-boot` loaders.

## Requirements
Requires `blkid` to be installed on the system.

## Installation
`pip3 install g2sd`

## Usage
`g2sd /boot/grub/grub.cfg /boot`

### Help
`GRUB_FILE` is usually located in `/boot/grub` and your `ESP_PATH` is usually `/boot` or `/boot/efi`.

```bash
Usage: g2sd [OPTIONS] GRUB_FILE ESP_PATH

  Convert your grub.cfg bootloader entries into systemd-boot loaders.
  GRUB_FILE is usually located in /boot/grub and your ESP_PATH is usually
  /boot.

Options:
  --help  Show this message and exit.
```

## License
See `LICENSE`. Message me if you'd like to use this project with a different license.
