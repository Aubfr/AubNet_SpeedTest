import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
import threading
import urllib.request
import time
from datetime import datetime
import platform
import re

class TestConnexionApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Test de Connexion Internet")
        self.root.geometry("700x500")
        self.root.configure(bg="white")

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TButton", font=("Helvetica", 12), padding=6)
        style.configure("TLabel", font=("Helvetica", 14), background="white")

        ttk.Label(root, text="Test de Connexion Internet", anchor="center").pack(pady=20)

        frame_btn = ttk.Frame(root)
        frame_btn.pack(pady=10)

        self.btn_start = ttk.Button(frame_btn, text="Lancer le test", command=self.lancer_test)
        self.btn_start.grid(row=0, column=0, padx=20)
        self.btn_quit = ttk.Button(frame_btn, text="Quitter", command=root.quit)
        self.btn_quit.grid(row=0, column=1, padx=20)

        self.text = tk.Text(root, wrap='word', font=("Consolas", 11), bg="#f0f0f0", relief="sunken", bd=4)
        self.text.pack(expand=True, fill='both', padx=20, pady=10)
        self._log("[Info] Cliquez sur 'Lancer le test' pour commencer.\n")

        self.progress = ttk.Progressbar(root, mode='indeterminate')
        self.progress.pack(fill='x', padx=20, pady=(0, 20))

    def _log(self, message):
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.text.config(state='normal')
        self.text.insert('end', f"[{timestamp}] {message}\n")
        self.text.see('end')
        self.text.config(state='disabled')
        self.root.update_idletasks()

    def lancer_test(self):
        self.btn_start.config(state='disabled')
        self.text.config(state='normal')
        self.text.delete(1.0, 'end')
        self.text.config(state='disabled')
        self.progress.start()
        threading.Thread(target=self._executer_test, daemon=True).start()

    def _executer_test(self):
        try:
            self._log("🚀 Début du test...")

            system = platform.system()
            if system == "Windows":
                self._log("📡 Ping vers 8.8.8.8...")

                # Ping Windows - decode en cp850 pour accents
                result = subprocess.run(['ping', '-n', '4', '8.8.8.8'],
                                        capture_output=True,
                                        timeout=10)

                output = result.stdout.decode('cp850', errors='replace')

            else:
                self._log("📡 Ping vers 8.8.8.8...")
                result = subprocess.run(['ping', '-c', '4', '8.8.8.8'],
                                        capture_output=True,
                                        text=True,
                                        timeout=10)
                output = result.stdout or ""

            latence = "Inconnue"
            perte = "Inconnue"

            for line in output.splitlines():
                l = line.lower()
                if "moyenne" in l or "average" in l:
                    match = re.search(r'(\d+)\s*ms', l)
                    if match:
                        latence = match.group(1) + " ms"
                if "perte" in l or "lost" in l:
                    perte = line.strip()

            self._log(f"⏱ Latence moyenne : {latence}")
            self._log(f"📉 Perte de paquets : {perte}")

            self._log("↓ Mesure du débit descendant (~1 Mo)...")
            try:
                start = time.time()
                url_down = "https://speed.cloudflare.com/__down?bytes=1048576"
                req_down = urllib.request.Request(url_down, headers={'User-Agent': 'Mozilla/5.0'})
                with urllib.request.urlopen(req_down, timeout=15) as r:
                    _ = r.read()
                duration_down = time.time() - start
                debit_down = (8 * 1) / duration_down
                self._log(f"📥 Débit descendant : {debit_down:.2f} Mbps")
            except Exception as e:
                self._log(f"⚠ Erreur débit descendant : {e}")

            self._log("↑ Mesure du débit montant (~1 Mo)...")
            try:
                start = time.time()
                url_up = "https://httpbin.org/post"
                data = b"x" * 1048576
                req_up = urllib.request.Request(url_up, data=data, method='POST',
                                               headers={'Content-Type': 'application/octet-stream'})
                with urllib.request.urlopen(req_up, timeout=15) as r:
                    _ = r.read()
                duration_up = time.time() - start
                debit_up = (8 * 1) / duration_up
                self._log(f"📤 Débit montant : {debit_up:.2f} Mbps")
            except Exception as e:
                self._log(f"⚠ Erreur débit montant : {e}")

            self._log("✅ Test terminé.")

        except Exception as e:
            self._log(f"❌ Erreur : {e}")
            messagebox.showerror("Erreur", str(e))
        finally:
            self.progress.stop()
            self.btn_start.config(state='normal')


def main():
    root = tk.Tk()
    app = TestConnexionApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
