import discord
from discord.ext import commands
import random
import asyncio

class TetrisGame(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.board = []
        self.num_of_rows = 18
        self.num_of_cols = 10
        self.empty_square = ':black_large_square:'
        self.colors = {
            "blue": ':blue_square:',
            "brown": ':brown_square:',
            "orange": ':orange_square:',
            "yellow": ':yellow_square:',
            "green": ':green_square:',
            "purple": ':purple_square:',
            "red": ':red_square:'
        }
        self.embed_colour = 0x077ff7  # Colour of line on embeds
        self.points = 0
        self.lines = 0
        self.down_pressed = False
        self.rotate_clockwise = False
        self.rotation_pos = 0
        self.h_movement = 0
        self.is_new_shape = False
        self.start_higher = False
        self.game_over = False
        self.index = 0
        self.current_message = None

        self.make_empty_board()

    def make_empty_board(self):
        self.board = [[self.empty_square for _ in range(self.num_of_cols)] for _ in range(self.num_of_rows)]

    def format_board_as_str(self):
        board_as_str = ''
        for row in self.board:
            board_as_str += ''.join(row) + "\n"
        return board_as_str

    def get_random_shape(self):
        shapes = [
            [[0, 3], [0, 4], [0, 5], [0, 6]],  # Example shape
            # Add more shapes based on the original code
        ]
        random_shape = random.choice(shapes)
        return random_shape

    async def reset_game(self):
        self.make_empty_board()
        self.down_pressed = False
        self.rotate_clockwise = False
        self.rotation_pos = 0
        self.h_movement = 0
        self.is_new_shape = False
        self.start_higher = False
        self.game_over = False
        self.points = 0
        self.lines = 0

    async def run_game(self, ctx, msg, cur_shape):
        self.is_new_shape = True
        while not self.game_over:
            await asyncio.sleep(1)  # Update the interval as needed
            # Update game logic here
            embed = discord.Embed(description=self.format_board_as_str(), color=self.embed_colour)
            await msg.edit(embed=embed)
            self.is_new_shape = False

    @commands.command()
    async def start_tetris(self, ctx):
        """Start a Tetris game."""
        await self.reset_game()
        embed = discord.Embed(
            title="Tetris in Discord",
            description=self.format_board_as_str(),
            color=self.embed_colour
        )
        embed.add_field(
            name="How to Play:",
            value="Use ⬅ ⬇ ➡ to move left, down, and right respectively. \n🔃 to rotate.",
            inline=False
        )
        self.current_message = await ctx.send(embed=embed)
        await self.current_message.add_reaction("▶")

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        if user == self.bot.user:
            return
        if str(reaction.emoji) == "▶" and reaction.message == self.current_message:
            await self.reset_game()
            await reaction.message.clear_reactions()
            await reaction.message.add_reaction("⬅")
            await reaction.message.add_reaction("⬇")
            await reaction.message.add_reaction("➡")
            await reaction.message.add_reaction("🔃")
            starting_shape = self.get_random_shape()
            await self.run_game(None, reaction.message, starting_shape)

async def setup(bot):
    await bot.add_cog(TetrisGame(bot))