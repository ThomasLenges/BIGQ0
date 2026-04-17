# Issue too slow because CV2 model running on CPU. Need to move to GPU.

## Option 1: Edge Impulse model
Edge Impulse enables deployement of optimized models for QRB2210. Download model .eim & .yaml files @ .arduino-bricks/models/custom-ei
Input model on videoObjectDetection Brick under app.yaml.

## Option 2: Snapdragon Neural Processing Engine SDK 
To run models on Adreno GPU or DSP Hexagon

## Steps

### 1: Move example app to local apps and link it with custom EI model (current app)

### 2: Move brick to local

### 3: Try without brick/personal brick

### 4: Add tracking (in eim or CPU?)