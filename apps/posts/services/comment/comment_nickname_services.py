import random


def generate_comment_nickname() -> str:
    adjectives = ["행복한", "용감한", "재빠른", "조용한", "똘똘한"]
    animals = ["고양이", "강아지", "토끼", "여우", "곰"]
    random_number = random.randint(1000, 9999)
    return f"{random.choice(adjectives)} {random.choice(animals)}{random_number}"
