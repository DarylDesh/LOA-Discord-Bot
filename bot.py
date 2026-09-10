import os
import sqlite3
import logging
from pathlib import Path

import discord
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")
DB_PATH = Path(os.getenv("LOA_DATABASE", "loa_config.db"))

STATUS_TAGS = {
    "pending": os.getenv("TAG_PENDING", "Pending"),
    "approved": os.getenv("TAG_APPROVED", "Approved"),
    "extended": os.getenv("TAG_EXTENDED", "Extended"),
    "denied": os.getenv("TAG_DENIED", "Denied"),
    "returned": os.getenv("TAG_RETURNED", "Returned"),
}

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
log = logging.getLogger("loa-bot")

intents = discord.Intents.default()
intents.guilds = True


def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS guild_settings (
                guild_id INTEGER PRIMARY KEY,
                forum_channel_id INTEGER NOT NULL,
                reviewer_role_id INTEGER NOT NULL,
                enabled INTEGER NOT NULL DEFAULT 1,
                updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        conn.commit()


def save_guild_settings(guild_id: int, forum_channel_id: int, reviewer_role_id: int):
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            """
            INSERT INTO guild_settings (guild_id, forum_channel_id, reviewer_role_id, enabled, updated_at)
            VALUES (?, ?, ?, 1, CURRENT_TIMESTAMP)
            ON CONFLICT(guild_id) DO UPDATE SET
                forum_channel_id = excluded.forum_channel_id,
                reviewer_role_id = excluded.reviewer_role_id,
                enabled = 1,
                updated_at = CURRENT_TIMESTAMP
            """,
            (guild_id, forum_channel_id, reviewer_role_id),
        )
        conn.commit()


def get_guild_settings(guild_id: int):
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        row = conn.execute(
            """
            SELECT guild_id, forum_channel_id, reviewer_role_id, enabled
            FROM guild_settings
            WHERE guild_id = ?
            """,
            (guild_id,),
        ).fetchone()
        return dict(row) if row else None


def disable_guild(guild_id: int):
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            "UPDATE guild_settings SET enabled = 0, updated_at = CURRENT_TIMESTAMP WHERE guild_id = ?",
            (guild_id,),
        )
        conn.commit()


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


def missing_status_tags(forum: discord.ForumChannel):
    available = {tag.name.casefold() for tag in forum.available_tags}
    return [name for name in STATUS_TAGS.values() if name.casefold() not in available]


def member_has_role(member: discord.Member, role_id: int) -> bool:
    return any(role.id == role_id for role in member.roles)


def member_can_review(member: discord.Member, reviewer_role_id: int) -> bool:
    return (
        member.guild_permissions.administrator
        or member.guild_permissions.manage_guild
        or member_has_role(member, reviewer_role_id)
    )


