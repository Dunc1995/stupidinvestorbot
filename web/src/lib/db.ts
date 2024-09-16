import { drizzle } from 'drizzle-orm/libsql';
import { createClient } from '@libsql/client';
import * as schema from './schema'
import path from 'path';


const url = 'file://' + path.resolve('../app.db');
const client = createClient({ url: url });

export const dbClient = drizzle(client, { schema });

