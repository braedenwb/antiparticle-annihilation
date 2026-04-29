GUIDE_SEQUENCE = ["welcome", "base", "elements", "antiparticles", "waves", "silicon", "begin_game", "compounding"]

GUIDES = {
    "welcome": {
        "title": "Welcome!",
        "description": "Welcome to Antiparticle Annihilation! Your goal is to use elements to defend the base from the antiparticles, which will travel down the white path and annihilate all in their way.",
        "image_group": None,
        "image_key": None,
    },
    "base": {
        "title": "Base",
        "description": "The base is at the end of the path. Your goal is to prevent antiparticles from reaching it.",
        "image_group": "tiles",
        "image_key": "base",
    },
    "elements": {
        "title": "Elements",
        "description": "Use elements as defenses against antiparticles. Elements are designed to be as related to their real world function as possible. The left side of the screen has all the elements and their stats available to you.",
        "image_group": None,
        "image_key": None,
    },
    "antiparticles": {
        "title": "Antiparticles",
        "description": "Antiparticles will travel down the white path and try to annihilate anything in their way. Design creative defenses with your elements to prevent them from reaching and destroying the base.",
        "image_group": None,
        "image_key": None,
    },
    "waves": {
        "title": "Waves",
        "description": "Press Start Wave to spawn antiparticles. There are 6 waves, each with progressing difficulty and ending with a boss antiparticle. Waves will automatically start after the first one within 10 second intervals",
        "image_group": "antiparticles",
        "image_key": "top_antiquark",
    },
    "silicon": {
        "title": "Silicon",
        "description": "In the real world silicon is a important material used in electronics. Inspired by this, it is used in the game for generating energy which is important for buying more elements.",
        "image_group": "elements",
        "image_key": "silicon",
    },
    "begin_game": {
        "title": "Buy an element",
        "description": "On the left side of the screen, click an element icon and buy it to build your defenses. The semi-transparent circle around the element shows the range. Its recommended to have the white path in the range so the element attacks antiparticles.",
        "image_group": None,
        "image_key": None,
    },
    "compounding": {
        "title": "Compounding",
        "description": "Some elements can bond together into compounds with new stats and behaviour. H2O, water, can be formed by placing a level 2 Hydrogen next to a level 1 Oxygen. This transforms the two elements into one compound.",
        "image_group": None,
        "image_key": None,
    }
}
