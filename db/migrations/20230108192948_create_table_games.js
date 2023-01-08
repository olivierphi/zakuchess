/**
 * @param { import("knex").Knex } knex
 * @returns { Promise<void> }
 */
export const up = function (knex) {
	return knex.schema.createTable("games", function (table) {
		table.increments("id")
		table.string("fen").notNullable()
		table.string("bot_side", 1).nullable()
	})
}

/**
 * @param { import("knex").Knex } knex
 * @returns { Promise<void> }
 */
export const down = function (knex) {
	return knex.schema.dropTable("games")
}
