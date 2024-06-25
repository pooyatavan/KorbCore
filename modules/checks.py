from modules.ConfigReader import Config

def Check(ForCheck):
    if bool(Config.read()['core'][ForCheck]) == " True":
        return True
    else:
        return False