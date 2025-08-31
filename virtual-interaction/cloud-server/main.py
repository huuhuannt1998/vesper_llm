from fastapi import FastAPI, HTTPException, Depends, Header, Request, Form, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.responses import RedirectResponse, JSONResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, declarative_base, selectinload, relationship
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, Float, select, update
from typing import Optional, Dict, Any, List
from datetime import datetime, timezone, timedelta
from pydantic import BaseModel, Field
from passlib.context import CryptContext
from jose import JWTError, jwt
import redis
import json
import os
import uuid
import logging
import asyncio
import aiohttp
import hashlib
import hmac
import time
from sqlalchemy.exc import IntegrityError

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# FastAPI app
app = FastAPI(title="Virtual Thermostat Cloud Server")

# Enable CORS for browser-based front-end access
from fastapi.middleware.cors import CORSMiddleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],          # In production, restrict origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


NGROK_AUTH_TOKEN = os.getenv("NGROK_AUTH_TOKEN", "")
SMARTTHINGS_CLIENT_ID = os.getenv("SMARTTHINGS_CLIENT_ID", "")
SMARTTHINGS_CLIENT_SECRET = os.getenv("SMARTTHINGS_CLIENT_SECRET", "")
# --- callback-token credentials (used when *we* call SmartThings)
SMARTTHINGS_CALLBACK_CLIENT_ID = os.getenv("SMARTTHINGS_CALLBACK_CLIENT_ID", "")
SMARTTHINGS_CALLBACK_CLIENT_SECRET = os.getenv("SMARTTHINGS_CALLBACK_CLIENT_SECRET", "")


# Configuration
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://admin:secure_password@postgres/thermostat_testbed")
REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379")
JWT_SECRET = os.getenv("JWT_SECRET", "your-jwt-secret")





# need to have visual delimiters such as lines to highlight the log block
logger.info("===================== Configuration =====================")
logger.info(f"SMARTTHINGS_CLIENT_ID: {SMARTTHINGS_CLIENT_ID}")
logger.info(f"SMARTTHINGS_CLIENT_SECRET: {'*' * len(SMARTTHINGS_CLIENT_SECRET)}")
logger.info(f"SMARTTHINGS_CALLBACK_CLIENT_ID: {SMARTTHINGS_CALLBACK_CLIENT_ID}")
logger.info(f"SMARTTHINGS_CALLBACK_CLIENT_SECRET: {'*' * len(SMARTTHINGS_CALLBACK_CLIENT_SECRET)}")
logger.info("=====================================================")



# Database setup
engine = create_async_engine(DATABASE_URL)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
Base = declarative_base()

# Redis connection
redis_host = REDIS_URL.split("//")[1].split(":")[0]
redis_port = int(REDIS_URL.split(":")[-1])
redis_client = redis.Redis(host=redis_host, port=redis_port, decode_responses=True)

# Security
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/oauth/token")

# Database Models
class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationship to Device
    devices = relationship("Device", back_populates="user")

