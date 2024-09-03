from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Float, ForeignKey, Enum, JSON, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, backref

# Remove duplicate imports
# ... (rest of the code)

Base = declarative_base()

# ... (rest of the code)
