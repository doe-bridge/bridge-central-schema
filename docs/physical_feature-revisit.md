# PhysicalFeature: items to revisit

These are open design questions for `PhysicalFeature`, not decisions about the schema.

1. **Bounding boxes and `location_coordinates`.** Discuss whether bounding boxes are common enough across BRIDGE to need a dedicated slot or other shared handling. The existing `location_coordinates` slot could hold bounding box coordinates; confirm the intended JSON representation and whether that is sufficient.
2. **Habitat and environment type.** Consider a dedicated habitat or environment type slot, or whether the `Attribute` concept can cover this and other observations or characterizations of a physical feature.
3. **Feature type.** Revisit the `feature_type` slot. BASIN-3D has a feature type, but ESS-DIVE deliberately omitted one because an enumeration that contributors would use consistently seemed impractical. ESS-DIVE instead encourages contributors to include common feature type descriptors in the location name or description; examples are currently in a figure in the [ESS-DIVE instructions](https://github.com/ess-dive-workspace/essdive-location-metadata/blob/release-v2.0.0/instructions.md).
4. **Source location identifiers.** Discuss why `source_location_id` is needed alongside `id` and whether source identifiers should follow a common pattern across BRIDGE classes, including `Measurement.source_record_id`.
5. **Site.** Reconcile the Site concept with `PhysicalFeature`, including whether Site should be a subclass or use a physical feature reference.
6. **Notes.** Discuss the purpose of the `notes` slot and when to use it instead of `description` or an attribute.
7. **`other` enum values.** `ElevationDatumEnum` and `VerticalPositionReferenceEnum` currently include `other` for ESS-DIVE compatibility. Discuss how to handle these values, which are not desired in BRIDGE schemas.
