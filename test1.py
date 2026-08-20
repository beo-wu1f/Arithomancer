import random


def generate_question(question_number):

    min_number = round(1 + question_number * 0.20)
    max_number = round(5 + question_number * 0.30)

    factor = random.randint(min_number, max_number)
    multiplier = random.randint(min_number, max_number)

    answer = factor * multiplier

    return factor, multiplier, answer

for question_number in range(1, 51):

    factor, multiplier = generate_question(question_number)

    print(
        f"Q{question_number:02}  "
        f"{factor} × {multiplier} = {factor * multiplier}"
    )