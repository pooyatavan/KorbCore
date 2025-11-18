import math
import random

# ----------------------------
# Color class
# ----------------------------
class Color:
    def __init__(self, r, g, b):
        self.set(r, g, b)

    def __str__(self):
        return f"rgb({round(self.r)}, {round(self.g)}, {round(self.b)})"

    def set(self, r, g, b):
        self.r = self.clamp(r)
        self.g = self.clamp(g)
        self.b = self.clamp(b)

    def clamp(self, value):
        return max(0, min(255, value))

    # ----------------------------
    # Color transforms
    # ----------------------------
    def hue_rotate(self, angle=0):
        angle = angle / 180 * math.pi
        sin = math.sin(angle)
        cos = math.cos(angle)

        self.multiply([
            0.213 + cos * 0.787 - sin * 0.213,
            0.715 - cos * 0.715 - sin * 0.715,
            0.072 - cos * 0.072 + sin * 0.928,
            0.213 - cos * 0.213 + sin * 0.143,
            0.715 + cos * 0.285 + sin * 0.140,
            0.072 - cos * 0.072 - sin * 0.283,
            0.213 - cos * 0.213 - sin * 0.787,
            0.715 - cos * 0.715 + sin * 0.715,
            0.072 + cos * 0.928 + sin * 0.072
        ])

    def grayscale(self, value=1):
        self.multiply([
            0.2126 + 0.7874 * (1 - value),
            0.7152 - 0.7152 * (1 - value),
            0.0722 - 0.0722 * (1 - value),
            0.2126 - 0.2126 * (1 - value),
            0.7152 + 0.2848 * (1 - value),
            0.0722 - 0.0722 * (1 - value),
            0.2126 - 0.2126 * (1 - value),
            0.7152 - 0.7152 * (1 - value),
            0.0722 + 0.9278 * (1 - value)
        ])

    def sepia(self, value=1):
        self.multiply([
            0.393 + 0.607 * (1 - value),
            0.769 - 0.769 * (1 - value),
            0.189 - 0.189 * (1 - value),
            0.349 - 0.349 * (1 - value),
            0.686 + 0.314 * (1 - value),
            0.168 - 0.168 * (1 - value),
            0.272 - 0.272 * (1 - value),
            0.534 - 0.534 * (1 - value),
            0.131 + 0.869 * (1 - value)
        ])

    def saturate(self, value=1):
        self.multiply([
            0.213 + 0.787 * value,
            0.715 - 0.715 * value,
            0.072 - 0.072 * value,
            0.213 - 0.213 * value,
            0.715 + 0.285 * value,
            0.072 - 0.072 * value,
            0.213 - 0.213 * value,
            0.715 - 0.715 * value,
            0.072 + 0.928 * value
        ])

    def multiply(self, m):
        r = self.clamp(self.r * m[0] + self.g * m[1] + self.b * m[2])
        g = self.clamp(self.r * m[3] + self.g * m[4] + self.b * m[5])
        b = self.clamp(self.r * m[6] + self.g * m[7] + self.b * m[8])
        self.r, self.g, self.b = r, g, b

    def brightness(self, value=1):
        self.linear(value)

    def contrast(self, value=1):
        self.linear(value, -(0.5 * value) + 0.5)

    def linear(self, slope=1, intercept=0):
        self.r = self.clamp(self.r * slope + intercept * 255)
        self.g = self.clamp(self.g * slope + intercept * 255)
        self.b = self.clamp(self.b * slope + intercept * 255)

    def invert(self, value=1):
        self.r = self.clamp((value + self.r / 255 * (1 - 2 * value)) * 255)
        self.g = self.clamp((value + self.g / 255 * (1 - 2 * value)) * 255)
        self.b = self.clamp((value + self.b / 255 * (1 - 2 * value)) * 255)

    # ----------------------------
    # RGB → HSL conversion
    # ----------------------------
    def hsl(self):
        r = self.r / 255
        g = self.g / 255
        b = self.b / 255

        mx = max(r, g, b)
        mn = min(r, g, b)
        l = (mx + mn) / 2

        if mx == mn:
            return {"h": 0, "s": 0, "l": l * 100}

        d = mx - mn
        s = d / (2 - mx - mn) if l > 0.5 else d / (mx + mn)

        if mx == r:
            h = ((g - b) / d + (6 if g < b else 0)) / 6
        elif mx == g:
            h = ((b - r) / d + 2) / 6
        else:
            h = ((r - g) / d + 4) / 6

        return {"h": h * 100, "s": s * 100, "l": l * 100}

