#!/bin/bash

# TPN 可诊断性分析工具 - 测试脚本

echo "=========================================="
echo "TPN Diagnosability Tool - Test Script"
echo "=========================================="
echo ""

# 检查 Python 环境
echo "[1/4] Checking Python environment..."
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed"
    exit 1
fi
echo "Python version: $(python3 --version)"
echo ""

# 安装依赖
echo "[2/4] Installing dependencies..."
pip3 install -q -r requirements.txt
if [ $? -eq 0 ]; then
    echo "Dependencies installed successfully"
else
    echo "Warning: Some dependencies may not be installed"
fi
echo ""

# 运行单元测试
echo "[3/4] Running unit tests..."
python3 -m unittest discover tests/ -v
if [ $? -eq 0 ]; then
    echo "All tests passed!"
else
    echo "Some tests failed"
fi
echo ""

# 运行示例分析
echo "[4/4] Running example analysis..."
echo "Analyzing example1.json..."
python3 main.py --input examples/example1.json --max-length 5 --output results/test1
echo ""

echo "Analyzing example2.json..."
python3 main.py --input examples/example2.json --max-length 5 --output results/test2
echo ""

# 批量分析
echo "Running batch analysis..."
python3 main.py --batch examples/ --max-length 5 --output results/batch
echo ""

echo "=========================================="
echo "Test completed!"
echo "Results saved to: results/"
echo "=========================================="
