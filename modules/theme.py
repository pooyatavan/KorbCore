from pathlib import Path
from PIL import Image

from modules.tools import GetProjectRoot
from modules.log import LOG
from modules.strings import Console


def GetLocation():
    return str(Path(__file__).resolve().parent.parent) + "\\static\\css\\style.css"

def ChangePNGoverlay(color):
    png_files = list(Path(GetProjectRoot() + "\\static\\img\\msg").glob("*.png"))
    for file in png_files:
        img = Image.open(file).convert("RGBA")
        r, g, b, a = img.split()
        colored = Image.new("RGBA", img.size, color)
        cr, cg, cb, _ = colored.split()
        result = Image.merge("RGBA", (cr, cg, cb, a))
        result.save(file)

def ChangeCSS(line, newcolor, username):
    csspath = GetLocation()
    with open(csspath, "r") as css:
        lines = css.readlines()
        if line == 6:
            lines[line] = f"--highlight: {newcolor};\n"
        if line == 7:
            lines[line] = f"--highlight-hover: {newcolor};\n"
        if line == 9:
            lines[line] = f"--background: {newcolor};\n"
    with open(csspath, "w") as css:
        css.writelines(lines)
        css.close()
    ChangePNGoverlay(newcolor)
    LOG.debug(Console.Theme.value.format(username=username))
    
def GetColors(line):
    csspath = GetLocation()
    with open(csspath, "r") as css:
        lines = css.readlines()
        css.close()
    if line == 6:
        return lines[line].replace("--highlight: ", "").replace(";", "")[0:7]
    if line == 7:
        return lines[line].replace("--highlight-hover: ", "").replace(";", "")[0:7]
    if line == 9:
        return lines[line].replace("--background: ", "").replace(";", "")[0:7]