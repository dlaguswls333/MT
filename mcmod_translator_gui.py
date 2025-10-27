import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import threading, json, os, time
import google.generativeai as genai

# API 키 설정
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

def translate_text_gpt(text, target_lang="ko"):
    """Google Gemini API를 사용한 번역"""
    if not text.strip():
        return text

    prompt = f"Translate this Minecraft mod text to {target_lang}. Keep item and block names natural for Minecraft players.\n\n{text}"

    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        print(f"번역 실패: {e}")
        return text


def translate_lang_file(input_path, output_path, target_lang="ko", log_callback=None, progress_callback=None):
    with open(input_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    translated = {}
    total = len(data)
    for i, (key, value) in enumerate(data.items(), start=1):
        translated[key] = translate_text_gpt(value, target_lang)
        if log_callback:
            log_callback(f"{key} → {translated[key]}")
        if progress_callback:
            progress_callback(i / total * 100)  # 진행률 % 업데이트
        time.sleep(0.2)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(translated, f, ensure_ascii=False, indent=4)


class TranslatorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Minecraft Mod Translator")
        self.root.geometry("500x450")

        self.folder_path = tk.StringVar()
        self.lang = tk.StringVar(value="ko")

        tk.Label(root, text="입력 폴더 선택:").pack(pady=5)
        tk.Entry(root, textvariable=self.folder_path, width=40).pack()
        tk.Button(root, text="폴더 선택", command=self.choose_folder).pack(pady=3)

        tk.Label(root, text="번역 언어 코드 (예: ko, ja, fr):").pack(pady=5)
        tk.Entry(root, textvariable=self.lang, width=10).pack()

        tk.Button(root, text="번역 시작", command=self.start_translation).pack(pady=10)

        # 로그 박스
        self.log_box = tk.Text(root, height=12, width=60)
        self.log_box.pack(pady=5)

        # 진행률 바
        self.progress = ttk.Progressbar(root, length=400, mode="determinate")
        self.progress.pack(pady=10)

    def log(self, message):
        self.log_box.insert(tk.END, message + "\n")
        self.log_box.see(tk.END)

    def update_progress(self, percent):
        self.progress['value'] = percent
        self.root.update_idletasks()

    def choose_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.folder_path.set(folder)

    def start_translation(self):
        folder = self.folder_path.get()
        if not folder:
            messagebox.showwarning("경고", "폴더를 먼저 선택하세요.")
            return
        self.log(f"번역 시작: {folder}")
        self.progress['value'] = 0
        threading.Thread(target=self.run_translation, daemon=True).start()

    def run_translation(self):
        folder = self.folder_path.get()
        for file_name in os.listdir(folder):
            if file_name.endswith(".json") and "en_us" in file_name:
                input_path = os.path.join(folder, file_name)
                output_path = os.path.join(folder, file_name.replace("en_us", f"{self.lang.get()}_kr"))
                self.log(f"🔄 {file_name} 번역 중...")
                translate_lang_file(
                    input_path,
                    output_path,
                    self.lang.get(),
                    log_callback=self.log,
                    progress_callback=self.update_progress
                )
        self.log("번역 완료!")
        self.progress['value'] = 100


if __name__ == "__main__":
    root = tk.Tk()
    app = TranslatorApp(root)
    root.mainloop()
