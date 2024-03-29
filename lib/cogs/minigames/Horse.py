from asyncio import sleep
from random import randint

from discord import Embed, Color
from discord.ext.commands import command, Cog, BucketType, cooldown

from lib.checks import general, minigames

COMMAND = "horse"


class Horse(Cog):
    MAX_HORSES = 5
    LENGTH_TRACK = 7

    def __init__(self, bot):
        self.bot = bot

    def create_racetrack(self, horses):
        racetrack = ""
        number = 1
        for horse in horses:
            racetrack += f"**{number}.** {'-' * (self.LENGTH_TRACK - horse)}:horse_racing:\n"
            number += 1
        return racetrack

    def create_embed(self, ctx, horses, desc="", color=Color.blue()):
        embed = Embed(description=f"{self.create_racetrack(horses)}\n{desc}", color=color)
        embed.set_author(name=COMMAND.title(), icon_url=f"{ctx.author.avatar_url}")
        embed.set_footer(text=self.bot.FOOTER)
        return embed

    @command(name="horse", aliases=["horse-race"])
    @cooldown(4, 3600, BucketType.user)
    async def horse(self, ctx, bet: int, horse: int):
        """
        Bet on a horse and hope it wins the race!
        /Examples/ `horse 500 1`\n`horse 500 5`
        """
        err_msg = minigames.general_checks(ctx.guild.id, ctx.author.id, bet)

        if err_msg is not None:
            await ctx.send(err_msg)
            return

        if self.MAX_HORSES >= horse >= 1:
            general.remove_money(ctx.guild.id, ctx.author.id, bet)
        else:
            await ctx.send("You have to give a valid number between %s and %s." % (1, self.MAX_HORSES))
            return

        horses = [0 for x in range(self.MAX_HORSES)]
        message = await ctx.send(embed=self.create_embed(ctx, horses))

        while self.LENGTH_TRACK not in horses:
            await sleep(1.2)
            horse_ = randint(1, self.MAX_HORSES)
            horses[horse_ - 1] += 1

            if horses[horse_ - 1] != self.LENGTH_TRACK:
                horse_ = randint(1, self.MAX_HORSES)
                horses[horse_ - 1] += 1

            await message.edit(embed=self.create_embed(ctx, horses))

        currency = general.get_currency(ctx.guild.id)

        horse_number = 1
        winning_horse = 0
        for horse_ in horses:
            if horse_ == self.LENGTH_TRACK:
                winning_horse = horse_number
                break
            horse_number += 1

        if winning_horse == horse:
            general.add_money(ctx.guild.id, ctx.author.id, int(bet * 2.5))
            desc = f"You Won {currency}{int(bet * 2.5)}"
            color = Color.green()
        else:
            desc = f"You Lost {currency}{bet}"
            color = Color.red()
        await message.edit(embed=self.create_embed(ctx, horses, desc, color))

    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up(COMMAND.title())


def setup(bot):
    bot.add_cog(Horse(bot))
