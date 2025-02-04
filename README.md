# Stupid Investor Bot

## Overview
This application is my attempt at implementing a Crypto trading bot that will
trade "intelligently" and hopefully be able to profit from the inherent
volatility in the Crypto market - I named it a stupid bot as a reminder to
myself that in all likelihood this application will fail unless I get lucky.

Initially the plan was to select coins to invest in, buy/sell in small
increments of USD based on simplistic statistical criteria and adjust its
trading criteria according to its classification of current market conditions -
I have now come to the conclusion that this approach, no matter what statistical
method you use, will essentially achieve average performance comparable to a buy
and hold strategy.

Going forward I plan to integrate the bot with a news API and cross-reference
news articles with a LLM such that I can use AI to make an educated guess about
how current events may impact the market in the future. My hope is that this
approach could yield some noticeable improvements to traditional methods.

## Usage

Important commands to the investorbot are accessible via CLI. These commands are
subject to change quite regularly as I flesh out the bot's functionality.
Accessing bot functions via CLI allows the application to be configured with
cron, or Task Scheduler, but for the time being I am letting Flask handle all
the bot's moving parts.

`python -m investorbot --help`

If you are met with the following error, you need to set your
INVESTOR_APP_INTEGRATION environment variable as stated. This quite deliberately
prevents you from trying to execute the bot against a live API unless this is
intended.

```
Please specify a trading platform integration via environment variable. For example:

`export INVESTOR_APP_INTEGRATION=SIMULATED`

Your options are ['SIMULATED', 'CRYPTODOTCOM']
```

## Docker Deployment

The bot can also be deployed with docker via:
```
docker-compose build && docker-compose up -d
```
> N.B. some dependencies may be missing from the front-end web app whilst using
> Docker - I have still to test building the application from a blank slate.

If configured correctly you should be able to access the front-end website via
http://localhost:3000 and the bot's API on http://localhost:8080. This is all
still under development so there are undoubtedly loose ends I need to tidy up
and fix.

If the front-end website styling doesn't look right, the likelihood is that
`output.css` needs to be recreated (name subject to change). This file can be
recreated by running the following (whilst in the `./web` directory):

`npx tailwindcss -i ./src/input.css -o ./static/output.css`

## Plan for MVP
- [ ] Integrate the bot with [thenewsapi](https://www.thenewsapi.com/) if
  useful.
- [ ] Integrate with ChatGPT or multiple LLM's.
- [ ] Have ChatGPT parse top news headlines and output a config for the bot to
  action on the market.
- [ ] Use websockets for timing an optimum trade price.
- [ ] Integrate REST and websockets to leverage the advantages of both
  protocols.
- [ ] Remove basic statistical methods and structs or integrate existing
  statistical code into websocket functionality - may or may not be needed.
- [ ] Implement performance monitoring for both LLM hypotheses and the profit
  made from particular instruments.

> Unfortunately I cannot prioritize this project until I find a job again, but I
> will definitely be revisiting this in the near future!

