import { Client } from "pg";

const client = new Client({
  user: "postgres",
  password: "123456",
  host: "localhost",
  port: 5432,
  database: "fundamentals",
});

export default {
  async query(text: string, params: any[] = []) {
    const res = await client.query(text, params);
    return res;
  },

  async getClient() {
    await client.connect();
    return client;
  },
};
