
# Software Build and Installation

In the preview (pre) version, a pre-built IMG file is provided. Please follow the steps below to burn it to the SD card.

> [!CAUTION]  
> **This is a Pre (Preview) Version:** This version is an ongoing development and testing release. If you encounter any bugs or have suggestions for improvement, please report them to the project's GitHub discussion area.  
---

## MicroSD Card Preparation

1. Prepare a **MicroSD card with a capacity of 4GB or more**.  
2. The capacity does not need to be large, but faster speed is preferred. **Recommended to use U1 / V10** or higher.  

---

## Burning the IMG

### 1. Download the IMG

- Visit [SourceForge](https://sourceforge.net/) to download the ZeroBETH IMG file. (Not yet uploaded)
- After extraction, you will get the file `zerobeth-0.9.x-pre-raspbian-lite-32bit-bookworm.img`.  

---

### 2. Burning on Windows

1. Download and install [Raspberry Pi Imager](https://www.raspberrypi.com/software/).
2. Open Raspberry Pi Imager and configure the following:  
   - **Raspberry Pi Device:** No selection needed  
   - **Operating System:** Choose **Use custom** and select the extracted IMG file  
   - **Storage:** Select the MicroSD card to be burned  
3. Click **Write** and wait for the process to complete.  

---

### 3. Burning on Linux

1. Use the `dd` command to burn the image:  
   ```bash
   sudo dd if=zerobeth.img of=/dev/sdX bs=4M status=progress conv=fsync
   ```
   - Replace `/dev/sdX` with the actual MicroSD card device path.  
   - Replace `zerobeth.img` with the actual path of the IMG file.  
2. After burning, execute the sync command to ensure proper writing:  
   ```bash
   sync
   ```  

---

## Completing the Burning Process

1. Insert the burned SD card into the Raspberry Pi Zero 2W.  
2. **Do not connect the ZeroBETH mainboard yet**, directly connect the MicroUSB power cable to boot.  
3. Wait for the system to initialize until the green power indicator goes off.  
4. Attach the Raspberry Pi Zero 2W to the ZeroBETH mainboard, ensure all hardware connections are secure, and complete the installation. Then, power on the system. Wait for about 30 seconds for the system to enter the hardware detection mode.  
5. Follow the on-screen instructions to complete the hardware checks.  

---

## Parameter Settings

1. After entering the system, press the **DOWN key 5 times** on the version information page to enter the engineering menu.  
2. Configure the following parameters:  
   - **Load Cell Weight (20kg / 50kg)**  
   - **Maximum Tension:** Set according to the purchased Load Cell:  
     - 20kg Load Cell: No more than 40lb  
     - 50kg Load Cell: No more than 70lb  
   - **Screw Type (1610 / 1605)**  
   - **Tension Calibration:** Calibrate according to the Load Cell weight.  
3. After completing the settings, restart the system and enter **RT Test Mode**.  
4. It is recommended to perform **at least 1000 tension tests** (approximately 1.5 hours) to ensure stability.  

---

## Notes

- **Avoid Overheating:**  
  During operation, the CPU temperature may rise, potentially causing Wi-Fi to malfunction. It is recommended to install a heatsink and ensure good ventilation.  
- **Risk of Data Loss:**  
  Avoid power interruptions during the burning or initialization process.  
- **Engineering Test Recommendation:**  
  After the initial installation, make sure to complete the **RT Test Mode** tension calibration and testing to ensure system accuracy.  
