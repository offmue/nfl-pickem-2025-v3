# NFL 2025 Season - Weekly Update Instructions

## 📋 Wöchentlicher Update-Prozess

### Wann aktualisieren?
- **Nach Abschluss der letzten Spiele jeder Woche**
- Normalerweise nach Monday Night Football
- Vor Beginn der nächsten Woche

### Was aktualisieren?

#### 1. Abgeschlossene Woche
- `result` Spalte mit echten Ergebnissen füllen (z.B. "DEN 20-12")
- `completed` auf `True` setzen

#### 2. Kommende Woche
- `away_team` und `home_team` mit echten Team-Namen ersetzen
- `date` und `time` mit korrekten Spielzeiten aktualisieren
- `TBD` Platzhalter entfernen

### Datenquellen
- **ESPN NFL Schedule**: https://www.espn.com/nfl/schedule
- **NFL.com**: https://www.nfl.com/schedules/
- **Offizielle Team-Websites**

### Beispiel Update nach Woche 2:

**Vorher (Woche 3):**
```
week: 3, away_team: "TBD", home_team: "TBD", time: "TBD"
```

**Nachher (Woche 3):**
```
week: 3, away_team: "Dallas Cowboys", home_team: "New York Giants", time: "13:00"
```

### Spalten-Struktur (Final)
- `game_id`: Eindeutige Spiel-ID
- `season`: 2025
- `week`: Woche 1-18
- `date`: YYYY-MM-DD Format
- `time`: HH:MM Format (24h)
- `datetime`: Automatisch generiert
- `away_team`: Auswärts-Team (vollständiger Name)
- `home_team`: Heim-Team (vollständiger Name)
- `result`: "AWAY XX-YY HOME" oder leer
- `completed`: True/False

### Wichtige Hinweise
- **Team-Namen**: Exakt wie in der Datenbank verwenden
- **Ergebnis-Format**: "AWAY XX-YY HOME" (z.B. "DEN 20-12")
- **Datum/Zeit**: Lokale Zeit (Deutschland/Österreich)
- **Bye Weeks**: Manche Wochen haben nur 15 Spiele

### Automatisierung
- Script kann erweitert werden für automatische ESPN-Abfrage
- Manuelle Kontrolle empfohlen für Genauigkeit
- Backup vor jeder Aktualisierung erstellen

