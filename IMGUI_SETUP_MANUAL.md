# ImGui Hybrid Architecture - Manual Setup Guide

## **Current Status**
✅ **Phase 1.1**: Requirements.txt updated with ImGui dependencies  
⚠️ **Phase 1.2**: Python 3.12 environment needed (current: Python 3.14)  
⏳ **Phase 1.3**: ImGui package installation pending  

## **Python Version Issue**
The current system is running Python 3.14.0, but ImGui packages may not have precompiled wheels for this version yet. **Python 3.12 is recommended** for best compatibility.

## **Manual Setup Instructions**

### **Option 1: Use Python 3.12 (Recommended)**
1. **Install Python 3.12** from [python.org](https://python.org)
2. **Create new virtual environment**:
   ```bash
   # Remove current venv
   Remove-Item -Recurse -Force venv
   
   # Create Python 3.12 environment
   py -3.12 -m venv venv
   
   # Activate environment
   venv\Scripts\activate
   ```
3. **Install dependencies**:
   ```bash
   pip install --upgrade pip
   pip install imgui[pygame]>=2.0.0 PyOpenGL>=3.1.0 PyOpenGL-accelerate>=3.1.0
   pip install -r requirements.txt
   ```

### **Option 2: Try Building from Source (Advanced)**
If you must use Python 3.14:
```bash
# Install Visual C++ Build Tools first
# Then try:
pip install --no-binary=imgui imgui[pygame]>=2.0.0
pip install PyOpenGL>=3.1.0 PyOpenGL-accelerate>=3.1.0
```

### **Option 3: Use Conda (Alternative)**
```bash
# Create conda environment
conda create -n turboshells python=3.12
conda activate turboshells

# Install packages
conda install pygame
pip install imgui[pygame]>=2.0.0 PyOpenGL>=3.1.0
```

## **Verification Commands**
After installation, verify with:
```bash
# Test ImGui import
python -c "import imgui; import pygame; import OpenGL.GL as gl; print('ImGui OK')"

# Run integration test
python test_imgui_integration.py
```

## **Next Steps After Setup**
1. **Phase 2**: Input Hijack System implementation
2. **Phase 3**: Overlay Rendering Pipeline
3. **Phase 4**: State Connection & Data Binding

## **Troubleshooting**

### **Common Issues**
- **"failed to locate pyvenv.cfg"**: Virtual environment corrupted, recreate it
- **"metadata-generation-failed"**: Python version compatibility, use Python 3.12
- **OpenGL errors**: Install graphics drivers or use software rendering

### **Alternative ImGui Packages**
If standard imgui fails:
```bash
pip install imgui-py
# or
pip install pygame-imgui
```

## **Environment Variables (Optional)**
Set for better performance:
```bash
set PYGAME_HIDE_SUPPORT_PROMPT=1
set SDL_AUDIODRIVER=directsound
```

---

**Once setup is complete, run `python test_imgui_integration.py` to verify the integration before proceeding to Phase 2.**
