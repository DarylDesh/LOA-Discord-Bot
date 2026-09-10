# LOA Discord Forum Bot — Multi-Server Edition

LOA Manager is a Discord Leave of Absence management bot designed to run from one hosted bot account while serving multiple Discord servers.

## What changed

The bot no longer uses one global `GUILD_ID`, `FORUM_CHANNEL_ID`, or `REVIEWER_ROLE_ID`.

Each Discord server configures its own settings with `/loa-setup`, and those settings are stored locally in `loa_config.db`.

## Server setup

A Discord administrator with **Manage Server** permission runs:

`/loa-setup`

Discord will ask them to choose:

- the Forum channel used for LOA requests
- the reviewer/staff role allowed to change LOA statuses

The selected Forum must already contain these tags:

- Pending
- Approved
- Extended
- Denied
- Returned

## Commands

- `/loa-setup` — configure or update the LOA Forum and reviewer role for that server
- `/loa-settings` — show the current server configuration
- `/loa-disable` — disable LOA Manager for that server

## Automatic workflow

When a new post is created in a configured LOA Forum, the bot:

1. applies the `Pending` tag
2. pings that server's configured reviewer role
3. posts persistent status buttons
4. lets authorized reviewers change the status to Pending, Approved, Extended, Denied, or Returned
5. preserves unrelated Forum tags
6. posts an audit message showing who changed the status

## Hosting environment variables

Only the Discord bot token is required for multi-server operation:

`DISCORD_TOKEN`

Optional variables:

- `TAG_PENDING`
- `TAG_APPROVED`
- `TAG_EXTENDED`
- `TAG_DENIED`
- `TAG_RETURNED`
- `LOA_DATABASE`

Never commit a real `.env` file or Discord bot token to GitHub.

## Bot permissions

The bot needs appropriate permissions in each configured LOA Forum, including:

- View Channel
- Send Messages
- Send Messages in Threads
- Read Message History
- Manage Threads
- Mention @everyone, @here, and All Roles

The bot does not need Administrator permission.

## Multi-server use

One hosted instance can be invited to multiple Discord servers. Each server maintains its own Forum and reviewer-role configuration in the bot database.

A licensing or paid-access system can be added separately later without changing the basic multi-server workflow.
