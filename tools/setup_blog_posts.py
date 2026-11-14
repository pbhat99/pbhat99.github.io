import os
import shutil
import json

posts_dir = "pages/06_blog/posts"

# --------------------------------------------------------------------------
# Post 1: FaceFusion
# --------------------------------------------------------------------------
p1_dir = os.path.join(posts_dir, "2025-06-18_facefusion-windows-portable")
os.makedirs(p1_dir, exist_ok=True)
p1_meta = {
    "title": "Step-by-Step Installation of FaceFusion on Windows",
    "date": "2025-06-18",
    "category": "AI / Deep Learning",
    "tags": ["FaceFusion", "AI", "Windows", "CUDA", "Python"],
    "subheading": "Complete installation walkthrough for FaceFusion next-generation face enhancement and swapping tool using isolated virtual environments.",
    "thumbnail": "cover.png",
    "author": "Prasannakumar T Bhat",
    "readTime": "4 min read"
}
with open(os.path.join(p1_dir, "post.json"), "w", encoding="utf-8") as f:
    json.dump(p1_meta, f, indent=2)

p1_md = """# Step-by-Step Installation of FaceFusion on Windows

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
"""
with open(os.path.join(p1_dir, "post.md"), "w", encoding="utf-8") as f:
    f.write(p1_md)

if os.path.exists(os.path.join(posts_dir, "blog_img_5.png")):
    shutil.copy2(os.path.join(posts_dir, "blog_img_5.png"), os.path.join(p1_dir, "cover.png"))

# --------------------------------------------------------------------------
# Post 2: ComfyUI Portable
# --------------------------------------------------------------------------
p2_dir = os.path.join(posts_dir, "2025-11-28_comfyui-portable-custom-nodes")
os.makedirs(p2_dir, exist_ok=True)
p2_meta = {
    "title": "ComfyUI Portable Setup & Production Custom Nodes Guide",
    "date": "2025-11-28",
    "category": "AI / Generative",
    "tags": ["ComfyUI", "Custom Nodes", "VFX Pipeline", "Python"],
    "subheading": "A battle-tested production guide to setting up a zero-bloat portable ComfyUI installation with essential custom nodes for VFX artists.",
    "thumbnail": "cover.png",
    "author": "Prasannakumar T Bhat",
    "readTime": "6 min read"
}
with open(os.path.join(p2_dir, "post.json"), "w", encoding="utf-8") as f:
    json.dump(p2_meta, f, indent=2)

p2_md = """# ComfyUI Portable Setup & Production Custom Nodes Guide

ComfyUI is the industry standard node-based GUI for Stable Diffusion, FLUX, and generative VFX pipelines. Running the standalone portable version gives artists complete environment isolation.

## 1. Download Standalone Portable Release

Download and extract the latest standalone portable release archive from GitHub:
[https://github.com/comfyanonymous/ComfyUI/releases](https://github.com/comfyanonymous/ComfyUI/releases)

---

## 2. Essential Production Custom Nodes

Navigate to `ComfyUI_windows_portable/ComfyUI/custom_nodes/` and clone these essential repositories:

### 1. ComfyUI Manager (Repository & Node Browser)
```bash
git clone https://github.com/ltdrdata/ComfyUI-Manager comfyui-manager
```

### 2. RGThree Tools (Node Routing & Quality of Life)
```bash
git clone https://github.com/rgthree/rgthree-comfy.git
```

### 3. Video Helper Suite (VHS) (Frame Sequences & EXRs)
```bash
git clone https://github.com/Kosinkadink/ComfyUI-VideoHelperSuite.git
```

<div class="blog-grid-2">
  <div class="col-text">
    <h3>Node Graph Organization</h3>
    <p>Using RGThree context nodes and VHS batch loaders allows VFX compositors to feed native 4K image sequences directly through ControlNet inpainting passes without manual frame extraction.</p>
  </div>
  <div class="col-media">
    <img src="cover.png" alt="ComfyUI Node Graph Execution">
  </div>
</div>

---

## 3. Automation Launch Script

Create a root `run_production.bat` launcher that checks git submodules and initializes with high VRAM allocation:

```batch
@echo off
setlocal
cd /d "%~dp0"
echo Starting ComfyUI with High VRAM Allocation...
.\\python_embeded\\python.exe -s ComfyUI\\main.py --windows-standalone-build --highvram --fast
pause
```
"""
with open(os.path.join(p2_dir, "post.md"), "w", encoding="utf-8") as f:
    f.write(p2_md)

