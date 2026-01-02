import os, datetime as dt
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func, desc

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATA_DB_URL")
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

class News(db.Model):
    __tablename__ = "news"
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey("companies.id"))
    source = db.Column(db.Text)
    headline = db.Column(db.Text)
    url = db.Column(db.Text)
    published_at = db.Column(db.DateTime(timezone=True))

class Sentiment(db.Model):
    __tablename__ = "sentiments"
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey("companies.id"))
    headline_id = db.Column(db.Integer, db.ForeignKey("news.id"))
    source = db.Column(db.Text)
    score = db.Column(db.Numeric)
    magnitude = db.Column(db.Numeric)
    computed_at = db.Column(db.DateTime(timezone=True), default=func.now())

@app.post("/ingest/sample")
def ingest_sample():
    """Seed minimal sectors/companies and a couple of sentiments for demo."""
    tech = Sector.query.filter_by(name="Technology").first()
    if not tech:
        tech = Sector(name="Technology")
        db.session.add(tech)
        db.session.commit()
    aapl = Company.query.filter_by(ticker="AAPL").first()
    if not aapl:
        aapl = Company(ticker="AAPL", name="Apple Inc.", sector_id=tech.id)
        db.session.add(aapl)
        db.session.commit()
    s = Sentiment(company_id=aapl.id, source="sample", score=0.42, magnitude=0.5)
    db.session.add(s)
    db.session.commit()
    return {"ok": True, "seeded": True}

@app.get("/companies")
def companies():
    rows = db.session.query(Company.id, Company.ticker, Company.name).order_by(Company.ticker).all()
    return jsonify([{"id": r.id, "ticker": r.ticker, "name": r.name} for r in rows])

@app.get("/sentiments")
def sentiments():
    sector = request.args.get("sector")
    days = int(request.args.get("days", "7"))
    q = db.session.query(Company.ticker, func.avg(Sentiment.score).label("avg_score"))         .join(Sentiment, Sentiment.company_id == Company.id)         .join(Sector, Sector.id == Company.sector_id, isouter=True)         .filter(Sentiment.computed_at >= func.now() - dt.timedelta(days=days))         .group_by(Company.ticker)
    if sector:
        q = q.filter(func.lower(Sector.name) == sector.lower())
    rows = q.order_by(desc("avg_score")).limit(100).all()
    return jsonify([{"ticker": r.ticker, "avg_score": float(r.avg_score)} for r in rows])

@app.get("/healthz")
def healthz():
    return {"ok": True}

if __name__ == "__main__":
    port = int(os.getenv("PORT", "5002"))
    with app.app_context():
        db.create_all()
    app.run(host="0.0.0.0", port=port)
