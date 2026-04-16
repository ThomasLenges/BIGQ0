from arduino.app_peripherals.camera import Camera
from fastapi.responses import Response
from arduino.app_utils.image.adjustments import compress_to_jpeg

camera = Camera()
camera.start()

latest_jpeg = None

def get_frame():
    global latest_jpeg
    # Get frame from camera
    frame = camera.capture()
    
    if frame is not None:
        jpeg = compress_to_jpeg(frame)
        if jpeg is not None:
            latest_jpeg = jpeg.tobytes() # Convert to bytes for Response

    
    if latest_jpeg is None:
        return Response(status_code=503) # Server up but image unavailable
        
    return Response(content=latest_jpeg, media_type="image/jpeg")
