from fastapi import FastAPI, Header, HTTPException
import webbrowser as web
import sys
import psutil
import os
import subprocess
import signal
import json
import lz4.block
import pathlib
import pyautogui as gui
import pyperclip

# Function to determine the OS where the webserver is running.
def _detect_os():
    if sys.platform.startswith("darwin"):
        os_type = "mac"
    elif sys.platform.startswith("win") or sys.platform.startswith("cygwin"):
        os_type = "windows"
    elif sys.platform.startswith("linux"):
        os_type = "linux"
    else:
        print("Unsupported OS Distribution!")
        exit(1)
    return os_type


# Function to get the Browser Executable Path
def _get_browser_path(os_type: str, browser_type: str):
    if os_type == "mac" and browser_type == "chrome":
        browser_path = "open -a /Applications/Google\ Chrome.app %s"
    elif os_type == "mac" and browser_type == "firefox":
        browser_path = "open -a /Applications/Firefox.app %s"
    elif os_type == "windows" and browser_type == "chrome":
        browser_path = "C:/Program Files (x86)/Google/Chrome/Application/chrome.exe %s"
    elif os_type == "windows" and browser_type == "firefox":
        browser_path = "C:/Program Files (x86)/Mozilla Firefox\Firefox.exe %s"
    elif os_type == "linux" and browser_type == "chrome":
        browser_path = "/usr/bin/google-chrome %s"
    elif os_type == "linux" and browser_type == "firefox":
        browser_path = "/usr/bin/firefox %s"
    else:
        print("Could not get the required browser path!")
        exit(1)
    return browser_path


def _check_process(browser_type: str):
    for proc in psutil.process_iter():
        try:
            # Check if process name contains the given name string.
            if browser_type.lower() in proc.name().lower():
                return True
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    return False


def _fetch_active_tab_firefox(ospath: str):
    path = pathlib.Path.home().joinpath(ospath)
    files = path.glob("*default/sessionstore-backups/recovery.js*")

    for f in files:
        b = f.read_bytes()
        if b[:8] == b"mozLz40\0":
            b = lz4.block.decompress(b[8:])
        j = json.loads(b)
        for w in j["windows"]:
            most_recent_tab = ""
            for t in w["tabs"]:
                i = t["index"] - 1
                most_recent_tab = t["entries"][i]["url"]

    return most_recent_tab


app = FastAPI()


@app.get("/start", status_code=200, description="Starts the browser!")
async def start_browser(
    browser_type: str = Header(
        default=None,
        description="Select the browser you want to open. Only Chrome and Firefox are supported!",
    ),
    url: str = Header(
        default=None, description="Type the website URL you want to open!"
    ),
):
    browser_type = browser_type.lower()

    url = url.lower()

    if browser_type not in ["firefox", "chrome"]:
        raise HTTPException(
            status_code=400,
            detail="Invalid Browser Type! Only Firefox or Chrome are supported.",
        )

    if not (url.startswith("http")):
        raise HTTPException(
            status_code=400, detail="Start the URL with http:// or https://"
        )

    os_type = _detect_os()

    browser_path = _get_browser_path(os_type, browser_type)

    web.get(browser_path).open_new_tab(url)
    return "The browser opened successfully!"


@app.get("/stop", status_code=200, description="Stops the opened browser!")
async def stop_browser(
    browser_type: str = Header(
        default=None,
        description="Select the browser you want to close. Only Chrome and Firefox are supported!",
    )
):
    browser_type = browser_type.lower()
    os_type = _detect_os()

    if browser_type not in ["firefox", "chrome"]:
        raise HTTPException(
            status_code=400,
            detail="Invalid Browser Type! Only Firefox or Chrome are supported.",
        )

    if not _check_process(browser_type):
        raise HTTPException(status_code=400, detail="No Browser was open to close!")

    if os_type == "mac" and browser_type == "chrome":
        os.system("killall -9 'Google Chrome'")
        return "Chrome browser closed successfully!"

    if os_type == "mac" and browser_type == "firefox":
        os.system("killall -9 'firefox'")
        return "Firefox browser closed successfully!"

    if os_type == "windows" and browser_type == "chrome":
        os.system("taskkill /im chrome.exe /f")
        return "Chrome browser closed successfully!"

    if os_type == "windows" and browser_type == "firefox":
        os.system("taskkill /im firefox.exe /f")
        return "Firefox browser closed successfully!"

    if os_type == "linux" and browser_type == "chrome":
        proc = subprocess.Popen(["pgrep", "chrome"], stdout=subprocess.PIPE)
        for pid in proc.stdout:
            os.kill(int(pid), signal.SIGTERM)
            # Check if the process that we killed is alive.
            try:
                os.kill(int(pid), 0)
                raise Exception(
                    """wasn't able to kill the process 
                                  HINT:use signal.SIGKILL or signal.SIGABORT"""
                )
            except OSError as ex:
                continue
        return "Chrome browser closed successfully!"

    if os_type == "linux" and browser_type == "firefox":
        proc = subprocess.Popen(["pgrep", "firefox"], stdout=subprocess.PIPE)
        for pid in proc.stdout:
            os.kill(int(pid), signal.SIGTERM)
            # Check if the process that we killed is alive.
            try:
                os.kill(int(pid), 0)
                raise Exception(
                    """wasn't able to kill the process 
                                              HINT:use signal.SIGKILL or signal.SIGABORT"""
                )
            except OSError as ex:
                continue
        return "Firefox browser closed successfully!"


