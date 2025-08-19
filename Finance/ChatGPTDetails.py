# permute_labels_to_mongo.py
import sys
import os
import itertools
import json
import re
import pdb
import time
from datetime import datetime
from pymongo import MongoClient
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# ==========================
# CONFIG
# ==========================
MONGO_URI = "mongodb://localhost:27017"
DB_NAME = "mongodb"
COLL_OUT = "prices_interpretation"
CHATGPT_CONFIG_FILE = 'chatgpt_url.txt'
CHATGPT_DEFAULT_URL = "https://chat.openai.com"

BAND5 = [
    "+Alto", "+Médio", "0",
    "-Médio", "-Alto"
]

# ==========================
# DB
# ==========================
def connect_mongo():
    client = MongoClient(MONGO_URI)
    return client[DB_NAME]

def ensure_unique_index(coll):
    try:
        coll.create_index(
            [
                ("DensitySpread_Label", 1),
                ("Liquidity_Label", 1),
                ("Pressure_Label", 1),
                ("AgentImbalance_Label", 1)
            ],
            unique=True
        )
        #print("✅ Unique index ensured on (DensitySpread_Label, Liquidity_Label, Pressure_Label, AgentImbalance_Label)")
    except Exception as e:
        pass
        #print("⚠️ Could not create unique index:", e)

# ==========================
# BROWSER / CHATGPT
# ==========================
def get_url():
    """Return the ChatGPT URL from config file if available, else default."""
    if os.path.exists(CHATGPT_CONFIG_FILE):
        with open(CHATGPT_CONFIG_FILE, "r", encoding="utf-8") as f:
            url = f.read().strip()
            if url:  # make sure it's not empty
                return url
    return CHATGPT_DEFAULT_URL

def start_browser():
    options = uc.ChromeOptions()
    options.add_argument(r"--user-data-dir=C:\ChromeSessionGPT")
    driver = uc.Chrome(options=options)
    url = get_url()
    driver.get(url)
    return driver

def send_prompt(driver, prompt):
    wait = WebDriverWait(driver, 20)
    textarea = wait.until(EC.presence_of_element_located((By.ID, "prompt-textarea")))
    textarea.clear()
    textarea.send_keys(prompt)
    textarea.send_keys(Keys.ENTER)

def wait_for_stable_response(driver, timeout=90, stable_duration=1.0):
    wait = WebDriverWait(driver, timeout)
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.markdown.prose")))
    previous_text, stable_start = None, None
    while True:
        messages = driver.find_elements(By.CSS_SELECTOR, "div.markdown.prose")
        latest = messages[-1].text.strip() if messages else ""
        if latest == previous_text:
            if stable_start is None:
                stable_start = time.time()
            elif latest and len(latest) > 0 and time.time() - stable_start >= stable_duration:
                break
        else:
            previous_text = latest
            stable_start = None
        time.sleep(1)
    return latest

# ==========================
# JSON PARSE HELPERS
# ==========================
def _extract_json_block(text):
    """Extract a valid JSON object even if fenced by ```json ... ``` or surrounded by extra text."""
    fenced = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, flags=re.DOTALL)
    if fenced:
        return fenced.group(1)
    first = text.find("{")
    last = text.rfind("}")
    if first != -1 and last != -1 and last > first:
        return text[first:last+1]
    return text

def parse_json_response(text):
    raw = _extract_json_block(text)
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        #print("❌ JSON inválido:", text)
        return None
    return {
        "leitura": data.get("leitura", "").strip(),
        "tendencia": data.get("tendencia", "").strip(),
        "observacoes": data.get("observacoes", "").strip(),
    }

def save_chat_url_once(driver):
    """Save the current chat URL into CHATGPT_CONFIG_FILE if file doesn't already exist."""
    if not os.path.exists(CHATGPT_CONFIG_FILE):
        try:
            url = driver.current_url
            if url and "/c/" in url:  # makes sure it's a chat URL
                with open(CHATGPT_CONFIG_FILE, "w", encoding="utf-8") as f:
                    f.write(url.strip())
                #print(f"💾 Saved chat URL into {CHATGPT_CONFIG_FILE}")
        except Exception as e:
            #print(f"⚠️ Could not save chat URL: {e}")
            pass


def process_label_quartet(ds_lab, liq_lab, press_lab, ad_lab):
    global driver, coll_out

    prompt = (
        "Você é um assistente de trading. Classifique os valores abaixo usando sua tabela de interpretação (INTERP5) "
        "e responda SOMENTE em JSON com as chaves exatamente 'leitura', 'tendencia', 'observacoes' "
        "Obs.: A chave 'leitura' refere-se a Leitura do livro/fluxo, então deve conter algo similar a 'Resistência clara, pressão tenta romper' "
        "E não use mais de uma resposta para eu escolher qual é a melhor "
        f"DensitySpread_Mean: {ds_lab} "
        f"Liquidity_Mean: {liq_lab} "
        f"Pressure_Mean: {press_lab} "
        f"AgentImbalance_Max: {ad_lab}"
    )

    try:
        send_prompt(driver, prompt)
        text = wait_for_stable_response(driver)
        parsed = parse_json_response(text)
    except Exception as e:
        #print("⚠️ Erro ao obter resposta:", e)
        return

    if not parsed:
        #print("❌ Falha no parse; seguindo adiante.")
        time.sleep(1.0)
        return

    out_doc = {
        "DensitySpread_Label": ds_lab,
        "Liquidity_Label": liq_lab,
        "Pressure_Label": press_lab,
        "AgentImbalance_Label": ad_lab,
        **parsed,
    }

    
    coll_out.update_one(
        {
            "DensitySpread_Label": ds_lab,
            "Liquidity_Label": liq_lab,
            "Pressure_Label": press_lab,
            "AgentImbalance_Label": ad_lab
        },
        {"$set": out_doc},
        upsert=True
    )
    #print(f"✅ Gravado/atualizado em '{COLL_OUT}'")

    #time.sleep(3)


# ==========================
# MAIN
# ==========================
def main():
    global driver, coll_out

    if len(sys.argv) != 5:
        #print("❌ Esperando 4 argumentos: DensitySpread Liquidity Pressure AgentImbalance")
        #print("💡 Exemplo:")
        #print('    python "Storing ChatGPT Details.py" "+Alto" "-Médio" "0" "+Médio"')
        return

    ds_lab, liq_lab, press_lab, ad_lab = sys.argv[1:5]

    db = connect_mongo()
    coll_out = db[COLL_OUT]
    ensure_unique_index(coll_out)

    #print("🧠 Resultado ainda não existe. Consultando o ChatGPT...")

    driver = start_browser()
    process_label_quartet(ds_lab, liq_lab, press_lab, ad_lab)
    save_chat_url_once(driver)
    driver.quit()

if __name__ == "__main__":
    main()

