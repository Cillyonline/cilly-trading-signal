# GitHub / VPS: zentraler Betriebspfad

Auftrag #837. Dieses **öffentliche** Repository betreibt weiterhin seine eigenen CI- und Security-Scan-Workflows. Der SSH-Zugang zum getrennten Netcup-VPS wird zentral und ausschließlich im privaten Repo [Cillyonline/cillyonline-core](https://github.com/Cillyonline/cillyonline-core) verwaltet.

## Zugriffsweg

- [Zentraler GitHub-Actions-Lesetest](https://github.com/Cillyonline/cillyonline-core/actions/workflows/vps-readonly.yml)
- [Einmalige SSH-Einrichtung](https://github.com/Cillyonline/cillyonline-core/blob/main/docs/VPS_READONLY.md)
- [Projektzuordnung und Grenzen](https://github.com/Cillyonline/cillyonline-core/blob/main/docs/VPS_PROJECT_ROUTING.md)

Der zentrale Test kann nur die SSH-Identität über `whoami` bestätigen. **Er überprüft keinen Anwendungsstatus und deployt nichts.** Die tatsächliche VPS-Konfiguration mit dediziertem Benutzer, gültigem Hostkey und Actions-Secret ist noch nicht live nachgewiesen.

## Aufgabenverteilung

- **Dieses Repo:** Quellcode, Docker-Compose, Web-/API-Tests und [Deployment-Runbook](DEPLOYMENT_RUNBOOK.md). Der [VPS-Staging-Plan](VPS_STAGING_PLAN.md) mit Bestands- und Konfliktrisiken bleibt maßgeblich. Bereits vorhandene Inventuren können inzwischen veraltet sein.
- **Privates Core-Repo:** Ausdrücklich beauftragte, begrenzte VPS-Zugriffs- und spätere Betriebsschritte nach einem aktuellen Bestandsabgleich.
- **Nicht erlaubt:** Repository-SSH-Secret duplizieren, private `workflow_call`-Workflows aus diesem öffentlichen Repo aufrufen, automatisches VPS-Deployment aus PRs/Issues/Pushes, Root-/Docker-Gruppenrechte für den reinen `whoami`-Prüfbenutzer, echte Trades oder Broker-Ausführungen.

Bevor eine separate Staging-Aktion auf dem VPS freigegeben wird, müssen aktive Container, Ports, Datenträger/Volumes, Backups, Secrets, Zielumgebung, Migrationsrisiken und ein konkreter Rollback geprüft sein. Das bestehende Compose-Projekt `staging` darf nicht versehentlich berührt werden. Ein erfolgreicher GitHub-CI-Build ist weder ein Deployment noch ein Nachweis, dass die Anwendung auf dem VPS erreichbar ist.

Dieses Dokument schafft **keine** direkte Repo-zu-VPS-Verbindung und ändert keine produktive Umgebung. Rückwechsel: dieses Dokument entfernen/revertieren.