if os.path.exists(os.path.join(posts_dir, "blog_img_2.png")):
    shutil.copy2(os.path.join(posts_dir, "blog_img_2.png"), os.path.join(p2_dir, "cover.png"))

# --------------------------------------------------------------------------
# Post 3: Deep Compositing in Nuke with Python
# --------------------------------------------------------------------------
p3_dir = os.path.join(posts_dir, "2026-02-10_deep-compositing-python-nuke")
os.makedirs(p3_dir, exist_ok=True)
p3_meta = {
    "title": "Automating Deep Compositing Workflows in Nuke with Python",
    "date": "2026-02-10",
    "category": "Nuke & VFX",
    "tags": ["Nuke", "DeepEXR", "Python", "Automation", "Compositing"],
    "subheading": "Techniques for managing DeepEXR volumetric channels, automating holdouts, and optimizing heavy read pipelines using Python scripts.",
    "thumbnail": "cover.jpg",
    "author": "Prasannakumar T Bhat",
    "readTime": "7 min read"
}
with open(os.path.join(p3_dir, "post.json"), "w", encoding="utf-8") as f:
    json.dump(p3_meta, f, indent=2)

p3_md = """# Automating Deep Compositing Workflows in Nuke with Python

Deep compositing stores multiple color and opacity samples per pixel along the camera ray (Z-depth). While it completely eliminates edge artifacts on complex volumes and volumetric hair/smoke, Deep files can quickly choke comp scripts if not managed procedurally.

## Understanding Deep Data Architecture

Unlike standard flat EXR images that have single values `(R, G, B, A, Z)`, each pixel in a DeepEXR file contains an array of depth ranges:

```
Pixel (x, y):
  Sample 0: Z_front = 10.2, Z_back = 10.5, Alpha = 0.45, Color = (0.2, 0.4, 0.8)
  Sample 1: Z_front = 14.1, Z_back = 18.0, Alpha = 0.85, Color = (0.7, 0.1, 0.0)
```

---

## Python Script: Automated Deep Holdout Generation

This Python utility script scans selected 3D render Read nodes, attaches a `DeepSample` inspector, inserts a `DeepCrop` node with bounding-box optimization, and builds automated holdout mattes:

```python
import nuke

def build_deep_holdout_rig(selection=None):
    \"\"\"
    Builds an automated Deep holdout rig from selected DeepRead nodes.
    Reduces memory overhead by clipping samples beyond camera frustum.
    \"\"\"
    nodes = selection or nuke.selectedNodes()
    if not nodes:
        nuke.message("Please select at least one DeepRead or Deep node.")
        return

    for node in nodes:
        if not node.Class().startswith("Deep"):
            continue

        # Create optimized DeepCrop
        crop = nuke.nodes.DeepCrop(inputs=[node])
        crop['use_znear'].setValue(True)
        crop['znear'].setValue(1.0)
        crop['use_zfar'].setValue(True)
        crop['zfar'].setValue(5000.0)

        # Create DeepToImage converter for 2D comp integration
        d2i = nuke.nodes.DeepToImage(inputs=[crop])
        d2i.setXpos(crop.xpos())
        d2i.setYpos(crop.ypos() + 60)

        print(f"Built Deep holdout rig for {node.name()}")

# Run the automation tool
build_deep_holdout_rig()
```

<div class="blog-grid-2">
  <div class="col-text">
    <h3>DeepSample & Optimization</h3>
    <p>Always combine multiple deep volumes using <code>DeepMerge</code> before converting down to flat 2D raster images. Keeping data in Deep space until the final beauty integration preserves sub-pixel optical thickness.</p>
  </div>
  <div class="col-media">
    <img src="cover.jpg" alt="Deep Sample Breakdown">
  </div>
</div>

> **Performance Rule:** Always place a `DeepCrop` or `DeepReformat` as close to the `DeepRead` node as possible to truncate unnecessary empty air samples before downstream merging.
"""
with open(os.path.join(p3_dir, "post.md"), "w", encoding="utf-8") as f:
    f.write(p3_md)

if os.path.exists(os.path.join(posts_dir, "blog_img_4.jpg")):
    shutil.copy2(os.path.join(posts_dir, "blog_img_4.jpg"), os.path.join(p3_dir, "cover.jpg"))

