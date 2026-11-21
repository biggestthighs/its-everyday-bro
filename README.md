# Its Everyday Bro

**Best executor ever, according to the guy in the video.**

Serverside mode comes pre-checked. The **Execute**, **Clear**, and **Inject** buttons are full size. The music-video thumbnail is in glorious potato quality. We put everything into the settings menu.

- **Serverside mode** — Already checked. That's one less thing between you and greatness.
- **FE bypass mode** — A second checkbox. For the advanced users.
- **Lua editor** — Type your masterpiece in full color.

## Download

- [Its Everyday Bro for Windows](https://github.com/biggestthighs/its-everyday-bro/releases/download/v1.0.0/Its-Everyday-Bro.exe)
- [Its Everyday Bro for Linux](https://github.com/biggestthighs/its-everyday-bro/releases/download/v1.1.0/its-everyday-bro-linux.pyz)

### Run on Linux

Open a terminal in the download folder and run:

```sh
python3 its-everyday-bro-linux.pyz
```

You'll need Python 3.9 or newer with Tkinter and a graphical desktop. On Debian or Ubuntu, install Tkinter with `sudo apt install python3-tk`. No pip packages are required.

To run from a checkout, use `python3 linux`. To rebuild the downloadable launcher, run:

```sh
python3 -m zipapp linux -o its-everyday-bro-linux.pyz -p '/usr/bin/env python3' --compress
```

This is a frontend-only app. The buttons and settings are visual controls. The app does not run scripts, connect to Roblox, or inject into any process.
