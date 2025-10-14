/* base.js
   Purpose: global namespace, component registration, auto-mounting and simple utils.
   Components must call MedApp.register('ComponentName', module) where module has init(el, props).
*/

window.MedApp = window.MedApp || {};
MedApp.components = MedApp.components || {};

/* Register a component module
   name string: component name used in data-component attribute
   module object: must implement init(el, props) optionally destroy(el)
*/
MedApp.register = function(name, module) {
  MedApp.components[name] = module;
};

/* Utility: safe JSON parse or empty object */
MedApp.safeParse = function(json) {
  try { return JSON.parse(json || '{}'); } catch (e) { return {}; }
};

/* Initialize components found in DOM */
MedApp.init = function() {
  document.querySelectorAll('[data-component]').forEach(function(el) {
    var name = el.getAttribute('data-component');
    var module = MedApp.components[name];
    if (module && typeof module.init === 'function') {
      var props = MedApp.safeParse(el.getAttribute('data-props'));
      try { module.init(el, props); } catch (err) { console.error('Component init error', name, err); }
    }
  });
};

/* Auto-run on DOM loaded */
document.addEventListener('DOMContentLoaded', MedApp.init);
