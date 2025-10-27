import json
import re
import itertools

def parse_flower_data(json_string, flower_type):
    data = json.loads(json_string)
    datalist = []

    if "products" not in data or "result" not in data["products"]:
        print("Unexpected JSON structure.")
        return datalist

    for listingWrapper in data["products"]["result"]:
        listing = list(listingWrapper.values())[0]  # unwrap the single-key map
        info = listing.get("info", {})
        delivery = listing.get("delivery", [{}])[0]  # take the first delivery option if available

        vendor = info.get("vendor", "Unknown Farm")
        name = info.get("name", "").strip()
        qty = delivery.get("qty_per_box", info.get("qty_per_box", 0))
        price_str = delivery.get("perboxprice", "$0").replace("$", "")
        try:
            cost = round(float(price_str), 2)
        except ValueError:
            cost = 0.0

        color = info.get("color", "Unknown").capitalize()
        if color == "Unknown":
            base_colors = ["Red", "Pink", "White", "Yellow", "Orange", "Purple", "Blue", "Green",
            "Cream", "Peach", "Coral", "Lavender", "Magenta", "Violet",
            "Burgundy", "Maroon", "Gold", "Silver", "Black", "Brown", "Burgundy"]

            # optional
            modifiers = ["Light", "Dark", "Hot", "Soft", "Pale", "Deep", "Bright", "Pastel", "Creamy"]

            # modifiers combined with base colors
            compound_colors = [f"{m} {c}" for m, c in itertools.product(modifiers, base_colors)]

            colors = base_colors + compound_colors + [
                # common special descriptors
                "Mixed", "Bi Color", "Two Tone", "Multi Color", "Variegated",
                "Blush", "Ivory", "Champagne", "Apricot", "Salmon", "Mauve",
                "Lilac", "Plum", "Wine", "Bronze", "Copper", "Dusty Rose",
                "Fuchsia", "Teal", "Mint", "Sky Blue", "Navy Blue",
                "Tangerine", "Canary Yellow", "Lemon Yellow", "Mustard",
                "Rust", "Terracotta", "Creamy White", "Off White", "Snow White"]
            
            pattern = r"\b(" + "|".join(colors) + r")\b"
            match = re.findall(pattern, name, re.IGNORECASE)
            if match:
                color = [m for m in match]

        '''flower_type = "Unknown"
        for t in ["Rose", "Lily", "Tulip", "Daisy", "Sunflower", "Orchid", "Carnation", "Chrysanthemum"]:
            if t.lower() in name.lower():
                flower_type = t
                break'''

        stem_length = info.get("length", 0)
        if isinstance(stem_length, str) and stem_length.isdigit():
            stem_length = int(stem_length)
        if not isinstance(stem_length, int) or stem_length == 0:
            match = re.search(r"\d+", name)
            if match:
                stem_length = int(match.group())
            else:
                stem_length = 0

        cutoff = delivery.get("cutoff_time", "00:00:00")
        try:
            h, m, s = [int(x) for x in cutoff.split(":")]
            shipping_time = h + m / 60
        except Exception:
            shipping_time = 0

        identifier = f"{vendor} {name}"

        datalist.append({
            "Identifier": identifier,
            "Cost": cost,
            "Type": flower_type,
            "Color": color,
            "Number of Flowers per Package": qty,
            "Stem Length": stem_length,
            "Shipping Time (Hours)": shipping_time
        })

    return datalist
