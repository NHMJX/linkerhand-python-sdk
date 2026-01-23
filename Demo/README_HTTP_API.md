# LinkerHand HTTP API 使用说明

本HTTP API服务将Demo/main.py中的功能包装为REST API，方便C++项目或其他语言通过HTTP调用来控制LinkerHand机械手。

## 支持的框架

项目提供了两种HTTP API实现：

1. **FastAPI版本** (`main_http.py`) - 推荐用于新项目
   - 自动API文档生成
   - 类型验证和更好的性能
   - 异步支持

2. **Flask版本** (`main_flask.py`) - 适合简单需求
   - 轻量级，学习曲线平缓
   - 丰富的生态系统
   - 更灵活的定制化

## 启动服务

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 选择API框架启动服务

#### FastAPI版本 (推荐)

```bash
cd Demo
python main_http.py
```

服务将在 `http://localhost:8000` 启动，并自动生成交互式API文档。

#### Flask版本 (轻量级)

```bash
cd Demo
python main_flask.py
```

服务将在 `http://localhost:5000` 启动。

## API端点

### GET /
获取API信息和可用端点列表

**响应示例：**
```json
{
  "message": "LinkerHand HTTP API 服务运行中",
  "version": "1.0.0",
  "endpoints": {
    "/hold_pen": "执行握笔动作",
    "/open_hand": "打开手部",
    "/close_hand": "关闭手部",
    "/set_speed": "设置速度",
    "/set_torque": "设置力矩",
    "/finger_move": "移动手指到指定位置"
  }
}
```

### POST /hold_pen
执行握笔动作（包含设置速度、力矩和移动手指）

**响应示例：**
```json
{
  "status": "success",
  "message": "握笔动作执行成功"
}
```

### POST /open_hand
打开手部

**响应示例：**
```json
{
  "status": "success",
  "message": "打开手部成功"
}
```

### POST /close_hand
关闭手部（断开CAN连接）

**响应示例：**
```json
{
  "status": "success",
  "message": "关闭手部成功"
}
```

### POST /set_speed
设置电机速度

**请求体：**
```json
{
  "speeds": [60, 60, 60, 60, 60, 60]
}
```

**响应示例：**
```json
{
  "status": "success",
  "message": "设置速度成功: [60, 60, 60, 60, 60, 60]"
}
```

### POST /set_torque
设置电机力矩

**请求体：**
```json
{
  "torques": [50, 50, 50, 50, 50, 50]
}
```

**响应示例：**
```json
{
  "status": "success",
  "message": "设置力矩成功: [50, 50, 50, 50, 50, 50]"
}
```

### POST /finger_move
移动手指到指定位置

**请求体：**
```json
{
  "positions": [120, 90, 120, 70, 50, 40]
}
```

**响应示例：**
```json
{
  "status": "success",
  "message": "移动手指成功: [120, 90, 120, 70, 50, 40]"
}
```

### GET /health
健康检查

**响应示例：**
```json
{
  "status": "healthy"
}
```

## C++ 调用示例

### 使用curl命令测试

#### FastAPI版本 (端口8000)

```bash
# 握笔动作
curl -X POST http://localhost:8000/hold_pen

# 打开手部
curl -X POST http://localhost:8000/open_hand

# 设置速度
curl -X POST http://localhost:8000/set_speed \
  -H "Content-Type: application/json" \
  -d '{"speeds": [60, 60, 60, 60, 60, 60]}'

# 移动手指
curl -X POST http://localhost:8000/finger_move \
  -H "Content-Type: application/json" \
  -d '{"positions": [120, 90, 120, 70, 50, 40]}'
```

#### Flask版本 (端口5000)

```bash
# 握笔动作
curl -X POST http://localhost:5000/hold_pen

# 打开手部
curl -X POST http://localhost:5000/open_hand

# 设置速度
curl -X POST http://localhost:5000/set_speed \
  -H "Content-Type: application/json" \
  -d '{"speeds": [60, 60, 60, 60, 60, 60]}'

# 移动手指
curl -X POST http://localhost:5000/finger_move \
  -H "Content-Type: application/json" \
  -d '{"positions": [120, 90, 120, 70, 50, 40]}'
```

### C++ HTTP客户端示例

#### 使用libcurl

