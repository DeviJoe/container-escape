#!/bin/bash

set -e

# Container Escape Demo Deployment Script
# WARNING: This deploys intentionally vulnerable containers for educational purposes only!

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
CONTAINER_NAME="vulnerable-container"
IMAGE_NAME="container-escape-demo"
PORT="5000"

# Functions
print_banner() {
    echo -e "${RED}"
    echo "=================================================================="
    echo "🚨 VULNERABLE CONTAINER DEPLOYMENT SCRIPT 🚨"
    echo "=================================================================="
    echo "WARNING: This deploys intentionally vulnerable containers!"
    echo "Use only in isolated testing environments for educational purposes."
    echo "=================================================================="
    echo -e "${NC}"
}

print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

check_requirements() {
    print_status "Checking requirements..."

    # Check if Docker is installed and running
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed or not in PATH"
        exit 1
    fi

    if ! docker info &> /dev/null; then
        print_error "Docker daemon is not running"
        exit 1
    fi

    # Check if Docker Compose is installed
    if ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose is not installed"
        exit 1
    fi

    # Check if we're running on Linux (required for kernel modules)
    if [[ "$OSTYPE" != "linux-gnu"* ]]; then
        print_warning "This demo is designed for Linux systems"
        print_warning "Kernel module functionality may not work on other platforms"
    fi

    # Check if running as root (may be needed for some operations)
    if [[ $EUID -eq 0 ]]; then
        print_warning "Running as root - this increases security risks"
    fi

    print_status "Requirements check passed"
}

cleanup() {
    print_status "Cleaning up existing containers and images..."

    # Stop and remove container if it exists
    if docker ps -a --format 'table {{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
        print_status "Stopping existing container: ${CONTAINER_NAME}"
        docker stop ${CONTAINER_NAME} || true
        docker rm ${CONTAINER_NAME} || true
    fi

    # Remove existing image if it exists
    if docker images --format 'table {{.Repository}}' | grep -q "^${IMAGE_NAME}$"; then
        print_status "Removing existing image: ${IMAGE_NAME}"
        docker rmi ${IMAGE_NAME} || true
    fi

    print_status "Cleanup completed"
}

build_and_deploy() {
    print_status "Building and deploying vulnerable container..."

    # Build and start with Docker Compose
    print_status "Building container with Docker Compose..."
    docker-compose up --build -d

    # Wait for container to be ready
    print_status "Waiting for container to start..."
    sleep 5

    # Check if container is running
    if docker ps --format 'table {{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
        print_status "Container is running successfully"
    else
        print_error "Container failed to start"
        docker-compose logs
        exit 1
    fi
}

test_deployment() {
    print_status "Testing deployment..."

    # Test HTTP connectivity
    for i in {1..10}; do
        if curl -s "http://localhost:${PORT}/health" > /dev/null; then
            print_status "Application is responding on port ${PORT}"
            break
        else
            if [ $i -eq 10 ]; then
                print_error "Application not responding after 10 attempts"
                print_status "Container logs:"
                docker logs ${CONTAINER_NAME}
                exit 1
            fi
            print_status "Waiting for application to start... (attempt $i/10)"
            sleep 2
        fi
    done

    # Test capabilities
    print_status "Checking container capabilities..."
    CAP_OUTPUT=$(docker exec ${CONTAINER_NAME} capsh --print 2>/dev/null || echo "Failed to check capabilities")
    if echo "$CAP_OUTPUT" | grep -q "cap_sys_module"; then
        print_status "CAP_SYS_MODULE capability confirmed"
    else
        print_warning "CAP_SYS_MODULE capability not detected"
        echo "Capability output: $CAP_OUTPUT"
    fi
}

show_usage_info() {
    echo -e "${GREEN}"
    echo "=================================================================="
    echo "🎯 DEPLOYMENT COMPLETED SUCCESSFULLY"
    echo "=================================================================="
    echo -e "${NC}"

    echo "Container Information:"
    echo "  Name: ${CONTAINER_NAME}"
    echo "  Port: ${PORT}"
    echo "  URL:  http://localhost:${PORT}"
    echo ""

    echo "Available Endpoints:"
    echo "  Web Interface:     http://localhost:${PORT}/"
    echo "  Health Check:      http://localhost:${PORT}/health"
    echo "  System Info:       http://localhost:${PORT}/sysinfo"
    echo "  Capabilities:      http://localhost:${PORT}/capabilities"
    echo "  Kernel Modules:    http://localhost:${PORT}/modules"
    echo "  API RCE:           http://localhost:${PORT}/api/rce (POST)"
    echo ""

    echo "Useful Commands:"
    echo "  View logs:         docker logs -f ${CONTAINER_NAME}"
    echo "  Execute shell:     docker exec -it ${CONTAINER_NAME} /bin/bash"
    echo "  Stop container:    docker-compose down"
    echo "  Run exploit:       python3 exploit.py"
    echo ""

    echo "Testing the RCE vulnerability:"
    echo "  curl -X POST http://localhost:${PORT}/api/rce \\"
    echo "       -H 'Content-Type: application/json' \\"
    echo "       -d '{\"command\": \"whoami\"}'"
    echo ""

    print_warning "This container has dangerous capabilities and vulnerabilities!"
    print_warning "Use only in isolated testing environments."
}

# Main execution
main() {
    case "${1:-deploy}" in
        "deploy")
            print_banner
            check_requirements
            cleanup
            build_and_deploy
            test_deployment
            show_usage_info
            ;;
        "cleanup")
            print_status "Cleaning up deployment..."
            docker-compose down || true
            cleanup
            print_status "Cleanup completed"
            ;;
        "logs")
            docker logs -f ${CONTAINER_NAME}
            ;;
        "shell")
            docker exec -it ${CONTAINER_NAME} /bin/bash
            ;;
        "test")
            test_deployment
            ;;
        "exploit")
            if [ -f "exploit.py" ]; then
                python3 exploit.py "http://localhost:${PORT}"
            else
                print_error "exploit.py not found"
                exit 1
            fi
            ;;
        "help"|"-h"|"--help")
            echo "Usage: $0 [command]"
            echo ""
            echo "Commands:"
            echo "  deploy    Build and deploy the vulnerable container (default)"
            echo "  cleanup   Stop and remove the container and images"
            echo "  logs      Show container logs"
            echo "  shell     Open shell in the container"
            echo "  test      Test the deployment"
            echo "  exploit   Run the exploit script"
            echo "  help      Show this help message"
            ;;
        *)
            print_error "Unknown command: $1"
            echo "Use '$0 help' for usage information"
            exit 1
            ;;
    esac
}

# Handle Ctrl+C gracefully
trap 'echo -e "\n${YELLOW}Interrupted by user${NC}"; exit 1' INT

# Execute main function
main "$@"
