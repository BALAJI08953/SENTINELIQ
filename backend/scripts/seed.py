"""Deterministic demo seed. All records are FICTIONAL and flagged is_demo=True.

Usage (from backend/): python -m scripts.seed [--reset]
"""
import hashlib
import sys
from datetime import UTC, datetime, timedelta

from sqlalchemy import select

from app.core.database import Base, SessionLocal, engine
from app.models import (
    Company,
    CompanyRelationship,
    DeliveryRecipient,
    DeliverySchedule,
    Event,
    Evidence,
    Observation,
    Report,
    RiskAssessment,
    Source,
    UserSettings,
    Workflow,
)
from app.services.risk.scoring import score_risk

BASE = datetime(2026, 9, 1, 9, 0, tzinfo=UTC)

COMPANIES = [
    ("Northwind Analytics", "SaaS analytics"), ("Helios Robotics", "Industrial robotics"),
    ("Brightpath Health", "Digital health"), ("Cobalt Freight", "Logistics"),
    ("Verdant Energy", "Renewable energy"),
]
# (company_idx, category, title, body, risk components)
EVENTS = [
    (0, "pricing_change", "Northwind cuts Pro tier price by 20%", "Northwind Analytics announced a 20% price reduction on its Pro plan effective next month.", (7, 8, 8, 8)),
    (0, "product_launch", "Northwind launches forecasting module", "Northwind Analytics released a forecasting module for enterprise customers.", (6, 5, 8, 7)),
    (0, "funding", "Northwind closes Series C", "Northwind Analytics reported closing a Series C funding round.", (6, 4, 6, 6)),
    (1, "partnership", "Helios partners with Cobalt Freight", "Helios Robotics and Cobalt Freight signed a warehouse automation partnership.", (6, 5, 7, 8)),
    (1, "product_launch", "Helios unveils HX-3 arm", "Helios Robotics unveiled the HX-3 robotic arm with a higher payload.", (7, 6, 7, 7)),
    (1, "leadership_change", "Helios names new CTO", "Helios Robotics appointed a new chief technology officer.", (4, 3, 5, 6)),
    (2, "regulatory_change", "Brightpath receives clearance", "Brightpath Health received regulatory clearance for its monitoring app.", (8, 6, 7, 8)),
    (2, "expansion", "Brightpath opens EU office", "Brightpath Health opened a new office to serve European clients.", (5, 4, 6, 7)),
    (2, "acquisition", "Brightpath acquires CareLoop", "Brightpath Health agreed to acquire the startup CareLoop.", (8, 7, 8, 7)),
    (3, "expansion", "Cobalt adds two regional hubs", "Cobalt Freight announced two new regional distribution hubs.", (5, 4, 5, 8)),
    (3, "pricing_change", "Cobalt raises fuel surcharge", "Cobalt Freight increased its fuel surcharge by 4 percent.", (4, 6, 4, 8)),
    (3, "other", "Cobalt publishes sustainability report", "Cobalt Freight published its annual sustainability report.", (2, 2, 3, 8)),
    (4, "funding", "Verdant secures project financing", "Verdant Energy secured financing for a new solar project.", (5, 4, 5, 7)),
    (4, "regulatory_change", "New subsidy rules affect Verdant", "A regional subsidy rule change may affect Verdant Energy project economics.", (7, 6, 6, 4)),
    (4, "partnership", "Verdant and Northwind sign data deal", "Verdant Energy contracted Northwind Analytics for grid analytics.", (5, 4, 6, 6)),
]
EXTRA_OBS = [  # 5 observations not tied to events (routine content)
    (0, "Northwind blog: customer story"), (1, "Helios careers page updated"),
    (2, "Brightpath newsletter issue"), (3, "Cobalt holiday schedule notice"),
    (4, "Verdant community update"),
]


def h(*parts: str) -> str:
    return hashlib.sha256("|".join(parts).encode()).hexdigest()


