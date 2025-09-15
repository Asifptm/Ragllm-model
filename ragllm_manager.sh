#!/bin/bash

# RAG-LLM Project Manager Script
# Author: Asif
# GitHub Repository: https://github.com/Asifptm/Ragllm-model.git
# Description: Menu-driven script for managing RAG-LLM project environment and operations
# Compatible with: Ubuntu 18.04+, Debian, and other Linux distributions

# Set default directory
RAGLLM_DIR="ragllm"
ENV_FILE=".env"
ENV_TEMPLATE="env.example"
GITHUB_REPO="https://github.com/Asifptm/Ragllm-model.git"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Function to print colored output
print_color() {
    local color=$1
    local message=$2
    echo -e "${color}${message}${NC}"
}

# Function to check system requirements
check_system_requirements() {
    print_color $BLUE "Checking system requirements..."
    
    # Check OS
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        if [ -f /etc/os-release ]; then
            . /etc/os-release
            print_color $GREEN "✅ Operating System: $PRETTY_NAME"
        else
            print_color $YELLOW "⚠️  Linux detected but OS version unknown"
        fi
    else
        print_color $YELLOW "⚠️  Non-Linux system detected. Some features may not work."
    fi
    
    # Check Python
    if command -v python3 >/dev/null 2>&1; then
        python_version=$(python3 --version 2>&1)
        print_color $GREEN "✅ $python_version"
    else
        print_color $RED "❌ Python3 not found"
    fi
    
    # Check pip
    if command -v pip3 >/dev/null 2>&1; then
        print_color $GREEN "✅ pip3 available"
    else
        print_color $RED "❌ pip3 not found"
    fi
    
    # Check git
    if command -v git >/dev/null 2>&1; then
        git_version=$(git --version)
        print_color $GREEN "✅ $git_version"
    else
        print_color $RED "❌ Git not found"
    fi
    
    echo
}

# Function to print header
print_header() {
    clear
    print_color $CYAN "=========================================="
    print_color $CYAN "    RAG-LLM Project Manager v1.0"
    print_color $CYAN "    GitHub: https://github.com/Asifptm/Ragllm-model.git"
    print_color $CYAN "=========================================="
    echo
}

# Function to create .env file from template
create_env_file() {
    print_color $YELLOW "Creating .env file from template..."
    
    if [ ! -f "$ENV_TEMPLATE" ]; then
        print_color $RED "Error: $ENV_TEMPLATE not found!"
        return 1
    fi
    
    if [ -f "$ENV_FILE" ]; then
        print_color $YELLOW "$ENV_FILE already exists. Do you want to overwrite it? (y/n)"
        read -r response
        if [[ ! "$response" =~ ^[Yy]$ ]]; then
            print_color $BLUE "Operation cancelled."
            return 0
        fi
    fi
    
    cp "$ENV_TEMPLATE" "$ENV_FILE"
    print_color $GREEN "✅ .env file created successfully from $ENV_TEMPLATE"
    print_color $YELLOW "⚠️  Please edit the .env file with your actual credentials!"
}

# Function to update environment variable
update_env_var() {
    print_color $YELLOW "Update Environment Variable"
    echo
    
    if [ ! -f "$ENV_FILE" ]; then
        print_color $RED "Error: $ENV_FILE not found! Please create it first."
        return 1
    fi
    
    print_color $BLUE "Available environment variables:"
    grep -E "^[A-Z_]+=" "$ENV_FILE" | cut -d'=' -f1 | nl
    echo
    
    print_color $YELLOW "Enter the variable name to update:"
    read -r var_name
    
    if ! grep -q "^$var_name=" "$ENV_FILE"; then
        print_color $RED "Variable '$var_name' not found in $ENV_FILE"
        return 1
    fi
    
    print_color $YELLOW "Enter new value for $var_name:"
    read -r var_value
    
    # Update the variable in .env file
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        sed -i '' "s/^$var_name=.*/$var_name=$var_value/" "$ENV_FILE"
    else
        # Linux
        sed -i "s/^$var_name=.*/$var_name=$var_value/" "$ENV_FILE"
    fi
    
    print_color $GREEN "✅ Updated $var_name=$var_value"
}

