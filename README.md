# The World in One Page — Wednesday 18 November 2026

A Python program (stdlib + PIL only) that draws a 1024×1024 newspaper
front page summing up the world news of Wednesday 18 November 2026 and
writes it to `$MAKEFUN_OUTPUT_DIR/entry.png`.

Layout: a masthead naming the day, a hero panel on Nvidia's earnings
(revenue $115.84bn, doubled year on year; the board will not reinstate
Jensen Huang), a grid of eight story tiles (Manila ASEAN talks, the
Crimean Bridge strikes, the Iran drone attack in Bahrain, Canada–China
trade, UK settlement sanctions, the UN casualty tolls, Dhoni's IPL
retirement, Deutsche Bank), and an "Also in brief" strip (Cyclone
Akvan, SpaceX, the Grammys, Trump's BBC lawsuit deadline).

Run: `MAKEFUN_OUTPUT_DIR=out python3 main.py` — deterministic, no
network, no randomness; repeated runs produce byte-identical output.
