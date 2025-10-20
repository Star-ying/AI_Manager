#!/bin/bash

# =====================================================
# AI Manager Backend - 依赖管理工具
# 功能：检查、更新、验证项目依赖
# =====================================================

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 项目根目录
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_ROOT"

echo -e "${BLUE}=====================================================${NC}"
echo -e "${BLUE}AI Manager Backend - 依赖管理工具${NC}"
echo -e "${BLUE}=====================================================${NC}"

# 检查Maven是否安装
check_maven() {
    if ! command -v mvn &> /dev/null; then
        echo -e "${RED}❌ Maven未安装，请先安装Maven${NC}"
        echo "安装指南："
        echo "  Ubuntu/Debian: sudo apt install maven"
        echo "  CentOS/RHEL: sudo yum install maven"
        echo "  macOS: brew install maven"
        echo "  Windows: 下载并安装 https://maven.apache.org/download.cgi"
        exit 1
    fi
    
    echo -e "${GREEN}✅ Maven已安装: $(mvn --version | head -n1)${NC}"
}

# 检查Java版本
check_java() {
    if ! command -v java &> /dev/null; then
        echo -e "${RED}❌ Java未安装，请先安装Java 17+${NC}"
        exit 1
    fi
    
    JAVA_VERSION=$(java -version 2>&1 | head -n1 | cut -d'"' -f2 | cut -d'.' -f1)
    if [ "$JAVA_VERSION" -lt 17 ]; then
        echo -e "${RED}❌ Java版本过低: $JAVA_VERSION，需要Java 17+${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}✅ Java版本: $(java -version 2>&1 | head -n1)${NC}"
}

# 显示依赖树
show_dependency_tree() {
    echo -e "${BLUE}📊 显示依赖树...${NC}"
    mvn dependency:tree -Dverbose=false
}

# 分析依赖
analyze_dependencies() {
    echo -e "${BLUE}🔍 分析依赖...${NC}"
    
    # 检查未使用的依赖
    echo -e "${YELLOW}检查未使用的依赖:${NC}"
    mvn dependency:analyze
    
    # 检查过时的依赖
    echo -e "${YELLOW}检查过时的依赖:${NC}"
    mvn versions:display-dependency-updates
    
    # 检查插件更新
    echo -e "${YELLOW}检查插件更新:${NC}"
    mvn versions:display-plugin-updates
}

# 更新依赖版本
update_dependencies() {
    echo -e "${BLUE}🔄 更新依赖版本...${NC}"
    
    # 更新依赖到最新版本
    echo -e "${YELLOW}更新依赖到最新版本:${NC}"
    mvn versions:use-latest-versions
    
    # 更新插件到最新版本
    echo -e "${YELLOW}更新插件到最新版本:${NC}"
    mvn versions:use-latest-releases
    
    echo -e "${GREEN}✅ 依赖更新完成${NC}"
}

# 检查安全漏洞
check_security() {
    echo -e "${BLUE}🔒 检查安全漏洞...${NC}"
    
    # 使用OWASP Dependency Check
    if command -v dependency-check.sh &> /dev/null; then
        echo -e "${YELLOW}运行OWASP依赖检查:${NC}"
        dependency-check.sh --project "AI Manager Backend" --scan "$PROJECT_ROOT"
    else
        echo -e "${YELLOW}OWASP Dependency Check未安装，跳过安全检查${NC}"
        echo "安装命令:"
        echo "  wget https://github.com/jeremylong/DependencyCheck/releases/latest/download/dependency-check-8.4.0-release.zip"
        echo "  unzip dependency-check-8.4.0-release.zip"
    fi
}

# 验证依赖
validate_dependencies() {
    echo -e "${BLUE}✅ 验证依赖...${NC}"
    
    # 编译项目
    echo -e "${YELLOW}编译项目:${NC}"
    mvn clean compile
    
    # 运行测试
    echo -e "${YELLOW}运行测试:${NC}"
    mvn test
    
    # 打包项目
    echo -e "${YELLOW}打包项目:${NC}"
    mvn package -DskipTests
    
    echo -e "${GREEN}✅ 依赖验证完成${NC}"
}

# 清理依赖
clean_dependencies() {
    echo -e "${BLUE}🧹 清理依赖...${NC}"
    
    # 清理Maven缓存
    echo -e "${YELLOW}清理Maven缓存:${NC}"
    mvn dependency:purge-local-repository
    
    # 清理项目
    echo -e "${YELLOW}清理项目:${NC}"
    mvn clean
    
    echo -e "${GREEN}✅ 依赖清理完成${NC}"
}

# 生成依赖报告
generate_report() {
    echo -e "${BLUE}📋 生成依赖报告...${NC}"
    
    # 生成依赖报告
    mvn dependency:analyze-report
    
    # 生成站点报告
    mvn site
    
    echo -e "${GREEN}✅ 报告生成完成，查看target/site/index.html${NC}"
}

# 显示帮助信息
show_help() {
    echo -e "${BLUE}使用方法:${NC}"
    echo "  $0 [选项]"
    echo ""
    echo -e "${BLUE}选项:${NC}"
    echo "  check       检查环境和依赖"
    echo "  tree        显示依赖树"
    echo "  analyze     分析依赖"
    echo "  update      更新依赖版本"
    echo "  security    检查安全漏洞"
    echo "  validate    验证依赖"
    echo "  clean       清理依赖"
    echo "  report      生成依赖报告"
    echo "  all         执行所有检查"
    echo "  help        显示帮助信息"
    echo ""
    echo -e "${BLUE}示例:${NC}"
    echo "  $0 check     # 检查环境"
    echo "  $0 analyze   # 分析依赖"
    echo "  $0 all       # 执行所有检查"
}

# 执行所有检查
run_all_checks() {
    echo -e "${BLUE}🚀 执行所有依赖检查...${NC}"
    
    check_maven
    check_java
    show_dependency_tree
    analyze_dependencies
    check_security
    validate_dependencies
    
    echo -e "${GREEN}🎉 所有检查完成！${NC}"
}

# 主函数
main() {
    case "${1:-help}" in
        "check")
            check_maven
            check_java
            ;;
        "tree")
            check_maven
            show_dependency_tree
            ;;
        "analyze")
            check_maven
            analyze_dependencies
            ;;
        "update")
            check_maven
            update_dependencies
            ;;
        "security")
            check_maven
            check_security
            ;;
        "validate")
            check_maven
            validate_dependencies
            ;;
        "clean")
            check_maven
            clean_dependencies
            ;;
        "report")
            check_maven
            generate_report
            ;;
        "all")
            run_all_checks
            ;;
        "help"|*)
            show_help
            ;;
    esac
}

# 执行主函数
main "$@"
