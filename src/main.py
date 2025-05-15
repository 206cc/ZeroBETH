#!/usr/bin/python3
# ZeroBETH - Open-Source Badminton Stringing Machine Firmware
# Copyright (C) 2025 KuoKuo
# Project homepage: https://github.com/206cc/ZeroBETH
# Contact: 500119.cpc@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.

VERSION = "0.9.65-Pre"
VERDATE = "2025-05-13"

# --- Standard library imports ---
import os
import sys
import re
import time
import random
import hashlib
import datetime
import tarfile
import subprocess

# --- Third-party imports ---
import requests
import psutil
import RPi.GPIO as GPIO
import lgpio
from gpiozero import LED

# --- Local application/library specific imports ---
from HX711 import *
from lib.rpi_i2c_lcd import I2cLcd

# --- Multiprocessing imports ---
from multiprocessing import Process, Manager, sharedctypes
from multiprocessing import Value as mpValue

KNOT = 15
LB_MIN = 15
LB_MAX = 35
PS_MAX = 30
KNOT_RANG = [5, 30]
CP_SLOW = 30
CP_FAST = 40
CORR_COEF_AUTO = 1
LOG_MAX = 50
CA_REM = 0.1
HX711_DIFRT = 2.0
HEAD_RESET = 1
LOAD_CELL_KG = 50
SLIDE_TABLE = 1610
BUTTON_MODE = {
    "USE_PULLDOWN": False
}
TEMP_WARNING_WIFI = 60
TEMP_WARNING_CPU = 70

# 初始化 GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

# 其它參數
FIRST_TEST = 1
SAVE_CFG_ARRAY = ['DEFAULT_LB','PRE_STRECH','MOTOR_STEPS','HX711_CAL','TENSION_COUNT','BOOT_COUNT', 'LB_KG_SELECT','CP_SW','KNOT','FIRST_TEST','BZ_SW','HX711_V0','MOTOR_SPEED_LV','LOAD_CELL_KG','LB_MAX','SLIDE_TABLE']
MENU_ARR = [[5,0],[4,1],[4,2],[14,0],[14,1],[15,1],[17,1],[18,1],[19,1],[8,3],[19,3]]
OPTIONS_DICT = {
    "UNIT_ARR": ['BOTH', 'LB  ', 'KG  '],
    "ONOFF_ARR": ['OFF', 'ON '],
    "MA_ARR": ['M', 'C'],
    "PSKT_ARR": ['PS', 'KT'],
    "LOAD_CELL": ['20KG', '50KG'],
}
TS_LB_ARR = [[4,0],[5,0],[7,0]]
TS_KG_ARR = [[4,1],[5,1],[7,1]]
TS_KT     = [[14,0]]
TS_PS_ARR = [[17,0],[18,0]]
MOTOR_MAX_STEPS = 10000
MOTOR_RS_STEPS = 1000
HX711_V0 = 0
RT_MODE = 0
HEAD_RESET_COUNT = 0
ABORT_GRAM = 1000
LB_KG_SELECT = 0
DEFAULT_LB = 20.0
PRE_STRECH = 10
CP_SW = 1
BZ_SW = 1
MOTOR_SPEED_V1 = 80
MOTOR_SPEED_V2 = 500
MOTOR_SPEED_V3 = 1000
MOTOR_SPEED_LV = 8
FWD_ABORT_COUNT = 100
WIFI_IP = "N/A"
MAIN_PATH = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE = os.path.join(MAIN_PATH, 'config.cfg')
SSH_FIAL = os.path.join(MAIN_PATH, '.zero_ssh')
WIFI_CFG_FILE = os.path.join(MAIN_PATH, 'wifi.cfg')
WIFI_SH_FILE = os.path.join(MAIN_PATH, 'wifi_connect.sh')
SSH_SH_FILE = os.path.join(MAIN_PATH, '.zero_ssh')
SYS_LOG_FILE = os.path.join(MAIN_PATH, 'sys_log.txt')
RT_LOG_FILE = os.path.join(MAIN_PATH, 'rt_logs.txt')
LIST_URL = "https://zerobeth-ota.206cc.tw/list.json"
DOWNLOAD_BASE_URL = "https://zerobeth-ota.206cc.tw/"
DEST_DIR = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "main"))

BUTTON_MODE["PULL_TYPE"] = GPIO.PUD_DOWN if BUTTON_MODE["USE_PULLDOWN"] else GPIO.PUD_UP
BUTTON_MODE["PRESSED_STATE"] = GPIO.HIGH if BUTTON_MODE["USE_PULLDOWN"] else GPIO.LOW

# 腳位定義（BCM）
PUL_NEG = 24
PUL_POS = 23
DIR_NEG = 12
DIR_POS = 25

# 開啟 GPIO 控制器
h = lgpio.gpiochip_open(0)

# 宣告 GPIO 為輸出腳
lgpio.gpio_claim_output(h, PUL_NEG, 0)
lgpio.gpio_claim_output(h, PUL_POS, 0)
lgpio.gpio_claim_output(h, DIR_NEG, 0)
lgpio.gpio_claim_output(h, DIR_POS, 0)

# 限位開關
MOTOR_SW_FRONT = 7
MOTOR_SW_REAR = 16
GPIO.setup(MOTOR_SW_FRONT, GPIO.IN, pull_up_down=BUTTON_MODE["PULL_TYPE"])
GPIO.setup(MOTOR_SW_REAR, GPIO.IN, pull_up_down=BUTTON_MODE["PULL_TYPE"])

# 按鍵
BUTTON_HEAD = 20
BUTTON_UP = 5
BUTTON_DOWN = 6
BUTTON_LEFT = 14
BUTTON_RIGHT = 15
BUTTON_SETTING = 18
BUTTON_EXIT = 8

BUTTON_PINS = {
    "BUTTON_HEAD": BUTTON_HEAD,
    "BUTTON_SETTING": BUTTON_SETTING,
    "BUTTON_EXIT": BUTTON_EXIT,
    "BUTTON_UP": BUTTON_UP,
    "BUTTON_DOWN": BUTTON_DOWN,
    "BUTTON_LEFT": BUTTON_LEFT,
    "BUTTON_RIGHT": BUTTON_RIGHT,
    "MOTOR_SW_FRONT": MOTOR_SW_FRONT,
    "MOTOR_SW_REAR": MOTOR_SW_REAR
}
BUTTON_CLICK_MS = 150

for btn in [BUTTON_HEAD, BUTTON_UP, BUTTON_DOWN, BUTTON_LEFT, BUTTON_RIGHT, BUTTON_SETTING, BUTTON_EXIT]:
    GPIO.setup(btn, GPIO.IN, pull_up_down=BUTTON_MODE["PULL_TYPE"])

# LED
LED_GREEN = LED(26)
LED_YELLOW = LED(19)
LED_RED = LED(13)
LED_GREEN.off()
LED_YELLOW.off()
LED_RED.off()

# 蜂鳴器
BEEP = 27
GPIO.setup(BEEP, GPIO.OUT)

# 全域變數
MOTOR_STEPS = 0
MENU_TEMP = 0
CURSOR_XY_TS_TEMP = 1
TENSION_COUNT = 0
BOOT_COUNT = 0
TIMER = 0
ERR_MSG = ["", ""]
ABORT_LM = 4000
TS_ARR = []
KNOT_FLAG = 0
RT_CC = [1.0, 1.0]
TIMER_FLAG = 0
ENGINEER_MENU = 0

# 2004 I2C LCD 設定
I2C_ADDR     = 0x27
I2C_NUM_COLS = 20
I2C_NUM_ROWS = 4
LCD = I2cLcd(i2c_bus=1, i2c_addr=I2C_ADDR, num_lines=I2C_NUM_ROWS, num_columns=I2C_NUM_COLS)

hx = SimpleHX711(4, 17, -370, -367471)
hx.setUnit(Mass.Unit.G)
hx.zero()

# LCD PUTSTR
def lcd_putstr(text, x, y, length):
    text = text[:length]
    text = f'{text :{" "}<{length}}'
    LCD.move_to(x, y)
    LCD.putstr(text)

# errno check
def handle_error(e, func):
    global ERR_MSG
    try:
        mem_used = psutil.virtual_memory().used
        msg = f"{e}/MEM:{mem_used} bytes"
        ERR_MSG[0] = msg
        logs_save(msg, func)
        with open(SYS_LOG_FILE, "a") as f:
            import traceback
            f.write(traceback.format_exc())

    except Exception as fatal:
        print(f"[FATAL] handle_error() failed: {fatal}")

# Read file parameters 參數讀取
def config_read():
    global HX711
    if os.path.isfile(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as file:
            data = file.read()
            config_list = data.split(',')
            for val in config_list:
                cfg = val.split("=")
                if cfg[0] and cfg[0] in SAVE_CFG_ARRAY:
                    if cfg[0] == "HX711_CAL":
                        HX711_CAL.value = float(cfg[1])
                    else:
                        if "." in cfg[1]:
                            globals()[cfg[0]] = float(cfg[1])
                        else:
                            globals()[cfg[0]] = int(cfg[1])
        HX711['HX711_CAL'] = HX711_CAL.value

# Writing file Parameter 參數寫入
def config_save():
    global HX711

    HX711['HX711_CAL'] = HX711_CAL.value
    save_cfg = ""

    for val in SAVE_CFG_ARRAY:
        if val == "HX711_CAL":
            save_cfg += f"{val}={round(HX711_CAL.value, 2)},"
        else:
            if isinstance(globals().get(val), (int, float)):
                save_cfg += f"{val}={globals()[val]},"

    with open(CONFIG_FILE, 'w') as file:
        file.write(save_cfg)

# Writing file LOG 寫入LOG
def logs_save(log_str, flag):
    global ERR_MSG
    ERR_MSG[1] = f"{log_str}"
    file = open(SYS_LOG_FILE, 'a')
    file.write(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}][{get_cpu_temp():.1f}C] {flag}:{TENSION_COUNT}T/{log_str}\n")
    file.close()
    os.sync()

# Logs cleanup 整理 LOGS
def logs_cleanup():
    SYS_LOG_ROTATE = os.path.join(MAIN_PATH, "sys_log.1.txt")
    if os.path.isfile(SYS_LOG_FILE) and os.stat(SYS_LOG_FILE).st_size > 100 * 1024:
        os.rename(SYS_LOG_FILE, SYS_LOG_ROTATE)

# Active buzzer 有源蜂鳴器
def beepbeep(run_time):
    if BZ_SW == 1:
        GPIO.output(BEEP, GPIO.HIGH)
        time.sleep(run_time)
        GPIO.output(BEEP, GPIO.LOW)
    else:
        time.sleep(run_time)

# Tension display 張力顯示
def tension_info(tension, flag):
    if tension is None:
        tension = TENSION_MON.value

    if flag == 1:
        lcd_putstr("{: >4.1f}".format(round(tension[0] * 0.00220462, 1)), 9, 0, 4)
        lcd_putstr("{: >4.1f}".format(round(tension[0] / 1000, 1)), 9, 1, 4)
        tension_diff = tension[0] - tension[1]
        if tension_diff <= -100:
            ts_str = '---'
        elif tension_diff >= 100:
            ts_str = '+++'
        else:
            ts_str = "{:+03d}".format(tension_diff)
        
        lcd_putstr(ts_str, 16, 3, 3)
    else:
        lcd_putstr("{: >4.1f}".format(tension * 0.0022), 9, 0, 4)
        lcd_putstr("{: >4.1f}".format(tension / 1000), 9, 1, 4)
        if flag == 0:
            ts_arr = []
            for i in range(5):
                ts_arr.append(TENSION_MON.value)
                time.sleep(0.03)
            ts_arr = sorted(ts_arr)
            lcd_putstr("{: >5d}G".format(ts_arr[2]), 14, 3, 6)
                
        elif flag == 3:
            lcd_putstr("     G", 14, 3, 6)
        elif flag == 2:
            lcd_putstr("{: >5d}R".format(RT_MODE), 14, 3, 6)

def set_direction(forward=True):
    if forward:
        lgpio.gpio_write(h, DIR_POS, 1)
        lgpio.gpio_write(h, DIR_NEG, 0)
    else:
        lgpio.gpio_write(h, DIR_POS, 0)
        lgpio.gpio_write(h, DIR_NEG, 1)

def step_once(delay):
    lgpio.gpio_write(h, PUL_POS, 1)
    lgpio.gpio_write(h, PUL_NEG, 0)
    delay_us(delay)
    lgpio.gpio_write(h, PUL_POS, 0)
    lgpio.gpio_write(h, PUL_NEG, 1)
    delay_us(delay)

def delay_us(microseconds):
    target_time = time.perf_counter_ns() + microseconds * 1000
    while time.perf_counter_ns() < target_time:
        pass

