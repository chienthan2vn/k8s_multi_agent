# Hệ thống Multi-Agent: Đội Phản ứng Nhanh Kỹ thuật số

Hệ thống này hoạt động như một đội y tế cấp cứu cho các sự cố Kubernetes. Khi có "cuộc gọi khẩn cấp" (alert),
cả đội sẽ phối hợp nhịp nhàng để giải quyết.

## 🏥 Các Chuyên gia trong Đội

1. **🩺 Analyst (Chuyên gia Chẩn đoán):**
   - Thực hiện "khám bệnh": dùng các công cụ để xem log và chỉ số hệ thống
   - Tìm ra chính xác **nguyên nhân gốc rễ**
   - Trả lời câu hỏi: **"Tại sao?"**

2. **📋 Planner (Chuyên gia Lên phác đồ Điều trị):**
   - Dựa trên chẩn đoán, đề xuất các **phương án chữa trị** khả thi
   - Mỗi phương án đều nêu rõ các bước, lệnh cần dùng và rủi ro
   - Trả lời câu hỏi: **"Làm gì?"**

3. **⚙️ Executor (Robot Phẫu thuật):**
   - Thực hiện "ca mổ" một cách **chính xác và an toàn tuyệt đối**
   - Chỉ làm theo lệnh, không tự ý hành động
   - Luôn có phương án rollback

4. **👨‍⚕️ Orchestrator (Trưởng nhóm / Bác sĩ Trực):**
   - Điều phối toàn bộ quy trình
   - Là người giao tiếp chính với kỹ sư
   - Tạo báo cáo tổng hợp

## 🔄 Quy trình làm việc

1. **Tiếp nhận:** Một "ca cấp cứu" đến, **Trưởng nhóm** mở hồ sơ
2. **Chẩn đoán:** **Chuyên gia Chẩn đoán** vào cuộc tìm nguyên nhân
3. **Lên phác đồ:** **Chuyên gia Lên phác đồ** đề xuất các phương án
4. **Hội chẩn:** **Trưởng nhóm** trình bày phác đồ cho kỹ sư để xin phê duyệt
5. **Can thiệp:** **Robot Phẫu thuật** thực hiện kế hoạch đã được duyệt
6. **Báo cáo:** **Trưởng nhóm** xác nhận sự cố đã được giải quyết và đóng hồ sơ

## 🚀 Cài đặt và Sử dụng

### Cài đặt dependencies

```bash
cd multi-agent-system
pip install -r requirements.txt
```

### Thiết lập API Keys

```bash
export GOOGLE_API_KEY="your-google-api-key"
export TAVILY_API_KEY="your-tavily-api-key"
```

### Chạy ứng dụng

#### Chế độ tương tác (recommended)
```bash
python -m src.app --interactive
```

#### Xử lý alert từ file
```bash
python -m src.app --alert-file ../examples/alerts/api-server-latency.json
```

## 📁 Cấu trúc dự án

```
src/
├── app.py              # Ứng dụng chính
├── config.py           # Cấu hình hệ thống
├── agents/             # Các agents
│   ├── analyst.py      # Agent chẩn đoán
│   ├── planner.py      # Agent lập kế hoạch
│   ├── executor.py     # Agent thực thi
│   └── orchestrator.py # Agent điều phối
├── prompts/            # System prompts
│   ├── prompt_analyst.py
│   ├── prompt_planner.py
│   ├── prompt_executor.py
│   └── prompt_orchestrator.py
├── utils/              # Utilities
│   ├── search_tool.py  # Tools tìm kiếm
│   └── parsers.py      # Output parsers
└── workflows/          # LangGraph workflows
    └── response_workflow.py
```

## 🛠️ Công nghệ sử dụng

- **LangGraph:** Tạo workflow và state management
- **LangChain:** ReAct agents và output parsing
- **Google Generative AI:** LLM chính
- **Tavily Search:** Tìm kiếm thông tin
- **Pydantic:** Structured outputs

## 📋 Ví dụ Alert

Hệ thống hỗ trợ các loại alert Kubernetes phổ biến:

- `api-server-latency.json` - Độ trễ API server cao
- `kubelet-down.json` - Kubelet ngừng hoạt động
- `node-down.json` - Node bị down
- `pod-crash-loop-backoff.json` - Pod crash liên tục
- `high-container-restart-rate.json` - Container restart nhiều

## 🔧 Tùy chỉnh

### Thêm Agent mới
1. Tạo file trong `src/agents/`
2. Implement bằng `create_react_agent`
3. Thêm vào workflow trong `response_workflow.py`

### Thêm Tools mới
1. Tạo tools trong `src/utils/`
2. Sử dụng decorator `@tool` của LangChain
3. Thêm vào agent tương ứng

### Custom Prompts
Chỉnh sửa prompts trong `src/prompts/` để phù hợp với use case cụ thể.
   * Sau khi "bác sĩ" (kỹ sư) đã phê duyệt phác đồ, Robot này sẽ tiến hành "ca mổ" một cách **chính xác và an toàn tuyệt đối**.
   Nó chỉ làm theo lệnh, không tự ý hành động.

## Quy trình làm việc của Đội

1. **Tiếp nhận:** Một "ca cấp cứu" đến, **Trưởng nhóm** mở hồ sơ.
2. **Chẩn đoán:** **Chuyên gia Chẩn đoán** vào cuộc tìm nguyên nhân.
3. **Lên phác đồ:** **Chuyên gia Lên phác đồ** đề xuất các phương án.
4. **Hội chẩn:** **Trưởng nhóm** trình bày phác đồ cho kỹ sư để xin phê duyệt.
5. **Can thiệp:** **Robot Phẫu thuật** thực hiện kế hoạch đã được duyệt.
6. **Báo cáo:** **Trưởng nhóm** xác nhận sự cố đã được giải quyết và đóng hồ sơ.
"""
