import requests
import pathlib
import datetime
from typing import List

root = pathlib.Path(__file__).parent.resolve()

class XPHolder:

    def __init__(self, xps, new_xps):
        self.xps = xps
        self.new_xps = new_xps
    
    def __lt__(self, value):
        return self.xps < value.xps
    
    def __le__(self, value):
        return self.xps <= value.xps
    
    def __gt__(self, value):
        return self.xps > value.xps
    
    def __ge__(self, value):
        return self.xps >= value.xps

class Machine(XPHolder):

    def __init__(self, name, xps, new_xps):
        super().__init__(xps, new_xps)
        self.name = name
    
    def __str__(self):
        return f"<Machine {self.name} with {self.xps} XP>"

class Language(XPHolder):

    def __init__(self, name, xps, new_xps):
        super().__init__(xps, new_xps)
        self.name = name
    
    def __str__(self):
        return f"<Language {self.name} with {self.xps} XP>"

class Date:

    def __init__(self, date, xp):
        self.date = datetime.datetime.strptime(date, "%Y-%m-%d")
        self.xp = xp
    
    def __str__(self):
        return f"<Date {self.date} with {self.xp} XP>"

class User:

    def __init__(self, user, total_xp, new_xp, machines, languages, dates):
        self.user = user
        self.total_xp = total_xp
        self.new_xp = new_xp

        self.machines = sorted([
            Machine(k, v['xps'], v['new_xps']) for k, v in machines.items()
        ], key=lambda item: item.xps, reverse=True)
        self.languages = sorted([
            Language(k, v['xps'], v['new_xps']) for k, v in languages.items()
        ], key=lambda item: item.xps, reverse=True)
        self.dates = sorted([Date(k, v) for k, v in dates.items()], key=lambda item: item.xp, reverse=True)
    
    def __str__(self):
        return f"<User {self.user} with {self.total_xp} XP>"

def get_levels():
    levels_response = requests.get("https://codestats.net/api/users/cozyGalvinism").json()
    me = User(levels_response['user'], levels_response['total_xp'], levels_response['new_xp'], levels_response['machines'], levels_response['languages'], levels_response['dates'])
    return me

def human_format(num):
    num = float('{:.3g}'.format(num))
    magnitude = 0
    while abs(num) >= 1000:
        magnitude += 1
        num /= 1000.0
    return '{}{}'.format('{:f}'.format(num).rstrip('0').rstrip('.'), ['', 'k', 'M', 'B', 'T', 'P'][magnitude])

def generate_language_line(language: Language):
    line = f"| {language.name} | {human_format(language.xps)} | {human_format(language.new_xps)} |"
    return line

def generate_md_table(languages: List[Language]):
    header = """| Language | Total XP | XP gained (last 12 hours) |\n| --- | --- | --- |"""
    body = "\n".join(list(map(generate_language_line, languages)))
    return f"""{header}
{body}"""

if __name__ == "__main__":
    readme = root / "README.md"
    me = get_levels()
    top_languages = me.languages[:10]
    md_lang_table = generate_md_table(top_languages)

    readme_complete = f"""### cozy's coding space
*But not as cozy as you think*

I've been coding for a little over 17 years, using various languages! See below, a list with my current top {len(top_languages)} used languages, powered by Code::Stats :3
    
{md_lang_table}
    
My profile page will probably become a bit prettier in the future, once I have proper ideas on what I can actually do with this ;D"""
    with open(readme, 'w') as f:
        f.write(readme_complete)