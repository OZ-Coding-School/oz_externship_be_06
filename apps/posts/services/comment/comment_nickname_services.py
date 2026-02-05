import random


def generate_comment_nickname() -> str:
    # 댓글 닉네임을 랜덤으로 생성하는 함수입니다. 형용사와 동물 이름을 조합합니다.
    adjectives = ["행복한", "용감한", "재빠른", "조용한", "똘똘한"]
    animals = ["고양이", "강아지", "토끼", "여우", "곰"]
    return f"{random.choice(adjectives)} {random.choice(animals)}"
