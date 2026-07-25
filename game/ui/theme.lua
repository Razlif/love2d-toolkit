-- Central UI palette and dimensions.
local Theme = {}

local themes = {
  default = {
    font_size = 18,
    spacing = 12,
    colors = {
      text = { 1, 1, 1, 1 },
      panel = { 0.05, 0.06, 0.09, 0.94 },
      panel_edge = { 0.35, 0.4, 0.52, 1 },
      card_panel = { 1, 1, 1, 1 },
      card_edge = { 0.08, 0.08, 0.1, 1 },
      card_text = { 0.05, 0.05, 0.06, 1 },
      card_speaker = { 0.08, 0.25, 0.55, 1 },
      selected = { 0.2, 0.55, 0.9, 1 },
      overlay = { 0, 0, 0, 0.55 }
    }
  }
}

function Theme.get(name)
  return themes[name or "default"] or themes.default
end

return Theme
