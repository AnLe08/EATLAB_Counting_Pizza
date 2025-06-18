FROM python:3.11-slim-buster

WORKDIR /app

RUN apt-get update && apt-get install -y \
    # libgl1-mesa-glx \
    # libglib2.0-0 \
    # libsm6 \
    # libxext6 \
    ffmpeg \
    && apt-get clean && rm -rf /var/lib/apt/lists/*
##
COPY requirements.txt .


# RUN pip install torch==2.7.1 --index-url https://download.pytorch.org/whl/cpu
# RUN pip install torchvision==0.18.1 torchaudio==2.3.1 --index-url https://download.pytorch.org/whl/cpu
# Cài đặt các thư viện Python
RUN pip install --no-cache-dir -r requirements.txt


COPY . .


CMD ["python", "Count_Pizza.py"]