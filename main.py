import os
import sys
import time
import shutil
import logging
import uvicorn
import platform
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
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from database import SessionLocal, engine
from models import Base, User
from auth import auth_manager

logging.basicConfig(
    format="%(asctime)s [%(levelname)s] %(filename)s:%(lineno)d - %(message)s",
    level=logging.INFO,
    datefmt="%Y-%m-%d %H:%M:%S"
)

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")
Base.metadata.create_all(bind=engine)

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("index.htm", {"request": request})

@app.get("/favicon.ico", include_in_schema=False)
def favicon():
    return FileResponse("static/favicon.ico")

@app.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse("login.htm", {"request": request, "msg": ""})

@app.post("/login")
def login(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    remember: str = Form(None),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.username == username).first()
    if not user or not auth_manager.verify_password(password, user.hashed_password):
        return templates.TemplateResponse("login.htm", {"request": request, "msg": "Invalid credentials"})    
    response = RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)    
    auth_manager.login_user(response, username, remember=(remember == "yes"))
    return response

@app.get("/register", response_class=HTMLResponse)
def register_page(request: Request):
    return templates.TemplateResponse("register.htm", {"request": request, "msg": "", "register": True})

@app.post("/register")
def register(
    request: Request, 
    username: str = Form(...), 
    password: str = Form(...), 
    db: Session = Depends(get_db)
):
    if db.query(User).filter(User.username == username).first():
        return templates.TemplateResponse("login.htm", {"request": request, "msg": "User exists", "register": True})
    new_user = User(username=username, hashed_password=auth_manager.hash_password(password))
    db.add(new_user)
    db.commit()
    return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)

@app.get("/logout")
def logout():
    response = RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)
    auth_manager.logout_user(response)
    return response

@app.get("/settings")
def app_settings():
    content = {
        "APP_NAME": settings.APP_NAME, 
        "APP_VERSION": settings.APP_VERSION,
        "APP_PORT": settings.APP_PORT,
        "APP_DEBUG": str(settings.APP_DEBUG),
        "LOG_LEVEL": settings.LOG_LEVEL,
        "UPLOAD_DIR": settings.UPLOAD_DIR,
        "DATABASE_URL": settings.DATABASE_URL,
    }
    return JSONResponse(content=content, status_code=200)

@app.get("/system")
def system_info():
    content = {
        "Node": platform.node(),
        "Platform": sys.platform,
        "OS": platform.platform(),
        "Version": platform.version(),
        "Arch": platform.machine(),
        "CPU": platform.processor(),  
        "Python": platform.python_version(),        
    }
    return JSONResponse(content=content, status_code=200)

@app.get("/upload", response_class=HTMLResponse)
def upload_page(request: Request, db: Session = Depends(get_db)):
    user = auth_manager.get_current_user(request, db)
    if not user:
        return RedirectResponse(url="/login")
    files = os.listdir(settings.UPLOAD_DIR)
    return templates.TemplateResponse("upload.htm", {
        "request": request,
        "files": files,
        "user": user,
    })
    
@app.post("/upload", response_class=HTMLResponse)
def handle_upload(
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
        "message": f"Uploaded: {', '.join(uploaded_names)}",
        "files": files_list,
        "user": user,
    })
    
@app.get("/files/{filename}")
def get_file(filename: str, db: Session = Depends(get_db), request: Request = None):
    user = auth_manager.get_current_user(request, db)
    if not user:
        return RedirectResponse(url="/login")
    file_path = path.join(settings.UPLOAD_DIR, filename)
    if not path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(file_path, filename=filename)

@app.get("/delete/{filename}")
def delete_file(filename: str, db: Session = Depends(get_db), request: Request = None):
    user = auth_manager.get_current_user(request, db)
    if not user:
        return RedirectResponse(url="/login")
    file_path = path.join(settings.UPLOAD_DIR, filename)
    if path.exists(file_path):
        os.remove(file_path)
    return RedirectResponse(url="/upload", status_code=302)

if __name__ == "__main__":
    logging.info(f"Application: {settings.APP_NAME} {settings.APP_VERSION}")
    logging.info(f"APP_PORT: {settings.APP_PORT}, DEBUG: {settings.APP_DEBUG}, LOG_LEVEL: {settings.LOG_LEVEL}, ENV: {settings.ENV_PATH}")
    logging.getLogger().setLevel(settings.LOG_LEVEL)
    logging.info(f"App listening on http://localhost:{settings.APP_PORT}")
    uvicorn.run("main:app", host="0.0.0.0", port=int(settings.APP_PORT), reload=settings.APP_DEBUG)
