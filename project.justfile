## Add your own just recipes here. This is imported by the main justfile.

# Overriding recipes from the root justfile by adding a recipe with the same
# name in this file is not possible until a known issue in just is fixed,
# https://github.com/casey/just/issues/2540

# Regenerate docs/measurements-hackathon/raised-items.md from raised_items.yaml
raised-items:
  uv run python scripts/render_raised_items.py
