from pathlib import Path

def GetLocation():
    return str(Path(__file__).resolve().parent.parent) + "\\static\\css\\style.css"

def ChangeCSS(line, newcolor):
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