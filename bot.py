import os
import json
import time
import random
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains

class YtuRezervasyonBotu:
    def __init__(self, ogrenci_no, sifre):
        self.ogrenci_no = ogrenci_no
        self.sifre = sifre
        self.tarayici = None
        self.baslat_tarayici()

    def baslat_tarayici(self):
        options = uc.ChromeOptions()
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")

        # Docker container içinde headless mod gerekli
        if os.environ.get("DOCKER_ENV"):
            options.add_argument("--headless=new")
            options.add_argument("--disable-gpu")
            options.add_argument("--window-size=1920,1080")
            options.add_argument("--disable-extensions")

        self.tarayici = uc.Chrome(options=options, use_subprocess=True)

    def insan_gibi_bekle(self, min_sn=1.0, max_sn=2.5):
        time.sleep(random.uniform(min_sn, max_sn))

    def bot_dogrulamasi_bekle(self):
        print("Bot doğrulaması kontrol ediliyor...")
        baslangic = time.time()
        while True:
            try:
                dogrulama_elementleri = self.tarayici.find_elements(By.XPATH, "//*[contains(text(), 'Bot doğrulaması yapılıyor')]")
                if len(dogrulama_elementleri) > 0:
                    print("Cloudflare doğrulama ekranı tespit edildi, bekleniyor...")
                    time.sleep(2)
                else:
                    self.insan_gibi_bekle(1, 2)
                    break
            except:
                break
            if time.time() - baslangic > 45:
                break

    def insan_gibi_tikla(self, element):
        try:
            self.tarayici.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
            self.insan_gibi_bekle(0.2, 0.4)
        except:
            pass
        actions = ActionChains(self.tarayici)
        actions.move_to_element(element)
        actions.pause(random.uniform(0.2, 0.5))
        actions.click()
        actions.perform()

    def giris_yap(self):
        print("Saha kapatma operasyonu başlıyor...")
        self.tarayici.get("https://tesis.yildiz.edu.tr/rezervasyon")
        self.insan_gibi_bekle(3, 5)
        
        self.bot_dogrulamasi_bekle()
        
        no_kutusu = self.tarayici.find_element(By.XPATH, "//input[@placeholder='E-posta ya da öğrenci numarası']")
        no_kutusu.click()
        self.insan_gibi_bekle(0.3, 0.7)
        no_kutusu.send_keys(self.ogrenci_no)
        self.insan_gibi_bekle(0.5, 1.0)
        
        sifre_kutusu = self.tarayici.find_element(By.XPATH, "//input[@placeholder='Şifre']")
        sifre_kutusu.click()
        self.insan_gibi_bekle(0.3, 0.7)
        sifre_kutusu.send_keys(self.sifre)
        self.insan_gibi_bekle(0.5, 1.0)
        
        giris_butonu = self.tarayici.find_element(By.XPATH, "//button[@type='submit']")
        self.insan_gibi_tikla(giris_butonu)
        print("Sisteme sızıldı aga!")
        
    def tesis_ve_saat_sec(self, hedef_gun="Çarşamba", hedef_saat="20.00 - 21.00"):
        self.bot_dogrulamasi_bekle()
        print(f"🎯 Hedef: {hedef_gun} - {hedef_saat} slotu piksel koordinatlarıyla aranıyor...")
        wait = WebDriverWait(self.tarayici, 30)
        
        while True:
            try:
                self.bot_dogrulamasi_bekle()

                try:
                    kabul_btn = self.tarayici.find_element(By.XPATH, "//button[contains(text(), 'Kabul Et')]")
                    kabul_btn.click()
                except:
                    pass

                print("Halı Saha menüsüne tıklanıyor...")
                hali_saha_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//h3[text()='Halı Saha']")))
                
                self.insan_gibi_bekle(1, 2)
                self.insan_gibi_tikla(hali_saha_btn) 
                
                print("Tablonun yüklenmesi bekleniyor...")
                wait.until(
                    EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'DOLU') or contains(text(), 'ÖDEME BEKLENİYOR') or contains(text(), '+')]"))
                )
                print("Veriler oturdu, koordinatlar hesaplanıyor...")
                
                self.insan_gibi_bekle(1.5, 2.0)
                
                gun_kisa = {"cumartesi": "Cmt", "perşembe": "Per", "cuma": "Cum", "salı": "Sal", "çarşamba": "Çar", "pazartesi": "Pzt", "pazar": "Paz"}.get(hedef_gun.lower().strip(), "Cmt")
                gun_element = wait.until(EC.presence_of_element_located((By.XPATH, f"//*[contains(text(), '{gun_kisa}')]")))
                gun_x = gun_element.location['x']
                
                saat_element = wait.until(EC.presence_of_element_located((By.XPATH, f"//*[contains(text(), '{hedef_saat}')]")))
                self.tarayici.execute_script("arguments[0].scrollIntoView({block: 'center'});", saat_element)
                self.insan_gibi_bekle(0.5, 1)
                saat_y = saat_element.location['y']
                
                artilar = self.tarayici.find_elements(By.XPATH, "//div[div[text()='+']]")
                
                hedef_buton = None
                for arti in artilar:
                    try:
                        loc = arti.location
                        if abs(loc['x'] - gun_x) < 90 and abs(loc['y'] - saat_y) < 35:
                            hedef_buton = arti
                            break
                    except:
                        continue
                        
                if not hedef_buton:
                    raise Exception("Koordinat kesişiminde uygun '+' kutusu bulunamadı.")
                
                self.insan_gibi_tikla(hedef_buton)
                print(f" {hedef_gun} {hedef_saat} slotuna tıklandı!")
                
                self.insan_gibi_bekle(1.5, 2.5)
                self.bot_dogrulamasi_bekle()
                
                print("Ödemeyi Onayla butonuna basılıyor...")
                onay_butonu = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Ödemeyi Onayla')]")))
                self.insan_gibi_tikla(onay_butonu)
                
                print("Gole gidiyoruz, saha kilitlendi ve ödendi aga!")
                break 
                
            except Exception as e:
                print(f"Hata oluştu veya slot henüz müsait değil, oturum tazeleniyor... Hata: {type(e).__name__}")
                try:
                    self.tarayici.refresh()
                except:
                    print("Oturum kapandı, yeniden başlatılıyor...")
                    try:
                        self.tarayici.quit()
                    except:
                        pass
                    self.baslat_tarayici()
                    self.giris_yap()
                self.insan_gibi_bekle(3, 5)

        time.sleep(5)
        self.tarayici.quit()

if __name__ == "__main__":
    # Öncelik: Environment variable > hedef.json > varsayılan
    hedef_gun = os.environ.get("HEDEF_GUN")
    hedef_saat = os.environ.get("HEDEF_SAAT")

    if not hedef_gun or not hedef_saat:
        try:
            with open("hedef.json", "r", encoding="utf-8") as f:
                hedef = json.load(f)
                hedef_gun = hedef_gun or hedef.get("gun", "Çarşamba")
                hedef_saat = hedef_saat or hedef.get("saat", "20.00 - 21.00")
        except FileNotFoundError:
            hedef_gun = hedef_gun or "Çarşamba"
            hedef_saat = hedef_saat or "20.00 - 21.00"

    ogrenci_no = os.environ.get("OGRENCI_NO", "24023039")
    sifre = os.environ.get("SIFRE", "Prqh975412.")

    print(f"Hedef: {hedef_gun} - {hedef_saat}")
    saha_botum = YtuRezervasyonBotu(ogrenci_no, sifre)
    saha_botum.giris_yap()
    saha_botum.tesis_ve_saat_sec(hedef_gun, hedef_saat)