# 雾港回声

一个使用 Python `tkinter` 编写的中文文字冒险游戏，包含：

- 约一万字体量的原创分支剧情
- 多选项推进与 4 个不同结局
- 完整桌面 UI
- 自生成循环背景音乐
- `PyInstaller` 一键打包为 Windows `exe`

## 运行

```powershell
python .\generate_bgm.py
python .\main.py
```

## 打包

```powershell
.\build.ps1
```

生成后的可执行文件位于：

```text
.\dist\FogHarborEcho.exe
```
