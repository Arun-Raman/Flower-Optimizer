import spacy
import numpy as np

nlp = spacy.load("en_core_web_lg")

colors = ["Red", "White", "Blue", "Green", "Yellow", "Orange", "Brown"]
colors_lower = [c.lower() for c in colors]
color_vecs = {c: nlp(c).vector for c in colors}

texts = [
    "Rose RED 60X"
]

for text in texts:
    doc = nlp(text)
    best_token, best_color, best_sim = None, None, -1

    for token in doc:
        token_lower = token.text.lower()

        # # Exact match
        # if token_lower in colors_lower:
        #     best_token = token.text
        #     best_color = token.text.capitalize()
        #     best_sim = 1.0
        #     break

        # Vector similarity
        if token.has_vector:
            for color, vec in color_vecs.items():
                sim = token.vector.dot(vec) / (np.linalg.norm(token.vector) * np.linalg.norm(vec))
                if sim > best_sim:
                    best_sim = sim
                    best_token = token.text
                    best_color = color

    print(f"Text: {text}")
    if best_token:
        print(f"  Most similar token: {best_token} → {best_color} (sim={best_sim:.2f})")
    else:
        print("  No matching token found.")
    print()
