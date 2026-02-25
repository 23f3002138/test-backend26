"""Seed the database with sample Connaissance events."""

from app import app
from models import db, Event


def seed():
    with app.app_context():
        if Event.query.count() > 0:
            print("Database already seeded.")
            return

        events = [
            Event(
                name="RoboWars",
                description="Build and battle robots in an electrifying arena combat. Teams design autonomous or remote-controlled bots to outsmart and overpower opponents.",
                date="2026-03-15",
                rules="1. Team of max 4 members\\n2. Robot weight limit: 8kg\\n3. No flame/chemical weapons\\n4. Match duration: 3 minutes",
                eligibility="Open to all engineering students",
                image_url="https://images.unsplash.com/photo-1485827404703-89b55fcc595e?w=600",
            ),
            Event(
                name="CAD Clash",
                description="Showcase your 3D modeling skills in a timed CAD challenge. Participants recreate complex mechanical assemblies using SolidWorks or Fusion 360.",
                date="2026-03-15",
                rules="1. Individual event\\n2. Software: SolidWorks / Fusion 360\\n3. Time limit: 90 minutes\\n4. Models judged on accuracy & creativity",
                eligibility="Mechanical & related branches",
                image_url="https://images.unsplash.com/photo-1581092160607-ee22621dd758?w=600",
            ),
            Event(
                name="Bridge Builder",
                description="Design and construct a bridge using popsicle sticks and glue. The bridge that withstands the maximum load wins!",
                date="2026-03-16",
                rules="1. Team of 2–3 members\\n2. Materials provided on-site\\n3. Bridge span: 30cm minimum\\n4. Judged on load-to-weight ratio",
                eligibility="Open to all branches",
                image_url="https://images.unsplash.com/photo-1545296664-39db56ad95bd?w=600",
            ),
            Event(
                name="Tech Quiz",
                description="Test your technical knowledge across engineering domains — mechanics, thermodynamics, coding, and general science.",
                date="2026-03-16",
                rules="1. Team of 2 members\\n2. Three rounds: MCQ, rapid fire, buzzer\\n3. No electronic devices allowed",
                eligibility="Open to all",
                image_url="https://images.unsplash.com/photo-1606326608606-aa0b62935f2b?w=600",
            ),
            Event(
                name="Paper Presentation",
                description="Present your research or innovative idea in front of a panel of judges. Topics span across all engineering and technology domains.",
                date="2026-03-17",
                rules="1. Team of 1–3 members\\n2. Presentation: 10 mins + 5 mins Q&A\\n3. PPT format required\\n4. Abstract submission mandatory",
                eligibility="UG and PG students",
                image_url="https://images.unsplash.com/photo-1531482615713-2afd69097998?w=600",
            ),
            Event(
                name="Drone Racing",
                description="Pilot your drone through an obstacle course at high speed. Precision and speed determine the winner in this thrilling race.",
                date="2026-03-17",
                rules="1. Individual or team of 2\\n2. Drone weight < 2kg\\n3. FPV or line-of-sight allowed\\n4. Course must be completed in one attempt",
                eligibility="Open to all engineering students",
                image_url="https://images.unsplash.com/photo-1508614589041-895b88991e3e?w=600",
            ),
        ]

        db.session.add_all(events)
        db.session.commit()
        print(f"Seeded {len(events)} events successfully!")


if __name__ == "__main__":
    seed()
