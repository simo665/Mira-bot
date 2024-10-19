import discord
from discord.ext import commands, tasks
import random
import asyncio

class Tetris(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.board = []
        self.num_of_rows = 18
        self.num_of_cols = 10
        self.empty_square = ':black_large_square:'
        self.colors = {
            "I": ':blue_square:',
            "O": ':yellow_square:',
            "T": ':purple_square:',
            "J": ':brown_square:',
            "L": ':orange_square:',
            "S": ':green_square:',
            "Z": ':red_square:'
        }
        self.current_piece = None
        self.current_position = (0, 4)
        self.current_rotation = 0
        self.points = 0
        self.channel = None
        self.message = None
        self.game_over = False
        self.tetris_task = None

        self.shapes = self.get_shapes()
        self.make_empty_board()

    def make_empty_board(self):
        self.board = [[self.empty_square for _ in range(self.num_of_cols)] for _ in range(self.num_of_rows)]

    def get_shapes(self):
        return {
            "I": [
                [[1, 0], [1, 1], [1, 2], [1, 3]],
                [[0, 2], [1, 2], [2, 2], [3, 2]],
            ],
            "O": [
                [[0, 1], [0, 2], [1, 1], [1, 2]]
            ],
            "T": [
                [[0, 1], [1, 0], [1, 1], [1, 2]],
                [[0, 1], [1, 1], [1, 2], [2, 1]],
                [[1, 0], [1, 1], [1, 2], [2, 1]],
                [[0, 1], [1, 0], [1, 1], [2, 1]],
            ],
            # Add shapes for J, L, S, Z similarly
        }

    def format_board(self):
        board_str = ""
        for row in self.board:
            board_str += "".join(row) + "\n"
        return board_str

    def can_move(self, shape, position):
        for block in shape:
            row = block[0] + position[0]
            col = block[1] + position[1]
            if row < 0 or row >= self.num_of_rows or col < 0 or col >= self.num_of_cols:
                return False
            if self.board[row][col] != self.empty_square:
                return False
        return True

    def add_piece_to_board(self, shape, position, piece_color):
        for block in shape:
            row = block[0] + position[0]
            col = block[1] + position[1]
            self.board[row][col] = self.colors[piece_color]

    def remove_piece_from_board(self, shape, position):
        for block in shape:
            row = block[0] + position[0]
            col = block[1] + position[1]
            self.board[row][col] = self.empty_square

    def clear_lines(self):
        full_rows = [i for i, row in enumerate(self.board) if all(square != self.empty_square for square in row)]
        for row in full_rows:
            del self.board[row]
            self.board.insert(0, [self.empty_square for _ in range(self.num_of_cols)])
        self.points += len(full_rows)

    async def run_game(self):
        self.game_over = False
        self.current_piece = random.choice(list(self.shapes.keys()))
        self.current_rotation = 0
        self.current_position = (0, 4)

        while not self.game_over:
            shape = self.shapes[self.current_piece][self.current_rotation]
            if self.can_move(shape, self.current_position):
                self.add_piece_to_board(shape, self.current_position, self.current_piece)
                embed = discord.Embed(title="Tetris", description=self.format_board(), color=0x077ff7)
                await self.message.edit(embed=embed)
                await asyncio.sleep(1)
                self.remove_piece_from_board(shape, self.current_position)
                self.current_position = (self.current_position[0] + 1, self.current_position[1])
            else:
                self.add_piece_to_board(shape, (self.current_position[0] - 1, self.current_position[1]), self.current_piece)
                self.clear_lines()
                self.current_piece = random.choice(list(self.shapes.keys()))
                self.current_rotation = 0
                self.current_position = (0, 4)
                if not self.can_move(self.shapes[self.current_piece][self.current_rotation], self.current_position):
                    self.game_over = True
                    await self.channel.send("Game Over!")
                    break

@commands.command(name="tstart")
    async def start_tetris(self, ctx):
        """Starts a game of Tetris."""
        self.channel = ctx.channel
        self.make_empty_board()
        embed = discord.Embed(title="Tetris", description=self.format_board(), color=0x077ff7)
        self.message = await ctx.send(embed=embed)
        if self.tetris_task:
            self.tetris_task.cancel()
        self.tetris_task = asyncio.create_task(self.run_game())

    @commands.command(name="rotate")
    async def rotate(self, ctx):
        """Rotates the current piece."""
        if self.game_over:
            await ctx.send("The game is over! Start a new one with `!start_tetris`.")
            return

        shape = self.shapes[self.current_piece][self.current_rotation]
        self.remove_piece_from_board(shape, self.current_position)
        self.current_rotation = (self.current_rotation + 1) % len(self.shapes[self.current_piece])
        shape = self.shapes[self.current_piece][self.current_rotation]
        if not self.can_move(shape, self.current_position):
            self.current_rotation = (self.current_rotation - 1) % len(self.shapes[self.current_piece])
        self.add_piece_to_board(shape, self.current_position, self.current_piece)

    @commands.command(name="move")
    async def move(self, ctx, direction: str):
        """Move the piece left, right, or down."""
        if self.game_over:
            await ctx.send("The game is over! Start a new one with `!start_tetris`.")
            return

        shape = self.shapes[self.current_piece][self.current_rotation]
        self.remove_piece_from_board(shape, self.current_position)

        if direction.lower() == "left":
            new_position = (self.current_position[0], self.current_position[1] - 1)
        elif direction.lower() == "right":
            new_position = (self.current_position[0], self.current_position[1] + 1)
        elif direction.lower() == "down":
            new_position = (self.current_position[0] + 1, self.current_position[1])
        else:
            await ctx.send("Invalid direction! Use 'left', 'right', or 'down'.")
            return

        if self.can_move(shape, new_position):
            self.current_position = new_position
        self.add_piece_to_board(shape, self.current_position, self.current_piece)

    @commands.command(name="stop_tetris")
    async def stop_tetris(self, ctx):
        """Stops the Tetris game."""
        if self.tetris_task:
            self.tetris_task.cancel()
            self.tetris_task = None
            self.game_over = True
            await ctx.send("Tetris game stopped.")
        else:
            await ctx.send("No game is currently running.")

async def setup(bot):
    await bot.add_cog(Tetris(bot))