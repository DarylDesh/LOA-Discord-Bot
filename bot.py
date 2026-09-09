import os
import logging

import discord
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")
GUILD_ID = int(os.getenv("GUILD_ID", "0"))
FORUM_CHANNEL_ID = int(os.getenv("FORUM_CHANNEL_ID", "0"))
REVIEWER_ROLE_ID = int(os.getenv("REVIEWER_ROLE_ID", "0"))

STATUS_TAGS = {
    "pending": os.getenv("TAG_PENDING", "Pending"),
    "approved": os.getenv("TAG_APPROVED", "Approved"),
    "extended": os.getenv("TAG_EXTENDED", "Extended"),
    "denied": os.getenv("TAG_DENIED", "Denied"),
    "returned": os.getenv("TAG_RETURNED", "Returned"),
}

REVIEW_MESSAGE = os.getenv(
    "REVIEW_MESSAGE",
    "🚨 **New Leave of Absence Request**\n"
    "<@&{role_id}>, a new LOA request has been submitted.\n"
    "Please review the information above and use the buttons below to update the request status."
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s"
)
log = logging.getLogger("loa-bot")

intents = discord.Intents.default()
intents.guilds = True


def get_forum(thread: discord.Thread):
    parent = thread.parent
    if isinstance(parent, discord.ForumChannel):
        return parent
    return None


def find_tag(forum: discord.ForumChannel, tag_name: str):
    return discord.utils.find(
        lambda t: t.name.casefold() == tag_name.casefold(),
        forum.available_tags,
    )


def member_has_reviewer_role(member: discord.Member) -> bool:
    return any(role.id == REVIEWER_ROLE_ID for role in member.roles)


async def set_status_tag(thread: discord.Thread, status_key: str):
    forum = get_forum(thread)
    if forum is None:
        raise RuntimeError("This thread is not inside a forum channel.")

    target_name = STATUS_TAGS[status_key]
    target_tag = find_tag(forum, target_name)

    if target_tag is None:
        raise RuntimeError(
            f'Forum tag "{target_name}" does not exist. '
            "Create it in the forum channel settings or correct the .env file."
        )

    status_names = {name.casefold() for name in STATUS_TAGS.values()}
    kept_tags = [
        tag for tag in thread.applied_tags
        if tag.name.casefold() not in status_names
    ]

    await thread.edit(
        applied_tags=kept_tags + [target_tag],
        reason=f"LOA status changed to {target_name}",
    )


class LOAStatusView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.guild is None or interaction.guild.id != GUILD_ID:
            await interaction.response.send_message(
                "These buttons can only be used in the configured server.",
                ephemeral=True,
            )
            return False

        if not isinstance(interaction.channel, discord.Thread):
            await interaction.response.send_message(
                "These buttons only work inside a Leave of Absence forum post.",
                ephemeral=True,
            )
            return False

        forum = get_forum(interaction.channel)
        if forum is None or forum.id != FORUM_CHANNEL_ID:
            await interaction.response.send_message(
                "These buttons only work inside the Leave of Absence forum.",
                ephemeral=True,
            )
            return False

        member = interaction.user
        if not isinstance(member, discord.Member) or not member_has_reviewer_role(member):
            await interaction.response.send_message(
                "You do not have permission to change LOA statuses.",
                ephemeral=True,
            )
            return False

        return True

    async def change_status(self, interaction: discord.Interaction, status_key: str):
        thread = interaction.channel
        try:
            await set_status_tag(thread, status_key)
            visible_name = STATUS_TAGS[status_key]
            await interaction.response.send_message(
                f"✅ LOA status changed to **{visible_name}** by {interaction.user.mention}."
            )
        except discord.Forbidden:
            await interaction.response.send_message(
                "I do not have permission to change the forum tags. "
                "Give the bot **Manage Threads** permission in this forum.",
                ephemeral=True,
            )
        except Exception as exc:
            log.exception("Failed to change LOA status.")
            await interaction.response.send_message(
                f"Could not change the LOA status: {exc}",
                ephemeral=True,
            )

    @discord.ui.button(
        label="Pending",
        emoji="🟡",
        style=discord.ButtonStyle.secondary,
        custom_id="loa_status:pending",
    )
    async def pending(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.change_status(interaction, "pending")

    @discord.ui.button(
        label="Approve",
        emoji="🟢",
        style=discord.ButtonStyle.success,
        custom_id="loa_status:approved",
    )
    async def approved(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.change_status(interaction, "approved")

    @discord.ui.button(
        label="Extend",
        emoji="🔵",
        style=discord.ButtonStyle.primary,
        custom_id="loa_status:extended",
    )
    async def extended(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.change_status(interaction, "extended")

    @discord.ui.button(
        label="Deny",
        emoji="🔴",
        style=discord.ButtonStyle.danger,
        custom_id="loa_status:denied",
    )
    async def denied(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.change_status(interaction, "denied")

    @discord.ui.button(
        label="Returned",
        emoji="⚪",
        style=discord.ButtonStyle.secondary,
        custom_id="loa_status:returned",
    )
    async def returned(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.change_status(interaction, "returned")


class LOABot(commands.Bot):
    async def setup_hook(self):
        self.add_view(LOAStatusView())
        log.info("Persistent LOA status buttons registered.")


bot = LOABot(command_prefix="!", intents=intents)


@bot.event
async def on_ready():
    log.info("Logged in as %s (%s)", bot.user, bot.user.id if bot.user else "?")


@bot.event
async def on_thread_create(thread: discord.Thread):
    try:
        forum = get_forum(thread)
        if forum is None or forum.id != FORUM_CHANNEL_ID:
            return

        log.info("New LOA forum post detected: %s (%s)", thread.name, thread.id)

        try:
            await set_status_tag(thread, "pending")
        except Exception:
            log.exception("Could not apply Pending tag to thread %s", thread.id)

        message = REVIEW_MESSAGE.format(role_id=REVIEWER_ROLE_ID)
        await thread.send(
            message,
            view=LOAStatusView(),
            allowed_mentions=discord.AllowedMentions(
                roles=True,
                users=False,
                everyone=False,
                replied_user=False,
            ),
        )

    except discord.Forbidden:
        log.exception(
            "Discord denied an action. Check the bot's forum/thread permissions."
        )
    except discord.HTTPException:
        log.exception("Discord API error while processing a new LOA post.")
    except Exception:
        log.exception("Unexpected error while processing a new LOA post.")


if not TOKEN:
    raise RuntimeError(
        "DISCORD_TOKEN is missing. Copy .env.example to .env and add your bot token."
    )

if not all([GUILD_ID, FORUM_CHANNEL_ID, REVIEWER_ROLE_ID]):
    raise RuntimeError(
        "GUILD_ID, FORUM_CHANNEL_ID, and REVIEWER_ROLE_ID must all be set in .env."
    )

bot.run(TOKEN)
