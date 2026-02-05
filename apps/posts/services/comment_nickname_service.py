import random


# 댓글에 특화된 랜덤 닉네임 생성 함수
def generate_comment_nickname() -> str:
    adjectives = ["행복한", "용감한", "재빠른", "조용한", "똑똑한"]
    animals = ["고양이", "강아지", "토끼", "여우", "곰"]
    return f"{random.choice(adjectives)} {random.choice(animals)}"
