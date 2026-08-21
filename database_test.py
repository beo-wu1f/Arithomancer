from database import create_table, save_score, get_high_scores

print("DATABASE TEST STARTED")

# Create the database table
create_table()

print("✓ High-score table ready")

# Test saving a score
save_score("Rishi", 42)

print("✓ Score saved")

# Test retrieving scores
scores = get_high_scores()

print("\n🏆 HIGH SCORES")
print("-" * 45)

for position, score in enumerate(scores, start=1):

    player, questions, played_date = score

    print(
        f"{position:<4}"
        f"{player:<12}"
        f"{questions:<20}"
        f"{played_date}"
    )

print("-" * 45)
print(f"✓ {len(scores)} scores stored")