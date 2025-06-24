"""
Output parsers cho các agents
"""
from langchain.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

class AnalysisResult(BaseModel):
    """Kết quả phân tích từ Analyst agent"""
    root_cause: str = Field(description="Nguyên nhân gốc rễ của sự cố")
    severity_level: str = Field(description="Mức độ nghiêm trọng: low, medium, high, critical")
    affected_components: List[str] = Field(description="Các thành phần bị ảnh hưởng")
    investigation_summary: str = Field(description="Tóm tắt quá trình điều tra")
    
class PlanStep(BaseModel):
    """Một bước trong kế hoạch khắc phục"""
    step_number: int = Field(description="Số thứ tự bước")
    action: str = Field(description="Hành động cần thực hiện")
    command: str = Field(description="Lệnh kubectl hoặc script cần chạy")
    expected_result: str = Field(description="Kết quả mong đợi")
    rollback_command: Optional[str] = Field(description="Lệnh rollback nếu có lỗi")

class RemediationPlan(BaseModel):
    """Kế hoạch khắc phục từ Planner agent"""
    plan_id: str = Field(description="ID của kế hoạch")
    plan_name: str = Field(description="Tên kế hoạch")
    description: str = Field(description="Mô tả kế hoạch")
    risk_level: str = Field(description="Mức độ rủi ro: low, medium, high")
    estimated_time: str = Field(description="Thời gian ước tính")
    steps: List[PlanStep] = Field(description="Các bước thực hiện")
    prerequisites: List[str] = Field(description="Điều kiện tiên quyết")

class ExecutionResult(BaseModel):
    """Kết quả thực thi từ Executor agent"""
    execution_id: str = Field(description="ID thực thi")
    status: str = Field(description="Trạng thái: success, failed, partial")
    executed_steps: List[Dict[str, Any]] = Field(description="Các bước đã thực hiện")
    error_message: Optional[str] = Field(description="Thông báo lỗi nếu có")
    rollback_performed: bool = Field(description="Có thực hiện rollback không")
    final_verification: str = Field(description="Kết quả kiểm tra cuối cùng")

# Tạo các parser instances
analysis_parser = PydanticOutputParser(pydantic_object=AnalysisResult)
plan_parser = PydanticOutputParser(pydantic_object=RemediationPlan)  
execution_parser = PydanticOutputParser(pydantic_object=ExecutionResult)

def get_analysis_format_instructions():
    """Trả về format instructions cho Analyst"""
    return analysis_parser.get_format_instructions()

def get_plan_format_instructions():
    """Trả về format instructions cho Planner"""
    return plan_parser.get_format_instructions()

def get_execution_format_instructions():
    """Trả về format instructions cho Executor"""
    return execution_parser.get_format_instructions()
