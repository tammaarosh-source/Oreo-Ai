import speech_recognition as sr
import pyttsx3
from googlesearch import search
import requests
from bs4 import BeautifulSoup
import time
import sys

NOME_AI = "Oreo"
LINGUA = "it-IT"
VELOCITA_VOCE = 180
VOLUME = 1.0

class Oreo:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.engine = pyttsx3.init()
        self.engine.setProperty('rate', VELOCITA_VOCE)
        self.engine.setProperty('volume', VOLUME)
        
        voci = self.engine.getProperty('voices')
        for voce in voci:
            if "italian" in voce.name.lower() or "italiano" in voce.name.lower():
                self.engine.setProperty('voice', voce.id)
                break

        print(f"\n{'='*50}")
        print(f"  {NOME_AI} è pronto! 🍪")
        print(f"{'='*50}\n")

    def parla(self, testo):
        print(f"\n{NOME_AI}: {testo}")
        self.engine.say(testo)
        self.engine.runAndWait()

    def ascolta(self):
        with sr.Microphone() as source:
            print("\n🎤 Sto ascoltando... (parla pure)")
            self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
            try:
                audio = self.recognizer.listen(source, timeout=6, phrase_time_limit=10)
                print("🔄 Riconoscimento in corso...")
                testo = self.recognizer.recognize_google(audio, language=LINGUA)
                print(f"Tu (voce): {testo}")
                return testo
            except sr.WaitTimeoutError:
                self.parla("Non ho sentito niente. Riprova.")
                return None
            except sr.UnknownValueError:
                self.parla("Non ho capito bene. Puoi ripetere?")
                return None
            except sr.RequestError:
                self.parla("Errore di connessione al servizio di riconoscimento vocale.")
                return None

    def cerca_google(self, query, num_risultati=5):
        print(f"\n🔍 Cerco: '{query}' ...")
        risultati = []
        try:
            for url in search(query, num_results=num_risultati, lang="it"):
                risultati.append(url)
                if len(risultati) >= num_risultati:
                    break
        except Exception as e:
            print(f"Errore ricerca: {e}")
            return None
        return risultati

    def estrai_contenuto_pagina(self, url):
        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }
            response = requests.get(url, headers=headers, timeout=4)
            soup = BeautifulSoup(response.text, "html.parser")

            titolo = soup.title.string.strip() if soup.title else "Senza titolo"
            descrizione = ""
            meta = soup.find("meta", attrs={"name": "description"})
            if meta and meta.get("content"):
                descrizione = meta["content"].strip()
            else:
                for p in soup.find_all("p"):
                    testo = p.get_text().strip()
                    if len(testo) > 80:
                        descrizione = testo[:300] + "..."
                        break

            return {
                "titolo": titolo,
                "descrizione": descrizione,
                "url": url
            }
        except Exception:
            return None

    def trova_risposta_migliore(self, query):
        urls = self.cerca_google(query, num_risultati=6)
        if not urls:
            return "Non sono riuscito a trovare risultati."

        priorita = []
        normali = []

        for url in urls:
            if "wikipedia.org" in url:
                priorita.insert(0, url)
            elif any(x in url for x in [".gov", ".edu", "treccani.it", "britannica.com"]):
                priorita.append(url)
            else:
                normali.append(url)

        candidati = priorita + normali

        for url in candidati[:4]:
            contenuto = self.estrai_contenuto_pagina(url)
            if contenuto and contenuto["descrizione"]:
                risposta = (
                    f"{contenuto['titolo']}\n\n"
                    f"{contenuto['descrizione']}\n\n"
                    f"Fonte: {contenuto['url']}"
                )
                return risposta

        return "Ho trovato questi risultati:\n" + "\n".join(candidati[:3])

    def elabora_domanda(self, domanda):
        if not domanda or len(domanda.strip()) < 2:
            self.parla("Non ho capito la domanda.")
            return

        domanda = domanda.strip().lower()

        if any(x in domanda for x in ["esci", "chiudi", "stop", "basta", "arrivederci"]):
            self.parla("Ciao! Alla prossima.")
            sys.exit(0)

        if any(x in domanda for x in ["chi sei", "come ti chiami", "presentati"]):
            self.parla(f"Ciao! Sono {NOME_AI}, il tuo assistente personale. Posso cercare qualsiasi cosa su Google per te.")
            return

        inizio = time.time()
        risposta = self.trova_risposta_migliore(domanda)
        tempo = round(time.time() - inizio, 1)

        print(f"\n⏱ Tempo di risposta: {tempo} secondi")
        self.parla(risposta)

    def avvia(self):
        self.parla(f"Ciao! Sono {NOME_AI}. Dimmi pure cosa vuoi cercare.")

        while True:
            print("\n" + "-"*50)
            print("Scegli modalità:")
            print("1. Chat (testo)")
            print("2. Voce")
            print("3. Esci")
            
            scelta = input("\nScelta (1/2/3): ").strip()

            if scelta == "1":
                domanda = input("\nTu: ").strip()
                self.elabora_domanda(domanda)

            elif scelta == "2":
                domanda = self.ascolta()
                if domanda:
                    self.elabora_domanda(domanda)

            elif scelta == "3":
                self.parla("Ciao! A presto.")
                break
            else:
                print("Scelta non valida.")

if __name__ == "__main__":
    oreo = Oreo()
    oreo.avvia()