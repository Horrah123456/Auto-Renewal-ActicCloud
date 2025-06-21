# 自动续期机器人 (Auto Renewal Bot)

这是一个使用 Python 和 Selenium 实现的自动化脚本，旨在自动登录指定网站，为产品进行续期，并通过 Telegram Bot 发送任务执行结果通知。

## ✨ 功能特性

- 自动登录网站
- 直接导航到指定产品页面
- 智能判断是否需要续期
- 执行续期操作
- 通过对比日期验证续期结果
- 将详细的执行日志保存到本地 `log/` 文件夹
- 通过 Telegram Bot 发送实时成功或失败通知

## 🚀 如何使用

### 1. 本地运行

1.  **克隆或下载本项目。**
2.  **安装依赖**: 确保你已安装 Python 3.9+。在项目根目录下运行：
    ```bash
    pip install -r requirements.txt
    ```
3.  **创建配置文件**: 将 `config.json.example` 文件重命名为 `config.json`。
4.  **填写配置**: 打开 `config.json` 文件，填入你自己的个人信息（网站用户名/密码、产品ID、Telegram Bot Token 和 Chat ID）。
5.  **运行脚本**:
    ```bash
    python main.py
    ```

### 2. 使用 GitHub Actions 部署 (推荐)

1.  **Fork 本项目** 到你自己的 GitHub 账户，并确保你的仓库是 **私有的 (Private)**。
2.  在你的私有仓库中，进入 **Settings -> Secrets and variables -> Actions**。
3.  点击 **"New repository secret"**，并添加以下5个Secrets，值来自于你的 `config.json`：
    - `USERNAME`
    - `PASSWORD`
    - `PRODUCT_ID`
    - `BOT_TOKEN`
    - `CHAT_ID`
4.  本项目中的 `.github/workflows/renewal_workflow.yml` 文件已配置好。它会根据你设定的 `schedule` (默认为每4天) 自动运行。你也可以在仓库的 **Actions** 标签页手动触发。

## ⚠️ 注意

- 本脚本按原样提供，请自行承担使用风险。
- 切勿将你的 `config.json` 文件或任何包含敏感信息的文件上传到公共仓库。