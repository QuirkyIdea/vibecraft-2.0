from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, UserFeedback
from feedback_service import submit_feedback
from config import get_settings

settings = get_settings()
engine = create_engine(settings.database_url)
SessionLocal = sessionmaker(bind=engine)
db = SessionLocal()

print("Submitting feedback...")
try:
    result = submit_feedback(
        db, 
        output_id="claim_1", 
        output_type="CLAIM", 
        project_id=2, 
        feedback_type="HELPFUL", 
        comment="Test comment"
    )
    print(f"Result: {result}")
except Exception as e:
    import traceback
    traceback.print_exc()
