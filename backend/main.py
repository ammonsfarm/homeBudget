from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from contextlib import asynccontextmanager
import os
from dotenv import load_dotenv

from database import engine, Base
from routers import auth, accounts, budgets, transactions, documents, net_worth, simplefin
from utils.security import verify_token

# Load environment variables
load_dotenv()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create database tables
    Base.metadata.create_all(bind=engine)
    yield

# Create FastAPI app
app = FastAPI(
    title="Home Budget App API",
    description="A modern budgeting application with SimpleFIN integration and budget rollover functionality",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
origins = os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Dependency to get current authenticated user"""
    try:
        payload = verify_token(credentials.credentials)
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return user_id
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(accounts.router, prefix="/api/accounts", tags=["Accounts"], dependencies=[Depends(get_current_user)])
app.include_router(budgets.router, prefix="/api/budgets", tags=["Budgets"], dependencies=[Depends(get_current_user)])
app.include_router(transactions.router, prefix="/api/transactions", tags=["Transactions"], dependencies=[Depends(get_current_user)])
app.include_router(documents.router, prefix="/api/documents", tags=["Documents"], dependencies=[Depends(get_current_user)])
app.include_router(net_worth.router, prefix="/api/net-worth", tags=["Net Worth"], dependencies=[Depends(get_current_user)])
app.include_router(simplefin.router, prefix="/api/simplefin", tags=["SimpleFIN"], dependencies=[Depends(get_current_user)])

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Home Budget App API",
        "version": "1.0.0",
        "status": "running"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=os.getenv("BACKEND_HOST", "0.0.0.0"),
        port=int(os.getenv("BACKEND_PORT", 8000)),
        reload=True
    )
