# Privacy notes (Kenya)

This is an engineering baseline, not legal advice. The service should be operated in line with the Kenya Data Protection Act, 2019 and applicable regulations.

- Collect only data needed to provide the service.
- AI training consent is separate, optional, timestamped, and off by default.
- A user must be able to use the service without agreeing to training.
- Future training pipelines must filter for consent and documented content rights.
- Provide a way to withdraw consent and request deletion; ensure future dataset builds exclude withdrawn/deleted records.
- Remove personal data such as names, phone numbers and payment identifiers before human dataset review.
- Define retention periods and access controls before production deployment.
- Never put secrets, private user media or training datasets in Git.
