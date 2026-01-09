# from fastapi import FastAPI, Request
# from fastapi.middleware.cors import CORSMiddleware
# from fastapi.responses import StreamingResponse
# from interview_bot import InterviewBot
# from vision_analyzer import VisionAnalyzer
# import threading

# app = FastAPI()

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# bot = InterviewBot()

# # ✅ START CAMERA
# vision = VisionAnalyzer()
# bot.attach_vision(vision)

# camera_thread = None

# @app.post("/start_camera")
# def start_camera():
#     global camera_thread
#     if camera_thread is None or not camera_thread.is_alive():
#         vision.start_flag = True
#         camera_thread = threading.Thread(target=vision.start)
#         camera_thread.daemon = True
#         camera_thread.start()
#     return {"status": "camera started"}


# @app.post("/stop_camera")
# def stop_camera():
#     vision.stop()
#     return {"status": "camera stopped"}


# # @app.post("/chat")
# # async def chat(request: Request):
# #     data = await request.json() if request.headers.get("content-length") != "0" else {}

# #     if not data or "message" not in data:
# #         return bot.start_interview()

# #     user_message = data["message"]
# #     response = bot.ask_question(user_message)

# #     return response

# @app.post("/chat")
# async def chat(request: Request):
#     data = await request.json() if request.headers.get("content-length") != "0" else {}

#     # ✅ If setup is sent (first call)
#     if "setup" in data:
#         return bot.start_interview(data["setup"])

#     # ✅ If normal start (fallback)
#     if not data or "message" not in data:
#         return bot.start_interview()

#     # ✅ Normal chat
#     user_message = data["message"]
#     response = bot.ask_question(user_message)

#     return response


# # ✅ METRICS ENDPOINT
# @app.get("/metrics")
# def metrics():
#     return vision.get_metrics()

# # ✅ VIDEO STREAM ENDPOINT
# def gen_frames():
#     while True:
#         frame = vision.get_frame()
#         if frame is None:
#             continue

#         yield (b"--frame\r\n"
#                b"Content-Type: image/jpeg\r\n\r\n" + frame + b"\r\n")

# @app.get("/video_feed")
# def video_feed():
#     return StreamingResponse(gen_frames(), media_type="multipart/x-mixed-replace; boundary=frame")


from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from interview_bot import InterviewBot
from vision_analyzer import VisionAnalyzer
import threading
from fastapi import UploadFile, File, Form
import pdfplumber
import io

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

bot = InterviewBot()

def extract_text_from_pdf_bytes(file_bytes: bytes):
    text = ""
    with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
        for page in pdf.pages:
            t = page.extract_text()
            if t:
                text += t + "\n"
    return text.strip()


# ✅ START CAMERA
vision = VisionAnalyzer()
bot.attach_vision(vision)

camera_thread = None

@app.post("/start_camera")
def start_camera():
    global camera_thread
    if camera_thread is None or not camera_thread.is_alive():
        vision.start_flag = True
        camera_thread = threading.Thread(target=vision.start)
        camera_thread.daemon = True
        camera_thread.start()
    return {"status": "camera started"}


@app.post("/stop_camera")
def stop_camera():
    vision.stop()
    return {"status": "camera stopped"}


@app.post("/chat")
async def chat(request: Request):
    try:
        data = await request.json()
    except:
        data = {}

    if "setup" in data:
        return bot.start_interview(data["setup"])

    if "message" not in data:
        return {"role": "assistant", "message": "Invalid request"}

    return bot.ask_question(data["message"])



# @app.post("/chat")
# async def chat(
#     request: Request,
#     resume: UploadFile = File(None),
#     notes: UploadFile = File(None),
#     setup: str = Form(None),
# ):
#     # If multipart/form-data with file
#     if setup:
#         import json
#         setup_data = json.loads(setup)

#         # If resume uploaded
#         if resume:
#             file_bytes = await resume.read()
#             text = extract_text_from_pdf_bytes(file_bytes)
#             setup_data["resume_text"] = text

#         # If notes uploaded
#         if notes:
#             file_bytes = await notes.read()
#             text = extract_text_from_pdf_bytes(file_bytes)
#             setup_data["notes_text"] = text

#         return bot.start_interview(setup_data)

#     # Else: normal JSON chat message
#     data = await request.json() if request.headers.get("content-length") != "0" else {}

#     if not data or "message" not in data:
#         return {
#             "role": "assistant",
#             "message": "⚠️ Invalid request."
#         }

#     user_message = data["message"]
#     return bot.ask_question(user_message)


# ✅ METRICS ENDPOINT
@app.get("/metrics")
def metrics():
    return vision.get_metrics()

# ✅ VIDEO STREAM ENDPOINT
def gen_frames():
    while True:
        frame = vision.get_frame()
        if frame is None:
            continue

        yield (b"--frame\r\n"
               b"Content-Type: image/jpeg\r\n\r\n" + frame + b"\r\n")

@app.get("/video_feed")
def video_feed():
    return StreamingResponse(gen_frames(), media_type="multipart/x-mixed-replace; boundary=frame")