# Increase in tension 張力增加
def forward(delay, steps, check, init):
    global RT_MODE
    tennis_g = 453 * 40
    LED_GREEN.off()
    IS_TENSIONING.value = 1
    delay_us_value = MOTOR_SPEED_V1
    abort_flag_1 = 0
    abort_flag_2 = 0
    abort_flag_3 = 0
    set_direction(False)
    fail_log = {}
    for i in range(steps):
        start_ns = time.perf_counter_ns()
        tension = TENSION_MON.value

        if check == 1:
            if MOTOR_STP.value == 1:
                IS_TENSIONING.value = 0
                MOTOR_STP.value = 0
                if len(fail_log) != 0:
                    logs_save(f"{fail_log}", "forward()")
                    
                return i

            if GPIO.input(BUTTON_EXIT) == BUTTON_MODE["PRESSED_STATE"]:
                head_reset(None)
                IS_TENSIONING.value = 0
                MOTOR_STP.value = 0
                logs_save("Abort BUTTON_EXIT", "forward()")
                return "Abort"

            if i > ABORT_LM and tension < 2267 and RT_MODE == 0:
                abort_flag_1 = abort_flag_1 + 1
                fail_log[i] = {}
                fail_log[i][0] = "No String?"
                fail_log[i][1] = abort_flag_1
                if abort_flag_1 > FWD_ABORT_COUNT:
                    head_reset(None)
                    IS_TENSIONING.value = 0
                    MOTOR_STP.value = 0
                    logs_save("No String?", "forward()")
                    return "No String?"
            else:
                abort_flag_1 = 0

            if tension < -2267:
                abort_flag_2 = abort_flag_2 + 1
                fail_log[i] = {}
                fail_log[i][0] = "YZC-133 Reversed?"
                fail_log[i][1] = abort_flag_2
                if abort_flag_2 > FWD_ABORT_COUNT:
                    head_reset(None)
                    IS_TENSIONING.value = 0
                    MOTOR_STP.value = 0
                    logs_save("YZC-133 Reversed?", "forward()")
                    return "YZC-133 Reversed?"
            else:
                abort_flag_2 = 0

        if GPIO.input(MOTOR_SW_REAR) == BUTTON_MODE["PRESSED_STATE"] or i > MOTOR_MAX_STEPS:
            head_reset(None)
            if init:
                return i
            IS_TENSIONING.value = 0
            MOTOR_STP.value = 0
            RT_MODE = 0
            logs_save(f"Over Limits {i}", "forward()")
            return f"Over Limits {i}"

        if ABORT_GRAM < tension:
            abort_flag_3 = abort_flag_3 + 1
            fail_log[i] = {}
            fail_log[i][0] = "ABORT GRAM"
            fail_log[i][1] = abort_flag_3
            if abort_flag_3 > FWD_ABORT_COUNT:
                head_reset(None)
                IS_TENSIONING.value = 0
                MOTOR_STP.value = 0
                RT_MODE = 0
                logs_save(f"ABORT GRAM/{ABORT_GRAM}/{tension}", "forward()")
                return "ABORT GRAM"
        else:
            abort_flag_3 = 0

        if abort_flag_1 == 0 and abort_flag_2 == 0 and abort_flag_3 == 0:
            if i < 30:
                target_delay_us = MOTOR_SPEED_V3
                
            elif tennis_g < tension:
                target_delay_us = MOTOR_SPEED_V2
                
            else:
                elapsed_us = (time.perf_counter_ns() - start_ns) // 1000
                target_delay_us = max(delay - elapsed_us, 0)

            target_ns = time.perf_counter_ns() + target_delay_us * 1000
            while time.perf_counter_ns() < target_ns:
                pass

            # 步進馬達驅動步序
            step_once(delay_us_value)
        else:
            delay_us(MOTOR_SPEED_V3)
            step_once(delay_us_value)
            
    if len(fail_log) != 0:
        logs_save(f"{fail_log}", "forward()")

# Tension decrease 張力減少
def backward(delay, steps, check):
    global MOTOR_STEPS
    LED_GREEN.off()
    delay_us_value = MOTOR_SPEED_V1
    set_direction(True)
    for i in range(steps):
        start_ns = time.perf_counter_ns()

        if check == 1:
            if GPIO.input(MOTOR_SW_FRONT) == BUTTON_MODE["PRESSED_STATE"]:
                time.sleep(0.2)
                forward(MOTOR_SPEED_V1 * (11 - MOTOR_SPEED_LV) / 2, MOTOR_RS_STEPS, 0, 0)
                return 0

        if i < 30:
            target_delay_us = MOTOR_SPEED_V3
            
        else:
            elapsed_us = (time.perf_counter_ns() - start_ns) // 1000
            target_delay_us = max(delay - elapsed_us, 0)
        
        target_ns = time.perf_counter_ns() + target_delay_us * 1000
        while time.perf_counter_ns() < target_ns:
            pass

        step_once(delay_us_value)

# Bead clip head Reset 珠夾頭復位
def head_reset(step):
    global HEAD_RESET_COUNT
    LED_YELLOW.on()
    time.sleep(0.2)

    if HEAD_RESET_COUNT == 99:
        backward(MOTOR_SPEED_V1, MOTOR_MAX_STEPS, 1)
        logs_save("head_reset", "head_reset()")
        HEAD_RESET_COUNT = 0

    elif step and HEAD_RESET == 1:
        backward(MOTOR_SPEED_V1, step, 1)
        HEAD_RESET_COUNT = HEAD_RESET_COUNT + 1
        if abs(TENSION_MON.value) > 100:
            backward(MOTOR_SPEED_V1, MOTOR_MAX_STEPS, 1)
            logs_save(f"head_reset_step_err:{TENSION_MON.value}G", "head_reset()")
            HEAD_RESET_COUNT = 0
    else:
        backward(MOTOR_SPEED_V1, MOTOR_MAX_STEPS, 1)
        HEAD_RESET_COUNT = HEAD_RESET_COUNT + 1

    beepbeep(0.3)
    LED_YELLOW.off()
    LED_GREEN.on()

def lb_kg_select():
    global TS_ARR
    if LB_KG_SELECT == 1:
        TS_ARR = TS_LB_ARR + TS_KT + TS_PS_ARR
    elif LB_KG_SELECT == 2:
        TS_ARR = TS_KG_ARR + TS_KT + TS_PS_ARR
    else:
        TS_ARR = TS_LB_ARR + TS_KG_ARR + TS_KT + TS_PS_ARR

def sys_logs_show():
    lcd_putstr("=ZeroBETH= SYSLOG", 0, 3, I2C_NUM_COLS)
    lines = []
    if os.path.isfile(SYS_LOG_FILE):
        with open(SYS_LOG_FILE, 'r') as file:
            for line in file:
                lines.append(line)
                if len(lines) > 50:
                    lines.pop(0)
    
        lens = len(lines)
        i = 0
        while True:
            lcd_putstr("{:02}".format(i), 18, 3, 2)
            str_list = [lines[(lens - 1 - i)][j:j+19] for j in range(0, 57, 19)]
            lcd_putstr(str_list[0], 0, 0, I2C_NUM_COLS)
            lcd_putstr(str_list[1], 0, 1, I2C_NUM_COLS)
            lcd_putstr(str_list[2], 0, 2, I2C_NUM_COLS)
            beepbeep(0.3)
            while True:
                if GPIO.input(BUTTON_LEFT) == BUTTON_MODE["PRESSED_STATE"]:
                    i = max(i - 1, 0)
                    break
                
                elif GPIO.input(BUTTON_RIGHT) == BUTTON_MODE["PRESSED_STATE"]:
                    i = min(i + 1, lens)
                    break
                    
                elif GPIO.input(BUTTON_EXIT) == BUTTON_MODE["PRESSED_STATE"]:
                    beepbeep(0.1)
                    shutdown_reboot(1)
                    
                time.sleep(0.05)
    else:
        lcd_putstr("No log file found.", 0, 0, I2C_NUM_COLS)
        lcd_putstr("Press EXIT Restart.", 0, 1, I2C_NUM_COLS)
        while True:
            if GPIO.input(BUTTON_EXIT) == BUTTON_MODE["PRESSED_STATE"]:
                beepbeep(0.1)
                shutdown_reboot(1)
            time.sleep(0.05)

# Main screen 主畫面顯示
def main_interface():
    # wifi status
    if WIFI_IP.count('.') == 3:
        wifi_status = "W"
    else:
        wifi_status = " "

    LCD.hide_cursor()
    lcd_putstr(f"LB:     /--.- {OPTIONS_DICT['PSKT_ARR'][KNOT_FLAG]}:  %", 0, 0, I2C_NUM_COLS)
    lcd_putstr("KG:     /--.-       ", 0, 1, I2C_NUM_COLS)
    lcd_putstr("                    ", 0, 2, I2C_NUM_COLS)
    lcd_putstr(f"=ZERO= {wifi_status} L{MOTOR_SPEED_LV} {OPTIONS_DICT['MA_ARR'][CP_SW]}", 0, 3, I2C_NUM_COLS)
    lcd_putstr(f"{DEFAULT_LB:.1f}", 4, 0, 4)
    lcd_putstr(f"{DEFAULT_LB * 0.45359237: >4.1f}", 4, 1, 4)
    lcd_putstr(f"{PRE_STRECH: >2d}", 17, 0, 2)

