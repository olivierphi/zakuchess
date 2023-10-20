export type Settings = {
  readonly ZAKUCHESS_VERSION: string
  readonly DEVELOPMENT_MODE: boolean
}

let currentSettings: Settings | null = null

export const setSettings = (newSettings: Settings): void => {
  currentSettings = newSettings
}

export const getSettings = (): Settings => {
  if (currentSettings === null) {
    throw new Error("Settings not set")
  }
  return currentSettings
}
