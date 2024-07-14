<p align="center">
    <img src="app/public/fine-weather-gallery.ico" />
    <br />
    <h1 align="center">Fine Weather</h1>
</p>

## 简介

FineWeather 是一个基于 Vue3 和 BootstrapFlask 构建的相册应用。该应用旨在提供一个简洁、美观且易于使用的界面来管理和浏览您的照片。

## 功能

- **照片上传**：用户可以轻松上传照片。
- **照片浏览**：用户可以浏览上传的照片，并支持缩略图和全屏查看。
- **照片分类**：用户可以对照片进行分类管理。
- **搜索功能**：用户可以通过关键字搜索照片。
- **响应式设计**：应用在各种设备上都能有良好的显示效果。

## 技术栈

- **前端**：Vue3
- **后端**：BootstrapFlask
- **数据库**：SQLite

## 安装与使用

### 前端

1. 克隆仓库
    ```bash
    git clone https://github.com/yourusername/FineWeather.git
    cd FineWeather/frontend
    ```

2. 安装依赖
    ```bash
    npm install
    ```

3. 运行开发服务器
    ```bash
    npm run serve
    ```

### 后端

1. 进入后端目录
    ```bash
    cd ../backend
    ```

2. 创建虚拟环境并激活
    ```bash
    python -m venv venv
    source venv/bin/activate  # 对于 Windows 用户，使用 `venv\Scripts\activate`
    ```

3. 安装依赖
    ```bash
    pip install -r requirements.txt
    ```

4. 运行 Flask 服务器
    ```bash
    flask run
    ```

## 贡献

欢迎任何形式的贡献！请提交 Pull Request 或创建 Issue 来报告问题或提出建议。

## 许可证

该项目基于 MIT 许可证。
