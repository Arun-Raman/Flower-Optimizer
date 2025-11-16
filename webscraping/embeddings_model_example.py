'''from sentence_transformers import SentenceTransformer, util
from matplotlib import colors

model = SentenceTransformer('all-MiniLM-L6-v2')  # lightweight & fast

# Example usage
text = "\"Sunflower Firewalker Medium\""
#all_colors = colors.get_named_colors_mapping()
colors_flat = ["red", "pink", "yellow", "white", "purple", "blue", "orange", "none"]
#colors_flat = [key for key in all_colors.keys()]

text_emb = model.encode(text, convert_to_tensor=True)
color_embs = model.encode(colors_flat, convert_to_tensor=True)

# Compare cosine similarity
cosine_scores = util.cos_sim(text_emb, color_embs)
best_color = colors_flat[cosine_scores.argmax()]

print("Predicted color:", best_color)'''

from transformers import pipeline
classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")

labels = ["red", "pink", "yellow", "white", "purple", "blue", "orange"]

results = []
results.append(classifier("Rose Fall Pack 40cm", labels))
results.append(classifier("Pom Bronze+Red CDN", labels))
results.append(classifier("Lily Fall Pack Hybrid Orange/Yellow 3/4", labels))
results.append(classifier("Mums Bronze+Red Spider / Cremon Combo", labels))
results.append(classifier("Sunflower Yellow Vincent Choice Select", labels))
results.append(classifier("POMPON DAISY ASSORTED 70CM", labels))
results.append(classifier("Lily L.A. Sweet Longwood Orange /Brown 3/5 Blooms", labels))
results.append(classifier("Sunflower Firewalker Medium", labels))

for r in results:
    color = r["labels"][0]
    print("score:", r["scores"][0])
    if r["scores"][0] < 0.5:
        print("no color listed")
    print("color:", color)
    print()
