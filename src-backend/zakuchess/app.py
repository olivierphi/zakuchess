from __future__ import annotations

from fastapi import FastAPI

from .http.response import AstroPageProxyResponse

app = FastAPI()


@app.get("/")
def read_root():
    return AstroPageProxyResponse("/")
