# QE Watchdog Agent

Agent giám sát QE process của team Zalopay: quét vi phạm (Level 0–3) trên sprint
hiện tại, chat phân tích/insights, lập lịch và gửi report về Microsoft Teams.
Chạy trên GreenNode AgentBase, LLM qua GreenNode AI Platform (OpenAI-compatible).

## Cấu trúc thư mục

```
qe_agent/
├── server.py            # Entry point — FastAPI app + UI (Docker CMD)
├── main.py              # CLI: chạy pipeline / scheduler (fetch → rules → send)
├── paths.py             # Đường dẫn tập trung (config/snapshots/data) + nạp .env
│
├── agent/               # LLM agent
│   └── claude_agent.py  #   vòng lặp tool-calling + streaming (GreenNode LLM)
│
├── engine/              # Lõi nghiệp vụ (thuần Python, không I/O ngoài)
│   ├── models.py        #   dataclasses: Ticket, DailyReport, Level…
│   ├── rule_engine.py   #   đọc rules → đánh giá vi phạm
│   └── mock_data.py     #   ticket mẫu để test
│
├── integrations/        # Kết nối hệ thống ngoài
│   ├── jira_adapter.py  #   normalize issue (dict) + fetch theo JQL
│   ├── jira_fetcher.py  #   fetch Jira → Ticket (live)
│   └── teams_sender.py  #   render report + gửi qua Power Automate Flow
│
├── services/            # Tầng nghiệp vụ cho web/API
│   ├── qa_service.py    #   scan / send / insights / chat / rules / snapshots
│   └── webstore.py      #   lưu task_runs + schedules (SQLite)
│
├── config/
│   └── rules.yaml       # Định nghĩa rule QE (Level 0–3)
├── snapshots/           # Dữ liệu Jira snapshot (*.json) cho demo offline
├── data/                # Runtime DB (watchdog.db) — gitignored
├── ui/index.html        # SPA chatbot (Chat · Scan · Rules · Lịch chạy · Lịch sử)
│
├── Dockerfile  .dockerignore  requirements.txt
```

**Quy tắc import:** mọi module import tuyệt đối từ ROOT (`from engine.rule_engine import …`,
`from integrations import teams_sender`). `server.py` / `main.py` tự thêm ROOT vào
`sys.path`; trong Docker ROOT = `/app`.

## Chạy local

```bash
cd qe_agent
pip install -r requirements.txt
python server.py            # mở http://localhost:8080
# hoặc CLI:
python main.py --once --mock
```

`.env` (ở thư mục cha hoặc cùng cấp) cung cấp `GREENNODE_API_KEY`, và khi gửi report
Teams: `TEAMS_FLOW_QE` / `TEAMS_FLOW_DEV_MS` / `TEAMS_FLOW_DEV_CRM` (Power Automate Flow URL).

## Biến môi trường chính

| Biến | Mô tả |
|------|-------|
| `GREENNODE_API_KEY` | API key LLM (GreenNode AI Platform) |
| `TEAMS_FLOW_*` | Power Automate Flow URL cho từng kênh (QE / Dev-MS / Dev-CRM) |
| `JIRA_BASE_URL`, `JIRA_PAT` | (tuỳ chọn) khi dùng Live Jira thay vì snapshot |
| `REPORT_MAX_ROWS_PER_EMAIL` | Số dòng tối đa mỗi bài post trước khi tách (mặc định 60) |

Các biến `GREENNODE_CLIENT_ID/SECRET/AGENT_IDENTITY/ENDPOINT_URL` do AgentBase tự inject — không set thủ công.
