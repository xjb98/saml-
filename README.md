# saml单点登录登出
# Azure AD SAML 登录/登出示例

这是一个使用 Flask 和 python3-saml 库实现 SAML 单点登录 (SSO) 和单点登出 (SLO) 的示例应用程序，与 Azure Active Directory (Azure AD) 集成。  

## 功能  

-   通过 SAML 与 Azure AD 进行单点登录。  
-   显示登录用户的 SAML 属性信息。  
-   实现单点登出。  

## 先决条件  

-   Python 3.6 或更高版本  
-   pip (Python 包管理器)  
-   OpenSSL (用于生成 SSL 证书和密钥)  
-   访问 Azure AD 租户并具有创建应用程序注册的权限  

## 设置步骤  

1.  **克隆或下载项目代码。** (假设你已经在本地拥有代码)  

2.  **安装 Python 依赖。**  

    ```bash  
    pip install Flask python3-saml python-dotenv PyOpenSSL  
    ```  

3.  **生成自签名 SSL 证书和私钥。**  

    你的应用程序需要运行在 HTTPS 上，以便接收来自 Azure AD 的 SAML 响应。你需要一对证书和私钥。  

    使用 OpenSSL（可以在 Git Bash 中运行）：  

    ```bash  
    mkdir saml  
    openssl genrsa -out saml/sp.key 2048  
    openssl req -new -x509 -key saml/sp.key -out saml/sp.cer -days 365 -nodes  
    ```  

    在生成证书时，会要求输入一些信息，可以按需填写或留空。确保 `saml` 目录下生成了 `sp.key` 和 `sp.cer` 文件。  

4.  **配置 SAML 设置 (`saml/settings.json`)。**  

    编辑 `saml/settings.json` 文件，根据你的环境和 Azure AD 应用程序注册信息进行更新。**特别注意，需要将 `idp` 部分的占位符替换为你自己的 Azure AD 应用的实际信息，并将 `sp` 部分的 URL 根据你的应用部署地址进行调整（如果不是 `https://localhost:5000`）。**  

    -   **`sp` (服务提供者) 配置：**  
        -   `entityId`: 你的 SP 实体 ID，通常是一个唯一的标识符，例如 `"http://localhost:5000/metadata"`。根据需要调整。  
        -   `assertionConsumerService.url`: 接收 SAML 响应的 URL。**必须使用 HTTPS**。设置为 `"https://localhost:5000/saml/acs"`。根据你的部署地址调整。  
        -   `singleLogoutService.url`: 处理单点登出的 URL。设置为 `"https://localhost:5000/saml/sls"`。根据你的部署地址调整。  
        -   `x509cert` 和 `privateKey`: 指向你刚刚生成的证书和私钥文件路径 (`"saml/sp.cer"` 和 `"saml/sp.key"`)。  

    -   **`idp` (身份提供者) 配置：**  
        -   `entityId`: Azure AD 的 IdP 实体 ID。**将占位符 `YOUR_IDP_ENTITY_ID_FROM_AZURE_AD` 替换为你的 Azure AD 应用程序注册中获取的实体 ID。**  
        -   `singleSignOnService.url`: Azure AD 的 SSO 登录 URL。**将占位符 `YOUR_IDP_SSO_URL_FROM_AZURE_AD` 替换为你的 Azure AD 应用程序注册中获取的 SSO URL。**  
        -   `singleLogoutService.url`: Azure AD 的 SLO 登出 URL。**将占位符 `YOUR_IDP_SLO_URL_FROM_AZURE_AD` 替换为你的 Azure AD 应用程序注册中获取的 SLO URL。**  
        -   `x509cert`: Azure AD 的签名证书内容。**将占位符 `YOUR_IDP_CERTIFICATE_CONTENT_FROM_AZURE_AD` 替换为从 Azure AD 下载的 Base64 格式证书的全部内容（包括 BEGIN/END 行）。**  

5.  **在 Azure AD 中配置应用程序注册。**  

    在 Azure 门户中为你的应用程序创建一个新的"企业应用程序"或使用现有的。  

    -   配置 SAML 单点登录。  
    -   **标识符 (Entity ID):** 设置为 `saml/settings.json` 中 `sp.entityId` 的值，例如 `http://localhost:5000/metadata`。  
    -   **回复 URL (Assertion Consumer Service URL):** 设置为 `saml/settings.json` 中 `sp.assertionConsumerService.url` 的值，**必须是 HTTPS**，例如 `https://localhost:5000/saml/acs`。  
    -   **注销 URL (Logout URL):** 设置为 `saml/settings.json` 中 `sp.singleLogoutService.url` 的值，例如 `https://localhost:5000/saml/sls`。  
    -   **SAML 签名证书：** 下载 Base64 格式的证书，并将其内容更新到 `saml/settings.json` 的 `idp.x509cert` 字段。  
    -   **设置用户属性和声明 (Attributes & Claims):** 确保 Azure AD 配置为在 SAML 响应中包含你的应用程序所需的属性，例如 `objectidentifier`、`emailaddress`、`givenname`、`surname` 和 `displayname`，这些属性需要在 `saml/settings.json` 的 `security.requestedAuthnContext` 或 `security.requestedAttributes` 中进行配置（如果需要的话）。你的应用程序代码 (`app.py`) 使用 `auth.get_attributes()` 来获取这些信息。  

## 运行应用程序  

在终端中导航到项目根目录，然后运行：  

```bash  
python app.py  
```  
  
应用程序将运行在 `https://localhost:5000`。  

## 使用说明  

1.  打开浏览器，访问 `https://localhost:5000`。  
2.  点击"登录"按钮，将被重定向到 Azure AD 登录页面。  
3.  使用在 Azure AD 中拥有访问该应用程序权限的用户进行登录。  
4.  成功登录后，将被重定向回你的应用程序，并显示用户信息。  
5.  点击"登出"按钮，将触发 SAML 单点登出流程。  

## 故障排除  

-   **`ERR_CONNECTION_RESET` 或无法访问页面：** 确保你使用的是 `https://localhost:5000` 而不是 `http://localhost:5000`，并且本地防火墙没有阻止连接。  
-   **`invalid_response` 错误：** 检查 `saml/settings.json` 中的配置是否与 Azure AD 中的配置完全匹配，特别是实体 ID、ACS URL、证书内容等。检查系统时间是否同步。  
-   **AADSTS 错误 (如 AADSTS50011)：** 这通常表示 Azure AD 中的配置与 SAML 请求中的信息不匹配。请仔细核对 Azure AD 应用程序注册中的"标识符"、"回复 URL"和"注销 URL"与 `saml/settings.json` 中的对应设置是否一致，特别是确保 URL 使用的是 `https`。
