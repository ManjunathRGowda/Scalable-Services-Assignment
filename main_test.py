from fastapi.testclient import TestClient
from main import app
from main import _check_process
import time

client = TestClient(app)


def test_start_browser_sad():
    response = client.get("/start", headers={"Browser-Type": "hailhydra", "Url": "http://www.google.com"})
    assert response.status_code == 400
    assert response.json() == {"detail": "Invalid Browser Type! Only Firefox or Chrome are supported."}

    response = client.get("/start", headers={"Browser-Type": "chrome", "Url": "www.google.com"})
    assert response.status_code == 400
    assert response.json() == {"detail": "Start the URL with http:// or https://"}


def test_start_browser_happy():
    response = client.get("/start", headers={"Browser-Type": "Chrome", "Url": "http://www.google.com"})
    assert response.status_code == 200
    assert response.text == '"The browser opened successfully!"'
    time.sleep(2)

    response = client.get("/start", headers={"Browser-Type": "firefox", "Url": "http://www.google.com"})
    assert response.status_code == 200
    assert response.text == '"The browser opened successfully!"'
    time.sleep(2)


def test_stop_browser_sad():
    response = client.get("/stop", headers={"Browser-Type": "hailhydra"})
    assert response.status_code == 400
    assert response.json() == {"detail": "Invalid Browser Type! Only Firefox or Chrome are supported."}


def test_stop_browser_happy():
    response = client.get("/stop", headers={"Browser-Type": "chrome"})
    assert response.status_code == 200
    assert response.text == '"Chrome browser closed successfully!"'
    time.sleep(2)

    response = client.get("/stop", headers={"Browser-Type": "FireFox"})
    assert response.status_code == 200
    assert response.text == '"Firefox browser closed successfully!"'
    time.sleep(2)

    if not _check_process("chrome"):
        response = client.get("/stop", headers={"Browser-Type": "chrome"})
        assert response.status_code == 400
        assert response.json() == {"detail": "No Browser was open to close!"}

    if not _check_process("firefox"):
        response = client.get("/stop", headers={"Browser-Type": "firefox"})
        assert response.status_code == 400
        assert response.json() == {"detail": "No Browser was open to close!"}


def test_cleanup_sad():
    response = client.get("/cleanup", headers={"Browser-Type": "hailHydra"})
    assert response.status_code == 400
    assert response.json() == {"detail": "Invalid Browser Type! Only Firefox or Chrome are supported."}

    client.get("/start", headers={"Browser-Type": "Chrome", "Url": "http://www.google.com"})
    time.sleep(2)

    client.get("/start", headers={"Browser-Type": "FireFox", "url": "http://www.google.com"})
    time.sleep(2)

    response = client.get("/cleanup", headers={"Browser-Type": "CHROME"})
    assert response.status_code == 400
    assert response.json() == {"detail": "Close the browser before running this API."}

    response = client.get("/cleanup", headers={"Browser-Type": "firefox"})
    assert response.status_code == 400
    assert response.json() == {"detail": "Close the browser before running this API."}


def test_cleanup_happy():
    client.get("/stop", headers={"Browser-Type": "chrome"})
    time.sleep(2)

    client.get("/stop", headers={"Browser-Type": "firefox"})
    time.sleep(2)

    if not _check_process("chrome"):
        response = client.get("/cleanup", headers={"Browser-Type": "CHROME"})
        assert response.status_code == 200
        assert response.text == '"Browser data clean up successful!"'

    if not _check_process("firefox"):
        response = client.get("/cleanup", headers={"Browser-Type": "FireFox"})
        assert response.status_code == 200
        assert response.text == '"Browser data clean up successful!"'


def test_geturl_sad():
    response = client.get("/geturl", headers={"Browser-Type": "hailHydra"})
    assert response.status_code == 400
    assert response.json() == {"detail": "Invalid Browser Type! Only Firefox or Chrome are supported."}

    if not _check_process("chrome"):
        response = client.get("/geturl", headers={"Browser-Type": "CHROME"})
        assert response.status_code == 400
        assert response.json() == {"detail": "Browser is not opened. Can't fetch active tab."}

    if not _check_process("firefox"):
        response = client.get("/geturl", headers={"Browser-Type": "firefox"})
        assert response.status_code == 400
        assert response.json() == {"detail": "Browser is not opened. Can't fetch active tab."}


def test_geturl_happy():
    client.get("/start", headers={"Browser-Type": "Chrome", "Url": "http://www.instagram.com"})
    time.sleep(2)

    client.get("/start", headers={"Browser-Type": "Chrome", "Url": "http://www.twitter.com"})
    time.sleep(2)

    client.get("/start", headers={"Browser-Type": "Chrome", "Url": "http://www.browserstack.com"})
    time.sleep(2)

    client.get("/start", headers={"Browser-Type": "FireFox", "Url": "http://www.facebook.com"})
    time.sleep(2)

    response = client.get("/geturl", headers={"Browser-Type": "chrome"})
    assert response.status_code == 200
    assert response.text == '"https://www.browserstack.com/\\n"'

    client.get("/stop", headers={"Browser-Type": "chrome"})
    time.sleep(2)

    client.get("/stop", headers={"Browser-Type": "firefox"})