<script lang="ts">
    import type { PageData } from "./$types";

    export let data: PageData;
</script>

<div class="container mx-auto pt-2 pb-2">
    <article class="p-5 prose">
        <h1>About</h1>
        <h2>Overview</h2>
        <p>
            The Stupid Investor Bot is a high frequency trading bot that can
            take a big picture analysis of the current market in the last 24
            hours and use this information to inform its strategy for investing
            in individual coins.
        </p>
        <p>
            As the crypto currency market is inherently irrational, it is my
            hypothesis that you don't need a particularly clever strategy to be
            able to profit from fluctuating prices.
        </p>
        <p>
            The following logic is applied depending on how the bot
            characterizes current market conditions:
        </p>
        <ul>
            <!-- TODO add a rationale column to the coin_selection_criteria table, then pull the column data into this page to populate this list. -->
            <li>
                If there is a general rising trend, then the bot can jump on the
                band wagon and risk investing in highly volatile coins that are
                rising sharply.
            </li>
            <li>
                If the market is flat-lining, then invest in coins that have a
                high volatility, i.e. standard deviation, as long as their
                general trend is flat or rising in value.
            </li>
            <li>
                If the market is plummeting in value, reduce the bot's trading
                cadence and only choose coins that are following the general
                market trend.
            </li>
        </ul>
        <p>
            Of course the above strategies may be inherently flawed, so the
            trading strategies for the bot are configurable.
        </p>
    </article>
</div>
