# 扬声器输出录制工具

这是一个基于 Python 的图形界面应用程序，用于录制计算机扬声器播放的声音。

## 功能特点

- 录制系统扬声器输出（内录）
- 图形用户界面操作
- 自动生成带有时间戳的文件名
- 实时显示录制时长
- 支持多次录制
- 可选窗口置顶功能

## 环境要求

- Python 3.6 或更高版本
- 支持 loopback recording 的操作系统（Windows 8+/macOS/Linux）

## 安装依赖

```bash
pip install -r requirements.txt
```

## 打包为可执行文件

要将程序打包为 Windows 可执行文件 (.exe)，请按以下步骤操作：

1. 安装 PyInstaller：
```bash
pip install pyinstaller
```

2. 使用以下命令打包程序：
```bash
pyinstaller --noconsole --onefile rec.py
```

或者使用优化版本减小文件大小：
```bash
pyinstaller --noconsole --onefile --exclude-module tkinter.test --exclude-module tkinter.dnd --exclude-module numpy.testing rec.py
```

进一步优化（需要UPX）：
```bash
pyinstaller --noconsole --onefile --strip --exclude-module tkinter.test --exclude-module tkinter.dnd --exclude-module numpy.testing rec.py
```

参数说明：
- `--noconsole`: 不显示控制台窗口（适用于GUI程序）
- `--onefile`: 打包成单个exe文件
- `--strip`: 移除调试符号以减小文件大小
- `--exclude-module`: 排除不必要的模块以减小文件大小（注意：tkinter 是必需的，不能排除）

3. 打包完成后，可在 `dist` 文件夹中找到生成的 exe 文件

## 使用说明

1. 运行程序：
```bash
python rec.py
```

或者双击打包好的 exe 文件运行

2. 点击"开始录制"按钮开始录制系统声音
3. 点击"停止录制"按钮结束录制并自动保存文件
4. 录制的文件将保存在程序同级目录下，文件名为 `年-月-日 时分秒毫秒.wav` 格式

## 界面说明

- **设备信息区域**：显示当前默认音频设备名称和最大通道数
- **录制设置区域**：可选择采样率和设置窗口是否置顶
- **控制按钮区域**：开始录制和结束录制按钮
- **状态区域**：显示当前操作状态（就绪、正在录制、正在保存、保存完成）
- **进度区域**：实时显示已录制时长（格式：已录制 X.Xs）
- **文件操作区域**：可选择自定义保存位置，或使用自动生成的文件名

## 注意事项

- 该程序录制的是系统扬声器输出的声音，而非麦克风输入
- 文件保存格式为 WAV 格式
- 文件名自动以录制开始时间命名，避免重复文件名冲突
- 程序支持连续多次录制操作
- 打包后的 exe 文件无需安装和管理员权限即可运行
- 程序默认窗口置顶，可根据需要取消置顶选项

## 依赖库说明

- `soundcard`：用于音频录制的核心库，支持 loopback recording
- `sounddevice`：用于查询音频设备信息和支持的采样率
- `numpy`：用于音频数据处理
- `tkinter`：用于构建图形用户界面
