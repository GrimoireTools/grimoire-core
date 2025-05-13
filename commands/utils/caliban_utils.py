from nextcord import Interaction, Embed, Color


async def send_caliban_message(
    interaction: Interaction,
    message: str | None,
) -> None:
    if not message:
        return

    embed = Embed(description=f"`{message}`", color=Color.greyple())
    embed.set_author(
        name="??????",
    )
    embed.set_thumbnail(
        url="https://i.imgur.com/ODo4nUl.png",
    )
    await interaction.followup.send(embed=embed, ephemeral=True, delete_after=5)
