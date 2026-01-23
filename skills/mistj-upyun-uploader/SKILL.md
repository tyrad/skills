---
name: mistj-upyun-uploader
description: 将文件及图片上传至又拍云 (UpYun) 存储并获取 CDN 链接。当用户需要执行持久化上传、Markdown 插入图片或生成分享链接时，请使用此技能。
---

# UpYun Uploader (mistj)

处理文件上传到又拍云存储的自动化工具。

## 核心流程

### 1. 鉴权校验与自动配置

当执行上传脚本返回错误提示缺少配置时，AI 应按下述步骤操作：

- **主动获取**：检查项目根目录下是否存在 `upyun_credentials.sh`。
- **用户交互**：若无，礼貌地提示用户提供相关信息（Bucket, Operator, Password, Domain）。
- **安全修复**：用户提供后，AI 必须将配置写入**项目根目录**（即技能文件夹之外，`/Users/mistj/Desktop/skillsDemo/upyun_credentials.sh`），以防止敏感信息被错误打包进 .skill 文件。
- **配置格式**：
  ```bash
  export UPYUN_BUCKET="xxx"
  export UPYUN_OPERATOR="xxx"
  export UPYUN_PASSWORD="xxx"
  export UPYUN_DOMAIN="xxx"
  ```

### 2. 执行上传

**操作命令 (路径相对于本技能根目录)：**

```bash
./scripts/upyun_upload.sh <local_file_path> [optional_sub_dir]
```

- **参数 1**：本地文件的绝对路径。
- **参数 2 (可选)**：自定义的基础目录名（若不传，脚本将使用默认配置）。

**执行逻辑：**

- AI 自动解析脚本物理路径。
- 脚本会自动向上搜索并加载 `upyun_credentials.sh`。

### 3. 输出处理

脚本成功运行后返回图片的 CDN 链接。AI 应将其直接嵌入到最终输出（如 Markdown 的 `![]()`)。

## 资源清单

### scripts/

- **[upyun_upload.sh](scripts/upyun_upload.sh)**: 核心 Shell 脚本，具备目录溯源配置加载功能。
