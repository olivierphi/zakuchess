import knex from "knex"

export const pg = knex({
	client: "cockroachdb",
	connection: process.env.DATABASE_URL,
})
