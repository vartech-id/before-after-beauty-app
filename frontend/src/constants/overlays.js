import Overlay_Mencerahkan from "../views/assets/Overlay/overlay_mencerahkan.png";
import Overlay_Mengurangi_Keriput from "../views/assets/Overlay/overlay_keriput.png";
import Overlay_Melembabkan from "../views/assets/Overlay/overlay_melembabkan.png";

export const logicOverlayMap = {
  MENCERAHKAN_KULIT: Overlay_Mencerahkan,
  MENGURANGI_KERIPUT: Overlay_Mengurangi_Keriput,
  MELEMBABKAN_KULIT: Overlay_Melembabkan,
};

export const logicOverlayUrls = Object.values(logicOverlayMap).filter(Boolean);
