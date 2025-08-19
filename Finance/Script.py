import undetected_chromedriver as uc

options = uc.ChromeOptions()
options.add_argument(r"--user-data-dir=C:\ChromeSessionGPT")

driver = uc.Chrome(options=options)
driver.get("https://chat.openai.com")
input("✅ ChatGPT loaded? Press ENTER to exit.")
driver.quit()
