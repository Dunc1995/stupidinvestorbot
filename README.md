# Stupid Investor Bot

## Overview
This application is my attempt at implementing a Crypto trading bot that will select coins to invest in, buy/sell in small increments of USD based on simplistic statistical criteria and adjust its trading criteria according to its classification of current market conditions. My hypothesis is that AI will flood the market with bots that end up in a state of group-think, so I'm hoping that decision-making based on a simple ruleset will in actual fact be a niche strategy that sees some success.

## **investorbot** Folder Structure
Most files in the project structure are self-explanatory - constants for constants, enums for enums, etc. - there is some potential confusion between structs and models, but essentially models are describing anything to be stored in a database whilst structs are simply any data structures used within the application.

```
├── __init__.py <- Currently used to store services used across the application - this may need to change.
├── __main__.py <- Defines all commands available via CLI.
├── analysis.py <- Stores market analysis commands.
├── app.py <- Describes Flask routes - here the application proxies any requests from external API's to make data available in the browser, without needing to expose any private keys.
├── constants.py
├── db.py <- Responsible for creating the application database and adding any necessary data.
├── decorators.py
├── enums.py
├── models.py
├── requirements.txt
├── routines.py <- Describes the main business logic of the application - executable either via CLI or via Flask background routines. Implementation hasn't been finalized.
├── services.py <- Perhaps should be called contextmanagers or similar.
├── websocket.py
├── integrations <- Any integration defined here should inherit the ICryptoService interface - this enables different services to connect to the application - either simulations or other Crypto trading platforms.
│   ├── __init__.py
│   ├── cryptodotcom
│   │   ├── __init__.py
│   │   ├── constants.py
│   │   ├── enums.py
│   │   ├── mappings.py
│   │   ├── services.py
│   │   ├── structs.py
│   │   └── http
│   │       ├── __init__.py
│   │       ├── base.py
│   │       ├── market.py
│   │       └── user.py
│   └── simulation
│       ├── __init__.py
│       ├── models.py
│       └── services.py
├── interfaces
│   ├── __init__.py
│   └── services.py <- Formalizes functionality required for the application to be able to run.
├── structs <- TODO - Maybe reduce files here to a single file in the folder above.
│   ├── __init__.py
│   ├── egress.py
│   └── internal.py
└── templates
    ├── index.html
    └── emails
        ├── example.html
        └── heartbeat.html
```