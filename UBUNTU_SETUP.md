# Ubuntu Setup Guide for RAG-LLM Project

This guide will help you set up the RAG-LLM project on Ubuntu 18.04+ systems.

## 🚀 Quick Setup

### Option 1: Automated Setup (Recommended)

1. **Clone the repository:**
   ```bash
   git clone https://github.com/Asifptm/Ragllm-model.git
   cd Ragllm-model
   ```

2. **Make the manager script executable:**
   ```bash
   chmod +x ragllm_manager.sh
   ```

3. **Run the manager script:**
   ```bash
   ./ragllm_manager.sh
   ```

4. **Choose option 12** to create the Ubuntu setup script, then run:
   ```bash
   ./ubuntu_setup.sh
   ```

### Option 2: Manual Setup

1. **Update package list:**
   ```bash
   sudo apt-get update
   ```

2. **Install essential packages:**
   ```bash
   sudo apt-get install -y python3 python3-pip python3-venv python3-dev git curl wget build-essential
   ```

3. **Clone the repository:**
   ```bash
   git clone https://github.com/Asifptm/Ragllm-model.git
   cd Ragllm-model
   ```

4. **Create virtual environment:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

5. **Install Python dependencies:**
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

6. **Create environment file:**
   ```bash
   cp env.example .env
   # Edit .env with your actual credentials
   nano .env
   ```

## 🎯 Using the Project Manager

The `ragllm_manager.sh` script provides a menu-driven interface for managing your RAG-LLM project:

### Available Options:

1. **Create .env file from template** - Sets up your environment configuration
2. **Update environment variable** - Modify specific environment variables
3. **Delete environment variable** - Remove unwanted environment variables
4. **Show file content** - Display contents of any project file
5. **Search in files** - Search for text across project files
6. **Set working directory** - Change the project working directory
7. **Show project status** - Display current project status
8. **Check system requirements** - Verify Ubuntu system setup
9. **Install system dependencies** - Install Ubuntu packages
10. **Install Python dependencies** - Install Python packages
11. **Clone repository from GitHub** - Clone the project repository
12. **Create Ubuntu setup script** - Generate automated setup script
13. **Run application** - Start the FastAPI server
14. **Exit** - Close the manager

## 🔧 Environment Configuration

After cloning the repository, you need to configure your environment:

1. **Copy the example environment file:**
   ```bash
   cp env.example .env
   ```

2. **Edit the .env file with your credentials:**
   ```bash
   nano .env
   ```

3. **Required configurations:**
   - `MONGODB_URI` - Your MongoDB connection string
   - `OPENAI_API_KEY` - Your OpenAI API key
   - `SERPER_API_KEY` - Your Serper API key for web search
   - `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY` - AWS credentials
   - `S3_BUCKET_NAME` - Your S3 bucket name

## 🚀 Running the Application

1. **Activate virtual environment:**
   ```bash
   source venv/bin/activate
   ```

2. **Start the FastAPI server:**
   ```bash
   uvicorn api:app --host 0.0.0.0 --port 8000 --reload
   ```

3. **Access the API:**
   - API Base: `http://localhost:8000`
   - Interactive Docs: `http://localhost:8000/docs`

## 🧪 Testing the Setup

Test your setup with a simple API call:

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"query":"What is Retrieval-Augmented Generation?"}'
```

## 📁 Project Structure

```
Ragllm-model/
├── api.py                 # FastAPI application
├── chat.py               # Chat orchestration logic
├── data.py               # Data service and MongoDB integration
├── ingest.py             # Document ingestion pipeline
├── requirements.txt      # Python dependencies
├── env.example          # Environment template
├── ragllm_manager.sh    # Project manager script
├── ubuntu_setup.sh      # Ubuntu setup script (generated)
└── tests/               # Test files
```

## 🆘 Troubleshooting

### Common Issues:

1. **Permission denied when running scripts:**
   ```bash
   chmod +x ragllm_manager.sh
   chmod +x ubuntu_setup.sh
   ```

2. **Python3 not found:**
   ```bash
   sudo apt-get install python3
   ```

3. **pip3 not found:**
   ```bash
   sudo apt-get install python3-pip
   ```

4. **Virtual environment issues:**
   ```bash
   sudo apt-get install python3-venv
   ```

5. **Build tools missing:**
   ```bash
   sudo apt-get install build-essential python3-dev
   ```

## 🔗 Useful Commands

- **Check system requirements:** `./ragllm_manager.sh` → Option 8
- **Install dependencies:** `./ragllm_manager.sh` → Option 9
- **View project status:** `./ragllm_manager.sh` → Option 7
- **Run application:** `./ragllm_manager.sh` → Option 13

## 📞 Support

For issues and questions:
- GitHub Repository: https://github.com/Asifptm/Ragllm-model.git
- Create an issue on GitHub for bug reports or feature requests

---

**Happy coding! 🎉**
