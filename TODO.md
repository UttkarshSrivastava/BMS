# TODO - Fix card application data not updating

- [x] Fix backend + UI flow so that a CardRequest row is always created reliably when user submits application.
- [x] Update `app/templates/apply card.html` so it calls backend `POST /card/apply` before redirecting to documents.
- [x] Update `app/templates/card-documents.html` so it updates the same request row using `card_request_id`.
- [ ] Add/verify the session key `customerAccountNumber` is set on login and not cleared unexpectedly.
- [x] Ensure `submitDocuments()` hits `/card/upload-documents` and handles response errors.
- [ ] Run server and manually test: apply -> submit docs -> my requests list shows new row.