# ----------------------------
# Solver class
# ----------------------------
class Solver:
    def __init__(self, target: Color):
        self.target = target
        self.target_hsl = target.hsl()
        self.reused_color = Color(0, 0, 0)

    # Main call
    def solve(self):
        w = self.solve_wide()
        n = self.solve_narrow(w)
        return {
            "values": n["values"],
            "loss": n["loss"],
            "filter": self.css(n["values"])
        }

    # Wide search
    def solve_wide(self):
        A = 5
        c = 15
        a = [60, 180, 18000, 600, 1.2, 1.2]

        best = {"loss": float("inf")}

        for _ in range(3):
            initial = [50, 20, 3750, 50, 100, 100]
            result = self.spsa(A, a, c, initial, 1000)
            if result["loss"] < best["loss"]:
                best = result

        return best

    # Narrow search
    def solve_narrow(self, wide):
        A = wide["loss"]
        A1 = A + 1
        a = [
            0.25 * A1,
            0.25 * A1,
            A1,
            0.25 * A1,
            0.2 * A1,
            0.2 * A1
        ]
        return self.spsa(A, a, 2, wide["values"], 500)

    # SPSA optimizer
    def spsa(self, A, a, c, values, iters):
        alpha = 1
        gamma = 1 / 6

        best_values = None
        best_loss = float("inf")

        for k in range(iters):
            ck = c / ((k + 1) ** gamma)

            deltas = [(1 if random.random() > 0.5 else -1) for _ in range(6)]
            high = [values[i] + ck * deltas[i] for i in range(6)]
            low = [values[i] - ck * deltas[i] for i in range(6)]

            loss_diff = self.loss(high) - self.loss(low)

            for i in range(6):
                g = loss_diff / (2 * ck) * deltas[i]
                ak = a[i] / ((A + k + 1) ** alpha)
                values[i] = self.fix(values[i] - ak * g, i)

            current_loss = self.loss(values)
            if current_loss < best_loss:
                best_loss = current_loss
                best_values = values[:]

        return {"values": best_values, "loss": best_loss}

    # Fix value limits
    def fix(self, value, idx):
        limits = [100, 100, 7500, 100, 200, 200]

        if idx == 3:  # hue-rotate
            value %= limits[idx]
        else:
            value = max(0, min(limits[idx], value))

        return value

    # Loss computation
    def loss(self, filters):
        c = self.reused_color
        c.set(0, 0, 0)

        c.invert(filters[0] / 100)
        c.sepia(filters[1] / 100)
        c.saturate(filters[2] / 100)
        c.hue_rotate(filters[3] * 3.6)
        c.brightness(filters[4] / 100)
        c.contrast(filters[5] / 100)

        hsl = c.hsl()

        return (
            abs(c.r - self.target.r) +
            abs(c.g - self.target.g) +
            abs(c.b - self.target.b) +
            abs(hsl["h"] - self.target_hsl["h"]) +
            abs(hsl["s"] - self.target_hsl["s"]) +
            abs(hsl["l"] - self.target_hsl["l"])
        )

    # Convert values to CSS filter string
    def css(self, f):
        return (
            f"filter: invert({round(f[0])}%) "
            f"sepia({round(f[1])}%) "
            f"saturate({round(f[2])}%) "
            f"hue-rotate({round(f[3] * 3.6)}deg) "
            f"brightness({round(f[4])}%) "
            f"contrast({round(f[5])}%);"
        )

# ----------------------------
# Helper function
# ----------------------------
def hex_to_rgb(hexcode):
    hexcode = hexcode.lstrip("#")
    if len(hexcode) == 3:
        hexcode = "".join([c * 2 for c in hexcode])
    return tuple(int(hexcode[i:i+2], 16) for i in (0, 2, 4))


print(hex_to_rgb("#ff8800"))