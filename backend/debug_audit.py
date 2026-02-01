from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, AuditLog, ActionType
from audit_service import log_action
from config import get_settings

settings = get_settings()
# Ensure DB url is correct
print(f"DB URL: {settings.database_url}")
engine = create_engine(settings.database_url)
SessionLocal = sessionmaker(bind=engine)
db = SessionLocal()

print("Submitting audit log...")
try:
    # Ensure table exists (simple check)
    # Base.metadata.create_all(bind=engine) 
    
    success = log_action(
        db, 
        "PROJECT_CREATED", 
        "Project", 
        999, 
        "debug_user",
        metadata={"test": "true"}
    )
    print(f"Log success: {success}")
    
    # Read it back
    log = db.query(AuditLog).filter(AuditLog.entity_id == 999).first()
    if log:
        print(f"Found log: {log.action_type} - {log.created_at}")
    else:
        print("Log NOT found in DB!")
        
except Exception as e:
    import traceback
    traceback.print_exc()
