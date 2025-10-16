# ecourts_scraper.py
import os
import time
import random
import json
import logging
import base64
import requests

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import TimeoutException, NoSuchElementException, UnexpectedAlertPresentException
from webdriver_manager.chrome import ChromeDriverManager

# --- Logging ---
logging.basicConfig(
    filename="scraper.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# --- Helper functions ---
def init_driver(headless=False):
    from selenium.webdriver.chrome.options import Options
    opts = Options()
    if headless:
        opts.add_argument("--headless=new")
    opts.add_argument("--disable-gpu")
    opts.add_argument("--no-sandbox")

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=opts)
    driver.set_window_size(1200, 900)
    return driver

def save_captcha(driver, path="captcha.png"):
    try:
        img = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "img[alt='Captcha']"))
        )
    except TimeoutException:
        logging.error("Captcha image not found!")
        raise RuntimeError("Captcha not found on page")
    src = img.get_attribute("src")
    if src.startswith("data:image"):
        header, b64 = src.split(",", 1)
        with open(path, "wb") as f:
            f.write(base64.b64decode(b64))
    else:
        r = requests.get(src)
        with open(path, "wb") as f:
            f.write(r.content)
    return path

def ensure_dir(path):
    os.makedirs(path, exist_ok=True)

def safe_join(*parts):
    return os.path.normpath(os.path.join(*parts))

def safe_download(url, out_path, retries=3, timeout=20):
    for attempt in range(retries):
        try:
            r = requests.get(url, timeout=timeout)
            r.raise_for_status()
            ensure_dir(os.path.dirname(out_path))
            with open(out_path, "wb") as f:
                f.write(r.content)
            logging.info(f"Downloaded successfully: {out_path}")
            return True
        except Exception as e:
            wait = 2 ** attempt
            logging.warning(f"Attempt {attempt+1} failed for {url}: {e}. Retrying in {wait}s")
            time.sleep(wait)
    logging.error(f"Failed after {retries} attempts: {url}")
    return False

def add_manifest_entry(date_str, state, district, court_complex, court_name, judge, file_path):
    manifest_path = os.path.join("output", f"{date_str}_manifest.json")
    if os.path.exists(manifest_path):
        with open(manifest_path, "r", encoding="utf-8") as mf:
            data = json.load(mf)
    else:
        data = {
            "date": date_str,
            "state": state,
            "district": district,
            "court_complex": court_complex,
            "downloads": []
        }

    entry = {"court": court_name, "judge": judge or "Unknown", "file": file_path.replace("\\", "/")}
    data["downloads"].append(entry)

    with open(manifest_path, "w", encoding="utf-8") as mf:
        json.dump(data, mf, indent=2, ensure_ascii=False)
    logging.info(f"Updated manifest: {manifest_path}")

# --- Robust element fetch ---
def wait_for_select(driver, possible_ids, timeout=40):
    """
    Wait for a <select> element to be visible and return it as a Select object.
    Tries multiple possible IDs for robustness.
    """
    for elem_id in possible_ids:
        try:
            el = WebDriverWait(driver, timeout).until(
                EC.visibility_of_element_located((By.ID, elem_id))
            )
            return Select(el)
        except TimeoutException:
            continue
    raise RuntimeError(f"No matching dropdown found from: {possible_ids}")

# --- Main scraper function ---
def fetch_cause_list_pdf(state, district, court_complex, date_str, civil_or_criminal="Civil", out_dir="output"):
    driver = init_driver(headless=False)
    try:
        driver.get("https://services.ecourts.gov.in/ecourtindia_v6/?p=cause_list/")
        time.sleep(3)  # let page fully render

        # --- Select dropdowns with multiple IDs ---
        state_select = wait_for_select(driver, ["ddlState", "state", "sess_state_code"])
        state_select.select_by_visible_text(state)

        district_select = wait_for_select(driver, ["ddlDistrict", "district", "sess_district_code"])
        district_select.select_by_visible_text(district)

        complex_select = wait_for_select(driver, ["ddlCourtComplex", "courtcomplex"])
        complex_select.select_by_visible_text(court_complex)

        court_select = wait_for_select(driver, ["ddlCourtName", "courtname"])
        court_select.select_by_index(1)
        court_name = court_select.first_selected_option.text

        # Set date
        date_input = driver.find_element(By.ID, "cldate")
        date_input.clear()
        date_input.send_keys(date_str)

        # Captcha
        captcha_path = save_captcha(driver, "captcha.png")
        print("Captcha saved at", captcha_path)
        captcha_value = input("Enter captcha: ")
        driver.find_element(By.ID, "captcha").send_keys(captcha_value)

        # Click Civil/Criminal
        try:
            if civil_or_criminal.lower().startswith("civ"):
                driver.find_element(By.ID, "btnCivil").click()
            else:
                driver.find_element(By.ID, "btnCriminal").click()
        except NoSuchElementException:
            logging.warning("Civil/Criminal button not found. Skipping click.")

        # Wait for possible alert (like "Select Establishment")
        time.sleep(2)
        try:
            alert = driver.switch_to.alert
            alert_text = alert.text
            logging.warning(f"Alert Text: {alert_text}")
            alert.dismiss()
            print(f"⚠️ Alert appeared and dismissed: {alert_text}")
        except:
            pass

        # Wait for PDF link
        time.sleep(3)
        pdf_link = None
        try:
            link_el = driver.find_element(By.PARTIAL_LINK_TEXT, "View PDF")
            pdf_link = link_el.get_attribute("href")
        except NoSuchElementException:
            logging.warning("PDF link not found; consider capturing printable view")

        if pdf_link:
            base_dir = safe_join(out_dir, state, district, court_complex, date_str)
            ensure_dir(base_dir)
            out_path = safe_join(base_dir, f"{court_name}.pdf")

            success = safe_download(pdf_link, out_path)
            if success:
                add_manifest_entry(date_str, state, district, court_complex, court_name, "Unknown", out_path)
                print(f"Saved PDF: {out_path}")
            else:
                print(f"Failed to download PDF for {court_name}")

            # Polite delay
            time.sleep(random.uniform(2, 4))
        else:
            print("PDF link not found. Cannot download.")
    finally:
        driver.quit()

# --- Example run ---
if __name__ == "__main__":
    try:
        fetch_cause_list_pdf("Delhi", "New Delhi", "District Court Complex", "16-10-2025")
    except Exception as e:
        print("❌ An error occurred:", e)
