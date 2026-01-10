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
import pdfplumber
import io
from fastapi import UploadFile, File, Form
import docx

app = FastAPI()

origins = [
    "http://localhost:5173",  # React (Vite)
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,      # or ["*"] for all (not recommended for prod)
    allow_credentials=True,
    allow_methods=["*"],        # GET, POST, PUT, DELETE, etc
    allow_headers=["*"],        # All headers
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


def extract_text_from_file(file: UploadFile):
    filename = file.filename.lower()

    content = file.file.read()

    # PDF
    if filename.endswith(".pdf"):
        return extract_text_from_pdf_bytes(content)

    # TXT
    elif filename.endswith(".txt"):
        try:
            return content.decode("utf-8", errors="ignore")
        except:
            return ""

    # DOCX
    elif filename.endswith(".docx"):
        try:
            doc = docx.Document(io.BytesIO(content))
            return "\n".join(p.text for p in doc.paragraphs)
        except:
            return ""

    else:
        return ""



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

@app.post("/start_interview")
async def start_interview(
    name: str = Form(...),
    topic: str = Form(""),
    difficulty: str = Form("Intermediate"),
    mode: str = Form("Conceptual"),
    resume: UploadFile = File(None),
    notes: UploadFile = File(None),
):
    resume_text = ""
    notes_text = ""

    if resume:
        resume_text = extract_text_from_file(resume)
        print("✅ Resume text length:", len(resume_text))

    if notes:
        notes_text = extract_text_from_file(notes)
        print("✅ Notes text length:", len(notes_text))

    setup = {
        "name": name,
        "topic": topic,
        "difficulty": difficulty,
        "mode": mode,
        "resume_text": resume_text,
        "notes_text": notes_text,
    }

    return bot.start_interview(setup)

# @app.post("/chat")
# async def chat(request: Request):
#     data = await request.json()
#     if "message" not in data:
#         return {"role": "assistant", "message": "Invalid request"}
#     return bot.ask_question(data["message"])

@app.post("/chat")
async def chat(request: Request):
    data = await request.json()

    if "message" not in data:
        return {"ended": False, "message": "Invalid request"}

    result = bot.ask_question(data["message"])

    # If bot returned full report (ended = True)
    if isinstance(result, dict) and result.get("ended") is True:
        return result

    # Normal message
    if isinstance(result, dict) and "message" in result:
        return {
            "ended": False,
            "message": result["message"]
        }

    # Fallback safety
    return {
        "ended": False,
        "message": str(result)
    }



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
