# 軟體建置與安裝

在預覽 (pre) 版本下，提供製作好的 img 檔。請依照以下步驟燒錄至 SD 卡。

> [!CAUTION]  
> **此為 Pre (預覽)版本**：此版本為開發中的測試版本，若遇到 Bug 或需要改進建議，請回報至專案的 GitHub 討論區。  
---

## MicroSD 卡準備

1. 請準備一張 **4GB 以上容量**的 MicroSD 卡。  
2. 容量不需太大，但速度越快越好，**建議使用 U1 / V10** 以上規格。  

---

## 燒錄 IMG

### 1. 下載 IMG

- 前往 [SourceForge](https://sourceforge.net/) 下載 ZeroBETH 的 img 檔案。(尚未上傳)
- 解壓縮後獲得 `zerobeth-0.9.x-pre-raspbian-lite-32bit-bookworm.img` 檔。  

---

### 2. Windows 環境燒錄

1. 下載並安裝 [Raspberry Pi Imager](https://www.raspberrypi.com/software/)。
2. 開啟 Raspberry Pi Imager，依序設定：  
   - **Raspberry Pi Device：** 不用選擇  
   - **Operating System：** 選擇 **Use custom**，指定解壓縮後的 IMG 檔案  
   - **Storage：** 指定要燒錄的 MicroSD 卡  
3. 點選 **寫入 (Write)**，等待燒錄完成。  

---

### 3. Linux 環境燒錄

1. 使用 `dd` 指令進行燒錄：  
   ```bash
   sudo dd if=zerobeth.img of=/dev/sdX bs=4M status=progress conv=fsync
   ```
   - 將 `/dev/sdX` 改為實際的 MicroSD 卡裝置路徑。  
   - 將 `zerobeth.img` 改為 IMG 檔案的實際路徑。  
2. 燒錄完成後，執行同步命令確保寫入：  
   ```bash
   sync
   ```  

---

## 完成燒錄

1. 將燒錄完成的 SD 卡插入 Raspberry Pi Zero 2W。
2. 將 Raspberry Pi Zero 2W 安裝至 ZeroBETH 主板，確保所有硬體連接無誤且已固定完成。
3. 首次開機：開啟電源，等待系統初始化，直至 Zero 上的綠色電源指示燈熄滅。
4. 重新啟動：關閉電源後再次開啟，等待約 1 分鐘，系統將自動進入硬體檢測模式。
5. 根據螢幕提示完成各項檢測。 

---

## 參數設定

1. 進入系統後，從版本資訊頁面連按 **DOWN 鍵 5 次**，進入工程選單。  
2. 設定以下參數：  
   - **Load Cell 公斤數 (20kg / 50kg)**  
   - **最大拉力**：請搭配所購買的 Load Cell 設定：  
     - 20kg Load Cell：不超過 40lb  
     - 50kg Load Cell：不超過 70lb
   - **螺杆型號 (1610 / 1605)**  
   - **張力校正**：根據 Load Cell 的 kg 進行校正。  
3. 完成後重新啟動，進入 **RT 測試模式**。  
4. 建議至少進行 **1000 次張力測試**（約 1.5 小時）以確保穩定性。  

---

## 注意事項

- **避免過熱：**  
  運作過程中，CPU 溫度的升高，可能造成 Wi-Fi 失效，建議加裝散熱片與良好散熱環境。  
- **資料丟失風險：**  
  在燒錄或初始化過程中，避免中途斷電。  
- **工程測試建議：**  
  首次安裝後，請務必完成 **RT 測試模式**下的張力校正與測試，以確保機台精度。  
