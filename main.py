import os
import sys
import time
import json
import shutil
import uvicorn
import logging
import platform

logging.basicConfig(
    format="%(asctime)s [%(levelname)s] %(filename)s:%(lineno)d - %(message)s",
    level=logging.INFO,
    datefmt="%Y-%m-%d %H:%M:%S"
)

from os import path
from settings import settings
from fastapi import ( 
    FastAPI, Request, HTTPException,
    status, UploadFile, Depends, Form, File,
)
from fastapi.responses import (
    HTMLResponse, RedirectResponse, FileResponse,
    JSONResponse, PlainTextResponse, StreamingResponse
)
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from sqlalchemy.orm import Session
from openai import AzureOpenAI

from database import SessionLocal, engine
from models import Base, User
from auth import auth_manager


app = FastAPI(title=settings.APP_NAME)
app.mount("/static", StaticFiles(directory="static"), name="static")
app.add_middleware(
    CORSMiddleware, 
    allow_origins=['*'], 
    allow_methods=['*'], 
    allow_headers=['*'])

templates = Jinja2Templates(directory="templates")
Base.metadata.create_all(bind=engine)

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    return FileResponse("static/favicon.ico")

@app.get("/", response_class=HTMLResponse)
async def home_page(
    request: Request,
    db: Session = Depends(get_db)
):
    user = auth_manager.get_current_user(request, db)
    return templates.TemplateResponse("index.htm", {
        "request": request, 
        "user": user
    })

@app.get("/login", response_class=HTMLResponse)
async def login_page(
    request: Request, 
    back_url: str="/",
    db: Session = Depends(get_db),
):
    if back_url != "/":
        user = auth_manager.get_current_user(request, db)
        if user:
            return RedirectResponse(url=back_url, status_code=status.HTTP_302_FOUND)
    return templates.TemplateResponse("login.htm", {
        "request": request, 
        "back_url": back_url, 
        "msg": ""
    })

@app.post("/login", response_class=RedirectResponse)
async def login(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    remember: str = Form(None),
    back_url: str = Form("/"),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.username == username).first()
    if not user or not auth_manager.verify_password(password, user.hashed_password):
        return templates.TemplateResponse("login.htm", {"request": request, "msg": "Invalid credentials"})    
    response = RedirectResponse(url=back_url, status_code=status.HTTP_302_FOUND)    
    auth_manager.login_user(response, username, remember=(remember == "yes"))
    return response

@app.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    return templates.TemplateResponse("register.htm", {
        "request": request, 
        "msg": "", 
        "register": True
    })

@app.post("/register", response_class=RedirectResponse)
async def register(
    request: Request, 
    username: str = Form(...), 
    password: str = Form(...), 
    db: Session = Depends(get_db)
):
    if db.query(User).filter(User.username == username).first():
        return templates.TemplateResponse("register.htm", {
            "request": request,
            "msg": "User exists", 
            "register": True
        })
    new_user = User(username=username, hashed_password=auth_manager.hash_password(password))
    db.add(new_user)
    db.commit()
    return RedirectResponse("/login", status_code=status.HTTP_302_FOUND)

@app.get("/logout", response_class=RedirectResponse)
async def logout():
    response = RedirectResponse("/", status_code=status.HTTP_302_FOUND)
    auth_manager.logout_user(response)
    return response

@app.get("/users", response_class=HTMLResponse)
async def users_page(
    request: Request, db: 
    Session = Depends(get_db)
):
    user = auth_manager.get_current_user(request, db)
    if not user:
        return RedirectResponse(url=f"/login?back_url={request.url.path}")
    users = db.query(User).all()
    db.commit()
    return templates.TemplateResponse("users.htm", {
        "request": request,
        "user": user,
        "users": users
        })

@app.get("/user/update/{user_id}", response_class=HTMLResponse)
async def user_update_page(
    user_id: int, 
    request: Request, 
    db: Session = Depends(get_db)
):
    user = auth_manager.get_current_user(request, db)
    if not user:
        return RedirectResponse(url="/login") 
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return templates.TemplateResponse("register.htm", {
        "request": request, 
        "user": user,
        "msg": "Upadte user information", 
        "register": True
    })

