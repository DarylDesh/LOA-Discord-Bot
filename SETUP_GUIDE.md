# COMPLETE BEGINNER SETUP GUIDE
## Leave of Absence Discord Forum Bot with Status Buttons

This guide assumes you have never created a Discord bot and are not comfortable using a PC yet.

The bot will do this:

1. A person creates a new post in your Leave of Absence Forum.
2. The bot automatically applies the `Pending` forum tag.
3. The bot automatically pings the role you choose, such as `High Command`.
4. The bot posts five buttons:
   - 🟡 Pending
   - 🟢 Approve
   - 🔵 Extend
   - 🔴 Deny
   - ⚪ Returned
5. Only members who have the reviewer role can press the buttons.
6. When a reviewer presses a button, the forum post status tag changes automatically.
7. The bot posts who changed the status.

The buttons are designed to keep working after the bot is restarted.

---

# PART 1 — EXTRACT THIS PACKAGE

1. Find the ZIP file you downloaded.
2. Right-click the ZIP file.
3. Click **Extract All...**
4. Windows will show you where it plans to create the folder.
5. Click **Extract**.
6. A normal folder should open.

Inside the folder you should see:

- `bot.py`
- `.env.example`
- `requirements.txt`
- `START_BOT.bat`
- `TEST_BOT.bat`
- `SETUP_GUIDE.md`
- `README.md`
- `.gitignore`

Do not delete these files.

---

# PART 2 — MAKE SURE YOU HAVE A DISCORD SERVER

You must have permission to manage the Discord server where the bot will be installed.

Open Discord.

Look on the left side for your server.

You will need to be the server owner or have enough permissions to:
- manage channels,
- manage roles,
- and add applications/bots.

---

# PART 3 — CREATE OR PREPARE THE LEAVE OF ABSENCE FORUM

In Discord:

1. Open your server.
2. Find your Leave of Absence Forum channel.

If you do not already have a Forum channel:

1. Right-click the server's channel area.
2. Choose **Create Channel**.
3. Choose **Forum**.
4. Give it a name such as `leave-of-absence`.
5. Finish creating it.

Now create these Forum tags:

- Pending
- Approved
- Extended
- Denied
- Returned

To do that:

1. Right-click the Leave of Absence Forum.
2. Choose **Edit Channel**.
3. Find the section for **Tags** or **Forum Tags**.
4. Add each of the five tags above.
5. You may assign emojis to them if you want:
   - 🟡 Pending
   - 🟢 Approved
   - 🔵 Extended
   - 🔴 Denied
   - ⚪ Returned
6. Save your changes.

IMPORTANT:
The WORDS must be `Pending`, `Approved`, `Extended`, `Denied`, and `Returned` unless you later change the names in the `.env` file.

---

# PART 4 — CHOOSE OR CREATE THE REVIEWER ROLE

The bot needs to know which role should:
- be pinged when a new LOA is submitted, and
- be allowed to press the status buttons.

This might be a role called:
- High Command
- Management
- Supervisors
- Administration

If the role already exists, you can use it.

If you need to create one:

1. Click the server name near the upper-left corner of Discord.
2. Click **Server Settings**.
3. Click **Roles**.
4. Click **Create Role**.
5. Give it a name such as `High Command`.
6. Save the role.
7. Give that role to the staff members who should review LOAs.

---

# PART 5 — TURN ON DISCORD DEVELOPER MODE

You need Developer Mode so Discord lets you copy IDs.

1. In Discord, look at the bottom-left corner.
2. Click the small gear icon next to your username.
3. This opens **User Settings**.
4. Scroll down the left side.
5. Click **Advanced**.
6. Find **Developer Mode**.
7. Turn **Developer Mode ON**.
8. Close User Settings.

Leave Developer Mode turned on while you finish this setup.

---

# PART 6 — COPY YOUR SERVER ID

1. Look at the server icon on the far left side of Discord.
2. Right-click the server icon.
3. Look near the bottom of the menu.
4. Click **Copy Server ID**.

Do not worry if you do not see anything happen. Discord copied the number to your clipboard.

Open Notepad and paste the number there temporarily.

It will be a long number similar to:

`123456789012345678`

Label it:

`SERVER ID`

---

# PART 7 — COPY THE LEAVE OF ABSENCE FORUM ID

1. Find your Leave of Absence Forum channel in Discord.
2. Right-click the Forum channel name.
3. Click **Copy Channel ID**.
4. Paste it into your temporary Notepad document.

Label it:

`LOA FORUM ID`

---

# PART 8 — COPY THE REVIEWER ROLE ID

1. Click the server name.
2. Click **Server Settings**.
3. Click **Roles**.
4. Find the role that should review LOAs.
5. Right-click that role.
6. Click **Copy Role ID**.
7. Paste that number into Notepad.

Label it:

`REVIEWER ROLE ID`

You should now have three long numbers saved temporarily.

---

# PART 9 — CREATE THE DISCORD APPLICATION

Open a web browser such as Chrome or Edge.

Go to the Discord Developer Portal:

https://discord.com/developers/applications

Sign in to Discord if asked.

