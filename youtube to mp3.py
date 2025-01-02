import os
from tkinter import Tk, Text, Label, Button, filedialog, Scrollbar, messagebox, StringVar
from tkinter.ttk import Progressbar
from pytubefix import YouTube
from moviepy.audio.io.AudioFileClip import AudioFileClip

def download_videos():
    urls = url_text.get("1.0", "end").strip().split("\n")
    output_dir = output_dir_var.get()

    if not urls or not output_dir:
        messagebox.showerror("에러", "정확한 URL과 디렉토리를 입력하십시오")
        return

    total_urls = len([url for url in urls if url.strip()])
    progress_bar["maximum"] = total_urls
    progress_bar["value"] = 0

    for index, url in enumerate(urls):
        if not url.strip():
            continue
        try:
            # Display the currently downloading file
            status_label.config(text=f"처리중 : {url}")
            root.update_idletasks()

            yt = YouTube(url.strip())
            audio_stream = yt.streams.filter(only_audio=True).first()

            # Update status with the file title
            current_file_label.config(text=f"다운로드중 : {yt.title}")
            root.update_idletasks()

            output_file = audio_stream.download(output_dir)

            base, ext = os.path.splitext(output_file)
            mp3_file = base + ".mp3"

            current_file_label.config(text=f"MP3 변환중 : {yt.title}")
            root.update_idletasks()

            with AudioFileClip(output_file) as audio_clip:
                audio_clip.write_audiofile(mp3_file)

            os.remove(output_file)

            # Increment progress bar
            progress_bar["value"] = index + 1
            root.update_idletasks()

        except Exception as e:
            messagebox.showerror("에러", f"URL 오류: {url}\nError: {e}")
    
    current_file_label.config(text="")
    status_label.config(text="다운로드 완료!")
    progress_bar["value"] = total_urls
    messagebox.showinfo("완료", "다운로드 완")

def select_output_dir():
    dir_path = filedialog.askdirectory()
    if dir_path:
        output_dir_var.set(dir_path)

# GUI Setup
root = Tk()
root.title("유튜브 음원 변환")

# URL Input Section
Label(root, text="URL을 입력하십시오 (한줄에 하나씩):").pack(pady=5)
url_text = Text(root, width=60, height=10)
url_text.pack(padx=10, pady=5)

# Scrollbar for URLs
scrollbar = Scrollbar(root, command=url_text.yview)
scrollbar.pack(side="right", fill="y")
url_text.config(yscrollcommand=scrollbar.set)

# Output Directory Section
output_dir_var = StringVar()
Label(root, text="내보낼 파일 위치 :").pack(pady=5)
output_dir_label = Label(root, textvariable=output_dir_var, relief="sunken", width=50)
output_dir_label.pack(pady=5)
Button(root, text="파일 위치 선택", command=select_output_dir).pack(pady=5)

# Progress Bar Section
progress_bar = Progressbar(root, orient="horizontal", length=400, mode="determinate")
progress_bar.pack(pady=10)

# Current File Name
current_file_label = Label(root, text="", fg="green")
current_file_label.pack(pady=5)

# Action Buttons
Button(root, text="다운로드 시작", command=download_videos).pack(pady=10)

# Status Section
status_label = Label(root, text="", fg="blue")
status_label.pack(pady=5)

# Run the application
root.mainloop()