import path from "node:path";
import { readFile } from "node:fs/promises";
import { getSettings } from "../settings.ts";

export async function getAstroPage(astroPageUrlPath: string): Promise<string> {
  switch (getSettings().DEVELOPMENT_MODE) {
    case true:
      return getAstroDevPageInRealTime(astroPageUrlPath);
    case false:
      return getAstroProdPageFromBuild(astroPageUrlPath);
  }
}

async function getAstroDevPageInRealTime(
  astroPageUrlPath: string,
): Promise<string> {
  const astroDevServerUrl = getSettings().ASTRO_DEV_URL;
  const targetAstroUrl = `${astroDevServerUrl}${astroPageUrlPath}`;
  const astroDevServerResponse = await fetch(targetAstroUrl);
  if (astroDevServerResponse.status !== 200) {
    throw new Error(
      `Got status '${astroDevServerResponse.status}' from Astro for URL '${targetAstroUrl}'`,
    );
  }
  const rawAstroPage = await astroDevServerResponse.text();
  const postProcessedAstroPage = postProcessAstroPage(rawAstroPage, {
    astroDevServerUrl,
  });
  return postProcessedAstroPage;
}

async function getAstroProdPageFromBuild(
  astroPageUrlPath: string,
): Promise<string> {
  const astroProdBuildPath = getSettings().ASTRO_PROD_BUILD_PATH;
  const targetPreBuiltAstroPagePath = path.join(
    astroProdBuildPath,
    astroPageUrlPath,
    "index.html",
  );
  const pageContent = await readFile(targetPreBuiltAstroPagePath, "utf8");
  return pageContent;
}

function postProcessAstroPage(
  pageContent: string,
  { astroDevServerUrl }: { astroDevServerUrl: string },
): string {
  for (const vitePrefix of [
    '"/@vite/',
    '"/@fs/',
    '"/@id/',
    '"/src/',
    '"/node_modules/',
    '"/favicon-',
    '"/assets/',
  ]) {
    pageContent = pageContent.replaceAll(
      vitePrefix,
      `"${astroDevServerUrl}${vitePrefix.substring(1)}`,
    );
  }
  return pageContent;
}
