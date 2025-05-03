[![cht](https://img.shields.io/badge/lang-cht-green.svg)](README.cht.md)
[![en](https://img.shields.io/badge/lang-en-red.svg)](README.md)

> [!TIP]
> Translated by ChatGPT  
> For the Chinese version, please click the ![image](https://img.shields.io/badge/lang-cht-green.svg) badge above.

# ZeroBETH

ZeroBETH is an extended version based on [PicoBETH](https://github.com/206cc/PicoBETH), upgrading the main controller from Raspberry Pi Pico to Raspberry Pi Zero 2 W, offering higher performance and more expansion capabilities. This variant retains the original design philosophy: economical, intuitive, and precise, while providing greater flexibility for advanced users and developers.

> [!TIP]
> Currently in testing phase. Will be released once completed and verified.

---

### Preview Videos

| Category | Description | Link |
|----------|-------------|------|
| Stringing Demo | Actual stringing demonstration using ZeroBETH | [Watch Video](https://youtu.be/M76PxqrGcno) |
| Comparison Demo | Performance comparison between ZeroBETH and PicoBETH (boot time, pulling response, etc.) | [Watch Video](https://youtu.be/osMxNlAMeeI) |
| New UI Design | Redesigned UI interface (LCD menu and screen refresh improvements) | [Watch Video](https://youtu.be/-ikYBSZI7xk) |

---

## Hardware Comparison: Pico vs Zero 2 W

| Item              | Raspberry Pi Pico                     | Raspberry Pi Zero 2 W             |
|-------------------|----------------------------------------|-----------------------------------|
| Processor         | Dual-core 133MHz                       | Quad-core 1GHz                    |
| Memory            | 264KB                                  | 512MB                             |
| Wireless          | None                                   | Wi-Fi 802.11n                     |
| Storage           | 2MB                                    | microSD                           |
| OS Support        | None                                   | Linux-based (Raspberry Pi OS)     |
| Price (USD)       | Around $7.00                           | Around $20.00                     |

---

## Hardware Differences: PicoBETH vs ZeroBETH

To upgrade to ZeroBETH, simply replace the mainboard and keypad board in PicoBETH EP6.

![img_pcb1](docs/img_pcb1.jpg)  
![img_pcb2](docs/img_pcb2.jpg)  
![img_pcb3](docs/img_pcb3.jpg)

**PCB & Gerber Files:** (To be uploaded after verification is complete)

### Cost Difference

| Item             | PicoBETH Cost | ZeroBETH Cost         | Notes                             |
|------------------|---------------|------------------------|-----------------------------------|
| Main Controller  | $7            | Around $20.00          | Based on Taiwan retail pricing    |
| Storage          | None          | Around $5 (16GB microSD) | Minimal capacity is sufficient    |

---

## Software Differences: PicoBETH vs ZeroBETH

### PicoBETH: Cost-effective and reliable

PicoBETH has been tested over a long period and validated by users. It offers stable performance and great value, ideal for entry-level stringing machines. It meets the needs of users who don’t require advanced features.

### ZeroBETH: Feature-rich and developer-friendly

- **OTA Firmware Update:** Automatically downloads and installs updates via Wi-Fi.
- **Faster Screen Refresh:** Improved performance leads to smoother screen updates. UI is redesigned.
- **Samba File Sharing:** Edit source code and settings over the local network, no cable needed—ideal for development.

### ZeroBETH Software Roadmap

| Version | Display Type     | Description                                                             |
|---------|------------------|-------------------------------------------------------------------------|
| v1      | 2004 LCD         | Redesigned UI and menu system                                           |
| v2      | 4" ILI9488 LCD   | Full-color 480x320 IPS LCD for an intuitive and advanced GUI. To be developed after v1 is complete |

---

## Feature Comparison Table

| Feature             | PicoBETH         | ZeroBETH         | Notes                                           |
|---------------------|------------------|------------------|------------------------------------------------|
| Tension Accuracy     | ±0.05 lb         | ±0.05 lb         | Maximum tension fluctuation after stabilization |
| Sampling Rate        | ≥80Hz            | ≥80Hz            | Depends on SparkFun HX711 module               |
| Pulling Frequency    | Lower            | Higher           | Faster processing improves response time       |
| OTA Firmware Update  | v2.80E and above | Supported        | Update firmware via Wi-Fi                      |
| UI Interface         | Minimal          | Redesigned       | v1: 2004 LCD, v2: 4" full-color IPS LCD        |

---

## Installation Guide

1. Build the machine body following the [PicoBETH project instructions](https://github.com/206cc/PicoBETH).
2. Replace the mainboard and keypad board in EP6 with ZeroBETH-specific parts.
3. Write the ZeroBETH firmware to a microSD card, insert it into the Zero 2 W, and install it on the machine to start using.

---

## Additional Documentation (In Progress)

> The following documents are currently being organized and drafted. Content will be added once ready.

- Operation & Settings Guide
- Software Build & Installation Guide

---

## Support

For questions, please post in the [PicoBETH Discussions](https://github.com/206cc/PicoBETH/discussions).

---

## Acknowledgements

- [HX711 Raspberry Pi HX711 Python Bindings](https://github.com/endail/hx711-rpi-py)
- [RPI-PICO-I2C-LCD](https://github.com/T-622/RPI-PICO-I2C-LCD), modified for Raspberry Pi Zero 2 W

---

## License

- **Source Code License:** GNU General Public License v3.0 (GPLv3)  
- **Hardware Design License:** CERN Open Hardware Licence v2 – Weakly Reciprocal (CERN-OHL-W)
