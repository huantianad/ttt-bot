import discord
from discord.ext import commands

emoji_dict = {
    u"\u2196": 0,
    u"\u2B06": 1,
    u"\u2197": 2,
    u"\u2B05": 3,
    u"\u23FA": 4,
    u"\u27A1": 5,
    u"\u2199": 6,
    u"\u2B07": 7,
    u"\u2198": 8
}

bot = commands.Bot(command_prefix="!")
color = discord.Color.blue()  # Change this color to read from the config later.


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}!")


def make_grid_internals(grid):
    """Converts the normal grid list into human-readable version."""
    # Replace all values in the grid list with emojis
    new_grid = [":white_large_square:" if (not x)
                else ":regional_indicator_x:" if x == 1
                else ":o2:" if x == 2
                else "?"
                for x in grid]

    # Adds a new line every three emojis.
    return "\n".join("".join(new_grid[i:i + 3]) for i in range(0, len(new_grid), 3))


async def draw_grid(channel, grid, player1, player2, current_player):
    """Draws the initial grid of the game."""
    grid = make_grid_internals(grid)

    current_player = player1 if current_player == 1 else player2
    description = f"{player1.mention} vs. {player2.mention}\n{current_player.mention}'s turn!"

    embed = discord.Embed(title="Tic-Tac-Toe!", description=description, color=color)
    embed.add_field(name="Grid", value=grid)

    return await channel.send(embed=embed)


async def edit_grid(message, grid, player1, player2, current_player):
    grid = make_grid_internals(grid)

    current_player = player1 if current_player == 1 else player2
    description = f"{player1.mention} vs. {player2.mention}\n{current_player.mention}'s turn!"

    embed = discord.Embed(title="Tic-Tac-Toe!", description=description, color=color)
    embed.add_field(name="Grid", value=grid)

    await message.edit(embed=embed)


async def edit_grid_end(message, grid, player1, player2, current_player, end_message):
    grid = make_grid_internals(grid)

    current_player = player1 if current_player == 1 else player2
    description = f"{player1.mention} vs. {player2.mention}\n{end_message}"

    embed = discord.Embed(title="Tic-Tac-Toe!", description=description, color=color)
    embed.add_field(name="Grid", value=grid)

    await message.edit(embed=embed)


def win_indexes(n):
    # Rows
    for r in range(n):
        yield [(r, c) for c in range(n)]
    # Columns
    for c in range(n):
        yield [(r, c) for r in range(n)]
    # Diagonal top left to bottom right
    yield [(i, i) for i in range(n)]
    # Diagonal top right to bottom left
    yield [(i, n - 1 - i) for i in range(n)]


def is_winner(board, decorator):
    n = len(board)
    for indexes in win_indexes(n):
        if all(board[r][c] == decorator for r, c in indexes):
            return True
    return False


def check_for_end(grid):
    if 0 not in grid:
        return "draw"
    elif is_winner([grid[i:i + 3] for i in range(0, len(grid), 3)], 1):
        return 1
    elif is_winner([grid[i:i + 3] for i in range(0, len(grid), 3)], 2):
        return 2
    else:
        return


@bot.command()
async def ttt(ctx, player2: commands.MemberConverter):
    """Starts a Tic-Tac-Toe game with the specified player!"""
    player1 = ctx.author
    current_player = 1
    running = True
    used_emojis = []

    # Makes sure that the player isn't a bot.
    if player2.bot:
        await ctx.send("You can't play against a bot!")
        return

    # Creates and sends the initial grid
    grid = [0 for x in range(9)]
    message = await draw_grid(ctx.channel, grid, player1, player2, current_player)

    # Adds all the emojis to make moves
    for emoji in emoji_dict:
        await message.add_reaction(emoji)

    # Running loop, continuously checks for new inputs until someone wins
    while running:
        # Makes a usable object based on current player
        current_player_object = player1 if current_player == 1 else player2

        def check(r, u):
            # Checks that it is a valid emoji, that the emoji wasn't used before, and that it is the current player
            return (r.emoji in emoji_dict) and (r.emoji not in used_emojis) and (u == current_player_object)

        # Waits for a reaction, edits grid and used emojis accordingly
        reaction, user = await bot.wait_for("reaction_add", check=check)
        grid[emoji_dict[reaction.emoji]] = 1 if current_player == 1 else 2 if current_player == 2 else "??"
        used_emojis.append(reaction.emoji)

        end = check_for_end(grid)
        if end == "draw":
            await edit_grid_end(message, grid, player1, player2, current_player, "It's a draw!")
            running = False
        elif end == 1:
            await edit_grid_end(message, grid, player1, player2, current_player, f"{player1.mention} has won!")
            running = False
        elif end == 2:
            await edit_grid_end(message, grid, player1, player2, current_player, f"{player2.mention} has won!")
            running = False
        else:
            # Switch current player to next player
            current_player = 2 if current_player == 1 else 1

            # Update grid with new information
            await edit_grid(message, grid, player1, player2, current_player)


bot.run("PUT BOT TOKEN HERE")
