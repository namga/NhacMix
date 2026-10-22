import { registerPlugin } from '@capacitor/core';

// Explicit JS proxies ensure the custom native media plugin is callable in a plain HTML app.
window.NhacMixMedia = registerPlugin('NhacMixMedia');
window.NhacMixBrowser = registerPlugin('Browser');
