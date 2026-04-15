from image.database import Base, engine

Base.metadata.create_all(bind=engine)

print("DB tables created successfully")