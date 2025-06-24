#!/usr/bin/env python3
"""
Demo script cho hệ thống Multi-Agent
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.app import main

if __name__ == "__main__":
    # Thiết lập environment variables mặc định
    if not os.getenv("GOOGLE_API_KEY"):
        os.environ["GOOGLE_API_KEY"] = "AIzaSyDgAlnEdV-wwLc41VtAvD3p4NvmmVrJIro"
    
    if not os.getenv("TAVILY_API_KEY"):
        os.environ["TAVILY_API_KEY"] = "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"
    
    # Chạy với interactive mode
    sys.argv = ["demo.py", "--interactive"]
    main()
