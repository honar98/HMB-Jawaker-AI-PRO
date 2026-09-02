from fastapi import FastAPI

app = FastAPI(title="HMB Jawaker AI PRO")


@app.get("/")
def root():
    return {
        "ok": True,
        "service": "HMB Jawaker AI PRO",
        "status": "online"
    }


@app.get("/health")
def health():
    return {"ok": True}
