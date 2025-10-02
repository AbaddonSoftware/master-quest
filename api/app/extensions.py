from app.persistence.orm import SoftDeleteQuery
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy(query_class=SoftDeleteQuery)
