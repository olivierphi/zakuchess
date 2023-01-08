/** @type import("knex").Knex.Config */
const config = {
	client: "cockroachdb",
	connection: process.env.DATABASE_URL,
	migrations: {
		directory: "../db/migrations",
	},
}

export default config
