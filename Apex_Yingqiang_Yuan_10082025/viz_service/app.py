import os
from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func, desc

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("VIZ_DB_URL")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

class Sector(db.Model):
    __tablename__ = "sectors"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text, unique=True, nullable=False)

class Company(db.Model):
    __tablename__ = "companies"
    id = db.Column(db.Integer, primary_key=True)
    ticker = db.Column(db.Text, unique=True, nullable=False)
    name = db.Column(db.Text, nullable=False)
    sector_id = db.Column(db.Integer, db.ForeignKey("sectors.id"))

class Sentiment(db.Model):
    __tablename__ = "sentiments"
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey("companies.id"))
    score = db.Column(db.Numeric)
    computed_at = db.Column(db.DateTime(timezone=True), default=func.now())

@app.get("/treemap/top5")
def treemap_top5():
    # Approximate: top 5 companies by avg sentiment within each sector
    subq = db.session.query(
        Company.sector_id,
        Company.ticker,
        func.avg(Sentiment.score).label("avg_score")
    ).join(Sentiment, Sentiment.company_id == Company.id)      .group_by(Company.sector_id, Company.ticker).subquery()

    # Rank within sector
    from sqlalchemy import over
    rank_col = func.rank().over(partition_by=subq.c.sector_id, order_by=desc(subq.c.avg_score)).label("rnk")
    ranked = db.session.query(
        subq.c.sector_id, subq.c.ticker, subq.c.avg_score, rank_col
    ).subquery()

    q = db.session.query(
        Sector.name.label("sector"),
        ranked.c.ticker,
        ranked.c.avg_score
    ).join(Sector, Sector.id == ranked.c.sector_id).filter(ranked.c.rnk <= 5)
    rows = q.all()
    return jsonify([{"sector": r.sector, "ticker": r.ticker, "score": float(r.avg_score)} for r in rows])

@app.get("/treemap/low5")
def treemap_low5():
    from sqlalchemy import over
    subq = db.session.query(
        Company.sector_id,
        Company.ticker,
        func.avg(Sentiment.score).label("avg_score")
    ).join(Sentiment, Sentiment.company_id == Company.id)      .group_by(Company.sector_id, Company.ticker).subquery()

    rank_col = func.rank().over(partition_by=subq.c.sector_id, order_by=subq.c.avg_score).label("rnk")
    ranked = db.session.query(
        subq.c.sector_id, subq.c.ticker, subq.c.avg_score, rank_col
    ).subquery()

    q = db.session.query(
        Sector.name.label("sector"),
        ranked.c.ticker,
        ranked.c.avg_score
    ).join(Sector, Sector.id == ranked.c.sector_id).filter(ranked.c.rnk <= 5)
    rows = q.all()
    return jsonify([{"sector": r.sector, "ticker": r.ticker, "score": float(r.avg_score)} for r in rows])

@app.get("/healthz")
def healthz():
    return {"ok": True}

if __name__ == "__main__":
    port = int(os.getenv("PORT", "5003"))
    with app.app_context():
        db.create_all()
    app.run(host="0.0.0.0", port=port)
