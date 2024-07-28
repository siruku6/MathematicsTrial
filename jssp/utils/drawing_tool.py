import random


# # 20色のカラー
# colors = [
#     "red", "blue", "skyblue", "gray", "purple",
#     "green", "cyan", "darkblue", "orange", "black",
#     "pink", "salmon", "mistyrose", "tomato", "greenyellow",
#     "lightseagreen", "aquamarine", "aliceblue", "palegreen", "lemonchiffon"
# ]
def create_colors(num: int) -> list[str]:
    """
    https://stackoverflow.com/questions/55965633/how-to-specify-additional-colors-in-plotly-gantt-chart
    """

    def rnd() -> int:
        return random.randint(0, 255)

    # r = lambda: random.randint(0, 255)

    colors = ["#%02X%02X%02X" % (rnd(), rnd(), rnd())]
    for i in range(1, num):
        colors.append("#%02X%02X%02X" % (rnd(), rnd(), rnd()))
    return colors
