from discord import Embed, Color
from discord.ext.commands import command, Cog, BucketType, cooldown
from lib.checks import general, lang, minigames
from random import choice
from asyncio import sleep

COMMAND = "slots"


class Slots(Cog):
    COLUMNS = 3

    def __init__(self, bot):
        self.bot = bot

    @staticmethod
    def create_row(emotes):
        return " | ".join(emote["emote"] for emote in emotes)

    def create_embed(self, ctx, emotes, currency, bet, outcome="", color=Color.blue()):
        if outcome != "":
            outcome = f"--- {outcome} ---"

        embed = Embed(description=f"{self.create_row(emotes)}\n{outcome}", color=color)
        embed.add_field(name="Bet" if outcome == "" else "Outcome", value=f"{currency}{bet}", inline=True)
        embed.set_author(name=COMMAND.title(), icon_url=f"{ctx.author.avatar_url}")
        embed.set_footer(text=self.bot.FOOTER)
        return embed

    @command(name="slots", aliases=["slot-machine"])
    @cooldown(2, 3600, BucketType.user)
    async def slots(self, ctx, bet: int):
        if general.check_status(ctx.guild.id, COMMAND):
            err_msg = minigames.general_checks(ctx.guild.id, ctx.author.id, bet, COMMAND)

            if err_msg is not None:
                await ctx.send(lang.get_message(ctx.language, err_msg))
                return

            slot_symbols = [{"emote": "💯", "multiplier": 1.5},
                            {"emote": "💰", "multiplier": 2},
                            {"emote": "💵", "multiplier": 3},
                            {"emote": "💎", "multiplier": 4},
                            {"emote": "🥇", "multiplier": 3.5}]
            spinning_emote = {"emote": "<a:slots:867113561436061706>", "multiplier": 1}
            emotes = [spinning_emote for x in range(self.COLUMNS)]
            currency = general.get_currency(ctx.guild.id)
            message = await ctx.send(embed=self.create_embed(ctx, emotes, currency, bet))

            column = 0
            while column < self.COLUMNS:
                await sleep(1.5)
                emotes[column] = choice(slot_symbols)
                await message.edit(embed=self.create_embed(ctx, emotes, currency, bet))
                column += 1

            if True if emotes[0] == emotes[1] == emotes[2] else False:
                outcome = lang.get_message(ctx.language, 'MINIGAMES_UserWon')
                color = Color.green()
                money = int(bet * emotes[0]['multiplier'])
                general.add_money(ctx.guild.id, ctx.author.id, money-bet)
            else:
                outcome = lang.get_message(ctx.language, 'MINIGAMES_UserLost')
                color = Color.red()
                money = bet
                general.remove_money(ctx.guild.id, ctx.author.id, money)
            await message.edit(embed=self.create_embed(ctx, emotes, currency, bet, outcome, color))
        else:
            ctx.command.reset_cooldown(ctx)

    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up(COMMAND.title())


def setup(bot):
    bot.add_cog(Slots(bot))
