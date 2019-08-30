import requests
from discord.ext import commands
import discord
import json
import datetime
import dateutil.parser

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36'}
husker_schedule = []
huskerbot_footer="Generated by HuskerBot"


class StatBot(commands.Cog, name="CFB Stats"):
    def __init__(self, bot):
        self.bot = bot

    # TODO Maybe have option to pick from various polls. Use reactions?
    @commands.command(aliases=["polls",])
    async def poll(self, ctx, year=2019, week=None, seasonType=None):
        """ Returns current Top 25 ranking from the Coach's Poll, AP Poll, and College Football Playoff ranking.
        Usage is: `$poll <year> <week>"""

        url = "https://api.collegefootballdata.com/rankings?year={}".format(year)

        if not seasonType:
            url = url + "&seasonType=regular"
        else:
            url = url + "&seasonType=postseason"

        if week:
            url = url + "&week={}".format(week)

        try:
            r = requests.get(url)
            poll_json = r.json()
        except:
            await ctx.send("An error occurred retrieving poll data.")
            return

        dump = True
        if dump:
            with open("cfb_polls.json", "w") as fp:
                json.dump(poll_json, fp, sort_keys=True, indent=4)
            fp.close()

        embed = discord.Embed(title="{} {} Season Week {} Poll".format(poll_json[0]['season'], str(poll_json[0]['seasonType']).capitalize(), poll_json[0]['week']), color=0xFF0000)

        ap_poll_raw = poll_json[0]['polls'][0]['ranks']
        last_rank = 1

        x = 0
        y = 0
        while x < len(ap_poll_raw):
            while y < len(ap_poll_raw):
                if ap_poll_raw[y]['rank'] == last_rank:
                    if ap_poll_raw[y]['firstPlaceVotes']:
                        embed.add_field(name="#{} {}".format(ap_poll_raw[y]['rank'], ap_poll_raw[y]['school']), value="{}\nPoints: {}\nFirst Place Votes: {}".format(ap_poll_raw[y]['conference'], ap_poll_raw[y]['points'], ap_poll_raw[y]['firstPlaceVotes']))
                    else:
                        embed.add_field(name="#{} {}".format(ap_poll_raw[y]['rank'], ap_poll_raw[y]['school']), value="{}\nPoints: {}".format(ap_poll_raw[y]['conference'], ap_poll_raw[y]['points']))
                    last_rank += 1
                    y = 0
                    break
                y += 1
            x += 1

        await ctx.send(embed=embed)

    # TODO Discord 2,000 char limit per message really limits this command. Need to make output more readable. Possibly add ability to filter by offense, defense, special teams, etc.
    @commands.command()
    async def roster(self, ctx, team="NEBRASKA", year=2019):
        """ Returns the current roster """
        await ctx.send("This command is under construction.")
        return

    @commands.command(aliases=["bs",])
    async def boxscore(self, ctx, year: int, week: int):
        """ Returns the box score of the searched for game. """

        if not type(year) is int:
            await ctx.send("You must enter a numerical year.")
            return
        elif year < 2004:
            await ctx.send("Data is not available prior to 2004.")
            return

        if not type(week) is int:
            await ctx.send("You must enter a numerical week.")
            return

        url = "https://api.collegefootballdata.com/games/teams?year={}&week={}&seasonType=regular&team=nebraska".format(year, week)

        try:
            r = requests.get(url)
            boxscore_json = r.json() # Actually imports a list
        except:
            await ctx.send("An error occurred retrieving boxscore data.")
            return

        if not boxscore_json:
            await ctx.send("This was a bye week. Try again.")
            return

        dump = False
        if dump:
            with open("boxscore_json.json", "w") as fp:
                json.dump(boxscore_json, fp, sort_keys=True, indent=4)
            fp.close()

        category_dict = {"rushingTDs": "Rushing TDs", "puntReturnYards": "Punt Return Yards", "puntReturnTDs": "Punt Return TDs", "puntReturns": "Punt Returns", "passingTDs": "Passing TDs",
                         "interceptionYards": "Interception Yards", "interceptionTDs": "Interception TDs", "passesIntercepted": "Passes Intercepted", "fumblesRecovered": "Fumbles Recovered",
                         "totalFumbles": "Total Fumbles", "tacklesForLoss": "Tackles For Loss", "defensiveTDs": "Defensive TDs", "tackles": "Tackles", "sacks": "Sacks", "qbHurries": "QB Hurries",
                         "passesDeflected": "Passes Defelcted", "possessionTime": "Possesion Time", "interceptions": "Interceptions", "fumblesLost": "Fumbles Lost", "turnovers": "Turnovers",
                         "totalPenaltiesYards": "Total Penalties Yards", "yardsPerRushAttempt": "Yards Per Rush Attempt", "rushingAttempts": "Rushing Attempts", "rushingYards": "Rushing Yards",
                         "yardsPerPass": "Yards Per Pass", "kickReturnYards": "Kick Return Yards", "kickReturnTDs": "Kick Return TDs", "kickReturns": "Kick Returns", "completionAttempts": "Completion Attempts",
                         "netPassingYards": "Net Passing Yards", "totalYards": "Total Yards", "fourthDownEff": "Fourth Down Eff", "thirdDownEff": "Third Down Eff", "firstDowns": "First Downs"}

        home_team = "({}) {}".format(boxscore_json[0]['teams'][0]['points'], boxscore_json[0]['teams'][0]['school'])
        away_team = "{} ({})\n".format(boxscore_json[0]['teams'][1]['school'], boxscore_json[0]['teams'][1]['points'])

        boxscore = "```\nBoxscore Stats for {} Week {}\n\n".format(year, week)
        boxscore += " " * (25 - len(home_team))
        boxscore += home_team
        boxscore += " " * 8
        boxscore += away_team
        boxscore += "-" * 50
        boxscore += "\n"

        i = 0

        while i < len(boxscore_json[0]['teams'][0]['stats']):
            boxscore += " " * (23 - len(category_dict[boxscore_json[0]['teams'][0]['stats'][i]['category']])) # Spaces
            boxscore += "{} ".format(category_dict[boxscore_json[0]['teams'][0]['stats'][i]['category']]) # Friendly category
            boxscore += "|" # Bar
            try:
                boxscore += "{}".format(boxscore_json[0]['teams'][0]['stats'][i]['stat']) # Home Stat
            except:
                pass
            boxscore += " " * (8 - len(boxscore_json[0]['teams'][0]['stats'][i]['stat'])) # Spaces
            boxscore += "|" # Bar
            try:
                boxscore += "{}\n".format(boxscore_json[0]['teams'][1]['stats'][i]['stat']) # Away Stat
            except:
                boxscore += "\n"
            i += 1

        boxscore = boxscore + "\n```"

        await ctx.send(boxscore)

    @commands.command(aliases=["sched",])
    async def schedule(self, ctx, year=2019):
        """ Returns the Nebraska Huskers football schedule. """

        edit_msg = await ctx.send("Loading...")

        url = "https://api.collegefootballdata.com/games?year={}&seasonType=regular&team=nebraska".format(year)
        try:
            r = requests.get(url)
            schedule_list = r.json() # Actually imports a list
        except:
            await ctx.send("An error occurred retrieving poll data.")
            return

        dump = False
        if dump:
            with open("husker_schedule.json", "w") as fp:
                json.dump(schedule_list, fp, sort_keys=True, indent=4)
            fp.close()

        embed = discord.Embed(title="{} Husker Schedule".format(year), color=0xFF0000)

        for game in schedule_list:
            game_start_datetime_raw = dateutil.parser.parse(game['start_date'])
            game_start_datetime_raw = game_start_datetime_raw + datetime.timedelta(hours=-5)

            # collegefootballdata.com puts TBD times as 23 or 0. ¯\_(ツ)_/¯
            if game_start_datetime_raw.hour == 23 or game_start_datetime_raw.hour == 0:
                game_info_str = "Week {}\n{}\n{}".format(game["week"], game["venue"], game_start_datetime_raw.strftime("%b %d, %Y TBD"))
            else:
                game_info_str = "Week {}\n{}\n{}".format(game["week"], game["venue"], game_start_datetime_raw.strftime("%b %d, %Y %H:%M %p"))

            home_team = ""
            home_split = []
            away_team = ""
            away_split = []
            name_len = 8

            # Abbreviate team names with two words in it.
            if " " in game["home_team"]:
                home_split = game["home_team"].split(" ")
                home_team = "{}. {}".format(home_split[0][0], home_split[1])
            else:
                home_team = game["home_team"]

            if " " in game["away_team"]:
                away_split = game["away_team"].split(" ")
                away_team = "{}. {}".format(away_split[0][0], away_split[1])
            else:
                away_team = game["away_team"]

            # Truncate the names if they are too long.
            if len(home_team) > name_len:
                home_team = "{}...".format(home_team[:name_len])

            if len(away_team) > name_len:
                away_team = "{}...".format(away_team[:name_len])

            # Add points next to names if they exist
            if game["home_points"]:
                embed.add_field(name="{} ({}) vs {} ({})".format(home_team, game["home_points"], away_team, game["away_points"]), value=game_info_str)
            # No points added
            else:
                embed.add_field(name="{} vs {}".format(home_team, away_team), value=game_info_str)

        embed.set_thumbnail(url="https://upload.wikimedia.org/wikipedia/commons/thumb/e/e5/Nebraska_Cornhuskers_logo.svg/1200px-Nebraska_Cornhuskers_logo.svg.png")
        await edit_msg.edit(content="", embed=embed)


def setup(bot):
    bot.add_cog(StatBot(bot))