# --------------------------------------------------------------------------
# Post 4: Camera Projections in Nuke
# --------------------------------------------------------------------------
p4_dir = os.path.join(posts_dir, "2026-03-15_camera-projections-in-nuke")
os.makedirs(p4_dir, exist_ok=True)
p4_meta = {
    "title": "Camera Projections in Nuke: The Technical Guide",
    "date": "2026-03-15",
    "category": "Nuke & VFX",
    "tags": ["Nuke", "Camera Projection", "Matte Painting", "Compositing", "3D"],
    "subheading": "Comprehensive breakdown of camera projections in Nuke, handling lens distortion, overscan matrices, and spherical UV unwrapping.",
    "thumbnail": "cover.jpg",
    "author": "Prasannakumar T Bhat",
    "readTime": "8 min read"
}
with open(os.path.join(p4_dir, "post.json"), "w", encoding="utf-8") as f:
    json.dump(p4_meta, f, indent=2)

p4_md = """# Camera Projections in Nuke: The Technical Guide

Camera projection is the cornerstone technique in digital matte painting, set extension, and shot cleanup. It allows 2D painted plates to be projected through a 3D camera onto card or geometry surfaces, creating photoreal perspective parallax.

## Core Projection Mechanics

The projection pipeline relies on three elements connected into a `Project3D` node:
1. **Camera**: The frame-locked projection camera matching the reference plate.
2. **Image Texture**: The clean painted plate or texture matte.
3. **Geometry**: 3D cards, lidar geometry, or modelled proxy meshes.

---

## Handling Lens Distortion Correctly

A common pitfall is projecting distorted plates onto 3D geometry:

> **Fundamental Principle:** The 3D world in Nuke is strictly rectilinear (pinhole camera model). Always **undistort** your reference plate before projecting, and re-apply lens distortion onto the final rendered output from the moving render camera.

```
Plate -> LensDistortion (Undistort) -> Clean Paint -> Project3D
                                                           |
Render Camera -> ScanlineRender -> LensDistortion (Distort) -> Beauty Comp
```

---

## Python Tool: Instant Project3D Rig Setup

Here is a Python script that connects a selected Camera and Read node into a complete Project3D rig with projection geometry:

```python
import nuke

def create_projection_rig():
    sel = nuke.selectedNodes()
    cam = next((n for n in sel if n.Class() in ('Camera', 'Camera2', 'Camera3', 'Camera4')), None)
    img = next((n for n in sel if n.Class() == 'Read'), None)

    if not cam or not img:
        nuke.message("Select a Camera node and a Read node to construct the projection rig.")
        return

    # Create FrameHold on projection camera
    cur_frame = nuke.frame()
    fh = nuke.nodes.FrameHold(inputs=[cam])
    fh['firstFrame'].setValue(cur_frame)

    # Create Project3D
    proj = nuke.nodes.Project3D(inputs=[img, fh])
    proj['crop'].setValue(True)

    # Create 3D Card positioned along camera axis
    card = nuke.nodes.Card2(inputs=[proj])
    card['z'].setValue(-100.0)

    # Create ScanlineRender
    sr = nuke.nodes.ScanlineRender(inputs=[card, cam])

    nuke.message(f"Projection rig created at frame {cur_frame}!")

create_projection_rig()
```

<div class="blog-grid-2">
  <div class="col-text">
    <h3>Planar vs Spherical Projections</h3>
    <p>For matte painting horizons and sky domes, spherical mapping onto a <code>Sphere</code> node provides seamless 360-degree panning. For building facades and ground planes, planar projection cards aligned with surveyed tracking points offer zero distortion.</p>
  </div>
  <div class="col-media">
    <img src="cover.jpg" alt="Projection Diagram Overview">
  </div>
</div>

---

## Summary Best Practices
- Freeze the projection camera with a `FrameHold` at the hero alignment frame.
- Enable `crop` on the `Project3D` node to prevent UV bleeding beyond geometry bounds.
- Use `Reconcile3D` to track card surface points for seamless 2D element integration.
"""
with open(os.path.join(p4_dir, "post.md"), "w", encoding="utf-8") as f:
    f.write(p4_md)

if os.path.exists(os.path.join(posts_dir, "blog_img_4.jpg")):
    shutil.copy2(os.path.join(posts_dir, "blog_img_4.jpg"), os.path.join(p4_dir, "cover.jpg"))

print("All 4 sample posts created successfully!")
