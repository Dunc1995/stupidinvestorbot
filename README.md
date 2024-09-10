# Stupid Investor Bot

## Overview
This application is my attempt at implementing a Crypto trading bot that will select coins to invest in, buy/sell in small increments of USD based on simplistic statistical criteria and adjust its trading criteria according to its classification of current market conditions. My hypothesis is that AI will flood the market with bots that end up in a state of group-think, so I'm hoping that decision-making based on a simple ruleset will in actual fact be a niche strategy that sees some success.

## Definitions
- **Instruments** - data describing how coin orders should be formatted in order to satisfy the Crypto API. For example, an order price of `$5.9875432` may need to be rounded to `$5.9875` for the API to successfully place an order. Each coin has its specific rounding properties.
- **PositionBalance** - tbc
- **Tickers** - tbc
- **Valuations** - tbc