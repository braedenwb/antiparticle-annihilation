MAP_WAVE_DATA = {
    "tutorial": {
        "waves": {
            1: ["down_antiquark", "down_antiquark"],
            2: ["down_antiquark", "down_antiquark", "down_antiquark"],
            3: ["down_antiquark", "down_antiquark", "down_antiquark", "down_antiquark"],
            4: ["up_antiquark", "up_antiquark"],
            5: ["down_antiquark", "down_antiquark", "down_antiquark", "down_antiquark", "down_antiquark", "down_antiquark", "down_antiquark", "down_antiquark", "down_antiquark", "down_antiquark", "down_antiquark", "down_antiquark"],
            6: ["top_antiquark"]
        }
    },
    "map1": {
        "waves": {
            # formatting:
            # "down_antiquark"
            # {"type": "antiparticle_name", "count": 1, "interval": 0.5, "delay": 1.0, "lane": "first"}
            1: [
                {"type": "down_antiquark", "count": 2}
            ],
            2: [
                {"type": "down_antiquark", "count": 2},
                {"type": "up_antiquark", "delay": 1.5}
            ],
            3: [
                {"type": "up_antiquark", "delay": 0.0},
                {"type": "down_antiquark", "delay": 0.75},
                {"type": "up_antiquark", "delay": 1.5}
            ],
            4: [
                {"type": "up_antiquark", "count": 2},
                {"type": "positron", "delay": 1.5}
            ],
            5: [
                {"type": "positron", "count": 4, "interval": 0.35}
            ],
            6: [
                {"type": "top_antiquark"}
            ],
            7: [
                {"type": "up_antiquark", "count": 8, "interval": 0.25}
            ],
            8: [
                {"type": "bottom_antiquark", "count": 2, "interval": 0.75}
            ],
            9: [
                {"type": "positron", "count": 4, "interval": 0.25},
                {"type": "up_antiquark", "count": 4, "delay": 1.25, "interval": 0.25},
                {"type": "bottom_antiquark", "delay": 2.5}
            ],
            10: [
                {"type": "top_antiquark", "count": 4, "interval": 0.6}
            ],
        }
    }
}
