# 開發者指南

本教學將說明如何透過 SSH 連線至 ZeroBETH 系統，並進行主程式的開發與修改。適用於進階使用者進行功能擴充、除錯或個人化調整。

---

## 取得 SSH 與 Samba 密碼

ZeroBETH 的 SSH 與 Samba 預設帳號為 `zerobeth`，密碼為裝置初始化時所產生的 8 位數密碼，每台機器皆不同。您可以透過以下方式取得密碼：

1. **開機畫面右下角**：開機時顯示版本號時，右下角會顯示當前密碼。
2. **工程模式中查詢**：進入工程模式後，切換至第 **9-8 頁面** 即可查看密碼。
3. **透過 SD 卡讀取**：若 LCD 無法正常顯示，您也可以將 SD 卡插入電腦，從根目錄中找到 `smb_ssh_pwd.txt` 檔案來取得密碼。

---

## 設定 Wi-Fi 與查詢 IP 位址

在 ZeroBETH 選單中進行 Wi-Fi 設定：

- 進入選單 **2-2**，連接可用 Wi-Fi。
- 連線成功後，前往選單 **3-1** 查看當前機器的 IP 位址。

> **注意**：當 CPU 溫度超過 60°C 時，系統會自動關閉 Wi-Fi 模組。此時請重新連線。

---

## 使用 SSH 進行開發

### 停止目前運行中的主程式 `main.py`

1. 使用 SSH 工具（如 PuTTY）連線至 ZeroBETH 的 IP 位址。  
   帳號：`zerobeth`  
   密碼：裝置顯示的 8 位數密碼

2. 查詢主程式的 PID：

   ```bash
   ps aux | grep main.py
   ```

3. 終止所有 `main.py` 相關的進程（將下列數字替換為實際查到的 PID）：

   ```bash
   sudo kill 111 222 333 444
   ```

---

### 編輯主程式

您現在可以開始編輯主程式。以下以 `nano` 編輯器為例：

```bash
nano /home/zerobeth/main/main.py
```

完成修改後，執行下列指令重新啟動主程式：

```bash
/home/zerobeth/script/boot_run.sh
```

若程式碼無誤，即會自動啟動 ZeroBETH 的操作介面與功能。

---

## 在 Windows 環境下進行開發

若您習慣使用 Windows 進行編輯，可透過 Samba 將 ZeroBETH 的開發資料夾掛載為網路磁碟機，並使用編輯器（如 Notepad++）進行開發。

設定步驟如下：

1. 開啟「我的電腦」或「檔案總管」。
2. 點選「**連線網路磁碟機**」。
3. 在「資料夾」欄輸入：

   ```
   \\YOUR_ZEROBETH_IP\zerobeth-dev
   ```

4. 系統會跳出認證視窗，請輸入：  
   帳號：`zerobeth`  
   密碼：裝置顯示的 8 位數密碼

5. 完成後將會出現一個新的網路磁碟機，可直接開啟並編輯主程式內容。

---

## 支援

如有任何問題，請至 [PicoBETH 討論區](https://github.com/206cc/PicoBETH/discussions) 提出。
