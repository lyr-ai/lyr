# Source passages — engineering team meeting notes (excerpts)

Raw notes the semantic records in `semantic_nodes.json` were drawn from. Kept for
provenance.

**standup-04-12.** Decision: we're sunsetting the legacy billing API by Q3. Also:
payments CI flaked again overnight and blocked the nightly release.

**standup-04-19.** Reconfirmed the billing API retirement (before Q3) after Priya
asked whether it was still on. Donuts, courtesy of Sam.

**standup-04-26.** Payments CI flaked again — third time this month it's held up a
release. More donuts.

**arch-review-03-02.** Agreed all new services standardize on Postgres.

**arch-review-05-11.** After load testing, we reversed the Postgres call and chose
DynamoDB for the new services — the access patterns are key-value and the write
volume was too high for our Postgres setup.

**retro-05-01.** Biggest recurring theme this month: payments CI flakiness keeps
blocking releases. Action: allocate time to stabilize it.

**planning-05-03.** Hired a second SRE to take over the on-call rotation.
