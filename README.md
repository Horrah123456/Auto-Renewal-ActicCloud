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
- 内置密钥验证机制，防止脚本被随意滥用

## 🚀 如何使用

### 1. 本地运行

1.  **克隆或下载本项目。**
2.  **安装依赖**: 确保你已安装 Python 3.9+。在项目根目录下运行：
    ```bash
    pip install -r requirements.txt
    ```
3.  **创建配置文件**: 将 `config.json.example` 文件重命名为 `config.json`。
4.  **填写配置**: 打开 `config.json` 文件，填入你自己的个人信息。
5.  **运行脚本**:
    ```bash
    python main.py
    ```

### 2. 使用 GitHub Actions 部署 (推荐)

1.  **Fork 本项目** 到你自己的 GitHub 账户。
2.  **将你的仓库设置为私有 (Private)**：进入你 Fork 后的仓库页面，点击 **Settings**，在 **General** 页面的最下方找到 "Danger Zone"，选择 "Change repository visibility" 将其设为私有。这是为了保护您的Secrets安全。
3.  **配置仓库 Secrets (关键步骤)**：
    - 进入你的私有仓库页面，点击 **Settings** -> **Secrets and variables** -> **Actions**。
    - 点击 **"New repository secret"** 按钮，逐一添加以下 **6** 个Secrets。请确保名称完全匹配。

    ```
    USERNAME         : 官网用户名
    PASSWORD         : 官网密码
    PRODUCT_ID       : 机器ID
    BOT_TOKEN        : TG_BOT API
    CHAT_ID          : TG_User ID
    SCRIPT_SECRET_KEY: Guess
    ```

4.  **运行工作流**:
    - 配置好所有Secrets后，进入仓库的 **Actions** 标签页。
    - 在左侧选择 **"Auto Renewal Bot"** 工作流。
    - 点击 **"Run workflow"** 按钮来手动触发一次，以测试所有配置是否正确。
    - 之后，工作流将根据 `.github/workflows/renewal_workflow.yml` 文件中 `schedule` 的设置（默认为每4天）自动运行。

## ⚠️ 注意

- 本脚本按原样提供，请自行承担使用风险。
- 切勿将你的 `config.json` 文件或任何包含敏感信息的文件上传到公共仓库。