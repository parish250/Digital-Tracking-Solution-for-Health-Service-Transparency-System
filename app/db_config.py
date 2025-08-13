from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL = "mysql+pymysql://admin:securePass123@localhost:3306/digital_aid_db"

engine = create_engine(DATABASE_URL, echo=True, future=True)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Dependency to get DB session for FastAPI routes
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Test model and function to verify DB connection
class TestUser(Base):
    __tablename__ = "test_users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50))

def test_db():
    # Create tables
    Base.metadata.create_all(bind=engine)

    # Open session
    db = SessionLocal()
    try:
        # Add a test user
        user = TestUser(name="Test User")
        db.add(user)
        db.commit()
        db.refresh(user)

        # Query to verify
        queried = db.query(TestUser).filter_by(name="Test User").first()
        print(f"Queried User: {queried.name} with id: {queried.id}")

        # Cleanup test data
        db.delete(queried)
        db.commit()
    finally:
        db.close()

if __name__ == "__main__":
    test_db()
