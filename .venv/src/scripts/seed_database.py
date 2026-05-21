"""Seed the Supabase database with mock pharmacies and users from data/ JSON files."""

import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from backend.database.connection import get_supabase_client

_DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")


def seed_pharmacies(client) -> None:
    with open(os.path.join(_DATA_DIR, "mock_pharmacies.json"), encoding="utf-8") as f:
        pharmacies = json.load(f)

    for pharmacy in pharmacies:
        row = {k: v for k, v in pharmacy.items() if k not in ("is_garde", "garde_horaires")}
        client.table("pharmacies").upsert(row).execute()

        horaires = pharmacy.get("garde_horaires")
        if pharmacy.get("is_garde") and horaires:
            client.table("garde_calendar").upsert({
                "pharmacy_id": pharmacy["id"],
                "date": horaires["date"],
                "heure_debut": horaires["debut"],
                "heure_fin": horaires["fin"],
            }).execute()

    print(f"Seeded {len(pharmacies)} pharmacies.")


def seed_users(client) -> None:
    with open(os.path.join(_DATA_DIR, "mock_users.json"), encoding="utf-8") as f:
        users = json.load(f)

    for user in users:
        medications = user.pop("medicaments", [])
        client.table("users").upsert(user).execute()

        for med in medications:
            client.table("medications").upsert({
                "user_id": user["id"],
                "name": med["nom"],
                "dosage": med.get("dosage"),
                "stock_quantity": med.get("stock_restant", 0),
                "stock_unit": med.get("unite", "comprime"),
            }).execute()

    print(f"Seeded {len(users)} users.")


def main() -> None:
    client = get_supabase_client()
    seed_pharmacies(client)
    seed_users(client)
    print("Database seeded successfully.")


if __name__ == "__main__":
    main()