# Function to delete environment variable
delete_env_var() {
    print_color $YELLOW "Delete Environment Variable"
    echo
    
    if [ ! -f "$ENV_FILE" ]; then
        print_color $RED "Error: $ENV_FILE not found! Please create it first."
        return 1
    fi
    
    print_color $BLUE "Available environment variables:"
    grep -E "^[A-Z_]+=" "$ENV_FILE" | cut -d'=' -f1 | nl
    echo
    
    print_color $YELLOW "Enter the variable name to delete:"
    read -r var_name
    
    if ! grep -q "^$var_name=" "$ENV_FILE"; then
        print_color $RED "Variable '$var_name' not found in $ENV_FILE"
        return 1
    fi
    
    print_color $RED "Are you sure you want to delete '$var_name'? (y/n)"
    read -r response
    if [[ "$response" =~ ^[Yy]$ ]]; then
        # Delete the line containing the variable
        if [[ "$OSTYPE" == "darwin"* ]]; then
            # macOS
            sed -i '' "/^$var_name=/d" "$ENV_FILE"
        else
            # Linux
            sed -i "/^$var_name=/d" "$ENV_FILE"
        fi
        print_color $GREEN "✅ Deleted $var_name"
    else
        print_color $BLUE "Operation cancelled."
    fi
}

# Function to show file content
show_file_content() {
    print_color $YELLOW "Show File Content"
    echo
    
    print_color $BLUE "Available files:"
    ls -la | grep -E "\.(py|txt|md|yml|yaml|json|env|example)$" | nl
    echo
    
    print_color $YELLOW "Enter filename to display:"
    read -r filename
    
    if [ ! -f "$filename" ]; then
        print_color $RED "Error: File '$filename' not found!"
        return 1
    fi
    
    print_color $GREEN "Content of $filename:"
    print_color $CYAN "----------------------------------------"
    cat "$filename"
    print_color $CYAN "----------------------------------------"
}

# Function to search in files
search_in_files() {
    print_color $YELLOW "Search in Files"
    echo
    
    print_color $YELLOW "Enter search term:"
    read -r search_term
    
    print_color $YELLOW "Enter file pattern (e.g., *.py, *.txt, or * for all files):"
    read -r file_pattern
    
    if [ -z "$file_pattern" ]; then
        file_pattern="*"
    fi
    
    print_color $GREEN "Searching for '$search_term' in $file_pattern files..."
    echo
    
    # Search in files
    if command -v grep >/dev/null 2>&1; then
        grep -r -n -i --include="$file_pattern" "$search_term" . 2>/dev/null | while read -r line; do
            print_color $BLUE "$line"
        done
    else
        print_color $RED "grep command not found!"
        return 1
    fi
}

# Function to set working directory
set_directory() {
    print_color $YELLOW "Set Working Directory"
    echo
    
    print_color $YELLOW "Enter directory name (default: ragllm):"
    read -r new_dir
    
    if [ -z "$new_dir" ]; then
        new_dir="ragllm"
    fi
    
    RAGLLM_DIR="$new_dir"
    
    if [ ! -d "$RAGLLM_DIR" ]; then
        print_color $YELLOW "Directory '$RAGLLM_DIR' doesn't exist. Create it? (y/n)"
        read -r response
        if [[ "$response" =~ ^[Yy]$ ]]; then
            mkdir -p "$RAGLLM_DIR"
            print_color $GREEN "✅ Created directory '$RAGLLM_DIR'"
        fi
    fi
    
    print_color $GREEN "✅ Working directory set to: $RAGLLM_DIR"
}

