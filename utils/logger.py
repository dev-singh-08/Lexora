from database import db
from models import QuestionHistory, UnansweredQuestion

def log_question(question, sector, user_id, response=None):
    """Logs successful research inquiries with the generated response."""
    entry = QuestionHistory(
        question=question,
        sector=sector,
        user_id=user_id,
        response=response
    )

    db.session.add(entry)
    db.session.commit()

def log_unanswered(question, sector):
    """Logs inquiries that returned no grounded results for empirical analysis."""
    entry = UnansweredQuestion(
        question=question,
        sector=sector
    )

    db.session.add(entry)
    db.session.commit()
