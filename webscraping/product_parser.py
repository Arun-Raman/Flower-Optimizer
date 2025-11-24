import colorsys
import re
from datetime import datetime

import numpy as np
import spacy

from matplotlib import colors


# Initialize module-level constants once
COLORS_CATEGORIZED = {'red': [], 'orange': [], 'yellow': [], 'green': [], 'blue': [], 'purple': [], 'pink': [], 'white': [], 'other': []}
all_colors = colors.get_named_colors_mapping()
for name, val in all_colors.items():
    r, g, b = colors.to_rgb(val)
    h, s, v = colorsys.rgb_to_hsv(r, g, b)

    if s < 0.2 and v > 0.8:
        COLORS_CATEGORIZED['white'].append(name)
    if 0.0 <= h < 0.05:
        COLORS_CATEGORIZED['red'].append(name)
    elif 0.05 <= h < 0.15:
        COLORS_CATEGORIZED['orange'].append(name)
    elif 0.15 <= h < 0.25:
        COLORS_CATEGORIZED['yellow'].append(name)
    elif 0.25 <= h < 0.45:
        COLORS_CATEGORIZED['green'].append(name)
    elif 0.45 <= h < 0.65:
        COLORS_CATEGORIZED['blue'].append(name)
    elif 0.65 <= h < 0.85:
        COLORS_CATEGORIZED['purple'].append(name)
    elif 0.85 <= h < 1.0:
        COLORS_CATEGORIZED['pink'].append(name)
    else:
        COLORS_CATEGORIZED['other'].append(name)

flat_colors = []
for cat, color_list in COLORS_CATEGORIZED.items():
    flat_colors.append(cat)
    for c in color_list:
        flat_colors.append(c)

pattern = r'\b(' + '|'.join(re.escape(c) for c in flat_colors) + r')\b'
COLOR_REGEX = re.compile(pattern, re.IGNORECASE)

SPACY_NLP = spacy.load("en_core_web_lg")
FLOWER_COLORS = ["red", "white", "blue", "green", "yellow", "orange", "purple", "pink"]
FLOWER_COLOR_VECS = {c: SPACY_NLP(c).vector for c in FLOWER_COLORS}

class ProductParser:
    def parse_products(self, data: list) -> list[dict]:
        print("Parsing Product")
        
        return [self._parse_product(listing) for listing in data]

    def _parse_product(self, listing):
        info = listing.get("info", {})
        name = str(info.get("name", "").strip())

        color_cat = 'placeholder'
        color = info.get("color", "Unknown").capitalize()
        color_listed = True

        texts = [] # for embeddings model


        if "sunf" in name.lower(): # sunflowers are yellow
            if color == "Unknown":
                color_listed = False
                color = color_cat = "yellow"
        else: # the 3 capital letters are from Tavolo Farms color naming convention
            if "coral" in name.lower() or "peach" in name.lower() or "COR" in name or "PCH" in name or "PKB" in name or "PKL" in name or "PKM" in name:
                color_listed = False
                color = color_cat = "pink"
            elif "CRM" in name or "IVO" in name or "SAN" in name or "WHT" in name:
                color_listed = False
                color = color_cat = "white"
            elif "GRN" in name:
                color_listed = False
                color = color_cat = "green"
            elif "LAV" in name:
                color_listed = False
                color = color_cat = "purple"
            elif "ORG" in name:
                color_listed = False
                color = color_cat = "orange"
            elif "YLW" in name:
                color_listed = False
                color = color_cat = "yellow"
            else:
                match = COLOR_REGEX.search(name.lower())
                if match:
                    if color == 'Unknown':
                        color = match.group(1)
                        color_listed = False
                    for cat, color_list in COLORS_CATEGORIZED.items():
                        if color in color_list:
                            color_cat = cat
                else: # use embeddings model
                    c_found = False
                    for c in FLOWER_COLORS:
                        if c in name:
                            color = color_cat = name
                            c_found = True
                            break
                    if not c_found:
                        texts.append(name)

        for text in texts:
            doc = SPACY_NLP(text)
            best_token, best_color, best_sim = None, None, -1
            for token in doc:
                if token.has_vector:
                    for c, vec in FLOWER_COLOR_VECS.items():
                        sim = token.vector.dot(vec) / (np.linalg.norm(token.vector) * np.linalg.norm(vec))
                        if sim > best_sim:
                            best_sim = sim
                            best_token = token.text
                            best_color = c

            if best_token and best_sim > 0.5:
                color = color_cat = best_color

        if color in FLOWER_COLORS:
            color_cat = color

        stem_length = info.get("length", 0)
        if isinstance(stem_length, str) and stem_length.isdigit():
            stem_length = int(stem_length)
        if not isinstance(stem_length, int) or stem_length == 0:
            match = re.search(r"\d+", name)
            if match:
                stem_length = int(match.group())
            else:
                stem_length = 0

        shipping_date = datetime.strptime(listing["delivery"][0]["delivery_date"], "%d-%b-%Y")
        now = datetime.now()
        shipping_time_hours = (shipping_date - now).total_seconds() / 3600

        entry = {
            "Identifier": listing["info"]["name"],
            "Cost": float(listing["delivery"][0]["perboxprice"].replace("$", "")),
            "Type": listing["category"],
            "Color": color,
            "Color Category": color_cat,
            "Color Listed": color_listed,
            "Number of Flowers per Package": listing["delivery"][0]["qty_per_box"],
            "Stem Length": stem_length,
            "Shipping Time (Hours)": shipping_time_hours,
        }

        return entry