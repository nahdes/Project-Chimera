#!/bin/bash
# chimera-setup.sh - Environment setup and management for Chimera project

# Exit on error
set -e

# Project configuration
PROJECT_ROOT=$(dirname "$(realpath "$0")")
VENV_DIR=".venv"
PYTHON_VERSION="3.11"
REQUIREMENTS_FILE="requirements.txt"

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

# Function to print status messages
print_status() {
    echo -e "${GREEN}✓${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1" >&2
}

# Check if UV is installed
check_uv() {
    if ! command -v uv &> /dev/null; then
        print_error "UV package manager not found. Please install UV first."
        echo "Installation instructions:"
        echo "  curl -LsSf https://astral.sh/uv/install.sh | sh"
        exit 1
    fi
}

# Create virtual environment
setup_venv() {
    echo -e "\n${YELLOW}Setting up Python virtual environment...${NC}"
    
    # Check if virtual environment already exists
    if [ -d "$VENV_DIR" ]; then
        print_warning "Virtual environment already exists. Reusing existing environment."
        return 0
    fi
    
    # Create virtual environment
    uv venv "$VENV_DIR" --python "$PYTHON_VERSION" || {
        print_error "Failed to create virtual environment"
        exit 1
    }
    
    print_status "Virtual environment created at $VENV_DIR"
}

# Install project dependencies
install_deps() {
    echo -e "\n${YELLOW}Installing project dependencies...${NC}"
    
    # Check if requirements file exists
    if [ ! -f "$REQUIREMENTS_FILE" ]; then
        print_warning "No requirements.txt found. Creating a basic one."
        echo "uv" > "$REQUIREMENTS_FILE"
        echo "pydantic" >> "$REQUIREMENTS_FILE"
        echo "rich" >> "$REQUIREMENTS_FILE"
        echo "python-dotenv" >> "$REQUIREMENTS_FILE"
    fi
    
    # Install dependencies
    "$VENV_DIR/bin/uv" pip install -r "$REQUIREMENTS_FILE" || {
        print_error "Failed to install dependencies"
        exit 1
    }
    
    print_status "Dependencies installed successfully"
}

# Activate environment (for manual use)
activate_env() {
    echo -e "\n${YELLOW}To activate the environment, run:${NC}"
    echo "  source $VENV_DIR/bin/activate"
}

# Run project services
run_services() {
    echo -e "\n${YELLOW}Starting Chimera services...${NC}"
    
    # Check if services exist
    if [ ! -d "services" ]; then
        print_error "Services directory not found. Expected at $PROJECT_ROOT/services"
        exit 1
    fi
    
    # Start services
    echo "Starting orchestrator..."
    "$VENV_DIR/bin/uv" run python services/orchestrator/main.py &
    ORCH_PID=$!
    
    echo "Starting planner..."
    "$VENV_DIR/bin/uv" run python services/planner/main.py &
    PLANNER_PID=$!
    
    echo "Starting worker..."
    "$VENV_DIR/bin/uv" run python services/worker/main.py &
    WORKER_PID=$!
    
    echo "Starting judge..."
    "$VENV_DIR/bin/uv" run python services/judge/main.py &
    JUDGE_PID=$!
    
    # Store PIDs for cleanup
    echo $ORCH_PID > .chimera_pids
    echo $PLANNER_PID >> .chimera_pids
    echo $WORKER_PID >> .chimera_pids
    echo $JUDGE_PID >> .chimera_pids
    
    print_status "All services started successfully"
    echo "Press Ctrl+C to stop services"
    
    # Trap Ctrl+C to stop services
    trap 'stop_services' INT
    wait
}

# Stop running services
stop_services() {
    echo -e "\n${YELLOW}Stopping Chimera services...${NC}"
    
    if [ -f ".chimera_pids" ]; then
        while read pid; do
            kill -9 $pid 2>/dev/null || true
        done < ".chimera_pids"
        rm -f .chimera_pids
    fi
    
    print_status "All services stopped"
    exit 0
}

# Initialize the project
initialize_project() {
    echo -e "\n${YELLOW}Initializing Chimera project...${NC}"
    
    # Create basic structure if missing
    if [ ! -d "specs" ]; then
        mkdir -p specs
        echo "# Project specifications" > specs/_meta.md
        echo "# Vision and constraints" > specs/vision.md
        print_status "Created specs directory"
    fi
    
    if [ ! -d "skills" ]; then
        mkdir -p skills
        echo "# Agent skill specifications" > skills/README.md
        print_status "Created skills directory"
    fi
    
    if [ ! -d "services" ]; then
        mkdir -p services/orchestrator services/planner services/worker services/judge
        print_status "Created services directory structure"
    fi
    
    if [ ! -d "tests" ]; then
        mkdir -p tests/unit tests/integration tests/e2e
        print_status "Created tests directory structure"
    fi
    
    # Create requirements file if missing
    if [ ! -f "$REQUIREMENTS_FILE" ]; then
        echo "uv" > "$REQUIREMENTS_FILE"
        echo "pydantic" >> "$REQUIREMENTS_FILE"
        echo "rich" >> "$REQUIREMENTS_FILE"
        echo "python-dotenv" >> "$REQUIREMENTS_FILE"
        echo "pytest" >> "$REQUIREMENTS_FILE"
        echo "pytest-asyncio" >> "$REQUIREMENTS_FILE"
        print_status "Created basic requirements.txt"
    fi
    
    print_status "Project initialized successfully"
}

# Main execution
main() {
    echo -e "\n${YELLOW}=== Chimera Project Setup ===${NC}"
    
    # Check UV installation
    check_uv
    
    # Initialize project structure if needed
    initialize_project
    
    # Setup virtual environment
    setup_venv
    
    # Install dependencies
    install_deps
    
    # Show activation instructions
    activate_env
    
    # Show usage instructions
    echo -e "\n${YELLOW}=== Setup Complete ===${NC}"
    echo "To start the project:"
    echo "  ./chimera-setup.sh run"
    echo ""
    echo "To stop running services:"
    echo "  Ctrl+C in the terminal where services are running"
    echo ""
    echo "For development environment:"
    echo "  source .venv/bin/activate"
    echo "  uv run python [your_script.py]"
}

# Run the main function
main "$@"