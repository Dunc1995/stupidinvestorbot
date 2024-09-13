import { numeric, sqliteTable, text } from "drizzle-orm/sqlite-core";

export const coinProperties = sqliteTable('coin_properties', {
    coinName: text('coin_name'),
    quantityTickSize: numeric('quantity_tick_size'),
    quantityDecimals: numeric('quantity_decimals'),
    priceTickSize: numeric('price_tick_size'),
    priceDecimals: numeric('price_decimals')
});