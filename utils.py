import base64


def get_base64_image(image_path):
    with open(image_path, "rb") as f:
        encoded = base64.b64encode(f.read()).decode()
    return f"data:image/png;base64,{encoded}"


def lighten_hex_color(hex_color, percentage):
    hex_color = hex_color.lstrip("#")
    r, g, b = int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)
    r, g, b = (
        int(r + (255 - r) * percentage),
        int(g + (255 - g) * percentage),
        int(b + (255 - b) * percentage),
    )
    r, g, b = min(255, int(r)), min(255, int(g)), min(255, int(b))

    return "#{:02x}{:02x}{:02x}".format(r, g, b)


def getStartingXI(df, team, deal_with_first_half_subs=True):
    startingXI = list(
        set(player for player in df[df["team"] == team]["player"] if player is not None)
        - set(df[(df["type"] == "SubstitutionOn") & (df["team"] == team)]["player"])
    )
    assert len(startingXI) == 11

    if deal_with_first_half_subs:
        sub_on = list(
            df[
                (df["type"] == "SubstitutionOn")
                & (df["team"] == team)
                & (df["minute"] < 45)
            ]["player"]
        )
        sub_off = list(
            df[
                (df["type"] == "SubstitutionOff")
                & (df["team"] == team)
                & (df["minute"] < 45)
            ]["player"]
        )
        startingXI += sub_on
        startingXI = [player for player in startingXI if player not in sub_off]

    return startingXI
