from __future__ import annotations

from textual.widgets import Static


class SummaryPanel(Static):
    def update_summary(self, *, local_url: str, public_url: str | None, status: str) -> None:
        public = public_url or "Waiting for cloudflared..."
        self.update(
            f"[b]Local URL:[/] {local_url}\n[b]Public URL:[/] {public}\n[b]Status:[/] {status}"
        )
