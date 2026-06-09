# AI Terminal Bridge

**Kết nối Claude, ChatGPT, Gemini, DeepSeek, Grok, Copilot với terminal / script qua API OpenAI-compatible.**

Dự án **100% Python** — server API + Playwright bridge. Playwright tự động gửi prompt lên giao diện web của các nền tảng AI, đọc phản hồi, rồi trả về cho ứng dụng qua endpoint `/v1/chat/completions`.

---

## Mục lục

- [Tính năng](#tính-năng)
- [Kiến trúc](#kiến-trúc)
- [Yêu cầu hệ thống](#yêu-cầu-hệ-thống)
- [Cài đặt](#cài-đặt)
- [Hướng dẫn sử dụng](#hướng-dẫn-sử-dụng)
- [API Reference](#api-reference) · [API.md đầy đủ](./API.md)
- [Cấu hình](#cấu-hình)
- [Thêm nền tảng AI mới](#thêm-nền-tảng-ai-mới)
- [Cấu trúc thư mục](#cấu-trúc-thư-mục)
- [Xử lý sự cố](#xử-lý-sự-cố)

---

## Tính năng

| Tính năng | Mô tả |
|-----------|--------|
| **Đa nền tảng** | Claude, ChatGPT, Gemini, DeepSeek, Grok, Copilot (cấu hình qua JSON) |
| **API OpenAI-compatible** | `POST /v1/chat/completions`, `GET /v1/models`, streaming cơ bản |
| **Playwright** | Điều khiển Chromium trực tiếp — không cần Chrome Extension |
| **Action chung** | Một bộ logic fill/click/read — chỉ 3 selector mỗi AI, đọc response cuối tự động trong code |
| **Cấu hình đơn giản** | Thêm AI mới: `name`, `model`, `url`, 3 selectors (`input`, `send_button`, `stop_button`) |
| **Profile lưu đăng nhập** | Session đăng nhập giữ trong `browser-profile/` |
| **Upstream proxy** | Tùy chọn chuyển tiếp sang API bên ngoài (OpenRouter, v.v.) |

---

## Kiến trúc

```
┌─────────────────┐     POST /v1/chat/completions      ┌──────────────────┐
│  client_test.py │ ─────────────────────────────────► │  server.py       │
│  (hoặc app khác)│                                    │  Port 5000 (API) │
└─────────────────┘                                    └────────┬─────────┘
                                                                  │
                                                     POST /api/ai/chat-request
                                                                  ▼
┌─────────────────┐     GET /api/ai/user-input         ┌──────────────────┐
│  Playwright     │ ◄────────────────────────────────► │  server.py       │
│  python -m bridge│    POST /api/ai/message          │  Port 3000       │
│  (Chromium)     │                                    │  (Bridge)        │
└────────┬────────┘                                    └──────────────────┘
         │ fill input / click send / đọc response
         ▼
┌─────────────────┐
│  claude.ai      │
│  chatgpt.com    │
│  gemini.google  │
│  chat.deepseek  │
└─────────────────┘
```

**Luồng hoạt động:**

1. App gọi `POST http://127.0.0.1:5000/v1/chat/completions` với `messages` và `model`.
2. API server chuyển tin sang Bridge (port 3000).
3. Playwright bridge poll `/api/ai/user-input`, mở tab AI tương ứng.
4. Action chung: điền prompt → bấm gửi → chờ nút stop biến mất → đọc câu trả lời cuối cùng.
5. Phản hồi POST về Bridge → API trả JSON OpenAI-compatible.

---

## Yêu cầu hệ thống

- **Python** 3.10+
- Tài khoản đã **đăng nhập** trên ít nhất một nền tảng AI
- Không cần Node.js

---

## Cài đặt

### 1. Clone / tải project

```bash
cd ai-extention-py
```

### 2. Cài dependencies Python

```bash
pip install -r requirements.txt
python -m playwright install chromium
```

### 3. Khởi động server

```bash
python server.py
```

Server tự khởi động Playwright bridge. Khi chạy thành công:

- **Port 3000** — Bridge (giao tiếp với Playwright)
- **Port 5000** — API OpenAI-compatible

Lần đầu chạy, Chromium mở ra — **đăng nhập** các nền tảng AI cần dùng. Session được lưu trong `browser-profile/`.

### 4. Chạy bridge thủ công (tùy chọn)

```bash
python -m bridge
```

Hoặc tắt auto-start: `set AUTO_START_BRIDGE=0` rồi chạy `python -m bridge` trong terminal riêng.

---

## Hướng dẫn sử dụng

### Chat từ terminal

```bash
python client_test.py
```

### Gọi API bằng curl

```bash
curl -X POST http://127.0.0.1:5000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "claude",
    "messages": [
      {"role": "user", "content": "Xin chào!"}
    ]
  }'
```

**Model ID:**

| `model` | Nền tảng |
|---------|----------|
| `claude` | Claude |
| `gpt` | ChatGPT |
| `gemini` | Gemini |
| `deepseek` | DeepSeek |
| `grok` | Grok |
| `copilot` | Copilot |

---

## API Reference

Hai server chạy song song:

| Server | URL | Ai gọi |
|--------|-----|--------|
| **Public API** | `http://127.0.0.1:5000` | App, script |
| **Bridge** | `http://127.0.0.1:3000` | Playwright bridge |

Chi tiết đầy đủ: [API.md](./API.md)

---

## Cấu hình

### Biến môi trường

| Biến | Mặc định | Mô tả |
|------|----------|--------|
| `SERVER_HOST` | `127.0.0.1` | Host bind server |
| `PORT_EXTENSION` | `3000` | Port Bridge |
| `PORT_API` | `5000` | Port API |
| `MODEL_ID` | `claude` | Model mặc định |
| `AUTO_START_BRIDGE` | `1` | `0` = không tự chạy Playwright |
| `BRIDGE_SERVER_URL` | `http://127.0.0.1:3000` | URL bridge cho Playwright |
| `UPSTREAM_CHAT_COMPLETIONS_URL` | *(trống)* | Proxy upstream (bỏ qua Playwright) |

### `ai_models_config.json`

```json
{
  "models": {
    "myai": {
      "name": "My AI",
      "model": "myai",
      "url": "https://example.com/chat",
      "selectors": {
        "input": "textarea",
        "send_button": "button[type=submit]",
        "stop_button": "button[aria-label*=\"Stop\"]"
      },
      "response_settings": {
        "stability_ms": 800,
        "streaming_grace_ms": 2500
      }
    }
  },
  "browser": {
    "headless": false,
    "user_data_dir": "browser-profile"
  }
}
```

**Selectors (chỉ 3 key, tất cả bắt buộc):**

| Key | Mô tả |
|-----|--------|
| `input` | Ô nhập prompt (textarea hoặc contenteditable) |
| `send_button` | Nút gửi |
| `stop_button` | Nút dừng generate — biết AI còn đang trả lời hay đã xong |

Đọc phản hồi **không cần cấu hình**: code trong `bridge/actions.py` luôn lấy câu trả lời assistant cuối cùng trên trang.

Nhiều selector trong một key (cách nhau bằng dấu phẩy) — thử lần lượt cho đến khi khớp (hữu ích cho đa ngôn ngữ UI).

**`response_settings` (tùy chọn):**

| Key | Mặc định | Mô tả |
|-----|----------|--------|
| `stability_ms` | `800` | Đợi text ổn định trước khi trả về |
| `streaming_grace_ms` | `2500` | Grace period sau khi nút stop biến mất |

---

## Thêm nền tảng AI mới

1. Mở trang web AI, F12 → tìm selector cho **input**, **nút gửi**, **nút stop** (khi AI đang generate).
2. Thêm block mới vào `ai_models_config.json`:

```json
"newai": {
  "name": "New AI",
  "model": "newai",
  "url": "https://newai.com",
  "selectors": {
    "input": "#chat-input",
    "send_button": "button.send",
    "stop_button": "button[aria-label*=\"Stop\"]"
  }
}
```

3. Khởi động lại server. Lần đầu mở tab, đăng nhập nếu cần.

Action chung tự xử lý:
- `textarea`/`input` → `fill()`
- `contenteditable` → gõ qua keyboard
- Click send → chờ `stop_button` biến mất → đọc câu trả lời cuối

Nếu DOM response của nền tảng mới khác hẳn các AI hiện có, bổ sung selector vào `_ASSISTANT_TURN_SELECTORS` / `_CONTENT_SELECTORS` trong `bridge/actions.py`.

---

## Cấu trúc thư mục

```
ai-extention-py/
├── ai_models_config.json   # Cấu hình model: url + 3 selectors
├── requirements.txt
├── server.py               # Bridge (3000) + API (5000)
├── bridge/
│   ├── worker.py           # Poll bridge, quản lý browser
│   ├── actions.py          # Action chung (fill, click, đọc response cuối)
│   └── config.py           # Load ai_models_config.json
├── client_test.py          # Client mẫu chat từ terminal
├── browser-profile/        # Session Chromium (tự tạo)
├── API.md
└── README.md
```

---

## Xử lý sự cố

### Playwright không khởi động

```bash
pip install -r requirements.txt
python -m playwright install chromium
```

### API trả `[Fallback] You asked: ...`

- Playwright bridge chưa chạy hoặc chưa nhận response
- Kiểm tra đã đăng nhập trong `browser-profile`
- Xem log terminal khi chạy `python server.py`

### Prompt không gửi được

- Selector lỗi thời — test trong DevTools: `document.querySelector('...')`
- Tăng `browser.wait_for_input_ms` trong config

### Phản hồi bị cắt hoặc đọc sai

- Kiểm tra `stop_button` — selector phải khớp khi AI đang generate
- Tăng `stability_ms` hoặc `streaming_grace_ms` trong `response_settings`
- Nếu lấy nhầm nội dung, cập nhật `_ASSISTANT_TURN_SELECTORS` trong `bridge/actions.py`

---

## Lưu ý pháp lý

Chỉ dùng cho mục đích cá nhân / nghiên cứu. Tự động hóa giao diện web có thể vi phạm Terms of Service của các nền tảng AI.

---

## Tóm tắt nhanh

```bash
pip install -r requirements.txt
python -m playwright install chromium
python server.py
# Terminal khác:
python client_test.py
```
