DIFFICULTY_DATA = {
    "beginner": {
        "id": 1,
        "name": "Beginner",
        "subtitle": "Easy questions",
    },
    "intermediate": {
        "id": 2,
        "name": "Intermediate",
        "subtitle": "Moderate questions",
    },
    "chemist": {
        "id": 3,
        "name": "Chemist",
        "subtitle": "Hard questions",
    },
    "albert einstein": {
        "id": 4,
        "name": "Albert Einstein",
        "subtitle": "Hardest questions.",
    }
}

DIFFICULTIES = [
    {
        "id": difficulty["id"],
        "name": difficulty["name"],
        "subtitle": difficulty["subtitle"],
    }
    for difficulty in DIFFICULTY_DATA.values()
]