def seed(reset: bool = False) -> None:
    if reset:
        Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    with SessionLocal() as db:
        if db.scalar(select(Company).limit(1)):
            print("Database already contains data; use --reset to reseed.")
            return
        companies = [Company(name=n, industry=i, is_demo=True,
                             website=f"https://demo.invalid/{n.split()[0].lower()}",
                             description=f"FICTIONAL demo company ({i}).") for n, i in COMPANIES]
        db.add_all(companies)
        db.flush()
        sources = []
        for c in companies:
            for kind, label in (("demo", "Demo newsroom"), ("demo", "Demo blog")):
                sources.append(Source(company_id=c.id, kind=kind, label=label, is_demo=True,
                                      url=f"https://demo.invalid/{c.name.split()[0].lower()}/{label.split()[1].lower()}",
                                      last_status="ok", last_collected_at=BASE))
        db.add_all(sources)
        db.flush()
        for i, (ci, cat, title, body, comps) in enumerate(EVENTS):
            c, src = companies[ci], sources[ci * 2]
            obs = Observation(source_id=src.id, company_id=c.id, title=title, body=body,
                              url=f"{src.url}/post-{i}", content_hash=h(c.name, title, body),
                              published_at=BASE + timedelta(days=i), collected_at=BASE + timedelta(days=i, hours=1),
                              is_demo=True)
            db.add(obs)
            db.flush()
            ev = Event(company_id=c.id, title=title, category=cat, is_demo=True,
                       occurred_at=BASE + timedelta(days=i))
            db.add(ev)
            db.flush()
            db.add(Evidence(event_id=ev.id, observation_id=obs.id, excerpt=body[:120], verification_status="unverified"))
            r = score_risk(*comps)
            db.add(RiskAssessment(event_id=ev.id, impact=r.impact, urgency=r.urgency,
                                  strategic_relevance=r.strategic_relevance, evidence_quality=r.evidence_quality,
                                  overall_score=r.overall_score, priority=r.priority, explanation=r.explanation))
        for ci, title in EXTRA_OBS:
            c, src = companies[ci], sources[ci * 2 + 1]
            db.add(Observation(source_id=src.id, company_id=c.id, title=title, body="Routine demo content.",
                               url=f"{src.url}/{h(title)[:8]}", content_hash=h(c.name, title),
                               published_at=BASE, collected_at=BASE + timedelta(hours=2), is_demo=True))
        db.flush()
        rels = [(0, 1, "competitor"), (1, 3, "partner"), (2, 0, "customer"), (4, 0, "customer"), (3, 4, "supplier")]
        for a, b, t in rels:
            db.add(CompanyRelationship(company_id=companies[a].id, related_company_id=companies[b].id,
                                       relationship_type=t, verification_status="unverified"))
        # Placeholder sample reports; real generation arrives in stage 6.
        for t in ("daily", "weekly"):
            db.add(Report(report_type=t, title=f"Sample {t} report (DEMO)", is_demo=True,
                          content_json={"note": "Seeded placeholder, not generated by the report engine."},
                          content_markdown=f"# Sample {t} report\n\nSeeded DEMO placeholder; fictional data.\n",
                          created_at=BASE))
        wf1 = Workflow(name="Daily competitor digest (demo)", company_ids=[c.id for c in companies[:3]],
                       categories=["pricing_change", "product_launch"], min_priority="medium", report_type="daily")
        wf2 = Workflow(name="High-priority weekly (demo)", company_ids=[], categories=[],
                       min_priority="high", report_type="weekly", enabled=False)
        db.add_all([wf1, wf2])
        db.flush()
        s1 = DeliverySchedule(workflow_id=wf1.id, mode="daily", time_of_day="08:30", timezone="Asia/Kolkata")
        s2 = DeliverySchedule(workflow_id=wf2.id, mode="interval", interval_minutes=10080, timezone="UTC")
        db.add_all([s1, s2])
        db.flush()
        db.add(DeliveryRecipient(schedule_id=s1.id, channel="email", address="demo@example.invalid", authorized=True))
        db.add(UserSettings(timezone="Asia/Kolkata", display_name="Demo user", show_demo_data=True))
        db.commit()
        print("Seeded: 5 companies, 10 sources, 20 observations, 15 events (all FICTIONAL demo data).")


if __name__ == "__main__":
    seed(reset="--reset" in sys.argv)