```cpp
#include <curl/curl.h>
#include <string>
#include <iostream>

// 回调函数处理响应
size_t WriteCallback(void* contents, size_t size, size_t nmemb, void* userp) {
    ((std::string*)userp)->append((char*)contents, size * nmemb);
    return size * nmemb;
}

// 发送POST请求的函数
std::string sendPostRequest(const std::string& url, const std::string& jsonData = "") {
    CURL* curl;
    CURLcode res;
    std::string readBuffer;

    curl = curl_easy_init();
    if(curl) {
        curl_easy_setopt(curl, CURLOPT_URL, url.c_str());
        curl_easy_setopt(curl, CURLOPT_POST, 1L);

        if (!jsonData.empty()) {
            curl_easy_setopt(curl, CURLOPT_POSTFIELDS, jsonData.c_str());
            struct curl_slist* headers = NULL;
            headers = curl_slist_append(headers, "Content-Type: application/json");
            curl_easy_setopt(curl, CURLOPT_HTTPHEADER, headers);
        }

        curl_easy_setopt(curl, CURLOPT_WRITEFUNCTION, WriteCallback);
        curl_easy_setopt(curl, CURLOPT_WRITEDATA, &readBuffer);

        res = curl_easy_perform(curl);
        curl_easy_cleanup(curl);

        if(res != CURLE_OK) {
            std::cerr << "curl_easy_perform() failed: " << curl_easy_strerror(res) << std::endl;
            return "";
        }
    }
    return readBuffer;
}

int main() {
    // 初始化curl
    curl_global_init(CURL_GLOBAL_DEFAULT);

    // 注意：根据你使用的API框架修改端口号
    // FastAPI: localhost:8000
    // Flask: localhost:5000
    const std::string baseUrl = "http://localhost:8000";  // 或 "http://localhost:5000"

    // 握笔动作
    std::string response = sendPostRequest(baseUrl + "/hold_pen");
    std::cout << "Hold pen response: " << response << std::endl;

    // 打开手部
    response = sendPostRequest(baseUrl + "/open_hand");
    std::cout << "Open hand response: " << response << std::endl;

    // 设置速度
    std::string speedData = R"({"speeds": [60, 60, 60, 60, 60, 60]})";
    response = sendPostRequest(baseUrl + "/set_speed", speedData);
    std::cout << "Set speed response: " << response << std::endl;

    // 移动手指
    std::string moveData = R"({"positions": [120, 90, 120, 70, 50, 40]})";
    response = sendPostRequest(baseUrl + "/finger_move", moveData);
    std::cout << "Finger move response: " << response << std::endl;

    // 清理curl
    curl_global_cleanup();
    return 0;
}
```

#### 使用C++ REST SDK (cpprestsdk)

首先安装cpprestsdk：
- Ubuntu: `sudo apt-get install libcpprest-dev`
- macOS: `brew install cpprestsdk`
- Windows: 通过vcpkg安装

```cpp
#include <cpprest/http_client.h>
#include <cpprest/json.h>
#include <iostream>

using namespace web;
using namespace web::http;
using namespace web::http::client;

int main() {
    // 创建HTTP客户端
    http_client client(U("http://localhost:8000"));

    try {
        // 握笔动作
        auto response = client.request(methods::POST, U("/hold_pen")).get();
        std::cout << "Hold pen status: " << response.status_code() << std::endl;
        std::cout << "Response: " << response.extract_string().get() << std::endl;

        // 打开手部
        response = client.request(methods::POST, U("/open_hand")).get();
        std::cout << "Open hand status: " << response.status_code() << std::endl;
        std::cout << "Response: " << response.extract_string().get() << std::endl;

        // 设置速度
        json::value speedJson;
        json::value speedArray = json::value::array();
        for(int i = 0; i < 6; i++) {
            speedArray[i] = json::value(60);
        }
        speedJson[U("speeds")] = speedArray;

        response = client.request(methods::POST, U("/set_speed"), speedJson).get();
        std::cout << "Set speed status: " << response.status_code() << std::endl;
        std::cout << "Response: " << response.extract_string().get() << std::endl;

        // 移动手指
        json::value moveJson;
        json::value posArray = json::value::array();
        int positions[] = {120, 90, 120, 70, 50, 40};
        for(int i = 0; i < 6; i++) {
            posArray[i] = json::value(positions[i]);
        }
        moveJson[U("positions")] = posArray;

        response = client.request(methods::POST, U("/finger_move"), moveJson).get();
        std::cout << "Finger move status: " << response.status_code() << std::endl;
        std::cout << "Response: " << response.extract_string().get() << std::endl;

    } catch (const std::exception& e) {
        std::cerr << "Error: " << e.what() << std::endl;
    }

    return 0;
}
```

## 错误处理

所有API端点在出错时会返回相应的HTTP状态码和错误信息：

- `500 Internal Server Error`: 服务器内部错误，通常是硬件通信问题

错误响应示例：
```json
{
  "detail": "执行握笔动作失败: 设备未连接"
}
```

## API文档

启动服务后，可以访问以下地址查看完整的API文档：

### FastAPI版本
- Swagger UI (交互式): http://localhost:8000/docs
- ReDoc (静态文档): http://localhost:8000/redoc
- OpenAPI JSON: http://localhost:8000/openapi.json

### Flask版本
Flask版本没有内置的API文档生成器，但你可以通过以下方式查看API信息：
- API信息: http://localhost:5000/
- 健康检查: http://localhost:5000/health

## 注意事项

1. 确保CAN设备正确连接并配置
2. 服务启动时会自动初始化LinkerHand设备
3. 建议在C++项目中使用异步HTTP请求以避免阻塞主线程
4. 注意处理网络超时和连接错误的情况