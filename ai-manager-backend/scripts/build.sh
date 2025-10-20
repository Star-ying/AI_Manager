#!/bin/bash

# =====================================================
# AI Manager Backend - 构建脚本
# 功能：编译、测试、打包项目
# =====================================================

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 项目根目录
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

echo -e "${BLUE}=====================================================${NC}"
echo -e "${BLUE}AI Manager Backend - 构建脚本${NC}"
echo -e "${BLUE}=====================================================${NC}"

# 构建选项
CLEAN=false
TEST=true
PACKAGE=true
SKIP_TESTS=false
PROFILE="dev"

# 解析命令行参数
while [[ $# -gt 0 ]]; do
    case $1 in
        --clean)
            CLEAN=true
            shift
            ;;
        --skip-tests)
            SKIP_TESTS=true
            TEST=false
            shift
            ;;
        --no-package)
            PACKAGE=false
            shift
            ;;
        --profile)
            PROFILE="$2"
            shift 2
            ;;
        --help)
            echo "使用方法: $0 [选项]"
            echo ""
            echo "选项:"
            echo "  --clean        清理项目"
            echo "  --skip-tests   跳过测试"
            echo "  --no-package   不打包"
            echo "  --profile      指定配置文件 (dev/test/prod)"
            echo "  --help         显示帮助"
            exit 0
            ;;
        *)
            echo -e "${RED}未知选项: $1${NC}"
            exit 1
            ;;
    esac
done

echo -e "${YELLOW}构建配置:${NC}"
echo "  清理项目: $CLEAN"
echo "  运行测试: $TEST"
echo "  打包项目: $PACKAGE"
echo "  配置文件: $PROFILE"

# 检查Maven
if ! command -v mvn &> /dev/null; then
    echo -e "${RED}❌ Maven未安装${NC}"
    exit 1
fi

# 检查Java
if ! command -v java &> /dev/null; then
    echo -e "${RED}❌ Java未安装${NC}"
    exit 1
fi

echo -e "${GREEN}✅ 环境检查通过${NC}"

# 清理项目
if [ "$CLEAN" = true ]; then
    echo -e "${BLUE}🧹 清理项目...${NC}"
    mvn clean
    echo -e "${GREEN}✅ 项目清理完成${NC}"
fi

# 编译项目
echo -e "${BLUE}🔨 编译项目...${NC}"
mvn compile -P$PROFILE
echo -e "${GREEN}✅ 项目编译完成${NC}"

# 运行测试
if [ "$TEST" = true ]; then
    echo -e "${BLUE}🧪 运行测试...${NC}"
    if [ "$SKIP_TESTS" = true ]; then
        mvn test -DskipTests -P$PROFILE
    else
        mvn test -P$PROFILE
    fi
    echo -e "${GREEN}✅ 测试完成${NC}"
fi

# 打包项目
if [ "$PACKAGE" = true ]; then
    echo -e "${BLUE}📦 打包项目...${NC}"
    if [ "$SKIP_TESTS" = true ]; then
        mvn package -DskipTests -P$PROFILE
    else
        mvn package -P$PROFILE
    fi
    echo -e "${GREEN}✅ 项目打包完成${NC}"
    
    # 显示打包结果
    JAR_FILE=$(find target -name "*.jar" -not -name "*sources.jar" -not -name "*javadoc.jar" | head -n1)
    if [ -n "$JAR_FILE" ]; then
        echo -e "${GREEN}📁 打包文件: $JAR_FILE${NC}"
        echo -e "${GREEN}📊 文件大小: $(du -h "$JAR_FILE" | cut -f1)${NC}"
    fi
fi

# 生成报告
echo -e "${BLUE}📋 生成构建报告...${NC}"
mvn site -P$PROFILE
echo -e "${GREEN}✅ 构建报告生成完成${NC}"

echo -e "${GREEN}🎉 构建完成！${NC}"
echo -e "${YELLOW}下一步:${NC}"
echo "  1. 运行应用: java -jar target/ai-manager-backend-1.0.0.jar"
echo "  2. 查看报告: target/site/index.html"
echo "  3. 查看日志: logs/ai-manager-backend.log"
