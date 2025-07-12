import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

# ---------------- 文件路径常量 ----------------
SITES_FILE  = 'pt_sites.json'
COOKIES_FILE = 'pt_cookies.json'

# ---------------- 业务函数 ----------------
def load_sites():
    """读取站点配置"""
    if not os.path.exists(SITES_FILE):
        messagebox.showerror("错误", f"{SITES_FILE} 不存在！")
        return {}
    with open(SITES_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def load_cookies(alias):
    """根据别名读取 cookies"""
    if not os.path.exists(COOKIES_FILE):
        return []
    with open(COOKIES_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
        return data.get(alias, [])

def save_cookies(alias, cookies):
    """将 cookies 写入 JSON"""
    data = {}
    if os.path.exists(COOKIES_FILE):
        with open(COOKIES_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
    data[alias] = cookies
    with open(COOKIES_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# ---------------- Selenium 相关 ----------------
driver = None   # 全局浏览器实例

def open_site():
    """打开站点并加载 cookies"""
    global driver
    alias = site_var.get()
    if not alias:
        messagebox.showwarning("警告", "请先选择 PT 站点")
        return

    url = sites.get(alias)
    if not url:
        messagebox.showerror("错误", f"未找到 {alias} 的 URL")
        return

    # 启动浏览器
    chrome_opts = Options()
    chrome_opts.add_argument("--disable-blink-features=AutomationControlled")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()),
                              options=chrome_opts)
    driver.get(url)
    WebDriverWait(driver, 60).until(EC.presence_of_element_located((By.TAG_NAME, 'body')))

    # 加载 cookies
    for c in load_cookies(alias):
        try:
            driver.add_cookie(c)
        except Exception as e:
            print("添加 cookie 失败:", e)
    driver.get(url)
    WebDriverWait(driver, 60).until(EC.presence_of_element_located((By.TAG_NAME, 'body')))

    # 按钮切换：隐藏“打开页面”，显示“保存 cookies”和“运行”
    open_btn.pack_forget()
    save_btn.pack(pady=5)
    run_btn.pack(pady=5)

def save_current_cookies():
    """保存当前浏览器 cookies"""
    alias = site_var.get()
    if driver is None:
        messagebox.showwarning("警告", "请先打开站点")
        return
    try:
        save_cookies(alias, driver.get_cookies())
        messagebox.showinfo("成功", f"{alias} 的 cookies 已保存")
    except Exception as e:
        messagebox.showerror("错误", f"保存失败：{e}")

def run_todo():
    messagebox.showinfo("提示", "todo")

# ---------------- GUI ----------------
root = tk.Tk()
root.title("PT 站点工具")
root.geometry("300x200")
root.resizable(False, False)

# 加载站点列表
sites = load_sites()
site_aliases = list(sites.keys())

# 下拉框
site_var = tk.StringVar()
site_combo = ttk.Combobox(root, textvariable=site_var,
                          values=site_aliases,
                          state="readonly", width=20)
site_combo.set("选择 PT 站点")
site_combo.pack(pady=20)

# 三个按钮，初始只显示 open_btn
open_btn = tk.Button(root, text="打开页面", command=open_site)
save_btn = tk.Button(root, text="保存 cookies", command=save_current_cookies)
run_btn  = tk.Button(root, text="运行", command=run_todo)

open_btn.pack()

root.mainloop()