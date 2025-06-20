
# Automated Pizza Counting System using YOLOv8 and Docker

This is a smart monitoring system developed to automatically count the number of pizzas sold from video footage. This project utilizes the YOLOv8 model for object detection and is containerized with Docker Compose for easy deployment.

## Table of Contents

* [Features](#features)
* [System Requirements](#system-requirements)
* [Directory Structure](#directory-structure)
* [Setup & Run](#setup--run)
    * [1. Clone Repository](#1-clone-repository)
    * [2. Prepare Data and Models](#2-prepare-data-and-models)
    * [3. Build and Run with Docker Compose](#3-build-and-run-with-docker-compose)
* [Configuration](#configuration)
* [View Results](#view-results)
* [Troubleshooting](#troubleshooting)

---

## Features

* Detects and counts pizzas in video using the YOLOv8 model.
* Supports custom counting regions for specific video files.
* Application containerized with Docker Compose for consistent and portable deployment.
* Exports processed videos with bounding boxes and pizza counts.

## System Requirements

To run this project, you need to have:

* **Docker Desktop** (for Windows/macOS) or **Docker Engine** (for Linux). You can download Docker from [docker.com/products/docker-desktop](https://www.docker.com/products/docker-desktop).

## Directory Structure

This project has the following directory structure:

```
your-pizza-counting-system/
├── data/
│   └── CH01.mp4             # Example input video
│   └── CH02_1.mp4
│   └── ...
├── weights/
│   └── best_yolov8.pt       # Your custom YOLOv8 model weights
│   └── yolov8n.pt           # Pre-trained YOLOv8 model (or other versions)
├── output_videos/           # Directory to store processed output videos
├── Count_Pizza.py           # Main application source code
├── Dockerfile               # Defines the Docker image environment
├── docker-compose.yml       # Docker Compose service configuration
├── requirements.txt         # List of required Python libraries
```

## Setup & Run

Follow the steps below to set up and run the system.

### 1. Clone Repository

First, clone this repository to your local machine:

```bash
git clone /AnLe08/EATLAB_Counting_Pizza
cd EATLAB_Counting_Pizza
```

### 2. Prepare Data and Models

* **Input Videos:**
    * Create a directory named `data` in the project root if it doesn't already exist.
    * Place the video files you want to process into the `data/` directory. Example: `CH01.mp4`.

* **Model Weights:**
    * Create a directory named `weights` in the project root if it doesn't already exist.
    * Place your YOLOv8 model weight files (e.g., `best_yolov8.pt` or `yolov8n.pt`) into the `weights/` directory.
    * The `yolov8n.pt` model might be downloaded automatically by the Ultralytics library if not present, but it's good practice to place it in `weights` for better management.

* **Output Directory:**
    * Create an empty directory named `output_videos` in the project root. This is where the processed videos will be saved.

### 3. Build and Run with Docker Compose

Navigate to the root directory of your project (`EATLAB_Counting_Pizza/`) in your Terminal or Command Prompt and run the following command:

```bash
docker compose up --build
```

* `docker compose up`: Starts the services defined in `docker-compose.yml`.
* `--build`: Forces Docker to rebuild the image from your `Dockerfile`. This is crucial to ensure all changes in your code or dependencies are applied.

This process might take some time on the first run as Docker downloads base images and installs all necessary dependencies.
## Note that: Because I don't have a GUI (crashes when running, so I did not put it in), I run docker compose without a GUI, and if you want to see a video on how the system works, please take a few seconds to uncomment lines that have cv2.inshow, cv2.namedWindow, cv2.Resize.
## The videos I changed the name:
* 1461_CH01_20250607193711_203711 -> CH01
* 1462_CH03_20250607192844_202844 -> CH03
* 1462_CH04_20250607210159_211703 -> CH04_1
* 1464_CH02_20250607180000_190000 -> CH02_1
* 1465_CH02_20250607170555_172408 -> CH02_2
* 1467_CH04_20250607180000_190000 -> CH04_2

## Configuration

You can configure the application's runtime parameters by editing the `command` section in the `docker-compose.yml` file:

```yaml
services:
  pizza-counter:
    # ... other configurations ...
    command: python Count_Pizza.py --video_path data/CH01.mp4 --model weights/best_yolov8.pt --conf 0.5 --classes Pizza
```

Configurable parameters:

* `--video_path`: The path to the input video file inside the container (must correspond to your volume mapping). Example: `data/CH01.mp4`.
* `--model`: The path to the YOLOv8 model weights file inside the container. Example: `weights/best_yolov8.pt`.
* `--conf`: The confidence threshold for object detection. Value between 0 and 1.
* `--classes`: Filter specific object classes to count. Example: `Pizza`.

## View Results

After the video processing is complete (you will see "Video processing complete and resources released." message in the Docker Compose logs), the processed video will be saved to the `output_videos/` directory on your host machine.

Example: If you process `data/CH01.mp4`, the result will be `output_videos/CH01_processed.mp4`.

## Troubleshooting

* **`docker daemon is not running`**: Ensure Docker Desktop is running on your machine.
* **Python dependency installation errors (`pip install` in Dockerfile)**: Double-check your `requirements.txt` and `Dockerfile` to ensure compatible library versions and correct installation commands.
* **`qt.qpa.xcb: could not connect to display`**: This error indicates the application is trying to display a GUI in a headless environment. This project is configured to run in "headless" mode by using `opencv-python-headless` and saving results to a file. Make sure you have replaced `opencv-python` with `opencv-python-headless` in your `requirements.txt` (or installed it directly in the Dockerfile) and removed `cv2.imshow()` lines from `Count_Pizza.py`.
* **`Error: Could not create video writer for ...`**: Verify that the `output_videos` directory exists on your host machine and is correctly volume-mapped in `docker-compose.yml`. Ensure the output video filename is valid.
* **Video codec-related errors**: Ensure `ffmpeg` is installed in your `Dockerfile`. If you still encounter errors, try changing the codec in `Count_Pizza.py` (e.g., `fourcc = cv2.VideoWriter_fourcc(*'XVID')` and save the file as `.avi`).
