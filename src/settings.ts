export type Settings = {
  readonly ZAKUCHESS_VERSION: string
  readonly DEVELOPMENT_MODE: boolean
  readonly COOKIES_SIGNING_SECRET: string
}

let currentSettings: Settings | null = null

export const setSettings = (newSettings: Settings): void => {
  if (
    !newSettings.COOKIES_SIGNING_SECRET ||
    newSettings.COOKIES_SIGNING_SECRET.length < 30
  ) {
    throw new Error("COOKIES_SIGNING_SECRET is too short (30 chars min)")
  }
  currentSettings = newSettings
}

export const getSettings = (): Settings => {
  if (currentSettings === null) {
    throw new Error("Settings not set")
  }
  return currentSettings
}
