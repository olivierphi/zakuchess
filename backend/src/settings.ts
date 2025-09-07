export type Settings = {
  readonly ZAKUCHESS_VERSION: string;
  readonly DEVELOPMENT_MODE: boolean;
  readonly COOKIES_SIGNING_SECRET: string;
  readonly ASTRO_DEV_URL: string;
  readonly ASTRO_PROD_BUILD_PATH: string;
  readonly ASTRO_ASSETS_PATH: string;
};

let currentSettings: Settings | null = null;

export const setSettings = (newSettings: Settings): void => {
  const cookiesSigningSecretLength = newSettings.COOKIES_SIGNING_SECRET
    ? newSettings.COOKIES_SIGNING_SECRET.length
    : 0;
  if (cookiesSigningSecretLength < 30) {
    throw new Error(
      `COOKIES_SIGNING_SECRET is too short (30 chars min, got ${cookiesSigningSecretLength})`,
    );
  }
  currentSettings = newSettings;
};

export const getSettings = (): Settings => {
  if (currentSettings === null) {
    throw new Error("Settings not set");
  }
  return currentSettings;
};
