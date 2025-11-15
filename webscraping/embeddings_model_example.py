from sentence_transformers import SentenceTransformer, util
from matplotlib import colors

model = SentenceTransformer('all-MiniLM-L6-v2')  # lightweight & fast

# Example usage
all_colors = colors.get_named_colors_mapping()
text = "text = The color mentioned in this product title: \"Lilies Oriental cappucino 3/5 BL QB\""
#colors = ["red", "pink", "yellow", "white", "purple", "blue", "orange"]
colors_flat = [key for key in all_colors.keys()]

text_emb = model.encode(text, convert_to_tensor=True)
color_embs = model.encode(colors_flat, convert_to_tensor=True)

# Compare cosine similarity
cosine_scores = util.cos_sim(text_emb, color_embs)
best_color = colors_flat[cosine_scores.argmax()]

print("Predicted color:", best_color)
