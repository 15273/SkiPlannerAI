# skiMate – Location Privacy Policy

**Effective date:** 2026-04-12
**App:** skiMate (iOS & Android)
**Contact:** privacy@skimate.app

---

## 1. Introduction

This Location Privacy Policy explains how skiMate ("we", "our", "us") collects, uses, stores, and shares location-related data when you use the skiMate mobile application. It supplements our general Privacy Policy and applies specifically to location data.

---

## 2. What Location Data We Collect

| Data type | How it is obtained | Retention |
|-----------|-------------------|-----------|
| **GPS coordinates** | Requested from your device OS at runtime (requires explicit permission) | Session only — never written to disk or database |
| **IP-inferred location** | Derived from your network IP address on first API call | Session only — never written to disk or database |
| **Origin city / airport (IATA code)** | Entered by you during onboarding or trip planning | Persisted in your onboarding preferences until you delete it |

We do **not** collect continuous background location, movement history, or precise location outside of an active session.

---

## 3. Why We Collect Location Data

| Purpose | Data used |
|---------|-----------|
| **Resort map proximity** – rank nearby ski resorts and centre the interactive map on your location | GPS coordinates (or IP-inferred fallback) |
| **Flight search origin pre-fill** – automatically populate the departure airport field so you do not have to type it each time | Origin city / airport stored in onboarding prefs |
| **Amadeus API calls** – pass an IATA departure airport code to the Amadeus Flight Offers Search API to retrieve available flights to ski-resort airports | Anonymised IATA code derived from origin city / airport preference |

We do not use location data for advertising, profiling, or any purpose not listed above.

---

## 4. Storage Duration

- **GPS coordinates:** Held in memory only for the duration of a single app session (from foreground launch to background/close). They are never written to persistent storage, databases, or log files.
- **IP-inferred location:** Processed server-side in memory for a single request/response cycle. Not logged or stored.
- **Origin city / airport:** Stored in your user profile until you explicitly delete it (see Section 6 – How to Opt Out) or request full account erasure.

---

## 5. Who We Share Location Data With

| Recipient | What is shared | Purpose |
|-----------|---------------|---------|
| **Amadeus for Developers API** | Anonymised IATA airport code only (e.g. `LAX`, `JFK`) — no raw coordinates, no IP address | Flight offer search |
| **OpenStreetMap tile servers** | No location data is transmitted; map tiles are fetched by tile coordinates (zoom/x/y) that do not identify you | Rendering the resort map |

We do **not** sell, rent, or trade any location data to any third party. We do not share location data with advertisers, data brokers, analytics platforms, or any party not listed in this table.

---

## 6. How to Opt Out

### 6a. Revoke OS Location Permission
You can revoke skiMate's access to GPS at any time without losing app functionality:

- **iOS:** Settings → Privacy & Security → Location Services → skiMate → set to **Never** or **Ask Next Time**
- **Android:** Settings → Apps → skiMate → Permissions → Location → set to **Deny**

When GPS permission is revoked, the app falls back to IP-inferred location for map centering. You can also dismiss the IP-inferred suggestion and enter your location manually.

### 6b. Use Manual Entry
At any point during onboarding or trip planning, you may skip automatic location detection and type your origin city or airport code directly. No GPS or IP-inferred data is used when you choose manual entry.

### 6c. Delete Your Origin City / Airport Preference
In the app: **Profile → Travel Preferences → Origin Airport → Remove**.

### 6d. Request Full Erasure
Email **privacy@skimate.app** with subject line "Location Data Erasure Request". We will erase all persisted location-related data associated with your account within **30 days** of receiving a verifiable request. We will confirm completion by reply.

---

## 7. GDPR (EU/UK Users)

### Legal Basis for Processing

| Processing activity | Legal basis |
|--------------------|-------------|
| GPS / IP location for map proximity (session only) | **Legitimate interest** (Art. 6(1)(f)) – enabling core navigation functionality; overridden by your right to opt out at any time |
| Origin city / airport storage and Amadeus API calls | **Consent** (Art. 6(1)(a)) – obtained during onboarding; withdrawable at any time |

### Your Rights

You have the following rights under GDPR. To exercise any of them, contact **privacy@skimate.app**:

- **Right of access** (Art. 15) – request a copy of all location data we hold about you.
- **Right to rectification** (Art. 16) – correct inaccurate stored location preferences.
- **Right to erasure ("right to be forgotten")** (Art. 17) – request deletion of all location data; we respond within 30 days.
- **Right to data portability** (Art. 20) – receive your stored origin city / airport preference in a machine-readable format (JSON).
- **Right to withdraw consent** – withdraw consent for origin city / airport storage at any time; this does not affect the lawfulness of prior processing.
- **Right to lodge a complaint** – you may lodge a complaint with your national supervisory authority (e.g. ICO in the UK, CNIL in France, BfDI in Germany).

---

## 8. CCPA (California Residents)

### Your Rights Under CCPA / CPRA

- **Right to know** – you may request disclosure of the categories and specific pieces of location data we collect, use, and share about you.
- **Right to delete** – you may request deletion of location data we hold; we will comply within 45 days (extendable by a further 45 days with notice).
- **Right to opt out of sale or sharing** – skiMate does **not** sell or share personal information (including location data) with third parties for cross-context behavioural advertising. There is nothing to opt out of.
- **Right to non-discrimination** – we will not discriminate against you for exercising any CCPA right.

To submit a CCPA request, email **privacy@skimate.app** or use the in-app erasure flow described in Section 6d.

---

## 9. COPPA (Children's Privacy)

skiMate is **not directed at children under 13**. We do not knowingly collect personal information, including location data, from anyone under 13 years of age. If you believe a child under 13 has provided location data to skiMate, contact **privacy@skimate.app** immediately and we will delete the data promptly.

---

## 10. OpenStreetMap Attribution

The skiMate app displays map tiles provided by **OpenStreetMap** contributors under the [Open Database Licence (ODbL)](https://opendatacommons.org/licenses/odbl/). Map tile requests are made using standard tile coordinates (zoom level, tile x, tile y); **no location data identifying you is transmitted to OpenStreetMap servers**. See [openstreetmap.org/copyright](https://www.openstreetmap.org/copyright) for full attribution.

---

## 11. Data Security

GPS and IP-inferred data exist only in process memory and are discarded when the request completes. Origin city / airport preferences are stored encrypted at rest in our database (AES-256) and transmitted only over TLS 1.2+. Access is restricted to authorised engineering staff on a need-to-know basis.

---

## 12. Changes to This Policy

We may update this policy from time to time. Material changes will be notified in-app and the effective date at the top of this document will be updated. Continued use of the app after the effective date constitutes acceptance of the revised policy.

---

## 13. Contact

For any questions or requests relating to this policy:

**Email:** privacy@skimate.app
**Subject line for erasure requests:** "Location Data Erasure Request"

We respond to all privacy enquiries within **72 hours** (acknowledgement) and resolve erasure requests within **30 days**.