# Function to show project status
show_status() {
    print_color $YELLOW "Project Status"
    echo
    
    print_color $BLUE "Current directory: $(pwd)"
    print_color $BLUE "Working directory: $RAGLLM_DIR"
    echo
    
    print_color $BLUE "Environment file status:"
    if [ -f "$ENV_FILE" ]; then
        print_color $GREEN "✅ $ENV_FILE exists"
        print_color $BLUE "Variables configured: $(grep -c "^[A-Z_]*=" "$ENV_FILE")"
    else
        print_color $RED "❌ $ENV_FILE not found"
    fi
    echo
    
    print_color $BLUE "Template file status:"
    if [ -f "$ENV_TEMPLATE" ]; then
        print_color $GREEN "✅ $ENV_TEMPLATE exists"
    else
        print_color $RED "❌ $ENV_TEMPLATE not found"
    fi
    echo
    
    print_color $BLUE "Project files:"
    ls -la | grep -E "\.(py|txt|md|yml|yaml|json|sh)$" | wc -l | xargs echo "Total files:"
}

# Function to run the application
run_application() {
    print_color $YELLOW "Run RAG-LLM Application"
    echo
    
    if [ ! -f "$ENV_FILE" ]; then
        print_color $RED "Error: $ENV_FILE not found! Please create it first."
        return 1
    fi
    
    print_color $BLUE "Starting FastAPI server..."
    print_color $YELLOW "Press Ctrl+C to stop the server"
    echo
    
    # Check if virtual environment exists
    if [ -d "venv" ]; then
        print_color $GREEN "Activating virtual environment..."
        source venv/bin/activate 2>/dev/null || source venv/Scripts/activate 2>/dev/null
    fi
    
    # Start the server
    uvicorn api:app --host 0.0.0.0 --port 8000 --reload
}

# Function to check and install system dependencies (Ubuntu/Debian)
install_system_dependencies() {
    print_color $YELLOW "Install System Dependencies (Ubuntu/Debian)"
    echo
    
    print_color $BLUE "Checking system dependencies..."
    
    # Check if running on Ubuntu/Debian
    if ! command -v apt-get >/dev/null 2>&1; then
        print_color $YELLOW "⚠️  Not running on Ubuntu/Debian. Skipping system dependencies."
        return 0
    fi
    
    # Update package list
    print_color $BLUE "Updating package list..."
    sudo apt-get update
    
    # Install essential packages
    print_color $BLUE "Installing essential packages..."
    sudo apt-get install -y python3 python3-pip python3-venv git curl wget build-essential
    
    # Install Python development headers (needed for some packages)
    sudo apt-get install -y python3-dev
    
    print_color $GREEN "✅ System dependencies installed successfully!"
}

# Function to install Python dependencies
install_dependencies() {
    print_color $YELLOW "Install Python Dependencies"
    echo
    
    if [ ! -f "requirements.txt" ]; then
        print_color $RED "Error: requirements.txt not found!"
        return 1
    fi
    
    # Check if virtual environment exists
    if [ ! -d "venv" ]; then
        print_color $BLUE "Creating virtual environment..."
        python3 -m venv venv
    fi
    
    # Activate virtual environment
    print_color $BLUE "Activating virtual environment..."
    source venv/bin/activate
    
    # Upgrade pip
    print_color $BLUE "Upgrading pip..."
    pip install --upgrade pip
    
    # Install dependencies
    print_color $BLUE "Installing Python dependencies..."
    pip install -r requirements.txt
    
    if [ $? -eq 0 ]; then
        print_color $GREEN "✅ Dependencies installed successfully!"
    else
        print_color $RED "❌ Failed to install dependencies!"
    fi
}

# Function to clone repository
clone_repository() {
    print_color $YELLOW "Clone Repository from GitHub"
    echo
    
    print_color $BLUE "Repository: $GITHUB_REPO"
    print_color $YELLOW "Enter directory name to clone into (default: ragllm-model):"
    read -r clone_dir
    
    if [ -z "$clone_dir" ]; then
        clone_dir="ragllm-model"
    fi
    
    if [ -d "$clone_dir" ]; then
        print_color $RED "Directory '$clone_dir' already exists!"
        return 1
    fi
    
    print_color $BLUE "Cloning repository..."
    git clone "$GITHUB_REPO" "$clone_dir"
    
    if [ $? -eq 0 ]; then
        print_color $GREEN "✅ Repository cloned successfully to '$clone_dir'"
        print_color $BLUE "To work with the project:"
        print_color $BLUE "  cd $clone_dir"
        print_color $BLUE "  ./ragllm_manager.sh"
    else
        print_color $RED "❌ Failed to clone repository!"
    fi
}

