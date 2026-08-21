// Mission Control: kanban board client plugin for DeepSeek Harness.
// Node half: the empty apply exists so the plugin appears in the host
// cordis.yml / Loader; the browser half ships via exports["./client"],
// discovered through the package.json dsh client declaration.
function apply() {}
export { apply };
