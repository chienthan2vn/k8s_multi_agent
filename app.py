"""
Ứng dụng chính cho hệ thống Multi-Agent phản ứng nhanh Kubernetes
"""

import json
import argparse
from pathlib import Path

# Import các module của project
from src.workflows.response_workflow import run_incident_response
from src.config import GOOGLE_API_KEY, TAVILY_API_KEY


def load_alert_from_file(alert_file: str) -> dict:
    """Load alert data từ file JSON"""
    try:
        with open(alert_file, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"❌ Lỗi đọc file alert: {e}")
        return {}


def setup_environment():
    """Thiết lập môi trường và kiểm tra API keys"""
    print("🔧 Đang thiết lập môi trường...")

    # Kiểm tra API keys
    if not GOOGLE_API_KEY:
        print("⚠️ Chưa có GOOGLE_API_KEY, sử dụng default key...")

    if not TAVILY_API_KEY:
        print("⚠️ Chưa có TAVILY_API_KEY, sử dụng default key...")

    print("✅ Môi trường đã được thiết lập")


def print_banner():
    """In banner của ứng dụng"""
    banner = """
╔══════════════════════════════════════════════════════════════╗
║                    ĐỘI PHẢN ỨNG NHANH KỸ THUẬT SỐ            ║
║                   Multi-Agent System for Kubernetes          ║
╠══════════════════════════════════════════════════════════════╣
║  🔬 Analyst    - Chuyên gia Chẩn đoán                       ║
║  📋 Planner    - Chuyên gia Lên phác đồ Điều trị            ║
║  ⚙️ Executor   - Robot Phẫu thuật                           ║
║  👨‍⚕️ Orchestrator - Trưởng nhóm / Bác sĩ Trực                ║
╚══════════════════════════════════════════════════════════════╝
    """
    print(banner)


def run_interactive_mode():
    """Chạy chế độ tương tác"""
    print("\n🎮 CHẾ ĐỘ TƯƠNG TÁC")
    print("Chọn một alert example để xử lý:")

    # Danh sách các alert examples
    examples_dir = Path(__file__).parent.parent.parent / "examples" / "alerts"
    alert_files = list(examples_dir.glob("*.json"))

    if not alert_files:
        print("❌ Không tìm thấy alert examples!")
        return

    # Hiển thị menu
    for i, alert_file in enumerate(alert_files, 1):
        print(f"{i}. {alert_file.stem}")

    try:
        choice = int(input(f"\nChọn alert (1-{len(alert_files)}): ")) - 1
        if 0 <= choice < len(alert_files):
            selected_file = alert_files[choice]
            print(f"\n📁 Đã chọn: {selected_file.name}")

            # Load và chạy workflow
            alert_data = load_alert_from_file(str(selected_file))
            if alert_data:
                result = run_incident_response(alert_data)
                print_final_report(result)
        else:
            print("❌ Lựa chọn không hợp lệ!")
    except ValueError:
        print("❌ Vui lòng nhập số!")


def print_final_report(report: dict):
    """In báo cáo cuối cùng"""
    print("\n" + "=" * 80)
    print("📊 BÁO CÁO CUỐI CÙNG")
    print("=" * 80)

    if "orchestrator_summary" in report:
        print(report["orchestrator_summary"])

    print("\n📋 THÔNG TIN CHI TIẾT:")
    print(f"Incident ID: {report.get('incident_id', 'N/A')}")
    print(f"Status: {report.get('status', 'N/A')}")
    print(f"Alert: {report.get('alert_summary', {}).get('name', 'N/A')}")
    print(f"Severity: {report.get('alert_summary', {}).get('severity', 'N/A')}")

    if "diagnosis" in report and not report["diagnosis"].get("error"):
        print(f"Root Cause: {report['diagnosis'].get('root_cause', 'N/A')}")
        print(f"Severity Level: {report['diagnosis'].get('severity_level', 'N/A')}")

    if "remediation_plan" in report and not report["remediation_plan"].get("error"):
        plan = report["remediation_plan"]
        print(f"Plan: {plan.get('plan_name', 'N/A')}")
        print(f"Risk Level: {plan.get('risk_level', 'N/A')}")
        print(f"Steps: {len(plan.get('steps', []))}")

    if "execution_result" in report:
        exec_result = report["execution_result"]
        print(f"Execution Status: {exec_result.get('status', 'N/A')}")


def main():
    """Hàm main của ứng dụng"""
    parser = argparse.ArgumentParser(
        description="Hệ thống Multi-Agent phản ứng nhanh Kubernetes"
    )
    parser.add_argument("--alert-file", "-f", help="File alert JSON để xử lý")
    parser.add_argument(
        "--interactive", "-i", action="store_true", help="Chạy chế độ tương tác"
    )

    args = parser.parse_args()

    # Thiết lập môi trường
    setup_environment()
    print_banner()

    if args.interactive:
        run_interactive_mode()
    elif args.alert_file:
        print(f"\n📁 Xử lý alert từ file: {args.alert_file}")
        alert_data = load_alert_from_file(args.alert_file)
        if alert_data:
            result = run_incident_response(alert_data)
            print_final_report(result)
    else:
        print(
            "\n❓ Không có tham số nào được cung cấp. Sử dụng --help để xem hướng dẫn."
        )
        print("💡 Thử: python -m src.app --interactive")


if __name__ == "__main__":
    main()
