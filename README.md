# Subtitle AI Translator

A Python application that uses AI to translate subtitles with a React frontend for easy interaction.

## Prerequisites

- Python 3.8 or higher
- Node.js 16 or higher
- npm 7 or higher
- For GPU support: NVIDIA GPU with CUDA capability

## Installation

### Step 1: Clone the repository

```bash
git clone https://github.com/ach-raf/subtitle_AI_translator.git
cd subtitle_AI_translator
```

### Step 2: Install uv (Python package installer)

#### Windows:

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

#### Linux/macOS:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Step 3: Set up the backend

First, determine if you have a compatible NVIDIA GPU:

1. For Windows, open Command Prompt and run: `nvidia-smi`
2. For Linux, open terminal and run: `nvidia-smi`

If the command shows your GPU information, you can use the GPU version. If you get an error or don't have an NVIDIA GPU, use the CPU version.

#### Windows:

```powershell
cd backend
uv venv
.\.venv\Scripts\activate

# Choose ONE of the following options:

# Option 1: If you have an NVIDIA GPU
uv pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu117

# Option 2: If you DO NOT have an NVIDIA GPU
uv pip install torch torchvision torchaudio

# Then install other requirements
uv install
```

#### Linux/macOS:

```bash
cd backend
uv venv
source .venv/bin/activate

# Choose ONE of the following options:

# Option 1: If you have an NVIDIA GPU
uv pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu117

# Option 2: If you DO NOT have an NVIDIA GPU
uv pip install torch torchvision torchaudio

# Then install other requirements
uv install
```

### Step 4: Set up the frontend

#### Windows/Linux/macOS:

```bash
cd frontend
npm install
```

## Running the Application

### Start the backend server

#### Windows:

```powershell
cd backend
.\.venv\Scripts\activate
python api.py
```

#### Linux/macOS:

```bash
cd backend
source .venv/bin/activate
python api.py
```

### Start the frontend development server

In a new terminal:

```bash
cd frontend
npm run dev
```

The application should now be running at `http://localhost:15571`

## Project Structure

```
subtitle_AI_translator/
├── backend/
│   ├── __pycache__
│   ├── downloads/
│   ├── library/
│   ├── models/
│   ├── uploads/
│   ├── api.py
│   ├── main.py
├── frontend/
│   ├── node_modules/
│   ├── public/
│   ├── src/
│   ├── .eslintrc.cjs
│   ├── components.json
│   ├── index.html
│   ├── package-lock.json
│   ├── package.json
│   ├── postcss.config.js
│   ├── README.md
│   ├── tailwind.config.js
│   ├── tsconfig.app.json
│   ├── tsconfig.json
│   ├── tsconfig.node.json
│   └── vite.config.ts
├── .env
├── .gitignore
├── .python-version
├── pyproject.toml
├── README.md
└── uv.lock
```

## Performance Expectations

- **GPU Version**: Faster translation speeds, recommended for large subtitle files
- **CPU Version**: Slower translation speeds but works on any computer

## Additional Notes

- The backend uses PyTorch for machine translation
- The frontend is built with React and Vite for fast development and performance
- uv is used for Python package management for improved installation speed

## Troubleshooting

1. If you're unsure whether you have a compatible GPU:

   - The GPU version will only work with NVIDIA GPUs
   - When in doubt, use the CPU version - it's slower but works everywhere

2. If you get "out of memory" errors with the GPU version:

   - Try using the CPU version instead
   - Or reduce the batch size if you're processing large subtitle files

3. For other issues, please check the project's [issue tracker](https://github.com/ach-raf/subtitle_AI_translator/issues) on GitHub

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
