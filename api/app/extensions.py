from app.persistence.orm import SoftDeleteQuery
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy(query_class=SoftDeleteQuery)
sessions = Session()
