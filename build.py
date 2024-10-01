import matplotlib.pyplot as plt
import requests
import pathlib
import datetime
from typing import List
import math

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

        self.machines = sorted(
            [Machine(k, v["xps"], v["new_xps"]) for k, v in machines.items()],
            key=lambda item: item.xps,
            reverse=True,
        )
        self.languages = sorted(
            [Language(k, v["xps"], v["new_xps"]) for k, v in languages.items()],
            key=lambda item: item.xps,
            reverse=True,
        )
        self.dates = sorted(
            [Date(k, v) for k, v in dates.items()],
            key=lambda item: item.xp,
            reverse=True,
        )

    def __str__(self):
        return f"<User {self.user} with {self.total_xp} XP>"


def get_levels():
    levels_response = requests.get(
        "https://codestats.net/api/users/cozyGalvinism"
    ).json()
    me = User(
        levels_response["user"],
        levels_response["total_xp"],
        levels_response["new_xp"],
        levels_response["machines"],
        levels_response["languages"],
        levels_response["dates"],
    )
    return me


def to_level(xp):
    LEVEL_FACTOR = 0.025
    return int(math.floor(LEVEL_FACTOR * math.sqrt(xp)))


def human_format(num):
    num = float("{:.3g}".format(num))
    magnitude = 0
    while abs(num) >= 1000:
        magnitude += 1
        num /= 1000.0
    return "{}{}".format(
        "{:f}".format(num).rstrip("0").rstrip("."),
        ["", "k", "M", "B", "T", "P"][magnitude],
    )


def generate_language_line(language: Language):
    line = f"| {language.name} | {to_level(language.xps)} | {human_format(language.xps)} | {human_format(language.new_xps)} |"
    return line


def generate_md_table(languages: List[Language]):
    header = """| Language | Level | Total XP | XP gained (last 12 hours) |\n| --- | --- | --- | --- |"""
    body = "\n".join(list(map(generate_language_line, languages)))
    return f"""{header}
{body}"""


def plot_language_xp(languages):
    names = [lang.name for lang in languages]
    xps = [lang.xps for lang in languages]

    plt.figure(figsize=(10, 6))

    # Muted color scheme using a grayish tone to match GitHub's style
    bar_color = '#2dba4e'
    
    plt.barh(names, xps, color=bar_color)

    # Setting font sizes and colors to match a minimalist style
    plt.xlabel("XP", fontsize=12, fontweight='light', color='#777')
    plt.title("Top Languages by XP", fontsize=14, fontweight='light', color='#777')

    # Invert y-axis to have the highest XP at the top
    plt.gca().invert_yaxis()

    # Remove the grid, and reduce axis line visibility
    plt.grid(False)
    plt.gca().spines['top'].set_visible(False)
    plt.gca().spines['right'].set_visible(False)
    plt.gca().spines['left'].set_color('#777')
    plt.gca().spines['bottom'].set_color('#777')

    # Format the tick labels to show human-readable XP values
    plt.xticks(ticks=plt.gca().get_xticks(), labels=[human_format(x) for x in plt.gca().get_xticks()], fontsize=10, color='#777')
    plt.yticks(fontsize=10, color='#777')

    plt.tight_layout()

    # Save the figure with a transparent background to blend with GitHub
    plt.savefig('language_xp_chart.png', transparent=True)
    plt.close()

def plot_new_xp_distribution(languages, min_xp=500):
    names = [lang.name for lang in languages]
    new_xps = [lang.new_xps for lang in languages]

    # Group small XP contributions
    grouped_names = []
    grouped_xps = []
    other_xp = 0

    for i in range(len(new_xps)):
        if new_xps[i] >= min_xp:  # Group smaller slices into "Others"
            grouped_names.append(names[i])
            grouped_xps.append(new_xps[i])
        else:
            other_xp += new_xps[i]

    if other_xp > 0:
        grouped_names.append("Others")
        grouped_xps.append(other_xp)

    plt.figure(figsize=(8, 8))

    # Light color palette with soft colors
    colors = ['#ff9999', '#66b3ff', '#99ff99', '#ffcc99', '#c2c2f0', '#ffb3e6', '#c4e17f']

    plt.pie(grouped_xps, labels=grouped_names, autopct='%1.1f%%', startangle=140,
            colors=colors[:len(grouped_names)], wedgeprops={'linewidth': 1, 'edgecolor': 'white'}, 
            pctdistance=0.85, textprops={'color': '#777'})

    plt.title('XP Gained in Last 12 Hours', fontsize=14, fontweight='light', color='#777')
    plt.tight_layout()

    # Save the figure with a transparent background
    plt.savefig('new_xp_pie_chart.png', transparent=True)
    plt.close()

if __name__ == "__main__":
    readme = root / "README.md"
    me = get_levels()
    top_languages = me.languages[:10]
    years = datetime.date.today().year - 2004

    plot_language_xp(top_languages)
    plot_new_xp_distribution(top_languages, 100)

    readme_complete = f"""# Hi there, I'm cozy! 👋

[![wakatime](https://wakatime.com/badge/user/c0ba07bb-3421-41be-bd1a-d611e670f250.svg)](https://wakatime.com/@c0ba07bb-3421-41be-bd1a-d611e670f250)

I've been coding for a little over {years} years, using various languages! See below, a few diagrams with my current top {len(top_languages)} used languages, powered by Code::Stats!

![Language XP](language_xp_chart.png)
![New XP Distribution](new_xp_pie_chart.png)
"""
    with open(readme, "w") as f:
        f.write(readme_complete)