# Function to show main menu
show_menu() {
    print_header
    print_color $GREEN "Main Menu:"
    echo
    print_color $BLUE "1. Create .env file from template"
    print_color $BLUE "2. Update environment variable"
    print_color $BLUE "3. Delete environment variable"
    print_color $BLUE "4. Show file content"
    print_color $BLUE "5. Search in files"
    print_color $BLUE "6. Set working directory"
    print_color $BLUE "7. Show project status"
    print_color $BLUE "8. Check system requirements"
    print_color $BLUE "9. Install system dependencies (Ubuntu/Debian)"
    print_color $BLUE "10. Install Python dependencies"
    print_color $BLUE "11. Clone repository from GitHub"
    print_color $BLUE "12. Create Ubuntu setup script"
    print_color $BLUE "13. Run application"
    print_color $BLUE "14. Exit"
    echo
    print_color $YELLOW "Enter your choice (1-14):"
}

# Main script loop
main() {
    while true; do
        show_menu
        read -r choice
        
        case $choice in
            1)
                create_env_file
                ;;
            2)
                update_env_var
                ;;
            3)
                delete_env_var
                ;;
            4)
                show_file_content
                ;;
            5)
                search_in_files
                ;;
            6)
                set_directory
                ;;
            7)
                show_status
                ;;
            8)
                check_system_requirements
                ;;
            9)
                install_system_dependencies
                ;;
            10)
                install_dependencies
                ;;
            11)
                clone_repository
                ;;
            12)
                create_ubuntu_setup
                ;;
            13)
                run_application
                ;;
            14)
                print_color $GREEN "Goodbye! 👋"
                exit 0
                ;;
            *)
                print_color $RED "Invalid choice! Please enter a number between 1-14."
                ;;
        esac
        
        echo
        print_color $YELLOW "Press Enter to continue..."
        read -r
    done
}

# Function to create Ubuntu setup script
create_ubuntu_setup() {
    print_color $YELLOW "Creating Ubuntu setup script..."
    
    cat > ubuntu_setup.sh << 'EOF'
#!/bin/bash

# Ubuntu Setup Script for RAG-LLM Project
# This script sets up the environment for the RAG-LLM project on Ubuntu

echo "🚀 Setting up RAG-LLM Project on Ubuntu..."

# Update package list
echo "📦 Updating package list..."
sudo apt-get update

# Install essential packages
echo "🔧 Installing essential packages..."
sudo apt-get install -y \
    python3 \
    python3-pip \
    python3-venv \
    python3-dev \
    git \
    curl \
    wget \
    build-essential \
    software-properties-common

# Clone the repository
echo "📥 Cloning RAG-LLM repository..."
git clone https://github.com/Asifptm/Ragllm-model.git
cd Ragllm-model

# Make the manager script executable
chmod +x ragllm_manager.sh

# Create virtual environment
echo "🐍 Creating Python virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "⚡ Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip

# Install Python dependencies
echo "📚 Installing Python dependencies..."
pip install -r requirements.txt

echo "✅ Setup complete!"
echo ""
echo "To start using the project:"
echo "1. cd Ragllm-model"
echo "2. ./ragllm_manager.sh"
echo ""
echo "Or run: source venv/bin/activate && uvicorn api:app --host 0.0.0.0 --port 8000 --reload"
EOF

    chmod +x ubuntu_setup.sh
    print_color $GREEN "✅ Ubuntu setup script created: ubuntu_setup.sh"
    print_color $BLUE "To use it: ./ubuntu_setup.sh"
}

# Check if script is being sourced or executed
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    # Script is being executed
    main
else
    # Script is being sourced
    print_color $GREEN "RAG-LLM Manager functions loaded. Use 'main' to start the menu."
fi
