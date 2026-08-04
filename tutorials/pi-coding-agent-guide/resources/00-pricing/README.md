# Provider and Cost Notes

Checked on 4 August 2026 against Pi 0.83.0.

Pi is MIT-licensed software. The model service you connect can still charge for
API calls, gateway usage, paid credits, or usage beyond a subscription quota.
The exact result depends on the provider and authentication method.

Use these current primary sources instead of a copied price table:

- [Pi provider authentication](https://github.com/earendil-works/pi/blob/main/packages/coding-agent/docs/providers.md)
- [Pi custom model cost metadata](https://github.com/earendil-works/pi/blob/main/packages/coding-agent/docs/models.md#model-configuration)
- the usage and billing page for the provider account you authenticated

## What the Session Display Measures

Pi shows token and cache usage reported by the provider. It combines that usage
with model metadata to calculate the cost shown in the footer and `/session`.

That display is useful for comparing sessions, but it is not a billing ledger:

- providers do not all report usage in the same way
- subscription quota and paid extra usage are separate from a model rate
- gateways can apply their own fees
- custom model metadata can be absent or stale
- a failed or retried request might appear differently in provider billing

Use the provider dashboard when you need the amount actually charged.

## Why This File Has No Prices

Model names, rate cards, subscription rules, and supported login methods change
independently. A dated table in this repository would become false while still
looking authoritative. Follow the provider link surfaced by Pi's current
documentation, then record pricing assumptions beside the system that uses them.
