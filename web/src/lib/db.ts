import { drizzle } from 'drizzle-orm/libsql';
import { createClient } from '@libsql/client';
import path from 'path';


const url = 'file://' + path.resolve('../app.db');
const client = createClient({ url: url });

export const dbClient = drizzle(client);

