// Read-only Asset Lab viewer. The manifest is supplied by manifest.js.
(function () {
  "use strict";

  const state = {
    manifest: window.ASSET_LAB_MANIFEST || { assets: [], orphans: [] },
    selectedAssetId: null,
    selectedMediaKey: null
  };
  const LAST_ASSET_STORAGE_KEY = "asset-lab:last-asset";

  const elements = {
    status: document.getElementById("manifest-status"),
    reload: document.getElementById("reload-button"),
    count: document.getElementById("asset-count"),
    tree: document.getElementById("asset-tree"),
    warnings: document.getElementById("asset-warnings"),
    previewTitle: document.getElementById("preview-title"),
    previewKind: document.getElementById("preview-kind"),
    previewStage: document.getElementById("preview-stage"),
    previewCaption: document.getElementById("preview-caption"),
    inspectorEmpty: document.getElementById("inspector-empty"),
    inspectorContent: document.getElementById("inspector-content")
  };

  const groupOrder = [
    ["character", "Characters"],
    ["prop", "Props"],
    ["background", "Backgrounds"],
    ["effect", "Effects"]
  ];

  function text(value) {
    return value === undefined || value === null || value === "" ? "-" : String(value);
  }

  function create(tag, className, content) {
    const node = document.createElement(tag);
    if (className) node.className = className;
    if (content !== undefined) node.textContent = content;
    return node;
  }

  function getAsset() {
    return state.manifest.assets.find((asset) => asset.id === state.selectedAssetId) || null;
  }

  function statusClass(asset) {
    const values = [];
    [...(asset.images || []), ...(asset.animations || [])].forEach((item) => values.push(item.status));
    if (values.includes("missing_on_disk")) return "is-danger";
    if (values.some((value) => value && value !== "created_on_disk")) return "is-warning";
    return "";
  }

  function renderTree() {
    elements.tree.replaceChildren();
    elements.count.textContent = state.manifest.assets.length;
    const grouped = new Map(groupOrder.map(([type]) => [type, []]));
    state.manifest.assets.forEach((asset) => {
      if (!grouped.has(asset.type)) grouped.set(asset.type, []);
      grouped.get(asset.type).push(asset);
    });

    groupOrder.concat([...grouped.keys()].filter((type) => !groupOrder.some(([known]) => known === type)).map((type) => [type, type])).forEach(([type, label]) => {
      const assets = grouped.get(type) || [];
      const group = document.createElement("details");
      group.className = "asset-group";
      group.open = assets.length > 0;
      const summary = document.createElement("summary");
      summary.textContent = `${label} (${assets.length})`;
      group.append(summary);
      const list = create("div", "asset-list");
      assets.forEach((asset) => {
        const button = create("button", `asset-button${asset.id === state.selectedAssetId ? " is-selected" : ""}`);
        button.type = "button";
        button.addEventListener("click", () => selectAsset(asset.id));
        const row = create("span", "asset-row");
        row.append(create("span", "asset-name", asset.id));
        const dot = create("span", `asset-status-dot ${statusClass(asset)}`);
        dot.title = statusClass(asset) === "is-danger" ? "Missing file" : "Asset status";
        row.append(dot);
        button.append(row);
        list.append(button);
      });
      if (!assets.length) list.append(create("p", "muted", "Empty"));
      group.append(list);
      elements.tree.append(group);
    });

    renderWarnings();
  }

  function renderWarnings() {
    elements.warnings.replaceChildren();
    const orphans = state.manifest.orphans || [];
    const missing = state.manifest.assets.flatMap((asset) => [...(asset.images || []), ...(asset.animations || [])].filter((item) => item.status === "missing_on_disk"));
    if (!orphans.length && !missing.length) return;
    if (orphans.length) elements.warnings.append(create("p", "warning-line", `${orphans.length} orphan file${orphans.length === 1 ? "" : "s"}`));
    if (missing.length) elements.warnings.append(create("p", "warning-line is-danger", `${missing.length} missing file${missing.length === 1 ? "" : "s"}`));
  }

  function selectAsset(assetId) {
    state.selectedAssetId = assetId;
    try {
      window.localStorage.setItem(LAST_ASSET_STORAGE_KEY, assetId);
    } catch (error) {
      // Local file storage can be unavailable in some browser settings.
    }
    const asset = getAsset();
    if (asset && asset.images && asset.images.length) {
      state.selectedMediaKey = `image:${asset.images[0].id}`;
    } else if (asset && asset.animations && asset.animations.length) {
      const animation = asset.animations[0];
      state.selectedMediaKey = `animation:${animation.id}:${animation.gif_path ? "gif" : "sheet"}`;
    } else {
      state.selectedMediaKey = null;
    }
    renderTree();
    renderInspector();
    renderPreview();
  }

  function preferredInitialAssetId() {
    const datedAssets = state.manifest.assets
      .map((asset) => ({ asset, timestamp: Date.parse(asset.updated_at || asset.created_at || "") }))
      .filter((entry) => !Number.isNaN(entry.timestamp))
      .sort((left, right) => right.timestamp - left.timestamp);
    if (datedAssets.length) return datedAssets[0].asset.id;
    try {
      const remembered = window.localStorage.getItem(LAST_ASSET_STORAGE_KEY);
      if (remembered && state.manifest.assets.some((asset) => asset.id === remembered)) return remembered;
    } catch (error) {
      // Local file storage can be unavailable in some browser settings.
    }
    return state.manifest.assets.length ? state.manifest.assets[state.manifest.assets.length - 1].id : null;
  }

  function metadataRow(label, value, isPath) {
    const row = create("div", "metadata-row");
    row.append(create("span", "metadata-label", label));
    row.append(isPath ? create("code", "metadata-value", text(value)) : create("span", "metadata-value", text(value)));
    return row;
  }

  function chooseMedia(key) {
    state.selectedMediaKey = key;
    renderInspector();
    renderPreview();
  }

  function choiceCard(title, meta, selected, actions) {
    const card = create("div", `choice-card${selected ? " is-selected" : ""}`);
    card.append(create("div", "choice-card-title", title));
    card.append(create("div", "choice-card-meta", meta));
    const actionRow = create("div", "animation-actions");
    actions.forEach((action) => {
      const button = create("button", `choice-button${action.active ? " is-active" : ""}`, action.label);
      button.type = "button";
      button.addEventListener("click", () => chooseMedia(action.key));
      actionRow.append(button);
    });
    card.append(actionRow);
    return card;
  }

  function collapsibleSection(title, open) {
    const section = create("details", "asset-section inspector-section");
    section.open = open;
    const summary = create("summary", "asset-section-title", title);
    section.append(summary);
    return section;
  }

  function renderInspector() {
    const asset = getAsset();
    if (!asset) {
      elements.inspectorEmpty.hidden = false;
      elements.inspectorContent.hidden = true;
      return;
    }
    elements.inspectorEmpty.hidden = true;
    elements.inspectorContent.hidden = false;
    elements.inspectorContent.replaceChildren();

    const header = create("div", "inspector-header");
    header.append(create("h2", null, asset.id));
    header.append(create("p", "muted", `${text(asset.type)} · ${text(asset.folder)}`));
    elements.inspectorContent.append(header);

    const imagesSection = collapsibleSection("Images", true);
    const imageList = create("div", "choice-list");
    (asset.images || []).forEach((image) => imageList.append(choiceCard(`Version ${text(image.version)}`, `${text(image.provider)} · ${text(image.width)} x ${text(image.height)}`, state.selectedMediaKey === `image:${image.id}`, [{ label: "Open image", key: `image:${image.id}`, active: state.selectedMediaKey === `image:${image.id}` }])));
    if (!asset.images || !asset.images.length) imageList.append(create("p", "muted", "No images recorded."));
    imagesSection.append(imageList);
    elements.inspectorContent.append(imagesSection);

    const animationsSection = collapsibleSection("Animations", true);
    const animationList = create("div", "choice-list");
    (asset.animations || []).forEach((animation) => {
      const baseKey = `animation:${animation.id}`;
      const actions = [];
      if (animation.gif_path) actions.push({ label: "GIF", key: `${baseKey}:gif`, active: state.selectedMediaKey === `${baseKey}:gif` });
      if (animation.sheet_path) actions.push({ label: "Sprite sheet", key: `${baseKey}:sheet`, active: state.selectedMediaKey === `${baseKey}:sheet` });
      animationList.append(choiceCard(`${text(animation.name)} · v${text(animation.version)}`, `${text(animation.provider)} · ${text(animation.frame_count)} frames · ${text(animation.fps)} FPS`, actions.some((action) => action.active), actions));
    });
    if (!asset.animations || !asset.animations.length) animationList.append(create("p", "muted", "No animations recorded."));
    animationsSection.append(animationList);
    elements.inspectorContent.append(animationsSection);

    const selected = selectedRecord(asset);
    const metadataSection = collapsibleSection("Metadata", false);
    const metadata = create("div", "metadata");
    if (selected) {
      metadata.append(metadataRow("Provider", selected.provider));
      metadata.append(metadataRow("Status", selected.status || "created_on_disk"));
      metadata.append(metadataRow("Prompt", selected.prompt));
      metadata.append(metadataRow("Source image", selected.source_image_path || selected.source_image_version));
      metadata.append(metadataRow("Dimensions", selected.width ? `${selected.width} x ${selected.height}` : `${selected.frame_width || "-"} x ${selected.frame_height || "-"}`));
      metadata.append(metadataRow("Frame count", selected.frame_count));
      metadata.append(metadataRow("FPS", selected.fps));
      metadata.append(metadataRow("Path", selected.path || selected.gif_path || selected.sheet_path, true));
    }
    metadataSection.append(metadata);
    elements.inspectorContent.append(metadataSection);
  }

  function selectedRecord(asset) {
    if (!state.selectedMediaKey) return null;
    const parts = state.selectedMediaKey.split(":");
    if (parts[0] === "image") return (asset.images || []).find((image) => image.id === parts[1]) || null;
    return (asset.animations || []).find((animation) => animation.id === parts[1]) || null;
  }

  function renderPreview() {
    const asset = getAsset();
    const record = selectedRecord(asset || { images: [], animations: [] });
    elements.previewStage.replaceChildren();
    if (!asset || !record) {
      elements.previewTitle.textContent = "Select an asset";
      elements.previewKind.textContent = "NONE";
      elements.previewCaption.textContent = "The selected file will appear here.";
      elements.previewStage.append(createEmptyPreview());
      return;
    }

    const keyParts = state.selectedMediaKey.split(":");
    const isImage = keyParts[0] === "image";
    const useGif = !isImage && keyParts[2] === "gif";
    const path = isImage ? record.path : (useGif ? record.gif_path : record.sheet_path);
    elements.previewTitle.textContent = asset.id;
    elements.previewKind.textContent = isImage ? "IMAGE" : (useGif ? "GIF" : "SPRITE SHEET");
    elements.previewCaption.textContent = path || "No preview path recorded.";
    if (!path) {
      elements.previewStage.append(create("p", "muted", "No file path recorded for this entry."));
      return;
    }
    const image = create("img", "preview-image");
    image.alt = `${asset.id} ${isImage ? "image" : text(record.name)}`;
    image.src = path;
    image.addEventListener("error", () => {
      elements.previewStage.replaceChildren(create("p", "warning-line is-danger", "File could not be loaded. Check the manifest and disk."));
    }, { once: true });
    elements.previewStage.append(image);
  }

  function createEmptyPreview() {
    const empty = create("div", "empty-state");
    empty.append(create("span", "empty-icon", "+"));
    empty.append(create("p", null, "Select an image or animation to inspect it."));
    return empty;
  }

  function setStatus(message, isError) {
    elements.status.textContent = message;
    elements.status.classList.toggle("is-error", Boolean(isError));
  }

  function start() {
    if (!window.ASSET_LAB_MANIFEST) {
      setStatus("manifest.js missing", true);
    } else {
      setStatus(`${state.manifest.assets.length} assets loaded`);
    }
    elements.reload.addEventListener("click", () => window.location.reload());
    renderTree();
    const initialAssetId = preferredInitialAssetId();
    if (initialAssetId) selectAsset(initialAssetId);
  }

  start();
}());
