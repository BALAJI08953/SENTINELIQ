"""Generate SYNTHETIC labeled training data (template-based, deterministic).

Output: sample_data/training_examples.csv. Every row has synthetic=true.
Template data is far easier than real news; metrics on it say nothing about real-world accuracy.
"""
import csv
import random
from pathlib import Path

COMPANIES = ["Zenith Corp", "Orbit Labs", "Pinecrest Ltd", "Atlas Dynamics", "Lumen Systems", "Fjord AI"]
TEMPLATES = {
    "pricing_change": ["{c} cuts subscription prices by {n} percent", "{c} raises the cost of its premium plan",
        "{c} introduces a new pricing tier and discounts for annual plans", "{c} increases fees for enterprise customers",
        "{c} slashes list prices to attract new buyers", "{c} announces revised pricing and a free trial"],
    "product_launch": ["{c} launches a new analytics product for enterprises", "{c} unveils its next generation platform",
        "{c} releases version {n} with new features", "{c} introduces a mobile app for customers",
        "{c} rolls out a new product line this quarter", "{c} debuts an AI assistant feature"],
    "partnership": ["{c} signs a strategic partnership with a logistics provider", "{c} and a cloud vendor announce a joint venture",
        "{c} enters a collaboration agreement with a university", "{c} teams up with a retailer on a co-marketing deal",
        "{c} forms an alliance to integrate products", "{c} announces a reseller partnership"],
    "funding": ["{c} raises ${n} million in a Series B round", "{c} secures new investment from venture capital firms",
        "{c} closes a funding round led by investors", "{c} completes an initial public offering",
        "{c} obtains a ${n} million credit facility", "{c} announces seed financing"],
    "leadership_change": ["{c} appoints a new chief executive officer", "{c} chief financial officer steps down",
        "{c} names a new head of engineering", "{c} founder resigns from the board",
        "{c} hires a veteran executive as president", "{c} announces CEO succession plan"],
    "regulatory_change": ["Regulators fine {c} over data privacy violations", "{c} receives regulatory approval for its service",
        "New compliance rules force {c} to change operations", "{c} faces an antitrust investigation",
        "{c} responds to new government regulation", "{c} granted a license by the financial authority"],
    "acquisition": ["{c} acquires a smaller rival for ${n} million", "{c} agrees to be acquired by a larger company",
        "{c} completes the purchase of a software startup", "{c} announces a merger with a competitor",
        "{c} buys a majority stake in a supplier", "{c} divests a business unit in a sale"],
    "expansion": ["{c} opens a new office in Europe", "{c} expands operations into the Asian market",
        "{c} builds a new manufacturing facility", "{c} launches services in {n} new cities",
        "{c} adds regional distribution hubs", "{c} hires {n} employees as it grows its footprint"],
    "other": ["{c} publishes its annual sustainability report", "{c} sponsors a local community event",
        "{c} employees volunteer at a charity drive", "{c} wins an industry workplace award",
        "{c} updates its website design", "{c} hosts a customer appreciation day"],
}


def main(per_class: int = 24, seed: int = 7) -> None:
    rng = random.Random(seed)
    rows = []
    for label, temps in TEMPLATES.items():
        for i in range(per_class):
            text = temps[i % len(temps)].format(c=rng.choice(COMPANIES), n=rng.randint(2, 90))
            rows.append((text, label, "true"))
    rng.shuffle(rows)
    out = Path(__file__).resolve().parents[2] / "sample_data" / "training_examples.csv"
    with out.open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["text", "label", "synthetic"])
        w.writerows(rows)
    print(f"wrote {len(rows)} SYNTHETIC rows to {out}")


if __name__ == "__main__":
    main()