Then:

1. Click **New Application**.
2. Enter a name such as:
   `Leave of Absence Manager`
3. Accept Discord's required terms if shown.
4. Click **Create**.

You are now inside your new Discord application.

---

# PART 10 — CREATE THE BOT USER

On the left side of the Developer Portal:

1. Click **Bot**.
2. Discord may already show a bot user for the application.
3. Give the bot a username if needed.
4. You can upload an icon if you want.

You do NOT need to turn on every Privileged Gateway Intent for this bot.

---

# PART 11 — GET THE BOT TOKEN

THIS IS THE MOST IMPORTANT SECURITY STEP.

On the **Bot** page:

1. Find the **Token** section.
2. Click **Reset Token** if Discord requires it.
3. Discord may ask for your password or two-factor authentication.
4. Click **Copy** to copy the token.

The bot token is basically the bot's password.

NEVER:
- post it in Discord,
- send it to another person,
- upload it to GitHub,
- take a screenshot showing it,
- or paste it into a public chat.

If anyone gets your token, go back to the Developer Portal and reset it.

For now, paste the token into your temporary Notepad file and label it:

`BOT TOKEN`

---

# PART 12 — INSTALL THE BOT INTO YOUR SERVER

In the Discord Developer Portal, look on the left for either:

- **Installation**, or
- **OAuth2**

Discord changes its Developer Portal layout from time to time.

The goal is to generate an installation link for your bot.

For a server installation, include these scopes if Discord asks:

- `bot`
- `applications.commands`

Even though this version uses buttons rather than slash commands, including `applications.commands` is harmless and keeps the application setup standard.

Give the bot these permissions:

- View Channels
- Send Messages
- Send Messages in Threads
- Read Message History
- Manage Threads
- Mention @everyone, @here, and All Roles

You do NOT need to give the bot Administrator.

After Discord gives you an install or authorization link:

1. Open that link.
2. Choose your Discord server.
3. Click **Continue** or **Authorize**.
4. Complete the CAPTCHA if Discord shows one.

The bot should now appear in your server's member list.

It may show as OFFLINE. That is normal because you have not started the Python program yet.

---

# PART 13 — GIVE THE BOT PERMISSION IN THE LOA FORUM

Channel permissions can block a bot even when the bot has server permissions.

In Discord:

1. Right-click your Leave of Absence Forum.
2. Click **Edit Channel**.
3. Click **Permissions**.
4. Add the bot itself or the bot's role.
5. Make sure the bot is allowed:
   - View Channel
   - Send Messages
   - Send Messages in Threads
   - Read Message History
   - Manage Threads
   - Mention @everyone, @here, and All Roles
6. Save your changes.

`Manage Threads` is especially important because the bot uses it to change the forum tags.

---

# PART 14 — INSTALL PYTHON ON YOUR COMPUTER

The bot is written in Python.

Open your web browser.

Go to:

https://www.python.org/downloads/

Download a current Python 3 version.

When the Python installer opens:

IMPORTANT:

Before clicking Install, look near the bottom of the installer window for:

`Add python.exe to PATH`

CHECK THAT BOX.

Then:

1. Click **Install Now**.
2. Let Python finish installing.
3. Click **Close** when finished.

If Python asks about disabling a path length limit, allowing it is generally fine.

---

# PART 15 — CREATE YOUR BOT SETTINGS FILE

Go back to the extracted bot folder.

Find:

`.env.example`

You must create a copy of it.

A safe way in Windows:

1. Right-click `.env.example`.
2. Click **Copy**.
3. Right-click an empty area inside the same folder.
4. Click **Paste**.

Windows may create a file named something like:

`.env - Copy.example`

You need the final file to be named exactly:

`.env`

If Windows hides file extensions:

1. Open the folder.
2. At the top of File Explorer click **View**.
3. Turn on **File name extensions**.
4. Now rename the copied file exactly to:
   `.env`

Windows may warn that changing a file extension could make the file unusable.

Click **Yes**.

DO NOT rename the original `.env.example`.
Keep it as a backup.

---

# PART 16 — EDIT THE .ENV FILE

Right-click the new `.env` file.

Choose:

**Open with → Notepad**

You will see lines like:

`DISCORD_TOKEN=PASTE_YOUR_BOT_TOKEN_HERE`

Replace each placeholder.

Example:

`DISCORD_TOKEN=your-real-token-goes-here`

`GUILD_ID=123456789012345678`

`FORUM_CHANNEL_ID=123456789012345678`

`REVIEWER_ROLE_ID=123456789012345678`

Use the values you saved in Notepad earlier.

IMPORTANT:
- Do not add spaces before or after the `=`.
- Do not put quotation marks around the IDs.
- Keep the tag names as they are unless your Discord Forum uses different names.

When finished:

1. Click **File**.
2. Click **Save**.
3. Close Notepad.

You may now delete the temporary Notepad document containing the token if you want.

---

# PART 17 — TEST THE BOT FILE FOR BASIC ERRORS

Inside the bot folder, double-click:

`TEST_BOT.bat`

A black window will open.

If everything is good, it should say:

