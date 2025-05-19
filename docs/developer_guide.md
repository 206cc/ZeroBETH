# Developer Guide

This tutorial explains how to connect to the ZeroBETH system via SSH and modify the main program. It is intended for advanced users who wish to expand features, debug, or customize the system.

---

## Obtaining SSH and Samba Password

ZeroBETH's default username for SSH and Samba is `zerobeth`, and the password is an 8-digit code generated during initialization. Each device has a unique password. You can obtain it in the following ways:

1. **Boot screen (bottom-right corner)**: The password is shown in the bottom-right corner during the version display at boot.
2. **Engineering Mode**: Enter engineering mode and go to page **9-8** to view the password.
3. **Via SD card**: If the LCD is not working, insert the SD card into a computer and find the `smb_ssh_pwd.txt` file in the root directory.

---

## Configuring Wi-Fi and Checking IP Address

To configure Wi-Fi in the ZeroBETH menu:

- Go to menu **2-2** to connect to a Wi-Fi network.
- Once connected, go to menu **3-1** to view the device's current IP address.

> **Note**: If the CPU temperature exceeds 60°C, the system will automatically disable the Wi-Fi module. Please reconnect.

---

## Developing via SSH

### Stopping the Currently Running `main.py` Program

1. Use an SSH client (e.g., PuTTY) to connect to the ZeroBETH IP address.  
   Username: `zerobeth`  
   Password: 8-digit code shown on the device

2. Check the PID of `main.py`:

   ```bash
   ps aux | grep main.py
   ```

3. Kill all related `main.py` processes (replace the numbers below with actual PIDs):

   ```bash
   sudo kill 111 222 333 444
   ```

---

### Editing the Main Program

You can now start editing the main program. Here's an example using `nano`:

```bash
nano /home/zerobeth/main/main.py
```

After editing, run the following command to restart the program:

```bash
/home/zerobeth/script/boot_run.sh
```

If there are no issues in the code, ZeroBETH will start running normally.

---

## Development on Windows

If you prefer to develop on Windows, you can use Samba to mount the ZeroBETH development folder as a network drive, then use an editor such as Notepad++.

Steps:

1. Open “This PC” or File Explorer.
2. Click “**Map network drive**”.
3. In the “Folder” field, enter:

   ```
   \\YOUR_ZEROBETH_IP\zerobeth-dev
   ```

4. When prompted, enter:  
   Username: `zerobeth`  
   Password: 8-digit code shown on the device

5. A new network drive will appear, which you can use to edit the main program files.

---

## Support

If you have any questions, please post them in the [PicoBETH Discussion Forum](https://github.com/206cc/PicoBETH/discussions).