async def set_status_tag(thread: discord.Thread, status_key: str):
    forum = get_forum(thread)
    if forum is None:
        raise RuntimeError("This thread is not inside a forum channel.")

    target_name = STATUS_TAGS[status_key]
    target_tag = find_tag(forum, target_name)

    if target_tag is None:
        raise RuntimeError(
            f'Forum tag "{target_name}" does not exist. '
            "A server administrator must create the required LOA status tags."
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
        if interaction.guild is None:
            await interaction.response.send_message(
                "These buttons can only be used inside a Discord server.",
                ephemeral=True,
            )
            return False

        settings = get_guild_settings(interaction.guild.id)
        if not settings or not settings["enabled"]:
            await interaction.response.send_message(
                "LOA Manager has not been configured for this server yet.",
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
        if forum is None or forum.id != settings["forum_channel_id"]:
            await interaction.response.send_message(
                "These buttons only work inside this server's configured LOA forum.",
                ephemeral=True,
            )
            return False

        member = interaction.user
        if not isinstance(member, discord.Member) or not member_can_review(
            member, settings["reviewer_role_id"]
        ):
            await interaction.response.send_message(
                "You do not have permission to change LOA statuses. You need the configured reviewer role or Server Administrator/Manage Server permission.",
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
        init_db()
        self.add_view(LOAStatusView())
        synced = await self.tree.sync()
        log.info("Persistent LOA status buttons registered.")
        log.info("Synced %s global application command(s).", len(synced))


bot = LOABot(command_prefix="!", intents=intents)


@bot.tree.command(name="loa-setup", description="Configure LOA Manager for this Discord server")
@app_commands.describe(
    forum="The Forum channel where members submit LOA requests",
    reviewer_role="The role allowed to review and change LOA statuses",
)
@app_commands.checks.has_permissions(manage_guild=True)
async def loa_setup(
    interaction: discord.Interaction,
    forum: discord.ForumChannel,
    reviewer_role: discord.Role,
):
    if interaction.guild is None:
        await interaction.response.send_message(
            "This command can only be used inside a Discord server.", ephemeral=True
        )
        return

    missing = missing_status_tags(forum)
    if missing:
        await interaction.response.send_message(
            "I cannot finish setup yet. Create these Forum tags first:\n"
            + "\n".join(f"• {name}" for name in missing)
            + "\n\nThen run `/loa-setup` again.",
            ephemeral=True,
        )
        return

    save_guild_settings(interaction.guild.id, forum.id, reviewer_role.id)

    await interaction.response.send_message(
        "✅ **LOA Manager is configured for this server.**\n\n"
        f"**LOA Forum:** {forum.mention}\n"
        f"**Reviewer Role:** {reviewer_role.mention}\n\n"
        "New posts in that forum will automatically be marked Pending and sent to the reviewer role with status buttons. Server administrators and members with Manage Server permission can also use the status buttons.",
        ephemeral=True,
        allowed_mentions=discord.AllowedMentions.none(),
    )


@loa_setup.error
async def loa_setup_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    if isinstance(error, app_commands.MissingPermissions):
        message = "You need the **Manage Server** permission to configure LOA Manager."
    else:
        log.exception("Error in /loa-setup", exc_info=error)
        message = "Something went wrong while configuring LOA Manager. Please try again."

    if interaction.response.is_done():
        await interaction.followup.send(message, ephemeral=True)
    else:
        await interaction.response.send_message(message, ephemeral=True)


@bot.tree.command(name="loa-settings", description="Show this server's LOA Manager settings")
@app_commands.checks.has_permissions(manage_guild=True)
async def loa_settings(interaction: discord.Interaction):
    if interaction.guild is None:
        await interaction.response.send_message(
            "This command can only be used inside a Discord server.", ephemeral=True
        )
        return

    settings = get_guild_settings(interaction.guild.id)
    if not settings or not settings["enabled"]:
        await interaction.response.send_message(
            "LOA Manager is not configured for this server. Run `/loa-setup` first.",
            ephemeral=True,
        )
        return

    forum = interaction.guild.get_channel(settings["forum_channel_id"])
    role = interaction.guild.get_role(settings["reviewer_role_id"])

    forum_text = forum.mention if forum else f"Missing channel ({settings['forum_channel_id']})"
    role_text = role.mention if role else f"Missing role ({settings['reviewer_role_id']})"

    await interaction.response.send_message(
        "**LOA Manager Settings**\n"
        f"LOA Forum: {forum_text}\n"
        f"Reviewer Role: {role_text}\n"
        "Status: Enabled",
        ephemeral=True,
        allowed_mentions=discord.AllowedMentions.none(),
    )


@bot.tree.command(name="loa-disable", description="Disable LOA Manager in this server")
@app_commands.checks.has_permissions(manage_guild=True)
async def loa_disable(interaction: discord.Interaction):
    if interaction.guild is None:
        await interaction.response.send_message(
            "This command can only be used inside a Discord server.", ephemeral=True
        )
        return

    disable_guild(interaction.guild.id)
    await interaction.response.send_message(
        "⏸️ LOA Manager has been disabled for this server. Run `/loa-setup` to enable it again.",
        ephemeral=True,
    )


@bot.event
async def on_ready():
    log.info("Logged in as %s (%s)", bot.user, bot.user.id if bot.user else "?")
    log.info("Connected to %s Discord server(s).", len(bot.guilds))


@bot.event
async def on_thread_create(thread: discord.Thread):
    try:
        if thread.guild is None:
            return

        settings = get_guild_settings(thread.guild.id)
        if not settings or not settings["enabled"]:
            return

        forum = get_forum(thread)
        if forum is None or forum.id != settings["forum_channel_id"]:
            return

        log.info(
            "New LOA forum post detected in %s: %s (%s)",
            thread.guild.name,
            thread.name,
            thread.id,
        )

        try:
            await set_status_tag(thread, "pending")
        except Exception:
            log.exception("Could not apply Pending tag to thread %s", thread.id)

        reviewer_role_id = settings["reviewer_role_id"]
        message = (
            "🚨 **New Leave of Absence Request**\n"
            f"<@&{reviewer_role_id}>, a new LOA request has been submitted.\n"
            "Please review the information above and use the buttons below to update the request status."
        )

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
        "DISCORD_TOKEN is missing. Add it as a private environment variable on your hosting service."
    )

bot.run(TOKEN)
