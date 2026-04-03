# 🦇 VTES Card detection tool 🦇
Automated card data extraction for OBS streaming
---
CREDITS

This tool is a fork of https://1vcian.github.io/Pokemon-TCGP-Card-Scanner/
---

## Project Overview
This project has been made to improve streaming VTES tournament finals and therefore improve the visibility of the game for the spectator. To achieve this, this *OBS plugin*. requires a detection mechanism to match the cards with their sets. We're using OpenCV and YOLOv11. The implementation is made in C++ to maximize OBS compatibility.

This repo uses public static sources like
https://static.krcg.org/data/vtes.json
or
https://static.krcg.org/card/

trainCreator.py creates a dataset of images that *should* include different angles, lighting, obstacles, rotation and resolution.

I own this code but not the images used. Those and their trademarks belong to Paradox Interactive AB, and are used with permission under the Dark Pack agreement.
