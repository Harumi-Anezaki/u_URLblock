[English](../README.md) | [日本語](README_ja.md) | [简体中文](README_zh.md)

# u_URLblock - 商业便携版 (Commercial Portable Edition)

**u_URLblock** 是一款适用于 Windows 平台的商业级高级网络过滤与时间管理应用程序，旨在为您提供高效的上网自律与家长控制解决方案。全面支持 **Google Chrome**（谷歌浏览器）、**Microsoft Edge** 以及 **Mozilla Firefox**（火狐浏览器）三大主流浏览器，提供毫秒级实时 URL 监控与选项卡自动关闭功能。

本软件运行于完全独立、自包含的便携式嵌入式 Python 环境（Embeddable Package）中，无需系统管理员权限（UAC），不修改任何 Windows 注册表项，不污染系统全局环境变量（PATH），实现真正意义上的绿色环保免安装。

---

## 🌟 核心功能与商业特性

1. **多浏览器实时精准监控**:
   - 采用 Windows UI Automation 核心技术，实时捕捉 **Chrome**、**Edge** 及 **Firefox** 中当前活动标签页的 URL 地址，响应速度极快（约 30~50 毫秒）。
2. **双层防护过滤机制**:
   - **每日时长限制**: 针对指定网站（如 YouTube、Instagram、TikTok 等）计算每日累计浏览时间，超时后即刻强制关闭对应网页标签。
   - **绝对黑名单**: 针对预设的不良网页域名或敏感关键词，一旦检测到访问将瞬间拦截并强行关闭窗口。
3. **静默智能启动脚本**:
   - 专属 VBScript 启动器 (`run.vbs`)，在日常开机或运行软件时完全隐藏命令行黑框，实现真正的后台无感运行。
4. **自愈式多进程相互守护架构**:
   - 采用伪装成 Windows 系统服务的后台进程组 (`WinLogonAssist`, `AudioDG_helper`, `FontHost_worker`, `SpoolerSub_helper`) 进行多进程互保（Watchdog）。即使某个进程被意外终止，也能在 1 秒内自动复活，确保防御固若金汤。
5. **现代化 UI 与高DPI缩放支持**:
   - 采用 CustomTkinter 构建科技感十足的深色悬浮仪表盘。内置 **高 DPI 缩放感知** (`SetProcessDpiAwareness`)，在 4K 高分辨率或高缩放显示器上依然保持字体锐利清晰，拒绝模糊。
6. **防篡改加密追踪引擎**:
   - 每日的使用时长数据均经过 Zlib 压缩、循环 XOR 加密以及 Base64 编码，并搭载 SHA-256 与 MD5 双重加密签名核实，彻底杜绝手动修改日志作弊。

---

## 🚀 快速上手指南

### 1. 首次环境初始化（仅需运行一次）
在第一次使用本产品前，请先初始化便携式运行环境：
1. 双击项目根目录下的 **`setup.bat`**。
2. 脚本将全自动下载 Windows 嵌入式 Python 运行库、配置依赖路径、解密 GUI 组件并安装好所有必需模块至独立的 `bin/` 文件夹中。全程自动化，无需人工干预。

### 2. 日常启动与使用
日常使用或需要开机运行应用时：
1. 双击项目根目录下的 **`run.vbs`**。
2. 没有任何命令行黑框闪烁，系统监控后台静默运行，屏幕一角将显示简洁精美的 **Time Keeper** 悬浮悬浮窗。

---

## ⚙️ 规则配置 (`config.json`)

通过使用文本编辑器打开根目录下的 **`config.json`**，您可以自由定制监控规则与限制时长：

```json
{
  "WHITE_LIST": [
    "chiebukuro.yahoo.co.jp"
  ],
  "TIME_LIMITS": {
    "instagram.com": 180,
    "x.com": 180,
    "youtube.com/shorts": 180,
    "tiktok.com": 600,
    "youtube.com": 1800
  },
  "BLOCK_LIST": [
    "crazygames.com",
    "streamtape.com",
    "duckduckgo.com"
  ]
}
```

- **`TIME_LIMITS`**: 配置域名及其每日最高允许浏览时间，单位为 **秒**（例如：`1800` 代表 30 分钟）。
- **`BLOCK_LIST`**: 配置一旦访问即被永久封锁并关闭的网页域名或关键词。
- **`WHITE_LIST`**: 白名单规则，访问此类域名将不计入时长且不被拦截。

---

## 🗑️ 绿色卸载方法

鉴于本产品采用完全独立的便携式架构，卸载过程极其简单纯净：
1. 通过任务管理器结束运行中的相关后台进程，或直接重启计算机。
2. 直接删除整个 `u_URLblock` 文件夹。
3. 您的个人电脑依然保持 100% 纯净，绝无任何注册表残留或垃圾文件。

---

## 📁 商业级目录结构

```text
u_URLblock/
 ├─ setup.bat          # 首次运行化自动化环境构建脚本
 ├─ run.vbs            # 日常使用无黑框静默启动器
 ├─ config.json        # 用户可自定义的监控与拦截规则配置文件
 ├─ README.md          # 英文版产品说明书
 ├─ docs/              # 多语言产品手册目录
 │   ├─ README_ja.md   # 日文版产品说明书
 │   └─ README_zh.md   # 中文版产品说明书 (本文档)
 ├─ bin/               # 自动生成的便携式嵌入式 Python 运行时 (隔离区域)
 └─ core/              # 对终端用户隐藏的底层核心源代码
     ├─ main.pyw       # 应用程序控制器与守护进程管理
     ├─ data_manager.py # 加密存储与配置读写模块
     ├─ ui.py          # CustomTkinter DPI 感知 UI 模块
     ├─ monitor.pyw    # 多浏览器实时 URL 监控核心引擎
     ├─ watcher.pyw    # 进程存活监控与自动复活工作线程
     ├─ system_guard.pyw # WMI/互斥体系统守护卫士
     └─ win_utils.py   # Windows API 底层交互工具集
```
