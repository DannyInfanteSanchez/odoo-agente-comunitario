import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.odoo_client import odoo_client

def test():
    print("Connecting to Odoo...")
    try:
        # Traer los departamentos (state_id is None, province_id is None)
        records = odoo_client.search_read(
            model="res.country.state",
            domain=[
                ("country_id.code", "=", "PE"),
                ("state_id", "=", False),
                ("province_id", "=", False)
            ],
            fields=["id", "name", "code"],
            limit=100
        )
        print(f"Total PE departments: {len(records)}")
        for r in sorted(records, key=lambda x: x['name']):
            print(f"ID: {r['id']} | Name: {r['name']} | Code: {r['code']}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test()
