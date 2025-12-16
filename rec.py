import soundcard as sc
import wave
import numpy as np
import threading
import tkinter as tk
from tkinter import messagebox
import datetime

framerate = 16000
channels = 1
blocksize = 1600
datas = []

class SpeakerRecorder:
    def __init__(self, master):
        self.master = master
        master.title("扬声器输出录制")
        master.geometry("300x150")
        
        self.recording = False
        self.mic = None
        self.record_thread = None
        self.file_name = ""
        self.is_topmost = False  # 添加置顶状态变量
        
        # 创建UI元素
        self.status_label = tk.Label(master, text="扬声器输出录制", font=("Arial", 14))
        self.status_label.pack(pady=10)
        
        self.status_text = tk.Label(master, text="准备就绪", fg="blue")
        self.status_text.pack()
        
        # 添加置顶功能复选框
        self.topmost_var = tk.BooleanVar()
        self.topmost_checkbox = tk.Checkbutton(
            master, 
            text="窗口置顶", 
            variable=self.topmost_var, 
            command=self.toggle_topmost
        )
        self.topmost_checkbox.pack()
        
        self.button_frame = tk.Frame(master)
        self.button_frame.pack(pady=10)
        
        self.start_button = tk.Button(self.button_frame, text="开始录制", command=self.start_recording, bg="green", fg="white")
        self.start_button.pack(side=tk.LEFT, padx=5)
        
        self.stop_button = tk.Button(self.button_frame, text="停止录制", command=self.stop_recording, bg="red", fg="white", state=tk.DISABLED)
        self.stop_button.pack(side=tk.LEFT, padx=5)
    
    def toggle_topmost(self):
        """切换窗口置顶状态"""
        self.is_topmost = self.topmost_var.get()
        self.master.attributes('-topmost', self.is_topmost)
    
    def record_audio(self):
        """在单独线程中录制音频"""
        try:
            with sc.get_microphone(id=str(sc.default_speaker().name), include_loopback=True).recorder(
                    samplerate=framerate, blocksize=blocksize, channels=channels) as mic:
                self.mic = mic
                i = 0
                while self.recording:
                    frame = mic.record(numframes=blocksize)
                    if frame.dtype == "float64":
                        datass = (frame * np.iinfo(np.int16).max).astype(np.int16)
                    elif frame.dtype == "float32":
                        datass = (np.array(frame) * 32767).astype(np.int16)
                    else:
                        # 默认处理其他浮点类型
                        datass = (np.array(frame) * 32767).astype(np.int16)
                    data = datass.tobytes()
                    datas.append(data)
                    if i % 10 == 0:  # 减少更新频率
                        # 计算录制时长（秒）= 块数 * 每块样本数 / 采样率
                        duration = i * blocksize / framerate
                        self.status_text.config(text=f"已录制 {duration:.1f}s")
                    i += 1
                    
        except Exception as e:
            messagebox.showerror("错误", f"录制过程中发生错误: {str(e)}")
            self.recording = False
            
        # 录制结束后自动保存
        if datas:
            self.save_recording()
    
    def start_recording(self):
        """开始录制"""
        if not self.recording:
            # 清空之前的数据
            datas.clear()
            
            # 生成带时间戳的文件名
            now = datetime.datetime.now()
            self.file_name = now.strftime("%Y-%m-%d %H%M%S%f")[:-3] + ".wav"
            
            # 更新状态
            self.recording = True
            self.status_text.config(text="正在录制...", fg="red")
            self.start_button.config(state=tk.DISABLED)
            self.stop_button.config(state=tk.NORMAL)
            
            # 在新线程中开始录制
            self.record_thread = threading.Thread(target=self.record_audio, daemon=True)
            self.record_thread.start()
    
    def stop_recording(self):
        """停止录制"""
        if self.recording:
            self.recording = False
            self.status_text.config(text="正在保存文件...", fg="orange")
            
            # 不再等待线程结束，而是让保存在record_audio中自动完成
            # 重置按钮状态
            self.start_button.config(state=tk.NORMAL)
            self.stop_button.config(state=tk.DISABLED)
    
    def save_recording(self):
        """保存录制的音频"""
        try:
            with wave.open(self.file_name, 'wb') as wf:
                wf.setnchannels(channels)
                wf.setsampwidth(2)
                wf.setframerate(framerate)
                for data in datas:
                    wf.writeframes(data)
                    
            self.status_text.config(text=f"已保存为 {self.file_name}", fg="green")
            # 修改这里的消息框提示，不再显示"段"的概念
            total_duration = len(datas) * blocksize / framerate
            messagebox.showinfo("完成", f"文件已保存为 {self.file_name}\n总时长: {total_duration:.1f}s")
        except Exception as e:
            self.status_text.config(text="保存失败", fg="red")
            messagebox.showerror("错误", f"保存文件时出错: {str(e)}")
        finally:
            # 重置状态，允许重新开始录制
            self.master.after(3000, self.reset_status)
    
    def reset_status(self):
        """重置状态为初始状态"""
        self.status_text.config(text="准备就绪", fg="blue")

if __name__ == "__main__":
    root = tk.Tk()
    app = SpeakerRecorder(root)
    root.mainloop()