# Timer 計時器顯示
def show_timer():
    if TIMER:
        LCD.hide_cursor()
        lcd_putstr("   m  ", 14, 1, 6)
        timer_diff = TIMER_FLAG - TIMER
        if timer_diff < 0:
            return 0
        
        timer_diff = int(timer_diff)
        lcd_putstr("{: >3d}".format(timer_diff // 60), 14, 1, 3)
        lcd_putstr("{: >2d}".format(timer_diff % 60), 18, 1, 2)

# Hardware Functional Testing 硬體功能測試
def hw_test(flag, ori_BZ_SW):
    global FIRST_TEST, BZ_SW

    LED_RED.off()
    i = 1

    while True:
        if i == 1:
            lcd_putstr(f"T{i}: BUTTON_SETTING P", 0, 2, I2C_NUM_COLS)
            lcd_putstr("    ress", 0, 3, 14)
            if button_list('BUTTON_SETTING'):
                lcd_putstr(f"T{i}: PASSED", 0, 2, I2C_NUM_COLS)
                lcd_putstr("", 0, 3, 14)
                i = i + 1

        elif i == 2:
            lcd_putstr(f"T{i}: BUTTON_UP Press", 0, 2, I2C_NUM_COLS)
            if button_list('BUTTON_UP'):
                lcd_putstr(f"T{i}: PASSED", 0, 2, I2C_NUM_COLS)
                lcd_putstr("", 0, 3, 14)
                i = i + 1

        elif i == 3:
            lcd_putstr(f"T{i}: BUTTON_DOWN Pres", 0, 2, I2C_NUM_COLS)
            lcd_putstr("    s", 0, 3, 14)
            if button_list('BUTTON_DOWN'):
                lcd_putstr(f"T{i}: PASSED", 0, 2, I2C_NUM_COLS)
                lcd_putstr("", 0, 3, 14)
                i = i + 1

        elif i == 4:
            lcd_putstr(f"T{i}: BUTTON_LEFT Pre", 0, 2, I2C_NUM_COLS)
            lcd_putstr("    ss", 0, 3, 14)
            if button_list('BUTTON_LEFT'):
                lcd_putstr(f"T{i}: PASSED", 0, 2, I2C_NUM_COLS)
                lcd_putstr("", 0, 3, 14)
                i = i + 1

        elif i == 5:
            lcd_putstr(f"T{i}: BUTTON_RIGHT Pre", 0, 2, I2C_NUM_COLS)
            lcd_putstr("    ss", 0, 3, 14)
            if button_list('BUTTON_RIGHT'):
                lcd_putstr(f"T{i}: PASSED", 0, 2, I2C_NUM_COLS)
                lcd_putstr("", 0, 3, 14)
                i = i + 1

        elif i == 6:
            lcd_putstr(f"T{i}: BUTTON_EXIT Pres", 0, 2, I2C_NUM_COLS)
            lcd_putstr("    s", 0, 3, 14)
            if button_list('BUTTON_EXIT'):
                lcd_putstr(f"T{i}: PASSED", 0, 2, I2C_NUM_COLS)
                lcd_putstr("", 0, 3, 14)
                i = i + 1

        elif i == 7:
            lcd_putstr(f"T{i}: BUTTON_HEAD Pres", 0, 2, I2C_NUM_COLS)
            lcd_putstr("    s", 0, 3, 14)
            if button_list('BUTTON_HEAD'):
                lcd_putstr(f"T{i}: PASSED", 0, 2, I2C_NUM_COLS)
                lcd_putstr("", 0, 3, 14)
                i = i + 1

        elif i == 8:
            lcd_putstr(f"T{i}: MOTO_LM_REAR Pre", 0, 2, I2C_NUM_COLS)
            lcd_putstr("    ss", 0, 3, 14)
            if button_list("MOTOR_SW_REAR"):
                lcd_putstr(f"T{i}: PASSED", 0, 2, I2C_NUM_COLS)
                lcd_putstr("", 0, 3, 14)
                i = i + 1

        elif i == 9:
            lcd_putstr(f"T{i}: MOTO_LM_FRONT Pr", 0, 2, I2C_NUM_COLS)
            lcd_putstr("    ess", 0, 3, 14)
            if button_list("MOTOR_SW_FRONT"):
                lcd_putstr(f"T{i}: PASSED", 0, 2, I2C_NUM_COLS)
                lcd_putstr("", 0, 3, 14)
                i = i + 1

        elif i == 10:
            lcd_putstr(f"T{i}: LED GREEN ON?", 0, 2, I2C_NUM_COLS)
            lcd_putstr("[Pres SET KEY]", 0, 3, 14)
            LED_GREEN.on()
            if button_list('BUTTON_SETTING'):
                LED_GREEN.off()
                lcd_putstr(f"T{i}: PASSED", 0, 2, I2C_NUM_COLS)
                i = i + 1

        elif i == 11:
            lcd_putstr(f"T{i}: LED YELLOW ON?", 0, 2, I2C_NUM_COLS)
            LED_YELLOW.on()
            if button_list('BUTTON_SETTING'):
                LED_YELLOW.off()
                lcd_putstr(f"T{i}: PASSED", 0, 2, I2C_NUM_COLS)
                i = i + 1

        elif i == 12:
            lcd_putstr(f"T{i}: LED RED ON?", 0, 2, I2C_NUM_COLS)
            LED_RED.on()
            if button_list('BUTTON_SETTING'):
                LED_RED.off()
                lcd_putstr(f"T{i}: PASSED", 0, 2, I2C_NUM_COLS)
                i = i + 1

        elif i == 13:
            lcd_putstr(f"T{i}: BEEP ON?", 0, 2, I2C_NUM_COLS)
            beepbeep(0.2)
            if button_list('BUTTON_SETTING'):
                lcd_putstr(f"T{i}: PASSED", 0, 2, I2C_NUM_COLS)
                i = i + 1

        elif i == 14:
            lcd_putstr(f"T{i}: Right KEY FWD?", 0, 2, I2C_NUM_COLS)
            if button_list('BUTTON_RIGHT'):
                forward(MOTOR_SPEED_V3, 500, 0, 0)
            if button_list('BUTTON_SETTING'):
                lcd_putstr(f"T{i}: PASSED", 0, 2, I2C_NUM_COLS)
                i = i + 1

        elif i == 15:
            lcd_putstr(f"T{i}: Left KEY BWD?", 0, 2, I2C_NUM_COLS)
            if button_list('BUTTON_LEFT'):
                backward(MOTOR_SPEED_V3, 500, 1)
            if button_list('BUTTON_SETTING'):
                lcd_putstr(f"T{i}: PASSED", 0, 2, I2C_NUM_COLS)
                i = i + 1

        elif i == 16:
            lcd_putstr(f"T{i}: Head Over 1000G", 0, 2, I2C_NUM_COLS)
            lcd_putstr(" ", 0, 3, 14)
            if abs(TENSION_MON.value) > 1000:
                lcd_putstr(f"All TESTS PASSED!", 0, 2, I2C_NUM_COLS)
                FIRST_TEST = 2
                if flag == 0:
                    BZ_SW = ori_BZ_SW
                    config_save()
                
                break
        
        # 持續顯示張力
        tension_info(None, 0)
        time.sleep(0.2)
        
    lcd_putstr("[Press EXIT Restart]", 0, 3, 20)
    while True:
        if button_list('BUTTON_EXIT'):
            beepbeep(0.1)
            shutdown_reboot(1)
        
        time.sleep(0.05)

# Reliability Testing Mode 穩定性測試模式
def rt_mode():
    global WIFI_IP
    try:
        global BUTTON_LIST, RT_MODE, PRE_STRECH, DEFAULT_LB, TIMER, CP_SW, RT_CC
        tmp_TENSION_COUNT = TENSION_COUNT
        tmp_RT_MODE = RT_MODE

        # 檢查 CPU 溫度
        if get_cpu_temp() >= TEMP_WARNING_CPU:
            lcd_putstr(f"CPU Temp High! {int(get_cpu_temp())}C", 0, 2, I2C_NUM_COLS)
            logs_save(f"CPU Temp High! {int(get_cpu_temp())}C", "rt_mode()")
            RT_MODE = 0
            while True:
                if button_list('BUTTON_EXIT'):
                    return False
                
                time.sleep(0.05)
                
        elif get_cpu_temp() >= TEMP_WARNING_WIFI and check_wifi_status() == True:
            logs_save("Wi-Fi turn off", "rt_mode()")
            change_wifi("down")
            WIFI_IP = "Wi-Fi Down"
            lcd_putstr(" ", 7, 3, 1)

        if RT_MODE == 1:
            RT_LOG_ROTATE_FILE = os.path.join(MAIN_PATH, 'rt_logs.1.txt')

            if os.path.isfile(RT_LOG_FILE):
                os.remove(RT_LOG_FILE)

            if os.path.isfile(RT_LOG_ROTATE_FILE):
                os.remove(RT_LOG_ROTATE_FILE)
            CP_SW = 1
            PRE_STRECH = 10
            RT_CC[0], RT_CC[1] = CORR_COEF.value, CORR_COEF.value
            TIMER = time.time()
            lcd_putstr("Pres SET Run RTM", 0, 2, I2C_NUM_COLS)
            lcd_putstr("{: >2d}".format(PRE_STRECH), 17, 0, 2)
            while True:
                if button_list('BUTTON_SETTING'):
                    break
                
                time.sleep(0.05)

        # 自動調整張力係數
        if RT_MODE % 10 == 0:
            RT_CC[0] = random.uniform(0.95, 1.2)
            CORR_COEF.value = RT_CC[0]

        DEFAULT_LB = (LB_MAX - 15) + (RT_MODE % 11)
        lcd_putstr("{:.1f}".format(DEFAULT_LB), 4, 0, 4)
        lcd_putstr("{: >4.1f}".format(DEFAULT_LB * 0.45359237), 4, 1, 4)
        lcd_putstr("    --G", 13, 3, 7)

        t0 = time.time()
        start_tensioning()
        rtm_time = time.time() - t0

        lcd_putstr("{: >4d}".format(min(int((time.time() - TIMER) / 60), 9999)) + "m", 15, 1, 5)
        tension_info(None, 2)

        rt_str = f"{TENSION_COUNT}T/{CORR_COEF.value:.2f}/{RT_CC[0]:.2f}/{DEFAULT_LB:.1f}/{rtm_time:.1f}"
        lcd_putstr(rt_str, 0, 2, I2C_NUM_COLS)

        if button_list('BUTTON_UP'):
            time.sleep(5)

        lcd_putstr("Pres SET Stop RTM", 0, 2, I2C_NUM_COLS)

        if button_list('BUTTON_SETTING'):
            RT_MODE = 0
            beepbeep(0.1)
            lcd_putstr("RTM: Manual Stop", 0, 2, I2C_NUM_COLS)
        elif rtm_time >= 20:
            RT_MODE = 0
            beepbeep(0.1)
            lcd_putstr(f"RTM: Timeout {rtm_time}S", 0, 2, I2C_NUM_COLS)
        elif (tmp_TENSION_COUNT + 1) != TENSION_COUNT:
            RT_MODE = 0
            beepbeep(0.1)
            lcd_putstr(ERR_MSG[1], 0, 2, I2C_NUM_COLS)

        if RT_MODE != 0:
            RT_LOG_ROTATE_FILE = os.path.join(MAIN_PATH, 'rt_logs.1.txt')

            with open(RT_LOG_FILE, 'a') as file:
                file.write("[{}]{}\n".format(time.strftime("%Y-%m-%d %H:%M:%S"), f"[{get_cpu_temp():.1f}C] {RT_MODE}/{rt_str}"))

            if RT_MODE % 1000 == 0:
                if os.path.isfile(RT_LOG_FILE):
                    os.rename(RT_LOG_FILE, RT_LOG_ROTATE_FILE)

            RT_MODE = RT_MODE + 1

        else:
            lcd_putstr("{: >4d}".format(min(int((time.time() - TIMER) / 60), 9999)) + "m", 15, 1, 5)
            lcd_putstr("{: >5d}R".format(tmp_RT_MODE), 14, 3, 6)
            while True:
                if button_list('BUTTON_EXIT'):
                    break
                
                time.sleep(0.05)

            TIMER = 0
            CORR_COEF.value = RT_CC[1]
            lcd_putstr("     ", 15, 1, 5)
            lcd_putstr("Ready", 0, 2, I2C_NUM_COLS)
            beepbeep(0.1)

    except Exception as e:
        handle_error(e, "rt_mode()")

# Check if any switch is stuck 檢查是否有按鍵卡住
def check_sw():
    check_count = 0
    while check_count < 3:
        for key in BUTTON_LIST:
            if button_list(key):
                return key

        check_count += 1
        time.sleep(0.5)

    return False

# Second core 第二核心
def tension_monitoring(HX711, TENSION_MON, MOTOR_STP, IS_TENSIONING, HX711_CAL, CORR_COEF, LB_CONV_G, RUNNING):
    try:
        # HX711 zeroing 歸零 HX711
        v0_arr = []
        t0 = time.time()
        while True:
            #val = float(hx.weight(1))
            val = int(hx.read(Options(1, ReadType.Median)))
            if val:
                v0_arr.append(val)
                if (time.time() - t0) > 1.0:  # 1000ms
                    v0_arr = sorted(v0_arr)
                    rate = len(v0_arr)
                    HX711["HX711_V0"] = v0_arr[int(len(v0_arr) / 2)]
                    HX711["DIFF"] = v0_arr[-1] - v0_arr[0]
                    HX711["RATE"] = rate
                    HX711["CP_HZ"] = round(1 / rate, 3) if rate != 0 else 0
                    HX711["V0"] = v0_arr
                    break
        
        cp_hz = HX711["CP_HZ"]
        last_tension = 0
        HX711["ANOM_COUNT"] = 0
        HX711["SAMPLE_COUNT"] = 0
        while True:
            # Tension monitoring 張力監控
            val = int(hx.read(Options(1, ReadType.Median)))

            if val:
                tension = int((val - HX711["HX711_V0"]) / 100 * (HX711_CAL.value / 20))
                HX711["HX711_VAL"] = val
                diff_tension  = abs(last_tension - tension)
                if (IS_TENSIONING.value == 0 and diff_tension < 100) or \
                   (IS_TENSIONING.value == 1 and diff_tension < 2000):
                    TENSION_MON.value = tension
                    if IS_TENSIONING.value == 1:
                        if LB_CONV_G.value < (tension * CORR_COEF.value):
                            MOTOR_STP.value = 1
                else:
                    HX711["ANOM_COUNT"] = HX711["ANOM_COUNT"] + 1
                
                last_tension = tension
                HX711["SAMPLE_COUNT"] = HX711["SAMPLE_COUNT"] + 1
                
            time.sleep(cp_hz)

    except Exception as e:
        handle_error(e, "tension_monitoring()")
        
# Third core 第三核心
def button_detection(BUTTON_LIST, RUNNING):
    try:
        sys_reboot = 0
        while True:
            # Button detection 按鍵偵測
            for key in list(BUTTON_LIST.keys()):
                pin = BUTTON_PINS[key]
                if GPIO.input(pin) == BUTTON_MODE["PRESSED_STATE"]:
                    BUTTON_LIST[key] = time.time()
                #    time.sleep(0.005)
                elif BUTTON_LIST[key]:
                    if (time.time() - BUTTON_LIST[key]) > (BUTTON_CLICK_MS / 1000.0):
                        BUTTON_LIST[key] = 0
            
            if GPIO.input(BUTTON_EXIT) == BUTTON_MODE["PRESSED_STATE"]:
                sys_reboot = sys_reboot + 1
                if(sys_reboot > 500):
                    shutdown_reboot(0)
                
            else:
                sys_reboot = 0
            
            time.sleep(0.01)

    except Exception as e:
        handle_error(e, "button_detection()")

# Button detection 按鈕偵測
def button_list(key):
    global BUTTON_LIST
    if BUTTON_LIST[key]:
        BUTTON_LIST[key] = 0
        return True
    else:
        return False

# Start increasing tension 開始增加張力
def start_tensioning():
    try:
        global TENSION_COUNT
        global KNOT_FLAG, RT_MODE, ERR_MSG, TIMER

        LCD.hide_cursor()
        lcd_putstr("Tensioning", 0, 2, I2C_NUM_COLS)
        lcd_putstr("     ", 15, 1, 5)

        if KNOT_FLAG == 0:
            LB_CONV_G.value = min(int((DEFAULT_LB * 453.59237) * ((PRE_STRECH + 100) / 100)), int(LB_MAX * 453.59237))
        else:
            LB_CONV_G.value = min(int((DEFAULT_LB * 453.59237) * ((KNOT + 100) / 100)), int(LB_MAX * 453.59237))

        timer_diff = time.time() - TIMER if TIMER else 0

        rel = forward(MOTOR_SPEED_V1 * (11 - MOTOR_SPEED_LV) / 2, MOTOR_MAX_STEPS, 1, 0)
        if not isinstance(rel, int):
            lcd_putstr(f"{rel}", 0, 2, I2C_NUM_COLS)
            logs_save(f"ts_err#0/{rel}", "start_tensioning()")
            return 0

        head_pos = rel
        IS_TENSIONING.value = 0
        abort_flag = 0
        count_add = 0
        count_sub = 0
        ts_phase = 0
        cc_count_add = 0
        cc_add_flag = 0
        log_lb_max = 0
        manual_flag = 1
        mt_ts = 0
        borken_flag = 0
        temp_LB_CONV_G = LB_CONV_G.value
        LED_YELLOW.on()
        t0 = time.time()
        while True:
            tension = TENSION_MON.value
            cp_phase = 0
            ft = 1

            # 第一階段：達到指定張力
            if ts_phase == 0:
                if abs(temp_LB_CONV_G - tension) < CP_FAST:
                    beepbeep(0.3)
                    log_lb_max = temp_LB_CONV_G
                    tension_info(log_lb_max, 3)
                    lcd_putstr("Target Tension", 0, 2, I2C_NUM_COLS)
                    lcd_putstr("S:   ", 15, 1, 5)
                    if KNOT_FLAG == 0:
                        temp_LB_CONV_G = int(DEFAULT_LB * 453.59237)
                    t0 = time.time()
                    ts_phase = 2 if PRE_STRECH == 0 else 1
                    manual_flag = 1 if CP_SW == 1 else 0

            elif ts_phase == 1:
                if abs(temp_LB_CONV_G - tension) < (CP_SLOW * 2) and (time.time() - t0) >= 1:
                    beepbeep(0.1)
                    t0 = time.time()
                    ts_phase = 2
                    manual_flag = 1 if CP_SW == 1 else 0

            # Constant-pull 增加
            if temp_LB_CONV_G > tension and (manual_flag or ts_phase == 0) and borken_flag == 0:
                diff_g = temp_LB_CONV_G - tension
                if diff_g > (453 * ((120 - DEFAULT_LB) / 100)):
                    cp_phase = 2
                    if not cc_add_flag:
                        cc_count_add = cc_count_add + 1000
                elif ts_phase == 2:
                    cc_add_flag = 1
                    if diff_g > 30:
                        cp_phase = 1     
                else:
                    cp_phase = 1
                    if not cc_add_flag:
                        cc_count_add += 1
                    if ts_phase == 0:
                        count_add = count_add + 1
                abort_flag = forward(MOTOR_SPEED_V2, ft, 0, 0)
                head_pos = head_pos + ft

            # Constant-pull 減少
            if (temp_LB_CONV_G + CP_SLOW * 1.5) < tension and (manual_flag or ts_phase == 0):
                diff_g = tension - temp_LB_CONV_G
                if diff_g < CP_FAST * (8 - (PRE_STRECH / 10)) and ts_phase == 2:
                    cp_phase = 0
                else:
                    cp_phase = 1
                
                if ts_phase == 0:
                    count_sub = count_sub + 1
                    
                abort_flag = backward(MOTOR_SPEED_V2, ft, 0)
                head_pos = head_pos - ft

            # 手動調整張力 UP
            if button_list('BUTTON_UP') and RT_MODE == 0 and (time.time() * 1000 - mt_ts) > 250:
                mt_ts = time.time() * 1000
                if LB_KG_SELECT == 2:
                    temp_lb = (int(temp_LB_CONV_G / 499) + 1) / 2
                    temp_LB_CONV_G = min(int(temp_lb * 1000), int(LB_MAX * 453.59237))
                else:
                    temp_lb = (int(temp_LB_CONV_G / 226) + 1) / 2
                    temp_LB_CONV_G = min(int(temp_lb * 453.59237), int(LB_MAX * 453.59237))
                lcd_putstr("{: >4.1f}".format(temp_LB_CONV_G / 453.592), 4, 0, 4)
                lcd_putstr("{: >4.1f}".format(temp_LB_CONV_G / 1000), 4, 1, 4)
                beepbeep(0.1)

            # 手動調整張力 DOWN
            if button_list('BUTTON_DOWN') and RT_MODE == 0 and (time.time() * 1000 - mt_ts) > 250:
                mt_ts = time.time() * 1000
                if LB_KG_SELECT == 2:
                    temp_lb = (int(temp_LB_CONV_G / 499) - 1) / 2
                    temp_LB_CONV_G = min(int(temp_lb * 1000), int(LB_MAX * 453.59237))
                else:
                    temp_lb = (int(temp_LB_CONV_G / 226) - 1) / 2
                    temp_LB_CONV_G = min(int(temp_lb * 453), int(LB_MAX * 453.59237))
                lcd_putstr("{: >4.1f}".format(temp_LB_CONV_G / 453.592), 4, 0, 4)
                lcd_putstr("{: >4.1f}".format(temp_LB_CONV_G / 1000), 4, 1, 4)
                beepbeep(0.1)

            # 切換自動/手動調整
            if button_list('BUTTON_SETTING') and RT_MODE == 0 and (time.time() * 1000 - mt_ts) > 500:
                mt_ts = time.time() * 1000
                manual_flag = 1 - manual_flag
                lcd_putstr(OPTIONS_DICT['MA_ARR'][manual_flag], 12, 3, 1)
                beepbeep(0.1)

            # 斷線檢測
            if tension < 2267:
                borken_flag = borken_flag + 1
                time.sleep(0.1)
                if borken_flag > 10:
                    lcd_putstr("Resetting...", 0, 2, I2C_NUM_COLS)
                    head_reset(None)
                    lcd_putstr("String Broken?", 0, 2, I2C_NUM_COLS)
                    MOTOR_STP.value = 0
                    RT_MODE = 0
                    logs_save("ts_err#3", "start_tensioning()")
                    return 0
            else:
                borken_flag = 0

            # 結束條件：按鈕觸發或自動退出
            button_exit_pressed = button_list('BUTTON_EXIT')
            rt_mode_time = time.time() - t0
            rt_mode_pressed = (ts_phase == 2 and rt_mode_time >= 1 and RT_MODE != 0)
            if button_exit_pressed or rt_mode_pressed:
                # 自我修正參數
                if CORR_COEF_AUTO:
                    if cc_count_add >= 1000 and CORR_COEF.value >= 1.1:
                        CORR_COEF.value = CORR_COEF.value - 0.05
                    elif cc_count_add > 20:
                        CORR_COEF.value = CORR_COEF.value - 0.01
                    elif cc_count_add == 0 and CORR_COEF.value <= 1.0:
                        CORR_COEF.value = 0.03 + CORR_COEF.value
                    elif cc_count_add < 10:
                        CORR_COEF.value = CORR_COEF.value + 0.01
                    CORR_COEF.value = max(0.95, min(CORR_COEF.value, 1.2))

                log_s = time.time() - t0
                lcd_putstr("Resetting...", 0, 2, I2C_NUM_COLS)
                lcd_putstr("{: >4.1f}".format(DEFAULT_LB), 4, 0, 4)
                lcd_putstr("{: >4.1f}".format(DEFAULT_LB * 0.45359237), 4, 1, 4)
                head_reset(head_pos)
                lcd_putstr("Ready", 0, 2, I2C_NUM_COLS)
                lcd_putstr("     ", 15, 1, 5)
                MOTOR_STP.value = 0

                if ts_phase == 2:
                    TENSION_COUNT = TENSION_COUNT + 1
                    if KNOT_FLAG:
                        KNOT_FLAG = 0
                        lcd_putstr(OPTIONS_DICT['PSKT_ARR'][KNOT_FLAG], 14, 0, 2)
                        lcd_putstr("{: >2d}".format(PRE_STRECH), 17, 0, 2)
                    if TENSION_COUNT % LOG_MAX == 0:
                        logs_cleanup()
                    config_save()
                else:
                    logs_save(f"ts_err#2/{int(button_exit_pressed)}/{int(rt_mode_pressed)}/{ts_phase}/{rt_mode_time}/{RT_MODE}", "start_tensioning()")
                return 0

            if abort_flag == 1:
                logs_save("ts_err#1", "start_tensioning()")
                return 0

            # 顯示張力資訊（慢速 or 快速恆拉）
            if cp_phase == 0:
                tension_info([tension, temp_LB_CONV_G], 1)
                if ts_phase == 2:
                    lcd_putstr("{: >3d}".format(min(int(time.time()-t0), 999)), 17, 1, 3)
                else:
                    lcd_putstr("   ", 17, 1, 3)
            elif cp_phase == 1:
                delay_us(6000)
                
    except Exception as e:
        handle_error(e, "start_tensioning()")

# Main screen 主畫面
def setting_ts():
    try:
        global DEFAULT_LB, PRE_STRECH, CURSOR_XY_TS_TEMP, KNOT_FLAG, KNOT

        if KNOT_FLAG == 1:
            ps_kt_show = DEFAULT_LB * ((KNOT + 100) / 100)
        else:
            ps_kt_show = DEFAULT_LB * ((PRE_STRECH + 100) / 100)

        lcd_putstr("{: >4.1f}".format(ps_kt_show), 9, 0, 4)
        lcd_putstr("{: >4.1f}".format(ps_kt_show * 0.45359237), 9, 1, 4)
        last_set_time = time.time() * 1000  # 使用毫秒
        set_count = len(TS_ARR)
        i = CURSOR_XY_TS_TEMP
        cursor_xy = TS_ARR[i][0], TS_ARR[i][1]
        LCD.move_to(TS_ARR[i][0], TS_ARR[i][1])
        LCD.blink_cursor_on()
        ps_kt_tmp = PRE_STRECH if KNOT_FLAG == 0 else KNOT
        beepbeep(0.04)

        while True:
            now_ms = time.time() * 1000

            if GPIO.input(BUTTON_UP) == BUTTON_MODE["PRESSED_STATE"] or GPIO.input(BUTTON_DOWN) == BUTTON_MODE["PRESSED_STATE"]:
                LCD.show_cursor()
                LCD.blink_cursor_on()
                kg = round(DEFAULT_LB * 0.45359237, 1)

                # 各種欄位判斷
                if cursor_xy == (4, 0):  # LB 十位
                    DEFAULT_LB += 10 if GPIO.input(BUTTON_UP) == BUTTON_MODE["PRESSED_STATE"] else -10
                elif cursor_xy == (5, 0):  # LB 個位
                    DEFAULT_LB += 1 if GPIO.input(BUTTON_UP) == BUTTON_MODE["PRESSED_STATE"] else -1
                elif cursor_xy == (7, 0):  # LB 小數
                    DEFAULT_LB += 0.1 if GPIO.input(BUTTON_UP) == BUTTON_MODE["PRESSED_STATE"] else -0.1
                elif cursor_xy == (4, 1):  # KG 十位
                    kg += 10 if GPIO.input(BUTTON_UP) == BUTTON_MODE["PRESSED_STATE"] else -10
                    DEFAULT_LB = round(kg * 2.20462262, 1)
                elif cursor_xy == (5, 1):  # KG 個位
                    kg += 1 if GPIO.input(BUTTON_UP) == BUTTON_MODE["PRESSED_STATE"] else -1
                    DEFAULT_LB = round(kg * 2.20462262, 1)
                elif cursor_xy == (7, 1):  # KG 小數
                    kg += 0.1 if GPIO.input(BUTTON_UP) == BUTTON_MODE["PRESSED_STATE"] else -0.1
                    DEFAULT_LB = round(kg * 2.20462262, 1)
                elif cursor_xy == (17, 0):  # 預拉或打結 十位
                    ps_kt_tmp += 10 if GPIO.input(BUTTON_UP) == BUTTON_MODE["PRESSED_STATE"] else -10
                elif cursor_xy == (18, 0):  # 預拉或打結 個位
                    ps_kt_tmp += 5 if GPIO.input(BUTTON_UP) == BUTTON_MODE["PRESSED_STATE"] else -5
                elif cursor_xy == (14, 0):  # 切換預拉/打結
                    if GPIO.input(BUTTON_UP) == BUTTON_MODE["PRESSED_STATE"] or GPIO.input(BUTTON_DOWN) == BUTTON_MODE["PRESSED_STATE"]:
                        KNOT_FLAG = 0 if KNOT_FLAG == 1 else 1
                        ps_kt_tmp = PRE_STRECH if KNOT_FLAG == 0 else KNOT
                        lcd_putstr(OPTIONS_DICT['PSKT_ARR'][KNOT_FLAG], 14, 0, 2)
                        lcd_putstr("{: >2d}".format(ps_kt_tmp), 17, 0, 2)

                DEFAULT_LB = max(LB_MIN, min(LB_MAX, DEFAULT_LB))

                if KNOT_FLAG == 1:
                    KNOT = max(KNOT_RANG[0], min(KNOT_RANG[1], ps_kt_tmp))
                    ps_kt_show = DEFAULT_LB * ((KNOT + 100) / 100)
                    lcd_putstr("{: >2d}".format(KNOT), 17, 0, 2)
                else:
                    PRE_STRECH = max(0, min(PS_MAX, ps_kt_tmp))
                    ps_kt_show = DEFAULT_LB * ((PRE_STRECH + 100) / 100)
                    lcd_putstr("{: >2d}".format(PRE_STRECH), 17, 0, 2)

                LCD.blink_cursor_off()
                LCD.hide_cursor()
                lcd_putstr("{: >4.1f}".format(min(ps_kt_show, LB_MAX)), 9, 0, 4)
                lcd_putstr("{: >4.1f}".format(min(ps_kt_show * 0.45359237, LB_MAX * 0.45359237)), 9, 1, 4)
                lcd_putstr("{:.1f}".format(DEFAULT_LB), 4, 0, 4)
                lcd_putstr("{: >4.1f}".format(DEFAULT_LB * 0.45359237), 4, 1, 4)
                LCD.move_to(TS_ARR[i][0],TS_ARR[i][1])
                LCD.show_cursor()
                LCD.blink_cursor_on()
                last_set_time = time.time() * 1000
                beepbeep(0.1)
                time.sleep(0.1)

            # 左右移動游標
            if GPIO.input(BUTTON_RIGHT) == BUTTON_MODE["PRESSED_STATE"] or GPIO.input(BUTTON_LEFT) == BUTTON_MODE["PRESSED_STATE"]:
                LCD.hide_cursor()
                LCD.blink_cursor_on()
                if GPIO.input(BUTTON_RIGHT) == BUTTON_MODE["PRESSED_STATE"]:
                    i = i + 1 if (i + 1) < set_count else 0
                else:
                    i = i - 1 if (i - 1) >= 0 else set_count - 1

                CURSOR_XY_TS_TEMP = i
                cursor_xy = TS_ARR[i][0], TS_ARR[i][1]
                LCD.move_to(TS_ARR[i][0], TS_ARR[i][1])
                last_set_time = time.time() * 1000
                beepbeep(0.1)
                time.sleep(0.1)

            # 離開設定
            if button_list('BUTTON_EXIT') or ((now_ms - last_set_time) > 1800):
                config_save()
                LCD.blink_cursor_off()
                LCD.hide_cursor()
                time.sleep(0.1)
                beepbeep(0.04)
                return 0

    except Exception as e:
        handle_error(e, "setting_ts()")

def ssh_dev_pwd():
    try:
        with open(SSH_SH_FILE, "r") as f:
            return f.read().strip()
    except Exception as e:
        return "UNKNOWN"

def fetch_list():
    try:
        response = requests.get(LIST_URL, timeout=5)
        response.raise_for_status()
        fw_list = response.json()
    except Exception as e:
        fw_list = "List fetch failed"
    return fw_list

def compute_sha1(filepath):
    sha1 = hashlib.sha1()
    with open(filepath, 'rb') as f:
        while chunk := f.read(8192):
            sha1.update(chunk)
    return sha1.hexdigest()

def download_firmware(name, date):
    filename = f"{name}_{date}.tar.gz"
    filepath = os.path.join("/tmp", filename)
    url = f"{DOWNLOAD_BASE_URL}{filename}"
    
    response = requests.get(url, stream=True)
    response.raise_for_status()

    with open(filepath, "wb") as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)

    return filepath

def extract_tarball(tar_file, dest_dir):
    os.makedirs(dest_dir, exist_ok=True)
    with tarfile.open(tar_file, "r:gz") as tar:
        tar.extractall(path=dest_dir)

def ota_update():
    
    lcd_putstr("== OTA FW Install ==", 0, 0, I2C_NUM_COLS)
    lcd_putstr("Checking network... ", 0, 1, I2C_NUM_COLS)
    lcd_putstr("                    ", 0, 2, I2C_NUM_COLS)
    lcd_putstr("                    ", 0, 3, I2C_NUM_COLS)
    
    if wifi_ip() == "N/A":
        wifi_config(1)
        return
    
    lcd_putstr("           Press SET", 0, 3, I2C_NUM_COLS)
    
    fw_list = fetch_list()
    
    if isinstance(fw_list, list) and len(fw_list) > 0:
        lcd_putstr(f"{fw_list[0]['name']}", 0, 1, I2C_NUM_COLS)
        lcd_putstr(f"{fw_list[0]['date']}", 0, 2, I2C_NUM_COLS)
        lcd_putstr(f"[1/{len(fw_list)}]", 0, 3, 9)
        change_flag = False
        i = 0
        while True:
            if button_list('BUTTON_RIGHT'):
                i = min(i + 1, len(fw_list) - 1)
                change_flag = True
                
            elif button_list('BUTTON_LEFT'):
                i = max(i - 1, 0)
                change_flag = True
            
            elif button_list('BUTTON_SETTING'):
                beepbeep(0.1)
                lcd_putstr("   Confirm Update?   ", 0, 1, I2C_NUM_COLS)
                lcd_putstr(f"{fw_list[i]['name']}", 0, 2, I2C_NUM_COLS)
                lcd_putstr(" Press UP to update ", 0, 3, I2C_NUM_COLS)
                while True:
                    if button_list('BUTTON_UP'):
                        beepbeep(0.1)
                        lcd_putstr("Downloading...", 0, 1, I2C_NUM_COLS)
                        lcd_putstr("", 0, 2, I2C_NUM_COLS)
                        filename = download_firmware(fw_list[i]['name'], fw_list[i]['date'])
                        lcd_putstr("Checksum check...", 0, 1, I2C_NUM_COLS)
                        actual_sha1 = compute_sha1(filename)
                        
                        if actual_sha1 != fw_list[i]['sha1']:
                            os.remove(filename)
                            lcd_putstr("Checksum error detec", 0, 1, I2C_NUM_COLS)
                            lcd_putstr("ted. Please retry.", 0, 2, I2C_NUM_COLS)
                            lcd_putstr("          Press EXIT", 0, 3, I2C_NUM_COLS)
                            while True:
                                if button_list('BUTTON_EXIT'):
                                    beepbeep(0.1)
                                    return False
                                time.sleep(0.05)
                        
                        lcd_putstr("Installing...", 0, 1, I2C_NUM_COLS)
                        extract_tarball(filename, DEST_DIR)
                        lcd_putstr(f"{fw_list[i]['name']}", 0, 1, I2C_NUM_COLS)
                        lcd_putstr("Update complete!", 0, 2, I2C_NUM_COLS)
                        lcd_putstr("Press EXIT to Reboot", 0, 3, I2C_NUM_COLS)
                        while True:
                            if button_list('BUTTON_EXIT'):
                                beepbeep(0.1)
                                shutdown_reboot(1)
                            time.sleep(0.05)
                        
                    elif button_list('BUTTON_EXIT'):
                        beepbeep(0.1)
                        return
                    time.sleep(0.05)
                    
            elif button_list('BUTTON_EXIT'):
                return
                
            if change_flag == True:
                lcd_putstr(f"{fw_list[i]['name']}", 0, 1, I2C_NUM_COLS)
                lcd_putstr(f"{fw_list[i]['date']}", 0, 2, I2C_NUM_COLS)
                lcd_putstr(f"[{i + 1}/{len(fw_list)}]", 0, 3, 9)
                change_flag = False
                beepbeep(0.1)
                
            time.sleep(0.1)
    else:
        lcd_putstr("No firmware found!  ", 0, 1, I2C_NUM_COLS)
        lcd_putstr("          Press EXIT", 0, 3, I2C_NUM_COLS)
        while True:
            if button_list('BUTTON_SETTING') or  button_list('BUTTON_EXIT'):
                return
            time.sleep(0.05)
    
def wifi_ip():
    global WIFI_IP
    WIFI_IP = "N/A"
    try:
        result = subprocess.run(
            ["nmcli", "-t", "-f", "DEVICE,STATE", "dev"],
            capture_output=True, text=True
        )
        time.sleep(1)
        ip = "N/A"
        if "wlan0:connected" in result.stdout:
            result = subprocess.run(
                ["nmcli", "-t", "-f", "IP4.ADDRESS", "device", "show", "wlan0"],
                capture_output=True, text=True
            )
            for line in result.stdout.splitlines():
                line = line.strip()
                match = re.search(r'(\d+\.\d+\.\d+\.\d+)', line)
                if match:
                    ip = match.group(1)
        
        WIFI_IP = ip
        return ip
            
    except Exception as e:
        handle_error(e, "wifi_ip()")

def wifi_config(flag):
    global WIFI_IP
    lcd_putstr(" == Wi-Fi Config == ", 0, 0, I2C_NUM_COLS)
    lcd_putstr("SSID:               ", 0, 1, I2C_NUM_COLS)
    lcd_putstr("PSWD:               ", 0, 2, I2C_NUM_COLS)  

    if check_wifi_status() == False:
        lcd_putstr("Turn On Wi-Fi...", 0, 3, I2C_NUM_COLS)
        change_wifi("up")
        time.sleep(3)
    
    lcd_putstr("          [OK][EXIT]", 0, 3, I2C_NUM_COLS)
    
    beepbeep(0.1) 
    WIFI_IP = wifi_ip()

    WIFI_CONFIG = {
        "ssid":[6],
        "pswd":[6,7,8,9,10,11,12,13,14,15,16,17,18,19],
        "type":[11,15]
    }
    
    char_arr = {
        0:'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ9876543210~!@#$%^&*()-=[]\\;\',./_+{}|:"<>?'
    }
    char_x = 0
    char_type = [0,26,52,62]
    wifi_list = scan_wifi()
    password = {
        0: None,
        1: None,
        2: None,
        3: None,
        4: None,
        5: None,
        6: None,
        7: None,
        8: None,
        9: None,
        10: None,
        11: None
        }
    
    con_ssid = None
    
    try:
        con_ssid = subprocess.check_output(["/usr/sbin/iwgetid", "-r"], encoding='utf-8').strip()
    except subprocess.CalledProcessError:
        con_ssid = None
    
    try:
        # 檢查檔案是否存在
        if not os.path.exists(WIFI_CFG_FILE):
            with open(WIFI_CFG_FILE, "w") as f:
                f.write("zerobeth\n")
                f.write("zerobeth\n")
        
        # 讀取設定檔
        with open(WIFI_CFG_FILE, "r") as f:
            lines = f.readlines()
            r_ssid = lines[0].strip() if len(lines) > 0 else ""
            r_password = lines[1].strip() if len(lines) > 1 else ""
        
        if con_ssid == None:
            if r_ssid == "zerobeth" and 'zerobeth' not in wifi_list:
                wifi_list.insert(0, 'zerobeth')
        
        # 寫入 ssid
        if r_ssid in wifi_list:
            x_ssid = wifi_list.index(r_ssid)
        #    if r_password == "zerobeth":
        #        lcd_putstr(f"{r_password}", 6, 2, len(r_password))
        #    else:
        #        lcd_putstr(f"{'*' * len(r_password)}", 6, 2, len(r_password))
            lcd_putstr(f"{r_password}", 6, 2, len(r_password))
                
            # 寫入 password
            for i, c in enumerate(r_password):
                if i >= len(password):
                    break
                try:
                    index = char_arr[0].index(c)
                    password[i] = index
                except ValueError:
                    password[i] = None
        else:
            x_ssid = 0
        
        x_pswd = 0
        x_type = 0
        y_idx = 1
        type_flag = 0
        locked_pswd = False
        flag_pswd = True
        press_flag = False
        
        # SSID default
        if len(wifi_list) > 0:
            index = x_ssid if x_ssid < len(wifi_list) else 0
            lcd_putstr(wifi_list[index], 6, 1, len(wifi_list[x_ssid]))

        LCD.move_to(WIFI_CONFIG['ssid'][0], 1)
        LCD.show_cursor() 
        while True:
            if button_list('BUTTON_UP'):
                press_flag = True
                if y_idx == 2:
                    if locked_pswd == False:
                        y_idx = 1
                        LCD.move_to(6, 1)
                    else:
                        if password[x_pswd] != None and flag_pswd == True:
                            char_x = max(password[x_pswd], 0)
                        
                        elif password[x_pswd] == None:
                            char_x = 0
                        
                        if char_x - 1 < 0:
                            char_x = len(char_arr[0]) - 1
                        else:
                            char_x = char_x - 1
                        
                        lcd_putstr(char_arr[0][char_x], WIFI_CONFIG['pswd'][x_pswd], 2, 1)
                        LCD.move_to(WIFI_CONFIG['pswd'][x_pswd], 2)
                        password[x_pswd] = char_x
                        flag_pswd = False
                
                elif y_idx == 3:
                    y_idx = 2
                    LCD.move_to(WIFI_CONFIG['pswd'][x_pswd], 2)
                
            elif button_list('BUTTON_DOWN'):
                press_flag = True
                if y_idx == 1:
                    y_idx = 2
                    LCD.move_to(WIFI_CONFIG['pswd'][x_pswd], 2)
                 
                elif y_idx == 2:
                    if locked_pswd == False:
                        y_idx = 3
                        LCD.move_to(WIFI_CONFIG['type'][0], 3)
                    else:
                        if password[x_pswd] != None and flag_pswd == True:
                            char_x = min(password[x_pswd], (len(char_arr[0]) - 1))
                        
                        if password[x_pswd] == None:
                            char_x = 0
                        else:
                            if (char_x + 1) > (len(char_arr[0]) - 1):
                                char_x = 0
                            else:
                                char_x = char_x + 1
                        
                        lcd_putstr(char_arr[0][char_x], WIFI_CONFIG['pswd'][x_pswd], 2, 1)
                        LCD.move_to(WIFI_CONFIG['pswd'][x_pswd], 2)
                        password[x_pswd] = char_x
                        flag_pswd = False
            
            elif button_list('BUTTON_LEFT'):
                press_flag = True
                if y_idx == 1:
                    x_ssid = max(x_ssid - 1, 0)
                    index = x_ssid if x_ssid < len(wifi_list) else 0
                    lcd_putstr(wifi_list[index], 6, 1, 14)
                    LCD.move_to(6, 1)
                    
                elif y_idx == 2:
                    if locked_pswd == False:
                        x_pswd = max(x_pswd - 1, 0)
                        LCD.move_to(WIFI_CONFIG['pswd'][x_pswd], 2)
                        flag_pswd = True 
                    
                elif y_idx == 3:
                    type_flag = 1 - type_flag
                    LCD.move_to(WIFI_CONFIG['type'][type_flag], 3)
            
            elif button_list('BUTTON_RIGHT'):
                press_flag = True
                if y_idx == 1:
                    x_ssid = min(x_ssid + 1, (len(wifi_list) - 1))
                    index = x_ssid if x_ssid < len(wifi_list) else 0
                    lcd_putstr(wifi_list[index], 6, 1, 14)
                    LCD.move_to(6, 1)
                    
                elif y_idx == 2:
                    if locked_pswd == False:
                        x_pswd = min(x_pswd + 1, 11)
                        LCD.move_to(WIFI_CONFIG['pswd'][x_pswd], 2)
                        flag_pswd = True
                    
                elif y_idx == 3:
                    type_flag = 1 - type_flag
                    LCD.move_to(WIFI_CONFIG['type'][type_flag], 3)
            
            elif button_list('BUTTON_SETTING'):
                press_flag = True
                if y_idx == 2:
                    if locked_pswd == False:
                        LCD.blink_cursor_on()
                        LCD.move_to(WIFI_CONFIG['pswd'][x_pswd], 2)
                        locked_pswd = True
                    else:
                        LCD.blink_cursor_off()
                        locked_pswd = False
                        
                elif y_idx == 3:
                    if type_flag == 0:
                        pwd = ''.join(
                            char_arr[0][password[i]] if password[i] is not None else ' '
                            for i in range(12)
                        ).strip()
                        if connect_to_wifi(wifi_list[x_ssid], pwd, flag):
                            return
                        
                    elif type_flag == 1:
                        return
            
            elif button_list('BUTTON_EXIT'):
                press_flag = True
                if y_idx == 2:
                    if locked_pswd == True:
                        char_x = password[x_pswd]
                        if char_x == None or char_x >= 62:
                            char_x = 0
                        else:
                            for i in range(len(char_type) - 1):
                                if char_type[i] <= char_x < char_type[i+1]:
                                    char_x = char_type[i+1]
                                    break
                        
                        lcd_putstr(char_arr[0][char_x], WIFI_CONFIG['pswd'][x_pswd], 2, 1)
                        LCD.move_to(WIFI_CONFIG['pswd'][x_pswd], 2)
                        password[x_pswd] = char_x
                    else:
                        lcd_putstr(" ", WIFI_CONFIG['pswd'][x_pswd], 2, 1)
                        LCD.move_to(WIFI_CONFIG['pswd'][x_pswd], 2)
                        password[x_pswd] = None
                    
                elif y_idx == 3:
                    return
                
            if press_flag == True:
                beepbeep(0.1)
                press_flag = False
            
            time.sleep(0.2)
            
    except Exception as e:
        handle_error(e, "wifi_config()")

def connect_to_wifi(ssid, password, flag):
    lcd_msg_len = 10
    try:
        with open(WIFI_SH_FILE, "w") as f:
            f.write("#!/bin/bash\n")
            f.write("nmcli device disconnect wlan0\n")
            f.write(f"nmcli connection delete '{ssid}' 2>/dev/null || true\n")
            f.write(f"nmcli device wifi connect '{ssid}' password '{password}'\n")
            
        with open(WIFI_CFG_FILE, "w") as f:
            f.write(f"{ssid}\n{password}\n")

        os.chmod(WIFI_SH_FILE, 0o755)
        lcd_putstr("Conneting", 0, 3, lcd_msg_len)
        result = subprocess.run(["sudo", WIFI_SH_FILE], check=True)
        ip = wifi_ip()
        if ip != "N/A":
            lcd_putstr("Success!", 0, 3, lcd_msg_len)
            logs_save(f"Success {ssid}", "connect_to_wifi()")
            
            if flag == 1:
                ota_update()
                return True
                
            elif flag == 0:
                time.sleep(2)
                return True
        else:
            lcd_putstr("Fail!#1", 0, 3, lcd_msg_len)
            logs_save(f"Fail!#1", "connect_to_wifi()")
        #    return False

    except subprocess.CalledProcessError as e:
        lcd_putstr("Fail!#0", 0, 3, lcd_msg_len)
        logs_save(f"Fail!#0", "connect_to_wifi()")

def scan_wifi():
    wifi_set = set()
    wifi_list = []

    try:
        result = subprocess.check_output(["sudo", "iwlist", "wlan0", "scan"], stderr=subprocess.DEVNULL).decode()
    except subprocess.CalledProcessError:
        return []

    cells = result.split("Cell ")
    for cell in cells[1:]:
        ssid_match = re.search(r'ESSID:"(.*?)"', cell)
        if ssid_match:
            ssid = ssid_match.group(1)
            if ssid and ssid not in wifi_set:
                wifi_set.add(ssid)
                wifi_list.append(ssid)

    return wifi_list

MENU_NOR_LIST_ARR = {
    "1-1":["Speed Level:"        ,"L1=Slow L9=Fast",[18],'MOTOR_SPEED_LV'],
    "1-2":["Constant-Pull:"      ,"ON or OFF",[17],'CP_SW'],
    "1-3":["Buzzer:"             ,"ON or OFF",[17],'BZ_SW'],
    "1-4":["Tension Unit:"       ,"LB KG or Both",[16],'LB_KG_SELECT'],
    "2-1":["HX Calibration:"     ,"HX711 Scale Factor",[15,16,18,19,20],'HX711_CAL'],
    "2-2":["Wi-Fi Config:    SET","Set Wi-Fi Network",[18],''],
    "3-1":["IP:"                 ,"Wi-Fi IP Address",[None],''],
    "3-2":["OTA Update:"         ,"",[15],''],
    "3-3":["Version:"            ,"",[None],'VERDATE'],
    "4-1":["SYS:  Rboot Shutdown","",[6],'']
,
}

MENU_ENG_LIST_ARR = {
    "9-1":["Load Cell:"          ,"Set Load Cell Rating",[16],'LOAD_CELL_KG'],
    "9-2":["Max Tension:"        ,"35LB to 70LB",[16],'LB_MAX'],
    "9-3":["Slide Table: "       ,"SGX 1610 or 1605",[16],'SLIDE_TABLE'],
    "9-4":["Boot Count:"         ,"Power On Counter",[None],'BOOT_COUNT'],
    "9-5":["Rate:"               ,"HX711 Rate (Hz)",[None],'HX711'],
    "9-6":["Drift:"              ,"HX711 Drift (g/s)",[None],'HX711'],
    "9-7":["Stability:"          ,"HX711 Stability",[None],'HX711'],
    "9-8":["SSH PWD:"            ,"For development use",[None],'']
,
}

def process_setting_item(item):
    global MOTOR_SPEED_LV, CP_SW, BZ_SW, LB_KG_SELECT, LB_MAX, LOAD_CELL_KG, HX711_V0, WIFI_IP, ABORT_GRAM, SLIDE_TABLE

    try:
        LCD.move_to(MENU_LIST_ARR[item][2][0], 1)
        LCD.blink_cursor_on()
        cursor_x = 0
        change_flag = False
        move_flag = False
        shift_flag = 0
        temp_LOAD_CELL_KG = LOAD_CELL_KG
        beepbeep(0.2)
        while True:
            if item == "1-1":
                if button_list('BUTTON_UP'):
                    MOTOR_SPEED_LV = min(MOTOR_SPEED_LV + 1, 9)
                    val_item = f"{MOTOR_SPEED_LV}"
                    change_flag = True
                    
                elif button_list('BUTTON_DOWN'):
                    MOTOR_SPEED_LV = max(MOTOR_SPEED_LV - 1, 1)
                    val_item = f"{MOTOR_SPEED_LV}"
                    change_flag = True
                    
            elif item == "1-2":
                if button_list('BUTTON_UP') or button_list('BUTTON_DOWN'):
                    CP_SW = 1 - CP_SW
                    val_item = OPTIONS_DICT['ONOFF_ARR'][CP_SW]
                    change_flag = True
                    
            elif item == "1-3":
                if button_list('BUTTON_UP') or button_list('BUTTON_DOWN'):
                    BZ_SW = 1 - BZ_SW
                    val_item = OPTIONS_DICT['ONOFF_ARR'][BZ_SW]
                    change_flag = True
                    
            elif item == "1-4":
                if button_list('BUTTON_UP'):
                    LB_KG_SELECT = (LB_KG_SELECT + 1) % 3
                    val_item = OPTIONS_DICT['UNIT_ARR'][LB_KG_SELECT]
                    lb_kg_select()
                    change_flag = True
                    
                elif button_list('BUTTON_DOWN'):
                    LB_KG_SELECT = (LB_KG_SELECT - 1) % 3
                    val_item = OPTIONS_DICT['UNIT_ARR'][LB_KG_SELECT]
                    lb_kg_select()
                    change_flag = True
                    
            elif item == "2-1":
                if button_list('BUTTON_LEFT'):
                    cursor_x = (cursor_x - 1) % 4
                    shift_flag = int(cursor_x >= 2)
                    move_flag = True
                
                elif button_list('BUTTON_RIGHT'):
                    cursor_x = (cursor_x + 1) % 4
                    shift_flag = int(cursor_x >= 2)
                    move_flag = True
                
                elif cursor_x == 0:
                    if button_list('BUTTON_UP'):
                        HX711_CAL.value = HX711_CAL.value + 10
                        change_flag = True
                        move_flag = True
                    elif button_list('BUTTON_DOWN'):
                        HX711_CAL.value = HX711_CAL.value - 10
                        change_flag = True
                        move_flag = True
                        
                elif cursor_x == 1:
                    if button_list('BUTTON_UP'):
                        HX711_CAL.value = HX711_CAL.value + 1
                        change_flag = True
                    elif button_list('BUTTON_DOWN'):
                        HX711_CAL.value = HX711_CAL.value - 1
                        change_flag = True
                        
                elif cursor_x == 2:
                    if button_list('BUTTON_UP'):
                        HX711_CAL.value = HX711_CAL.value + 0.1
                        change_flag = True
                    elif button_list('BUTTON_DOWN'):
                        HX711_CAL.value = HX711_CAL.value - 0.1
                        change_flag = True
                        
                elif cursor_x == 3:
                    if button_list('BUTTON_UP'):
                        HX711_CAL.value = HX711_CAL.value + 0.01
                        change_flag = True
                    elif button_list('BUTTON_DOWN'):
                        HX711_CAL.value = HX711_CAL.value - 0.01
                        change_flag = True
                
                if change_flag:
                    HX711_CAL.value = max(LOAD_CELL_KG - 10, min(LOAD_CELL_KG + 10, HX711_CAL.value))
                    HX711_V0 = HX711["HX711_V0"]
                    val_item = f"{HX711_CAL.value:.2f}"
            
            elif item == "9-1":
                if button_list('BUTTON_UP') or button_list('BUTTON_DOWN'):
                    LOAD_CELL_KG = 70 - LOAD_CELL_KG
                    
                    # 如設定 LOAD_CELL 需重新校正
                    if temp_LOAD_CELL_KG != LOAD_CELL_KG:
                        if LOAD_CELL_KG == 20:
                            HX711_CAL.value = 20
                        elif LOAD_CELL_KG == 50:
                            HX711_CAL.value = 50
                        HX711_V0 = 0
                        
                    temp_LOAD_CELL_KG = LOAD_CELL_KG
                    val_item = f"{LOAD_CELL_KG}KG"
                    change_flag = True
            
            elif item == "9-2":
                if button_list('BUTTON_LEFT'):
                    cursor_x = (cursor_x - 1) % 2
                    shift_flag = int(cursor_x >= 2)
                    move_flag = True
                
                elif button_list('BUTTON_RIGHT'):
                    cursor_x = (cursor_x + 1) % 2
                    shift_flag = int(cursor_x >= 2)
                    move_flag = True

                elif cursor_x == 0:
                    if button_list('BUTTON_UP'):
                        LB_MAX = LB_MAX + 10
                        change_flag = True
                    elif button_list('BUTTON_DOWN'):
                        LB_MAX = LB_MAX - 10
                        change_flag = True
                        
                elif cursor_x == 1:
                    if button_list('BUTTON_UP'):
                        LB_MAX = LB_MAX + 1
                        change_flag = True
                    elif button_list('BUTTON_DOWN'):
                        LB_MAX = LB_MAX - 1
                        change_flag = True
                
                if change_flag:
                    if LOAD_CELL_KG == 20:
                        LB_MAX = max(35, min(50, LB_MAX))
                    elif LOAD_CELL_KG == 50:
                        LB_MAX = max(35, min(70, LB_MAX))
                    val_item = f"{LB_MAX}LB"
                    ABORT_GRAM = (LB_MAX + 5) * 454

            elif item == "9-3":
                if button_list('BUTTON_UP') or button_list('BUTTON_DOWN'):
                    if SLIDE_TABLE == 1610:
                        SLIDE_TABLE = 1605
                    elif SLIDE_TABLE == 1605:
                        SLIDE_TABLE = 1610
                        
                    val_item = f"{SLIDE_TABLE}"
                    slide_table(SLIDE_TABLE)
                    change_flag = True
            
            elif item == "4-1":
                if button_list('BUTTON_LEFT') or button_list('BUTTON_RIGHT'):
                    cursor_x = (cursor_x - 1) % 2
                    shift_flag = 0 if cursor_x == 0 else 5
                    move_flag = True
                    
                elif cursor_x == 1 and button_list('BUTTON_UP'):
                    shutdown_reboot(0)
                    
                elif cursor_x == 0 and button_list('BUTTON_UP'):
                    shutdown_reboot(1)
            
            if button_list('BUTTON_EXIT'):
                LCD.blink_cursor_off()
                config_save()
                return
                
            if change_flag == True:
                lcd_putstr(f"{val_item}", (I2C_NUM_COLS - len(val_item)), 1, len(val_item))
                LCD.move_to(MENU_LIST_ARR[item][2][0] + cursor_x + shift_flag, 1)
                beepbeep(0.1)
                change_flag = False

            if move_flag:
                LCD.move_to(MENU_LIST_ARR[item][2][0] + cursor_x + shift_flag, 1)
                beepbeep(0.1)
                move_flag = False
                
            time.sleep(0.2)
        
    except Exception as e:
        handle_error(e, "process_setting_item()") 

# setting_interface 設定頁面
def setting_interface(flag):
    try:
        global MENU_TEMP, MENU_LIST_ARR, ENGINEER_MENU, WIFI_IP
    
        lcd_putstr(" ==== MENU     ==== ", 0, 0, I2C_NUM_COLS)
        lcd_putstr(f"[\x7FB N\x7E SET]  {TENSION_COUNT:>6}T", 0, 3, I2C_NUM_COLS)
        
        if ENGINEER_MENU >= 5:
            MENU_LIST_ARR = MENU_NOR_LIST_ARR | MENU_ENG_LIST_ARR
        else:
            MENU_LIST_ARR = MENU_NOR_LIST_ARR
        
        menu_len = len(MENU_LIST_ARR)
        
        if flag == 0:
            i = MENU_TEMP
        else:
            i= flag
        
        while True: 
            items = list(MENU_LIST_ARR.items())
            if i < len(items):
                key, val = items[i]
            else:
                key, val = items[0]
            
            lcd_putstr(f"{val[0]}", 0, 1, I2C_NUM_COLS)
            lcd_putstr(f"{val[1]}", 0, 2, I2C_NUM_COLS)
            lcd_putstr(f"{key}", 11, 0, 3)
            
            # 顯示 itme 數值
            val_item = ""
            if key == '1-1':
                val_item = f"L{globals()[MENU_LIST_ARR[key][3]]}"
            elif key == '1-2' or key == '1-3':
                val_item = f"{OPTIONS_DICT['ONOFF_ARR'][globals()[MENU_LIST_ARR[key][3]]]}"
            elif key == '1-4':
                val_item = f"{OPTIONS_DICT['UNIT_ARR'][globals()[MENU_LIST_ARR[key][3]]]}"
            elif key == '2-1':
                val_item = f"{globals()[MENU_LIST_ARR[key][3]].value:.2f}"
            elif key == '9-1':
                val_item = f"{globals()[MENU_LIST_ARR[key][3]]}KG"
            elif key == '9-2':
                val_item = f"{str(globals()[MENU_LIST_ARR[key][3]])}LB"
            elif key == '9-3':
                val_item = f"{str(globals()[MENU_LIST_ARR[key][3]])}"
            elif key == '9-4':
                val_item = f"{globals()[MENU_LIST_ARR[key][3]]}"
            elif key == '9-5':
                val_item = f"{HX711['RATE']}Hz"
            elif key == '9-6':
                val_item = f"{str(HX711['DIFF'] / 1000)[:3]}G"
            elif key == '9-7':
                val_item = f"{str(round(1 - ((HX711['ANOM_COUNT'] / HX711['SAMPLE_COUNT']) / 2), 4) * 100)[:5]}%"
            elif key == '3-1':
                val_item = f"{WIFI_IP}"
            elif key == '9-8':
                val_item = f"{ssh_dev_pwd()}"
            elif key == '4-1':
                val_item = ""
            elif key == '3-2':
                val_item = "Check"
                lcd_putstr("Online FW Update", 0, 2, I2C_NUM_COLS)
            elif key == '3-3':
                val_item = f"v{VERSION}"
                lcd_putstr(f"          {VERDATE}", 0, 2, I2C_NUM_COLS)
            
            lcd_putstr(f"{val_item}", (I2C_NUM_COLS - len(val_item)), 1, len(val_item))
            LCD.hide_cursor()
            
            while True:
                if button_list('BUTTON_RIGHT'):
                    i = min(i + 1, menu_len - 1)
                    MENU_TEMP = i
                    break
                    
                elif button_list('BUTTON_LEFT'):
                    i = max(i - 1, 0)
                    MENU_TEMP = i
                    break
                    
                elif button_list('BUTTON_SETTING'):
                    if key == '2-2':
                        wifi_config(0)
                        lcd_putstr(f" ==== MENU {key} ==== ", 0, 0, I2C_NUM_COLS)
                        lcd_putstr(f"[\x7FB N\x7E SET]  {TENSION_COUNT:>6}T", 0, 3, I2C_NUM_COLS)
                        
                    elif key == '3-2':
                        beepbeep(0.1)
                        ota_update()
                        lcd_putstr(f" ==== MENU {key} ==== ", 0, 0, I2C_NUM_COLS)
                        lcd_putstr(f"[\x7FB N\x7E SET]  {TENSION_COUNT:>6}T", 0, 3, I2C_NUM_COLS)
                        
                    elif key == '3-1':
                        beepbeep(0.1)
                        WIFI_IP = wifi_ip()
                        lcd_putstr(f"{WIFI_IP}", (I2C_NUM_COLS - len(WIFI_IP)), 1, len(WIFI_IP))

                    elif MENU_LIST_ARR[key][2][0] != None:
                    
                        if key == '4-1':
                            lcd_putstr("Press UP to Confirm", 0, 2, I2C_NUM_COLS)
                            
                        process_setting_item(key) 

                    break
                    
                elif button_list('BUTTON_DOWN'):
                    if key == '3-3':
                        ENGINEER_MENU = ENGINEER_MENU + 1
                        break
                    
                elif button_list('BUTTON_EXIT'):
                    beepbeep(0.1)
                    return 
            
            beepbeep(0.1)
            time.sleep(0.125)
    
    except Exception as e:
        handle_error(e, "setting_interface()")

def shutdown_reboot(flag):
    if flag == 0:
        lcd_putstr("System Shutdown Now!", 0, 0, I2C_NUM_COLS)
        lcd_putstr("Please power off in ", 0, 1, I2C_NUM_COLS)
        lcd_putstr("10s.", 0, 2, I2C_NUM_COLS)
        lcd_putstr("", 0, 3, I2C_NUM_COLS)
        logs_save(f"System Shutdown", "shutdown_reboot()")
        os.system("sudo shutdown -h now")
    elif flag == 1:
        lcd_putstr("System Reboot Now!", 0, 0, I2C_NUM_COLS)
        lcd_putstr("Please wait 30s to", 0, 1, I2C_NUM_COLS)
        lcd_putstr("boot.", 0, 2, I2C_NUM_COLS)
        lcd_putstr("", 0, 3, I2C_NUM_COLS)
        logs_save(f"System Reboot", "shutdown_reboot()")
        os.system("sudo reboot")

def check_status(flag):
    global WIFI_IP
    hx_diff_g = int((HX711["HX711_V0"] - HX711_V0) / 100 * (HX711_CAL.value / 20))
    if abs(hx_diff_g) > 45:
        if HX711_V0 == 0:
            hx_str = "HX Need Calibration!"
        else:
            hx_str = "HX Need Calibration?"
            
        lcd_putstr(f"{hx_str}", 0, 2, I2C_NUM_COLS)
        if flag == 1:
            logs_save(f"{hx_str} {hx_diff_g}g", "check_status()")
        
    elif get_cpu_temp() >= TEMP_WARNING_WIFI and check_wifi_status() == True:
        lcd_putstr(f"Wi-Fi turn off! {int(get_cpu_temp())}C", 0, 2, I2C_NUM_COLS)
        logs_save("Wi-Fi turn off", "check_status()")
        change_wifi("down")
        WIFI_IP = "Wi-Fi Down"
        
    else:
        lcd_putstr("Ready", 0, 2, I2C_NUM_COLS)
        
    # wifi status
    if WIFI_IP.count('.') == 3:
        lcd_putstr("W", 7, 3, 1)
    else:
        lcd_putstr(" ", 7, 3, 1)

def slide_table(flag):
    global MOTOR_MAX_STEPS, MOTOR_RS_STEPS, ABORT_LM
    MOTOR_MAX_STEPS = 10000
    MOTOR_RS_STEPS = 1000
    ABORT_LM = 4000
    if flag == 1605:
        MOTOR_MAX_STEPS = int(MOTOR_MAX_STEPS * 2)
        MOTOR_RS_STEPS = int(MOTOR_RS_STEPS * 2)
        ABORT_LM = int(ABORT_LM * 2)

def get_cpu_temp():
    try:
        with open("/sys/class/thermal/thermal_zone0/temp", "r") as file:
            temp = file.read().strip()
        cpu_temp = float(temp) / 1000.0
        return cpu_temp
    except FileNotFoundError:
        return None

def change_wifi(state):
    try:
        if state == "up":
            result = subprocess.run(["sudo", "nmcli", "radio", "wifi", "on"], check=True)
            if result.returncode == 0:
                logs_save(f"Wi-Fi turn on", "change_wifi()")
            else:
                logs_save(f"Wi-Fi turn on fail!：{result.stderr}", "change_wifi()")

        elif state == "down":
            result = subprocess.run(["sudo", "nmcli", "radio", "wifi", "off"], check=True)
            if result.returncode == 0:
                logs_save(f"Wi-Fi turn off", "change_wifi()")
            else:
                logs_save(f"Wi-Fi turn off fail!：{result.stderr}", "change_wifi()")
    
    except Exception as e:
        handle_error(e, "change_wifi()")

def check_wifi_status():
    try:
        result = subprocess.run(
            ["nmcli", "radio", "wifi"],
            capture_output=True, text=True, check=True
        )
        status = result.stdout.strip()
        if status == "enabled":
            return True
        elif status == "disabled":
            return False
        else:
            return None

    except subprocess.CalledProcessError as e:
        handle_error(e, "check_wifi_status()")

if __name__ == "__main__":

    RUNNING = mpValue('b', True)
    manager = Manager()
    HX711 = manager.dict({
        "RATE": 0,
        "DIFF": 0,
        "V0": [],
        "CP_HZ": 0.125,
        "HX711_CAL": LOAD_CELL_KG,
        "HX711_STABILITY_RATE": 0
        })
    
    TENSION_MON = sharedctypes.Value('i', 0)
    MOTOR_STP = sharedctypes.Value('i', 0)
    IS_TENSIONING = sharedctypes.Value('i', 0)
    CORR_COEF = sharedctypes.Value('d', 0)
    LB_CONV_G = sharedctypes.Value('i', 0)    
    HX711_CAL = manager.Value('d', 0)
    HX711_CAL.value = LOAD_CELL_KG
    CORR_COEF.value = 1.00
    LB_CONV_G.value = 0

    BUTTON_LIST = manager.dict({
        "BUTTON_HEAD": 0,
        "BUTTON_SETTING": 0,
        "BUTTON_EXIT": 0,
        "BUTTON_UP": 0,
        "BUTTON_DOWN": 0,
        "BUTTON_LEFT": 0,
        "BUTTON_RIGHT": 0,
        "MOTOR_SW_FRONT": 0,
        "MOTOR_SW_REAR": 0
    })

    try:
        logs_save("------", "init()PowerOn")
        logs_save(f"VER:{VERSION}/DATE:{VERDATE}", "init()")
        lcd_putstr(" ==== ZeroBETH ==== ", 0, 0, I2C_NUM_COLS)
        lcd_putstr(f"Ver : {VERSION}", 0, 1, I2C_NUM_COLS)
        lcd_putstr(f"Date: {VERDATE}", 0, 2, I2C_NUM_COLS)
        lcd_putstr("Ghub: 206cc/ZeroBETH", 0, 3, I2C_NUM_COLS)
        time.sleep(1)
        lcd_putstr("", 0, 3, I2C_NUM_COLS)
        
        boot_mode = 0
        for i in range(10):
            time.sleep(0.2)

            # HW Test Mode
            if GPIO.input(BUTTON_SETTING) == BUTTON_MODE["PRESSED_STATE"]:
                boot_mode = 1

            # Factory Settings Mode
            if GPIO.input(BUTTON_EXIT) == BUTTON_MODE["PRESSED_STATE"]:            
                boot_mode = 2

            # RT Mode
            if GPIO.input(BUTTON_UP) == BUTTON_MODE["PRESSED_STATE"]:
                boot_mode = 3

            # OTA Update Mode
            if GPIO.input(BUTTON_DOWN) == BUTTON_MODE["PRESSED_STATE"]:
                boot_mode = 4

            # Sys Logs Mode
            if GPIO.input(BUTTON_RIGHT) == BUTTON_MODE["PRESSED_STATE"]:
                boot_mode = 5
            
            if boot_mode == 0:
                lcd_putstr(".", i, 3, 1)
            else:
                lcd_putstr(f"{boot_mode}", i, 3, 1)
        
        with open(SSH_FIAL, "r", encoding="utf-8") as f:
            content = f.read()
            lcd_putstr(content, 12, 3, 8)
        time.sleep(2)
        LCD.clear()

        # HW Test Mode
        if boot_mode == 1:
            lcd_putstr("HW Testing MODE", 0, 0, I2C_NUM_COLS)
            time.sleep(2)

        # Factory Settings Mode
        if boot_mode == 2:
            beepbeep(0.1)
            lcd_putstr("Factory Reset?", 0, 0, I2C_NUM_COLS)
            lcd_putstr("[UP=Y DOWN=N]", 0, 3, I2C_NUM_COLS)
            logs_save("Factory Reset Check", "init()")
            while True:
                if GPIO.input(BUTTON_UP) == BUTTON_MODE["PRESSED_STATE"]:
                    if os.path.isfile(CONFIG_FILE):
                        os.rename(CONFIG_FILE, CONFIG_FILE + '.bak')
                        logs_save("Config Backup", "init()")
                        
                    beepbeep(0.1)
                    break
                    
                elif GPIO.input(BUTTON_DOWN) == BUTTON_MODE["PRESSED_STATE"]:
                    logs_save("Factory Reset Cancel", "init()")
                    beepbeep(0.1)
                    break
                    
                time.sleep(0.05)

        # RT Mode
        if boot_mode == 3:
            lcd_putstr("Reliability Testing", 0, 0, I2C_NUM_COLS)
            lcd_putstr("MODE", 0, 1, I2C_NUM_COLS)
            time.sleep(2)

        # Sys Logs Mode
        if boot_mode == 5:
            lcd_putstr("Display System Logs", 0, 0, I2C_NUM_COLS)
            lcd_putstr("MODE", 0, 1, I2C_NUM_COLS)
            time.sleep(2)
            sys_logs_show()

        # Disable Wi-Fi 連線
        subprocess.run(["sudo", "nmcli", "radio", "wifi", "on"], check=True)
        
        test_MOTOR_SPEED_LV = MOTOR_SPEED_LV
        config_read()
        DEFAULT_LB = min(DEFAULT_LB, LB_MAX)
        ori_BZ_SW = BZ_SW
        ori_MOTOR_SPEED_LV = max(1, min(9, MOTOR_SPEED_LV))
        MOTOR_SPEED_LV = test_MOTOR_SPEED_LV
        BZ_SW = 1
        LB_CONV_G.value = min(
            int((DEFAULT_LB * 453.59237) * ((PRE_STRECH + 100) / 100)),
            int(LB_MAX * 453.59237)
        )
        WIFI_IP = wifi_ip()
        lb_kg_select()
        slide_table(SLIDE_TABLE)
        
        # boot thread Initializing
        lcd_putstr(" == Startup Mode == ", 0, 0, I2C_NUM_COLS)
        lcd_putstr(">>Initializing", 0, 1, I2C_NUM_COLS)
        lcd_putstr("Tension monitoring", 0, 2, I2C_NUM_COLS)
        lcd_putstr("", 0, 3, I2C_NUM_COLS)
        p1 = Process(target=tension_monitoring, args=(HX711, TENSION_MON, MOTOR_STP, IS_TENSIONING, HX711_CAL, CORR_COEF, LB_CONV_G, RUNNING))
        p1.start()
        time.sleep(1)

        i = 0
        while True:
            if HX711["RATE"] != 0:
                logs_save(f"HX_Thread_Init_Time:{i/10}", "init()")
                break
            if i > 20:
                ERR_MSG[0] = "ERR: HX711@Zero #1"
                logs_save(ERR_MSG[0], "init()")
                break
            i = i + 1
            time.sleep(0.1)
        
        lcd_putstr("<DONE>", 0, 3, I2C_NUM_COLS)
        time.sleep(1)
        
        lcd_putstr("Detecting Buttons", 0, 2, I2C_NUM_COLS)
        lcd_putstr("", 0, 3, I2C_NUM_COLS)
        time.sleep(1)
        p2 = Process(target=button_detection, args=(BUTTON_LIST, RUNNING))
        p2.start()
        lcd_putstr("<DONE>", 0, 3, I2C_NUM_COLS)
        time.sleep(1)
        
        if boot_mode == 4:
            beepbeep(0.1)
            ota_update()
            lcd_putstr(" ==== ZeroBETH ==== ", 0, 0, I2C_NUM_COLS)
        
        # boot checking starting
        boot_check_err = {}
        lcd_putstr(">>Checking", 0, 1, I2C_NUM_COLS)
        
        # 檢查 hx711 取樣頻率
        lcd_putstr("HX711 Data Rate", 0, 2, I2C_NUM_COLS)
        lcd_putstr("", 0, 3, I2C_NUM_COLS)
        if HX711["RATE"] < 75:
            err_str = f"{HX711['RATE']}Hz"
            boot_check_err["HX711_Data_Rate"] = err_str
            logs_save(f"{boot_check_err['HX711_Data_Rate']}:{err_str}", "init()")
            lcd_putstr(f"<FAIL> {err_str}", 0, 3, I2C_NUM_COLS)
            LED_RED.on()
        else:
            lcd_putstr(f"<PASS> {HX711['RATE']}Hz", 0, 3, I2C_NUM_COLS)
        time.sleep(1)
        
        # 檢查 hx711 0值飄移
        lcd_putstr("HX711 Zero Drift", 0, 2, I2C_NUM_COLS)
        lcd_putstr("", 0, 3, I2C_NUM_COLS)
        if HX711["DIFF"] < 10:
            err_str = f"{HX711['DIFF']}"
            boot_check_err["HX711_Zero_Drift"] = err_str
            logs_save(f"{boot_check_err['HX711_Zero_Drift']}:{err_str}", "init()")
            lcd_putstr(f"<FAIL> {err_str}", 0, 3, I2C_NUM_COLS)
            LED_RED.on()
        else:
            lcd_putstr(f"<PASS> {HX711['DIFF']}", 0, 3, I2C_NUM_COLS)
        time.sleep(1)
        
        # 檢查 hx711 值飄移
        lcd_putstr("HX711 Drift", 0, 2, I2C_NUM_COLS)
        lcd_putstr("", 0, 3, I2C_NUM_COLS)
        hx711_drift = round(HX711['DIFF']/1000, 1)
        if HX711["DIFF"] > (HX711_DIFRT * 1000) or HX711["DIFF"] < 200:
            err_str = f"{hx711_drift}g"
            boot_check_err["HX711_Drift"] = err_str
            logs_save(f"{boot_check_err['HX711_Drift']}:{err_str}", "init()")
            lcd_putstr(f"<FAIL> {err_str}", 0, 3, I2C_NUM_COLS)
            LED_RED.on()
        else:
            lcd_putstr(f"<PASS> {hx711_drift}g", 0, 3, I2C_NUM_COLS)
        time.sleep(1)

        # 檢查 hx711 張力飄移
        lcd_putstr("Tension Drift", 0, 2, I2C_NUM_COLS)
        lcd_putstr("", 0, 3, I2C_NUM_COLS)
        tension_drift = abs(TENSION_MON.value)
        if tension_drift > 500:
            err_str = f"{tension_drift}g"
            boot_check_err["Tension_Drift"] = err_str
            logs_save(f"{boot_check_err['Tension_Drift']}:{err_str}", "init()")
            lcd_putstr(f"<FAIL> {err_str}", 0, 3, I2C_NUM_COLS)
            LED_RED.on()
        else:
            lcd_putstr(f"<PASS> {tension_drift}g", 0, 3, I2C_NUM_COLS)
        time.sleep(1)
        
        # 檢查 hx711 Stability Rate
        lcd_putstr("HX711 Stability Rate", 0, 2, I2C_NUM_COLS)
        lcd_putstr("", 0, 3, I2C_NUM_COLS)
        stability_rate = round(1 - ((HX711["ANOM_COUNT"] / HX711["SAMPLE_COUNT"]) / 2), 4) * 100
        if stability_rate < 99.0:
            err_str = f"{stability_rate:.2f}%"
            boot_check_err["HX711_Stability_Rate"] = err_str
            logs_save(f"{boot_check_err['HX711_Stability_Rate']}:{err_str}", "init()")
            lcd_putstr(f"<FAIL> {err_str}", 0, 3, I2C_NUM_COLS)
            LED_RED.on()
        else:
            lcd_putstr(f"<PASS> {stability_rate:.2f}%", 0, 3, I2C_NUM_COLS) 
        time.sleep(1)
 
        # 檢查按鍵是否正常
        lcd_putstr("Buttons Released", 0, 2, I2C_NUM_COLS)
        lcd_putstr("", 0, 3, I2C_NUM_COLS)
        chk_sw = check_sw()
        if chk_sw:
            err_str = f"{chk_sw}"
            boot_check_err["Buttons_Released"] = err_str
            logs_save(f"{boot_check_err['Buttons_Released']}:{err_str}", "init()")
            lcd_putstr(f"<FAIL> {err_str}", 0, 3, I2C_NUM_COLS)
            LED_RED.on()
        else:
            lcd_putstr(f"<PASS>", 0, 3, I2C_NUM_COLS)
        time.sleep(1)
 
        # show error list
        if len(boot_check_err) != 0:
            lcd_putstr(f" === {len(boot_check_err)} Error(s) === ", 0, 0, I2C_NUM_COLS)
            lcd_putstr("\x7FB N\x7E  UP=RST DW=OFF", 0, 3, I2C_NUM_COLS)
            beepbeep(1)
            i = 0
            while True:
                key, val = list(boot_check_err.items())[i]
                lcd_putstr(f"{key}", 0, 1, I2C_NUM_COLS)
                lcd_putstr(f"{val}", 0, 2, I2C_NUM_COLS)
                
                while True:
                    if GPIO.input(BUTTON_RIGHT) == BUTTON_MODE["PRESSED_STATE"]:
                        i = min(i + 1, len(boot_check_err) - 1)
                        break
                        
                    elif GPIO.input(BUTTON_LEFT) == BUTTON_MODE["PRESSED_STATE"]:
                        i = max(i - 1, 0)
                        break
                        
                    elif GPIO.input(BUTTON_DOWN) == BUTTON_MODE["PRESSED_STATE"]:
                        shutdown_reboot(0)
                        
                    elif GPIO.input(BUTTON_UP) == BUTTON_MODE["PRESSED_STATE"]:
                        shutdown_reboot(1)
                        
                    time.sleep(0.1)
        ### boot checking end ###
 
        hx_diff_g = int((HX711["HX711_V0"] - HX711_V0) / 100 * (HX711_CAL.value / 20))
        logs_save(
            f"RV0:{HX711_V0}/V0:{HX711['HX711_V0']}/DIFF:{HX711['DIFF']}/RATE:{HX711['RATE']}/DIFF_G:{hx_diff_g}/HX711_CAL:{HX711_CAL.value}/HX711_Stability_Rate:{stability_rate}",
            "init()HX711"
        )
        
        # 硬體測式模式
        if boot_mode == 1:
            main_interface()
            logs_save("HW TEST", "init()")
            beepbeep(0.1)
            hw_test(1, ori_BZ_SW)

        # 可靠性測試模式
        elif boot_mode == 3:
            logs_save("RT TEST", "init()")
            RT_MODE = 1
        
        # 第一次始用強制進入硬體測式模式
        if FIRST_TEST == 1:
            main_interface()
            logs_save("HW TEST FIRST", "init()")
            hw_test(0, ori_BZ_SW)

        time.sleep(1)
        
        # Resetting Clamp
        lcd_putstr(">>Motor Check...", 0, 1, I2C_NUM_COLS)
        logs_save("Resetting Clamp#0", "init()")
        lcd_putstr("Resetting Clamp", 0, 2, I2C_NUM_COLS)
        lcd_putstr("", 0, 3, I2C_NUM_COLS)
            
        BZ_SW = ori_BZ_SW
        ABORT_GRAM = (LB_MAX + 5) * 454
        head_reset(None)
        MOTOR_SPEED_LV = ori_MOTOR_SPEED_LV
        main_interface()
        lcd_putstr("Ready", 0, 2, I2C_NUM_COLS)
        check_status(1)

        beepbeep(0.3)
        BOOT_COUNT = BOOT_COUNT + 1
        config_save()

    except Exception as e:
        handle_error(e, "init()")
    
    try:
        ts_info_time = int(time.time() * 1000)
        press_time = 0
        v0_arr = []
        while True:
            if RT_MODE == 0:
                # Start tensioning 開始張緊
                if button_list('BUTTON_HEAD'):
                    start_tensioning()
                    show_timer()
                #    check_status()

                # Setting mode 設定模式
                if button_list('BUTTON_SETTING'):
                    beepbeep(0.1)
                    setting_interface(0)
                    main_interface()
                    lcd_putstr("Ready", 0, 2, I2C_NUM_COLS)
                    beepbeep(0.1)
                    show_timer()
                #    check_status()

                # Timer switch & Head reset 計時器開關 & 珠夾復位
                if button_list('BUTTON_EXIT'):
                    press_time = int(time.time() * 1000)
                    while GPIO.input(BUTTON_EXIT) == BUTTON_MODE["PRESSED_STATE"]:
                        if int(time.time() * 1000) - press_time > 1000:
                            head_reset(None)
                            break
                    
                    if int(time.time() * 1000) - press_time <= 1000:
                        if TIMER:
                            if TIMER_FLAG:
                                TIMER = 0
                                TIMER_FLAG = 0
                                lcd_putstr("      ", 14, 1, 6)
                            else:
                                TIMER_FLAG = time.time()
                        else:
                            TIMER = time.time()
                            lcd_putstr("   m  ", 14, 1, 6)

                    beepbeep(0.5)

                # Tension increment/decrement setting 加減張力設定
                if button_list('BUTTON_UP') or button_list('BUTTON_DOWN') or button_list('BUTTON_LEFT') or button_list('BUTTON_RIGHT'):
                    setting_ts()

                # Tension display update 張力顯示更新
                current_time = int(time.time() * 1000)
                if (current_time - ts_info_time) > 200:
                    LCD.hide_cursor()
                    tension_info(None, 0)
                    if TIMER and not TIMER_FLAG:
                        timer_diff = int(time.time() - TIMER)
                        lcd_putstr("{: >3d}".format(timer_diff // 60), 14, 1, 3)
                        lcd_putstr("{: >2d}".format(timer_diff % 60), 18, 1, 2)

                    LCD.move_to(TS_ARR[CURSOR_XY_TS_TEMP][0], TS_ARR[CURSOR_XY_TS_TEMP][1])
                    LCD.show_cursor()
                    ts_info_time = current_time

            # Reliability Testing Mode 穩定性測試模式
            else:
                rt_mode()

            # 自動 V0 修正
            v0_arr.append(HX711["HX711_VAL"])
            if len(v0_arr) > 600:
                v0_arr = sorted(v0_arr)
                HX711["HX711_V0"] = v0_arr[int(len(v0_arr) / 2)]
                v0_arr = []
                check_status(0)

            if ERR_MSG[0]:
                LED_RED.on()
                beepbeep(3)
                lcd_putstr(ERR_MSG[0], 0, 2, I2C_NUM_COLS)
                RUNNING.value = False
                p1.join()
                p2.join()
                break
            
            time.sleep(0.01)

    except Exception as e:
        handle_error(e, "main_loop()")