@app.get("/cleanup", status_code=200, description="Clears the entire browsing data!")
async def clear_browser_data(
    browser_type: str = Header(
        default=None,
        description="Select the browser you want to clear the browsing data. Only Chrome and Firefox are supported!",
    )
):
    os_type = _detect_os()
    browser_type = browser_type.lower()

    if browser_type not in ["firefox", "chrome"]:
        raise HTTPException(
            status_code=400,
            detail="Invalid Browser Type! Only Firefox or Chrome are supported.",
        )

    if _check_process(browser_type):
        raise HTTPException(
            status_code=400, detail="Close the browser before running this API."
        )

    if os_type == "mac":
        try:
            command = "chmod +x mac.sh && ./mac.sh " + browser_type
            os.system(command)
            return "Browser data clean up successful!"
        except Exception as e:
            raise HTTPException(status_code=400, detail=e)

    if os_type == "linux":
        try:
            command = "chmod +x linux.sh && ./linux.sh " + browser_type
            os.system(command)
            return "Browser data clean up successful!"
        except Exception as e:
            raise HTTPException(status_code=400, detail=e)

    if os_type == "windows" and browser_type == "chrome":
        try:
            subprocess.call([r"win_chrome.bat"])
            return "Browser data clean up successful!"
        except Exception as e:
            raise HTTPException(status_code=400, detail=e)

    if os_type == "windows" and browser_type == "firefox":
        try:
            subprocess.call([r"win_firefox.bat"])
            return "Browser data clean up successful!"
        except Exception as e:
            raise HTTPException(status_code=400, detail=e)


@app.get(
    "/geturl",
    status_code=200,
    description="Fetches the url of the active tab in the browser!",
)
async def get_active_url(
    browser_type: str = Header(
        default=None,
        description="Select the browser you want to fetch active tab url. Only Chrome and Firefox are supported!",
    )
):
    os_type = _detect_os()
    browser_type = browser_type.lower()

    if browser_type not in ["firefox", "chrome"]:
        raise HTTPException(
            status_code=400,
            detail="Invalid Browser Type! Only Firefox or Chrome are supported.",
        )

    if not _check_process(browser_type):
        raise HTTPException(
            status_code=400, detail="Browser is not opened. Can't fetch active tab."
        )

    if os_type == "mac" and browser_type == "firefox":
        ospath = "Library/Application Support/Firefox/Profiles"
        active_url = _fetch_active_tab_firefox(ospath)
        return active_url

    if os_type == "mac" and browser_type == "chrome":
        script = 'tell application "Google Chrome" to get URL of active tab of window 1'
        p = subprocess.Popen(
            ["osascript", "-"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True,
        )
        active_url, err = p.communicate(script)
        return active_url

    if os_type == "linux" and browser_type == "firefox":
        ospath = ".mozilla/firefox"
        active_url = _fetch_active_tab_firefox(ospath)
        return active_url

    if os_type == "linux" and browser_type == "chrome":
        p = subprocess.Popen(
            ["chrome-session-dump", "-active"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        active_url, err = p.communicate()
        return active_url

    if os_type == "windows" and browser_type == "firefox":
        ospath = "AppData\\Local\\Mozilla\\Firefox\\Profiles"
        active_url = _fetch_active_tab_firefox(ospath)
        return active_url

    if os_type == "windows" and browser_type == "chrome":
        gui.click(0, 200)
        gui.press("f6")
        gui.hotkey("ctrl", "c")
        active_url = pyperclip.paste()
        return active_url
