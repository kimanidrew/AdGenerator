# Training policy
No live or unsupervised model updates. Training runs are scheduled, gated, logged and reversible. Each candidate records base model, code revision, dataset manifest/version, hyperparameters, evaluation results and approval. Candidates must pass fixed held-out evaluation and safety checks before staged deployment. Keep the production model available for one-click rollback.
