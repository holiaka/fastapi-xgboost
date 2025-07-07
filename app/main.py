from app.utils.rate_limit import setup_rate_limiter
from fastapi import FastAPI
from app.routes import auth, user, predict

app = FastAPI()
setup_rate_limiter(app)

app.include_router(auth.router)
app.include_router(user.router)
app.include_router(predict.router)