class Device(Base):
    __tablename__ = "devices"
    
    id = Column(Integer, primary_key=True, index=True)
    serial_number = Column(String, unique=True, index=True, nullable=False)
    device_id = Column(String, unique=True, index=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"))
    smartthings_device_id = Column(String, unique=True, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    config_file = Column(String, nullable=True)

    # Relationship to User
    user = relationship("User", back_populates="devices")

class OAuthToken(Base):
    __tablename__ = "oauth_tokens"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    access_token = Column(String, unique=True, nullable=False)
    refresh_token = Column(String, unique=True, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

# Pydantic Models
class DeviceRegistration(BaseModel):
    serial_number: str
    device_type: str
    capabilities: List[str]
    username: Optional[str] = "admin"

class DeviceState(BaseModel):
    mode: str
    current_temp: float
    current_humidity: float
    target_temp: float
    fan_mode: str
    is_running: bool
    last_updated: str

class SmartThingsCommand(BaseModel):
    capability: str
    command: str
    arguments: Optional[List[Any]] = []

class SmartThingsDevice(BaseModel):
    externalDeviceId: str
    deviceCookie: Optional[Dict[str, Any]] = {}
    friendlyName: str
    manufacturerInfo: Dict[str, str]
    deviceContext: Dict[str, Any]

# Helper Functions
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(hours=24)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET, algorithm="HS256")
    return encoded_jwt

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

async def get_current_user(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    # Get user from database
    # For simplicity, returning username
    return username

# SmartThings Integration
class SmartThingsConnector:
    def __init__(self):
        self.webhook_url = None
        self.ngrok_tunnel = None
        
    async def setup_ngrok(self):
        """Setup webhook URL using external ngrok container"""
        try:
            # Use the configured domain or default
            custom_domain = os.getenv("NGROK_DOMAIN", "vt-testbed-2025.ngrok.app")
            logger.info(f"Using ngrok domain: {custom_domain}")
            
            # Set webhook URL based on ngrok container
            self.webhook_url = f"https://{custom_domain}"
            logger.info(f"SmartThings webhook URL configured: {self.webhook_url}")
            
            # Update SmartThings webhook configuration
            await self.update_smartthings_webhook()
            
            return self.webhook_url
            
        except Exception as e:
            logger.error(f"Error setting up webhook URL: {e}")
            return None
    
    async def update_smartthings_webhook(self):
        """Update webhook URL in SmartThings"""
        # This would normally update the webhook URL in SmartThings
        # For now, just log it
        logger.info(f"SmartThings webhook URL: {self.webhook_url}/smartthings/webhook")
    
    def verify_smartthings_signature(self, body: bytes, signature: str) -> bool:
        """Verify SmartThings webhook signature"""
        if not SMARTTHINGS_CLIENT_SECRET:
            return False
            
        expected = hmac.new(
            SMARTTHINGS_CLIENT_SECRET.encode(),
            body,
            hashlib.sha256
        ).hexdigest()
        
        return hmac.compare_digest(expected, signature)

# Create SmartThings connector instance
st_connector = SmartThingsConnector()

# -------------------------------------------------------------
# Sync helper: ensure DB devices table matches Redis metadata
# -------------------------------------------------------------
async def sync_devices_from_redis(db: AsyncSession):
    """Insert any Redis devices not yet in the DB Device table"""
    # Collect serials from Redis metadata
    redis_serials = [
        key.split(":")[1]
        for key in redis_client.scan_iter("device:*:metadata")
    ]

    if not redis_serials:
        return

    # Collect existing serials from DB
    result = await db.execute(select(Device.serial_number))
    existing_serials = {row[0] for row in result.all()}

    # Insert missing devices
    added = 0
    for serial in redis_serials:
        if serial in existing_serials:
            continue

        # Determine username from metadata
        metadata = redis_client.hgetall(f"device:{serial}:metadata")
        username = metadata.get("username", "admin")
        # Look up user
        result_user = await db.execute(
            select(User).filter(User.username == username)
        )
        user = result_user.scalar_one_or_none()
        if not user:
            # Fallback to admin
            result_user = await db.execute(
                select(User).filter(User.username == "admin")
            )
            user = result_user.scalar_one()

        # Create Device entry
        db_device = Device(
            serial_number=serial,
            device_id=f"d{uuid.uuid4().hex[:7]}",
            user_id=user.id,
            created_at=datetime.utcnow(),
            config_file=metadata.get("config_file")
        )
        db.add(db_device)
        added += 1

    if added:
        await db.commit()
        logger.info("Sync added %s missing devices from Redis to DB", added)
    else:
        logger.info("Device sync: DB already up to date")

# Startup event
@app.on_event("startup")
async def startup_event():
    """Initialize database and ngrok tunnel"""
    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # Setup ngrok
    await st_connector.setup_ngrok()
    
    # Create default user if not exists
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(User).filter(User.username == "admin"))
        if not result.scalar_one_or_none():
            admin_user = User(
                username="admin",
                password_hash=get_password_hash("admin123")
            )
            db.add(admin_user)
            await db.commit()
            logger.info("Default admin user created")

        # After ensuring admin exists, sync any Redis devices
        # into the database so SmartThings discovery matches
        # backend-console devices.
        await sync_devices_from_redis(db)

# Health check
@app.get("/health")
async def health_check():
    return {"status": "healthy", "webhook_url": st_connector.webhook_url}

# Device Management APIs
@app.post("/api/devices/register")
async def register_device(
    device: DeviceRegistration,
    db: AsyncSession = Depends(get_db)
):
    # Look up user (default to provided username, else admin)
    result_user_lookup = await db.execute(
        select(User).filter(User.username == device.username)
    )
    user_for_registration = result_user_lookup.scalar_one_or_none()
    if not user_for_registration:
        # Instead of falling back to admin:
        logger.error(
            f"User '{device.username}' not found. Cannot register device '{device.serial_number}'."
        )
        raise HTTPException(
            status_code=400, detail=f"User '{device.username}' not found. Device not registered."
        )
    
    # Check if device already exists
    result_device = await db.execute(
        select(Device).options(selectinload(Device.user))
        .filter(Device.serial_number == device.serial_number)
    )
    existing_device = result_device.scalar_one_or_none()

    if existing_device:
        logger.info(
            "Device %s already registered (device_id=%s, user_id=%s)",
            existing_device.serial_number, existing_device.device_id, existing_device.user_id
        )
        # Ensure SmartThings gets an updated discoveryCallback even when
        # the device already existed (e.g., concurrent spawn or retry).
        # Use the user_id from the existing_device record.
        if existing_device.user_id:
            asyncio.create_task(send_discovery_callback(existing_device.user_id))
        else:  # Should not happen if device is properly registered, but as a fallback
            asyncio.create_task(send_discovery_callback(user_for_registration.id))

        return {
            "device_id": existing_device.device_id,
            "serial_number": existing_device.serial_number,
            "username": existing_device.user.username if existing_device.user else user_for_registration.username
        }

    # Otherwise create a new record
    device_id_new = f"d{uuid.uuid4().hex[:7]}"
    db_device_to_add = Device(
        serial_number=device.serial_number,
        device_id=device_id_new,
        user_id=user_for_registration.id  # Use the initially looked-up user's ID
    )
    db.add(db_device_to_add)
    try:
        await db.commit()
        await db.refresh(db_device_to_add, attribute_names=['user'])  # Refresh to load relationships
        logger.info("Device registered: %s -> %s for user_id %s", device.serial_number, device_id_new, user_for_registration.id)
        asyncio.create_task(send_discovery_callback(user_for_registration.id))
        
        return {
            "device_id": device_id_new,
            "serial_number": device.serial_number,
            "username": user_for_registration.username
        }
    except IntegrityError:
        # Another concurrent request inserted the same serial in parallel
        await db.rollback()
        logger.warning(
            "Concurrent registration detected for %s. Re-fetching.",
            device.serial_number
        )
        refetched_device_result = await db.execute(
            select(Device).options(selectinload(Device.user))
            .filter(Device.serial_number == device.serial_number)
        )
        refetched_device = refetched_device_result.scalar_one_or_none()

        if refetched_device:
            logger.info(
                "Concurrent registration handled for %s, returning existing device_id=%s, user_id=%s",
                refetched_device.serial_number, refetched_device.device_id, refetched_device.user_id
            )
            # Use user_id from the re-fetched device for the callback
            if refetched_device.user_id:
                asyncio.create_task(send_discovery_callback(refetched_device.user_id))
            
            return {
                "device_id": refetched_device.device_id,
                "serial_number": refetched_device.serial_number,
                "username": refetched_device.user.username if refetched_device.user else "unknown"
            }
        else:
            # This case should be rare if IntegrityError was due to this serial
            logger.error(
                "IntegrityError for %s, but device not found on re-fetch. This is unexpected.",
                device.serial_number
            )
            raise HTTPException(status_code=500, detail="Failed to register device after concurrency issue.")

@app.get("/api/devices")
async def list_devices(
    db: AsyncSession = Depends(get_db)
):
    """Return all registered devices (for debugging / integration check)."""
    result = await db.execute(select(Device))
    devices = result.scalars().all()
    return [
        {
            "id": d.id,
            "serial_number": d.serial_number,
            "device_id": d.device_id,
            "user_id": d.user_id,
            "smartthings_device_id": d.smartthings_device_id,
            "created_at": d.created_at.isoformat() if d.created_at else None
        } for d in devices
    ]

@app.post("/api/devices/{device_id}/state")
async def update_device_state(
    device_id: str,
    state: DeviceState,
    db: AsyncSession = Depends(get_db)
):
    """Update device state"""
    # Verify device exists
    result = await db.execute(select(Device).filter(Device.device_id == device_id))
    device = result.scalar_one_or_none()
    
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    
    # Store state in Redis (already done by thermostat)
    # Just log for now
    logger.info(f"State update received for device {device_id}")
    
    return {"status": "success"}

@app.post("/api/devices/{serial_number}/state-changed")
async def notify_state_changed(
    serial_number: str,
    db: AsyncSession = Depends(get_db)
):
    """Notify cloud server that device state has changed (called by backend console)"""
    logger.info(f"State change notification received for device {serial_number}")
    
    # Verify device exists
    result = await db.execute(select(Device).filter(Device.serial_number == serial_number))
    device = result.scalar_one_or_none()
    
    if not device:
        logger.warning(f"Device {serial_number} not found in database")
        return {"status": "device_not_found"}
    
    # Send state update to SmartThings
    try:
        await send_state_update_to_smartthings(serial_number, {})
        logger.info(f"State update sent to SmartThings for device {serial_number}")
        return {"status": "success", "callback_sent": True}
    except Exception as e:
        logger.error(f"Failed to send state update to SmartThings for {serial_number}: {e}")
        return {"status": "error", "error": str(e)}

@app.post("/api/devices/discovery-changed")
async def notify_discovery_changed(
    user_id: int = None,
    db: AsyncSession = Depends(get_db)
):
    """Notify cloud server that device discovery has changed (new device added)"""
    logger.info(f"Discovery change notification received for user_id {user_id}")
    
    # If no user_id provided, get admin user
    if user_id is None:
        result = await db.execute(select(User).filter(User.username == "admin"))
        admin_user = result.scalar_one_or_none()
        if admin_user:
            user_id = admin_user.id
        else:
            logger.error("No admin user found for discovery callback")
            return {"status": "error", "error": "No admin user found"}
    
    # Send discovery callback to SmartThings
    try:
        await send_discovery_callback(user_id)
        logger.info(f"Discovery callback sent to SmartThings for user_id {user_id}")
        return {"status": "success", "callback_sent": True}
    except Exception as e:
        logger.error(f"Failed to send discovery callback to SmartThings for user {user_id}: {e}")
        return {"status": "error", "error": str(e)}

# OAuth Endpoints
@app.get("/oauth/authorize", response_class=HTMLResponse)
async def oauth_authorize(
    request: Request,
    client_id: str,
    redirect_uri: str,
    state: str,
    response_type: str = "code",
    scope: Optional[str] = None,
    error: Optional[str] = None
):
    """OAuth authorization endpoint - shows login page first"""
    # Validate redirect URI against SmartThings allowed URIs
    allowed_redirect_uris = [
        "https://c2c-us.smartthings.com/oauth/callback",
        "https://c2c-eu.smartthings.com/oauth/callback",
        "https://c2c-ap.smartthings.com/oauth/callback"
    ]
    
    if redirect_uri not in allowed_redirect_uris:
        logger.warning(f"Invalid redirect URI: {redirect_uri}")
        # For development, allow localhost
        if not redirect_uri.startswith("http://localhost"):
            raise HTTPException(status_code=400, detail="Invalid redirect URI")
    
    # Validate client_id
    if client_id != SMARTTHINGS_CLIENT_ID:
        raise HTTPException(status_code=400, detail="Invalid client ID")
    
    # Check if user is already authenticated (session-based)
    user_session = request.cookies.get("oauth_session")
    if user_session and redis_client.exists(f"oauth_session:{user_session}"):
        # User is already authenticated, show consent page directly
        return await show_consent_page(client_id, redirect_uri, state, scope, response_type, user_session)
    
    # If the user is NOT authenticated yet, render the login page
    try:
        with open("oauth_login.html", "r") as f:
            html_content = f.read()
    except FileNotFoundError:
        # Fallback HTML if file doesn't exist
        html_content = """
        <!DOCTYPE html>
        <html>
        <head><title>Login</title></head>
        <body>
            <h1>Login</h1>
            <form method="POST" action="/oauth/login">
                <input type="hidden" name="client_id" value="{client_id}">
                <input type="hidden" name="redirect_uri" value="{redirect_uri}">
                <input type="hidden" name="state" value="{state}">
                <input type="hidden" name="scope" value="{scope}">
                <input type="hidden" name="response_type" value="{response_type}">
                <input type="text" name="username" placeholder="Username" required>
                <input type="password" name="password" placeholder="Password" required>
                <button type="submit">Login</button>
            </form>
        </body>
        </html>
        """.format(
            client_id=client_id,
            redirect_uri=redirect_uri,
            state=state,
            scope=scope or '',
            response_type=response_type
        )
    return HTMLResponse(content=html_content)

@app.get("/oauth/logout")
async def oauth_logout(
    request: Request,
    client_id: str,
    redirect_uri: str,
    state: str,
    response_type: str = "code",
    scope: Optional[str] = None
):
    """Logout current session and redirect to login to switch accounts"""
    # Delete session in Redis
    user_session = request.cookies.get("oauth_session")
    if user_session:
        redis_client.delete(f"oauth_session:{user_session}")
    # Build redirect URL back to login
    login_params = f"?client_id={client_id}&redirect_uri={redirect_uri}&state={state}&scope={scope or ''}&response_type={response_type}"
    response = RedirectResponse(
        url=f"/oauth/authorize{login_params}",
        status_code=302
    )
    # Clear cookie
    response.delete_cookie("oauth_session")
    return response

async def show_consent_page(client_id: str, redirect_uri: str, state: str, scope: Optional[str], response_type: str, user_session: str):
    """Show the consent page with user information"""
    # Get user info from session
    session_data = redis_client.get(f"oauth_session:{user_session}")
    if not session_data:
        raise HTTPException(status_code=401, detail="Session expired")
    
    session_info = json.loads(session_data)
    username = session_info.get("username", "Unknown")
    
    # Load consent page and inject user information
    try:
        with open("oauth_consent.html", "r") as f:
            html_content = f.read()
        # Replace the username in the HTML
        html_content = html_content.replace('id="username">admin</strong>', f'id="username">{username}</strong>')
    except FileNotFoundError:
        # Fallback HTML if file doesn't exist
        html_content = """
        <!DOCTYPE html>
        <html>
        <head><title>Authorize</title></head>
        <body>
            <h1>Authorize SmartThings</h1>
            <p>Logged in as: <strong id="username">{username}</strong></p>
            <form method="POST" action="/oauth/authorize/consent">
                <input type="hidden" name="client_id" value="{client_id}">
                <input type="hidden" name="redirect_uri" value="{redirect_uri}">
                <input type="hidden" name="state" value="{state}">
                <input type="hidden" name="scope" value="{scope}">
                <input type="hidden" name="response_type" value="{response_type}">
                <button type="submit" name="action" value="allow">Allow</button>
                <button type="submit" name="action" value="cancel">Cancel</button>
            </form>
        </body>
        </html>
        """.format(
            username=username,
            client_id=client_id,
            redirect_uri=redirect_uri,
            state=state,
            scope=scope or '',
            response_type=response_type
        )
    
    return HTMLResponse(content=html_content)

@app.post("/oauth/login")
async def oauth_login(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    client_id: str = Form(...),
    redirect_uri: str = Form(...),
    state: str = Form(...),
    scope: str = Form(None),
    response_type: str = Form("code"),
    db: AsyncSession = Depends(get_db)
):
    """Handle OAuth login form submission"""
    # Validate user credentials
    result = await db.execute(select(User).filter(User.username == username))
    user = result.scalar_one_or_none()
    
    # Special handling for default admin credentials to avoid bcrypt incompatibility issues
    if username == "admin" and password == "admin123":
        if not user:
            user = User(
                username="admin",
                password_hash=get_password_hash("admin123")
            )
            db.add(user)
            await db.commit()
            logger.info("Auto-created default admin user during OAuth login")
        # Skip hash verification for default admin – treat as authenticated
    else:
        # Verify credentials for all non-default users
        if not user or not verify_password(password, user.password_hash):
            # Redirect back to login with error
            error_params = f"?client_id={client_id}&redirect_uri={redirect_uri}&state={state}&scope={scope or ''}&response_type={response_type}&error=invalid_credentials"
            return RedirectResponse(
                url=f"/oauth/authorize{error_params}",
                status_code=302
            )
    
    # Create user session
    session_id = str(uuid.uuid4())
    session_data = {
        "user_id": user.id,
        "username": user.username,
        "login_time": datetime.utcnow().isoformat()
    }
    
    # Store session in Redis (expires in 1 hour)
    redis_client.setex(
        f"oauth_session:{session_id}",
        3600,
        json.dumps(session_data)
    )
    
    # Redirect to consent page with session cookie
    consent_params = f"?client_id={client_id}&redirect_uri={redirect_uri}&state={state}&scope={scope or ''}&response_type={response_type}"
    response = RedirectResponse(
        url=f"/oauth/consent{consent_params}",
        status_code=302
    )
    
    # Set secure session cookie
    response.set_cookie(
        "oauth_session",
        session_id,
        max_age=3600,
        httponly=True,
        secure=True,
        samesite="lax"
    )
    
    logger.info(f"User {username} authenticated successfully for OAuth")
    return response

@app.get("/oauth/consent", response_class=HTMLResponse)
async def oauth_consent_page(
    request: Request,
    client_id: str,
    redirect_uri: str,
    state: str,
    response_type: str = "code",
    scope: Optional[str] = None
):
    """OAuth consent page endpoint"""
    # Validate client_id
    if client_id != SMARTTHINGS_CLIENT_ID:
        raise HTTPException(status_code=400, detail="Invalid client ID")
    
    # Check if user is authenticated
    user_session = request.cookies.get("oauth_session")
    if not user_session or not redis_client.exists(f"oauth_session:{user_session}"):
        # Redirect back to login
        login_params = f"?client_id={client_id}&redirect_uri={redirect_uri}&state={state}&scope={scope or ''}&response_type={response_type}"
        return RedirectResponse(
            url=f"/oauth/authorize{login_params}",
            status_code=302
        )
    
    return await show_consent_page(client_id, redirect_uri, state, scope, response_type, user_session)

@app.post("/oauth/authorize/consent")
async def oauth_authorize_consent(
    request: Request,
    client_id: str = Form(...),
    redirect_uri: str = Form(...),
    state: str = Form(...),
    scope: str = Form(None),
    response_type: str = Form("code"),
    # SmartThings posts without an "action" form field; default to "allow"
    action: str = Form("allow")
):
    """Handle consent form submission"""
    # Check if user cancelled
    if action == "cancel":
        redirect_url = f"{redirect_uri}?error=access_denied&state={state}"
        return RedirectResponse(url=redirect_url, status_code=302)
    
    # Check if user is authenticated
    user_session = request.cookies.get("oauth_session")
    if not user_session or not redis_client.exists(f"oauth_session:{user_session}"):
        # Redirect back to login
        login_params = f"?client_id={client_id}&redirect_uri={redirect_uri}&state={state}&scope={scope or ''}&response_type={response_type}"
        return RedirectResponse(
            url=f"/oauth/authorize{login_params}",
            status_code=302
        )
    
    # Get user info from session
    session_data = redis_client.get(f"oauth_session:{user_session}")
    session_info = json.loads(session_data)
    user_id = session_info.get("user_id")
    
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid session")
    
    # User authorized - generate auth code
    auth_code = f"ac_{uuid.uuid4().hex}"
    
    # Store auth code in Redis (expires in 10 minutes)
    redis_client.setex(
        f"auth_code:{auth_code}",
        600,
        json.dumps({
            "client_id": client_id,
            "redirect_uri": redirect_uri,
            "user_id": user_id,
            "scope": scope or "device:all"
        })
    )
    
    # Log for debugging
    logger.info(f"OAuth authorized: client_id={client_id}, redirect_uri={redirect_uri}, state={state}, user_id={user_id}")
    
    # Redirect back with auth code
    redirect_url = f"{redirect_uri}?code={auth_code}&state={state}"
    return RedirectResponse(url=redirect_url, status_code=302)

@app.post("/oauth/token")
async def oauth_token(
    grant_type: str = Form(...),
    code: str = Form(None),
    refresh_token: str = Form(None),
    client_id: str = Form(...),
    client_secret: str = Form(...),
    db: AsyncSession = Depends(get_db)
):
    """OAuth token endpoint"""
    # Validate client credentials
    if client_id != SMARTTHINGS_CLIENT_ID or client_secret != SMARTTHINGS_CLIENT_SECRET:
        raise HTTPException(
            status_code=401,
            detail="Invalid client credentials",
            headers={"WWW-Authenticate": "Basic"}
        )
    
    if grant_type == "authorization_code":
        # Exchange auth code for tokens
        if not code:
            raise HTTPException(status_code=400, detail="Code required")
        
        # Validate auth code
        auth_data = redis_client.get(f"auth_code:{code}")
        if not auth_data:
            raise HTTPException(status_code=400, detail="Invalid or expired code")
        
        auth_info = json.loads(auth_data)
        
        # Generate tokens
        access_token = f"st_{uuid.uuid4().hex}"
        refresh_token_new = f"rt_{uuid.uuid4().hex}"
        expires_in = 3600  # 1 hour
        
        # Store tokens in database
        token_record = OAuthToken(
            user_id=auth_info["user_id"],
            access_token=access_token,
            refresh_token=refresh_token_new,
            expires_at=datetime.utcnow() + timedelta(seconds=expires_in)
        )
        db.add(token_record)
        await db.commit()
        
        # Delete used auth code
        redis_client.delete(f"auth_code:{code}")
        
        return {
            "access_token": access_token,
            "token_type": "Bearer",
            "expires_in": expires_in,
            "refresh_token": refresh_token_new
        }
    
    elif grant_type == "refresh_token":
        # Refresh access token
        if not refresh_token:
            raise HTTPException(status_code=400, detail="Refresh token required")
        
        # Validate refresh token
        result = await db.execute(
            select(OAuthToken).filter(OAuthToken.refresh_token == refresh_token)
        )
        token_record = result.scalar_one_or_none()
        
        if not token_record:
            raise HTTPException(status_code=400, detail="Invalid refresh token")
        
        # Generate new access token
        new_access_token = f"st_{uuid.uuid4().hex}"
        expires_in = 3600
        
        # Update token record
        token_record.access_token = new_access_token
        token_record.expires_at = datetime.utcnow() + timedelta(seconds=expires_in)
        await db.commit()
        
        return {
            "access_token": new_access_token,
            "token_type": "Bearer",
            "expires_in": expires_in
        }
    
    else:
        raise HTTPException(status_code=400, detail="Unsupported grant type")

# SmartThings Schema Cloud Connector Endpoint
@app.post("/schema")
async def smartthings_schema(
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """Handle SmartThings Schema Cloud Connector requests"""
    
    # Log incoming request headers
    logger.info("=== SCHEMA CONNECTOR REQUEST ===")
    logger.info(f"Request Headers: {dict(request.headers)}")
    
    body = await request.body()
    data = await request.json()
    
    # Log incoming request payload
    logger.info(f"Request Payload: {json.dumps(data, indent=2)}")
    
    # Get request headers
    headers = data.get("headers", {})
    request_id = headers.get("requestId")
    interaction_type = headers.get("interactionType")
    
    logger.info(f"SmartThings Schema request type: {interaction_type}, requestId: {request_id}")
    
    # Determine proper response interaction type per ST Schema specifications
    response_interaction_type = {
        "discoveryRequest": "discoveryResponse",
        "stateRefreshRequest": "stateRefreshResponse",
        "commandRequest": "commandResponse",
        "grantCallbackAccess": "grantCallbackAccessResponse",
        "integrationDeleted": "integrationDeletedResponse",
        "interactionResult": "interactionResult"  # Echo back for result notifications
    }.get(interaction_type, interaction_type)

    # Prepare response with corrected interactionType
    response = {
        "headers": {
            "schema": "st-schema",
            "version": "1.0",
            "interactionType": response_interaction_type,
            "requestId": request_id
        }
    }
    
    # Get authentication token
    auth = data.get("authentication", {})
    token = auth.get("token")
    
    try:
        if interaction_type == "discoveryRequest":
            # Handle device discovery
            devices_payload = await handle_schema_discovery(db, token)
            # handle_schema_discovery historically returned {"devices": [...]}
            # but ST Schema expects the array directly. Normalize here.
            if isinstance(devices_payload, dict) and "devices" in devices_payload:
                devices_payload = devices_payload["devices"]
            response["devices"] = devices_payload
            
        elif interaction_type == "stateRefreshRequest":
            # Handle state refresh
            devices = data.get("devices", [])
            states = []
            
            for device in devices:
                device_id = device.get("externalDeviceId")
                state = await handle_schema_state_refresh(device_id)
                if state:
                    states.append(state)
            
            response["deviceState"] = states
            
        elif interaction_type == "commandRequest":
            # Handle commands
            devices = data.get("devices", [])
            states = []
            
            for device in devices:
                device_id = device.get("externalDeviceId")
                commands = device.get("commands", [])
                state = await handle_schema_command(device_id, commands)
                if state:
                    states.append(state)
            
            response["deviceState"] = states
            
        elif interaction_type == "grantCallbackAccess":
            # Grant callback access - exchange code for tokens
            callback_authentication = data.get("callbackAuthentication")
            callback_urls = data.get("callbackUrls")
            
            logger.info("=== GRANT CALLBACK ACCESS START ===")
            logger.info(f"Received grantCallbackAccess request. Request ID: {request_id}")
            logger.info(f"Callback Authentication details: {json.dumps(callback_authentication, indent=2)}")
            logger.info(f"Callback URLs: {json.dumps(callback_urls, indent=2)}")
            
            # Extract the authorization code and exchange for tokens
            grant_type = callback_authentication.get("grantType")
            auth_code = callback_authentication.get("code")
            client_id = callback_authentication.get("clientId")
            oauth_token_url = callback_urls.get("oauthToken")
            
            if grant_type == "authorization_code" and auth_code and oauth_token_url:
                logger.info(f"Attempting to exchange authorization_code: {auth_code[:10]}... for tokens at URL: {oauth_token_url} with client_id: {client_id}")
                
                try:
                    # Exchange code for tokens
                    token_data = await exchange_callback_code_for_tokens(
                        oauth_token_url,
                        auth_code,
                        SMARTTHINGS_CALLBACK_CLIENT_ID,
                        SMARTTHINGS_CALLBACK_CLIENT_SECRET
                    )
                except Exception as e:
                    logger.error(f"Exception during token exchange: {e}")
                    token_data = None
                
                if token_data:
                    # Store tokens for this user
                    user_id = await get_user_id_from_token(token, db)
                    key = (
                        f"smartthings_callback:{user_id}"
                        if user_id is not None
                        else "smartthings_callback:global"
                    )
                    
                    callback_data = {
                        "access_token": token_data["accessToken"],
                        "refresh_token": token_data["refreshToken"],
                        "expires_at": (datetime.utcnow() + timedelta(seconds=token_data["expiresIn"])).isoformat(),
                        "urls": callback_urls,
                        "oauth_token_url": oauth_token_url,
                        "client_id": client_id,
                        "timestamp": datetime.utcnow().isoformat()
                    }
                    
                    redis_client.set(
                        key,
                        json.dumps(callback_data),
                        ex=86400 * 30  # 30 days expiry
                    )
                    logger.info(f"Successfully exchanged code and stored callback tokens under Redis key: {key}")
                    logger.info(f"Access token expires at: {callback_data['expires_at']}")
                    logger.debug(f"Stored callback data: {json.dumps(callback_data, indent=2)}")
                else:
                    logger.error("Failed to exchange callback code for tokens")
            else:
                logger.error(f"Invalid callback authentication: grant_type={grant_type}, has_code={bool(auth_code)}, has_url={bool(oauth_token_url)}")
            
            response = {}  # Empty response for grant callback
            logger.info("=== GRANT CALLBACK ACCESS END ===")
            
        elif interaction_type == "integrationDeleted":
            # Handle integration deletion - cleanup user data
            user_id = await get_user_id_from_token(token, db)
            if user_id:
                # Clean up callback tokens
                redis_client.delete(f"smartthings_callback:{user_id}")
                # Mark devices as unlinked
                await mark_devices_unlinked(user_id, db)
            
            response = {}  # Empty response
            
        elif interaction_type == "interactionResult":
            # Log interaction results for debugging
            originating_type = data.get("originatingInteractionType")
            global_error = data.get("globalError")
            device_errors = data.get("deviceState", [])
            
            logger.warning(f"Interaction result received for {originating_type}")
            if global_error:
                logger.error(f"Global error: {global_error}")
            for device_error in device_errors:
                logger.error(f"Device error for {device_error.get('externalDeviceId')}: {device_error.get('deviceError')}")
            
            response = {}  # No response needed
            
        else:
            # Unknown interaction type
            response["globalError"] = {
                "errorEnum": "INVALID-INTERACTION-TYPE",
                "detail": f"Unknown interaction type: {interaction_type}"
            }
            
    except Exception as e:
        logger.error(f"Error handling {interaction_type}: {e}")
        response["globalError"] = {
            "errorEnum": "BAD-REQUEST",
            "detail": str(e)
        }
    
    # Log outgoing response
    logger.info("=== SCHEMA CONNECTOR RESPONSE ===")
    logger.info(f"Response Headers: schema=st-schema, version=1.0, interactionType={response_interaction_type}, requestId={request_id}")
    logger.info(f"Response Payload: {json.dumps(response, indent=2)}")
    logger.info("=== END SCHEMA CONNECTOR EXCHANGE ===")
    
    return response

# SmartThings sometimes posts schema payloads to the root path ("/").
# Provide a shim that forwards those requests to the /schema handler.
@app.post("/")
async def smartthings_schema_root(
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    return await smartthings_schema(request, db)

async def get_user_id_from_token(token: str, db: AsyncSession) -> Optional[int]:
    """Get user ID from OAuth token"""
    if not token:
        return None
    
    result = await db.execute(
        select(OAuthToken).filter(OAuthToken.access_token == token)
    )
    token_record = result.scalar_one_or_none()
    
    return token_record.user_id if token_record else None

async def mark_devices_unlinked(user_id: int, db: AsyncSession):
    """Mark all devices for a user as unlinked from SmartThings"""
    result = await db.execute(
        update(Device)
        .where(Device.user_id == user_id)
        .values(smartthings_device_id=None)
    )
    await db.commit()
    logger.info(f"Marked {result.rowcount} devices as unlinked for user {user_id}")

async def handle_schema_discovery(db: AsyncSession, token: str = None) -> List[Dict[str, Any]]:
    """Handle Schema discovery request"""
    # Check if we need to request callback access
    logger.info("Handling discovery request...")
    request_grant_callback = False
    user_id = await get_user_id_from_token(token, db) if token else None
    logger.info(f"Discovery request received with token. User ID from token: {user_id}")

    if user_id:
        # Check if callback token exists or is expired
        callback_data = redis_client.get(f"smartthings_callback:{user_id}")
        if not callback_data:
            request_grant_callback = True
    
    # If the caller is authenticated, limit results to that user's devices
    if user_id is not None:
        logger.info(f"Querying devices for user_id: {user_id}")
        result = await db.execute(
            select(Device).where(Device.user_id == user_id)
        )
    else:
        # For initial account linking SmartThings calls discovery without auth.
        # Return all devices so the user can pick which to add.
        logger.info("Querying all devices (no user token provided)")
        result = await db.execute(select(Device))
    devices = result.scalars().all()

    logger.info(f"Found {len(devices)} devices in DB for discovery.")
    
    schema_devices = []
    for device in devices:
        # Get device state from Redis
        state_key = f"thermostat:{device.serial_number}:state"
        state_data = redis_client.get(state_key)
        
        # Prepare device payload for SmartThings
        # Include device even if it hasn't reported state yet
        state = json.loads(state_data) if state_data else {
            "current_temp": 72,
            "target_temp": 72,
            "mode": "auto",
            "fan_mode": "auto",
            "current_humidity": 40,
            "is_running": False
        }
        # Get metadata
        metadata_key = f"device:{device.serial_number}:metadata"
        metadata = redis_client.hgetall(metadata_key)
        logger.debug(f"Preparing device {device.serial_number} for discovery response.")
        
        schema_devices.append({
            "externalDeviceId": device.serial_number,
            "deviceCookie": {"userId": device.user_id},
            "friendlyName": f"Virtual Thermostat {device.serial_number[-4:]}",
            "manufacturerInfo": {
                "manufacturerName": "Virtual Testbed",
                "modelName": "VT-1000",
                "hwVersion": "1.0",
                "swVersion": "1.0"
            },
            "deviceContext": {
                "roomName": metadata.get("room_name", "Virtual Room"),
                "groups": ["Virtual Thermostats"],
                "categories": ["thermostat"]
            },
            "deviceHandlerType": "c2c-thermostat-battery",
            "deviceUniqueId": device.serial_number
        })
    logger.info(f"Prepared {len(schema_devices)} devices for SmartThings response payload.")
    
    response = {"devices": schema_devices}
    if request_grant_callback:
        response["requestGrantCallbackAccess"] = True
    
    return response

async def handle_schema_state_refresh(device_id: str, include_timestamp: bool = False) -> Optional[Dict[str, Any]]:
    """Handle Schema state refresh request"""
    logger.info(f"=== STATE REFRESH DEBUG for {device_id} ===")
    
    # Check if device exists
    device_exists_key = f"device:{device_id}:metadata"
    if not redis_client.exists(device_exists_key):
        logger.warning(f"Device {device_id} metadata not found in Redis")
        return {
            "externalDeviceId": device_id,
            "deviceError": [{
                "errorEnum": "DEVICE-DELETED",
                "detail": "Device has been removed from the system"
            }]
        }
    
    # Get state from Redis
    state_key = f"thermostat:{device_id}:state"
    state_data = redis_client.get(state_key)
    
    if not state_data:
        logger.warning(f"No state data found for device {device_id} at key {state_key}")
        return {
            "externalDeviceId": device_id,
            "deviceError": [{
                "errorEnum": "DEVICE-OFFLINE",
                "detail": "Device is currently offline"
            }]
        }
    
    state = json.loads(state_data)
    logger.info(f"Device {device_id} current state: {state}")
    timestamp = int(time.time() * 1000)
    
    # Check device health
    is_online = state.get("online", True)
    if not is_online:
        logger.warning(f"Device {device_id} is marked as offline")
        return {
            "externalDeviceId": device_id,
            "states": [{
                "component": "main",
                "capability": "st.healthCheck",
                "attribute": "healthStatus",
                "value": "offline",
                "timestamp": timestamp
            }]
        }
    
    # Convert to Schema format with all required states
    states_list = [
        {
            "component": "main",
            "capability": "st.healthCheck",
            "attribute": "healthStatus",
            "value": "online"
        },
        {
            "component": "main",
            "capability": "st.temperatureMeasurement",
            "attribute": "temperature",
            "value": state["current_temp"],
            "unit": "F"
        },
        {
            "component": "main",
            "capability": "st.thermostatCoolingSetpoint",
            "attribute": "coolingSetpoint",
            "value": state["target_temp"],
            "unit": "F"
        },
        {
            "component": "main",
            "capability": "st.thermostatHeatingSetpoint",
            "attribute": "heatingSetpoint",
            "value": state["target_temp"],
            "unit": "F"
        },
        {
            "component": "main",
            "capability": "st.thermostatMode",
            "attribute": "thermostatMode",
            "value": state["mode"]
        },
        {
            "component": "main",
            "capability": "st.thermostatFanMode",
            "attribute": "thermostatFanMode",
            "value": state["fan_mode"]
        },
        {
            "component": "main",
            "capability": "st.relativeHumidityMeasurement",
            "attribute": "humidity",
            "value": state["current_humidity"],
            "unit": "%"
        },
        {
            "component": "main",
            "capability": "st.thermostatOperatingState",
            "attribute": "thermostatOperatingState",
            "value": "idle" if not state["is_running"] else state["mode"]
        }
    ]
    
    # Add timestamps only if requested (for callbacks, not for request responses)
    if include_timestamp:
        for state_item in states_list:
            state_item["timestamp"] = timestamp
    
    response_states = {
        "externalDeviceId": device_id,
        "states": states_list
    }
    
    logger.info(f"Returning state response for {device_id} with {len(response_states['states'])} attributes")
    logger.info(f"=== END STATE REFRESH DEBUG ===")
    return response_states

async def wait_for_command_execution(device_id: str, commands: List[Dict[str, Any]], timeout: float = 10.0, poll_interval: float = 0.5):
    """Wait for commands to be executed by polling the device state"""
    logger.info(f"Waiting for command execution on device {device_id}")
    
    # Get current state before command execution
    state_key = f"thermostat:{device_id}:state"
    initial_state_data = redis_client.get(state_key)
    if not initial_state_data:
        logger.warning(f"No initial state found for device {device_id}")
        return
    
    initial_state = json.loads(initial_state_data)
    
    # Extract expected values from commands
    expected_changes = {}
    for command in commands:
        capability = command.get("capability")
        cmd = command.get("command")
        arguments = command.get("arguments", [])
        
        if capability == "st.thermostatCoolingSetpoint" and cmd == "setCoolingSetpoint":
            expected_changes["target_temp"] = arguments[0] if arguments else 72
        elif capability == "st.thermostatHeatingSetpoint" and cmd == "setHeatingSetpoint":
            expected_changes["target_temp"] = arguments[0] if arguments else 72
        elif capability == "st.thermostatMode" and cmd == "setThermostatMode":
            expected_changes["mode"] = arguments[0] if arguments else "auto"
        elif capability == "st.thermostatFanMode" and cmd == "setThermostatFanMode":
            expected_changes["fan_mode"] = arguments[0] if arguments else "auto"
    
    if not expected_changes:
        logger.info("No state changes expected, skipping wait")
        return
    
    logger.info(f"Expected state changes: {expected_changes}")
    
    # Poll for state changes
    start_time = asyncio.get_event_loop().time()
    while (asyncio.get_event_loop().time() - start_time) < timeout:
        current_state_data = redis_client.get(state_key)
        if current_state_data:
            current_state = json.loads(current_state_data)
            
            # Check if all expected changes have been applied
            changes_applied = True
            for key, expected_value in expected_changes.items():
                if current_state.get(key) != expected_value:
                    changes_applied = False
                    break
            
            if changes_applied:
                logger.info(f"All command changes applied to device {device_id}")
                return
        
        await asyncio.sleep(poll_interval)
    
    logger.warning(f"Timeout waiting for command execution on device {device_id}")

async def handle_schema_command(device_id: str, commands: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    """Handle Schema command request"""
    for command in commands:
        component = command.get("component", "main")
        capability = command.get("capability")
        cmd = command.get("command")
        arguments = command.get("arguments", [])
        
        # Queue command for thermostat
        command_data = {
            "command": "",
            "params": {}
        }
        
        if capability == "st.thermostatCoolingSetpoint" and cmd == "setCoolingSetpoint":
            command_data["command"] = "set_temperature"
            command_data["params"]["temperature"] = arguments[0] if arguments else 72
        elif capability == "st.thermostatHeatingSetpoint" and cmd == "setHeatingSetpoint":
            command_data["command"] = "set_temperature"
            command_data["params"]["temperature"] = arguments[0] if arguments else 72
        elif capability == "st.thermostatMode" and cmd == "setThermostatMode":
            command_data["command"] = "set_mode"
            command_data["params"]["mode"] = arguments[0] if arguments else "auto"
        elif capability == "st.thermostatFanMode" and cmd == "setThermostatFanMode":
            command_data["command"] = "set_fan_mode"
            command_data["params"]["fan_mode"] = arguments[0] if arguments else "auto"
        
        # Queue command in Redis
        command_key = f"thermostat:{device_id}:commands"
        redis_client.lpush(command_key, json.dumps(command_data))
    
    # Wait for the command to be processed by polling the state
    await wait_for_command_execution(device_id, commands)
    
    # Return updated state
    return await handle_schema_state_refresh(device_id)

# ------------------------------------------------------------
# Callback helpers
# ------------------------------------------------------------

async def send_discovery_callback(user_id: int):
    """Push an on-demand discoveryCallback listing all the user's devices."""
    callback_raw = redis_client.get(f"smartthings_callback:{user_id}") or redis_client.get("smartthings_callback:global")
    if not callback_raw:
        logger.warning("No discovery callback token/url found for user %s", user_id)
        return
    cb = json.loads(callback_raw)
    discovery_url = cb["urls"].get("discoveryCallback") or cb["urls"].get("discoveryCallbackUrl")
    if not discovery_url:
        return

    # Check if we have access token (new format)
    access_token = cb.get("access_token")
    if not access_token:
        logger.warning(f"No access token found for discovery callback for user {user_id}")
        return

    # Build device list
    async with AsyncSessionLocal() as db:
        res = await db.execute(select(Device).where(Device.user_id == user_id))
        devices = res.scalars().all()

    device_array = []
    for d in devices:
        device_array.append({
            "externalDeviceId": d.serial_number,
            "deviceCookie": {"userId": user_id},
            "friendlyName": f"Virtual Thermostat {d.serial_number[-4:]}",
            "manufacturerInfo": {
                "manufacturerName": "Virtual Testbed",
                "modelName": "VT-1000",
                "hwVersion": "1.0",
                "swVersion": "1.0"
            },
            "deviceContext": {"roomName": "Virtual Room"},
            "deviceHandlerType": "c2c-thermostat-battery"
        })

    payload = {
        "headers": {
            "schema": "st-schema",
            "version": "1.0",
            "interactionType": "discoveryCallback",
            "requestId": str(uuid.uuid4())
        },
        "devices": device_array
    }

    try:
        async with aiohttp.ClientSession() as session:
            headers = {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json"
            }
            async with session.post(discovery_url, json=payload, headers=headers) as resp:
                if resp.status == 200:
                    logger.info("Discovery callback sent for user %s", user_id)
                else:
                    logger.error("Discovery callback failed (%s)", resp.status)
    except Exception as e:
        logger.error("Error sending discovery callback: %s", e)

# Callback function to send state updates to SmartThings
async def send_state_update_to_smartthings(device_id: str, state: Dict[str, Any]):
    """Send state update to SmartThings via callback"""
    # Find the callback data - try user-specific first, then global
    callback_data = None
    user_id = None
    
    # Get device to find user_id
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(Device).filter(Device.serial_number == device_id))
        device = result.scalar_one_or_none()
        
        if device and device.user_id:
            user_id = device.user_id
            callback_data = redis_client.get(f"smartthings_callback:{device.user_id}")
        
        # Fallback to global callback
        if not callback_data:
            callback_data = redis_client.get("smartthings_callback:global")
    
    if not callback_data:
        logger.warning(f"No SmartThings callback configured for device {device_id}")
        return
    
    callback_info = json.loads(callback_data)
    state_callback_url = callback_info["urls"].get("stateCallback")
    
    if not state_callback_url:
        logger.warning(f"No stateCallback URL configured for device {device_id}")
        return
    
    # Check if we have access token (new format) or old authentication
    access_token = callback_info.get("access_token")
    if not access_token:
        logger.warning(f"No access token found for device {device_id} - callback not properly exchanged")
        return
    
    # Check if token is expired
    expires_at_str = callback_info.get("expires_at")
    if expires_at_str:
        expires_at = datetime.fromisoformat(expires_at_str)
        if datetime.utcnow() >= expires_at:
            logger.info(f"Access token expired for device {device_id}, attempting refresh...")
            # Try to refresh token
            new_token_data = await refresh_callback_tokens(callback_info)
            if new_token_data:
                # Update stored callback data
                callback_info["access_token"] = new_token_data["accessToken"]
                callback_info["refresh_token"] = new_token_data["refreshToken"]
                callback_info["expires_at"] = (datetime.utcnow() + timedelta(seconds=new_token_data["expiresIn"])).isoformat()
                
                # Store updated tokens
                key = f"smartthings_callback:{user_id}" if user_id else "smartthings_callback:global"
                redis_client.set(key, json.dumps(callback_info), ex=86400 * 30)
                
                access_token = new_token_data["accessToken"]
                logger.info(f"Successfully refreshed access token for device {device_id}")
            else:
                logger.error(f"Failed to refresh access token for device {device_id}")
                return
    
    # Prepare Schema state update
    device_state = await handle_schema_state_refresh(device_id, include_timestamp=True)
    if not device_state:
        logger.warning(f"Could not get state for device {device_id}")
        return
        
    update_data = {
        "headers": {
            "schema": "st-schema",
            "version": "1.0",
            "interactionType": "stateCallback",
            "requestId": str(uuid.uuid4())
        },
        "authentication": {               # NEW
            "tokenType": "Bearer",
            "token": access_token
        },
        "deviceState": [device_state]
    }
    
    # Log the state callback we're sending
    logger.info(f"=== SENDING STATE CALLBACK to SmartThings ===")
    logger.info(f"Device: {device_id}")
    logger.info(f"Callback URL: {state_callback_url}")
    logger.info(f"Using access token: {access_token[:10]}...")
    logger.info(f"Payload: {json.dumps(update_data, indent=2)}")
    
    # Send update with proper access token
    try:
        async with aiohttp.ClientSession() as session:
            headers = {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json"
            }
            
            logger.info(f"Request headers: {headers}")
            
            async with session.post(
                state_callback_url,
                json=update_data,
                headers=headers
            ) as response:
                response_text = await response.text()
                if response.status == 202:
                    logger.info(f"State update sent to SmartThings for {device_id}")
                else:
                    logger.error(f"Failed to send state update for {device_id}: {response.status} - {response_text}")
                logger.info(f"=== END STATE CALLBACK ===")
    except Exception as e:
        logger.error(f"Error sending state update to SmartThings for {device_id}: {e}")

# SmartThings Reciprocal Access Token Endpoints
@app.post("/oauth/callback/token")
async def callback_access_token(
    grant_type: str = Form(...),
    client_id: str = Form(...),
    client_secret: str = Form(...),
    scope: str = Form(None),
    refresh_token: str = Form(None),
    db: AsyncSession = Depends(get_db)
):
    """SmartThings reciprocal access token endpoint for callbacks"""
    logger.info(f"=== RECIPROCAL ACCESS TOKEN REQUEST ===")
    logger.info(f"Grant type: {grant_type}")
    logger.info(f"Client ID: {client_id}")
    logger.info(f"Scope: {scope}")
    
    # Validate client credentials
    if client_id != SMARTTHINGS_CLIENT_ID or client_secret != SMARTTHINGS_CLIENT_SECRET:
        logger.error(f"Invalid client credentials for reciprocal token")
        raise HTTPException(
            status_code=401,
            detail="Invalid client credentials",
            headers={"WWW-Authenticate": "Basic"}
        )
    
    if grant_type == "client_credentials":
        # Generate callback access token
        callback_access_token = f"cb_{uuid.uuid4().hex}"
        callback_refresh_token = f"cbr_{uuid.uuid4().hex}"
        expires_in = 3600  # 1 hour
        
        # Store callback token in Redis for validation
        redis_client.setex(
            f"callback_token:{callback_access_token}",
            expires_in,
            json.dumps({
                "client_id": client_id,
                "scope": scope or "callback",
                "issued_at": datetime.utcnow().isoformat(),
                "token_type": "callback"
            })
        )
        
        # Store refresh token
        redis_client.setex(
            f"callback_refresh:{callback_refresh_token}",
            86400 * 7,  # 7 days
            json.dumps({
                "access_token": callback_access_token,
                "client_id": client_id,
                "scope": scope or "callback"
            })
        )
        
        logger.info(f"Generated callback access token: {callback_access_token}")
        
        return {
            "access_token": callback_access_token,
            "token_type": "Bearer",
            "expires_in": expires_in,
            "refresh_token": callback_refresh_token,
            "scope": scope or "callback"
        }
    
    elif grant_type == "refresh_token":
        if not refresh_token:
            raise HTTPException(status_code=400, detail="Refresh token required")
        
        # Validate refresh token
        refresh_data = redis_client.get(f"callback_refresh:{refresh_token}")
        if not refresh_data:
            raise HTTPException(status_code=400, detail="Invalid refresh token")
        
        refresh_info = json.loads(refresh_data)
        
        # Generate new access token
        new_access_token = f"cb_{uuid.uuid4().hex}"
        expires_in = 3600
        
        # Store new access token
        redis_client.setex(
            f"callback_token:{new_access_token}",
            expires_in,
            json.dumps({
                "client_id": refresh_info["client_id"],
                "scope": refresh_info["scope"],
                "issued_at": datetime.utcnow().isoformat(),
                "token_type": "callback"
            })
        )
        
        # Update refresh token with new access token
        refresh_info["access_token"] = new_access_token
        redis_client.setex(
            f"callback_refresh:{refresh_token}",
            86400 * 7,  # 7 days
            json.dumps(refresh_info)
        )
        
        logger.info(f"Refreshed callback access token: {new_access_token}")
        
        return {
            "access_token": new_access_token,
            "token_type": "Bearer",
            "expires_in": expires_in,
            "scope": refresh_info["scope"]
        }
    
    else:
        raise HTTPException(status_code=400, detail="Unsupported grant type")

async def exchange_callback_code_for_tokens(
    oauth_token_url: str,
    auth_code: str,
    client_id: str,
    client_secret: str
) -> Optional[Dict[str, Any]]:
    """Exchange authorization code for access/refresh tokens from SmartThings"""
    logger.info("=== EXCHANGING CALLBACK AUTH CODE FOR TOKENS START ===")
    logger.info(f"Target OAuth Token URL: {oauth_token_url}")
    logger.info(f"Authorization Code (first 10 chars): {auth_code[:10]}...")
    logger.info(f"Client ID for exchange: {client_id}")
    
    try:
        async with aiohttp.ClientSession() as session:
            # Use proper SmartThings Schema format
            payload = {
                "headers": {
                    "schema": "st-schema",
                    "version": "1.0",
                    "interactionType": "accessTokenRequest",
                    "requestId": str(uuid.uuid4())
                },
                "callbackAuthentication": {
                    "grantType": "authorization_code",
                    "code": auth_code,
                    "clientId": client_id,
                    "clientSecret": client_secret
                }
            }
            
            headers = {
                "Content-Type": "application/json"
            }
            
            logger.debug(f"Sending token exchange request to SmartThings: {json.dumps(payload, indent=2)}")
            
            async with session.post(
                oauth_token_url,
                json=payload,
                headers=headers
            ) as response:
                logger.info(f"SmartThings token exchange response status: {response.status}")
                response_text = await response.text()
                logger.debug(f"SmartThings token exchange raw response: {response_text}")
                
                if response.status == 200:
                    response_json = await response.json()
                    # Tokens are nested under callbackAuthentication
                    if "callbackAuthentication" in response_json:
                        token_data = response_json["callbackAuthentication"]
                        logger.info("Successfully exchanged authorization_code for tokens from SmartThings.")
                        logger.info(f"Received Access Token (first 10 chars): {token_data.get('accessToken', '')[:10]}...")
                        logger.info(f"Received Refresh Token (first 10 chars): {token_data.get('refreshToken', '')[:10]}...")
                        logger.info(f"Access token expires in: {token_data.get('expiresIn')} seconds.")
                        return token_data
                    logger.error("Token exchange response from SmartThings missing 'callbackAuthentication' field.")
                    return None
                else:
                    logger.error(f"Token exchange with SmartThings failed. Status: {response.status}")
                    return None
                    
    except Exception as e:
        logger.error(f"Error exchanging callback code for tokens: {e}")
        return None

async def refresh_callback_tokens(callback_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Refresh expired callback tokens"""
    oauth_token_url = callback_data.get("oauth_token_url")
    refresh_token = callback_data.get("refresh_token")
    client_id = SMARTTHINGS_CALLBACK_CLIENT_ID
    client_secret = SMARTTHINGS_CALLBACK_CLIENT_SECRET
    
    if not all([oauth_token_url, refresh_token, client_id]):
        logger.error("Missing required data for token refresh")
        return None
    
    logger.info("=== REFRESHING CALLBACK TOKENS START ===")
    logger.info(f"Target OAuth Token URL for refresh: {oauth_token_url}")
    logger.info(f"Refresh Token (first 10 chars): {refresh_token[:10]}...")
    logger.info(f"Client ID for refresh: {client_id}")
    
    try:
        async with aiohttp.ClientSession() as session:
            # Use proper SmartThings Schema format for refresh too
            payload = {
                "headers": {
                    "schema": "st-schema",
                    "version": "1.0",
                    "interactionType": "refreshAccessTokens",
                    "requestId": str(uuid.uuid4())
                },
                "callbackAuthentication": {
                    "grantType": "refresh_token",
                    "refreshToken": refresh_token,
                    "clientId": client_id,
                    "clientSecret": client_secret
                }
            }
            
            headers = {
                "Content-Type": "application/json"
            }
            
            logger.debug(f"Sending token refresh request to SmartThings: {json.dumps(payload, indent=2)}")
            
            async with session.post(
                oauth_token_url,
                json=payload,
                headers=headers
            ) as response:
                logger.info(f"SmartThings token refresh response status: {response.status}")
                response_text = await response.text()
                logger.debug(f"SmartThings token refresh raw response: {response_text}")
                
                if response.status == 200:
                    response_json = await response.json()
                    # Tokens are nested under callbackAuthentication
                    if "callbackAuthentication" in response_json:
                        token_data = response_json["callbackAuthentication"]
                        logger.info("Successfully refreshed callback tokens from SmartThings.")
                        logger.info(f"New Access Token (first 10 chars): {token_data.get('accessToken', '')[:10]}...")
                        logger.info(f"New Refresh Token (first 10 chars): {token_data.get('refreshToken', '')[:10]}...")
                        logger.info(f"New access token expires in: {token_data.get('expiresIn')} seconds.")
                        return token_data
                    logger.error("Token refresh response from SmartThings missing 'callbackAuthentication' field.")
                    return None
                else:
                    logger.error(f"Token refresh with SmartThings failed. Status: {response.status}")
                    return None
                    
    except Exception as e:
        logger.error(f"Error refreshing callback tokens: {e}")
        return None

def validate_callback_token(token: str) -> bool:
    """Validate SmartThings callback access token"""
    if not token:
        return False
    
    # Remove 'Bearer ' prefix if present
    if token.startswith('Bearer '):
        token = token[7:]
    
    token_data = redis_client.get(f"callback_token:{token}")
    if not token_data:
        logger.warning(f"Invalid or expired callback token: {token}")
        return False
    
    token_info = json.loads(token_data)
    logger.info(f"Valid callback token for client: {token_info.get('client_id')}")
    return True

# User Management APIs
@app.post("/api/users/register")
async def register_user(
    username: str,
    password: str,
    db: AsyncSession = Depends(get_db)
):
    """Register a new user"""
    # Check if user exists
    result = await db.execute(select(User).filter(User.username == username))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Username already exists")
    
    # Create user
    user = User(
        username=username,
        password_hash=get_password_hash(password)
    )
    db.add(user)
    await db.commit()
    
    return {"username": username, "status": "created"}

@app.post("/api/users/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """User login"""
    # For demo, simplified authentication
    if form_data.username == "admin" and form_data.password == "admin123":
        access_token = create_access_token(data={"sub": form_data.username})
        return {"access_token": access_token, "token_type": "bearer"}
    
    raise HTTPException(
        status_code=401,
        detail="Incorrect username or password",
        headers={"WWW-Authenticate": "Bearer"}
    )

# Additional User APIs
@app.get("/api/users")
async def list_users(db: AsyncSession = Depends(get_db)):
    """List all registered users"""
    result = await db.execute(select(User))
    users = result.scalars().all()
    return [
        {
            "id": user.id,
            "username": user.username,
            "created_at": user.created_at.isoformat() if user.created_at else None
        }
        for user in users
    ]

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
