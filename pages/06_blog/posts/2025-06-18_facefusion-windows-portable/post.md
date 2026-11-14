# Step-by-Step Installation of FaceFusion on Windows

FaceFusion is a next-generation face analysis, enhancement, and swapping framework built on ONNX Runtime and modern deep learning models.

## Prerequisites

Before beginning, ensure your workstation meets the following hardware and software requirements:
- **GPU**: NVIDIA RTX 3000 series or newer (recommended 8GB+ VRAM)
- **CUDA Toolkit**: 11.8 or 12.x installed with cuDNN
- **Python**: 3.10.x (recommended for maximum library compatibility)
- **Git for Windows**

---

## 1. Clone the Repository

Clone FaceFusion into an isolated drive with ample NVMe storage:

```bash
git clone https://github.com/FaceFusion/FaceFusion.git
cd FaceFusion
```

## 2. Create an Isolated Virtual Environment

Never install AI pip dependencies directly into your system Python. Always create an isolated virtual environment:

```bash
python -m venv myenv
# Activate the environment in PowerShell or Command Prompt
myenv/Scripts/activate
```

---


## 3. Automated Dependency Installation

FaceFusion includes a built-in installer script that configures `onnxruntime-gpu` and PyTorch automatically:

```bash
python install.py --onnxruntime cuda
```

<div class="blog-grid-2">
  <div class="col-text">
    <h3>Acceleration Providers</h3>
    <p>By specifying <code>--onnxruntime cuda</code>, the installer configures TensorRT and CUDA execution providers for real-time inference on NVIDIA GPUs. If using DirectML on AMD GPUs, pass <code>--onnxruntime directml</code>.</p>
  </div>
  <div class="col-media">
    <img src="cover.png" alt="FaceFusion Terminal Launch">
  </div>
</div>

---

## 4. Running the Web UI

Launch the interface by activating your environment and running:

```bash
python facefusion.py run --open-browser
```

> **Production Tip:** Use the `--execution-providers cuda` flag and enable face mask padding in the settings tab to eliminate edge blending seams on moving feature film plates.
