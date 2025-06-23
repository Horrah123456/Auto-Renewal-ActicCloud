# ArcticCloud 自动续期机器人

这是一个使用 Python 和 Selenium 实现的自动化脚本，旨在自动登录指定网站，为多个产品进行续期，并通过 Telegram Bot 发送任务执行结果通知。

## ✨ 功能特性

- **多产品支持**: 一次登录，循环处理账户下的多个产品。
- **智能判断**: 自动分析产品到期时间，决定续期操作的报告类型。
- **状态验证**: 通过对比操作前后的到期日期，确保续期结果真实有效。
- **实时通知**: 通过 Telegram Bot 发送图文并茂、格式清晰的执行报告。
- **安全设计**:
    - 使用 GitHub Secrets 存储凭证，与代码完全分离。
    - 内置密钥验证机制，防止项目被随意滥用。
- **云端原生**: 基于 GitHub Actions，无需自备服务器，实现云端全自动定时执行。

## ⚙️ 准备工作

在开始部署之前，请确保您已拥有：
1.  一个 **GitHub 账户**。
2.  一个 **Telegram 账户**。
3.  目标网站（例如 ArcticCloud）的**账户**和需要续期的**产品ID**。

## 🚀 部署指南

请严格按照以下步骤操作，即可拥有一个为您7x24小时工作的自动化机器人。

### 第一步: 创建 Telegram Bot (`获取 Token 和 Chat ID`)

我们需要创建一个机器人来为您发送通知。

1.  在Telegram中，搜索并打开官方机器人 **`@BotFather`**。
2.  发送 `/newbot` 命令，然后按照提示为您的机器人取一个名字（如 `我的续期助手`）和一个独一无二的用户名（必须以`bot`结尾，如 `MyRenewalHelper_bot`）。
3.  `BotFather` 会回复您一长串以数字开头的 **Token**。这就是您的 `BOT_TOKEN`，请复制并妥善保管。
4.  接下来，搜索并打开 **`@userinfobot`**。
5.  发送 `/start`，它会立刻回复您的信息，第一行的 **`Id:`** 后面的那串数字，就是您的 `CHAT_ID`。
6.  **重要**: 回到您刚刚创建的机器人对话框，给它发送一条 `/start` 消息，以“激活”它，否则它无法主动给您发送消息。

### 第二步: Fork 项目(`创建你的代码仓库`)

1.  点击本项目右上角的 **"Fork"** 按钮，将项目复制到您自己的GitHub账户下。


### 第三步: 配置仓库 Secrets (`为机器人注入灵魂`)

这是最关键的步骤，我们将把所有敏感信息安全地存放在GitHub的“保险箱”中。

1.  在您的**私有仓库**页面，点击 **"Settings"** -> **"Secrets and variables"** -> **"Actions"**。
2.  点击绿色的 **"New repository secret"** 按钮，逐一添加以下 **2** 个Secrets。

---
**`ACCOUNT_CONFIG_JSON`**

* **Name**: `ACCOUNT_CONFIG_JSON`
* **Secret**: (将下面JSON内容根据您的信息修改后，完整粘贴进去)

    ```json
    {
      "username": "your_email@example.com",
      "password": "your_super_secret_password",
      "product_ids": [
        "999",
        "975",
        "1001"
      ],
      "script_secret_key": "BearBoss Is Watching You"
    }
    ```

---
**`TELEGRAM_CONFIG_JSON`**

* **Name**: `TELEGRAM_CONFIG_JSON`
* **Secret**: (将下面JSON内容根据您的信息修改后，完整粘贴进去)

    ```json
    {
      "bot_token": "123456:ABC-DEF1234567890",
      "chat_id": "123456789"
    }
    ```


### 第四步: 运行与监控 (`点火与观察`)

1.  配置好所有Secrets后，进入仓库的 **"Actions"** 标签页。
2.  在左侧选择 **"Auto Renewal Bot"** 工作流。
3.  点击 **"Run workflow"** 按钮来手动触发一次，以测试所有配置是否正确。
4.  您可以点击正在运行的任务，实时查看日志。片刻之后，您的Telegram就会收到来自机器人的通知。
5.  测试成功后，无需再做任何事。工作流将根据 `.github/workflows/renewal_workflow.yml` 文件中 `schedule` 的设置（默认为每4天）自动运行。

## ⚠️ 注意

- 本脚本按原样提供，请自行承担使用风险。
- 切勿将您的真实配置信息以任何形式上传到公共仓库。