`SUCCESS: bot.py passed the syntax test.`

Press a key to close the window.

If it says Python is not installed, restart your computer after installing Python and try again.

---

# PART 18 — START THE BOT

Inside the bot folder, double-click:

`START_BOT.bat`

The first time you run it, the program will:

1. Check for Python.
2. Create a private Python environment for the bot.
3. Download the required Discord bot software.
4. Start the bot.

The first run needs an internet connection.

Eventually you should see a message similar to:

`Logged in as Leave of Absence Manager`

Do not close the black window.

While that window is open, the bot is running.

Look at Discord. The bot should now show as ONLINE.

---

# PART 19 — TEST A NEW LEAVE OF ABSENCE POST

Go to your Leave of Absence Forum.

Create a test post.

You can use:

Title:
`Test LOA`

Body:
`Discord Name: Test User`

`Department: Test Department`

`Rank: Test Rank`

`LOA Start Date: 08/19/2026`

`Expected Return Date: 08/25/2026`

`Reason: Testing the LOA system`

Submit the post.

The bot should:

1. Apply the `Pending` tag.
2. Reply inside the forum post.
3. Ping your reviewer role.
4. Show five buttons:
   - 🟡 Pending
   - 🟢 Approve
   - 🔵 Extend
   - 🔴 Deny
   - ⚪ Returned

---

# PART 20 — TEST THE BUTTONS

Have an account with the reviewer role open the test LOA.

Click:

`🟢 Approve`

The bot should:

1. Remove the old LOA status tag.
2. Apply `Approved`.
3. Post a message showing who changed the status.

Try the other buttons as well.

The bot keeps unrelated Forum tags in place.

---

# PART 21 — WHAT HAPPENS IF A NORMAL MEMBER CLICKS A BUTTON?

A person who does NOT have the reviewer role should not be allowed to change the status.

If they click one of the buttons, they should receive a private Discord message saying they do not have permission.

---

# PART 22 — KEEPING THE BOT ONLINE

This package runs the bot on your Windows PC.

That means:

PC ON + `START_BOT.bat` running = bot online.

If:
- you shut down the PC,
- Windows restarts,
- you close the black bot window,
- or the internet goes out,

the bot will go offline.

Existing status buttons are persistent in the bot code, so after the bot starts again, old button messages can work again.

A bot that must run 24 hours a day is normally moved to a hosting service or VPS later.

---

# PART 23 — HOW TO STOP THE BOT

Click the black bot window.

Press:

`CTRL + C`

Windows may ask if you want to terminate the batch job.

Type:

`Y`

and press Enter.

You may then close the window.

---

# PART 24 — HOW TO START IT AGAIN LATER

You do NOT need to repeat the whole setup.

Simply:

1. Open the bot folder.
2. Double-click `START_BOT.bat`.

That is all.

---

# TROUBLESHOOTING

## The bot shows offline

Make sure `START_BOT.bat` is still open.

If the black window shows an error, read the last few lines.

Common causes:
- wrong bot token,
- Python not installed correctly,
- internet connection problem.

---

## It says DISCORD_TOKEN is missing

Your settings file is probably not named exactly:

`.env`

Make sure it is NOT:

`.env.txt`

Turn on **File name extensions** in Windows File Explorer and check again.

---

## The bot does not react to new LOA posts

Check that `FORUM_CHANNEL_ID` is the ID of the actual Leave of Absence Forum channel.

Do not use the ID of an individual LOA post/thread.

Also check that the bot has:
- View Channel,
- Send Messages in Threads,
- Manage Threads.

---

## The role is shown but does not receive a notification

Make sure the bot has permission to:

`Mention @everyone, @here, and All Roles`

inside the LOA Forum.

Also make sure `REVIEWER_ROLE_ID` is the correct role ID.

---

## The Pending tag is not added

Make sure a Forum tag named exactly:

`Pending`

exists.

Check spelling.

Also check that the bot has:

`Manage Threads`

permission.

---

## Approve says the Approved tag does not exist

Create a Forum tag named exactly:

`Approved`

The same rule applies to:
- Extended
- Denied
- Returned

---

## A staff member cannot use the buttons

Make sure that staff member actually has the role whose ID you placed in:

`REVIEWER_ROLE_ID`

The bot checks for that exact role.

---

## I accidentally showed someone my bot token

Immediately:

1. Go to the Discord Developer Portal.
2. Open the bot application.
3. Open **Bot**.
4. Reset the bot token.
5. Copy the new token.
6. Open your `.env` file.
7. Replace the old token with the new token.
8. Save the file.
9. Restart `START_BOT.bat`.

The old token will no longer work.

---

# FILES YOU SHOULD NEVER SHARE

Do not share:

`.env`

That file contains your private bot token.

The package's `.gitignore` is included to reduce the risk of accidentally uploading `.env` to GitHub.

---

# NORMAL DAILY USE

Once everything is set up, you do not need to touch the code.

Your normal process is:

Member submits LOA
→ Bot marks Pending
→ Reviewer role is pinged
→ Reviewer clicks a button
→ Forum status changes

That is the entire workflow.
