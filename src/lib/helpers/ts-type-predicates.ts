export function isNotNull<T>(arg: T | null): arg is T {
	return arg !== null
}
