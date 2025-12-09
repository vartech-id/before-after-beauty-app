// Central list of static assets we want warmed up so view transitions stay smooth.
import loadingA from "../views/assets/LoadingAnimation/loading-a.webp";
import loadingB from "../views/assets/LoadingAnimation/loading-b.webp";
import loadingC from "../views/assets/LoadingAnimation/loading-c.webp";

import bg from "../views/assets/bg.png";
import bgLast from "../views/assets/bg-last.png";
import startBtn from "../views/assets/start.png";
import nextBtn from "../views/assets/next.png";
import btnHome from "../views/assets/btn-home.png";
import btnQr from "../views/assets/btn-qr.png";

import productVibrant from "../views/assets/ULTIMATE-VIBRANT.png";
import productRadiance from "../views/assets/ULTIMATE-RADIANCE.png";
import productBioE from "../views/assets/BIO-E.png";

import siluet from "../assets/Siluet.png";

export const loadingAnimationAssets = [loadingA, loadingB, loadingC];
export const uiChromeAssets = [startBtn, nextBtn, btnHome, btnQr];
export const backgroundAssets = [bg, bgLast];
export const productAssets = [productVibrant, productRadiance, productBioE];
export const captureHelperAssets = [siluet];

export const staticAssetManifest = [
  ...loadingAnimationAssets,
  ...uiChromeAssets,
  ...backgroundAssets,
  ...productAssets,
  ...captureHelperAssets,
];
