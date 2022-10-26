# BK7231 SPI Flasher
This is a simple SPI programmer for BK7231T chips. By default, everyone is using UART bootloader to program BK7231T, but in some rare cases one might overwrite Beken bootloader and thus brick the BK. The only way to unbrick it, is to use SPI flashing mode.

This tool is able to read and write whole flash content of BK7231T (maybe also other chips?) in the SPI mode, by using SPI access pins.

Tested only on Banana Pi, but should also work on Raspberry Pi.

More detailed readme coming soon.