@app.post("/user/update", response_class=RedirectResponse)
async def user_update(
    request: Request, 
    user_id: int = Form(...), 
    username: str = Form(...), 
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    user = auth_manager.get_current_user(request, db)
    if not user:
        return RedirectResponse(url="/login")    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    user.username = username
    user.hashed_password=auth_manager.hash_password(password)
    db.commit()
    return RedirectResponse("/users", status_code=status.HTTP_303_SEE_OTHER)

@app.get("/user/delete/{user_id}", response_class=RedirectResponse)
async def user_delete(
    user_id: str,
    request: Request, 
    db: Session = Depends(get_db)
):
    user = auth_manager.get_current_user(request, db)
    if not user:
        return RedirectResponse(url="/login")    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    db.delete(user)
    db.commit()
    return RedirectResponse("/users", status_code=status.HTTP_302_FOUND)

@app.get("/api/system", response_class=JSONResponse)
async def system_info(
    request: Request, 
    db: Session = Depends(get_db)
):
    user = auth_manager.get_current_user(request, db)
    if not user:
        return JSONResponse(
            content={"detail": "Not Authorized"}, 
            status_code=status.HTTP_401_UNAUTHORIZED)
    return {
        "Node": platform.node(),
        "Platform": sys.platform,
        "OS": platform.platform(),
        "Version": platform.version(),
        "Arch": platform.machine(),
        "CPU": platform.processor(),  
        "Python": platform.python_version(),
    }

@app.get("/api/settings", response_class=JSONResponse)
async def app_settings(
    request: Request, 
    db: Session = Depends(get_db)
):
    user = auth_manager.get_current_user(request, db)
    if not user:
        return JSONResponse(
            content={"detail": "Not Authorized"},
            status_code=status.HTTP_401_UNAUTHORIZED)
    return settings.to_json()

class NoteRequest(BaseModel):
    text: str

webpad_storage_text = ""

@app.get("/webpad", response_class=HTMLResponse)
async def webpad_page(
    request: Request,
    db: Session = Depends(get_db)
):
    user = auth_manager.get_current_user(request, db)
    return templates.TemplateResponse("webpad.htm", {
        "request": request,
        "user": user,
        "text": webpad_storage_text
    })

@app.post("/webpad/save", response_class=RedirectResponse)
async def webpad_save(textarea: str = Form(...)):
    global webpad_storage_text
    webpad_storage_text = textarea
    return RedirectResponse("/webpad", status_code=status.HTTP_303_SEE_OTHER)

@app.post("/webpad/clear", response_class=RedirectResponse)
async def webpad_clear():
    global webpad_storage_text
    webpad_storage_text = ""
    return RedirectResponse("/webpad", status_code=status.HTTP_303_SEE_OTHER)

@app.post("/api/webpad", response_class=JSONResponse)
async def webpad_save(
    request: Request,
    notereq: NoteRequest,
    db: Session = Depends(get_db)
):
    user = auth_manager.get_current_user(request, db)
    if not user:
        return JSONResponse(
            content={"detail": "Not Authorized"},
            status_code=status.HTTP_401_UNAUTHORIZED)
    global webpad_storage_text
    webpad_storage_text = notereq.text
    return {"reply": "ok"}

@app.get("/upload", response_class=HTMLResponse)
async def upload_page(
    request: Request, 
    db: Session = Depends(get_db)
):
    user = auth_manager.get_current_user(request, db)
    if not user:
        return RedirectResponse(url=f"/login?back_url={request.url.path}")
    filenames = os.listdir(settings.UPLOAD_DIR)
    return templates.TemplateResponse("upload.htm", {
        "request": request,
        "user": user,
        "filenames": filenames,
        "username": user.username,
    })
    
@app.post("/file/upload", response_class=HTMLResponse)
async def handle_upload(
    request: Request,
    files: list[UploadFile] = File(...),
    db: Session = Depends(get_db)
):
    user = auth_manager.get_current_user(request, db)
    if not user:
        return RedirectResponse(url="/login")
    uploaded_names = []
    for file in files:
        # rename if file already exists
        file_path = path.join(settings.UPLOAD_DIR, file.filename)
        if path.exists(file_path):
            timestamp = int(time.time())        
            filename = path.splitext(file.filename)[0]
            ext = path.splitext(file.filename)[1]
            new_filename = f"{filename} - {timestamp}{ext}"
            file_path = path.join(settings.UPLOAD_DIR, new_filename)

        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        uploaded_names.append(file.filename)

    files_list = os.listdir(settings.UPLOAD_DIR)
    return templates.TemplateResponse("upload.htm", {
        "request": request,
        "user": user,
        "message": f"Uploaded: {', '.join(uploaded_names)}",
        "filenames": files_list,
    })
    
@app.get("/file/download/{filename}", response_class=FileResponse)
async def get_file(
    filename: str,
    request: Request = None,
    db: Session = Depends(get_db),
):
    user = auth_manager.get_current_user(request, db)
    if not user:
        return JSONResponse(
            content={"detail": "Not Authorized"},
            status_code=status.HTTP_401_UNAUTHORIZED)
    file_path = path.join(settings.UPLOAD_DIR, filename)
    if not path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(file_path, filename=filename)

@app.get("/file/delete/{filename}", response_class=RedirectResponse)
async def delete_file(
    filename: str,
    request: Request = None,
    db: Session = Depends(get_db)
):
    user = auth_manager.get_current_user(request, db)
    if not user:
        return JSONResponse(
            content={"detail": "Not Authorized"},
            status_code=status.HTTP_401_UNAUTHORIZED)
    file_path = path.join(settings.UPLOAD_DIR, filename)
    if path.exists(file_path):
        os.remove(file_path)
    return RedirectResponse(url="/upload", status_code=302)

class ChatRequest(BaseModel):
    prompt: str

class ChatResponse(BaseModel):
    reply: str

aiclient = AzureOpenAI(
    azure_endpoint=settings.AZUREAI_ENDPOINT_URL,
    api_key=settings.AZUREAI_ENDPOINT_KEY,
    api_version=settings.AZUREAI_API_VERSION,
)

@app.get("/chatbot", response_class=HTMLResponse)
async def chat_page(
    request: Request, 
    db: Session = Depends(get_db)
):
    user = auth_manager.get_current_user(request, db)
    if not user:
        return RedirectResponse(url=f"/login?back_url={request.url.path}")
    return templates.TemplateResponse("chatbot.htm", {
        "request": request,
        "user": user,
    })

@app.post('/api/chat', response_model=ChatResponse)
async def chat_endpoint(
    request: Request,
    chatreq: ChatRequest,
    db: Session = Depends(get_db)
):
    if not chatreq.prompt.strip():
        raise HTTPException(
            detail='Empty prompt!', 
            status_code=status.HTTP_400_BAD_REQUEST)
    
    user = auth_manager.get_current_user(request, db)
    if not user:
        return JSONResponse(
            content={"detail": "Not Authorized"},
            status_code=status.HTTP_401_UNAUTHORIZED)

    response = aiclient.chat.completions.create(
        model=settings.AZUREAI_DEPLOYMENT,
        messages=[
            { "role": "system", "content": "You are a helpful assistant." },
            { "role": "user", "content": chatreq.prompt }
        ],
        max_tokens=4096,
        temperature=1.0,
        top_p=1.0
    )    
    reply = "No response!"
    if response.choices:
        reply = response.choices[0].message.content
    return {"reply": reply}

logging.info(f"Application: {settings.APP_NAME} v{settings.APP_VERSION}")
logging.info(f"APP_PORT: {settings.APP_PORT}, DEBUG: {settings.APP_DEBUG}, " + 
             f"LOG_LEVEL: {settings.LOG_LEVEL}, ENV: {settings.ENV_PATH}")
logging.getLogger().setLevel(settings.LOG_LEVEL)

if __name__ == "__main__":
    logging.info(f"{settings.APP_NAME} listening on http://localhost:{settings.APP_PORT}")
    uvicorn.run("main:app", host="0.0.0.0", port=int(settings.APP_PORT), reload=settings.APP_DEBUG)
