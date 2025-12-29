import soundcard as sc
import sounddevice as sd
import numpy as np
import wave
import datetime
import threading
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os

class SpeakerRecorderGUI:
    def __init__(self, master):
        self.master = master
        master.title("扬声器录制工具")
        master.geometry("400x340")
        # 窗口置顶默认开启
        master.attributes('-topmost', True)  
        
        self.recording = False
        self.record_thread = None
        self.recorded_data = []
        self.output_file = None
        self.start_time = None
        
        # 获取默认扬声器
        try:
            self.speaker = sc.default_speaker()
            self.speaker_name = self.speaker.name
            self.channels = min(2, self.speaker.channels)
        except Exception as e:
            messagebox.showerror("错误", f"无法获取默认扬声器: {e}")
            self.speaker = None
            return
            
        # 支持的采样率 (使用 sounddevice 方式获取)
        self.supported_rates = self.detect_supported_rates_with_sounddevice()
        
        self.create_widgets()
        
    def detect_supported_rates_with_sounddevice(self):
        """使用 sounddevice 方式检测支持的采样率"""
        try:
            # 获取默认音频设备信息
            devices = sd.query_devices()
            default_device_idx = sd.default.device[1]  # 默认输出设备索引
            default_device = devices[default_device_idx]
            
            # 获取通道数
            channels = default_device['max_output_channels']
            
            # 常见的采样率列表
            common_rates = [8000, 11025, 16000, 22050, 32000, 44100, 48000, 88200, 96000, 176400, 192000, 352800, 384000]
            
            # 检查设备支持的采样率
            supported_samplerates = []
            for rate in common_rates:
                try:
                    sd.check_output_settings(device=default_device_idx, samplerate=rate, channels=min(channels, 2))
                    supported_samplerates.append(rate)
                except Exception:
                    # 不支持的采样率
                    pass
                    
            return supported_samplerates if supported_samplerates else [44100, 48000]
        except Exception as e:
            # 出现异常时返回默认值
            return [44100, 48000]
    
    def create_widgets(self):
        """创建界面元素"""
        # 主框架
        main_frame = ttk.Frame(self.master, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 设备信息
        device_frame = ttk.LabelFrame(main_frame, text="设备信息", padding="5")
        device_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Label(device_frame, text=f"设备名称: {self.speaker_name}").grid(row=0, column=0, sticky=tk.W)
        ttk.Label(device_frame, text=f"最大通道数: {self.channels}").grid(row=1, column=0, sticky=tk.W)
        
        # 录制设置
        settings_frame = ttk.LabelFrame(main_frame, text="录制设置", padding="5")
        settings_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # 采样率选择
        ttk.Label(settings_frame, text="采样率:").grid(row=0, column=0, sticky=tk.W)
        self.rate_var = tk.StringVar(value=str(self.supported_rates[0]) if self.supported_rates else "48000")
        self.rate_combo = ttk.Combobox(settings_frame, textvariable=self.rate_var, 
                                      values=[str(rate) for rate in self.supported_rates],
                                      state="readonly", width=15)
        self.rate_combo.grid(row=0, column=1, sticky=tk.W, padx=(5, 0))
        
        # 窗口置顶选项，默认选中
        self.topmost_var = tk.BooleanVar(value=True)
        self.topmost_check = ttk.Checkbutton(settings_frame, text="窗口置顶", variable=self.topmost_var, 
                                           command=self.toggle_topmost)
        self.topmost_check.grid(row=0, column=2, padx=(20, 0))
        
        # 控制按钮
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=2, column=0, columnspan=2, pady=(0, 10))
        
        self.start_button = ttk.Button(button_frame, text="开始录制", command=self.start_recording)
        self.start_button.grid(row=0, column=0, padx=(0, 5))
        
        self.stop_button = ttk.Button(button_frame, text="结束录制", command=self.stop_recording, state=tk.DISABLED)
        self.stop_button.grid(row=0, column=1, padx=(5, 0))
        
        # 状态显示
        status_frame = ttk.LabelFrame(main_frame, text="状态", padding="5")
        status_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        self.status_var = tk.StringVar(value="就绪")
        self.status_label = ttk.Label(status_frame, textvariable=self.status_var)
        self.status_label.grid(row=0, column=0, sticky=tk.W)
        
        # 进度显示
        progress_frame = ttk.Frame(main_frame)
        progress_frame.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        self.progress_var = tk.StringVar(value="已录制 0.0s")
        self.progress_label = ttk.Label(progress_frame, textvariable=self.progress_var)
        self.progress_label.grid(row=0, column=0, sticky=tk.W)
        
        # 文件操作
        file_frame = ttk.Frame(main_frame)
        file_frame.grid(row=5, column=0, columnspan=2, pady=(0, 10))
        
        ttk.Button(file_frame, text="选择保存位置", command=self.select_save_location).grid(row=0, column=0, padx=(0, 5))
        self.file_var = tk.StringVar(value="自动生成")
        ttk.Label(file_frame, textvariable=self.file_var, foreground="gray").grid(row=0, column=1)
        
        # 配置网格权重
        self.master.columnconfigure(0, weight=1)
        self.master.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
    def toggle_topmost(self):
        """切换窗口置顶状态"""
        self.master.attributes('-topmost', self.topmost_var.get())
        
    def select_save_location(self):
        """选择保存位置"""
        file_path = filedialog.asksaveasfilename(
            defaultextension=".wav",
            filetypes=[("WAV files", "*.wav"), ("All files", "*.*")],
            title="选择保存位置"
        )
        if file_path:
            self.output_file = file_path
            self.file_var.set(os.path.basename(file_path))
        
    def record_audio(self):
        """在独立线程中录制音频"""
        try:
            samplerate = int(self.rate_var.get())
            blocksize = samplerate  # 1秒的块大小
            
            self.status_var.set("正在录制...")
            self.recorded_data = []  # 清理之前的录制数据
            self.start_time = datetime.datetime.now()
            
            # 获取回放设备的麦克风接口
            microphone = sc.get_microphone(id=str(self.speaker_name), include_loopback=True)
            
            with microphone.recorder(samplerate=samplerate, blocksize=blocksize, channels=self.channels) as recorder:
                while self.recording:
                    data = recorder.record(numframes=blocksize)
                    self.recorded_data.append(data.copy())
                    # 更新录制时长
                    elapsed = (datetime.datetime.now() - self.start_time).total_seconds()
                    self.progress_var.set(f"已录制 {elapsed:.1f}s")
                    
            # 保存录制的数据
            if self.recorded_data and self.recording == False:  # 确保是正常停止而不是异常退出
                self.save_recording(samplerate)
                
        except Exception as e:
            self.recording = False
            self.update_ui_state()
            messagebox.showerror("错误", f"录制过程中出现错误: {e}")
            
    def save_recording(self, samplerate):
        """保存录制的音频"""
        try:
            self.status_var.set("正在保存...")
            
            # 生成文件名
            if not self.output_file:
                timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                output_file = f"speaker_recording_{timestamp}.wav"
            else:
                output_file = self.output_file
                
            # 合并所有数据
            full_data = np.concatenate(self.recorded_data, axis=0)
            
            # 转换数据格式
            if full_data.dtype == np.float64:
                audio_data = (full_data * np.iinfo(np.int16).max).astype(np.int16)
            elif full_data.dtype == np.float32:
                audio_data = (full_data * 32767).astype(np.int16)
            else:
                audio_data = full_data.astype(np.int16)
            
            # 保存为WAV文件
            with wave.open(output_file, 'wb') as wf:
                wf.setnchannels(self.channels)
                wf.setsampwidth(2)
                wf.setframerate(samplerate)
                wf.writeframes(audio_data.tobytes())
                
            self.status_var.set("保存完成")
            messagebox.showinfo("完成", f"文件已保存为:\n{output_file}")
            
        except Exception as e:
            self.status_var.set("保存失败")
            messagebox.showerror("错误", f"保存文件时出现错误: {e}")
        finally:
            # 清理临时变量
            self.recorded_data = []
            self.output_file = None
            self.start_time = None
            # 重置状态显示
            self.progress_var.set("已录制 0.0s")
            
    def start_recording(self):
        """开始录制"""
        if not self.recording:
            self.recording = True
            self.update_ui_state()
            
            # 在新线程中开始录制
            self.record_thread = threading.Thread(target=self.record_audio, daemon=True)
            self.record_thread.start()
            
    def stop_recording(self):
        """结束录制"""
        if self.recording:
            self.recording = False
            self.update_ui_state()
            
    def update_ui_state(self):
        """更新界面状态"""
        if self.recording:
            self.start_button.config(state=tk.DISABLED)
            self.stop_button.config(state=tk.NORMAL)
            self.rate_combo.config(state=tk.DISABLED)
            self.topmost_check.config(state=tk.DISABLED)
        else:
            self.start_button.config(state=tk.NORMAL)
            self.stop_button.config(state=tk.DISABLED)
            self.rate_combo.config(state="readonly")
            self.topmost_check.config(state=tk.NORMAL)
            # 重置状态显示
            self.progress_var.set("已录制 0.0s")

def main():
    root = tk.Tk()
    app = SpeakerRecorderGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
