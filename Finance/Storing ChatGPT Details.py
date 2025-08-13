# permute_labels_to_mongo.py
import itertools
import json
import re
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
DRY_RUN = False           # True = print only; do not write to Mongo
SKIP_EXISTING = True      # Skip combos already stored

CHROME_BINARY = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
USER_DATA_DIR = r"C:\ChromeSession"   # requires an already logged-in profile
CHATGPT_URL = "https://chat.openai.com"

BAND7 = [
    "+Muito Alto", "+Alto", "+Médio", "0",
    "-Médio", "-Alto", "-Muito Alto"
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
                ("Pressure_Label", 1)
            ],
            unique=True
        )
        print("✅ Unique index ensured on (DensitySpread_Label, Liquidity_Label, Pressure_Label)")
    except Exception as e:
        print("⚠️ Could not create unique index:", e)

# ==========================
# BROWSER / CHATGPT
# ==========================
def start_browser():
    options = uc.ChromeOptions()
    options.binary_location = CHROME_BINARY
    # If you have a logged-in profile, uncomment:
    # options.add_argument(f"--user-data-dir={USER_DATA_DIR}")
    # options.add_argument("--profile-directory=Default")
    driver = uc.Chrome(options=options)
    driver.get(CHATGPT_URL)
    print("Aguardando ChatGPT abrir...")
    time.sleep(8)
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
        time.sleep(0.2)
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
        print("❌ JSON inválido:", text)
        return None
    return {
        "leitura": data.get("leitura", "").strip(),
        "tendencia": data.get("tendencia", "").strip(),
        "observacoes": data.get("observacoes", "").strip(),
    }

# ==========================
# MAIN
# ==========================
def main():
    db = connect_mongo()
    coll_out = db[COLL_OUT]
    ensure_unique_index(coll_out)  # ← keep a single doc per label trio

    driver = start_browser()
    input("Pressione ENTER quando estiver autenticado no ChatGPT...")

    total = 0
    for ds_lab, liq_lab, press_lab in itertools.product(BAND7, repeat=3):
        # Skip if already present (saves tokens/time)
        if SKIP_EXISTING and coll_out.find_one({
            "DensitySpread_Label": ds_lab,
            "Liquidity_Label": liq_lab,
            "Pressure_Label": press_lab
        }):
            print(f"⏩ Já existe: ({ds_lab}, {liq_lab}, {press_lab}) — pulando.")
            continue

        prompt = (
            "Você é um assistente de trading. Classifique os valores abaixo usando sua tabela de interpretação (INTERP7) "
            "e responda SOMENTE em JSON com as chaves exatamente 'leitura', 'tendencia', 'observacoes' (sem texto extra): "
            f"DensitySpread_Mean: {ds_lab} "
            f"Liquidity_Mean: {liq_lab} "
            f"Pressure_Mean: {press_lab}"
        )

        print(f"\n📨 Enviando para combo ({ds_lab}, {liq_lab}, {press_lab})")
        try:
            send_prompt(driver, prompt)
            text = wait_for_stable_response(driver)
            parsed = parse_json_response(text)
        except:
            continue
        if not parsed:
            print("❌ Falha no parse; seguindo adiante.")
            time.sleep(1.0)
            continue

        out_doc = {
            # "created_at": datetime.utcnow(),   # opcional
            "DensitySpread_Label": ds_lab,
            "Liquidity_Label": liq_lab,
            "Pressure_Label": press_lab,
            **parsed,
        }

        if DRY_RUN:
            print("💡 DRY_RUN - não salvando no Mongo. Documento seria:\n",
                  json.dumps(out_doc, ensure_ascii=False, indent=2))
        else:
            # Upsert pelo trio de labels (composto)
            coll_out.update_one(
                {
                    "DensitySpread_Label": ds_lab,
                    "Liquidity_Label": liq_lab,
                    "Pressure_Label": press_lab
                },
                {"$set": out_doc},
                upsert=True
            )
            print(f"✅ Gravado/atualizado em '{COLL_OUT}' com labels ({ds_lab}, {liq_lab}, {press_lab})")
            total += 1

        time.sleep(3)  # mitigar rate-limit

    driver.quit()
    print(f"\n✅ Finalizado. Documentos gravados/atualizados: {total}")

if __name__ == "__main__":
    main()
