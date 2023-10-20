export type StaticAssetOriginalPath = string
export type StaticAssetRewrittenPath = string
export type StaticAssetsMapping = Record<
  StaticAssetOriginalPath,
  StaticAssetRewrittenPath
>

let staticAssetsMapping: StaticAssetsMapping = {}
let staticAssetsViteDevServerURL: string = ""

export const setStaticAssetsMapping = (mapping: StaticAssetsMapping): void => {
  if (staticAssetsViteDevServerURL) {
    throw new Error(
      "Cannot set static assets mapping (prod setting) after setting Vite dev server URL (development setting)",
    )
  }
  staticAssetsMapping = mapping
}
export const setStaticAssetsViteDevServerURL = (url: string): void => {
  if (Object.keys(staticAssetsMapping).length > 0) {
    throw new Error(
      "Cannot set Vite dev server URL (development setting) after setting static assets mapping (prod setting)",
    )
  }
  staticAssetsViteDevServerURL = url.replace(/\/$/, "") // strip trailing slash
}

export const getStaticAssetsViteDevServerURL = (): string => {
  return staticAssetsViteDevServerURL
}

export const staticAssetPath = (
  path: StaticAssetOriginalPath,
): StaticAssetRewrittenPath => {
  if (staticAssetsViteDevServerURL) {
    return `${staticAssetsViteDevServerURL}/${path}`
  }

  if (!(path in staticAssetsMapping)) {
    throw new Error(`Path ${path} not found in static assets mapping`)
  }
  return staticAssetsMapping[path]
}
