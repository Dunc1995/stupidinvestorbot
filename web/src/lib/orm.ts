import { drizzle } from 'drizzle-orm/libsql';
import { createClient } from '@libsql/client';
import { sqliteTable, text, numeric } from 'drizzle-orm/sqlite-core';
import path from 'path';


const url = 'file://' + path.resolve('../app.db');

export const coinProperties = sqliteTable('coin_properties', {
    coinName: text('coin_name'),
    quantityTickSize: numeric('quantity_tick_size'),
    quantityDecimals: numeric('quantity_decimals'),
    priceTickSize: numeric('price_tick_size'),
    priceDecimals: numeric('price_decimals')
});


const client = createClient({ url: url });

export const dbClient = drizzle(client);

