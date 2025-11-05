from database import Base, Engine
from models import *

print("Creating all tables...")
Base.metadata.create_all(bind=Engine)
print("✅ Tables created successfully!")