def ChangeCSS(old, new):
    with open('style.css') as mycss:
        mylist = mycss.readlines()
        for a, b in enumerate(mylist):
            if b.find("font") == 2:
                print(b)